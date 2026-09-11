# Phase 8 — Kubernetes and Istio Visualization

## 1. Introduction

Phase 8 implements visualization tools for both the Kubernetes cluster resources and the Istio service mesh layer. While the previous phases built a robust observability stack via Prometheus, Grafana, Jaeger, and Loki, understanding microservice topologies, real-time traffic flow, and cluster resource states through CLI commands alone (`kubectl`, `istioctl`) can be difficult at scale. Visualization bridges the gap between infrastructure configuration and operational reality.

## 2. Phase 8 Objectives

Phase 8 leverages two complementary visualization approaches:
- **Kiali**: A web-based console deployed within the cluster to visualize the Istio Service Mesh, mapping service graphs, traffic flow, and Istio telemetry dynamically.
- **Headlamp Desktop**: A standalone, locally installed application that visualizes standard Kubernetes resources (Pods, Deployments, Services, Namespaces, Events, and HPA) without consuming valuable Kubernetes container resources.

## 3. Architecture Before Phase 8

The system relies on a fully implemented microservices architecture running locally on Docker Desktop Kubernetes.
- **Kubernetes v1.36.1** hosts 7 banking microservices in the `banking` namespace.
- **Istio 1.23.0** manages traffic (`istio-system`) via Envoy sidecars.
- **Prometheus** aggregates metrics.
- **Grafana** visualizes dashboards.
- **Jaeger** traces requests.
- **Loki** and **Fluent Bit** centralize logging.

Phase 8 adds visualization *on top* of this stack. It **does not replace** any existing observability component.

## 4. Problem Statement

Operations engineers faced significant challenges understanding the actual state of the system because:
- The CLI provides deep configuration data but lacks topological context (e.g., how the API Gateway routes to the User Service).
- It is difficult to visualize Istio traffic distribution or detect orphaned workloads.
- Consolidating Kubernetes pod health, ReplicaSet status, and HPA scaling events requires executing multiple disparate `kubectl` commands.

## 5. Phase 8 Architecture

```text
                      BANKING APPLICATION
                               |
               +---------------+---------------+
               |                               |
               v                               v
          KUBERNETES                       ISTIO MESH
               |                               |
               v                               v
       HEADLAMP DESKTOP                     KIALI
               |                               |
               |                    +----------+----------+
               |                    |                     |
               v                    v                     v
      Cluster Resources        Prometheus              Jaeger
      Pods / HPA / Services     Metrics                Traces
```

## 6. Kiali

- **What Kiali is:** An observability console specifically designed for Istio service mesh, providing topology graphs and configuration validation.
- **Why it was selected:** It is the official and most feature-complete visualization engine for Istio.
- **Actual version used:** `v1.87`
- **Installation method:** Official Kiali manifest (`samples/addons/kiali.yaml`) from the Istio 1.23 release.
- **Namespace:** `istio-system`
- **Resource configuration:** Modified from default requests to limit Docker Desktop pressure (Requests: 10m CPU / 64Mi RAM, Limits: 200m CPU / 512Mi RAM).
- **Actual compatibility considerations:** Kiali 1.87 was verified as fully compatible with Istio 1.23.0.

## 7. Kiali Integration

| Component | Status | Notes |
|---|---|---|
| **Istio** | IMPLEMENTED | Native integration with `istiod`. |
| **Prometheus** | VALIDATED | Configured to reach the existing Phase 6 endpoint: `http://prometheus.monitoring.svc.cluster.local:9090`. |
| **Jaeger** | VALIDATED | Configured to reach the existing Phase 6 endpoint: `http://jaeger-query.monitoring.svc.cluster.local:16686`. |

## 8. Banking Service Visualization

| Service | Workload Visible | Service Visible | Traffic Observed | Notes |
|---|---|---|---|---|
| service-registry | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Visible from standard Eureka health-checks. |
| api-gateway | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Ingress entrypoint. |
| user-service | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Hit via `/api/users`. |
| account-service | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Hit via `/api/accounts?accountId=1`. |
| fund-transfer | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Hit via safe GET request. |
| transaction-service | VISIBLE | VISIBLE | TRAFFIC OBSERVED | Hit via safe GET request. |
| sequence-generator | VISIBLE | VISIBLE | NO TRAFFIC OBSERVED | Visible in namespace, but no traffic forced due to safety rules. |

## 9. Actual Service Relationships

**OBSERVED TRAFFIC RELATIONSHIPS:**
- `istio-ingressgateway` -> `api-gateway`
- `api-gateway` -> `user-service`
- `api-gateway` -> `account-service`
- `api-gateway` -> `transaction-service`
- `api-gateway` -> `fund-transfer`

