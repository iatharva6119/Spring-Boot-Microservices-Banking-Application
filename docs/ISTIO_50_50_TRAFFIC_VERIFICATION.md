# ISTIO 50/50 TRAFFIC VERIFICATION REPORT

## 1. Objective
Verify and maintain account-service traffic at 50% v1 and 50% v2.

## 2. Files Inspected

| File | Purpose | Relevant? | Finding |
| --- | --- | --- | --- |
| `k8s/istio-phase5-comprehensive.yaml` | Main Istio configuration | Yes | Contains VirtualService `account-service-route` (90/10) and DestinationRule `account-service-destination` |
| `k8s/istio-traffic-management.yaml` | Older/alternative Istio config | Yes | Contains resources for `user-service` but not `account-service` |
| `API-Gateway/src/main/resources/application.yml` | API Gateway configuration | Yes | Uses `lb://account-service` which routes via Eureka client-side load balancing, bypassing Istio. |
| `performance/scripts/canary-demo-test.js` | Load testing script | Yes | Generates traffic. No routing logic found here. |

## 3. All Account-Service Istio Resources

**VirtualService**
- `account-service-route` (Namespace: `banking`)

**DestinationRule**
- `account-service-destination` (Namespace: `banking`)

**Gateway**
- No `Gateway` resource specifically for `account-service`. It relies on the mesh or the main `banking-gateway`.

## 4. Repository Configuration

Exact current repository traffic weights from `k8s/istio-phase5-comprehensive.yaml`:

```yaml
http:
  - route:
      - destination:
          host: account-service.banking.svc.cluster.local
          subset: v1
        weight: 90
      - destination:
          host: account-service.banking.svc.cluster.local
          subset: v2
        weight: 10
```

## 5. Live Cluster Configuration

Exact active weights on the live cluster:

```yaml
http:
  - route:
      - destination:
          host: account-service.banking.svc.cluster.local
          subset: v1
        weight: 90
      - destination:
          host: account-service.banking.svc.cluster.local
          subset: v2
        weight: 10
```

## 6. Repository vs Live Cluster Comparison

| Configuration | Repository Value | Live Cluster Value | Match? |
| --- | --- | --- | --- |
| account-service VirtualService v1 weight | 90 | 90 | Yes |
| account-service VirtualService v2 weight | 10 | 10 | Yes |
| DestinationRule v1 subset | version: v1 | version: v1 | Yes |
| DestinationRule v2 subset | version: v2 | version: v2 | Yes |
| Kubernetes Service selector | app: account-service | app: account-service | Yes |
| v1 deployment labels | (Implied) version: v1 | app=account-service, version=v1 | Yes |
| v2 deployment labels | (Implied) version: v2 | app=account-service, version=v2 | Yes |

## 7. Kubernetes Version Verification

- **v1 deployment**: Verified existing pod `account-service-7b4958bb5d-srkdm` has label `version=v1`.
- **v2 deployment**: Verified existing pod `account-service-v2-7b86b4cd5c-qhpvs` has label `version=v2`.
- **Service selector**: Verified `account-service` Kubernetes Service has selector `app: account-service`.
- **Pod labels**: Verified pods have `app=account-service` and `version=v1` or `version=v2`.
- **DestinationRule subsets**: Verified `account-service-destination` maps `v1` subset to `version: v1` and `v2` subset to `version: v2`.

## 8. Current Traffic Control Mechanism

**CONFIRMED**

The API Gateway is currently configured with `uri: lb://account-service`. This uses Spring Cloud LoadBalancer (via Eureka) to perform client-side load balancing directly to the pod IPs, completely bypassing the Kubernetes Service `account-service` and thus bypassing Istio's VirtualService routing rules. Because there is one v1 pod and one v2 pod, the round-robin client-side load balancing results in a 50/50 traffic split, overriding the 90/10 split defined in the Istio VirtualService.

## 9. Final 50/50 Decision

**D. ISTIO DOES NOT CURRENTLY CONTROL THE SPLIT. NO CHANGE MADE UNTIL ROUTING IS VERIFIED.**

## 10. Exact Modification, If Required

No modification to the Istio config will affect the current split unless the API Gateway is changed to route through the Kubernetes Service (e.g., `http://account-service.banking.svc.cluster.local:8081`). 

**Minimum-risk next step:**
Before modifying the API Gateway, we should confirm if the intention is to use Istio for all traffic management (replacing Eureka/Spring Cloud Gateway's load balancing). If yes, the API Gateway configuration needs to be updated to route to the Kubernetes service DNS, and then the Istio VirtualService weights in `k8s/istio-phase5-comprehensive.yaml` should be updated to 50/50 to match the desired state.
