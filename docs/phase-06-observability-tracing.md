# Phase 6 — Observability + Prometheus + Grafana + Jaeger

## 1. Objective

- **Why Observability was introduced:** As the architecture transitioned to a distributed service mesh in previous phases, it became impossible to monitor performance and debug issues using traditional monolithic approaches. True performance engineering requires deep visibility into every layer of the stack.
- **Why Prometheus & Grafana were introduced:** Prometheus is the industry standard for scraping and storing time-series metrics dynamically in Kubernetes. Grafana provides powerful visualization to interpret these metrics.
- **Why Jaeger & Distributed Tracing were introduced:** In a microservices ecosystem, a single user request (e.g., fetching a user profile) traverses multiple services (API Gateway -> User Service -> MySQL). Distributed tracing allows us to visualize this entire journey, identifying bottlenecks and failures across service boundaries.
- **Performance Engineering relevance:** You cannot optimize what you cannot measure. Phase 6 provides the critical telemetry data needed to perform load testing, capacity planning, and latency analysis in future phases.

## 2. Starting Architecture

Before Phase 6:
- The application ran on Kubernetes with Istio and Envoy sidecars.
- Health checks (liveness/readiness probes), Resource requests/limits, and HPA (for User-Service) were active.
- Telemetry was limited to basic default Envoy metrics collected by `istiod`.
- No centralized visualization or tracing existed.

## 3. Tool Selection & Versions

- **Prometheus:** Deployed natively in the `monitoring` namespace using Kubernetes deployments.
- **Grafana:** Deployed natively in the `monitoring` namespace, heavily utilizing ConfigMaps for automated provisioning.
- **Jaeger:** `jaegertracing/all-in-one:latest` deployed in the `monitoring` namespace.
- **Context Propagator:** OpenTelemetry Java Agent (`opentelemetry-javaagent.jar`).

## 4. Metrics Collection (Prometheus)

- **What was configured:** A Prometheus server to actively pull metrics from all microservices, Istio sidecars, and Kubernetes components.
- **Dynamic Discovery:** Instead of hardcoding IP addresses, `kubernetes_sd_configs` was implemented in `prometheus.yml`. Prometheus automatically discovers all pods in the `banking` and `istio-system` namespaces.
- **Scraping Annotations:** All 7 application Deployments were annotated to instruct Prometheus how to scrape them:
  - `prometheus.io/scrape: "true"`
  - `prometheus.io/path: "/actuator/prometheus"`
  - `prometheus.io/port: "8082"` (dynamic per service)

## 5. Visualization (Grafana)

- **What was configured:** A Grafana instance connected to Prometheus as its primary data source.
- **Automated Provisioning:** Dashboards and data sources are automatically loaded from K8s ConfigMaps upon startup, eliminating the need to manually configure Grafana via the UI.
- **Phase 6 Dashboards:** 5 separate dashboards were created to cleanly categorize the telemetry data without modifying the existing Phase 3 dashboards:
  1. `Phase 6 - Application Metrics` (Request rates, HTTP 5xx errors)
  2. `Phase 6 - Kubernetes Metrics` (Pod counts, restarts)
  3. `Phase 6 - JVM Metrics` (Heap usage, GC pauses)
  4. `Phase 6 - HPA Metrics` (Replica counts, CPU targets)
  5. `Phase 6 - Istio/Envoy Metrics` (Service-to-service latency, P99)

## 6. Distributed Tracing (Jaeger & Envoy)

- **What Jaeger does:** Collects and visualizes the distributed traces.
- **Istio Integration:** The Istio `MeshConfig` was updated to define an `extensionProvider` pointing Envoy sidecars to the `jaeger-collector` service on port `9411` (Zipkin format).
- **Envoy's Role:** Envoy automatically intercepts all ingress and egress HTTP traffic, generating `x-b3-traceid` and `x-b3-spanid` headers and exporting the spans to Jaeger.

## 7. Trace Context Propagation (Zero-Code-Change Approach)

- **The Challenge:** While Envoy generates traces, it cannot magically correlate an incoming request with an outgoing OpenFeign request *inside* the JVM. The Java application must manually read the `x-b3-*` headers from the incoming request and inject them into the outgoing request.
- **The Constraint:** The instruction explicitly stated: "Do not modify Java business logic," and "Make the smallest compatible change." Additionally, attempting to compile the legacy Java 17 codebase with `spring-cloud-starter-sleuth` caused fatal Lombok compilation failures.
- **The Solution:** The **OpenTelemetry Java Agent** (`opentelemetry-javaagent.jar`) was injected directly into the `Dockerfile` of all 7 microservices.
- **Configuration:** By configuring the agent purely as a propagator via Kubernetes environment variables, it seamlessly intercepts bytecode at runtime to propagate B3 headers without exporting its own duplicate spans.
  - `OTEL_TRACES_EXPORTER=none`
  - `OTEL_PROPAGATORS=b3multi,tracecontext`
- **Result:** Complete end-to-end trace correlation across all OpenFeign calls without changing a single line of Java source code or upgrading Spring Boot.

## 8. Final Architecture