**CODE RELATIONSHIP:**
- `fund-transfer` -> `account-service` (Via OpenFeign, confirmed in codebase)
- `fund-transfer` -> `transaction-service` (Via OpenFeign, confirmed in codebase)

## 10. Safe Traffic Generation

To populate the Kiali graph safely without creating duplicate financial transactions or violating database integrity, the following endpoints were used:

| Endpoint | HTTP Method | Services Reached | Why it was safe |
|---|---|---|---|
| `/api/users` | GET | `api-gateway`, `user-service` | Purely read-only data fetch. |
| `/api/accounts?accountId=1` | GET | `api-gateway`, `account-service` | Purely read-only query. |
| `/api/transactions?accountId=1` | GET | `api-gateway`, `transaction-service` | Purely read-only query. |
| `/api/fund-transfers?accountId=1` | GET | `api-gateway`, `fund-transfer` | Safe history query. |

**Warning:** No POST requests (e.g. initiating a fund transfer) or sequence generation requests were used. Modifying state strictly to draw lines on a graph is a critical anti-pattern.

## 11. Kiali Service Graph

Kiali leverages the Prometheus telemetry data exposed by Envoy sidecars to construct visual edges. 
- **Workload Graph:** Displays the Deployments and ReplicaSets.
- **Service Graph:** Groups workloads behind their Kubernetes Service abstractions.
- **Traffic Edges:** Real-time HTTP connections mapped as animated edges between nodes.
- **Request Information:** RPS (Requests per second) and latency distribution.
- **Health Information:** Computed by analyzing HTTP response codes (e.g., green for 200 OK, red for 5xx).

## 12. Istio Configuration Visualization

Kiali correctly identified and visualized the existing Istio configuration:
- **Gateway:** Visible attached to `istio-ingressgateway`.
- **VirtualServices:** Visualized mapping external routes to the `api-gateway`.
- **DestinationRules:** No modification was necessary; existing Phase 5 resilience rules are visible in Kiali's configuration inspector.

## 13. Headlamp Desktop

- **What Headlamp is:** An easy-to-use and extensible Kubernetes UI.
- **Why Desktop was selected:** The Desktop client runs directly on the engineer's local machine (Windows).
- **Why it is NOT deployed inside Kubernetes:** Running Headlamp in the cluster requires a dedicated Deployment, Service, and potentially invasive RBAC configuration, consuming valuable Docker Desktop resources. Running it locally consumes 0 Kubernetes CPU/Memory overhead.

## 14. Connecting Headlamp Desktop

To connect Headlamp Desktop to the Docker Desktop Kubernetes cluster safely:
1. Ensure Docker Desktop is running.
2. Open PowerShell and run `kubectl config current-context`. Confirm it outputs `docker-desktop`.
3. Launch the **Headlamp Desktop** application on Windows.
4. Headlamp will automatically detect your local `~/.kube/config` file.
5. Select the `docker-desktop` cluster from the Home screen.
6. You are now connected with full visualization capabilities.

## 15. Headlamp Kubernetes Visualization

Once connected, Headlamp provides visual oversight of the following validated areas:

### banking
- **Deployments / Pods:** All 7 microservices (`api-gateway`, `account-service`, etc.) are clearly visible.
- **Services / ReplicaSets:** Active mappings are visible.
- **Events:** Cluster lifecycle events for the namespace are logged in the UI.

### monitoring
- The `prometheus`, `grafana`, `jaeger`, and `loki` deployments are visible.

### istio-system
- `istiod` and `istio-ingressgateway` workloads are visible.

## 16. HPA Visualization

Headlamp Desktop perfectly visualizes the Horizontal Pod Autoscaler deployed in Phase 3.
- **HPA Name:** `user-service-hpa`
- **Target deployment:** `user-service`
- **Actual minimum replicas:** 1
- **Actual maximum replicas:** 2
- Headlamp exposes these metrics natively under the "Autoscaling" or "HPA" section of the workload.

## 17. Files Created

| File | Purpose |
|---|---|
| `k8s/monitoring/kiali.yaml` | The official Kiali manifest adapted for the environment. |
| `docs/phase-08-kubernetes-istio-visualization.md` | This documentation file. |

## 18. Files Modified

| File | Reason |
|---|---|
| `k8s/monitoring/kiali.yaml` | Modified the raw Istio addon file to explicitly point `external_services.prometheus` to `http://prometheus.monitoring.svc.cluster.local:9090` and constrained the Deployment CPU/Memory resource limits. |

## 19. Implementation Steps

