# Phase 9 — Performance Testing & Bottleneck Analysis

## 1. Phase Objective
Establish a professional performance engineering framework using `k6` to measure response times, throughput, and error rates across the microservices ecosystem. This phase integrates with the existing observability stack to isolate bottlenecks without compromising the application's financial data integrity.

## 2. Existing Architecture
The ecosystem leverages:
- Docker Desktop Kubernetes
- Istio Service Mesh
- Prometheus, Grafana, Jaeger, Loki
- Spring Boot microservices

Phase 9 introduces load-testing *against* this architecture to observe scaling behavior (HPA), resource limits, and JVM stability.

## 3. Why k6 was selected
`k6` is an open-source, developer-centric load testing tool built for performance engineering. It uses JavaScript for scripting, consumes minimal system resources, and generates clear, actionable summary metrics without requiring heavy Java-based GUI tools (like JMeter). 

## 4. All 7 Services Considered
- **API-Gateway:** Tested as the primary entry point.
- **User-Service:** Tested via safe read-only queries.
- **Account-Service:** Tested via safe read-only balance lookups.
- **Transaction-Service:** Tested via safe read-only transaction history queries.
- **Fund-Transfer-Service:** Safe transaction history query utilized; destructive POSTs avoided.
- **Sequence-Generator:** Intentionally avoided direct load to prevent state mutation. Monitored implicitly.
- **Service-Registry:** Intentionally avoided direct load to preserve cluster stability.

## 5. Safe vs Unsafe Endpoint Classification
- **SAFE (Implemented in k6):** `GET /api/users`, `GET /api/accounts?accountId=1`, `GET /api/transactions?accountId=1`, `GET /api/fund-transfers?accountId=1`.
- **UNSAFE (Excluded from k6):** `POST /api/users/register`, `POST /api/fund-transfers`, Sequence generation.

## 6. Authentication Strategy
The `API-Gateway` requires an OAuth2 token from Keycloak for protected routes, though certain GET routes mapped via Istio `VirtualServices` can bypass gateway enforcement locally depending on the namespace context.
To ensure robustness, the k6 scripts use an environment variable `K6_TOKEN`. If provided via `k6 run --env K6_TOKEN="<token>"`, it attaches an `Authorization: Bearer` header.

## 7. Test Environment
Tests run locally on the Windows host targeting the `docker-desktop` Kubernetes cluster via `http://localhost:8088` (the port-forwarded `istio-ingressgateway`).

## 8. Test Prerequisites
1. Ensure Kubernetes is running.
2. `kubectl port-forward svc/istio-ingressgateway 8088:80 -n istio-system`
3. Install `k6` locally (`choco install k6` or download from `k6.io`).

## 9. Baseline Test Design
- **File:** `performance/scripts/baseline-test.js`
- **Purpose:** Establish P50/P95 latencies under minimal, steady traffic (5 VUs).

## 10. Load Test Design
- **File:** `performance/scripts/load-test.js`
- **Purpose:** Simulate normal expected traffic, ramping up to 20 users and sustaining to evaluate GC and thread stability.

## 11. Stress Test Design
- **File:** `performance/scripts/stress-test.js`
- **Purpose:** Push boundaries up to 100 VUs to observe Istio outlier ejection, Envoy queuing, and pod scaling without crashing the local Docker Desktop instance.

## 12. Spike Test Design
- **File:** `performance/scripts/spike-test.js`
- **Purpose:** Immediate jump to 100 VUs, simulating a flash-sale or sudden burst, validating the responsiveness of the HPA.

## 13. k6 Architecture
```text
performance/
├── README.md
├── scripts/
│   ├── baseline-test.js
│   ├── load-test.js
│   ├── stress-test.js
│   ├── spike-test.js
│   └── scenarios/
│       └── safe-workflows.js
├── results/
│   └── .gitignore
└── config/
    └── test-config.example.js
```

## 14. Metrics Collected
- k6: `http_req_duration` (latency), `http_req_failed` (error rate), `http_reqs` (throughput).

## 15. Prometheus Analysis
Prometheus captures:
- Istio Envoy metrics (`istio_requests_total`, `istio_request_duration_milliseconds_bucket`).
- JVM Micrometer metrics (`jvm_memory_used_bytes`, `jvm_gc_pause_seconds_sum`).

