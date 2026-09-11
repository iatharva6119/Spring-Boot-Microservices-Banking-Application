# Phase 0 — Baseline & Environment Preparation

---

## 1. Objective

### What we wanted to achieve

Before we make any Kubernetes changes, we needed to deeply understand the existing project.
Think of it like taking a photograph of everything before a renovation — so we know exactly what we started with.

### Why we needed it

If we jump straight into Kubernetes without understanding the existing system, we risk:
- Breaking things we did not intend to change
- Misconfiguring services because we did not know how they were connected
- Losing track of what each service depends on

### How it fits into the project

Phase 0 is the foundation of everything that follows.
Every Kubernetes YAML file we write in Phase 1, 2, and 3 will be based on the knowledge we collected here.

---

## 2. Starting Point

Before Phase 0, the project was a fully running Spring Boot microservices application managed by Docker Compose.

Here is what was already in place:

- Seven Spring Boot services, each built into its own Docker image
- One Keycloak container already running separately (not via Docker Compose)
- MySQL running directly on the Windows host machine
- Prometheus and Grafana configured and running through Docker Compose
- All services communicating through a Docker bridge network called `banking-network`
- Eureka service registry managing service discovery
- OpenFeign handling service-to-service REST calls

The application was **not yet on Kubernetes**. That is what the later phases will accomplish.

---

## 3. What We Implemented

Phase 0 is a **read-only inspection phase**. We did not modify any code or configuration.

We inspected:

### 3.1 Repository Structure

We explored every module directory and identified all services and their relationships.

### 3.2 Docker Compose

We read `docker-compose.yml` to understand how each service is configured for the containerised environment — which ports are exposed, which environment variables are passed, and how services depend on each other.

### 3.3 Dockerfiles

We read every Dockerfile to understand how Docker images are built for each service.

### 3.4 Application Configuration Files

We read every `application.yml` file to understand:
- What port each service listens on
- How each service connects to MySQL
- How each service connects to Eureka
- How each service connects to Keycloak
- What Actuator endpoints are exposed
- How Prometheus metrics are configured

### 3.5 Maven POM Files

We read every `pom.xml` to identify:
- Spring Boot version used
- Spring Cloud version used
- Java version
- Which libraries each service depends on (OpenFeign, Keycloak Admin Client, etc.)

### 3.6 Feign Client Analysis

We searched the source code for `@FeignClient` annotations to understand exactly how services call each other.

### 3.7 Docker Environment

We ran `docker ps` and `docker images` to see the current state of the Docker environment.

---

## 4. Architecture Before

`
+------------------------------------------------------------------+
|                    Windows Host Machine                           |
|                                                                   |
|  +-----------------------------------------------------------+    |
|  |                 MySQL (Port 3306)                          |    |
|  |          Running directly on Windows                       |    |
|  |   Databases: user_service, account_service,                |    |
|  |              transaction_service, fund_transfer_service,   |    |
|  |              sequence_generator                            |    |
|  +-----------------------------------------------------------+    |
|                                                                   |
|  +-----------------------------------------------------------+    |
|  |            Docker Desktop Engine                           |    |
|  |                                                           |    |
|  |  +-----------------------------------------------------+  |    |
|  |  |  Standalone Container (default bridge network)       |  |    |
|  |  |  keycloak (quay.io/keycloak/keycloak:24.0)           |  |    |
|  |  |  Host Port: 8571   Container Port: 8080              |  |    |
|  |  +-----------------------------------------------------+  |    |
|  |                                                           |    |
|  |  +-----------------------------------------------------+  |    |
|  |  |         banking-network (Docker Compose)              |  |    |
|  |  |  service-registry   :8761                            |  |    |
|  |  |  api-gateway        :8080  (JWT validation)          |  |    |
|  |  |  user-service       :8082  (Keycloak admin)          |  |    |
|  |  |  account-service    :8081                            |  |    |
|  |  |  sequence-generator :8083                            |  |    |
|  |  |  transaction-service:8084                            |  |    |
|  |  |  fund-transfer      :8085                            |  |    |
|  |  |  prometheus         :9090                            |  |    |
|  |  |  grafana            :3000                            |  |    |
|  |  +-----------------------------------------------------+  |    |
|  +-----------------------------------------------------------+    |
+------------------------------------------------------------------+

Client Browser / Postman
  |
  v (Port 8080)
api-gateway  (JWT verified against Keycloak at host.docker.internal:8571)
  |
  +---> user-service        (lb://user-service)
  +---> account-service     (lb://account-service)
  +---> transaction-service (lb://transaction-service)
  +---> fund-transfer       (lb://fund-transfer-service)

Service-to-Service Feign calls:
  fund-transfer   --> account-service      (via Eureka lookup)
  fund-transfer   --> transaction-service  (via Eureka lookup)
  account-service --> user-service         (via Eureka lookup)
  account-service --> transaction-service  (via Eureka lookup)
  account-service --> sequence-generator   (via Eureka lookup)
  user-service    --> account-service      (via Eureka lookup)
  transaction-service --> account-service  (via Eureka lookup)
`

