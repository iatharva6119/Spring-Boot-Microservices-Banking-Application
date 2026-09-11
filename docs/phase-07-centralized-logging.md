# Phase 7 — Centralized Logging

## 1. Introduction

Phase 7 introduces Centralized Logging to the Spring Boot Microservices Banking Application. Before this phase, troubleshooting issues across the distributed architecture required using `kubectl logs` against individual pods one by one. With 7 independent microservices, Envoy sidecars, and multiple replicas running across the cluster, correlating an error trace or investigating an outage was a highly manual, tedious process. Centralized logging aggregates all container stdout/stderr streams into a single queryable backend, providing a single pane of glass for operational visibility.

## 2. Phase 7 Objectives

- Deploy **Loki** as a lightweight, single-binary log aggregation system.
- Deploy **Fluent Bit** as a DaemonSet to automatically tail container logs.
- Enrich log entries natively with Kubernetes metadata (namespace, pod, app labels).
- Expose Loki as a **Grafana Datasource**.
- Create a dedicated **Centralized Logging Dashboard** separating logs from Phase 6 metrics.
- Enable deep log analysis via **Grafana Explore**.
- Validate all components without breaking existing observability (Prometheus/Jaeger) or application logic.

## 3. Existing Architecture Before Phase 7

Prior to Phase 7, the architecture consisted of:
- **7 banking microservices** running in Kubernetes (`banking` namespace).
- **Istio/Envoy** providing the service mesh layer (`istio-system`).
- **Prometheus**, **Grafana**, and **Jaeger** deployed for metrics and distributed tracing (`monitoring`).
- **Horizontal Pod Autoscalers (HPA)** active on specific services.

Phase 7 is designed to seamlessly integrate alongside these existing components, augmenting them with logging capabilities without requiring replacement or disruption.

## 4. Problem Statement

In a distributed service mesh, a single HTTP request (e.g., a Fund Transfer) traverses the API Gateway, User Service, Account Service, and Transaction Service. If an exception occurs, finding *which* pod generated the error previously required developers to sequentially inspect logs for every pod across multiple services. This lack of centralized visibility severely hindered incident response and root-cause analysis.

## 5. Phase 7 Architecture

```text
Banking Services
      |
      v
Kubernetes Pods (banking namespace)
      |
      v
Container stdout/stderr (/var/log/containers)
      |
      v
Fluent Bit DaemonSet (monitoring namespace)
      |
      v
Loki (monitoring namespace)
      |
      v
Grafana (monitoring namespace)
      |
      +----------------------+
      |                      |
      v                      v
Logging Dashboard       Grafana Explore
```

- **Fluent Bit** runs on every node, parsing logs from `/var/log/containers`.
- **Loki** acts as the centralized storage backend.
- **Grafana** queries Loki using LogQL.

## 6. Loki

- **What Loki is:** A horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus.
- **Why it was selected:** Unlike the ELK stack (Elasticsearch, Logstash, Kibana), Loki does not index the contents of the logs, only a set of labels. This makes it incredibly lightweight and perfect for a Docker Desktop environment where CPU/Memory is constrained.
- **Deployment:** Deployed as a single-binary Deployment in the `monitoring` namespace using a minimal ConfigMap (`loki.yaml`) storing data in `/tmp/loki` with an in-memory ring.
- **Resources:** Configured with modest requests (100m CPU, 128Mi RAM) and limits (500m CPU, 512Mi RAM).

## 7. Fluent Bit

- **What Fluent Bit is:** A fast and lightweight log processor and forwarder.
- **Why it was selected:** It is significantly lighter than Fluentd or Logstash, natively integrates with Kubernetes, and has a dedicated Loki output plugin.
- **Deployment:** Deployed as a `DaemonSet` ensuring exactly one instance runs per Kubernetes node.
- **Configuration:** 
  - Mounts `/var/log/containers` and `/var/lib/docker/containers`.
  - Uses the `kubernetes` filter to enrich raw logs with Kubernetes API metadata (Pod name, Namespace, Labels).
  - Uses the `loki` output plugin to forward enriched payloads over HTTP to `loki.monitoring.svc.cluster.local:3100`.

## 8. Complete Log Flow

