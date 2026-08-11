# Banking Application — Performance Engineering Monitoring

Complete observability stack for the Spring Boot Microservices Banking Application.
Implemented using **Prometheus + Grafana + cAdvisor + Spring Boot Actuator + Micrometer**.

---

## 1. Monitoring Architecture

```
                         ┌──────────────────┐
                         │     Grafana      │
                         │   Performance    │
                         │    Dashboards    │
                         └────────▲─────────┘
                                  │
                                  │ PromQL
                                  │
                         ┌────────┴─────────┐
                         │    Prometheus    │
                         │ Metrics Storage  │
                         └───────▲───▲──────┘
                                 │   │
                   JVM Metrics   │   │ Container Metrics
                                 │   │
                ┌────────────────┘   └──────────────┐
                │                                   │
        ┌───────┴────────┐                    ┌─────┴──────┐
        │ Spring Boot    │                    │  cAdvisor  │
        │   Actuator     │                    │            │
        │   Micrometer   │                    └─────┬──────┘
        └───────▲────────┘                          │
                │                                   │
        ┌───────┴───────────────────────────────────┴──────┐
        │                  Docker / banking-network         │
        │                                                   │
        │ API Gateway (8080)   Account Service (8081)       │
        │ User Service (8082)  Sequence Generator (8083)    │
        │ Transaction Service (8084)  Fund Transfer (8085)  │
        │ Service Registry (8761)                           │
        └───────────────────────────────────────────────────┘
```

---

## 2. Components

| Component          | Role                               | Version   |
|--------------------|-------------------------------------|-----------|
| Spring Boot Actuator | Exposes `/actuator/prometheus`   | 2.7.x BOM |
| Micrometer Prometheus | Formats metrics for Prometheus  | 1.9.x BOM |
| Prometheus         | Scrapes and stores time-series data | v2.47.0   |
| Grafana            | Visualization and dashboards        | v10.1.0   |
| cAdvisor           | Docker container resource metrics   | v0.47.2   |

---

## 3. Detected Existing Versions (Phase 1 Inspection)

```text
Java:          17 (eclipse-temurin:17-jdk in Dockerfiles)
Maven:         3.9.16
Spring Boot:   2.7.14 (API-Gateway, User-Service, Fund-Transfer, Service-Registry)
               2.7.15 (Account-Service, Transaction-Service, Sequence-Generator)
Spring Cloud:  2021.0.8 (all services)
Actuator:      Already present in ALL 7 services (no additions needed)
Micrometer:    Added micrometer-registry-prometheus to all 7 pom.xml files
```

---

## 4. Docker Services — Ports

| Service          | Port  | Purpose                            |
|------------------|-------|------------------------------------|
| service-registry | 8761  | Eureka UI                          |
| api-gateway      | 8080  | API Gateway                        |
| account-service  | 8081  | Account microservice               |
| user-service     | 8082  | User microservice                  |
| sequence-generator | 8083 | Sequence Generator microservice   |
| transaction-service | 8084 | Transaction microservice         |
| fund-transfer    | 8085  | Fund Transfer microservice         |
| prometheus       | 9090  | Prometheus UI + API                |
| grafana          | 3000  | Grafana UI (admin/admin)           |
| cadvisor         | 8089  | cAdvisor UI + metrics              |

---

## 5. Actuator Configuration

