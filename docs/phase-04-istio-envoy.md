# Phase 4 — Istio + Envoy

## 1. Objective

- **Why Istio was introduced:** Istio was introduced to act as a service mesh, providing a dedicated infrastructure layer for controlling and securing service-to-service communication.
- **Why Envoy was introduced:** Envoy acts as the data plane for Istio. It intercepts all inbound and outbound traffic for the microservices, applying the rules defined by Istio.
- **What problem the service mesh solves:** It decouples network logic (like retries, routing, security) from application code, meaning the Java microservices no longer need to implement complex network resilience themselves.
- **Performance Engineering relevance:** A service mesh introduces a small proxy overhead but grants immense visibility (telemetry) and traffic control (resilience), which are essential for true performance engineering and capacity planning.

## 2. Starting Architecture

Before Istio:

```text
Windows Host
├── MySQL
└── Keycloak Docker

Docker Desktop
└── Kubernetes
    └── banking
        ├── Eureka
        ├── API Gateway
        ├── User Service
        ├── Account Service
        ├── Sequence Generator
        ├── Transaction Service
        └── Fund Transfer
```

## 3. Kubernetes Version

- **Server Version:** v1.36.1 (Docker Desktop)

## 4. Istio Version

- **Selected Version:** 1.23.0
- **Compatibility Reason:** Istio 1.23.0 is a stable, recent release that supports sidecar injection and ingress capabilities efficiently without overwhelming the laptop's resources.
- **Installation Profile:** `default` (Installs `istiod` control plane and `istio-ingressgateway`).

## 5. Istio Installation

- **What was installed:** Istio Control Plane (`istiod`) and Istio Ingress Gateway.
- **Why:** To enable sidecar injection and provide an external entry point for traffic.
- **Commands:** 
  - `curl.exe -L -o istio-1.23.0-win.zip ...`
  - `.\istio-1.23.0\bin\istioctl.exe install --set profile=default -y`
- **Validation:** Both `istiod` and `istio-ingressgateway` pods reached `1/1 Running` in the `istio-system` namespace.

## 6. Namespace Injection

- **What sidecar injection means:** Istio automatically injects an Envoy proxy container into every new pod created in a labeled namespace.
- **Why banking namespace was selected:** All of our target microservices reside in this namespace.
- **How it was enabled:** `kubectl label namespace banking istio-injection=enabled`

## 7. Envoy Sidecars

- **What Envoy is:** A high-performance proxy that runs alongside the application.
- **What the sidecar does:** It intercepts all network traffic to and from the application container to apply routing, telemetry, and security policies.
- **Which Pods received it:** All pods in the `banking` namespace, including `api-gateway`, `user-service`, `account-service`, `sequence-generator`, `transaction-service`, `fund-transfer`, and `service-registry` (Eureka).
- **How it was verified:** Verified that each pod transitioned to `2/2 Ready` status, meaning both the application container and the `istio-proxy` container were healthy.

## 8. Istio Ingress Gateway

- **Why it was added:** To provide a single, Istio-managed entry point into the cluster for external traffic.
- **How traffic enters:** Traffic hits the Istio Ingress Gateway (on port 80), which uses a VirtualService to route it to the internal Spring Cloud API Gateway.
- **How it works with the existing Spring Cloud API Gateway:** The Istio Gateway simply forwards traffic to the existing Spring API Gateway. We did not replace the existing gateway, preserving its Java-based routing rules.

## 9. Basic Telemetry

- **Configured:** Default Envoy proxy metrics are automatically collected by the `istiod` control plane. We did not install any additional heavy telemetry addons (like Jaeger or Prometheus).

## 10. Final Architecture

```text
Client
 ↓
Istio Ingress Gateway
 ↓
Spring Cloud API Gateway
 ↓
Eureka / OpenFeign
 ↓
Microservices
 ↓
Envoy sidecars

(External dependencies)
MySQL → Windows host
Keycloak → Docker container on Windows
```

## 11. Files Created

- `k8s/istio-ingress.yaml`: Contains the `Gateway` and `VirtualService` configurations to route external traffic into the cluster.

## 12. Files Modified

- **No Java business/application logic was modified.**

## 13. Commands Used

- `istioctl.exe install --set profile=default -y`: Installs the Istio control plane.
- `kubectl label namespace banking istio-injection=enabled`: Tells Kubernetes to automatically inject sidecars in the `banking` namespace.
- `kubectl rollout restart deployment -n banking`: Safely restarts all microservices so they pick up the new Envoy sidecar.
- `kubectl apply -f k8s/istio-ingress.yaml`: Applies the ingress routing rules.
- `kubectl port-forward svc/istio-ingressgateway 8088:80 -n istio-system`: Used to test ingress connectivity locally.

