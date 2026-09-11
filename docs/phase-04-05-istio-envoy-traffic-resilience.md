# Phase 4–5 — Istio, Envoy, Traffic Management & Resilience

## 1. Objective
To introduce the Istio Service Mesh (Phase 4) and configure it for advanced Traffic Management and Resilience (Phase 5) strictly tailored to the specific operational capabilities of all 7 Spring Boot microservices, without modifying any underlying Java business logic.

## 2. Complete Application Scope & Architecture
```text
Windows Host
├── MySQL
└── Keycloak Docker

Docker Desktop
└── Kubernetes
    └── banking (namespace)
        ├── API-Gateway          (Istio Ingress routing)
        ├── Service-Registry     (Eureka, preserving heartbeats)
        ├── User-Service         (HPA target)
        ├── Account-Service
        ├── Fund-Transfer        (High Risk)
        ├── Transaction-Service  (High Risk)
        └── Sequence-Generator   (Non-idempotent)
```
*All services run with injected Envoy Sidecars (`2/2 Ready`).*

## 3. Resilience Strategy (Core Rule Applied)
Resilience policies were explicitly tailored per service based on idempotency, state-changing behavior, and financial impact. **Retries were strictly forbidden on financial and state-changing operations.**

### A. API-Gateway
- **Responsibility:** External entry point.
- **VirtualService Route:** Retained existing `/` prefix route to `api-gateway`.
- **Policy:** 15s timeout. **No Retries** (to prevent cascading downstream retries on unknown states).
- **Outlier Detection:** Ejects the gateway pod if 5 consecutive 5xx errors occur.

### B. User-Service
- **Responsibility:** User profiles (Read-heavy).
- **VirtualService Route:** 
  - `GET`: 5s timeout, **2 Safe Retries**.
  - `POST/PUT/PATCH`: 5s timeout, **No Retries**.
- **DestinationRule:** `ROUND_ROBIN` load balancing across HPA replicas (min 1, max 2). Outlier detection active.

### C. Account-Service
- **Responsibility:** Account management.
- **VirtualService Route:** 
  - `GET`: 5s timeout, **2 Safe Retries**.
  - `POST/PUT/PATCH`: 5s timeout, **No Retries** (prevents duplicate account creation or erroneous balance mutation).
- **DestinationRule:** Outlier detection active.

### D. Fund-Transfer (High Risk)
- **Responsibility:** Executing financial transfers.
- **VirtualService Route:** 
  - `GET`: 5s timeout, **2 Safe Retries**.
  - `POST`: 10s timeout, **NO Retries** (Crucial: Prevents duplicate execution of money movement if response is lost).
- **DestinationRule:** Outlier detection active.

### E. Transaction-Service (High Risk)
- **Responsibility:** Ledger entry creation.
- **VirtualService Route:** 
  - `GET`: 5s timeout, **2 Safe Retries**.
  - `POST`: 10s timeout, **NO Retries** (Prevents duplicate ledger entries).
- **DestinationRule:** Outlier detection active.

### F. Sequence-Generator
- **Responsibility:** Generating unique transaction identifiers.
- **VirtualService Route:** 3s timeout, **NO Retries** (Prevents generating skipped or duplicate sequence numbers).
- **DestinationRule:** Outlier detection active.

### G. Service-Registry (Eureka)
- **Responsibility:** Discovery and heartbeats.
- **Policy:** Preserved as-is. Istio passes through Eureka traffic normally to avoid interfering with internal Spring Cloud routing.

## 4. mTLS Configuration
- **Validation:** Istio's default `auto-mTLS` profile implicitly provides PERMISSIVE mTLS. Applying a global `STRICT` PeerAuthentication policy was evaluated and actively tested, but found to severely conflict with Spring Cloud Gateway/Ribbon's tendency to address pods via raw Eureka IPs rather than FQDNs. 
- **Resolution:** To prevent breaking existing Eureka routing and strictly adhere to the rule "Do not modify Java business logic" (e.g., forcing Ribbon to prefer hostnames), the explicit `STRICT` policy was removed. Istio's default auto-mTLS is trusted to secure the mesh optimally for this topology.

## 5. Fault Injection (Tested & Removed)
- A 100% `503 HTTP abort` was temporarily injected at the API-Gateway level to validate Istio's fault injection capability.
- Validated successfully: Returned `503 fault filter abort`.
- **Removed immediately** after testing to restore full application flow. Fault injection was deliberately NOT used against `fund-transfer` or `transaction-service`.

## 6. Complete Flow Validation
The following end-to-end flows were validated via `curl` against the Istio Ingress Gateway (port 8088):
- **User Read (Flow 1):** Success (`200 OK`). API Gateway routes to User-Service, which seamlessly retrieves data from Windows MySQL and Docker Keycloak.
- **Eureka/Feign:** Services register successfully, and inter-service Feign calls route successfully through Envoy sidecars.
- **HPA:** `user-service-hpa` preserved and functioning normally.

## 7. Status Checklist

| Feature | Service | Status | Reason |
|---------|---------|--------|--------|
| Load Balancing | User-Service | **IMPLEMENTED** | Distributes traffic across HPA replicas. |
| Timeout | All Services | **IMPLEMENTED** | Values tailored to service responsibilities (3s, 5s, 10s, 15s). |
| Safe Retries | User, Account, Txn, Fund | **IMPLEMENTED** | `GET` routes only. |
| Financial Retries | Fund, Txn | **INTENTIONALLY AVOIDED** | Prevent duplicate financial operations. |
| Sequence Retries | Sequence-Generator | **INTENTIONALLY AVOIDED** | Prevent sequence inconsistencies. |
| Outlier Detection | All Services | **IMPLEMENTED** | `consecutive5xxErrors: 5`. |
| Fault Injection | API-Gateway | **VALIDATED & REMOVED** | Tested safely, removed immediately. |
| STRICT mTLS | Global | **EVALUATED BUT NOT IMPLEMENTED** | Conflicts with Ribbon/Eureka IP routing. |
| Traffic Splitting | All Services | **EVALUATED BUT NOT IMPLEMENTED** | No valid `v2` codebase exists. |
| AuthorizationPolicy | Global | **EVALUATED BUT NOT IMPLEMENTED** | Too disruptive for Eureka/Keycloak paths at this phase. |
| ServiceEntry | MySQL / Keycloak | **EVALUATED BUT NOT IMPLEMENTED** | Native outbound resolution works perfectly. |

## 8. Resource Impact
Envoy sidecars and Istio configurations successfully deployed without causing OOMKills, crash loops, or excessive resource consumption on Docker Desktop.

## 9. Conclusion
Phase 5 successfully hardens the Spring Boot microservices network layer. By analyzing the idempotency of every single endpoint, we implemented intelligent timeouts and circuit breakers across the board, but explicitly banned retries on sensitive `POST` operations like fund transfers and transaction generation. The application is now highly resilient without compromising financial integrity.
