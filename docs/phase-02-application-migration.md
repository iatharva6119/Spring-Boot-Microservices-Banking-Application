# Phase 2 — Kubernetes Application Migration

---

## 1. Objective

### What we wanted to achieve

Our goal in Phase 2 was to migrate all 7 Spring Boot microservices into the Kubernetes anking namespace we created in Phase 1. We needed to ensure they could connect to each other via Eureka (internal to Kubernetes) and successfully connect to the MySQL database and Keycloak instance running on the Windows host.

### Why we needed it

The microservices architecture depends on service discovery (Eureka) and a centralized database (MySQL). Moving the services into Kubernetes introduces a new networking boundary. We needed to translate the existing docker-compose.yml configurations into Kubernetes-native Deployments and Services while maintaining all the necessary connections and dependencies.

### How it fits into the project

This phase is the core of the migration. It takes the application from running in standalone Docker containers (via Docker Compose) to running inside a managed Kubernetes cluster, completing the functional migration before we focus on performance tuning in Phase 3.

---

## 2. Starting Point

Before Phase 2, we had:
- A running Kubernetes cluster (Docker Desktop).
- A local Docker registry containing all 7 application images.
- A dedicated anking namespace.
- An empty k8s/ directory structure ready for YAML files.
- The MySQL database and Keycloak server running on the Windows host, accessible via host.docker.internal.

---

## 3. What We Implemented

### 3.1 Network Connectivity Verification
Before writing any YAML, we verified that a pod inside our Kubernetes cluster could reach the host resources. We launched a temporary usybox pod and confirmed:
- DNS resolution for host.docker.internal resolved to the Windows host IP (192.168.65.254).
- TCP connections to port 3306 (MySQL) succeeded.
- TCP connections to port 8571 (Keycloak) succeeded.

### 3.2 Global Configuration (ConfigMap and Secret)
We created a centralized ConfigMap (anking-configmap.yaml) to hold common environment variables for all services:
- EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: "http://service-registry:8761/eureka/"
- EUREKA_INSTANCE_PREFERIPADDRESS: "true"
- MYSQL_HOST: "host.docker.internal"
- APP_CONFIG_KEYCLOAK_URL: "http://host.docker.internal:8571/"

We also created a Kubernetes Secret (anking-secret.yaml) to store sensitive data like the MySQL credentials and Keycloak client secrets using Base64 encoding.

### 3.3 Eureka Service Registry Deployment
Eureka must start before any other service so that they can register with it upon startup.
We created k8s/eureka/deployment.yaml and k8s/eureka/service.yaml.
- Deployed as a NodePort service (port 30761) to allow external access if needed.
- We deployed this first and waited for the pod status to reach Running and the application to log Started Eureka Server.

### 3.4 Application Services Deployment
Once Eureka was ready, we deployed the remaining 6 services simultaneously:
- User Service (k8s/user-service/)
- Account Service (k8s/account-service/)
- Sequence Generator (k8s/sequence-generator/)
- Transaction Service (k8s/transaction-service/)
- Fund Transfer Service (k8s/fund-transfer/)
- API Gateway (k8s/api-gateway/)

Each service was configured to:
- Pull its image from the local registry (localhost:5001/banking/*).
- Use imagePullPolicy: IfNotPresent.
- Inject environment variables from the anking-config ConfigMap and anking-secret Secret.
- Connect to MySQL and Keycloak on the host via host.docker.internal.
- Expose itself internally as a ClusterIP service (except API Gateway, which was exposed as a NodePort on 30080).

### 3.5 Verification and Registration
We waited for all 7 pods to transition from ContainerCreating to Running.
We then launched a temporary curl pod inside the cluster to query the internal Eureka API (http://service-registry:8761/eureka/apps).
We successfully verified that all 6 application services registered themselves with Eureka with a status of UP.
We finally reviewed the application logs for pi-gateway, ccount-service, and user-service to confirm a clean startup with no database connection errors.

---

## 4. Architecture After Phase 2

`
+---------------------------------------------------------------------------------+
|  Windows Host                                                                   |
|                                                                                 |
|  +-- MySQL 3306                                                                 |
|  +-- Keycloak 8571                                                              |
|                                                                                 |
|  +-- Docker Desktop Kubernetes (banking namespace)                              |
|  |     |                                                                        |
|  |     +-- ConfigMap: banking-config                                            |
|  |     +-- Secret: banking-secret                                               |
|  |     |                                                                        |
|  |     +-- Pod: service-registry (NodePort 30761)                               |
|  |     +-- Pod: api-gateway (NodePort 30080)                                    |
|  |     +-- Pod: user-service (ClusterIP)                                        |
|  |     +-- Pod: account-service (ClusterIP)                                     |
|  |     +-- Pod: sequence-generator (ClusterIP)                                  |
|  |     +-- Pod: transaction-service (ClusterIP)                                 |
|  |     +-- Pod: fund-transfer (ClusterIP)                                       |
|  |     |                                                                        |
|  |     |   * All pods communicate internally via Kubernetes DNS / Eureka IP     |
|  |     |   * All pods reach MySQL/Keycloak via host.docker.internal             |
|  +------------------------------------------------------------------------------+
`

---

## 5. Files Created

| File | Purpose |
|------|---------|
| k8s/banking-configmap.yaml | Common environment variables |
| k8s/banking-secret.yaml | Sensitive credentials (DB, Keycloak) |
| k8s/eureka/*.yaml | Eureka Deployment and Service |
| k8s/user-service/*.yaml | User Service Deployment and Service |
| k8s/account-service/*.yaml | Account Service Deployment and Service |
| k8s/sequence-generator/*.yaml | Sequence Generator Deployment and Service |
| k8s/transaction-service/*.yaml | Transaction Service Deployment and Service |
| k8s/fund-transfer/*.yaml | Fund Transfer Deployment and Service |
| k8s/api-gateway/*.yaml | API Gateway Deployment and Service |
| docs/phase-02-application-migration.md | This document |

---

## 6. Validation

- [x] Connectivity from K8s to Host MySQL (Port 3306) verified.
- [x] Connectivity from K8s to Host Keycloak (Port 8571) verified.
- [x] ConfigMap and Secret applied successfully.
- [x] Eureka deployed and confirmed running.
- [x] All 6 application services deployed and confirmed running (Pods 1/1 Ready).
- [x] Eureka internal registry queried: All 6 services registered successfully.
- [x] Pod logs reviewed: No database connection errors, successful application startup.

---

## 7. What Comes Next

**Phase 3 — Kubernetes Performance & Reliability**

In Phase 3, we will add production-grade performance and reliability configurations to our Kubernetes resources:
- **Resource Requests & Limits:** Ensuring pods don't consume excessive CPU/Memory.
- **Liveness & Readiness Probes:** Telling Kubernetes how to check if our applications are healthy and ready to receive traffic.
- **Scaling Configurations (HPA):** Setting up auto-scaling based on CPU utilization.

We will NOT start Phase 3 until you explicitly approve.

---

Document created: 2026-08-25
Phase: 2 — Application Migration
Status: COMPLETE — Waiting for approval to proceed to Phase 3
