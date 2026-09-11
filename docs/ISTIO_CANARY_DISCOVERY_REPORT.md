# ISTIO CANARY DEPLOYMENT – COMPLETE PROJECT DISCOVERY & ANALYSIS

## 1. Executive Summary

- **Current architecture:** The system comprises six core microservices (Account, User, Transaction, Fund-Transfer, Sequence-Generator), an API Gateway, and a Eureka Service Registry. Metrics are collected via Prometheus and Grafana.
- **Current traffic flow:** K6 -> Istio Ingress Gateway -> API Gateway -> Spring Cloud LoadBalancer (via Eureka) -> Direct to Pod IPs (v1 or v2).
- **What controls traffic distribution:** Currently, the Spring Cloud Gateway's client-side load balancer controls distribution. It resolves instances via Eureka and round-robins across the registered Pod IPs.
- **Observed 50/50 behavior confirmed?**: CONFIRMED. Kiali shows 50/50 because the API Gateway bypasses Istio's sidecar routing (VirtualService) and directly load-balances traffic to the Pod IPs retrieved from Eureka.
- **Canary deployment feasible?**: Yes, both `v1` and `v2` deployments exist and share a common Kubernetes Service, but routing configurations must be adjusted to allow Istio to manage the traffic weights.
- **Biggest technical risk:** The API Gateway bypasses Istio `VirtualService` by using `lb://account-service` and Eureka IP registration (`EUREKA_INSTANCE_PREFERIPADDRESS: "true"`). Istio cannot intercept and route traffic correctly based on weights unless traffic goes through the Kubernetes Service hostname.
- **Exact recommended next step:** Modify the API Gateway configuration to route `account-service` requests to the Kubernetes Service hostname (`http://account-service.banking.svc.cluster.local:8081`) instead of using Eureka (`lb://account-service`).

## 2. Complete Repository Review Status

| Repository Area | Inspected? | Relevant? | Key Findings |
|---|---|---|---|
| Root configuration | FULLY INSPECTED | Yes | Found docker-compose, batch scripts, and comprehensive documentation. |
| All microservices | FULLY INSPECTED | Yes | Found source code and `application.yml` for all services. |
| API Gateway | FULLY INSPECTED | Yes | Uses `lb://` for all routing, bypassing K8s Services. |
| Service Registry | FULLY INSPECTED | Yes | Standard Eureka server configuration. |
| Config Server | NOT AVAILABLE | No | No central Config Server found in the repo. |
| Kubernetes manifests | FULLY INSPECTED | Yes | Found Deployments, Services, ConfigMaps in `k8s/`. Both v1 and v2 deployments exist for `account-service`. |
| Istio manifests | FULLY INSPECTED | Yes | Found `istio-phase5-comprehensive.yaml` with subsets and VirtualServices. |
| Docker configuration | FULLY INSPECTED | Yes | Multi-stage Dockerfiles exist for services. |
| Deployment scripts | PARTIALLY INSPECTED | Yes | Found `build_all.bat` and python build scripts. |
| CI/CD | NOT AVAILABLE | No | No GitHub Actions or Jenkinsfiles found. |
| Monitoring | FULLY INSPECTED | Yes | Prometheus and Grafana configs available in root directories. |
| Performance directory | FULLY INSPECTED | Yes | K6 scripts use safe GET endpoints, targeting the Gateway. |
| Documentation | FULLY INSPECTED | Yes | Multiple detailed architecture and runbook documents found. |

## 3. Complete Project Architecture

```text
                  +-------------------+
                  |   K6 Canary Test  |
                  +-------------------+
                            |
                            v (localhost:8088)
               +---------------------------+
               |   Istio Ingress Gateway   |
               +---------------------------+
                            |
                            v
                  +-------------------+
                  |    API Gateway    |
                  +-------------------+
                            | (Currently uses Eureka for resolution)
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
+---------------+   +---------------+   +-------------------+
| User-Service  |   | Fund-Transfer |   | Transaction-Svc   |
+---------------+   +---------------+   +-------------------+
        |                   
        | (account-service) 
        v                   
+-------------------------------------------------+
|               account-service                   |
|  (Targeted via Istio VirtualService in future)  |
|                                                 |
|    +----------------+       +----------------+  |
|    |      v1        |       |      v2        |  |
|    +----------------+       +----------------+  |
+-------------------------------------------------+
```

## 4. Microservices Inventory

| Service | App Name | Port | Deployment | K8s Service | Replicas | Image |
|---|---|---|---|---|---|---|
| Account Service | account-service | 8081 | account-service, account-service-v2 | account-service | 1 (each) | localhost:5001/banking/account-service:latest / :v2 |
| API Gateway | api-gateway | 8080 | api-gateway | api-gateway | 1 | localhost:5001/banking/api-gateway:latest |
| User Service | user-service | 8082 | user-service | user-service | 1 | localhost:5001/banking/user-service:latest |
| Transaction Svc | transaction-service | 8084 | transaction-service | transaction-service | 1 | localhost:5001/banking/transaction-service:latest |
| Fund Transfer | fund-transfer | 8085 | fund-transfer | fund-transfer | 1 | localhost:5001/banking/fund-transfer:latest |
| Sequence Gen | sequence-generator | 8083 | sequence-generator | sequence-generator | 1 | localhost:5001/banking/sequence-generator:latest |
| Service Registry | service-registry | 8761 | eureka | service-registry | 1 | localhost:5001/banking/service-registry:latest |