Added to all 7 `application.yml` files (Spring Boot 2.7.x syntax):

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
```

### Available Endpoints (per service)

```
/actuator/health     — Health check with details
/actuator/info       — Application info
/actuator/metrics    — Metrics list
/actuator/prometheus — Prometheus metrics (raw text format)
```

> **Note:** Sensitive endpoints (`/env`, `/configprops`, `/heapdump`, `/threaddump`) are NOT exposed.

---

## 6. Prometheus Configuration

**File:** `prometheus/prometheus.yml`

- Global scrape interval: **15s**
- Retention: **15 days**
- Rule files: `prometheus/rules/banking-alerts.yml`

### Scrape Jobs

| Job Name           | Target                     | Path                  |
|--------------------|----------------------------|-----------------------|
| service-registry   | service-registry:8761      | /actuator/prometheus  |
| api-gateway        | api-gateway:8080           | /actuator/prometheus  |
| account-service    | account-service:8081       | /actuator/prometheus  |
| user-service       | user-service:8082          | /actuator/prometheus  |
| sequence-generator | sequence-generator:8083    | /actuator/prometheus  |
| transaction-service| transaction-service:8084   | /actuator/prometheus  |
| fund-transfer      | fund-transfer:8085         | /actuator/prometheus  |
| cadvisor           | cadvisor:8080              | /metrics              |
| prometheus         | localhost:9090             | /metrics              |

> All targets use Docker service names (not localhost) because Prometheus runs inside `banking-network`.

---

## 7. Grafana Configuration

**File:** `grafana/provisioning/datasources/datasource.yml`
**File:** `grafana/provisioning/dashboards/dashboard.yml`
**File:** `grafana/provisioning/dashboards/banking-performance.json`

- Prometheus data source auto-provisioned at `http://prometheus:9090`
- Dashboard auto-loaded on first startup

### Dashboard: "Banking Application — Performance Engineering"

| Row | Title                        | Content                                         |
|-----|------------------------------|-------------------------------------------------|
| 1   | Overall System               | Total RPS, Error Rate, Active Services, Requests, Avg Latency |
| 2   | Latency                      | p50, p90, p95, p99, avg response time           |
| 3   | HTTP Status                  | 2xx/4xx/5xx rate, RPS per service               |
| 4   | JVM Memory & GC              | Heap used/committed/max, Non-heap, GC pause, GC rate |
| 4b  | JVM Threads & Classes        | Live/peak/daemon threads, Loaded/unloaded classes|
| 5   | CPU                          | Process CPU, System CPU, Container CPU (cAdvisor)|
| 6   | Memory                       | JVM heap/committed, Container memory (cAdvisor) |
| 7   | Per-Microservice Latency & RPS | p95 per service, Throughput per service       |
| 8   | Database Connection Pool     | HikariCP active/idle/max, utilization %, acquire time, pending, timeouts |
| 9   | Docker Containers (cAdvisor) | Container CPU, Memory, Network RX/TX, Restarts |
| 10  | Target Health                | UP/DOWN status per service, Process uptime      |

---

## 8. cAdvisor Configuration

**Image:** `gcr.io/cadvisor/cadvisor:v0.47.2`
**Host Port:** `8089` (internal: `8080`)

Monitors:
- Container CPU usage
- Container memory usage
- Container network RX/TX
- Container filesystem usage
- Container disk I/O

> cAdvisor requires `privileged: true` and access to host paths (`/`, `/var/run`, `/sys`, `/var/lib/docker`).

---

## 9. Metrics Collected

### JVM Metrics (from Micrometer)
```
jvm_memory_used_bytes{area, id}
jvm_memory_committed_bytes{area, id}
jvm_memory_max_bytes{area, id}
jvm_gc_pause_seconds_count{action, cause}
jvm_gc_pause_seconds_sum{action, cause}
jvm_threads_live_threads
jvm_threads_peak_threads
jvm_threads_daemon_threads
jvm_classes_loaded_classes
jvm_classes_unloaded_classes_total
```

### HTTP Metrics (from Micrometer)
```
http_server_requests_seconds_count{application, method, status, uri, exception}
http_server_requests_seconds_sum{application, method, status, uri, exception}
http_server_requests_seconds_bucket{application, le, ...}
```

### Process/System Metrics (from Micrometer)
```
process_cpu_usage{application}
system_cpu_usage{application}
process_uptime_seconds{application}
```

### Database Metrics (HikariCP via Micrometer)
```
hikaricp_connections_active{application, pool}
hikaricp_connections_idle{application, pool}
hikaricp_connections_max{application, pool}
hikaricp_connections_pending{application, pool}
hikaricp_connections_timeout_total{application, pool}
hikaricp_connections_acquire_seconds_sum{application, pool}
hikaricp_connections_acquire_seconds_count{application, pool}
```

