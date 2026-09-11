# K6 and Istio Traffic Test Discovery Report

## 1. Executive Summary
This report provides a comprehensive, evidence-based analysis of the Spring Boot Microservices Banking Application based on current source code and Kubernetes/Istio manifests. 

- **Architecture:** 5 Core Microservices, 1 API Gateway, Eureka Service Registry, MySQL Database, and Keycloak for IAM.
- **Service/API Counts:** 5 microservices exposing 23 distinct business REST endpoints, plus actuator endpoints.
- **Gateway & Istio Routing:** API Gateway routes external traffic via Spring Cloud Gateway (`lb://...`). Istio provides VirtualServices and DestinationRules with mutual TLS (`ISTIO_MUTUAL`) configured across the `banking` namespace.
- **Existing k6 Status:** Found k6 scripts (`baseline-test.js`, `load-test.js`, `spike-test.js`, `stress-test.js`, and `scenarios/safe-workflows.js`) targeting safe, read-only endpoints.
- **Canary Readiness:** Account Service is **Partially Ready**. It possesses `v1`/`v2` labels in its DestinationRule and weighted routing in its VirtualService (`istio-phase5-comprehensive.yaml`), but the Kubernetes Deployment manifest currently only deploys `version: v1`.

## 2. Complete Architecture Diagram
```mermaid
graph TD
    User([User / k6]) --> IstioIngress[Istio Ingress Gateway]
    IstioIngress --> APIGateway[API Gateway :8080]
    
    subgraph banking [Banking Namespace (Istio mTLS)]
        APIGateway --> UserService[User Service :8082]
        APIGateway --> AccountService[Account Service :8081]
        APIGateway --> FundTransferService[Fund Transfer Service :8085]
        APIGateway --> TransactionService[Transaction Service :8084]
        APIGateway --> SequenceGen[Sequence Generator]
        
        UserService -.Feign.-> AccountService
        AccountService -.Feign.-> UserService
        AccountService -.Feign.-> TransactionService
        AccountService -.Feign.-> SequenceGen
        FundTransferService -.Feign.-> AccountService
        FundTransferService -.Feign.-> TransactionService
        TransactionService -.Feign.-> AccountService
    end
    
    UserService --> DB1[(MySQL)]
    AccountService --> DB1
    FundTransferService --> DB1
    TransactionService --> DB1
    SequenceGen --> DB1
```

## 3. Microservice Inventory

| Service | Module Path | Application Port | Kubernetes Service | Database |
|---|---|---:|---|---|
| API Gateway | `API-Gateway/` | 8080 | `api-gateway` | N/A |
| User Service | `User-Service/` | 8082 | `user-service` | MySQL |
| Account Service | `Account-Service/` | 8081 | `account-service` | MySQL (`account_service`) |
| Fund Transfer | `Fund-Transfer/` | 8085 | `fund-transfer` | MySQL (`fund_transfer_service`) |
| Transaction Service | `Transaction-Service/` | 8084 | `transaction-service` | MySQL |
| Sequence Generator | `Sequence-Generator/` | - | `sequence-generator` | MySQL |

## 4. Complete API Inventory

### Business APIs

| Service | Method | Endpoint | Request Body | Parameters | Success Response | DB Mod |
|---|---|---|---|---|---|---|
| User Service | POST | `/api/users/register` | `CreateUser` | None | `Response` | Yes |
| User Service | GET | `/api/users` | None | None | `List<UserDto>` | No |
| User Service | GET | `/api/users/auth/{authId}` | None | Path: `authId` | `UserDto` | No |
| User Service | PATCH | `/api/users/{id}` | `UserUpdateStatus` | Path: `id` | `Response` | Yes |
| User Service | PUT | `/api/users/{id}` | `UserUpdate` | Path: `id` | `Response` | Yes |
| User Service | GET | `/api/users/{userId}` | None | Path: `userId` | `UserDto` | No |
| User Service | GET | `/api/users/accounts/{accountId}` | None | Path: `accountId` | `UserDto` | No |
| Account Service | POST | `/accounts` | `AccountDto` | None | `Response` | Yes |
| Account Service | PATCH | `/accounts` | `AccountStatusUpdate`| Query: `accountNumber` | `Response` | Yes |
| Account Service | GET | `/accounts` | None | Query: `accountNumber` | `AccountDto` | No |
| Account Service | PUT | `/accounts` | `AccountDto` | Query: `accountNumber` | `Response` | Yes |
| Account Service | GET | `/accounts/balance` | None | Query: `accountNumber` | `String` (Balance) | No |
| Account Service | GET | `/accounts/{accountId}/transactions`| None | Path: `accountId` | `List<TransactionResponse>` | No |
| Account Service | PUT | `/accounts/closure` | None | Query: `accountNumber` | `Response` | Yes |
| Account Service | GET | `/accounts/{userId}` | None | Path: `userId` | `AccountDto` | No |
| Fund Transfer | POST | `/fund-transfers` | `FundTransferRequest`| None | `FundTransferResponse` | Yes |
| Fund Transfer | GET | `/fund-transfers/{referenceId}` | None | Path: `referenceId` | `FundTransferDto` | No |
| Fund Transfer | GET | `/fund-transfers` | None | Query: `accountId` | `List<FundTransferDto>` | No |
| Transaction Svc | POST | `/transactions` | `TransactionDto` | None | `Response` | Yes |
| Transaction Svc | POST | `/transactions/internal` | `List<TransactionDto>`| Query: `transactionReference`| `Response` | Yes |
| Transaction Svc | GET | `/transactions` | None | Query: `accountId` | `List<TransactionRequest>`| No |
| Transaction Svc | GET | `/transactions/{referenceId}` | None | Path: `referenceId` | `List<TransactionRequest>`| No |
| Sequence Gen | POST | `/sequence` | None | None | `Sequence` | Yes |