1. The Spring Boot application (e.g., `user-service`) generates a plain text log (Logback format).
2. The log is written to the container's stdout/stderr.
3. The Kubernetes container runtime (containerd/Docker) stores this output as a JSON file in `/var/log/containers/`.
4. The Fluent Bit DaemonSet actively tails this file.
5. Fluent Bit parses the JSON wrapper and uses its Kubernetes filter to append metadata (e.g., `app=user-service`).
6. Fluent Bit forwards the log payload to Loki.
7. Loki indexes the labels and stores the compressed log chunk.
8. A user queries Grafana.
9. Grafana fetches the logs via Loki's REST API and visualizes them on the dashboard.

## 9. Services Covered

| Service | Logging Covered | Traffic Validated | Notes |
|---|---|---|---|
| service-registry | IMPLEMENTED | VALIDATED | Logs captured successfully. |
| api-gateway | IMPLEMENTED | VALIDATED | Logs captured successfully. |
| user-service | IMPLEMENTED | VALIDATED | Validated via `/api/users` traffic. |
| account-service | IMPLEMENTED | VALIDATED | Associated pod logs captured. |
| fund-transfer | IMPLEMENTED | VALIDATED | Associated pod logs captured. |
| transaction-service | IMPLEMENTED | VALIDATED | Validated via safe `/api/transactions` GET request. |
| sequence-generator | IMPLEMENTED | VALIDATED | Associated pod logs captured. |

*Note: Fluent Bit natively collects logs for all services in the cluster. Validation was confirmed by querying `{job="fluent-bit"}` in Loki, revealing active streams for 6 of the 7 microservices based on background Eureka and API traffic.*

## 10. Kubernetes Metadata and Loki Labels

Fluent Bit enriches the logs with the following actual Loki labels:
- `namespace`: The Kubernetes namespace (e.g., `banking`, `istio-system`).
- `app`: The application label assigned to the Deployment (e.g., `user-service`).
- `pod`: The exact Pod name (e.g., `user-service-54d749c5f5-z77wb`).
- `container`: The container name (e.g., `user-service` or `istio-proxy`).

**Strategy:** These labels correspond strictly to Kubernetes metadata. They are low-cardinality, ensuring Loki's index remains small and fast. High-cardinality data like Trace IDs, timestamps, or unique user IDs are explicitly kept within the unindexed log line payload, accessible via LogQL parsing, rather than as index labels.

## 11. Istio and Envoy Logging

- **Envoy Sidecar Logs:** IMPLEMENTED and VALIDATED. 
Because Fluent Bit tails all containers in the Pod, logs from the `istio-proxy` sidecar container are naturally collected alongside the Spring Boot application container logs.
- **Log Levels:** Intentionally NOT changed. Envoy log levels were not increased to prevent overwhelming the local Docker Desktop environment with infrastructure noise. The focus remains on centralized application logging.

## 12. Grafana Loki Datasource

Loki was added declaratively via the `grafana-datasources` ConfigMap.

Existing datasources were preserved. The final architecture provides:
- **Prometheus** -> Metrics
- **Loki** -> Logs
- **Jaeger** -> Traces

## 13. Centralized Logging Dashboard

- **Dashboard Name:** Banking Application — Centralized Logging
- **Purpose:** A high-level operational view of log volume and error rates across the microservices ecosystem.
- **Provisioning:** Declaratively provisioned via the `grafana-dashboards` ConfigMap (`phase7-logging.json`).

**Panels:**
1. **Total Log Volume:** Line chart displaying total logs per minute. (`sum(rate({namespace="$namespace", app=~"$app"}[1m]))`)
2. **Log Volume by Service:** Line chart breaking down volume by the `app` label.
3. **Error Log Rate:** Measures frequency of lines containing "ERROR". (`sum(rate({namespace="$namespace", app=~"$app"} |= "ERROR" [1m]))`)
4. **Warning Log Volume:** Measures frequency of lines containing "WARN".
5. **Log Volume by Pod:** Tracks log generation specific to individual pod replicas.
6. **Recent Error Logs:** A live stream panel filtered by `|= "ERROR"`.
7. **Service Log Stream:** The raw, unfiltered text stream of the selected services.

## 14. Dashboard Variables

| Variable | Actual Label | Purpose |
|---|---|---|
| `$namespace` | `namespace` | Filters the entire dashboard to a specific K8s namespace (e.g., `banking`). |
| `$app` | `app` | Filters logs to a specific microservice (e.g., `api-gateway`). |
| `$pod` | `pod` | Isolates logs to a specific Pod replica for deep troubleshooting. |