## 16. Grafana Dashboard
A distinct dashboard, **"Banking Application — Performance Testing"** (`phase9-performance.json`), provides dedicated panels for:
- Throughput and P95 latency (from Envoy).
- Service-level breakdown.
- JVM Heap consumption.
- HPA scaling operations.

## 17. JVM Analysis
Monitor `jvm_memory_used_bytes` during the **Load Test**. Heavy sustained load will typically produce a sawtooth pattern as Garbage Collection activates. Watch for memory leaks (the baseline of the sawtooth drifting upwards).

## 18. Kubernetes Analysis
During **Stress Tests**, monitor `kube_pod_container_resource_usage_cpu_cores` (if cadvisor is active) to detect CPU throttling when pods exceed their defined `limits`.

## 19. HPA Analysis
During **Spike Tests**, the `kube_deployment_status_replicas` panel on the Performance Dashboard will visualize the delay between the traffic spike and the `user-service` scaling from 1 to 2 replicas.

## 20. Istio/Envoy Analysis
Istio telemetry is critical during stress tests. As load increases, watch for `503 Service Unavailable` or `504 Gateway Timeout` originating from Envoy if the downstream service thread pool is exhausted.

## 21. Jaeger Tracing Analysis
Analyze traces (via Headlamp or port-forwarding Jaeger to `16686`) to find the slowest spans. A slow API Gateway response might be bottlenecked by a slow database query inside `transaction-service`. 

## 22. Loki Logging Analysis
Query Loki (`{namespace="banking"} |= "Exception"`) during stress tests to capture database connection pool exhaustion errors (e.g., HikariCP timeouts) that occur under heavy concurrent load.

## 23. Kiali Traffic Analysis
Observe Kiali during the **Load Test**. Traffic edges will thicken, and RPS (Requests Per Second) will display above the connections. Watch the graph turn yellow or red if HTTP 5xx errors begin accumulating.

## 24. Headlamp Usage
Keep Headlamp Desktop open during testing to observe real-time Kubernetes Events. When the HPA triggers scaling, Headlamp will show ReplicaSet updates and Pod scheduling events instantly.

## 25. How to Execute Each Test
Open PowerShell in the project root:
```powershell
k6 run performance/scripts/baseline-test.js
k6 run performance/scripts/load-test.js
k6 run performance/scripts/stress-test.js
k6 run performance/scripts/spike-test.js
```

## 26. How to Capture Results
The `performance/results/.gitignore` ignores generated files but keeps the directory structured. You can pipe outputs into results logs:
```powershell
k6 run performance/scripts/load-test.js > performance/results/load/run-01.txt
```

## 27. How to Identify Bottlenecks
1. **CPU/Memory Limits:** If K6 shows high latency but JVM Heap is fine, check Kubernetes Limits. The pod may be getting CPU throttled.
2. **Database Connections:** If latency spikes instantly, the HikariCP connection pool may be exhausted (default is usually 10). Check Loki for timeout errors.
3. **Thread Pools:** If Tomcat threads are exhausted, Istio will report 503s.

## 28. Expected Bottleneck Categories
- **Compute:** CPU throttling by Kubernetes.
- **Memory:** JVM out-of-memory or excessive GC pauses.
- **I/O:** Database query latency or network congestion.
- **Configuration:** Thread pools or connection pools set too low.

## 29. Local Docker Desktop Limitations
Docker Desktop imposes strict virtualization resource caps. A stress test capped at 100 VUs is designed to find application-level bottlenecks (like connection pools) *before* it crashes the entire Docker VM.

## 30. Known Limitations
- Destructive workloads (`POST /fund-transfers`) are intentionally omitted; full system throughput involving database writes is not modeled in this phase.
- `sequence-generator` is not explicitly tested.

## 31. Troubleshooting Guide
- **`connection refused` in k6:** Ensure `istio-ingressgateway` is port-forwarded to 8088.
- **`401 Unauthorized` in k6:** Pass the Keycloak token via `--env K6_TOKEN="<token>"`.
- **Docker Desktop freezes:** Reduce the `target: 100` in `stress-test.js` to `50`.

## 32. Future Improvements
- Integrate `k6` results directly into Prometheus/Grafana using the `k6-out-influxdb` or Prometheus remote-write capabilities.
- Create automated mock-data generation scripts to safely test `POST` operations in isolated ephemeral namespaces.
