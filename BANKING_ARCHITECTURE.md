# Banking Microservices Architecture

> Generated from complete analysis of source code, Kubernetes manifests, Istio configuration,
> observability stack, Grafana dashboards, and k6 test scripts. All facts verified from code.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Complete Technology Stack](#2-complete-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Core Banking Microservices](#4-core-banking-microservices)
5. [API Gateway and Request Routing](#5-api-gateway-and-request-routing)
6. [Security Architecture](#6-security-architecture)
7. [Service Discovery](#7-service-discovery)
8. [Service-to-Service Communication](#8-service-to-service-communication)
9. [Database Architecture](#9-database-architecture)
10. [Docker Architecture](#10-docker-architecture)
11. [Kubernetes Architecture](#11-kubernetes-architecture)
12. [Istio Service Mesh](#12-istio-service-mesh)
13. [Resilience and Traffic Protection](#13-resilience-and-traffic-protection)
14. [Canary Deployment](#14-canary-deployment)
15. [Observability Architecture](#15-observability-architecture)
16. [Performance Testing](#16-performance-testing)
17. [End-to-End Request Flows](#17-end-to-end-request-flows)
18. [Deployment Guide](#18-deployment-guide)
19. [Important Commands](#19-important-commands)
20. [Troubleshooting Guide](#20-troubleshooting-guide)
21. [Security Considerations](#21-security-considerations)
22. [Project Achievements](#22-project-achievements)
23. [Analysis Summary](#23-analysis-summary)

---

## 1. Project Overview

This is a **Spring Boot Microservices Banking Application** - a fully functional banking
backend split into small, independently deployable services. Instead of one large monolith,
the system is divided into specialized services each responsible for a specific banking function.

**What it solves:**
- Each banking domain (users, accounts, transactions, fund transfers) managed by a dedicated service
- Services scaled independently (e.g., scale Account Service without touching User Service)
- Each service has its own database preventing a single point of failure (database-per-service)
- Failures in one service do not cascade to others

**Main technologies:** Spring Boot 2.7.14, Spring Cloud 2021.0.8, Java 17, MySQL 8, Docker,
Kubernetes (Docker Desktop), Istio 1.23.0, Keycloak, Prometheus, Grafana, Loki, Jaeger, OTel, k6

---

## 2. Complete Technology Stack

| Category | Technology | Version | Purpose |
|---|---|---|---|
| Backend Language | Java | 17 | All microservices |
| Framework | Spring Boot | 2.7.14 | Microservice development |
| Cloud Framework | Spring Cloud | 2021.0.8 | Gateway, Eureka client, Feign |
| API Gateway | Spring Cloud Gateway (WebFlux) | 2021.0.8 | Entry point, JWT validation, routing |
| Service Discovery | Netflix Eureka | Spring Cloud | Service registration and lookup |
| HTTP Client | OpenFeign | Spring Cloud | Service-to-service REST calls |
| Security / IAM | Keycloak | External (port 8571) | JWT issuance, user management, OAuth2 |
| JWT Validation | Spring Security OAuth2 Resource Server | 2.7.x | JWT validation at API Gateway only |
| Database | MySQL | 8.x | Persistent data, one DB per service |
| ORM | Spring Data JPA / Hibernate | 2.7.x | Entity management |
| Containerization | Docker | - | Container build and run |
| Container Orchestration | Kubernetes (Docker Desktop) | - | Deployment management |
| Service Mesh | Istio | 1.23.0 | Traffic management, mTLS, observability |
| Ingress | Istio Ingress Gateway | 1.23.0 | External traffic entry to cluster |
| Metrics Collection | Micrometer + Prometheus registry | - | Metric collection at application level |
| Metrics Storage | Prometheus | v2.47.0 (Docker) / v2.45.0 (K8s) | Metrics scraping and storage |
| Visualization | Grafana | 10.1.0 / 10.1.1 | Dashboards for metrics, logs, and traces |
| Log Aggregation | Loki | 2.9.2 | Centralized log storage |
| Log Collector | Fluent Bit | 2.2.0 | Kubernetes pod log collection (DaemonSet) |
| Distributed Tracing | OpenTelemetry Java Agent | Latest | Auto-instrumentation (no code changes) |
| Trace Backend | Jaeger all-in-one | 1.47 | Trace storage and visualization |
| Trace Protocol | Zipkin-compatible / B3 Multi | - | Trace context propagation across services |
| Kubernetes Metrics | kube-state-metrics | v2.9.2 | Kubernetes object metrics |
| Service Visualization | Kiali | - | Istio service graph (config present) |
| Load Testing | k6 | - | Performance and traffic simulation |
| Build Tool | Maven | 3.8.7 | Java build management |

---

## 3. Project Structure

```
Spring-Boot-Microservices-Banking-Application/
|
+-- API-Gateway/            <- Spring Cloud Gateway (port 8080)
+-- Account-Service/        <- Account management (port 8081)
+-- User-Service/           <- User management + Keycloak integration (port 8082)
+-- Sequence-Generator/     <- Account number generation (port 8083)
+-- Transaction-Service/    <- Transaction management (port 8084)
+-- Fund-Transfer/          <- Fund transfer orchestration (port 8085)
+-- Service-Registry/       <- Eureka server (port 8761)
|
+-- k8s/                    <- All Kubernetes manifests
|   +-- namespace.yaml              (banking namespace)
|   +-- banking-configmap.yaml      (shared non-sensitive config)
|   +-- banking-secret.yaml         (DB + Keycloak secrets, base64)
|   +-- api-gateway/                (deployment + NodePort service)
|   +-- user-service/
|   +-- account-service/            (deployment with version:v1 pod label)
|   +-- transaction-service/
|   +-- fund-transfer/
|   +-- sequence-generator/
|   +-- eureka/
|   +-- istio-ingress.yaml          (Gateway + base VirtualService)
|   +-- istio-mtls.yaml             (PeerAuthentication STRICT mTLS)
|   +-- istio-phase5-comprehensive.yaml  <- MAIN Istio config (use this)
|   +-- istio-traffic-management.yaml   (User Service specific traffic)
|   +-- istio-fault-injection.yaml      (Testing tool ONLY - 100% 503 injection)
|   +-- istio-local-overlay.yaml        (NodePort mode for Docker Desktop)
|   +-- monitoring/
|       +-- prometheus.yaml
|       +-- grafana.yaml
|       +-- loki.yaml
|       +-- jaeger.yaml
|       +-- fluent-bit.yaml
|       +-- kube-state-metrics.yaml
|       +-- istio-cm.yaml           (Istio mesh config with Jaeger extension provider)
|       +-- istio-telemetry.yaml    (100% trace sampling configuration)
|
+-- grafana/provisioning/
|   +-- datasources/datasource.yml  (Prometheus + Loki + Jaeger sources)
|   +-- dashboards/                 (8 pre-built JSON dashboards)
|
+-- prometheus/prometheus.yml       (Kubernetes pod scraping config)
+-- performance/scripts/            (7 k6 test scripts)
|   +-- load-test.js, stress-test.js, spike-test.js
|   +-- canary-demo-test.js, istio-visualization-test.js
|   +-- baseline-test.js, debug-test.js
|   +-- scenarios/safe-workflows.js (read-only endpoint definitions)
+-- docker-compose.yml              (Local stack with Prometheus + Grafana)
+-- build_all.bat                   (Build all 7 Maven projects)
+-- opentelemetry-javaagent.jar     (OTel agent - embedded in every Docker image)
+-- istio-1.23.0/                   (Istio 1.23.0 CLI binaries for Windows)
```

---

## 4. Core Banking Microservices

### 4.1 API Gateway

| Property | Value |
|---|---|
| Spring App Name | api-gateway |
| Port | 8080 (NodePort 30080 in Kubernetes) |
| Framework | Spring Cloud Gateway (WebFlux - reactive, non-blocking) |
| Spring Boot | 2.7.14 / Spring Cloud 2021.0.8 |

**Responsibility:** The ONLY public entry point for all external requests. Routes based on
path, validates JWT from Keycloak, resolves targets via Eureka, and forwards requests.

**Routes configured (verified from API-Gateway/src/main/resources/application.yml):**

| Route ID | Path Pattern | Target Service |
|---|---|---|
| user-service | /api/users/** | lb://user-service |
| fund-transfer-service | /api/fund-transfers/** | lb://fund-transfer-service |
| account-service | /accounts/** | lb://account-service |
| sequence-generator | /sequence/** | lb://sequence-generator |
| transaction-service | /transactions/** | lb://transaction-service |
| fund-transfer-service-raw | /fund-transfers/** | lb://fund-transfer-service |

**JWT validation:** OAuth2 Resource Server. Validates JWT against Keycloak JWKS endpoint:
`
http://localhost:8571/realms/banking-service/protocol/openid-connect/certs
`

**pom.xml key dependencies:** spring-cloud-starter-gateway, spring-cloud-starter-netflix-eureka-client,
spring-boot-starter-oauth2-resource-server, micrometer-registry-prometheus, spring-cloud-starter-sleuth

**Actuator endpoints:** health, info, metrics, prometheus (exposed explicitly in application.yml)

---

### 4.2 Service Registry (Eureka)

| Property | Value |
|---|---|
| Spring App Name | SERVICE-REGISTRY |
| Port | 8761 |
| Technology | Spring Cloud Netflix Eureka Server |

**Responsibility:** Service directory. Every microservice registers on startup. Other services
query it to find target service instances. API Gateway resolves lb://service-name via Eureka.

**Configuration:** register-with-eureka=false, fetch-registry=false (standalone, not clustered)

In Kubernetes, all services reach Eureka at: http://service-registry:8761/eureka/
("service-registry" resolves via Kubernetes DNS to the Eureka ClusterIP).

---

### 4.3 User Service

| Property | Value |
|---|---|
| Spring App Name | user-service |
| Port | 8082 |
| Database | MySQL - user_service schema |
| Keycloak Client | banking-service-api-client (client_credentials grant) |

**Responsibility:** Manages banking users. Registration creates user in both local MySQL AND
Keycloak (disabled). Admin approval enables the Keycloak account so user can obtain JWT tokens.

**Key APIs (base path: /api/users):**

| Method | Path | Description |
|---|---|---|
| POST | /register | Create user in MySQL + Keycloak (disabled initially) |
| GET | / | Get all users |
| GET | /{userId} | Get user by ID |
| GET | /auth/{authId} | Get user by Keycloak UUID |
| GET | /accounts/{accountId} | Get user by account ID |
| PATCH | /{id} | Update status: PENDING -> APPROVED enables Keycloak account |
| PUT | /{id} | Update user details |

**Keycloak integration (KeycloakServiceImpl.java verified):**
Uses org.keycloak.admin.client.resource.UsersResource to create/read/update users.
Realm: banking-service. When APPROVED: enabled=true, emailVerified=true set on Keycloak user.

**Feign client:** AccountService -> GET /accounts?accountNumber= (used for get-user-by-account-id)

---

### 4.4 Account Service

| Property | Value |
|---|---|
| Spring App Name | account-service |
| Port | 8081 |
| Database | MySQL - account_service schema |
| Canary Pod Label | version: v1 (for Istio traffic splitting) |

**Responsibility:** Creates and manages bank accounts. Account creation calls UserService
(verify user) and SequenceService (get account number). Stores result in MySQL.

**Account number format:** ACC + 7-digit zero-padded sequence (e.g., ACC0000001)
**Account lifecycle:** PENDING -> ACTIVE -> CLOSED
**Minimum balance to activate:** Rs. 1000

**Key APIs (base path: /accounts):**

| Method | Path | Description |
|---|---|---|
| POST | / | Create account (calls User + Sequence services) |
| GET | ?accountNumber=... | Get account by number |
| PUT | ?accountNumber=... | Update account fields |
| PATCH | ?accountNumber=... | Update status |
| GET | /balance?accountNumber=... | Get balance |
| GET | /{accountId}/transactions | Get transaction history (calls Transaction Service) |
| PUT | /closure?accountNumber=... | Close account (balance must be exactly 0) |
| GET | /{userId} | Get account by user ID (returns first ACTIVE account) |

**Feign clients (3):** UserService, SequenceService, TransactionService

---

### 4.5 Sequence Generator

| Property | Value |
|---|---|
| Spring App Name | sequence-generator |
| Port | 8083 |
| Database | MySQL - sequence_generator schema |

**Responsibility:** Internal utility service. Generates unique sequential account numbers.
Only called by Account Service. No business logic beyond sequential number generation.

**API:** POST /sequence -> returns Sequence entity with next auto-increment number.

---

### 4.6 Transaction Service

| Property | Value |
|---|---|
| Spring App Name | transaction-service |
| Port | 8084 |
| Database | MySQL - transaction_service schema |

**Responsibility:** Records all financial transactions. Validates accounts, updates balances
through Account Service Feign client, persists records.

**Transaction Types:** DEPOSIT, WITHDRAWAL, INTERNAL_TRANSFER

**Key APIs (base path: /transactions):**

| Method | Path | Description |
|---|---|---|
| POST | / | Record deposit or withdrawal |
| POST | /internal?transactionReference=... | Record 2 internal transfer entries (DEBIT + CREDIT) |
| GET | ?accountId=... | Get all transactions for account |
| GET | /{referenceId} | Get by reference ID |

**Feign client:** AccountService -> GET (validate) and PUT (update balance)

---

### 4.7 Fund Transfer Service

| Property | Value |
|---|---|
| Spring App Name | fund-transfer-service |
| Port | 8085 |
| Database | MySQL - fund_transfer_service schema |

**Responsibility:** Saga coordinator for fund transfers. Validates both accounts, updates
balances, creates transaction records, persists transfer record.

**Key APIs (base path: /api/fund-transfers or /fund-transfers):**

| Method | Path | Description |
|---|---|---|
| POST | / | Initiate fund transfer |
| GET | /{referenceId} | Get transfer by reference UUID |
| GET | ?accountId=... | Get all transfers for account |

**Validation before transfer:**
1. Source account exists and is ACTIVE
2. Source has sufficient balance
3. Destination account exists

**Feign clients:** AccountService (4 calls: 2 reads + 2 updates), TransactionService (1 call - creates 2 records)

---

## 5. API Gateway and Request Routing

The API Gateway is the ONLY public-facing entry point. All client requests pass through it.

**How routing works:**
1. Client sends request (port 8080 locally, 30080 K8s NodePort, or 31380 Istio Ingress)
2. Gateway matches path against route table
3. Resolves lb://service-name -> Spring Cloud LoadBalancer asks Eureka for pod IPs
4. Eureka returns registered pod IP
5. Gateway forwards request (via Istio Envoy sidecar when in Kubernetes)

**NOTE on Eureka vs Kubernetes DNS:**
Services register with Eureka using pod IPs (EUREKA_INSTANCE_PREFERIPADDRESS=true).
Feign clients go through Eureka, NOT Kubernetes DNS directly.

---

## 6. Security Architecture

### Keycloak Configuration

| Property | Value |
|---|---|
| Keycloak URL | http://localhost:8571 (Windows host machine) |
| Realm | banking-service |
| Gateway Client | banking-service-client (authorization_code for user login) |
| User Service Client | banking-service-api-client (client_credentials for admin ops) |

### Authentication Flow

`
Step 1: User Registration
  Client -> POST /api/users/register
  User Service:
    - Creates user in Keycloak (disabled)
    - Saves user to MySQL (status=PENDING, authId=Keycloak UUID)
  Admin -> PATCH /api/users/{id} {status: APPROVED}
  User Service:
    - Keycloak: enabled=true, emailVerified=true
    - MySQL: status=APPROVED

Step 2: Login (Get JWT)
  Client -> POST http://keycloak:8571/realms/banking-service/protocol/openid-connect/token
    Body: grant_type=password, username, password, client_id=banking-service-client
  <- Returns { access_token: "eyJ...", expires_in: 300 }

Step 3: API Call
  Client -> API Gateway with "Authorization: Bearer <JWT>"
  Gateway:
    - Fetches JWKS from Keycloak (cached)
    - Validates JWT signature + expiry
    - If valid: routes to target service
    - If invalid: 401 Unauthorized
`

**CRITICAL:** Only API Gateway validates JWT. Backend services do NOT independently
validate tokens - they trust that gateway-forwarded requests are already authenticated.

### Kubernetes Secrets (banking-secret)

| Key | Purpose |
|---|---|
| mysql-username | DB username (root) |
| mysql-password | DB password (Netcracker@123) |
| keycloak-gateway-secret | API Gateway OAuth2 client secret |
| keycloak-api-secret | User Service Keycloak admin secret |

> WARNING: Kubernetes Secrets are only base64-encoded, NOT encrypted. Use Vault or cloud KMS for production.

---

## 7. Service Discovery

Eureka runs at port 8761 as standalone service registry.

**Startup sequence:**
1. Microservice starts
2. Registers with Eureka (name, IP, port)
3. Sends heartbeat every 30 seconds
4. 3 missed heartbeats -> Eureka removes service from registry

**In Kubernetes:**
`
EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka/
EUREKA_INSTANCE_PREFERIPADDRESS=true
`
"service-registry" resolves via Kubernetes DNS to Eureka ClusterIP.
Pod IPs are registered (not pod hostnames) so Feign can connect directly.

---

## 8. Service-to-Service Communication

All inter-service calls are SYNCHRONOUS HTTP REST via OpenFeign.
NO asynchronous messaging (no Kafka, no RabbitMQ, no event bus).

### Complete Feign Client Map (verified from source code)

`
User Service      -> Account Service     : GET /accounts?accountNumber=...
Account Service   -> User Service        : GET /api/users/{userId}
Account Service   -> Sequence Generator  : POST /sequence
Account Service   -> Transaction Service : GET /transactions?accountId=...
Fund Transfer     -> Account Service     : GET /accounts?accountNumber=... (x2: source + dest)
Fund Transfer     -> Account Service     : PUT /accounts?accountNumber=... (x2: debit + credit)
Fund Transfer     -> Transaction Service : POST /transactions/internal
Transaction Svc   -> Account Service     : GET /accounts?accountNumber=...
Transaction Svc   -> Account Service     : PUT /accounts?accountNumber=...
`

### Full Feign Client Table

| Caller | Target | Method | Endpoint | Purpose |
|---|---|---|---|---|
| User Service | Account Service | GET | /accounts?accountNumber= | Find user by account |
| Account Service | User Service | GET | /api/users/{userId} | Verify user before creating account |
| Account Service | Sequence Generator | POST | /sequence | Get next account number |
| Account Service | Transaction Service | GET | /transactions?accountId= | Get transaction history |
| Fund Transfer | Account Service | GET | /accounts?accountNumber= | Validate source account |
| Fund Transfer | Account Service | GET | /accounts?accountNumber= | Validate destination account |
| Fund Transfer | Account Service | PUT | /accounts?accountNumber= | Deduct from source |
| Fund Transfer | Account Service | PUT | /accounts?accountNumber= | Credit to destination |
| Fund Transfer | Transaction Service | POST | /transactions/internal | Create 2 transaction records |
| Transaction Service | Account Service | GET | /accounts?accountNumber= | Validate account |
| Transaction Service | Account Service | PUT | /accounts?accountNumber= | Update balance |

---

## 9. Database Architecture

Database-per-service pattern: each service owns its own MySQL schema.
No service directly queries another service's database.

| Microservice | MySQL Schema | Key Entities |
|---|---|---|
| User Service | user_service | users (userId, emailId, contactNo, identificationNumber, status, authId) |
| Account Service | account_service | accounts (accountNumber, accountType, accountStatus, availableBalance, userId) |
| Transaction Service | transaction_service | transactions (accountId, transactionType, amount, status, referenceId, transactionDate) |
| Fund Transfer | fund_transfer_service | fund_transfers (fromAccount, toAccount, amount, status, transactionReference, transferType) |
| Sequence Generator | sequence_generator | sequences (auto-increment counter) |
| Service Registry | None | In-memory only |
| API Gateway | None | Stateless |

**MySQL access by environment:**

| Environment | Connection String |
|---|---|
| Local dev | localhost:3306 |
| Docker Compose | host.docker.internal:3306 |
| Kubernetes | host.docker.internal:3306 (MySQL on Windows host, NOT in K8s) |

**DDL:** hibernate.ddl-auto=update (Hibernate auto-manages schema).

> IMPORTANT: MySQL is NOT inside Kubernetes. It runs on the Windows host machine.
> No StatefulSets or PVCs for MySQL exist in this project.
> The only PVC is loki-pvc (10Gi) in the monitoring namespace for Loki log storage.

---

## 10. Docker Architecture

### Docker Compose Services

| Container | Image | Host Port |
|---|---|---|
| service-registry | Built from ./Service-Registry | 8761 |
| api-gateway | Built from ./API-Gateway | 8080 |
| user-service | Built from ./User-Service | 8082 |
| account-service | Built from ./Account-Service | 8081 |
| transaction-service | Built from ./Transaction-Service | 8084 |
| fund-transfer | Built from ./Fund-Transfer | 8085 |
| sequence-generator | Built from ./Sequence-Generator | 8083 |
| prometheus | prom/prometheus:v2.47.0 | 9090 |
| grafana | grafana/grafana:10.1.0 | 3000 |

All containers join banking-network (Docker bridge).
MySQL (port 3306) and Keycloak (port 8571) run on the Windows host - accessed via host.docker.internal.

**Docker volumes:** prometheus-data, grafana-data (local driver, persistent).

### Dockerfile Pattern (all 7 services, verified)

```dockerfile
FROM eclipse-temurin:17-jdk
WORKDIR /app
COPY target/*.jar app.jar
COPY opentelemetry-javaagent.jar opentelemetry-javaagent.jar
EXPOSE <service-port>
ENTRYPOINT ["java", "-javaagent:opentelemetry-javaagent.jar", "-jar", "app.jar"]
```

OTel Java Agent embedded in EVERY image. Auto-instruments Spring Boot, Feign, JDBC without code changes.

### Kubernetes Image Registry

All K8s deployments pull from: localhost:5001/banking/<service-name>:latest
Local registry must be running (docker run -d -p 5001:5000 --name registry registry:2).

---

## 11. Kubernetes Architecture

### Namespace Layout

| Namespace | Contents |
|---|---|
| banking | API Gateway, 5 business services, Eureka (all with Istio sidecar) |
| monitoring | Prometheus, Grafana, Loki, Jaeger, Fluent Bit DaemonSet, kube-state-metrics |
| istio-system | Istio control plane (istiod), Ingress Gateway (NodePort 31380) |

### Banking Namespace Deployments

| Deployment | Container Port | K8s Service | External Port |
|---|---|---|---|
| api-gateway | 8080 | NodePort | 30080 |
| user-service | 8082 | ClusterIP | - |
| account-service | 8081 | ClusterIP | - |
| transaction-service | 8084 | ClusterIP | - |
| fund-transfer | 8085 | ClusterIP | - |
| sequence-generator | 8083 | ClusterIP | - |
| service-registry | 8761 | ClusterIP | - |

All: 1 replica, imagePullPolicy: IfNotPresent, image: localhost:5001/banking/<name>:latest

### Resource Limits

| Service | CPU Req/Limit | Memory Req/Limit | JVM Heap |
|---|---|---|---|
| api-gateway | 100m / 500m | 256Mi / 512Mi | -Xms256m -Xmx512m |
| user-service | 100m / 500m | 256Mi / 512Mi | -Xms256m -Xmx512m |
| account-service | 100m / 500m | 256Mi / 512Mi | -Xms256m -Xmx512m |
| transaction-service | 100m / 500m | 256Mi / 512Mi | -Xms256m -Xmx512m |
| fund-transfer | 100m / 500m | 256Mi / 512Mi | -Xms256m -Xmx512m |
| sequence-generator | 100m / 500m | 256Mi / 256Mi | -Xms128m -Xmx256m |
| service-registry | 100m / 500m | 256Mi / 512Mi | -Xms128m -Xmx256m |

### Health Probes

| Probe | Path | Initial Delay | Period |
|---|---|---|---|
| Readiness | /actuator/health/readiness | 30s | 10s |
| Liveness | /actuator/health/liveness | 60s | 15s |
| Startup (account only) | /actuator/health/liveness | Up to 200s | 5s |

### Configuration Injection

**ConfigMap banking-config:**
- EUREKA_CLIENT_SERVICEURL_DEFAULTZONE = http://service-registry:8761/eureka/
- EUREKA_INSTANCE_PREFERIPADDRESS = true
- MYSQL_HOST = host.docker.internal
- APP_CONFIG_KEYCLOAK_URL = http://host.docker.internal:8571/
- OTEL_EXPORTER_ZIPKIN_ENDPOINT = http://jaeger-collector.monitoring.svc.cluster.local:9411/api/v2/spans

**Secret banking-secret:** mysql-username, mysql-password, keycloak-gateway-secret, keycloak-api-secret

### Monitoring Namespace

| Workload | Type | Image | Ports |
|---|---|---|---|
| prometheus | Deployment 1 replica | prom/prometheus:v2.45.0 | 9090 |
| grafana | Deployment 1 replica | grafana/grafana:10.1.1 | 3000 |
| loki | Deployment 1 replica | grafana/loki:2.9.2 | 3100 |
| jaeger | Deployment 1 replica | jaegertracing/all-in-one:1.47 | 16686, 9411 |
| fluent-bit | DaemonSet (every node) | cr.fluentbit.io/fluent/fluent-bit:2.2.0 | 2020 |
| kube-state-metrics | Deployment 1 replica | registry.k8s.io/kube-state-metrics:v2.9.2 | 8080 |

Loki PVC: loki-pvc, 10Gi, standard storage class.

---

## 12. Istio Service Mesh

Istio 1.23.0 in istio-system namespace. Injects Envoy sidecar into pods in namespaces
labeled istio-injection=enabled.

### How Envoy Sidecars Work

Pod gets 2 containers: application + Envoy sidecar (injected automatically by Istio).
All network traffic flows through Envoy - app container never handles raw TCP.

`
Incoming request
      |
      v
Envoy sidecar (:15001) - intercepts ALL inbound
      |
      v
Application container (e.g., :8081)
      |
      v
Envoy sidecar (outbound) - intercepts ALL outbound
      | encrypted mTLS channel
      v
Destination pod Envoy sidecar -> Destination app
`

### mTLS - banking namespace

PeerAuthentication STRICT mode:
`yaml
kind: PeerAuthentication
namespace: banking
spec:
  mtls:
    mode: STRICT
`
ALL pod-to-pod traffic encrypted via mTLS. Application code is unaware - Envoy handles certs.

### Istio Gateway

banking-gateway listens on HTTP port 80, accepts all hosts (*).
On Docker Desktop: NodePort mode via istio-local-overlay.yaml (avoids Windows HTTP.sys conflict).

### VirtualServices and DestinationRules (istio-phase5-comprehensive.yaml)

#### API Gateway Traffic Policy
- VirtualService timeout: 15 seconds
- DestinationRule mTLS: ISTIO_MUTUAL
- Outlier Detection: 5 consecutive 5xx -> eject 30s

#### User Service Traffic Policy
- GET: 5s timeout, 2 retries (2s each), on connect-failure/refused-stream/503
- Other: 5s timeout
- Load Balancer: ROUND_ROBIN
- Outlier Detection: 5 consecutive 5xx -> eject 30s (max 100% ejection)

#### Account Service Traffic Policy (Canary)
- Subsets: v1 (label version:v1), v2 (label version:v2)
- Traffic split: 50% -> v1, 50% -> v2 (all request methods)
- GET retries: 2 attempts, 2s/attempt
- Timeout: 5s
- Outlier Detection: 5 consecutive 5xx -> eject 30s

#### Fund Transfer Traffic Policy
- GET: 5s timeout, 2 retries (2s each)
- POST/write: 10s timeout
- Outlier Detection: 5 consecutive 5xx -> eject 30s

#### Transaction Service Traffic Policy
- GET: 5s timeout, 2 retries (2s each)
- POST/write: 10s timeout
- Outlier Detection: 5 consecutive 5xx -> eject 30s

#### Sequence Generator Traffic Policy
- All methods: 3s timeout
- Outlier Detection: 5 consecutive 5xx -> eject 30s

### Istio Telemetry (verified from istio-cm.yaml and istio-telemetry.yaml)

`yaml
# istio-cm.yaml mesh config
defaultProviders:
  metrics: [prometheus]
  tracing: [jaeger]
extensionProviders:
  - name: jaeger
    zipkin:
      service: jaeger-collector.monitoring.svc.cluster.local
      port: 9411
      maxTagLength: 256
enablePrometheusMerge: true

# istio-telemetry.yaml
tracing:
  randomSamplingPercentage: 100.0   # Every request generates a trace
`

---

## 13. Resilience and Traffic Protection

### Implemented Features

| Feature | Technology | Configuration |
|---|---|---|
| Circuit Breaking (Outlier Detection) | Istio DestinationRule | 5 consecutive 5xx -> eject 30s |
| Request Timeouts | Istio VirtualService | 3s (seq-gen) to 15s (api-gateway) |
| Automatic Retries | Istio VirtualService | 2 attempts, 2s/attempt, on 503/conn failures |
| mTLS Encryption | Istio PeerAuthentication | STRICT mode for entire banking namespace |
| Resource Limits | Kubernetes Deployment | CPU 100m-500m, Memory 256Mi-512Mi |

### NOT Implemented
- Rate Limiting: No EnvoyFilter, no rate limit service
- Application Circuit Breaker: No Resilience4j

### Outlier Detection Explained

`
1. Envoy tracks per-pod success/failure counts
2. If pod returns 5 consecutive 5xx errors in 10s window
3. Envoy ejects that pod from load balancing pool for 30s
4. Traffic goes to remaining healthy pods only
5. After 30s pod is readmitted and monitored again
`

Configuration (same across all services in istio-phase5-comprehensive.yaml):
`yaml
outlierDetection:
  consecutive5xxErrors: 5
  interval: 10s
  baseEjectionTime: 30s
`

### Timeout Table

| Service | GET Timeout | POST/Write Timeout |
|---|---|---|
| API Gateway | 15s | 15s |
| User Service | 5s | 5s |
| Account Service | 5s | 5s |
| Fund Transfer | 5s | 10s |
| Transaction Service | 5s | 10s |
| Sequence Generator | 3s | 3s |

### Retry Policy (GET requests for User, Account, Fund Transfer, Transaction)

`yaml
retries:
  attempts: 2
  perTryTimeout: 2s
  retryOn: connect-failure, refused-stream, 503
`
Does NOT retry on 4xx client errors.

> WARNING: k8s/istio-fault-injection.yaml injects 100% 503 into User Service.
> DO NOT apply in production. Testing tool only.

---

## 14. Canary Deployment

Account Service has canary infrastructure via Istio traffic splitting.

### How It Works

**Pod version labels:**
`yaml
# Current k8s/account-service/deployment.yaml
labels:
  app: account-service
  version: v1        # <- This label enables canary routing

# Deploy separately for canary
labels:
  app: account-service
  version: v2
`

**DestinationRule subsets (istio-phase5-comprehensive.yaml):**
`yaml
subsets:
  - name: v1
    labels: { version: v1 }
  - name: v2
    labels: { version: v2 }
`

**VirtualService 50/50 split (current):**
`yaml
route:
  - destination:
      host: account-service.banking.svc.cluster.local
      subset: v1
    weight: 50
  - destination:
      host: account-service.banking.svc.cluster.local
      subset: v2
    weight: 50
`

### Canary Rollout Workflow

`
1. Deploy v2 pod alongside v1 (both run simultaneously)
2. Start conservative: 90% v1 / 10% v2
3. Monitor Kiali service graph + Grafana Istio/Envoy dashboard
4. If v2 healthy: shift to 70/30, then 50/50, then 0/100
5. If v2 has issues: rollback to 100/0 instantly via kubectl apply
`

**Current state:** Only v1 pods deployed. 50/50 VirtualService routes both weights to v1.
Deploy a second Deployment (version:v2 label) to activate actual traffic splitting.

**k6 canary test (canary-demo-test.js):** 8 VUs, 10 minutes, Account Service GET endpoints.
Generates traffic visible in Kiali service graph during weight changes.

---

## 15. Observability Architecture

Three pillars: Metrics (Prometheus + Grafana), Logs (Loki + Fluent Bit), Traces (Jaeger + OTel).

### A. Metrics Pipeline

`
Banking Service /actuator/prometheus
    |
    v (scraped every 15 seconds)
Prometheus (monitoring namespace, port 9090)
Discovers banking pods via kubernetes_sd_configs + prometheus.io/scrape=true annotation
Also scrapes kube-state-metrics for Kubernetes object metrics
    |
    v
Grafana (Prometheus datasource, default)
`

**Pod annotation required for scraping:**
`yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/path: /actuator/prometheus
  prometheus.io/port: "<service-port>"
`

**Metrics histogram config (all services):**
`yaml
management.metrics.distribution:
  percentiles-histogram.all: true
  percentiles.http.server.requests: 0.50, 0.95, 0.99
  slo.http.server.requests: 100ms, 250ms, 500ms, 1s, 2s, 5s
`

Istio metrics merged: enablePrometheusMerge=true in istio-cm.yaml merges Envoy sidecar
metrics into each pod's /actuator/prometheus endpoint.

### B. Centralized Logging Pipeline

`
Banking Pod stdout/stderr
    | Container runtime -> /var/log/containers/*_banking_*.log
    v
Fluent Bit DaemonSet (on every K8s node)
    | Reads: /var/log/containers/*_banking_*.log (banking namespace only)
    | Parsers: docker JSON and CRI format
    | Kubernetes filter: adds namespace, pod, container, app labels
    | Lua script: extracts clean message text
    v
Loki (monitoring namespace, port 3100)
    | Retention: 168 hours (7 days)
    | Query timeout: 120s
    | Max outstanding requests: 256/tenant
    | Split queries by: 15 minute intervals
    v
Grafana (Loki datasource, UID: Loki)
`

**Logging Dashboard** (phase7-logging.json - "Banking Application - Centralized Logging"):
- Total Log Volume (logs/min), Log Volume by Service, Error Log Rate, Warning Volume, Log by Pod

### C. Distributed Tracing Pipeline

`
Client Request
    v
API Gateway (OTel Java Agent -javaagent:opentelemetry-javaagent.jar)
    | Auto-creates span, injects B3 trace context headers
    v
Target Service (OTel Agent continues trace, propagates context)
    | All Feign calls also auto-instrumented
    v
Downstream services... (trace chain builds)
    |
    v (async export)
Jaeger Collector (monitoring namespace, port 9411, Zipkin format)
    v
Jaeger Query UI (port 16686) and Grafana (Jaeger datasource)
`

**OTEL env vars in all K8s deployments (verified from deployment.yaml files):**
`
OTEL_TRACES_EXPORTER=zipkin
OTEL_EXPORTER_ZIPKIN_ENDPOINT=http://jaeger-collector.monitoring.svc.cluster.local:9411/api/v2/spans
OTEL_SERVICE_NAME=<service-name>
OTEL_METRICS_EXPORTER=none
OTEL_LOGS_EXPORTER=none
OTEL_PROPAGATORS=b3multi,tracecontext
`

Service Registry: OTEL_TRACES_EXPORTER=none (Eureka excluded from tracing).
Sampling: 100% (randomSamplingPercentage: 100.0 in istio-telemetry.yaml).

### D. Grafana Dashboards (8 pre-provisioned)

| File | Dashboard Title | Datasource |
|---|---|---|
| banking-performance.json | Banking Application - Performance Engineering | Prometheus |
| phase6-application.json | Phase 6 - Application Metrics | Prometheus |
| phase6-hpa.json | Phase 6 - HPA Metrics | Prometheus |
| phase6-istio-envoy.json | Phase 6 - Istio/Envoy Metrics | Prometheus |
| phase6-jvm.json | Phase 6 - JVM Metrics | Prometheus |
| phase6-kubernetes.json | Phase 6 - Kubernetes Metrics | Prometheus |
| phase7-logging.json | Banking Application - Centralized Logging | Loki |
| phase9-performance.json | Banking Application - Performance Testing | Prometheus |

**Datasources provisioned (auto-loaded at Grafana startup):**
- Prometheus (isDefault=true): http://prometheus:9090 (Docker) / http://prometheus.monitoring.svc.cluster.local:9090 (K8s)
- Loki (UID: Loki): http://loki:3100
- Jaeger: http://jaeger-query:16686

---

## 16. Performance Testing

k6 sends load to API Gateway (BASE_URL in test-config.example.js), which routes through
Istio and all services. Results visible in Grafana "Banking Application - Performance Testing" dashboard.

### Test Scripts

| Script | VUs | Duration | Thresholds |
|---|---|---|---|
| baseline-test.js | Small | Short | - |
| load-test.js | 0->20->0 staged | 2 min | p95<2s, error<5% |
| stress-test.js | 20->50->100->0 | ~3 min | p95<3s, error<10% |
| spike-test.js | 5->100->5 | ~1 min | p95<3s |
| canary-demo-test.js | 8 fixed | 10 min | error<1% |
| istio-visualization-test.js | 10 fixed | 5 min | p95<2s, error<30% |
| debug-test.js | debug | - | - |

### Tested Endpoints (read-only GET only, no destructive operations)

`
GET /api/users
GET /api/users/{userId}
GET /accounts?accountNumber=<TEST_ACCOUNT_NUMBER>
GET /accounts/balance?accountNumber=<TEST_ACCOUNT_NUMBER>
GET /accounts/{accountId}/transactions
GET /transactions?accountId=<TEST_ACCOUNT_NUMBER>
GET /transactions/{referenceId}
GET /fund-transfers?accountId=<TEST_ACCOUNT_NUMBER>
GET /fund-transfers/{referenceId}
`

Note: istio-visualization-test.js allows error<30% because some endpoints 404/400 with test data.

---

## 17. End-to-End Request Flows

### Flow 1: User Registration and Activation

`
1. Client -> POST /api/users/register
   {firstName, lastName, emailId, password, contactNo}

2. Gateway -> user-service:8082

3. User Service:
   a. Creates Keycloak user (disabled, status=PENDING)
   b. Saves to MySQL user_service (authId=Keycloak UUID, status=PENDING)
   c. Returns 200 OK

4. Admin -> PATCH /api/users/{id} {status: APPROVED}

5. User Service:
   a. Keycloak: enabled=true, emailVerified=true
   b. MySQL: status=APPROVED
   User can now login and get JWT tokens
`

### Flow 2: Login (Get JWT)

`
Client -> POST http://keycloak:8571/realms/banking-service/protocol/openid-connect/token
  Body: grant_type=password, username=user@test.com, password=pass,
        client_id=banking-service-client, client_secret=<secret>

Keycloak validates -> returns:
  { access_token: "eyJ...", expires_in: 300, token_type: "Bearer" }

Client sends in all API calls:
  Authorization: Bearer eyJ...
`

### Flow 3: Authenticated API Request

`
Client -> GET /accounts?accountNumber=ACC0000001
          Authorization: Bearer <JWT>
    |
    v (Istio Ingress Gateway, NodePort 31380)
    v
API Gateway:
  1. Fetches Keycloak JWKS (cached public keys)
  2. Validates JWT signature and expiry
  3. If invalid -> 401 Unauthorized
  4. If valid -> asks Eureka for account-service IP
  5. Forwards to Account Service pod via Istio Envoy (mTLS)
    |
    v
Account Service -> MySQL account_service
  -> Returns AccountDto JSON
    |
    v (response path: Account Service -> Gateway -> Istio -> Client)
Client receives 200 OK + account JSON
`

### Flow 4: Fund Transfer (most complex - 5 Feign calls)

`
Client -> POST /api/fund-transfers
  {fromAccount: "ACC0000001", toAccount: "ACC0000002", amount: 500.00}
  Authorization: Bearer <JWT>

API Gateway validates JWT -> routes to fund-transfer:8085

Fund Transfer Service executes:
  [1] GET account-service /accounts?accountNumber=ACC0000001
      -> Verify: EXISTS, status=ACTIVE, balance >= 500.00

  [2] GET account-service /accounts?accountNumber=ACC0000002
      -> Verify: EXISTS

  [3] PUT account-service /accounts?accountNumber=ACC0000001
      -> Update: balance = balance - 500.00 (debit)

  [4] PUT account-service /accounts?accountNumber=ACC0000002
      -> Update: balance = balance + 500.00 (credit)

  [5] POST transaction-service /transactions/internal?transactionReference=<UUID>
      -> Creates 2 records:
         INTERNAL_TRANSFER DEBIT  : ACC0000001, -500.00
         INTERNAL_TRANSFER CREDIT : ACC0000002, +500.00

  [6] Saves fund_transfer record to fund_transfer_service DB

Returns: { transactionId: "<UUID>", message: "Fund transfer was successful" }

Total K8s-internal Feign calls: 5 (2 reads + 2 account updates + 1 transaction batch)
`

### Flow 5: Istio Retry on Failure

`
Client -> GET /api/users/{userId}
Istio forwards to user-service-pod-1 -> returns 503

Istio VirtualService detects 503 (retryOn: 503 configured)
Retry 1 -> user-service-pod-1 (or another pod) -> 200 OK -> returned to client

If retry also fails:
Retry 2 -> 2s timeout -> 503 returned to client after 4s (2 retries x 2s)
Max total: 5s (configured timeout)
`

### Flow 6: Observability (simultaneous, every request)

`
METRICS:   Service -> Micrometer -> /actuator/prometheus
           Prometheus scrapes every 15s -> Grafana displays

TRACES:    OTel Agent creates span -> exports to Jaeger :9411
           Full distributed trace visible in Jaeger UI and Grafana

LOGS:      Service writes to stdout -> container runtime logs to /var/log/containers/
           Fluent Bit reads -> sends to Loki :3100 -> Grafana queries
`

---

## 18. Deployment Guide

### Prerequisites

- Java 17 JDK, Maven 3.8+
- Docker Desktop with Kubernetes enabled
- kubectl, istioctl (istio-1.23.0/bin/ in project root)
- k6 (for load testing)
- MySQL 8.x on Windows host at port 3306
- Keycloak on Windows host at port 8571

### Step 1: Prepare MySQL

`sql
CREATE DATABASE user_service;
CREATE DATABASE account_service;
CREATE DATABASE transaction_service;
CREATE DATABASE fund_transfer_service;
CREATE DATABASE sequence_generator;
`

### Step 2: Build All Services

`at
build_all.bat
`

### Option A: Run with Docker Compose (local)

`ash
docker-compose up --build
`
Access: API Gateway :8080, Eureka :8761, Prometheus :9090, Grafana :3000 (admin/admin)

### Option B: Deploy to Kubernetes

`ash
# 1. Install Istio (NodePort mode for Docker Desktop Windows)
istio-1.23.0\bin\istioctl install -f k8s\istio-local-overlay.yaml -y

# 2. Enable sidecar injection
kubectl label namespace banking istio-injection=enabled

# 3. Start local image registry
docker run -d -p 5001:5000 --name registry registry:2

# 4. Build and push all images (repeat for each service)
docker build -t localhost:5001/banking/api-gateway:latest ./API-Gateway
docker push localhost:5001/banking/api-gateway:latest
# ... user-service, account-service, transaction-service, fund-transfer,
#     sequence-generator, service-registry

# 5. Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl create namespace monitoring
kubectl apply -f k8s/banking-configmap.yaml
kubectl apply -f k8s/banking-secret.yaml
kubectl apply -f k8s/eureka/
kubectl apply -f k8s/api-gateway/
kubectl apply -f k8s/user-service/
kubectl apply -f k8s/account-service/
kubectl apply -f k8s/transaction-service/
kubectl apply -f k8s/fund-transfer/
kubectl apply -f k8s/sequence-generator/

# 6. Apply Istio (use ONLY the comprehensive file - not both)
kubectl apply -f k8s/istio-mtls.yaml
kubectl apply -f k8s/istio-phase5-comprehensive.yaml

# 7. Deploy monitoring stack
kubectl apply -f k8s/monitoring/

# 8. Verify
kubectl get pods -n banking
kubectl get pods -n monitoring
kubectl get pods -n istio-system
`

---

## 19. Important Commands

### Build

`at
build_all.bat                                           # All 7 services
cd Account-Service && mvn clean package -DskipTests     # Single service
`

### Docker Compose

`ash
docker-compose up --build -d          # Start stack
docker-compose logs -f user-service   # Tail logs
docker-compose down                   # Stop
docker ps                             # List containers
`

### Kubernetes - Inspection

`ash
kubectl get pods -n banking
kubectl get pods -n banking -o wide
kubectl get deployments -n banking
kubectl get services -n banking
kubectl describe pod <pod-name> -n banking
kubectl logs <pod-name> -n banking
kubectl logs <pod-name> -n banking -f           # Follow
kubectl logs <pod-name> -n banking --previous   # Previous container
kubectl get events -n banking --sort-by='.lastTimestamp'
`

### Kubernetes - Operations

`ash
kubectl rollout restart deployment/user-service -n banking
kubectl scale deployment account-service --replicas=2 -n banking
kubectl rollout status deployment/user-service -n banking
kubectl apply -f k8s/istio-phase5-comprehensive.yaml
`

### Kubernetes - Port Forwarding

`ash
kubectl port-forward svc/api-gateway 8080:8080 -n banking
kubectl port-forward svc/service-registry 8761:8761 -n banking
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
kubectl port-forward svc/grafana 3000:3000 -n monitoring
kubectl port-forward svc/loki 3100:3100 -n monitoring
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
`

### Istio

`ash
istio-1.23.0\bin\istioctl verify-install
istio-1.23.0\bin\istioctl proxy-status -n banking
kubectl get virtualservices -n banking
kubectl get destinationrules -n banking
kubectl get gateway -n banking
kubectl get peerauthentication -n banking
kubectl describe virtualservice account-service-route -n banking
istio-1.23.0\bin\istioctl proxy-config routes <pod> -n banking
`

### k6 Load Tests

`ash
k6 run performance/scripts/load-test.js
k6 run performance/scripts/stress-test.js
k6 run performance/scripts/spike-test.js
k6 run performance/scripts/canary-demo-test.js
k6 run performance/scripts/istio-visualization-test.js
`

---

## 20. Troubleshooting Guide

### Pod Not Starting (Pending / ContainerCreating)

`ash
kubectl describe pod <pod-name> -n banking
kubectl get events -n banking --sort-by='.lastTimestamp'
`
Causes: image not in local registry, insufficient memory, storage class unavailable.

### CrashLoopBackOff

`ash
kubectl logs <pod-name> -n banking --previous
`
Causes: MySQL not running on host port 3306, Keycloak unreachable on port 8571,
wrong credentials in banking-secret, service-registry must start first.

### ImagePullBackOff

`ash
docker build -t localhost:5001/banking/<service>:latest ./<Service-Dir>
docker push localhost:5001/banking/<service>:latest
`

### 502/503 Service Unavailable

`ash
kubectl get pods -n banking
istio-1.23.0\bin\istioctl proxy-status -n banking
kubectl describe virtualservice api-gateway-route -n banking
`
Causes: pod not Ready (check readiness probe), Istio config conflict (KNOWN ISSUE below).

### 401 Unauthorized

Check: Keycloak running on port 8571, token not expired (default TTL ~5 min),
APP_CONFIG_KEYCLOAK_URL in ConfigMap matches actual Keycloak URL.

Test token endpoint:
`ash
curl -X POST http://localhost:8571/realms/banking-service/protocol/openid-connect/token \
  -d "grant_type=password&username=user@test.com&password=pass" \
  -d "client_id=banking-service-client&client_secret=<secret>"
`

### Eureka Registration Problems

`ash
kubectl logs <pod-name> -n banking | grep -i eureka
`
Check: EUREKA_CLIENT_SERVICEURL_DEFAULTZONE and EUREKA_INSTANCE_PREFERIPADDRESS=true both set.

### Prometheus Target Down

Port-forward Prometheus and check http://localhost:9090/targets.
Check: pod Running, prometheus.io/scrape=true annotation present,
management.endpoints.web.exposure.include contains "prometheus".

### Grafana No Data

K8s datasource URLs:
`
Prometheus: http://prometheus.monitoring.svc.cluster.local:9090
Loki:       http://loki.monitoring.svc.cluster.local:3100
Jaeger:     http://jaeger-query.monitoring.svc.cluster.local:16686
`

### Loki No Logs

`ash
kubectl get daemonset fluent-bit -n monitoring
kubectl logs daemonset/fluent-bit -n monitoring | grep -i "error\|loki"
`
Fluent Bit reads /var/log/containers/*_banking_*.log. Pods must be in banking namespace.

### Jaeger No Traces

`ash
kubectl exec -it <pod-name> -n banking -- env | grep OTEL
kubectl exec -it <pod-name> -n banking -- cat /proc/1/cmdline | tr '\0' '\n'
`
Expected: OTEL_TRACES_EXPORTER=zipkin, correct ENDPOINT, -javaagent in cmdline.

### Canary Not Splitting

`ash
kubectl get pods -n banking -l app=account-service --show-labels
`
With only v1 pods, both weights route to v1 (correct). Deploy v2 Deployment to activate splitting.

---

### KNOWN ISSUES

**1. Duplicate VirtualService "api-gateway-route"**
Both k8s/istio-ingress.yaml AND k8s/istio-phase5-comprehensive.yaml define it.
Applying both causes conflict. Use ONLY istio-phase5-comprehensive.yaml.

**2. Account Service hardcoded DB URL in application.yml**
Has jdbc:mysql://localhost:3306/account_service without .
K8s overrides this correctly with SPRING_DATASOURCE_URL env var.
For local dev (without K8s env vars): set SPRING_DATASOURCE_URL manually.

**3. istio-fault-injection.yaml**
Injects 100% HTTP 503 into User Service. DO NOT apply accidentally.

---

## 21. Security Considerations

### What Is Implemented

| Control | Implementation | Status |
|---|---|---|
| Authentication | Keycloak JWT tokens | Implemented |
| JWT Validation | API Gateway OAuth2 Resource Server | Implemented |
| Service-to-service encryption | Istio mTLS STRICT mode | Implemented |
| Basic secrets management | Kubernetes Secrets (base64) | Implemented (basic) |
| User account lifecycle | Admin approval workflow | Implemented |
| Keycloak admin integration | User Service manages users via Admin API | Implemented |

### Security Gaps (for production)

1. **K8s Secrets NOT encrypted** - only base64. Use Vault or cloud KMS.
2. **MySQL on host machine** - not network-isolated, accessible from host.
3. **Backend services don't validate JWT** - only Gateway authenticates. Direct service access bypasses auth.
4. **No RBAC** - any authenticated user can call any endpoint.
5. **Keycloak on host without TLS** - needs HTTPS for production.
6. **Grafana anonymous access** in K8s (GF_AUTH_ANONYMOUS_ENABLED=true) - disable for production.
7. **Client secrets in YAML files** - do not commit to public repositories.

---

## 22. Project Achievements

| Achievement | Verified From |
|---|---|
| 7 independently deployable Spring Boot services | All pom.xml + Dockerfiles |
| Database-per-service (5 MySQL schemas) | application.yml + k8s deployment envs |
| Spring Cloud Gateway with JWT validation + Eureka routing | API-Gateway/src/main/resources/application.yml |
| Netflix Eureka service registry | Service-Registry/ + all service application.yml |
| 9 OpenFeign inter-service calls (all verified) | Feign client interfaces in all src/ directories |
| Keycloak IAM with programmatic admin integration | User-Service/src/main/java/**/KeycloakServiceImpl.java |
| OTel Java Agent in every Docker image | All service Dockerfiles |
| K8s deployment with health probes + resource limits + config injection | k8s/*/deployment.yaml |
| Istio service mesh with mTLS STRICT | k8s/istio-mtls.yaml |
| Istio Gateway + VirtualServices + DestinationRules | k8s/istio-phase5-comprehensive.yaml |
| Canary deployment (v1/v2 traffic splitting) | k8s/account-service/ + istio-phase5-comprehensive.yaml |
| Outlier detection circuit breaking on all services | k8s/istio-phase5-comprehensive.yaml |
| Per-service request timeouts | k8s/istio-phase5-comprehensive.yaml |
| Automatic retries on connection failures | k8s/istio-phase5-comprehensive.yaml |
| 100% distributed tracing (OTel -> Jaeger) | k8s/*/deployment.yaml OTEL vars + Dockerfiles |
| Centralized logging (Fluent Bit -> Loki -> Grafana) | k8s/monitoring/fluent-bit.yaml + loki.yaml |
| Metrics monitoring (Micrometer -> Prometheus -> Grafana) | k8s/monitoring/prometheus.yaml + grafana.yaml |
| 8 pre-provisioned Grafana dashboards | grafana/provisioning/dashboards/*.json |
| kube-state-metrics for cluster-level visibility | k8s/monitoring/kube-state-metrics.yaml |
| 7 k6 test scripts for load/stress/spike/canary testing | performance/scripts/*.js |

---

## 23. Analysis Summary

### Repository Statistics

| Component | Count |
|---|---|
| Total Microservices | 7 |
| Business Services | 5 (User, Account, Transaction, Fund Transfer, Sequence Generator) |
| Infrastructure Services | 2 (API Gateway, Service Registry) |
| MySQL Schemas | 5 |
| Kubernetes Namespaces | 3 (banking, monitoring, istio-system) |
| Kubernetes Deployments | 13 (7 banking + 6 monitoring) |
| Istio Version | 1.23.0 (verified from istio-cm.yaml metadata timestamp 2026-08-26) |
| Istio Resources Applied | 1 Gateway + 6 VirtualServices + 6 DestinationRules + 1 PeerAuthentication + 1 Telemetry |
| Grafana Dashboards | 8 pre-provisioned (JSON files verified) |
| Grafana Datasources | 3 (Prometheus default, Loki UID:Loki, Jaeger) |
| Inter-service Feign Calls | 9 (all mapped and verified from source code) |
| k6 Test Scripts | 7 |
| Observability Stack | Prometheus + Grafana + Loki + Fluent Bit + Jaeger + kube-state-metrics + OTel Agent |

### Configuration Issues Found

| Issue | Severity | Location | Resolution |
|---|---|---|---|
| Duplicate VirtualService "api-gateway-route" | High | istio-ingress.yaml + istio-phase5-comprehensive.yaml | Use only istio-phase5-comprehensive.yaml |
| Account Service hardcoded DB URL | Medium | Account-Service/src/main/resources/application.yml | K8s env var SPRING_DATASOURCE_URL overrides correctly |
| Canary v2 pods not deployed | Info | k8s/account-service/ | VirtualService ready; deploy v2 Deployment separately |
| Rate limiting not configured | Info | k8s/ directory | No EnvoyFilter or rate limit service present |
| MySQL outside Kubernetes | Design | docker-compose.yml + deployments | Use managed DB for production |
| Fault injection file can be accidentally applied | High | k8s/istio-fault-injection.yaml | DO NOT apply in production |
| Grafana anonymous access enabled | Security | k8s/monitoring/grafana.yaml | Set GF_AUTH_ANONYMOUS_ENABLED=false for production |