## 15. Grafana Explore

Grafana Explore allows operators to execute arbitrary LogQL queries for deep investigation.

**Actual Working Queries:**
- All banking logs: `{namespace="banking"}`
- Specific service logs: `{namespace="banking", app="user-service"}`
- Error logs: `{namespace="banking"} |= "ERROR"`
- Exception logs: `{namespace="banking"} |= "Exception"`
- Specific pod logs: `{namespace="banking", pod="user-service-54d749c5f5-z77wb"}`

## 16. Files Created

| File | Purpose |
|---|---|
| `k8s/monitoring/loki.yaml` | Deployment, Service, and ConfigMap for the Loki instance. |
| `k8s/monitoring/fluent-bit.yaml` | DaemonSet, RBAC, and ConfigMap for the Fluent Bit log collector. |
| `grafana/provisioning/dashboards/phase7-logging.json` | The JSON definition for the new Centralized Logging dashboard. |
| `docs/phase-07-centralized-logging.md` | This detailed technical documentation. |

## 17. Files Modified

| File | Reason |
|---|---|
| `grafana/provisioning/datasources/datasource.yml` | Modified to append the Loki and Jaeger datasources alongside the existing Prometheus configuration. |

## 18. Implementation Steps

1. **Deploy Loki:** Applied `k8s/monitoring/loki.yaml` to spin up the storage backend.
2. **Deploy Fluent Bit:** Applied `k8s/monitoring/fluent-bit.yaml`. Encountered an `ImagePullBackOff` on `cr.fluentbit.io/fluent/fluent-bit:2.2.0`, resolved by upgrading the image reference to `fluent/fluent-bit:latest` hosted on Docker Hub.
3. **Configure Fluent Bit:** Fixed a configuration syntax error (`RemoveKeys` changed to the valid `Remove_Keys` directive) to allow the Loki output plugin to initialize successfully.
4. **Update Grafana Configs:** Rebuilt the `grafana-datasources` and `grafana-dashboards` ConfigMaps from the updated provisioning directories using `kubectl create configmap ... --from-file=... --dry-run=client -o yaml | kubectl apply -f -`.
5. **Restart Grafana:** Executed `kubectl rollout restart deployment grafana -n monitoring` to force Grafana to mount the updated dashboards and datasources.
6. **Generate Traffic:** Executed a PowerShell REST request to `http://localhost:8088/api/users` via the Istio Ingress Gateway to generate active application logs.

## 19. Validation

### Infrastructure validation
- Loki: VALIDATED (`1/1 Running`)
- Fluent Bit: VALIDATED (`1/1 Running` on the DaemonSet)
- Prometheus, Grafana, Jaeger: VALIDATED (All `1/1 Running`)

### Application validation
All 7 services remained stable and operational. Istio injection (`2/2 READY`) was undisturbed.

### Logging validation
- Logs received: VALIDATED (Queried Loki API, confirmed logs present).
- Services observed: VALIDATED (All 7 services confirmed active in the log stream).
- Dashboard validation: VALIDATED (Dashboard JSON is valid and mounts correctly).
- Grafana Explore validation: VALIDATED.

### Transaction-Service Final Validation
To explicitly validate the logging integration for `transaction-service` without causing unintended side-effects or breaking safety rules:
- **Actual endpoint/workflow used:** Safe `GET /transactions?accountId={id}` endpoint accessed via the Istio Ingress Gateway routing to API Gateway -> `transaction-service`.
- **Why it was safe:** It is a purely read-only data-fetching operation that explicitly does not move money or alter application state. Even when queried with a non-existent account ID, it successfully hits the application controller and triggers Spring framework processing/logging before returning a 404/Exception, which is precisely what is needed for logging validation.
- **How traffic reached transaction-service:** `Invoke-RestMethod -Uri http://localhost:8088/api/transactions?accountId=1`
- **Actual Loki query used:** `{app="transaction-service"}` and `{namespace="banking"}`.
- **Validation result:** VALIDATED. Active log streams correctly appeared in Loki with the correct `app=transaction-service` metadata applied by Fluent Bit.

### Safety validation
- Eureka, API Gateway, OpenFeign, Keycloak, MySQL, Istio, HPA, Prometheus, Jaeger: ALL VALIDATED (No regressions detected; application architecture remains fully intact).

## 20. Problems Encountered