## 5. Account-Service Deep Dive

**Application details:**
- **Endpoints:** Extensive `GET` endpoints for accounts, balances, and transactions. `POST`/`PUT`/`PATCH` endpoints for modifications.
- **Dependencies:** MySQL (`account_service`), Eureka client, Keycloak (OAuth2).

**Kubernetes details:**
- **v1 Deployment:** `account-service`, labels `app: account-service`, `version: v1`. Image `...:latest`.
- **v2 Deployment:** `account-service-v2`, labels `app: account-service`, `version: v2`. Image `...:v2`.
- **Service:** `account-service`, selects `app: account-service`.
Both deployments correctly sit behind the same Kubernetes Service, allowing them to support the `v1`/`v2` Istio subsets safely.

## 6. API Gateway Route Inventory

| Route ID | URI | Path Predicates |
|---|---|---|
| `user-service` | `lb://user-service` | `/api/users/**` |
| `fund-transfer-service` | `lb://fund-transfer-service` | `/api/fund-transfers/**` |
| `account-service` | `lb://account-service` | `/accounts/**` |
| `sequence-generator` | `lb://sequence-generator` | `/sequence/**` |
| `transaction-service` | `lb://transaction-service` | `/transactions/**` |
| `fund-transfer-service-raw` | `lb://fund-transfer-service` | `/fund-transfers/**` |

**Request path to account-service:** `K6 -> Istio Ingress (port 80) -> API Gateway -> Eureka Discovery -> Pod IP`.

## 7. Istio Configuration Inventory

| File Path | Resource Type | Name | Namespace | Hosts | Routes/subsets/weights | Status |
|---|---|---|---|---|---|---|
| `k8s/istio-ingress.yaml` | Gateway | `banking-gateway` | `banking` | `*` | N/A | ACTIVE |
| `k8s/istio-ingress.yaml` | VirtualService | `api-gateway-route` | `banking` | `*` | -> `api-gateway...:8080` | ACTIVE |
| `k8s/istio-phase5-comprehensive.yaml` | DestinationRule | `account-service-destination` | `banking` | `account-service...` | Subsets: `v1`, `v2` | LIKELY ACTIVE |
| `k8s/istio-phase5-comprehensive.yaml` | VirtualService | `account-service-route` | `banking` | `account-service...` | `v1`: 90, `v2`: 10 | LIKELY ACTIVE |

## 8. Kubernetes Labels and Selectors

| Component | Labels | Selector | Expected Relationship | Status |
|---|---|---|---|---|
| Service | `app: account-service` | `app: account-service` | Should route to both v1 and v2 pods | OK |
| v1 Deployment | `app: account-service`, `version: v1` | `app: account-service` | Should match Service and DR v1 subset | OK |
| v2 Deployment | `app: account-service`, `version: v2` | `app: account-service` | Should match Service and DR v2 subset | OK |
| DestinationRule | N/A | `v1`->`version:v1`, `v2`->`version:v2` | Should map subsets to pod labels | OK |

## 9. Current Traffic Flow

```text
K6 Test (http://localhost:8088/accounts?...)
 |
 v
Istio Ingress Gateway
 |
 v
API Gateway (matches /accounts/**)
 |
 v
Eureka Service Registry (looks up account-service Pod IPs)
 |
 v
Spring Cloud LoadBalancer (round-robins client-side to Pod IPs)
 |
 +----------------+
 |                |
 v                v
Pod v1           Pod v2
(Bypasses Istio VirtualService entirely)
```

## 10. Current Traffic Distribution Analysis

**What currently produces the observed Kiali traffic distribution?**
**CONFIRMED**: The API Gateway uses `lb://account-service` in its routing configuration. Combined with `EUREKA_INSTANCE_PREFERIPADDRESS: "true"` in the `banking-config` ConfigMap, the Spring Cloud Gateway fetches Pod IPs directly from Eureka and performs its own client-side round-robin load balancing. By routing traffic directly to the Pod IPs, the API Gateway completely bypasses the Istio `VirtualService` bound to the Kubernetes Service hostname, resulting in a 50/50 traffic split.

Evidence:
- `API-Gateway/src/main/resources/application.yml` uses `lb://account-service`.
- `k8s/banking-configmap.yaml` has `EUREKA_INSTANCE_PREFERIPADDRESS: "true"`.

## 11. K6 Canary Test Analysis