### Container Metrics (from cAdvisor)
```
container_cpu_usage_seconds_total{name}
container_memory_usage_bytes{name}
container_network_receive_bytes_total{name}
container_network_transmit_bytes_total{name}
container_fs_reads_bytes_total{name}
container_fs_writes_bytes_total{name}
```

---

## 10. Key PromQL Queries

### Request Rate (RPS)
```promql
sum(rate(http_server_requests_seconds_count{application=~"$service"}[1m]))
```

### p95 Latency
```promql
histogram_quantile(0.95,
  sum(rate(http_server_requests_seconds_bucket{application=~"$service", uri!~"/actuator.*"}[5m]))
  by (le)
)
```

### 5xx Error Rate
```promql
sum(rate(http_server_requests_seconds_count{application=~"$service", status=~"5.."}[1m]))
/
sum(rate(http_server_requests_seconds_count{application=~"$service"}[1m]))
```

### JVM Heap Utilization %
```promql
sum(jvm_memory_used_bytes{application=~"$service", area="heap"})
/
sum(jvm_memory_max_bytes{application=~"$service", area="heap"})
```

### GC Pause Rate
```promql
sum(rate(jvm_gc_pause_seconds_sum{application=~"$service"}[1m])) by (application, action)
/
sum(rate(jvm_gc_pause_seconds_count{application=~"$service"}[1m])) by (application, action)
```

### HikariCP Pool Utilization
```promql
hikaricp_connections_active{application=~"$service"}
/
hikaricp_connections_max{application=~"$service"}
```

### Container CPU Usage
```promql
sum(rate(container_cpu_usage_seconds_total{name=~"api-gateway|account-service|..."}[1m])) by (name)
```

---

## 11. Alerts

**File:** `prometheus/rules/banking-alerts.yml`

| Alert                       | Condition                              | Severity |
|-----------------------------|----------------------------------------|----------|
| ServiceDown                 | Target unreachable for 1m              | critical |
| HighP95Latency              | p95 > 2s for 5m                        | warning  |
| CriticalP99Latency          | p99 > 5s for 5m                        | critical |
| High5xxErrorRate            | Error rate > 5% for 3m                 | warning  |
| CriticalErrorRate           | Error rate > 20% for 2m                | critical |
| HighProcessCPU              | CPU > 80% for 5m                       | warning  |
| CriticalProcessCPU          | CPU > 95% for 3m                       | critical |
| HighJVMHeapUtilization      | Heap > 85% of max for 5m               | warning  |
| CriticalJVMHeapUtilization  | Heap > 95% of max for 2m               | critical |
| HighGCPauseTime             | Avg GC pause > 200ms for 5m            | warning  |
| HighDBConnectionPoolUtil    | Pool utilization > 80% for 3m          | warning  |
| DBConnectionPoolExhaustion  | Pool utilization > 95% for 1m          | critical |
| DBConnectionTimeouts        | Connection timeouts occurring           | warning  |

---

## 12. URLs

```
Prometheus UI:        http://localhost:9090
Prometheus Targets:   http://localhost:9090/targets
Prometheus Alerts:    http://localhost:9090/alerts
Grafana:              http://localhost:3000          (admin / admin)
cAdvisor:             http://localhost:8089

Actuator Health:
  http://localhost:8080/actuator/health    (api-gateway)
  http://localhost:8081/actuator/health    (account-service)
  http://localhost:8082/actuator/health    (user-service)
  http://localhost:8083/actuator/health    (sequence-generator)
  http://localhost:8084/actuator/health    (transaction-service)
  http://localhost:8085/actuator/health    (fund-transfer)
  http://localhost:8761/actuator/health    (service-registry)

Actuator Prometheus:
  http://localhost:8080/actuator/prometheus
  http://localhost:8081/actuator/prometheus
  http://localhost:8082/actuator/prometheus
  http://localhost:8083/actuator/prometheus
  http://localhost:8084/actuator/prometheus
  http://localhost:8085/actuator/prometheus
  http://localhost:8761/actuator/prometheus
```