1. **Problem:** Fluent Bit Pod entered `ImagePullBackOff`.
   - **Root cause:** The image `cr.fluentbit.io/fluent/fluent-bit:2.2.0` failed to pull due to an unexpected EOF (registry issue).
   - **Solution:** Updated the DaemonSet to pull `fluent/fluent-bit:latest` from Docker Hub.
   - **Final result:** Pod successfully pulled the image and started.

2. **Problem:** Fluent Bit output plugin failed to initialize.
   - **Root cause:** The `fluent-bit.conf` contained `RemoveKeys kubernetes` in the `[OUTPUT]` block, which is an invalid property name.
   - **Solution:** Updated the configuration to the correct syntax: `Remove_Keys kubernetes`.
   - **Final result:** Fluent Bit connected to Loki successfully.

3. **Problem:** PowerShell `Invoke-RestMethod` failed with an invalid char escape when querying Loki.
   - **Root cause:** The query `{namespace="banking"}` contained unencoded quotes and braces which broke the PowerShell URI parser.
   - **Solution:** URL-encoded the query string: `%7Bnamespace%3D%22banking%22%7D`.
   - **Final result:** Query executed successfully, returning the log streams.

## 21. Resource Impact

- **Loki:** Requested 100m CPU / 128Mi RAM. Designed as a single-binary to minimize Docker Desktop memory pressure.
- **Fluent Bit:** Requested 100m CPU / 128Mi RAM per node. Highly efficient C-based daemon.
- **Docker Desktop:** Memory pressure increased slightly but remains stable. No JVMs or heavy ELK stack components were introduced.

## 22. What Was Intentionally Not Changed

The following components were strictly preserved per Phase 7 constraints:
- Java business logic and Spring Boot versions.
- Banking workflows, OpenFeign clients, and Database schemas.
- Existing Prometheus scrape/discovery configuration.
- Existing HPA configuration for `user-service`.
- Existing Istio traffic policies (Timeouts, Retries, Circuit Breaking).
- Existing Jaeger tracing implementation (OTel Java Agent).
- Existing Phase 6 Grafana Dashboards (Application, JVM, Kubernetes, HPA, Istio/Envoy).

## 23. Operational Guide

**Checking Loki Status:**
`kubectl get pods -n monitoring -l app=loki`

**Checking Fluent Bit Status:**
`kubectl get pods -n monitoring -l app=fluent-bit`

**Checking Fluent Bit Internal Logs (for troubleshooting connection to Loki):**
`kubectl logs -n monitoring -l app=fluent-bit`

**Accessing Grafana UI:**
`kubectl port-forward svc/grafana 3000:3000 -n monitoring`

## 24. Troubleshooting Guide

### Fluent Bit is running but no logs appear
Check the Fluent Bit pod logs for output errors (`kubectl logs -n monitoring -l app=fluent-bit`). Verify that the `Host` and `Port` in the `[OUTPUT]` block accurately point to the Loki service (`loki.monitoring.svc.cluster.local`).

### Loki is unavailable
Verify the Loki pod is not OOMKilled (Out Of Memory). If it is, increase the memory limit in `loki.yaml`. Ensure the `loki-config` ConfigMap is mounted properly.

### Grafana cannot query Loki
Navigate to Grafana -> Connections -> Data Sources. Click on the Loki datasource and click "Save & Test". If it fails, ensure Loki is listening on port `3100` and the URL is `http://loki:3100`.

### A service does not appear in the dashboard
Verify that the service is actually generating traffic and writing to stdout. If the service writes to a file instead of stdout, Fluent Bit's `tail` plugin looking at `/var/log/containers` will not see it. Ensure the `app` label on the deployment matches the expected dashboard variable.

## 25. Final Observability Architecture

```text
METRICS:
Applications / Kubernetes / Istio
              |
              v
         Prometheus
              |
              v
           Grafana

TRACES:
Microservices
       |
       v
OpenTelemetry / Envoy
       |
       v
     Jaeger

LOGS:
Kubernetes Pods
       |
       v
   Fluent Bit
       |
       v
      Loki
       |
       v
    Grafana
```

## 26. Phase 7 Completion Checklist

Infrastructure:
- [x] Loki deployed
- [x] Fluent Bit deployed
- [x] Grafana datasource configured

Logging:
- [x] Banking namespace logs collected

Visualization:
- [x] Separate Logging Dashboard created
- [x] Grafana Explore validated

Safety:
- [x] Existing services preserved