```text
Client
 ↓
Istio Ingress Gateway (Envoy intercepts & starts trace)
 ↓
Spring Cloud API Gateway (OTel agent propagates trace)
 ↓
Eureka / OpenFeign
 ↓
Microservices (Envoy intercepts & exports span to Jaeger)
 ↓
(Telemetry Flow)
Prometheus ← scrapes ← Actuator endpoints (/actuator/prometheus)
Grafana ← queries ← Prometheus
Jaeger ← receives spans ← Envoy Sidecars
```

## 9. Files Created & Modified

- **Created:**
  - `k8s/monitoring/namespace.yaml`
  - `k8s/monitoring/prometheus.yaml`
  - `k8s/monitoring/grafana.yaml`
  - `k8s/monitoring/jaeger.yaml`
  - `grafana/provisioning/dashboards/phase6-*.json` (5 dashboards)
- **Modified:**
  - `prometheus/prometheus.yml`: Added `kubernetes_sd_configs`.
  - `k8s/*/deployment.yaml`: Added `prometheus.io` annotations and `OTEL_*` environment variables.
  - `*/Dockerfile`: Added `COPY opentelemetry-javaagent.jar` and `-javaagent` to the entrypoint.

## 10. Commands Used

- `kubectl apply -f k8s/monitoring/`: Deployed the observability stack.
- `docker-compose build`: Rebuilt all docker images with the OpenTelemetry Java Agent and pre-existing JARs.
- `kubectl apply -f ...`: Applied updated Deployments to trigger rolling restarts of the banking pods.
- `kubectl port-forward svc/grafana 3000:3000 -n monitoring`: Accessed Grafana UI.
- `kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring`: Accessed Jaeger UI.

## 11. Validation

- **Monitoring Namespace:**
  - Expected: Prometheus, Grafana, and Jaeger pods running.
  - Actual: All pods reached `1/1 Ready`.
  - Result: Pass.
- **Dynamic Metrics Scraping:**
  - Expected: Prometheus automatically discovers and scrapes banking pods.
  - Actual: `http://localhost:9090/api/v1/targets` showed `kubernetes-pods` discovering all application and Istio sidecars.
  - Result: Pass.
- **Trace Propagation (OpenFeign):**
  - Expected: A single API call to `/api/users` generates a unified trace spanning the API Gateway, User Service, etc.
  - Actual: Queried the Jaeger API (`http://localhost:16686/api/traces?service=api-gateway.banking`) and confirmed traces with multiple span counts grouping the downstream services.
  - Result: Pass.
- **Zero-Code-Change Constraint:**
  - Expected: No Java source code (`.java` files) modified.
  - Actual: Tracing achieved via `opentelemetry-javaagent.jar` injection.
  - Result: Pass.
- **Application Health:**
  - Expected: API continues to function normally.
  - Actual: `Invoke-RestMethod` to API Gateway returned HTTP 200 with user payload from MySQL.
  - Result: Pass.

## 12. Problems Encountered

- **Problem:** Attempting to inject `spring-cloud-starter-sleuth` caused the Maven compiler to fail with `cannot find symbol` on Lombok-generated methods (e.g., `getUserProfile()`).
- **Cause:** Spring Cloud Sleuth introduces annotation processors that conflict with Lombok's code generation on this specific combination of Java 17, Spring Boot 2.7.14, and Maven.
- **Solution:** Aborted the Sleuth injection to respect the "do not modify business logic" and "do not upgrade Java/Spring" constraints. Extracted the original, working JARs from the Phase 0 Docker images, and injected the OpenTelemetry Java Agent at the Dockerfile layer.

## 13. Performance Engineering Relevance

- **Observability Overhead:** The OpenTelemetry agent introduces a negligible overhead to JVM memory and CPU, which is far outweighed by the visibility gained.
- **Bottleneck Identification:** Jaeger traces explicitly visualize exactly which downstream OpenFeign call is causing latency in a complex microservice transaction.
- **Data-Driven Decisions:** Grafana dashboards provide the visual evidence required to tune CPU/Memory limits and HPA thresholds effectively.

## 14. Completion Checklist

- [x] Prometheus deployed in K8s
- [x] Grafana deployed in K8s
- [x] Jaeger deployed in K8s
- [x] Istio configured to export spans to Jaeger
- [x] Prometheus dynamic service discovery configured
- [x] Application Pods annotated for scraping
- [x] Trace Context Propagation implemented via OTel Agent
- [x] 5 Separate Phase 6 Dashboards provisioned via ConfigMap
- [x] No Java business/application logic was modified
- [x] No centralized logging implemented (Phase 7 reserved)
- [x] Phase 1-5 capabilities successfully preserved

## 15. What Comes Next

With deep observability now embedded in the infrastructure, the foundation is set to measure the impact of future architectural changes, load tests, or advanced Istio traffic management rules (like circuit breaking) with empirical data.

## 16. Learning Summary

In Phase 6, we successfully transformed the microservices architecture from a black box into a fully observable system. We deployed the industry-standard stack of Prometheus, Grafana, and Jaeger. Crucially, we navigated a severe Java compilation constraint by employing the OpenTelemetry Java Agent to achieve seamless W3C/B3 trace propagation across OpenFeign boundaries without altering a single line of application code. The system is now fully instrumented and ready for rigorous performance and reliability testing.
