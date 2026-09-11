# Account Service 50/50 Traffic Status

## 1. Purpose

The application currently demonstrates traffic reaching both:
- `account-service` v1
- `account-service` v2

with approximately equal observed traffic during the Canary K6 test.

## 2. Current Version Architecture

- `account-service` → `version=v1`
- `account-service-v2` → `version=v2`

Both versions share the same Kubernetes Service relationship.

## 3. Current Kubernetes Configuration

Kubernetes Service `account-service`
Selector:
```yaml
app: account-service
```

v1:
```yaml
app: account-service
version: v1
```

v2:
```yaml
app: account-service
version: v2
```

## 4. Current Istio Configuration

File:
```text
k8s/istio-phase5-comprehensive.yaml
```

Current configured weights:
```yaml
v1 = 90%
v2 = 10%
```

> **WARNING:** These configured Istio weights do not currently match the approximately 50/50 traffic distribution observed during the K6/Kiali demonstration.

## 5. Current API Gateway Configuration

```yaml
uri: lb://account-service
```

**CONFIRMED:** The API Gateway uses Spring Cloud's `lb://` routing for account-service.

**NOT FULLY VERIFIED:** The exact Envoy/Istio interception behavior for every resolved endpoint connection.

## 6. Current K6 Test Status

Command:
```bash
cd performance
k6 run scripts/canary-demo-test.js
```

Latest successful characteristics:
- 8 VUs
- 10 minutes
- 100% checks passed
- 0% HTTP failures

The K6 script generates application traffic.
The K6 script does not directly configure Istio traffic weights.

## 7. Observed Traffic Behavior

```text
OBSERVED:
v1 ≈ 50%
v2 ≈ 50%
```

This observation is based on Kiali during the successful K6 test.

## 8. Important Configuration Discrepancy

| Layer | Configuration / Observation |
|---|---|
| Istio VirtualService | 90% v1 / 10% v2 |
| Kiali observed traffic | Approximately 50% v1 / 50% v2 |
| API Gateway | `lb://account-service` |
| K6 | Generates traffic only |

> The configured Istio weights and observed traffic distribution currently do not match.

## 9. Current Conclusion

The application currently provides a successful two-version traffic demonstration, with Kiali observing approximately equal traffic across account-service v1 and v2.

However, based on the currently available evidence, it must not be claimed that the Istio VirtualService's configured weights are responsible for the observed 50/50 distribution.

## 10. Recommended Demonstration Status

```text
CURRENT DEMONSTRATION STATUS: WORKING
```

---

## Optional Istio Configuration Consistency Analysis

**OPTION A — NO CHANGE RECOMMENDED**

Reason:
> The current runtime behavior is working, but changing the VirtualService would not be proven to affect the observed traffic path.