---

## 13. Start / Stop / Rebuild Commands

### Build Application JARs
```powershell
# Build all services (run from each service directory)
cd Account-Service;  mvn clean package -DskipTests; cd ..
cd API-Gateway;      mvn clean package -DskipTests; cd ..
cd User-Service;     mvn clean package -DskipTests; cd ..
cd Transaction-Service; mvn clean package -DskipTests; cd ..
cd Fund-Transfer;    mvn clean package -DskipTests; cd ..
cd Sequence-Generator;  mvn clean package -DskipTests; cd ..
cd Service-Registry; mvn clean package -DskipTests; cd ..
```

### Build Docker Images
```powershell
docker compose build
```

### Start All Services (Application + Monitoring)
```powershell
docker compose up -d
```

### Start Monitoring Only (without rebuilding app)
```powershell
docker compose up -d prometheus grafana cadvisor
```

### Stop All
```powershell
docker compose down
```

### Stop and Remove Volumes (clean slate)
```powershell
docker compose down -v
```

### View Logs
```powershell
docker logs prometheus
docker logs grafana
docker logs cadvisor
docker logs account-service
```

### Reload Prometheus Config (without restart)
```powershell
curl -X POST http://localhost:9090/-/reload
```

---

## 14. Performance Testing Workflow

```
1. Start stack:           docker compose up -d
2. Verify targets UP:     http://localhost:9090/targets
3. Open Grafana:          http://localhost:3000
4. Open dashboard:        "Banking Application — Performance Engineering"
5. Run JMeter test:       Point JMeter to http://localhost:8080
6. Observe in real-time:
   - Row 1: RPS increasing
   - Row 2: Latency percentiles rising under load
   - Row 3: HTTP status distribution
   - Row 4: JVM heap climbing, GC kicking in
   - Row 5: CPU climbing
   - Row 8: HikariCP connections saturating
   - Row 9: Container resource usage
7. Correlate bottlenecks using the dashboard variables
```

---

## 15. Troubleshooting

### Prometheus targets are DOWN

1. Verify application containers are running: `docker ps`
2. Check container logs: `docker logs account-service`
3. Check if Prometheus is on the same network: `docker network inspect banking_banking-network`
4. Try manual scrape: `docker exec -it prometheus wget -O- http://account-service:8081/actuator/prometheus`
5. Confirm `/actuator/prometheus` endpoint exists: `curl http://localhost:8081/actuator/prometheus`

### Grafana shows "No data"

1. Verify Prometheus datasource is connected: Grafana → Configuration → Data Sources → Prometheus → Test
2. Run a test query in Prometheus: `http://localhost:9090/graph` → query `up`
3. Check Grafana logs: `docker logs grafana`

### cAdvisor not showing container metrics

- On Windows Docker Desktop, `/var/lib/docker` maps through WSL2 — cAdvisor may have limited data.
- On Linux hosts, all container metrics will be fully available.

### Actuator endpoint returns 404

- Verify `micrometer-registry-prometheus` was added to the service's `pom.xml`
- Rebuild the Docker image: `docker compose build <service-name>`
- Check the application log: `docker logs account-service | grep prometheus`

### Spring Boot 2.7.x Property Notes

The correct Prometheus metrics export property for Spring Boot **2.7.x** is:
```yaml
management.metrics.export.prometheus.enabled: true
```
NOT the Spring Boot 3.x syntax (`management.prometheus.metrics.export.enabled`).

---

## 16. Known Limitations

1. **cAdvisor on Windows Docker Desktop:** Container metrics may be limited due to WSL2 virtualization layer. CPU/memory metrics will be available but `/dev/kmsg` and some disk metrics may not be fully populated.