### Actuator/Health APIs
All services (`Account`, `User`, `Fund Transfer`, `Transaction`, `API Gateway`) expose `/actuator/health` and `/actuator/prometheus` (verified via k8s deployment `prometheus.io/path` annotations).

## 5. API Gateway Routing Map
(Source: `API-Gateway/src/main/resources/application.yml`)

| External Path | Gateway Route | Target Service | Rewrite/Strip Prefix |
|---|---|---|---|
| `/api/users/**` | `user-service` | `lb://user-service` | No |
| `/api/fund-transfers/**` | `fund-transfer-service` | `lb://fund-transfer-service` | No |
| `/accounts/**` | `account-service` | `lb://account-service` | No |
| `/sequence/**` | `sequence-generator` | `lb://sequence-generator` | No |
| `/transactions/**` | `transaction-service` | `lb://transaction-service` | No |
| `/fund-transfers/**` | `fund-transfer-service-raw` | `lb://fund-transfer-service` | No |

**K6 Base URL Requirement:**
Requests must hit the API Gateway directly (or via Istio Ingress). Based on the test config, it should target `http://localhost:8088` (assumed Ingress port-forward) with paths like `/api/users`.

## 6. Istio Traffic Management Inventory
(Source: `k8s/istio-phase5-comprehensive.yaml`)

**DestinationRules (Global TLS Policy: `ISTIO_MUTUAL`)**
- `api-gateway-destination`
- `user-service-destination`
- `fund-transfer-destination`
- `transaction-service-destination`
- `sequence-generator-destination`
- `account-service-destination`: Includes subsets `v1` and `v2` mapping to `version: v1`/`version: v2` labels.

**VirtualServices**
| Host | Match Rule | Destination | Timeout | Retries |
|---|---|---|---|---|
| `account-service...` | HTTP GET | 90% `v1`, 10% `v2` | 5s | 2 attempts |
| `account-service...` | HTTP (Other) | 90% `v1`, 10% `v2` | 5s | None |
| `user-service...` | HTTP GET | `user-service` | 5s | 2 attempts |
| `fund-transfer...` | HTTP GET | `fund-transfer` | 5s | 2 attempts |

## 7. Service-to-Service Communication Map

| Source Service | Target Service | Communication Method |
|---|---|---|
| User Service | Account Service | OpenFeign (`@FeignClient`) |
| Account Service | User Service | OpenFeign (`@FeignClient`) |
| Account Service | Transaction Service | OpenFeign (`@FeignClient`) |
| Account Service | Sequence Generator | OpenFeign (`@FeignClient`) |
| Fund Transfer | Account Service | OpenFeign (`@FeignClient`) |
| Fund Transfer | Transaction Service | OpenFeign (`@FeignClient`) |
| Transaction Service| Account Service | OpenFeign (`@FeignClient`) |

## 8. Database Inventory
Entities mapping to tables:
- **User Service:** `User` (PK: `userId`), `UserProfile` (PK: `userProfileId`)
- **Account Service:** `Account` (PK: `accountId`, Fields: `accountNumber`, `availableBalance`, `userId`, `accountStatus`)
- **Transaction Service:** `Transaction` (PK: `transactionId`, Fields: `referenceId`, `accountId`, `amount`, `status`)
- **Fund Transfer Service:** `FundTransfer` (PK: `fundTransferId`, Fields: `transactionReference`, `fromAccount`, `toAccount`, `amount`)
- **Sequence Generator:** `Sequence` (PK: `id`)

## 9. Safe Database Test Data (Verification Required)
To prepare for tests, the following `SELECT` queries should be executed to verify data validity. **DO NOT run inserts or updates.**