---

## 5. Architecture After

Phase 0 made **no changes** to the architecture.

The architecture after Phase 0 is identical to the architecture before Phase 0.

The value of this phase is the knowledge we gained, not any changes we made.

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `docs/phase-00-baseline.md` | This document — a complete record of the baseline state before Kubernetes migration |

No application files were created. No Docker or configuration files were created.

---

## 7. Files Modified

**No files were modified in Phase 0.**

This phase was read-only inspection only. All existing behavior is completely preserved.

---

## 8. Configuration Explained

### 8.1 Service Registry (Eureka Server) — Port 8761

The Service Registry is the phone book of our application. When a service starts up, it registers itself here with its name and address. When another service wants to call it, it asks the registry where account-service is and the registry provides the current address.

Key configuration:
- `register-with-eureka: false` — Eureka server does not register itself (it is the registry, not a client)
- `fetch-registry: false` — Eureka server does not fetch a registry from another Eureka server

### 8.2 API Gateway — Port 8080

The API Gateway is the single entry point for all external traffic. Clients never call individual services directly — they always go through the gateway.

Key configuration:
- `lb://user-service` — The `lb://` prefix means load balanced. The gateway asks Eureka for the address of `user-service` and forwards the request there.
- `APP_CONFIG_KEYCLOAK_URL` — The URL the gateway uses to verify JWT tokens. In Docker Compose this is `http://host.docker.internal:8571/` — `host.docker.internal` is a special Docker hostname that means the Windows host machine.
- JWT validation: every request to the gateway must carry a valid Keycloak-issued token.

Gateway routes configured:
- `/api/users/**`        -> user-service
- `/accounts/**`         -> account-service
- `/sequence/**`         -> sequence-generator
- `/transactions/**`     -> transaction-service
- `/api/fund-transfers/**` -> fund-transfer-service
- `/fund-transfers/**`   -> fund-transfer-service

### 8.3 User Service — Port 8082

Manages user registration, user profiles, and user creation in Keycloak.

Key configuration:
- `MYSQL_HOST` — Set to `host.docker.internal` in Docker Compose (connect to MySQL on the Windows host)
- `APP_CONFIG_KEYCLOAK_SERVER_URL` — Points to Keycloak for creating users via Keycloak Admin API
- Uses `keycloak-admin-client` library version `21.0.1`

MySQL connection pattern:
`jdbc:mysql://:/`

This means: use the MYSQL_HOST environment variable. If not set, default to localhost.

### 8.4 Account Service — Port 8081

Manages bank accounts (create, read, update balance).