- **Script:** `performance/scripts/canary-demo-test.js`
- **Endpoints:** `/accounts`, `/accounts?accountNumber=...`, `/accounts/balance`, `/accounts/{id}/transactions`
- **VUs & Duration:** 8 VUs, 10 minutes.
- **Thresholds:** `http_req_failed < 0.01`
- **Checks:** All checks verify a `200 OK` response.
- **Traffic Control:** K6 ONLY GENERATES TRAFFIC – ISTIO/KUBERNETES CONTROLS DISTRIBUTION.

## 12. Safety Analysis

| Operation | Classification |
|---|---|
| `getAccount()` | SAFE (Read-only) |
| `getSecondaryAccount()` | SAFE (Read-only) |
| `getAccountBalance()` | SAFE (Read-only) |
| `getAccountTransactions()` | SAFE (Read-only) |
| `getFundTransfers()` | SAFE (Read-only) |

## 13. Kiali and Observability Readiness

To validate future 80/20 and 60/40 distributions:
- Generate traffic using `canary-demo-test.js`.
- Open Kiali -> Graph -> Select `banking` namespace.
- Ensure "Traffic Distribution" edges are enabled in Display settings.
- Verify the edges extending from `account-service` (Service node) to the `v1` and `v2` workload nodes match the intended percentages.

## 14. Canary Deployment Readiness

The existing architecture **does** support `account-service v1` and `v2` behind a common service. Both deployments possess the correct `app` and `version` labels. However, the API Gateway routing mechanism must be updated to ensure traffic utilizes the Kubernetes Service hostname, allowing Istio to apply VirtualService traffic weights.

## 15. Recommended Canary Architecture

The API Gateway should rely on Kubernetes DNS for `account-service` instead of Eureka's client-side load balancing.
API Gateway Route -> `http://account-service.banking.svc.cluster.local:8081`

This ensures that the API Gateway's sidecar proxy intercepts the outbound request to the Service hostname and applies the `account-service-route` Istio VirtualService weights correctly.

## 16. Proposed Future Traffic Stages

**Stage 1**
v1 = 80%
v2 = 20%

**Stage 2**
v1 = 60%
v2 = 40%

These percentages will be controlled by the Istio `VirtualService` named `account-service-route`.

## 17. Best Canary Version Difference

Recommend adding a custom HTTP response header (e.g., `X-Canary-Version: v1` and `X-Canary-Version: v2`) to responses in `AccountController.java`.
**Why:** It is completely safe, does not alter the JSON body payload, prevents breaking API contracts, requires no database schema changes, and can be easily verified using K6, Postman, or `curl`.

## 18. Exact Files That Would Need Modification

| File Path | Current Purpose | Required Future Change | Why |
|---|---|---|---|
| `API-Gateway/src/main/resources/application.yml` | Defines Gateway routes | Change `lb://account-service` to `http://account-service.banking.svc.cluster.local:8081` | To stop bypassing the Istio sidecar proxy and allow VirtualService traffic weights to apply. |
| `k8s/istio-phase5-comprehensive.yaml` | Defines Istio routing | Update VirtualService weights to 80/20 and 60/40 | To implement the specific Canary deployment stages. |
| `Account-Service/src/main/java/org/training/account/service/controller/AccountController.java` | Application controller | Add custom `X-Canary-Version` response header | To provide an observable difference between v1 and v2. |

## 19. Files That Do NOT Need Modification

- `performance/scripts/canary-demo-test.js`
**NO K6 CHANGES REQUIRED.** The K6 test perfectly targets the safe endpoints.

## 20. Configuration Conflict Risks

- **IST0109 Duplicate VirtualServices:** Ensure that `istio-traffic-management.yaml` (which might contain duplicate/conflicting configurations) is not applied alongside `istio-phase5-comprehensive.yaml`.
- **API Gateway Resolution:** Changing `lb://` to `http://` for one service while leaving others on `lb://` is safe, but we must ensure the `account-service` Kubernetes Service port (8081) is correct in the new URI.

## 21. Validation Commands

**NOT EXECUTED – FOR FUTURE LIVE CLUSTER VALIDATION**
```bash
kubectl get pods -n banking --show-labels
kubectl get svc -n banking
kubectl get deploy -n banking
kubectl get gateway -n banking
kubectl get virtualservice -n banking
kubectl get destinationrule -n banking
kubectl get endpoints -n banking
kubectl get endpointslices -n banking

kubectl describe svc account-service -n banking
kubectl get pods -n banking -l app=account-service --show-labels

# Istio analysis
istioctl analyze -n banking
```

## 22. Recommended Next Implementation Step

1. Update `API-Gateway/src/main/resources/application.yml` to change `lb://account-service` to `http://account-service.banking.svc.cluster.local:8081`.
2. Rebuild the API Gateway Docker image and restart the deployment.
3. Update `account-service` code to inject `X-Canary-Version: v1` and `v2` headers into responses, rebuild, and redeploy.
4. Update `istio-phase5-comprehensive.yaml` VirtualService weights to 80/20 and apply it.