```sql
-- Verify valid Users
SELECT user_id, auth_id, email_id, status FROM user;

-- Verify valid Accounts (needed for GET and Transfer testing)
SELECT account_id, account_number, account_status, available_balance, user_id FROM account WHERE account_status = 'APPROVED';

-- Verify Transactions
SELECT transaction_id, reference_id, account_id, amount FROM transaction;
```

## 10. Endpoint Classification for k6

| Classification | Endpoints | Safety/Impact |
|---|---|---|
| **A) Safe Read-Only** | `GET /api/users`, `GET /api/users/{id}`, `GET /accounts?accountNumber=...`, `GET /accounts/balance`, `GET /api/fund-transfers`, `/actuator/health` | Safe to hit heavily. Will not bloat DB. Idempotent. Ideal for latency metrics & service graphs. |
| **B) Controlled State-Changing** | `POST /api/users/register`, `POST /accounts` | Creates new entities. Running in a loop will bloat DB. Generates unique IDs. Not idempotent without cleanup. |
| **C) High-Risk (Financial)** | `POST /api/fund-transfers`, `POST /transactions` | Alters balances, generates internal fan-out (writes to multiple DBs). Needs valid source/destination accounts and sufficient balance. |

## 11. Existing k6 Test Inventory
Directory: `performance/scripts/`
- `baseline-test.js`: Baseline performance test.
- `load-test.js`: General load generation.
- `spike-test.js`: Extreme traffic spike test.
- `stress-test.js`: Stress limits test.
- `scenarios/safe-workflows.js`: Contains safe GET routines (`getUser`, `getAccount`, `getTransactions`, `getFundTransfers`).
- `performance/config/test-config.example.js`: Relies on env vars (`TEST_ACCOUNT_ID`, `BASE_URL`).

**Note:** The safe workflow scripts are properly architected to hit the API Gateway `/api/...` endpoints and refrain from destructive POST operations.

## 12. Recommended k6 Testing Plan
- **Phase A — Smoke test:** Run `safe-workflows.js` with 1 VU to verify Gateway routing, Keycloak auth (if enforced), and DB connectivity.
- **Phase B — Baseline test:** Run `baseline-test.js` to establish latency P90/P99 norms.
- **Phase C — Load test:** Run `load-test.js` to trigger HPA scaling (if configured) and Istio retries.
- **Phase D — Istio Traffic-Visualization Test:** Run sustained `safe-workflows.js` traffic while observing Kiali graph.
- **Phase E — Canary Demonstration Test:** Deploy Account Service `v2` (with visual/log changes) and observe the 90/10 traffic split in Kiali.

## 13. Canary Deployment Readiness Assessment (Account Service)
**CANARY READINESS: PARTIALLY READY**

*Reasoning:*
- **Ready:** The Istio `VirtualService` (`account-service-route`) is fully configured for a 90/10 traffic split based on subsets.
- **Ready:** The Istio `DestinationRule` (`account-service-destination`) defines the `v1` and `v2` subsets based on the `version` label.
- **Not Ready (Action Required):** The Kubernetes deployment (`k8s/account-service/deployment.yaml`) currently only deploys the `v1` pod (`version: v1` label). 
- **Next Step for Canary:** To demonstrate the canary, a second deployment (`account-service-v2.yaml`) must be created with `labels: version: v2`, pointing to a `v2` Docker image or utilizing different environment variables, so Kiali can register both subsets and visualize the Istio weighted routing.

## 14. Kiali Demonstration Plan
1. Start Kiali (e.g., `istioctl dashboard kiali`).
2. Verify empty or baseline service graph in `banking` namespace.
3. Generate controlled k6 traffic using `safe-workflows.js`.
4. Observe request flow traversing `Ingress -> API Gateway -> Microservices -> DB`.
5. Demonstrate traffic metrics (latency, HTTP 200s, RPS).
6. **Deploy canary v2:** Apply `account-service-v2` deployment.
7. Observe v1/v2 traffic split actively occurring on the Kiali graph (90% to v1, 10% to v2).
8. Demonstrate rollback by updating the `VirtualService` weight to 100% `v1`.

## 15. Missing Information / Manual Verification Required
- **Live DB Values:** Actual valid Account IDs/Numbers for `TEST_ACCOUNT_ID` in `test-config.example.js`.
- **Keycloak Token:** If security is fully enforced, a valid JWT is required to bypass 401 Unauthorized responses.
- **Istio Ingress URL:** Determining if traffic hits `localhost:8088` (k6 config default) or `localhost:80` (Standard ingress).

## 16. Recommended Next Step (Pre-Testing Checklist)
```markdown
[ ] Verify API Gateway base URL/Ingress port-forward
[ ] Verify valid account numbers and user IDs via SQL SELECT
[ ] Verify sufficient account balances for any planned POST tests
[ ] Verify Keycloak token generation and inject into `K6_TOKEN`
[ ] Confirm Kiali and Prometheus are actively scraping metrics from pods (`prometheus.io/scrape: 'true'`)
```