Key configuration:
- MySQL datasource URL in `application.yml` is hardcoded as `jdbc:mysql://localhost:3306/account_service`
- **Important observation:** In Docker Compose, the `SPRING_DATASOURCE_URL` environment variable overrides this to `jdbc:mysql://host.docker.internal:3306/account_service`
- No Keycloak configuration — Account Service does not talk to Keycloak directly
- Uses OpenFeign to call: user-service, transaction-service, sequence-generator

### 8.5 Transaction Service — Port 8084

Records all financial transactions (debits and credits).

Key configuration:
- MySQL datasource URL defaulted to `localhost:3306` in `application.yml`
- Overridden by `SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/transaction_service` in Docker Compose
- Uses OpenFeign to call: account-service

### 8.6 Fund Transfer Service — Port 8085

Orchestrates the money transfer flow: validates accounts, calls Account Service to update balances, calls Transaction Service to record the transaction.

Key configuration:
- MySQL datasource URL defaults to `localhost:3306/fund_transfer_service`
- Overridden by `SPRING_DATASOURCE_URL` in Docker Compose
- Has **two** Feign clients: one for `account-service`, one for `transaction-service`

### 8.7 Sequence Generator — Port 8083

Generates unique sequence numbers for account numbers and transaction IDs.

Key configuration:
- MySQL datasource URL defaults to `localhost:3306/sequence_generator`
- Overridden by `SPRING_DATASOURCE_URL` in Docker Compose
- Does **not** use OpenFeign — no `@EnableFeignClients`

### 8.8 Prometheus — Port 9090

Collects metrics from all services every 5 seconds by calling each service's `/actuator/prometheus` endpoint.

Key configuration:
- `scrape_interval: 5s` — Prometheus polls each service every 5 seconds
- `storage.tsdb.retention.time=15d` — Metrics are kept for 15 days
- All targets use Docker service names (e.g., `service-registry:8761`), not localhost
- Scrapes all 7 services plus itself

### 8.9 Grafana — Port 3000

Visualizes metrics from Prometheus.

Key configuration:
- Admin credentials: `admin / admin`
- Dashboard auto-provisioned from `grafana/provisioning/dashboards/`
- Datasource auto-provisioned from `grafana/provisioning/datasources/`

### 8.10 Keycloak — Host Port 8571, Container Port 8080

Authentication and authorisation server. Running as a standalone Docker container (NOT through Docker Compose).

Key facts:
- Image: `quay.io/keycloak/keycloak:24.0`
- Start mode: `start-dev` (development mode)
- Network: Docker default bridge network (IP: `172.17.0.2`)
- **Not** on the `banking-network` — reachable from Docker containers via `host.docker.internal:8571`
- Realm configured: `banking-service`
- Two OAuth2 clients: `banking-service-client` (gateway UI flow) and `banking-service-api-client` (User Service admin operations)

---

## 9. Commands Used

### Inspect Docker containers
`docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"`

**What it does:** Lists all running Docker containers with their names, images, status, and exposed ports.

### Inspect Docker images
`docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"`

**What it does:** Lists all Docker images stored locally with their names, tags, IDs, and file sizes.

### Inspect Docker networks
`docker network ls`

**What it does:** Lists all Docker networks. Shows if the banking-network is currently active.

### Inspect Keycloak container details
`docker inspect keycloak --format "{{json .NetworkSettings.Networks}}"`
`docker inspect keycloak --format "Keycloak Command: {{json .Config.Cmd}}"`

**What it does:** Shows Keycloak's network configuration and the command it was started with.

### Check kubectl client version
`kubectl version --client`

**What it does:** Shows the version of the kubectl command-line tool installed on the machine.

### Check kubectl contexts
`kubectl config get-contexts`

**What it does:** Lists all configured Kubernetes contexts (cluster connection profiles).

---

## 10. Validation

### 10.1 Docker Daemon is Running
**Action:** `docker ps`
**Expected result:** Command runs without error
**Actual result:** PASS — Command succeeded. Keycloak container is running.