2. **Distributed Tracing:** Not implemented in this phase. See Section 17 for the future plan.

3. **No MySQL exporter:** Database-level metrics (slow query logs, InnoDB buffer pool, lock waits) require `mysqld_exporter`. See Section 18. Application-level HikariCP metrics are available.

4. **No authentication on Prometheus:** Prometheus UI (port 9090) has no authentication. In production, restrict access via network policies or a reverse proxy.

5. **Alert routing:** Alert rules exist in Prometheus but Alertmanager is not configured. To route alerts to Slack/email/PagerDuty, add Alertmanager to docker-compose.yml.

---

## 17. Future Kubernetes Monitoring Plan

When migrating to Kubernetes, the monitoring stack will evolve:

```
kube-state-metrics    — Kubernetes resource state
node-exporter         — Node (VM) level metrics
Prometheus Operator   — Manages Prometheus via CRDs
ServiceMonitor CRDs   — Declarative scrape configuration
Grafana               — Same dashboards, new data sources
HPA metrics           — Horizontal Pod Autoscaler visibility
```

Helm chart: `kube-prometheus-stack` (combines all the above).

---

## 18. Future Distributed Tracing Plan

**Compatible with Spring Boot 2.7.x + Spring Cloud 2021.0.8:**

The existing Spring Cloud version ships with `spring-cloud-sleuth` which supports:
- Brave tracer (Zipkin-compatible)
- OpenTelemetry bridge (via `spring-cloud-sleuth-otel`)

**Proposed implementation:**

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

**Stack:**
```
API Gateway
    ↓ trace-id propagated via HTTP headers (B3/W3C)
Account Service
    ↓
Transaction Service
    ↓
MySQL (JDBC instrumented via datasource proxy)
    ↓
Zipkin UI (http://localhost:9411)
    ↓
Grafana Tempo (optional — replaces Zipkin for Grafana integration)
```

This allows identifying **exactly where latency is being spent** in the request chain, complementing the Prometheus aggregate metrics.

> **IMPORTANT:** Do NOT add tracing until basic monitoring is validated. No Spring Boot version upgrade required for Sleuth.

---

## 19. Files Modified / Created

### Modified Files
| File | Change |
|------|--------|
| `Account-Service/pom.xml` | Added `micrometer-registry-prometheus` |
| `API-Gateway/pom.xml` | Added `micrometer-registry-prometheus` |
| `User-Service/pom.xml` | Added `micrometer-registry-prometheus` |
| `Transaction-Service/pom.xml` | Added `micrometer-registry-prometheus` |
| `Fund-Transfer/pom.xml` | Added `micrometer-registry-prometheus` |
| `Sequence-Generator/pom.xml` | Added `micrometer-registry-prometheus` |
| `Service-Registry/pom.xml` | Added `micrometer-registry-prometheus` |
| `Account-Service/src/main/resources/application.yml` | Added management/actuator config |
| `API-Gateway/src/main/resources/application.yml` | Added management/actuator config |
| `User-Service/src/main/resources/application.yml` | Added management/actuator config |
| `Transaction-Service/src/main/resources/application.yml` | Added management/actuator config |
| `Fund-Transfer/src/main/resources/application.yml` | Added management/actuator config |
| `Sequence-Generator/src/main/resources/application.yml` | Added management/actuator config |
| `Service-Registry/src/main/resources/application.yml` | Added management/actuator config |
| `docker-compose.yml` | Added prometheus, grafana, cadvisor services + volumes |

### Created Files
| File | Purpose |
|------|---------|
| `prometheus/prometheus.yml` | Prometheus scrape configuration |
| `prometheus/rules/banking-alerts.yml` | Performance alerting rules |
| `grafana/provisioning/datasources/datasource.yml` | Auto-provision Prometheus datasource |
| `grafana/provisioning/dashboards/dashboard.yml` | Dashboard provider configuration |
| `grafana/provisioning/dashboards/banking-performance.json` | Main performance dashboard |
| `MONITORING.md` | This documentation file |