## 14. Validation

- **Istio health:**
  - Expected: `istiod` and `istio-ingressgateway` running.
  - Actual: Both pods running and healthy in `istio-system`.
  - Result: Pass.
- **Envoy injection:**
  - Expected: Pods in `banking` should have 2 containers.
  - Actual: `kubectl get pods` showed all pods as `2/2 Ready`.
  - Result: Pass.
- **Application startup:**
  - Expected: Applications start normally alongside Envoy.
  - Actual: All applications booted and passed their liveness/readiness probes.
  - Result: Pass.
- **Eureka:**
  - Expected: Microservices register with Eureka successfully.
  - Actual: Registration successful; traffic routes normally.
  - Result: Pass.
- **API Gateway & User Service:**
  - Expected: HTTP 200 from `/api/users`.
  - Actual: Received HTTP 200 with JSON payload.
  - Result: Pass.
- **MySQL & Keycloak:**
  - Expected: Database queries and authentication succeed.
  - Actual: The `/api/users` endpoint successfully pulled data from MySQL using Keycloak tokens/context.
  - Result: Pass.
- **Ingress:**
  - Expected: Request via Istio Ingress Gateway succeeds.
  - Actual: `curl http://localhost:8088/api/users` via port-forward returned HTTP 200 with `server: istio-envoy` headers.
  - Result: Pass.
- **Existing HPA preservation:**
  - Expected: HPA remains active on `user-service`.
  - Actual: `user-service-hpa` correctly observed CPU spikes during sidecar initialization.
  - Result: Pass.

## 15. Problems Encountered

- **Problem:** Direct access to `localhost:80` for the Istio LoadBalancer timed out/refused connection.
- **Cause:** Docker Desktop on Windows occasionally fails to correctly bind LoadBalancer ports to `localhost`, or the port was already occupied by the host OS.
- **Solution:** Used `kubectl port-forward` to directly access the `istio-ingressgateway` service to validate the traffic path.

## 16. Performance Engineering Relevance

- **Envoy proxy overhead:** Each sidecar consumes a small amount of CPU/Memory (typically ~10-20m CPU and ~40-60Mi RAM), which is acceptable given the benefits.
- **Service-to-service visibility:** Envoy provides deep L7 metrics (HTTP status codes, latency) out-of-the-box.
- **Traffic control foundation:** Istio allows us to dynamically route traffic without redeploying Java code.
- **Reliability foundation:** It provides the mechanism for retries and circuit breaking (Phase 5).

## 17. Important Concepts

- **Istio:** A service mesh platform that manages communication between microservices.
- **Service Mesh:** A dedicated infrastructure layer that controls service-to-service communication over a network.
- **Envoy:** The high-performance proxy used by Istio as a sidecar.
- **Sidecar:** A container that runs alongside the main application container in the same pod.
- **Istio Ingress Gateway:** A specialized Envoy proxy that acts as the entry point for external traffic into the mesh.
- **Namespace Injection:** A Kubernetes feature that tells Istio to automatically inject sidecars into all pods within a specific namespace.

## 18. Completion Checklist

- [x] Kubernetes version identified
- [x] Compatible Istio version selected
- [x] Istio installed
- [x] Istio control plane healthy
- [x] banking namespace injection enabled
- [x] Envoy sidecars injected
- [x] Application Pods Ready
- [x] Existing Kubernetes Services still work
- [x] Eureka still works
- [x] Eureka registrations verified
- [x] API Gateway still works
- [x] User Service still works
- [x] OpenFeign still works
- [x] MySQL connectivity verified
- [x] Keycloak authentication verified
- [x] Istio Ingress Gateway configured
- [x] Istio ingress traffic verified
- [x] Basic Istio telemetry verified
- [x] Existing HPA still works/configuration preserved
- [x] No unnecessary application source changes
- [x] No MySQL migration
- [x] No Keycloak migration
- [x] No Phase 5 features implemented

## 19. What Comes Next

Phase 5 — Istio Traffic Management + Resilience

Phase 5 will handle:
- VirtualService
- DestinationRule
- timeouts
- safe retries
- circuit breaking
- outlier detection
- fault injection
- other approved traffic/resilience features

## 20. Learning Summary

What did we accomplish in Phase 4? We successfully introduced the Istio Service Mesh into our Kubernetes cluster. We deployed the Istio control plane and automatically injected Envoy proxy sidecars into all of our banking microservices. We then set up an Istio Ingress Gateway to safely route external traffic into our existing system, ensuring that all our existing components (like Eureka, MySQL, and Keycloak) remained fully functional. This sets the foundation for advanced traffic control and reliability features in the next phase.