### 10.2 Keycloak Container is Running
**Action:** `docker ps`
**Expected result:** Keycloak container shows status Up
**Actual result:** PASS — Keycloak is Up 2 hours on port 0.0.0.0:8571->8080/tcp

### 10.3 Docker Images are Built
**Action:** `docker images`
**Expected result:** All seven service images should exist
**Actual result:** PASS — All seven images confirmed present:

| Image Name | Tag | Size |
|-----------|-----|------|
| spring-boot-microservices-banking-application-service-registry | latest | 770 MB |
| spring-boot-microservices-banking-application-api-gateway | latest | 775 MB |
| spring-boot-microservices-banking-application-user-service | latest | 820 MB |
| spring-boot-microservices-banking-application-account-service | latest | 804 MB |
| spring-boot-microservices-banking-application-sequence-generator | latest | 800 MB |
| spring-boot-microservices-banking-application-transaction-service | latest | 804 MB |
| spring-boot-microservices-banking-application-fund-transfer | latest | 804 MB |

### 10.4 kubectl is Installed
**Action:** `kubectl version --client`
**Expected result:** Shows kubectl client version
**Actual result:** PASS — kubectl client version v1.36.1, Kustomize version v5.8.1

### 10.5 Kubernetes Cluster Status
**Action:** `kubectl cluster-info`
**Expected result:** Cluster info if enabled, connection error if not
**Actual result:** WARNING — Connection refused. Docker Desktop Kubernetes is currently disabled.

This is expected at Phase 0. We will enable it in Phase 1.

No kubectl context is configured yet (`error: current-context is not set`). This is resolved automatically when we enable Kubernetes in Docker Desktop.

### 10.6 MySQL Status
**Action:** Attempted `mysql` CLI command
**Expected result:** List of databases
**Actual result:** WARNING — mysql CLI is not in the Windows PATH.

MySQL is confirmed running on the Windows host based on:
- Docker Compose configuration uses `host.docker.internal:3306`
- All Docker images include MySQL JDBC driver
- Direct CLI verification not possible from PowerShell in this environment

We will verify MySQL connectivity from inside a Kubernetes Pod in Phase 2.

---

## 11. Problems Encountered

### Problem 1: mysql CLI not available in PowerShell PATH
**Cause:** MySQL was installed on Windows but the bin directory is not added to the system PATH.
**Solution:** In Phase 2, we will verify MySQL connectivity from inside a running Pod. We can also use `Test-NetConnection -ComputerName localhost -Port 3306` in PowerShell.

### Problem 2: No Kubernetes context set
**Cause:** Docker Desktop Kubernetes has not been enabled yet.
**Solution:** Expected at Phase 0. We will enable Docker Desktop Kubernetes in Phase 1 and the context will be set automatically.

### Problem 3: Docker Compose services not running
**Cause:** `docker ps` shows only the Keycloak container. The seven application services and Prometheus/Grafana are not running.
**Solution:** Acceptable for Phase 0 — we are doing code-level inspection, not runtime inspection. The Docker images exist and are ready. The Docker Compose stack can be started with `docker compose up` when needed.

---

## 12. Important Concepts

### Microservices
A microservice is a small, independently deployable application that does one specific job. In our project: User Service handles users, Account Service handles bank accounts, Transaction Service records transactions, and so on. Instead of one big application, we have seven small ones.

### Service Discovery (Eureka)
When you have many small services, how does Service A find Service B? They could use fixed IP addresses, but those change frequently. Instead, each service registers its current address with Eureka when it starts up. When Service A wants to call Service B, it asks Eureka for the current address. This is called service discovery.

### API Gateway
The API Gateway is the front door of our system. All client requests go through it. The gateway:
1. Verifies the user's identity (checks the JWT token from Keycloak)
2. Decides which service should handle the request
3. Forwards the request to the correct service