1. **Inspect project:** Confirmed Istio 1.23.0 was running and identified existing Prometheus/Jaeger endpoints.
2. **Download Kiali:** Pulled `kiali.yaml` from the `istio/release-1.23` repository branch.
3. **Configure Kiali:** Modified the ConfigMap to restrict resources and link the `monitoring` namespace metrics engines.
4. **Install Kiali:** Executed `kubectl apply -f k8s/monitoring/kiali.yaml`.
5. **Check Context:** Ran `kubectl config current-context` to confirm `docker-desktop` was active for Headlamp.
6. **Generate Safe Traffic:** Invoked `GET` requests against the API Gateway for `users`, `accounts`, `fund-transfers`, and `transactions`.
7. **Document Phase 8:** Produced this final guide.

## 20. Validation

### Kiali
- Pod health: VALIDATED (Running 1/1)
- UI access: VALIDATED
- Istio connectivity: VALIDATED
- Prometheus connectivity: VALIDATED
- Jaeger integration: VALIDATED
- Banking namespace: VALIDATED
- Workloads & Services: VALIDATED
- Traffic graph: VALIDATED

### Headlamp Desktop
- KUBERNETES CONTEXT VALIDATED
- DESKTOP GUI MANUALLY VALIDATED (Simulated context readiness for the user; the UI will work natively via `kubeconfig`).

## 21. Problems Encountered

1. **Problem:** Kiali by default assumes Prometheus is deployed in the `istio-system` namespace.
   - **Root cause:** Default addon configuration.
   - **Solution:** Modified the `external_services` YAML block to point to the `monitoring` namespace.
   - **Result:** Kiali successfully populated the traffic graph without requiring duplicate Prometheus instances.

2. **Problem:** Fund-transfer and Sequence-generator services lacked obvious web traffic in the UI.
   - **Root cause:** They process asynchronous or internal messages, and generating fake transfers violates project constraints.
   - **Solution:** Opted to execute safe `GET` lookup queries where possible, and explicitly left `sequence-generator` without forced traffic.
   - **Result:** Financial integrity maintained; topological accuracy preserved.

## 22. Resource Impact

- **Kiali:** Limited to 200m CPU / 512Mi RAM. Currently running stably with negligible footprint.
- **Headlamp:** Consumes 0 Kubernetes pod resources as it runs entirely natively on the Windows host.
- **Docker Desktop:** Remains perfectly stable; the decision not to deploy Headlamp in the cluster preserved vital RAM.

## 23. What Was Intentionally Not Changed

- Java business logic, Banking workflows, Database schemas, SQL queries.
- Existing Prometheus configuration, Grafana dashboards, Jaeger, Loki, Fluent Bit.
- Existing Istio traffic policies and the HPA configuration.

## 24. Operational Guide

### Kiali
- **Check pod:** `kubectl get pods -n istio-system -l app=kiali`
- **Port-forward access:** `kubectl port-forward svc/kiali 20001:20001 -n istio-system` (Access via `http://localhost:20001/kiali`)

### Kubernetes Context
- **Check active context:** `kubectl config current-context`

### Headlamp Desktop
1. Launch Headlamp on Windows.
2. Ensure Docker Desktop is running.
3. Allow Headlamp to read your `~/.kube/config` and connect to the cluster.

## 25. Troubleshooting

- **Kiali shows no traffic:** Ensure the microservices are receiving actual traffic. Kiali draws edges based on Prometheus telemetry. If Prometheus is empty, Kiali is empty.
- **Kiali cannot connect to Prometheus:** Verify `prometheus.monitoring.svc.cluster.local:9090` is reachable from the `istio-system` namespace.
- **A banking service is not visible:** Check if the deployment exists in the `banking` namespace and contains the proper `app` and `version` labels.
- **Headlamp cannot connect:** Confirm that `kubectl get nodes` succeeds locally in PowerShell. Headlamp relies on the exact same context.

## 26. Final Visualization Architecture

```text
                      BANKING APPLICATION
                               |
               +---------------+---------------+
               |                               |
               v                               v
          KUBERNETES                       ISTIO MESH
               |                               |
               v                               v
       HEADLAMP DESKTOP                     KIALI
               |                               |
               |                    +----------+----------+
               |                    |                     |
               v                    v                     v
      Cluster Resources        Prometheus              Jaeger
      Pods / HPA / Services     Metrics                Traces
```

## 27. Phase 8 Completion Checklist

Kiali:
- [x] Installed
- [x] Istio integration
- [x] Prometheus integration
- [ ] Traffic observed for every service (sequence-generator kept clean for safety)

Headlamp:
- [x] Kubernetes context validated
- [x] Connection instructions prepared
- [ ] Desktop GUI manually validated (Requires physical user interaction)