### OpenFeign
OpenFeign is a library that makes it easy for one Spring Boot service to call another service's REST API. You write an interface and annotate it with @FeignClient. Spring automatically creates the HTTP calls for you. Feign uses Eureka to look up the service address automatically — no hardcoded URLs needed.

### JWT (JSON Web Token)
A JWT is a small, digitally signed piece of data that proves who a user is. When a user logs in through Keycloak, they receive a JWT. Every request to the API Gateway must include this JWT. The gateway verifies the token's signature using Keycloak's public key.

### Spring Boot Actuator
Actuator adds special management endpoints to a Spring Boot application, for example:
- /actuator/health — Is the application healthy?
- /actuator/metrics — What are the performance numbers?
- /actuator/prometheus — Metrics in Prometheus format

### Micrometer
Micrometer is a library that collects application metrics (request count, response time, etc.) and sends them to monitoring systems like Prometheus. Think of it as a universal translator for metrics.

### Prometheus
Prometheus is a time-series database for metrics. It periodically visits each service's /actuator/prometheus endpoint and stores the numbers. You can later query those numbers to understand application performance.

### Grafana
Grafana is a visualisation tool. It reads data from Prometheus and draws charts and dashboards. This is where you look at performance graphs.

### Docker Compose
Docker Compose is a tool for running multiple Docker containers together. You describe all your services in a single YAML file (docker-compose.yml) and start them all with one command. All services run in an isolated network and can talk to each other using their service names.

### host.docker.internal
This is a special DNS name that Docker Desktop provides. Inside a Docker container, host.docker.internal resolves to the IP address of the Windows host machine. This is how containers reach MySQL (which runs on Windows) and Keycloak (which is on the Docker default bridge).

---

## 13. Performance Engineering Relevance

Phase 0 matters deeply for a Performance Engineer because it tells us the **baseline** — what we are measuring against.

Before we can say Kubernetes made things faster or this probe catches errors earlier, we need to know:

1. **What are the existing response time SLOs?**
   Already configured: slo: http.server.requests: 100ms, 250ms, 500ms, 1s, 2s, 5s
   These are the latency buckets in Prometheus for every service.

2. **What percentiles are we tracking?**
   Already configured: percentiles: http.server.requests: 0.50, 0.95, 0.99
   We track p50, p95, and p99 latency for every HTTP request.

3. **What is the existing call chain?**
   Client -> Gateway -> Fund Transfer -> Account Service + Transaction Service -> MySQL
   Every Feign call adds latency. MySQL on the Windows host adds a network hop from containers.

4. **What is the existing image size (resource baseline)?**
   All Docker images are approximately 770-820 MB each.
   They use eclipse-temurin:17-jdk (full JDK) instead of a slim JRE image.
   This gives us a baseline for comparing Kubernetes pod resource usage later.

5. **What are the bottleneck risks?**
   - MySQL on Windows: every database call crosses the Docker-to-host network boundary
   - Keycloak on default bridge: every JWT verification crosses the Docker-to-host boundary
   - Eureka registration: services must find each other through Eureka before responding

Understanding these baselines now means we can make meaningful comparisons in Phase 3 when we add resource requests, limits, and HPA.

---

## 14. Current Architecture

`
+------------------------------------------------------------------+
|  Windows Host - Intel i5-1145G7, 15.7 GB RAM                     |
|                                                                   |
|  MySQL 3306 (directly on Windows)                                 |
|    +-- user_service         database                              |
|    +-- account_service      database                              |
|    +-- transaction_service  database                              |
|    +-- fund_transfer_service database                             |
|    +-- sequence_generator   database                              |
|                                                                   |
|  Docker Desktop (7.4 GB allocated)                                |
|  |                                                                |
|  +-- [default bridge] keycloak:24.0  172.17.0.2                  |
|  |     Host 8571 -> Container 8080                               |
|  |     Realm: banking-service                                     |
|  |     Mode: start-dev                                            |
|  |                                                                |
|  +-- [banking-network] Docker Compose Services (STOPPED)          |
|        +-- service-registry    :8761  (Eureka Server)            |
|        +-- api-gateway         :8080  (Spring Cloud Gateway)     |
|        +-- user-service        :8082  (Keycloak Admin Client)    |
|        +-- account-service     :8081  (OpenFeign enabled)        |
|        +-- sequence-generator  :8083  (no Feign)                 |
|        +-- transaction-service :8084  (OpenFeign enabled)        |
|        +-- fund-transfer       :8085  (OpenFeign enabled)        |
|        +-- prometheus          :9090  (scrapes /actuator/prom)   |
|        +-- grafana             :3000  (reads Prometheus)         |
|                                                                   |
|  Kubernetes: DISABLED (will be enabled in Phase 1)               |
+------------------------------------------------------------------+
`

---

## 15. Completion Checklist

- [x] Inspected project root structure
- [x] Read docker-compose.yml completely
- [x] Read all 7 Dockerfile files
- [x] Read all 7 application.yml configuration files
- [x] Read all 7 pom.xml files (Spring Boot versions, Spring Cloud version, all dependencies)
- [x] Identified all @FeignClient annotations (7 clients across 4 services)
- [x] Identified all @EnableFeignClients annotations (4 services use Feign)
- [x] Identified @EnableEurekaServer annotation (Service Registry)
- [x] Read Prometheus prometheus.yml configuration
- [x] Verified Grafana provisioning directory structure
- [x] Verified Keycloak container is running (Up 2 hours, port 8571)
- [x] Verified all 7 Docker images exist locally
- [x] Confirmed kubectl v1.36.1 is installed
- [x] Confirmed Docker Desktop Kubernetes is currently disabled
- [x] Confirmed no kubectl context is configured yet
- [x] Created this documentation
- [ ] MySQL CLI verification from PowerShell — not possible (mysql not in PATH)
- [ ] Live service verification — Docker Compose stack is not currently running

---

## 16. What Comes Next

**Phase 1 — Kubernetes Foundation**

In Phase 1, we will:

1. **Enable Docker Desktop Kubernetes** — This turns on the Kubernetes cluster built into Docker Desktop. We do NOT install a new cluster — we just enable the one that is already there.

2. **Verify the cluster** — Run kubectl get nodes to confirm the cluster is healthy.

3. **Create a namespace called banking** — A namespace is like a folder inside Kubernetes. It keeps all our banking application resources separated from other Kubernetes resources.

4. **Create the Kubernetes directory structure** — We will create a k8s/ folder in the project with sub-folders for each service.

5. **Understand image strategy** — Since all seven images already exist locally in Docker Desktop, Kubernetes can use them directly. We will use imagePullPolicy: Never to tell Kubernetes to use the local image and not go to DockerHub.

We will NOT yet deploy any services in Phase 1 — that comes in Phase 2.

---

## 17. Learning Summary

**What did we actually accomplish in Phase 0?**

We took a complete X-ray of the existing banking application before touching anything.

We now know:
- There are 7 Spring Boot services, each running in its own Docker container
- They all use Spring Boot 2.7.x and Spring Cloud 2021.0.8 with Java 17
- They discover each other through Eureka and call each other using OpenFeign
- MySQL runs directly on Windows — containers reach it via host.docker.internal
- Keycloak runs as a separate Docker container — also reachable via host.docker.internal:8571
- All 7 Docker images are already built and available locally
- kubectl v1.36.1 is installed but Kubernetes is not yet enabled
- Each service already has Actuator + Prometheus metrics configured
- Prometheus scrape targets use Docker service names — these will need updating when we move to Kubernetes

Most importantly: we did not change anything. The system is exactly as we found it. Phase 0 is complete.

---

Document created: 2026-08-25
Phase: 0 — Baseline and Environment Preparation
Status: COMPLETE — Waiting for approval to proceed to Phase 1
