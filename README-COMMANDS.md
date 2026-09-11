# 🚀 Spring Boot Microservices Banking Application
## Kubernetes, Monitoring, Istio & K6 Command Reference

> **This document contains verified operational commands discovered directly from the repository.**
> All namespaces, service names, deployment names, ports, and K6 script paths are sourced from
> the actual Kubernetes manifests, Docker Compose files, Istio resources, and K6 scripts in this repository.
> No commands were invented or assumed.

---

## 📖 Table of Contents

1. [Project Environment Overview](#1--project-environment-overview)
2. [🎯 Project-Specific Quick Commands](#-project-specific-quick-commands)
3. [📦 Resource Inventory](#-resource-inventory)
4. [☸️ Kubernetes Cluster Commands](#2-️-kubernetes-cluster-commands)
5. [📦 Application Deployment Commands](#3--application-deployment-commands)
6. [🔍 Pod Debugging Commands](#4--pod-debugging-commands)
7. [⚠️ Kubernetes Warning & Error Detection](#5-️-kubernetes-warning--error-detection)
8. [🔌 Service & Networking Commands](#6--service--networking-commands)
9. [🔄 Port Forwarding Commands](#7--port-forwarding-commands)
10. [🕸️ Istio Commands](#8-️-istio-commands)
11. [📊 Prometheus Commands](#9--prometheus-commands)
12. [📈 Grafana Commands](#10--grafana-commands)
13. [📜 Loki / Fluent Bit Logging Commands](#11--loki--fluent-bit-logging-commands)
14. [🔎 Kiali Commands](#12--kiali-commands)
15. [🔭 Jaeger / Distributed Tracing Commands](#13--jaeger--distributed-tracing-commands)
16. [🧪 K6 Performance Testing](#14--k6-performance-testing)
17. [🚦 K6 + Kubernetes End-to-End Workflow](#15--k6--kubernetes-end-to-end-testing-workflow)
18. [🔥 Real-Time Troubleshooting](#16--real-time-troubleshooting-commands)
19. [🧹 Cleanup Commands](#17--cleanup-commands)
20. [🔐 ConfigMap & Secret Commands](#18--configuration-configmap--secret-commands)
21. [⚡ Useful One-Liners](#19--useful-one-liners)
22. [🗺️ Daily Development Workflow](#20-️-daily-development-workflow)
23. [🧭 Quick Access Cheat Sheet](#21--quick-access-cheat-sheet)

---

## 1. 📋 Project Environment Overview

| Component | Technology | Namespace | Access Method |
|-----------|-----------|-----------|---------------|
| Kubernetes Cluster | Docker Desktop Kubernetes | — | `kubectl` |
| Service Registry (Eureka) | Spring Cloud Eureka | `banking` | NodePort `30761` → `http://localhost:30761` |
| API Gateway | Spring Cloud Gateway | `banking` | NodePort `30080` → `http://localhost:30080` |
| User Service | Spring Boot | `banking` | ClusterIP `:8082` (via Gateway) |
| Account Service (v1 + v2) | Spring Boot | `banking` | ClusterIP `:8081` (via Gateway) |
| Transaction Service | Spring Boot | `banking` | ClusterIP `:8084` (via Gateway) |
| Fund Transfer | Spring Boot | `banking` | ClusterIP `:8085` (via Gateway) |
| Sequence Generator | Spring Boot | `banking` | ClusterIP `:8083` (via Gateway) |
| Istio Service Mesh | Istio 1.23.0 | `istio-system` | `istioctl`, port-forward |
| Istio Ingress Gateway | Istio IngressGateway (NodePort) | `istio-system` | port-forward `:8088` |
| Prometheus | prom/prometheus:v2.45.0 | `monitoring` | port-forward `:9090` |
| Grafana | grafana/grafana:10.1.1 | `monitoring` | port-forward `:3000` |
| Loki | grafana/loki:2.9.2 | `monitoring` | ClusterIP `:3100` (via Grafana) |
| Fluent Bit (log agent) | fluent-bit:2.2.0 | `monitoring` | DaemonSet |
| Jaeger (all-in-one) | jaegertracing/all-in-one:1.47 | `monitoring` | port-forward `:16686` |
| Kiali | quay.io/kiali/kiali:v1.87 | `istio-system` | port-forward `:20001` |
| kube-state-metrics | kube-state-metrics:v2.9.2 | `monitoring` | ClusterIP `:8080` |
| MySQL (external) | MySQL on Windows host | host | `host.docker.internal:3306` |
| Keycloak (external) | Keycloak on Windows host | host | `host.docker.internal:8571` |
| K6 | k6 CLI | — | Local terminal |

---

## 🎯 Project-Specific Quick Commands

```text
Application Namespace:    banking
Monitoring Namespace:     monitoring
Istio Namespace:          istio-system

API Gateway Deployment:   api-gateway
API Gateway Service:      api-gateway  (NodePort 30080)
Direct API URL:           http://localhost:30080

Service Registry:         service-registry  (NodePort 30761)
Eureka Dashboard:         http://localhost:30761

User Service:             user-service        (port 8082, ClusterIP)
Account Service v1:       account-service     (port 8081, label version=v1)
Account Service v2:       account-service-v2  (port 8081, label version=v2)
Transaction Service:      transaction-service (port 8084, ClusterIP)
Fund Transfer:            fund-transfer       (port 8085, ClusterIP)
Sequence Generator:       sequence-generator  (port 8083, ClusterIP)

Prometheus:               prometheus       (monitoring, port 9090)
Grafana:                  grafana          (monitoring, port 3000)
Loki:                     loki             (monitoring, port 3100)
Jaeger UI:                jaeger-query     (monitoring, port 16686)
Jaeger Collector:         jaeger-collector (monitoring, port 9411 zipkin)
Kiali:                    kiali            (istio-system, port 20001)

ConfigMap:                banking-config   (banking)
Secret:                   banking-secret   (banking)
HPA:                      user-service-hpa (banking, 1-2 replicas, 70% CPU)

K6 Scripts Root:          ./performance/scripts/
K6 Config File:           ./performance/config/test-config.example.js
Default K6 BASE_URL:      http://localhost:8088  (via Istio Ingress port-forward)
```

---

## 📦 Resource Inventory

| Resource Type | Name | Namespace | Purpose |
|---|---|---|---|
| Namespace | `banking` | — | All banking microservices |
| Namespace | `monitoring` | — | Prometheus, Grafana, Loki, Jaeger, Fluent Bit, kube-state-metrics |
| Namespace | `istio-system` | — | Istio control plane, Kiali |
| Deployment | `api-gateway` | `banking` | Spring Cloud API Gateway (port 8080) |
| Deployment | `service-registry` | `banking` | Eureka Service Registry (port 8761) |
| Deployment | `user-service` | `banking` | User management (port 8082) |
| Deployment | `account-service` | `banking` | Account management v1 (port 8081) |
| Deployment | `account-service-v2` | `banking` | Account management v2 canary (port 8081) |
| Deployment | `transaction-service` | `banking` | Transaction management (port 8084) |
| Deployment | `fund-transfer` | `banking` | Fund transfer (port 8085) |
| Deployment | `sequence-generator` | `banking` | Sequence/reference number generator (port 8083) |
| Deployment | `prometheus` | `monitoring` | Metrics collection (v2.45.0) |
| Deployment | `grafana` | `monitoring` | Dashboards — Prometheus, Loki, Jaeger (v10.1.1) |
| Deployment | `loki` | `monitoring` | Log aggregation (v2.9.2) |
| Deployment | `jaeger` | `monitoring` | Distributed tracing all-in-one (v1.47) |
| Deployment | `kube-state-metrics` | `monitoring` | Kubernetes metrics exporter |
| Deployment | `kiali` | `istio-system` | Istio service graph UI (v1.87) |
| DaemonSet | `fluent-bit` | `monitoring` | Log collection agent (v2.2.0) |
| Service | `api-gateway` | `banking` | NodePort 30080 → 8080 |
| Service | `service-registry` | `banking` | NodePort 30761 → 8761 |
| Service | `user-service` | `banking` | ClusterIP 8082 |
| Service | `account-service` | `banking` | ClusterIP 8081 |
| Service | `transaction-service` | `banking` | ClusterIP 8084 |
| Service | `fund-transfer` | `banking` | ClusterIP 8085 |
| Service | `sequence-generator` | `banking` | ClusterIP 8083 |
| Service | `prometheus` | `monitoring` | ClusterIP 9090 |
| Service | `grafana` | `monitoring` | ClusterIP 3000 |
| Service | `loki` | `monitoring` | ClusterIP 3100 |
| Service | `jaeger-query` | `monitoring` | ClusterIP 16686 (Jaeger UI) |
| Service | `jaeger-collector` | `monitoring` | ClusterIP 9411 (Zipkin endpoint) |
| Service | `kube-state-metrics` | `monitoring` | ClusterIP 8080 |
| Service | `kiali` | `istio-system` | ClusterIP 20001 |
| ConfigMap | `banking-config` | `banking` | Eureka URL, MySQL host, Keycloak URL |
| ConfigMap | `prometheus-config` | `monitoring` | Prometheus scrape jobs |
| ConfigMap | `loki-config` | `monitoring` | Loki server configuration |
| ConfigMap | `fluent-bit-config` | `monitoring` | Fluent Bit log pipeline |
| ConfigMap | `kiali` | `istio-system` | Kiali server configuration |
| ConfigMap | `istio` | `istio-system` | Istio mesh config (Jaeger extension provider) |
| Secret | `banking-secret` | `banking` | MySQL credentials, Keycloak client secrets |
| HPA | `user-service-hpa` | `banking` | CPU autoscaler — 1 to 2 replicas at 70% CPU |
| Gateway | `banking-gateway` | `banking` | Istio ingress gateway — all HTTP traffic |
| VirtualService | `api-gateway-route` | `banking` | Ingress → api-gateway:8080, timeout 15s |
| VirtualService | `user-service-route` | `banking` | Timeout 5s, 2 retries on connect-failure/503 |
| VirtualService | `account-service-route` | `banking` | Canary: 50% v1 / 50% v2 weight split |
| VirtualService | `fund-transfer-route` | `banking` | GET timeout 5s, other timeout 10s |
| VirtualService | `transaction-service-route` | `banking` | GET timeout 5s, other timeout 10s |
| VirtualService | `sequence-generator-route` | `banking` | Timeout 3s |
| DestinationRule | `api-gateway-destination` | `banking` | mTLS ISTIO_MUTUAL, outlier detection |
| DestinationRule | `user-service-destination` | `banking` | mTLS ISTIO_MUTUAL, ROUND_ROBIN, outlier |
| DestinationRule | `account-service-destination` | `banking` | mTLS ISTIO_MUTUAL, subsets v1/v2, outlier |
| DestinationRule | `fund-transfer-destination` | `banking` | mTLS ISTIO_MUTUAL, outlier detection |
| DestinationRule | `transaction-service-destination` | `banking` | mTLS ISTIO_MUTUAL, outlier detection |
| DestinationRule | `sequence-generator-destination` | `banking` | mTLS ISTIO_MUTUAL, outlier detection |
| PeerAuthentication | `default` | `banking` | mTLS STRICT for all banking namespace pods |
| Telemetry | `mesh-default` | `istio-system` | 100% trace sampling via Jaeger provider |

---

## 2. ☸️ Kubernetes Cluster Commands

### Cluster Information

```powershell
# Get cluster endpoint and core service URLs
kubectl cluster-info

# List all nodes in the cluster
kubectl get nodes

# List all nodes with extra details (IP, OS, container runtime)
kubectl get nodes -o wide

# Show client and server Kubernetes version
kubectl version

# List all namespaces
kubectl get namespaces
```

**Expected `kubectl get namespaces` output:**
```text
NAME              STATUS   AGE
banking           Active   ...
monitoring        Active   ...
istio-system      Active   ...
default           Active   ...
kube-system       Active   ...
```

### Context Commands

```powershell
# Show current context
kubectl config current-context

# List all available contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>
```

### Namespace Resource Overview

```powershell
# All resources in banking namespace (pods, services, deployments, etc.)
kubectl get all -n banking

# All resources in monitoring namespace
kubectl get all -n monitoring

# All resources in istio-system namespace
kubectl get all -n istio-system
```

---

## 3. 📦 Application Deployment Commands

### Apply All Kubernetes Resources (Correct Order)

Apply in this specific order — later resources depend on earlier ones:

```powershell
# Step 1 — Create namespaces
kubectl apply -f k8s/namespace.yaml

# Step 2 — Apply ConfigMap and Secret BEFORE any pods
kubectl apply -f k8s/banking-configmap.yaml
kubectl apply -f k8s/banking-secret.yaml

# Step 3 — Deploy Service Registry (Eureka) first — all services depend on it
kubectl apply -f k8s/eureka/deployment.yaml
kubectl apply -f k8s/eureka/service.yaml

# Step 4 — Deploy API Gateway
kubectl apply -f k8s/api-gateway/deployment.yaml
kubectl apply -f k8s/api-gateway/service.yaml

# Step 5 — Deploy all microservices
kubectl apply -f k8s/user-service/deployment.yaml
kubectl apply -f k8s/user-service/service.yaml
kubectl apply -f k8s/user-service/hpa.yaml

kubectl apply -f k8s/account-service/deployment.yaml
kubectl apply -f k8s/account-service/service.yaml

kubectl apply -f k8s/transaction-service/deployment.yaml
kubectl apply -f k8s/transaction-service/service.yaml

kubectl apply -f k8s/fund-transfer/deployment.yaml
kubectl apply -f k8s/fund-transfer/service.yaml

kubectl apply -f k8s/sequence-generator/deployment.yaml
kubectl apply -f k8s/sequence-generator/service.yaml

# Step 6 — Apply Istio resources (after services exist)
kubectl apply -f k8s/istio-ingress.yaml
kubectl apply -f k8s/istio-mtls.yaml
kubectl apply -f k8s/istio-traffic-management.yaml
kubectl apply -f k8s/istio-phase5-comprehensive.yaml

# Step 7 — Deploy monitoring stack
kubectl apply -f k8s/monitoring/kube-state-metrics.yaml
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/grafana.yaml
kubectl apply -f k8s/monitoring/loki.yaml
kubectl apply -f k8s/monitoring/fluent-bit.yaml
kubectl apply -f k8s/monitoring/jaeger.yaml
kubectl apply -f k8s/monitoring/kiali.yaml
kubectl apply -f k8s/monitoring/istio-telemetry.yaml
kubectl apply -f k8s/monitoring/istio-cm.yaml
```

### Apply Canary Deployment (Account Service v2)

```powershell
# Deploy account-service v2 alongside v1 for canary traffic split
kubectl apply -f k8s/account-service/deployment-v2.yaml

# The istio-phase5-comprehensive.yaml already defines 50/50 canary split
kubectl apply -f k8s/istio-phase5-comprehensive.yaml
```

### Restart Deployments

```powershell
# Restart individual deployments
kubectl rollout restart deployment/api-gateway -n banking
kubectl rollout restart deployment/service-registry -n banking
kubectl rollout restart deployment/user-service -n banking
kubectl rollout restart deployment/account-service -n banking
kubectl rollout restart deployment/account-service-v2 -n banking
kubectl rollout restart deployment/transaction-service -n banking
kubectl rollout restart deployment/fund-transfer -n banking
kubectl rollout restart deployment/sequence-generator -n banking

# Restart ALL deployments in banking namespace at once
kubectl rollout restart deployment -n banking

# Restart monitoring deployments
kubectl rollout restart deployment/prometheus -n monitoring
kubectl rollout restart deployment/grafana -n monitoring
kubectl rollout restart deployment/loki -n monitoring
```

### Rollout Status

```powershell
kubectl rollout status deployment/api-gateway -n banking
kubectl rollout status deployment/service-registry -n banking
kubectl rollout status deployment/user-service -n banking
kubectl rollout status deployment/account-service -n banking
kubectl rollout status deployment/account-service-v2 -n banking
kubectl rollout status deployment/transaction-service -n banking
kubectl rollout status deployment/fund-transfer -n banking
kubectl rollout status deployment/sequence-generator -n banking
```

### Rollback Deployments

```powershell
kubectl rollout undo deployment/api-gateway -n banking
kubectl rollout undo deployment/user-service -n banking
kubectl rollout undo deployment/account-service -n banking
kubectl rollout undo deployment/account-service-v2 -n banking
kubectl rollout undo deployment/transaction-service -n banking
kubectl rollout undo deployment/fund-transfer -n banking
kubectl rollout undo deployment/sequence-generator -n banking
```

### Scale Deployments

```powershell
# Scale up user-service to 2 replicas (HPA max is 2)
kubectl scale deployment/user-service -n banking --replicas=2

# Pause a service without deleting it
kubectl scale deployment/fund-transfer -n banking --replicas=0

# Restore
kubectl scale deployment/fund-transfer -n banking --replicas=1
```

---

## 4. 🔍 Pod Debugging Commands

### Get Pods

```powershell
# Banking application pods
kubectl get pods -n banking

# Monitoring stack pods
kubectl get pods -n monitoring

# Istio control plane, ingress gateway, Kiali
kubectl get pods -n istio-system
```

**Expected `kubectl get pods -n banking` output:**
```text
NAME                                  READY   STATUS    RESTARTS   AGE
api-gateway-xxxx-xxxx                 2/2     Running   0          5m
service-registry-xxxx-xxxx            2/2     Running   0          5m
user-service-xxxx-xxxx                2/2     Running   0          5m
account-service-xxxx-xxxx             2/2     Running   0          5m
account-service-v2-xxxx-xxxx          2/2     Running   0          5m
transaction-service-xxxx-xxxx         2/2     Running   0          5m
fund-transfer-xxxx-xxxx               2/2     Running   0          5m
sequence-generator-xxxx-xxxx          2/2     Running   0          5m
```
> `READY 2/2` = application container + Istio `istio-proxy` sidecar.

### Watch Pods Live

```powershell
kubectl get pods -n banking -w
kubectl get pods -n monitoring -w
```

### Describe Pods

```powershell
# Replace <pod-name> with the actual pod name from kubectl get pods
kubectl describe pod <pod-name> -n banking
kubectl describe pod <pod-name> -n monitoring
kubectl describe pod <pod-name> -n istio-system
```

### Pod Logs Using Deployment Selectors

```powershell
# Stream logs using deployment name (no need to know exact pod name)
kubectl logs deployment/api-gateway -n banking
kubectl logs deployment/service-registry -n banking
kubectl logs deployment/user-service -n banking
kubectl logs deployment/account-service -n banking
kubectl logs deployment/account-service-v2 -n banking
kubectl logs deployment/transaction-service -n banking
kubectl logs deployment/fund-transfer -n banking
kubectl logs deployment/sequence-generator -n banking

# Follow logs in real-time (Ctrl+C to stop)
kubectl logs -f deployment/api-gateway -n banking
kubectl logs -f deployment/user-service -n banking

# Previous crashed container instance
kubectl logs <pod-name> -n banking --previous
```

### Multi-Container Pod Logs (App + Istio Proxy)

All banking pods have TWO containers: the application and `istio-proxy`. Specify with `-c`:

```powershell
# Application container logs
kubectl logs <pod-name> -c api-gateway -n banking
kubectl logs <pod-name> -c user-service -n banking
kubectl logs <pod-name> -c account-service -n banking
kubectl logs <pod-name> -c transaction-service -n banking
kubectl logs <pod-name> -c fund-transfer -n banking
kubectl logs <pod-name> -c sequence-generator -n banking
kubectl logs <pod-name> -c service-registry -n banking

# Istio proxy sidecar logs (mTLS, traffic routing debug)
kubectl logs <pod-name> -c istio-proxy -n banking

# Follow both in separate terminals
kubectl logs -f <pod-name> -c api-gateway -n banking
kubectl logs -f <pod-name> -c istio-proxy -n banking
```

### Execute Into a Running Pod

```powershell
# Shell into the application container
kubectl exec -it <pod-name> -c api-gateway -n banking -- /bin/sh

# Shell into Istio proxy sidecar
kubectl exec -it <pod-name> -c istio-proxy -n banking -- /bin/sh
```

---

## 5. ⚠️ Kubernetes Warning & Error Detection

### Failed Pods

```powershell
kubectl get pods -A --field-selector=status.phase=Failed
```

### All Pods — Find Non-Running

```powershell
# Show all pods across all namespaces
kubectl get pods -A

# PowerShell: filter out healthy pods to find problems
kubectl get pods -A | Select-String -NotMatch "Running|Completed|NAME"

# Bash/WSL alternative:
# kubectl get pods -A | grep -v "Running\|Completed\|NAME"
```

### Warning Events

```powershell
# All Warning events across the cluster
kubectl get events -A --field-selector type=Warning

# Sorted by most recent timestamp
kubectl get events -A --sort-by='.lastTimestamp'

# Warning events in banking namespace specifically
kubectl get events -n banking --field-selector type=Warning
kubectl get events -n banking --sort-by='.lastTimestamp'

# Warning events in monitoring namespace
kubectl get events -n monitoring --sort-by='.lastTimestamp'

# Warning events in istio-system namespace
kubectl get events -n istio-system --sort-by='.lastTimestamp'
```

### Detecting Specific Error Conditions

```powershell
# CrashLoopBackOff pods
kubectl get pods -A | Select-String "CrashLoopBackOff"
# Bash: kubectl get pods -A | grep CrashLoopBackOff

# ImagePullBackOff pods
kubectl get pods -A | Select-String "ImagePullBackOff"

# Pending pods (scheduling issues)
kubectl get pods -A --field-selector=status.phase=Pending

# OOMKilled — check lastState reason
kubectl get pods -n banking -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.containerStatuses[*]}{.lastState.terminated.reason}{"\n"}{end}{end}'

# Check readiness probe failures
kubectl describe pod <pod-name> -n banking | Select-String "Readiness"

# Check liveness probe failures
kubectl describe pod <pod-name> -n banking | Select-String "Liveness"

# Pod restart counts sorted
kubectl get pods -n banking --sort-by='.status.containerStatuses[0].restartCount'
```

---

## 6. 🔌 Service & Networking Commands

### List Services

```powershell
kubectl get svc -n banking
kubectl get svc -n monitoring
kubectl get svc -n istio-system
```

### Describe Services

```powershell
# Banking application services
kubectl describe svc api-gateway -n banking
kubectl describe svc service-registry -n banking
kubectl describe svc user-service -n banking
kubectl describe svc account-service -n banking
kubectl describe svc transaction-service -n banking
kubectl describe svc fund-transfer -n banking
kubectl describe svc sequence-generator -n banking

# Monitoring services
kubectl describe svc prometheus -n monitoring
kubectl describe svc grafana -n monitoring
kubectl describe svc loki -n monitoring
kubectl describe svc jaeger-query -n monitoring
kubectl describe svc jaeger-collector -n monitoring

# Istio / Kiali
kubectl describe svc kiali -n istio-system
kubectl describe svc istio-ingressgateway -n istio-system
```

### Check Endpoints (Confirm Pods are Backing Services)

```powershell
kubectl get endpoints -n banking
kubectl get endpoints -n monitoring
kubectl get endpointslices -n banking
kubectl get endpointslices -n monitoring
```

### Internal Cluster DNS Names

These DNS names are valid for in-cluster communication (Istio VirtualServices, Fluent Bit, Kiali config):

```text
# Banking services
api-gateway.banking.svc.cluster.local:8080
service-registry.banking.svc.cluster.local:8761
user-service.banking.svc.cluster.local:8082
account-service.banking.svc.cluster.local:8081
transaction-service.banking.svc.cluster.local:8084
fund-transfer.banking.svc.cluster.local:8085
sequence-generator.banking.svc.cluster.local:8083

# Monitoring services
prometheus.monitoring.svc.cluster.local:9090
grafana.monitoring.svc.cluster.local:3000
loki.monitoring.svc.cluster.local:3100
jaeger-query.monitoring.svc.cluster.local:16686
jaeger-collector.monitoring.svc.cluster.local:9411
kube-state-metrics.monitoring.svc.cluster.local:8080
```

### Test DNS Resolution from Inside a Pod

```powershell
kubectl exec -it <pod-name> -c <container-name> -n banking -- nslookup prometheus.monitoring.svc.cluster.local
kubectl exec -it <pod-name> -c <container-name> -n banking -- curl http://prometheus.monitoring.svc.cluster.local:9090/-/ready
```

---

## 7. 🔄 Port Forwarding Commands

> **NodePort Services** (no port-forward needed on Docker Desktop):
> - API Gateway: `http://localhost:30080`
> - Service Registry (Eureka): `http://localhost:30761`
>
> **All other tools require kubectl port-forward.**

### Port Forward Summary Table

| Component | Namespace | K8s Resource | Local URL | Command |
|---|---|---|---|---|
| API Gateway | `banking` | `svc/api-gateway` | `http://localhost:30080` | **NodePort — no port-forward** |
| Eureka | `banking` | `svc/service-registry` | `http://localhost:30761` | **NodePort — no port-forward** |
| Istio Ingress | `istio-system` | `svc/istio-ingressgateway` | `http://localhost:8088` | `kubectl port-forward -n istio-system svc/istio-ingressgateway 8088:80` |
| Prometheus | `monitoring` | `svc/prometheus` | `http://localhost:9090` | `kubectl port-forward -n monitoring svc/prometheus 9090:9090` |
| Grafana | `monitoring` | `svc/grafana` | `http://localhost:3000` | `kubectl port-forward -n monitoring svc/grafana 3000:3000` |
| Loki | `monitoring` | `svc/loki` | `http://localhost:3100` | `kubectl port-forward -n monitoring svc/loki 3100:3100` |
| Jaeger UI | `monitoring` | `svc/jaeger-query` | `http://localhost:16686` | `kubectl port-forward -n monitoring svc/jaeger-query 16686:16686` |
| Kiali | `istio-system` | `svc/kiali` | `http://localhost:20001/kiali` | `kubectl port-forward -n istio-system svc/kiali 20001:20001` |

### Istio Ingress Gateway (K6 Default Target)

K6 scripts default to `BASE_URL=http://localhost:8088`, routed through Istio:

```powershell
# Run in a separate terminal — keep open during K6 tests
kubectl port-forward -n istio-system svc/istio-ingressgateway 8088:80
```

```text
Access: http://localhost:8088
Note: The local overlay (k8s/istio-local-overlay.yaml) configures this as
      NodePort to avoid Windows HTTP.sys conflicts with port 80.
```

### Prometheus

```powershell
# Run in a separate terminal
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

```text
Access: http://localhost:9090
Targets: http://localhost:9090/targets
```

### Grafana

```powershell
# Run in a separate terminal
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

```text
Access:    http://localhost:3000
Username:  admin
Password:  admin
Note: Anonymous access is also enabled (Admin role)
```

### Loki (direct access for debugging)

```powershell
kubectl port-forward -n monitoring svc/loki 3100:3100
```

```text
Health check: http://localhost:3100/ready
```

### Jaeger UI

```powershell
# Run in a separate terminal
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

```text
Access: http://localhost:16686
```

### Kiali

```powershell
# Run in a separate terminal
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

```text
Access: http://localhost:20001/kiali
Auth:   anonymous (configured in kiali ConfigMap)
```

### Direct Microservice Access (Bypass API Gateway, for Debugging)

```powershell
kubectl port-forward -n banking svc/user-service 8082:8082
kubectl port-forward -n banking svc/account-service 8081:8081
kubectl port-forward -n banking svc/transaction-service 8084:8084
kubectl port-forward -n banking svc/fund-transfer 8085:8085
kubectl port-forward -n banking svc/sequence-generator 8083:8083
kubectl port-forward -n banking svc/service-registry 8761:8761
```

### Health Endpoints

```powershell
# API Gateway health (NodePort — always available)
Invoke-WebRequest -Uri "http://localhost:30080/actuator/health" | Select-Object StatusCode, Content

# Via Istio Ingress (requires port-forward above)
Invoke-WebRequest -Uri "http://localhost:8088/actuator/health" | Select-Object StatusCode, Content

# Individual services (after port-forward)
Invoke-WebRequest -Uri "http://localhost:8082/actuator/health"  # user-service
Invoke-WebRequest -Uri "http://localhost:8081/actuator/health"  # account-service
Invoke-WebRequest -Uri "http://localhost:8084/actuator/health"  # transaction-service
Invoke-WebRequest -Uri "http://localhost:8085/actuator/health"  # fund-transfer
Invoke-WebRequest -Uri "http://localhost:8083/actuator/health"  # sequence-generator

# Bash/curl alternative
curl http://localhost:30080/actuator/health
```

---

## 8. 🕸️ Istio Commands

### Check Istio Installation

```powershell
# All Istio system pods (istiod, ingressgateway)
kubectl get pods -n istio-system

# Istio services (including ingressgateway)
kubectl get svc -n istio-system

# Installed Istio version
istioctl version
```

### Check All Istio Resources

```powershell
kubectl get gateway -A
kubectl get virtualservice -A
kubectl get destinationrule -A
kubectl get peerauthentication -A
kubectl get authorizationpolicy -A
kubectl get telemetry -A
```

### Inspect Specific Istio Resources in This Project

```powershell
# --- Gateway ---
kubectl describe gateway banking-gateway -n banking

# --- VirtualServices ---
kubectl describe virtualservice api-gateway-route -n banking
kubectl describe virtualservice user-service-route -n banking
kubectl describe virtualservice account-service-route -n banking
kubectl describe virtualservice fund-transfer-route -n banking
kubectl describe virtualservice transaction-service-route -n banking
kubectl describe virtualservice sequence-generator-route -n banking

# --- DestinationRules ---
kubectl describe destinationrule api-gateway-destination -n banking
kubectl describe destinationrule user-service-destination -n banking
kubectl describe destinationrule account-service-destination -n banking
kubectl describe destinationrule fund-transfer-destination -n banking
kubectl describe destinationrule transaction-service-destination -n banking
kubectl describe destinationrule sequence-generator-destination -n banking

# --- PeerAuthentication (mTLS STRICT) ---
kubectl describe peerauthentication default -n banking

# --- Telemetry (100% Jaeger tracing) ---
kubectl describe telemetry mesh-default -n istio-system
```

### Istioctl Diagnostic Commands

```powershell
# Show proxy sync status for all Envoy sidecars
istioctl proxy-status

# Analyze Istio configuration for errors and warnings — all namespaces
istioctl analyze -A

# Analyze only banking namespace
istioctl analyze -n banking

# Full proxy config dump for a pod
istioctl proxy-config all <pod-name> -n banking

# View configured routes in a pod's Envoy
istioctl proxy-config routes <pod-name> -n banking

# View upstream clusters
istioctl proxy-config clusters <pod-name> -n banking

# View listeners
istioctl proxy-config listeners <pod-name> -n banking

# View endpoints Envoy knows about
istioctl proxy-config endpoints <pod-name> -n banking

# Human-readable policy summary for a pod
istioctl experimental describe pod <pod-name> -n banking
```

### Istio Proxy Logs

```powershell
# Istio proxy sidecar logs for any banking pod
kubectl logs <pod-name> -c istio-proxy -n banking
kubectl logs -f <pod-name> -c istio-proxy -n banking

# Istio ingress gateway logs (traffic in/out of cluster)
kubectl logs deployment/istio-ingressgateway -n istio-system
kubectl logs -f deployment/istio-ingressgateway -n istio-system

# Istiod (control plane) logs
kubectl logs deployment/istiod -n istio-system
```

### Sidecar Injection

```powershell
# Check if injection is enabled on banking namespace
kubectl get namespace banking --show-labels | Select-String "istio"

# Enable sidecar injection (if not already enabled)
kubectl label namespace banking istio-injection=enabled

# Verify — all banking pods should show READY 2/2
kubectl get pods -n banking
```

### Canary Traffic Management

```powershell
# View current account-service traffic split (50/50 v1/v2 defined in phase5)
kubectl describe virtualservice account-service-route -n banking

# Restore to phase5 comprehensive config (50/50 canary split)
kubectl apply -f k8s/istio-phase5-comprehensive.yaml

# Apply fault injection on user-service (100% 503 abort — for testing)
kubectl apply -f k8s/istio-fault-injection.yaml

# Remove fault injection — restore user-service-route to normal
kubectl apply -f k8s/istio-phase5-comprehensive.yaml

# Apply NodePort overlay for Istio ingress on Docker Desktop
istioctl install -f k8s/istio-local-overlay.yaml
```

### mTLS Verification

```powershell
# View PeerAuthentication — banking uses STRICT mTLS
kubectl describe peerauthentication default -n banking

# Check mTLS status between pods
istioctl authn tls-check <pod-name> -n banking

# Check mTLS injection status
istioctl x check-inject -n banking
```

---

## 9. 📊 Prometheus Commands

### Prometheus Pod and Service Discovery

```powershell
kubectl get pods -n monitoring | Select-String "prometheus"
kubectl get svc -n monitoring | Select-String "prometheus"
kubectl describe deployment prometheus -n monitoring
```

### Prometheus Configuration

```powershell
# View scrape configuration
kubectl describe configmap prometheus-config -n monitoring
kubectl get configmap prometheus-config -n monitoring -o yaml
```

> **Scrape target:** All pods in `banking` namespace with annotation `prometheus.io/scrape: 'true'`.
> All 7 microservices expose metrics at `/actuator/prometheus` and have this annotation.
> Metrics port per service: api-gateway=8080, user-service=8082, account-service=8081,
> transaction-service=8084, fund-transfer=8085, sequence-generator=8083, service-registry=8761.

### Access Prometheus

```powershell
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

```text
UI:      http://localhost:9090
Targets: http://localhost:9090/targets
```

### Verified PromQL Queries for This Project

```promql
# === HTTP Request Rate ===
# Total request rate across all banking services
rate(http_server_requests_seconds_count{kubernetes_namespace="banking"}[5m])

# Per-service request rate
rate(http_server_requests_seconds_count{job="api-gateway"}[5m])
rate(http_server_requests_seconds_count{job="user-service"}[5m])
rate(http_server_requests_seconds_count{job="account-service"}[5m])
rate(http_server_requests_seconds_count{job="transaction-service"}[5m])
rate(http_server_requests_seconds_count{job="fund-transfer"}[5m])

# === Error Rate ===
# HTTP 5xx error rate
rate(http_server_requests_seconds_count{kubernetes_namespace="banking",status=~"5.."}[5m])

# HTTP 4xx + 5xx combined error rate
rate(http_server_requests_seconds_count{kubernetes_namespace="banking",status=~"[45].."}[5m])

# === Latency — P95 ===
# Requires histogram (MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
# is set in ALL deployment manifests)
histogram_quantile(0.95, sum(rate(http_server_requests_seconds_bucket{kubernetes_namespace="banking"}[5m])) by (le, job))

# === JVM Memory ===
jvm_memory_used_bytes{area="heap", kubernetes_namespace="banking"}
jvm_memory_committed_bytes{area="heap", kubernetes_namespace="banking"}

# === JVM CPU ===
process_cpu_usage{kubernetes_namespace="banking"}

# === Kubernetes (kube-state-metrics) ===
kube_pod_container_status_restarts_total{namespace="banking"}
kube_pod_status_ready{namespace="banking"}
kube_deployment_spec_replicas{namespace="banking"}
kube_deployment_status_replicas_ready{namespace="banking"}
kube_horizontalpodautoscaler_status_current_replicas{namespace="banking"}
```

---

## 10. 📈 Grafana Commands

### Grafana Pod and Service Discovery

```powershell
kubectl get pods -n monitoring | Select-String "grafana"
kubectl get svc -n monitoring | Select-String "grafana"
kubectl describe deployment grafana -n monitoring
```

### Access Grafana

```powershell
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

```text
Access:    http://localhost:3000
Username:  admin
Password:  admin
Note: GF_AUTH_ANONYMOUS_ENABLED=true — no login required for viewing
```

### Grafana Dashboard Files (from Repository)

Provisioned from `./grafana/provisioning/dashboards/`:

| Dashboard File | Purpose |
|---|---|
| `banking-performance.json` | Main banking performance dashboard |
| `phase6-application.json` | Application-level metrics |
| `phase6-hpa.json` | HPA autoscaling metrics |
| `phase6-istio-envoy.json` | Istio/Envoy proxy metrics |
| `phase6-jvm.json` | JVM heap, GC, threads |
| `phase6-kubernetes.json` | Kubernetes cluster metrics |
| `phase7-logging.json` | Loki log panels |
| `phase9-performance.json` | K6 performance test results |

### Grafana Datasources (Auto-Provisioned)

| Name | Type | In-Cluster URL |
|---|---|---|
| `Prometheus` (default) | Prometheus | `http://prometheus:9090` |
| `Loki` | Loki | `http://loki:3100` |
| `Jaeger` | Jaeger | `http://jaeger-query:16686` |

### Grafana ConfigMaps

```powershell
kubectl describe configmap grafana-datasources -n monitoring
kubectl get configmap grafana-datasources -n monitoring -o yaml
kubectl describe configmap grafana-dashboards -n monitoring
```

### Grafana Logs

```powershell
kubectl logs deployment/grafana -n monitoring
kubectl logs -f deployment/grafana -n monitoring
```

---

## 11. 📜 Loki / Fluent Bit Logging Commands

### Logging Architecture

```text
Banking Pods (namespace: banking)
    ↓  writes stdout/stderr to
/var/log/containers/*_banking_*.log  (on Kubernetes node)
    ↓  tailed by
Fluent Bit DaemonSet (namespace: monitoring)
    ↓  enriched with labels: namespace, app, pod, container
    ↓  shipped to
Loki (monitoring:3100)
    ↓  queried by
Grafana Loki Datasource
```

### Check Loki

```powershell
kubectl get pods -n monitoring | Select-String "loki"
kubectl get svc -n monitoring | Select-String "loki"
kubectl logs deployment/loki -n monitoring
kubectl logs -f deployment/loki -n monitoring
kubectl describe deployment loki -n monitoring
```

### Loki Health Check

```powershell
kubectl port-forward -n monitoring svc/loki 3100:3100

# Then check health
Invoke-WebRequest -Uri "http://localhost:3100/ready" | Select-Object StatusCode
# Bash: curl http://localhost:3100/ready
```

### Check Fluent Bit

```powershell
# DaemonSet status (1 pod per Kubernetes node)
kubectl get daemonset fluent-bit -n monitoring

# Fluent Bit pods
kubectl get pods -n monitoring | Select-String "fluent-bit"

# Fluent Bit logs (shows log shipping to Loki)
kubectl logs <fluent-bit-pod-name> -n monitoring
kubectl logs -f <fluent-bit-pod-name> -n monitoring

# Fluent Bit pipeline configuration
kubectl describe configmap fluent-bit-config -n monitoring
```

### LogQL Queries for This Project

The Fluent Bit output labels are: `job`, `namespace`, `app`, `pod`, `container`

```logql
# All logs from banking namespace
{namespace="banking"}

# Per-service log streams
{namespace="banking", app="api-gateway"}
{namespace="banking", app="user-service"}
{namespace="banking", app="account-service"}
{namespace="banking", app="transaction-service"}
{namespace="banking", app="fund-transfer"}
{namespace="banking", app="sequence-generator"}
{namespace="banking", app="service-registry"}

# Filter ERROR logs across all banking services
{namespace="banking"} |= "ERROR"

# Filter WARN logs
{namespace="banking"} |= "WARN"

# Exceptions and stack traces
{namespace="banking"} |= "Exception"

# Logs for a specific pod (replace name)
{pod="api-gateway-xxxx-xxxx", namespace="banking"}

# Monitoring namespace logs (Loki, Prometheus, Grafana)
{namespace="monitoring"}

# Istio system logs
{namespace="istio-system"}
```

---

## 12. 🔎 Kiali Commands

### Check Kiali

```powershell
kubectl get pods -n istio-system | Select-String "kiali"
kubectl get svc -n istio-system | Select-String "kiali"
kubectl describe deployment kiali -n istio-system
kubectl logs deployment/kiali -n istio-system
kubectl logs -f deployment/kiali -n istio-system
```

### Access Kiali

```powershell
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

```text
Access: http://localhost:20001/kiali
Auth:   anonymous (Admin role configured in ConfigMap)
```

### Kiali Configuration Reference

```text
Version:                  v1.87.0
Prometheus URL:           http://prometheus.monitoring.svc.cluster.local:9090
Grafana in-cluster URL:   http://grafana.monitoring.svc.cluster.local:3000
Jaeger in-cluster URL:    http://jaeger-query.monitoring.svc.cluster.local:16686
Tracing provider:         jaeger
Istio root namespace:     istio-system
Accessible namespaces:    ** (all)
Kiali web root:           /kiali
```

### Kiali ConfigMap

```powershell
kubectl describe configmap kiali -n istio-system
kubectl get configmap kiali -n istio-system -o yaml
```

### Troubleshooting Kiali

```powershell
# Verify Prometheus is reachable from Kiali
kubectl exec -it deployment/kiali -n istio-system -- curl http://prometheus.monitoring.svc.cluster.local:9090/-/ready

# Generate traffic to populate the service graph
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/istio-visualization-test.js

# Check Kiali errors
kubectl logs deployment/kiali -n istio-system | Select-String "error\|Error"
```

---

## 13. 🔭 Jaeger / Distributed Tracing Commands

### Check Jaeger

```powershell
# Jaeger all-in-one pod (collector + query + UI in one pod)
kubectl get pods -n monitoring | Select-String "jaeger"

# Jaeger services (query UI and collector)
kubectl get svc -n monitoring | Select-String "jaeger"

kubectl describe deployment jaeger -n monitoring
kubectl logs deployment/jaeger -n monitoring
kubectl logs -f deployment/jaeger -n monitoring
```

### Access Jaeger UI

```powershell
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

```text
Access: http://localhost:16686
```

### Tracing Architecture

```text
Configuration source:
  k8s/monitoring/istio-cm.yaml  — Istio mesh config, jaeger extension provider
  k8s/monitoring/istio-telemetry.yaml — Telemetry resource, 100% sampling

Trace flow:
  All banking pods → Istio sidecar (generates spans) →
  jaeger-collector.monitoring.svc.cluster.local:9411 (Zipkin protocol) →
  Jaeger storage → Jaeger Query UI

Context propagation (configured in all deployments):
  OTEL_PROPAGATORS=b3multi,tracecontext

Services visible in Jaeger:
  api-gateway, user-service, account-service,
  transaction-service, fund-transfer, sequence-generator
```

### Verify Traces

```text
1. Port-forward Jaeger: kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
2. Open http://localhost:16686
3. Select service from dropdown (e.g., "api-gateway")
4. Click "Find Traces"
5. If empty — generate traffic: k6 run performance/scripts/baseline-test.js
```

### Verify Jaeger Collector Connectivity

```powershell
kubectl get svc jaeger-collector -n monitoring
kubectl describe configmap istio -n istio-system | Select-String "jaeger"
kubectl describe telemetry mesh-default -n istio-system
```

---

## 14. 🧪 K6 Performance Testing

### K6 Scripts Inventory

| Script | Path | Purpose | Profile |
|---|---|---|---|
| `baseline-test.js` | `performance/scripts/baseline-test.js` | Minimal load, optimal conditions | 5 VUs / 30s |
| `load-test.js` | `performance/scripts/load-test.js` | Normal expected load | ramp to 20 VUs / ~2m |
| `stress-test.js` | `performance/scripts/stress-test.js` | Find breaking point (up to 100 VUs) | ramp to 100 VUs / ~3m |
| `spike-test.js` | `performance/scripts/spike-test.js` | Sudden spike, tests autoscaling | 5→100→5 VUs / ~70s |
| `canary-demo-test.js` | `performance/scripts/canary-demo-test.js` | Account-service traffic for Kiali canary demo | 8 VUs / 10m |
| `istio-visualization-test.js` | `performance/scripts/istio-visualization-test.js` | Multi-service traffic to populate Kiali graph | 10 VUs / 5m |
| `debug-test.js` | `performance/scripts/debug-test.js` | Debug specific endpoints with response logging | 1 VU / 1 iteration |
| `safe-workflows.js` | `performance/scripts/scenarios/safe-workflows.js` | Shared library of safe GET-only functions | (library) |

> **Smoke Test:** Not a separate script — use `baseline-test.js`.
> **Soak Test:** Not currently implemented in this repository.

### K6 Configuration Setup

```powershell
# Copy example config to working config
Copy-Item "performance/config/test-config.example.js" "performance/config/test-config.js"

# Edit performance/config/test-config.js and set your values
# Key settings:
#   BASE_URL: http://localhost:8088  (via Istio port-forward — default)
#   or
#   BASE_URL: http://localhost:30080 (via API Gateway NodePort)
```

**Default config values (from `test-config.example.js`):**
```javascript
BASE_URL:                  "http://localhost:8088"
TEST_USER_ID:              "1"
TEST_ACCOUNT_ID:           "0600140000003"
TEST_ACCOUNT_NUMBER:       "0600140000003"
SECONDARY_ACCOUNT_NUMBER:  "0600140000004"
PENDING_ACCOUNT_NUMBER:    "0600140000007"
TEST_REFERENCE_ID:         "40f50462-2db7-4451-b815-126a4e0996cf"
```

### K6 Run Commands

All commands are run from the **project root directory**:

#### Baseline Test

```powershell
# Standard run (uses default BASE_URL from config)
k6 run performance/scripts/baseline-test.js

# Override BASE_URL via environment variable
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/baseline-test.js

# With Keycloak authentication token
k6 run -e BASE_URL=http://localhost:8088 -e K6_TOKEN="ey..." performance/scripts/baseline-test.js
```

**Profile:** 5 VUs / 30s | **Thresholds:** P95 < 1000ms, errors < 5%

#### Load Test (Normal Expected Load)

```powershell
k6 run performance/scripts/load-test.js
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/load-test.js
```

**Profile:** Ramp 0→20 VUs (30s), sustain 20 VUs (1m), ramp down (30s)
**Thresholds:** P95 < 2000ms, errors < 5%

#### Stress Test (Find Breaking Point)

```powershell
k6 run performance/scripts/stress-test.js
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/stress-test.js
```

**Profile:** Ramp 0→20→50→100 VUs, sustain 100 VUs (1m), ramp down
**Thresholds:** P95 < 3000ms, errors < 10%
**Note:** Capped at 100 VUs to avoid crashing Docker Desktop.

#### Spike Test (Autoscaling and Circuit Breaker)

```powershell
k6 run performance/scripts/spike-test.js
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/spike-test.js
```

**Profile:** 5 VUs (10s) → spike to 100 VUs (10s+20s sustain) → drop to 5 VUs (10s+20s recovery)
**Thresholds:** P95 < 3000ms
**Observation:** Watch HPA scale user-service-hpa and Kiali circuit breaker in real time.

#### Canary Demo Test (Kiali Traffic Split Observation)

```powershell
k6 run performance/scripts/canary-demo-test.js
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/canary-demo-test.js
```

**Profile:** 8 VUs / 10 minutes | **Targets:** Only account-service GET endpoints
**Use:** Run while watching Kiali service graph to observe v1/v2 50%/50% traffic split.

#### Istio Visualization Test (Populate Kiali Service Graph)

```powershell
k6 run performance/scripts/istio-visualization-test.js
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/istio-visualization-test.js
```

**Profile:** 10 VUs / 5 minutes | **Targets:** All services (user, account, transaction, fund-transfer)
**Use:** Run while watching Kiali Graph view to see all service connections.

#### Debug Test (Response Inspection)

```powershell
k6 run performance/scripts/debug-test.js -e BASE_URL=http://localhost:8088
```

**Profile:** 1 VU, 1 iteration | Logs full response status and body for transaction/account endpoints.

### K6 Output Options

```powershell
# Save JSON summary report
k6 run performance/scripts/load-test.js --summary-export=performance/results/load-summary.json

# Verbose output
k6 run performance/scripts/load-test.js -v

# Specify log output
k6 run performance/scripts/load-test.js --log-output stdout --verbose
```

### API Endpoints Targeted by K6

| Endpoint | Service | K6 Function |
|---|---|---|
| `GET /api/users` | user-service | `getUser()` |
| `GET /api/users/{id}` | user-service | `getUserById()` |
| `GET /accounts?accountNumber=0600140000003` | account-service | `getAccount()` |
| `GET /accounts?accountNumber=0600140000004` | account-service | `getSecondaryAccount()` |
| `GET /accounts?accountNumber=0600140000007` | account-service | `getPendingAccount()` |
| `GET /accounts/balance?accountNumber=0600140000003` | account-service | `getAccountBalance()` |
| `GET /accounts/0600140000003/transactions` | account-service | `getAccountTransactions()` |
| `GET /transactions?accountId=0600140000003` | transaction-service | `getTransactions()` |
| `GET /transactions/{referenceId}` | transaction-service | `getTransactionByRef()` |
| `GET /fund-transfers?accountId=0600140000003` | fund-transfer | `getFundTransfers()` |
| `GET /fund-transfers/{referenceId}` | fund-transfer | `getFundTransferByRef()` |

---

## 15. 🚦 K6 + Kubernetes End-to-End Testing Workflow

### Step 1 — Verify Cluster

```powershell
kubectl get nodes
# Expected: STATUS=Ready
```

### Step 2 — Verify Banking Application

```powershell
kubectl get pods -n banking
# Expected: All 8 pods Running, READY=2/2
```

### Step 3 — Verify Monitoring Stack

```powershell
kubectl get pods -n monitoring
# Expected: prometheus, grafana, loki, jaeger, kube-state-metrics, fluent-bit Running
```

### Step 4 — Verify Istio

```powershell
kubectl get pods -n istio-system
# Expected: istiod, istio-ingressgateway, kiali Running
```

### Step 5 — Open Port-Forward Terminals

Open 4 separate PowerShell terminals, one command each:

```powershell
# Terminal 1 — Istio Ingress (K6 default target)
kubectl port-forward -n istio-system svc/istio-ingressgateway 8088:80

# Terminal 2 — Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Terminal 3 — Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Terminal 4 — Kiali
kubectl port-forward -n istio-system svc/kiali 20001:20001

# Optional Terminal 5 — Jaeger
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

### Step 6 — Health Check

```powershell
# Via NodePort (always works without port-forward)
Invoke-WebRequest -Uri "http://localhost:30080/actuator/health"

# Via Istio Ingress (requires Terminal 1 above)
Invoke-WebRequest -Uri "http://localhost:8088/actuator/health"
```

### Step 7 — Open Monitoring Dashboards

```text
Grafana:     http://localhost:3000     (admin/admin)
Prometheus:  http://localhost:9090
Kiali:       http://localhost:20001/kiali
Jaeger:      http://localhost:16686
Eureka:      http://localhost:30761    (NodePort — no port-forward)
```

### Step 8 — Run K6 Tests

```powershell
# First, run baseline to confirm setup is working
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/baseline-test.js

# Then run the Istio visualization test to populate Kiali graph
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/istio-visualization-test.js

# Then run the load test
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/load-test.js
```

### Step 9 — Monitor During Test

```powershell
# Watch pods for scaling / crashes (separate terminal)
kubectl get pods -n banking -w

# Resource usage (requires metrics-server)
kubectl top pods -n banking

# Follow API gateway logs
kubectl logs -f deployment/api-gateway -n banking -c api-gateway

# Watch HPA scaling
kubectl get hpa -n banking -w
```

**Browser monitoring during test:**
- **Grafana** → `banking-performance` dashboard — request rate, P95, JVM
- **Kiali** → Graph view — service mesh traffic visualization
- **Jaeger** → Find Traces — distributed trace inspection
- **Prometheus** → Targets — confirm all services are UP

### Step 10 — Cleanup After Testing

```powershell
# Stop K6 (Ctrl+C in K6 terminal)
# Stop all port-forward processes (Ctrl+C in each port-forward terminal)
```

---

## 16. 🔥 Real-Time Troubleshooting Commands

### 🔴 Application Not Starting

```powershell
# 1. Check pod status
kubectl get pods -n banking

# 2. Describe the failing pod — look at Events section at the bottom
kubectl describe pod <pod-name> -n banking

# 3. Application container logs
kubectl logs <pod-name> -c <container-name> -n banking

# 4. Check for startup probe failures (account-service has startup probes)
kubectl describe pod <pod-name> -n banking | Select-String "Startup"

# 5. Check events
kubectl get events -n banking --sort-by='.lastTimestamp'
```

**Common causes for this project:**
- MySQL not reachable at `host.docker.internal:3306` (check Docker Desktop network)
- Eureka not ready yet — `service-registry` must start before other services
- `banking-config` ConfigMap or `banking-secret` Secret missing — apply them first
- OOMKilled — check if limits need increasing

### 🔴 CrashLoopBackOff

```powershell
# 1. Get pod name
kubectl get pods -n banking

# 2. Read current crash logs
kubectl logs <pod-name> -c <container-name> -n banking

# 3. Read PREVIOUS container's logs (critical — these are the crash logs)
kubectl logs <pod-name> -c <container-name> -n banking --previous

# 4. Describe — check restart count and last termination reason
kubectl describe pod <pod-name> -n banking

# 5. Events
kubectl get events -n banking --sort-by='.lastTimestamp'
```

### 🔴 503 Service Unavailable

```powershell
# 1. Verify pod is Running and Ready 2/2
kubectl get pods -n banking

# 2. Check service endpoints — must not be empty
kubectl get endpoints user-service -n banking
kubectl get endpoints account-service -n banking

# 3. Check VirtualService and DestinationRule
kubectl describe virtualservice user-service-route -n banking
kubectl describe destinationrule user-service-destination -n banking

# 4. Check for active fault injection
kubectl get virtualservice user-service-route -n banking -o yaml | Select-String "fault"

# 5. Remove fault injection if present
kubectl apply -f k8s/istio-phase5-comprehensive.yaml

# 6. Istio proxy errors
kubectl logs <pod-name> -c istio-proxy -n banking | Select-String "503"

# 7. Validate Istio config
istioctl analyze -n banking
```

### 🔴 504 Gateway Timeout

```powershell
# 1. API Gateway logs
kubectl logs -f deployment/api-gateway -c api-gateway -n banking

# 2. Check VirtualService timeout (api-gateway-route has 15s timeout)
kubectl describe virtualservice api-gateway-route -n banking

# 3. Test downstream service directly (port-forward and curl)
kubectl port-forward -n banking svc/user-service 8082:8082
Invoke-WebRequest -Uri "http://localhost:8082/actuator/health"

# 4. Check endpoints
kubectl get endpoints -n banking

# 5. Proxy timeout errors
kubectl logs <pod-name> -c istio-proxy -n banking | Select-String "504"

# 6. DestinationRule outlier detection — may be ejecting pods
kubectl describe destinationrule -n banking
```

### 🔴 ImagePullBackOff

```powershell
# 1. Identify failing pod
kubectl get pods -n banking | Select-String "ImagePull"

# 2. Describe for exact error
kubectl describe pod <pod-name> -n banking

# The project uses localhost:5001 local registry
# Verify local registry is running:
docker ps | Select-String "registry"

# Re-push image to local registry:
docker tag banking/api-gateway:latest localhost:5001/banking/api-gateway:latest
docker push localhost:5001/banking/api-gateway:latest
```

### 🔴 No Metrics in Grafana

```powershell
# 1. Check Prometheus is running
kubectl get pods -n monitoring | Select-String "prometheus"

# 2. Port-forward and check targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open: http://localhost:9090/targets
# Look for: kubernetes-pods job with banking targets in UP state

# 3. Verify pod prometheus annotations
kubectl describe pod <pod-name> -n banking | Select-String "prometheus.io"

# 4. Manually test metrics endpoint
kubectl port-forward -n banking svc/user-service 8082:8082
Invoke-WebRequest -Uri "http://localhost:8082/actuator/prometheus" | Select-Object Content

# 5. In Grafana: Configuration -> Data Sources -> Prometheus -> Save & Test

# 6. Check ConfigMap
kubectl describe configmap prometheus-config -n monitoring
```

### 🔴 No Logs in Grafana / Loki

```powershell
# 1. Check Loki is running
kubectl get pods -n monitoring | Select-String "loki"

# 2. Loki health check
kubectl port-forward -n monitoring svc/loki 3100:3100
Invoke-WebRequest -Uri "http://localhost:3100/ready"

# 3. Fluent Bit shipping status
kubectl get pods -n monitoring | Select-String "fluent-bit"
kubectl logs <fluent-bit-pod-name> -n monitoring | Select-String "loki\|error"

# 4. In Grafana: Explore -> Loki datasource -> query: {namespace="banking"}

# 5. Check Fluent Bit config
kubectl describe configmap fluent-bit-config -n monitoring
```

### 🔴 Kiali Not Showing Traffic

```powershell
# 1. Generate traffic
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/istio-visualization-test.js

# 2. Verify Prometheus is scraping banking pods
# http://localhost:9090/targets -- check kubernetes-pods entries show UP

# 3. Check Prometheus URL in Kiali config
kubectl describe configmap kiali -n istio-system | Select-String "prometheus"

# 4. Verify sidecars are injected (READY must be 2/2)
kubectl get pods -n banking

# 5. Check Kiali logs
kubectl logs deployment/kiali -n istio-system | Select-String "error\|Error"
```

### 🔴 Pending Pods

```powershell
# Find pending pods
kubectl get pods -A --field-selector=status.phase=Pending

# Describe for scheduling reason
kubectl describe pod <pod-name> -n <namespace>

# Check node capacity
kubectl describe nodes | Select-String "Allocatable\|Allocated"
kubectl top nodes
```

---

## 17. 🧹 Cleanup Commands

### Delete All Istio Resources

```powershell
kubectl delete -f k8s/istio-phase5-comprehensive.yaml
kubectl delete -f k8s/istio-traffic-management.yaml
kubectl delete -f k8s/istio-mtls.yaml
kubectl delete -f k8s/istio-ingress.yaml
```

### Delete Banking Application

```powershell
kubectl delete -f k8s/api-gateway/
kubectl delete -f k8s/eureka/
kubectl delete -f k8s/user-service/
kubectl delete -f k8s/account-service/
kubectl delete -f k8s/fund-transfer/
kubectl delete -f k8s/transaction-service/
kubectl delete -f k8s/sequence-generator/
kubectl delete -f k8s/banking-configmap.yaml
kubectl delete -f k8s/banking-secret.yaml
```

### Delete Monitoring Stack

```powershell
kubectl delete -f k8s/monitoring/
```

### Delete Entire Namespaces

> ⚠️ **DESTRUCTIVE — Permanently removes ALL resources in the namespace.**

```powershell
# Removes ALL banking resources
kubectl delete namespace banking

# Removes ALL monitoring resources
kubectl delete namespace monitoring
```

### Delete Specific Deployments

```powershell
# Banking
kubectl delete deployment api-gateway -n banking
kubectl delete deployment service-registry -n banking
kubectl delete deployment user-service -n banking
kubectl delete deployment account-service -n banking
kubectl delete deployment account-service-v2 -n banking
kubectl delete deployment transaction-service -n banking
kubectl delete deployment fund-transfer -n banking
kubectl delete deployment sequence-generator -n banking

# Monitoring
kubectl delete deployment prometheus -n monitoring
kubectl delete deployment grafana -n monitoring
kubectl delete deployment loki -n monitoring
kubectl delete deployment jaeger -n monitoring
kubectl delete deployment kube-state-metrics -n monitoring

# Istio-system
kubectl delete deployment kiali -n istio-system
```

### Remove Canary (Account Service v2 Only)

```powershell
# Remove v2 canary deployment only
kubectl delete deployment account-service-v2 -n banking

# Then edit k8s/istio-phase5-comprehensive.yaml:
# Change account-service-route weights to v1=100, v2=0
# Then apply:
kubectl apply -f k8s/istio-phase5-comprehensive.yaml
```

### Restart All Deployments in Banking

```powershell
kubectl rollout restart deployment -n banking
```

### Docker Compose Cleanup

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (clears Prometheus and Grafana data)
docker-compose down -v
```

---

## 18. 🔐 Configuration, ConfigMap & Secret Commands

### ConfigMaps

```powershell
# List all ConfigMaps in each namespace
kubectl get configmap -n banking
kubectl get configmap -n monitoring
kubectl get configmap -n istio-system

# Describe key ConfigMaps
kubectl describe configmap banking-config -n banking
kubectl describe configmap prometheus-config -n monitoring
kubectl describe configmap loki-config -n monitoring
kubectl describe configmap fluent-bit-config -n monitoring
kubectl describe configmap kiali -n istio-system
kubectl describe configmap istio -n istio-system

# Get full YAML
kubectl get configmap banking-config -n banking -o yaml
kubectl get configmap prometheus-config -n monitoring -o yaml
kubectl get configmap fluent-bit-config -n monitoring -o yaml
```

### Secrets

> ⚠️ **Avoid printing secret values in shared or logged terminals.**

```powershell
# List secrets in banking namespace
kubectl get secrets -n banking

# Describe banking-secret — shows KEY names only (values are not printed)
kubectl describe secret banking-secret -n banking
# Keys: mysql-username, mysql-password, keycloak-gateway-secret, keycloak-api-secret

# ⚠️ SENSITIVE — Decode a specific secret value (only in secure environments):
# PowerShell:
$encoded = kubectl get secret banking-secret -n banking -o jsonpath='{.data.mysql-username}'
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($encoded))

# Bash:
# kubectl get secret banking-secret -n banking -o jsonpath='{.data.mysql-username}' | base64 --decode
```

### HPA

```powershell
# View HPA status (user-service: 1-2 replicas, scales at 70% CPU)
kubectl get hpa -n banking
kubectl describe hpa user-service-hpa -n banking

# Watch HPA real-time scaling decisions
kubectl get hpa -n banking -w
```

---

## 19. ⚡ Useful One-Liners

### View All Resources

```powershell
# All pods across all namespaces
kubectl get pods -A

# Watch all pods live
kubectl get pods -A -w

# All services
kubectl get svc -A
```

### Find Specific Components

```powershell
# PowerShell
kubectl get pods -A | Select-String "grafana"
kubectl get pods -A | Select-String "prometheus"
kubectl get pods -A | Select-String "loki"
kubectl get pods -A | Select-String "jaeger"
kubectl get pods -A | Select-String "kiali"
kubectl get pods -A | Select-String "istio"
kubectl get svc -A | Select-String "prometheus"
kubectl get svc -A | Select-String "grafana"

# Bash equivalents
# kubectl get pods -A | grep grafana
# kubectl get pods -A | grep prometheus
```

### Find High-Restart Pods

```powershell
kubectl get pods -n banking --sort-by='.status.containerStatuses[0].restartCount'
```

### Warning Events

```powershell
kubectl get events -A --field-selector type=Warning
kubectl get events -n banking --sort-by='.lastTimestamp'
```

### Pod IPs and Node Info

```powershell
kubectl get pods -A -o wide
kubectl get pods -n banking -o wide
```

### Service Endpoints

```powershell
kubectl get endpoints -A
kubectl get endpoints -n banking
```

### Resource Usage

```powershell
kubectl top nodes
kubectl top pods -n banking
kubectl top pods -n monitoring
```

### Force Delete Stuck Pod

```powershell
# ⚠️ Only when pod is stuck in Terminating state
kubectl delete pod <pod-name> -n banking --force --grace-period=0
```

### Count Running Pods in Banking

```powershell
(kubectl get pods -n banking | Select-String "Running").Count
```

---

## 20. 🗺️ Daily Development Workflow

```text
1.  Start Docker Desktop and enable Kubernetes
2.  kubectl get nodes  →  verify STATUS=Ready
3.  kubectl get namespaces  →  verify banking, monitoring, istio-system exist
4.  kubectl apply -f k8s/banking-configmap.yaml  →  apply if changed
5.  kubectl apply -f k8s/banking-secret.yaml  →  apply if changed
6.  kubectl apply -f k8s/eureka/  →  start service registry first
7.  kubectl rollout status deployment/service-registry -n banking  →  wait for Ready
8.  kubectl apply -f k8s/api-gateway/ k8s/user-service/ k8s/account-service/
    k8s/transaction-service/ k8s/fund-transfer/ k8s/sequence-generator/
9.  kubectl apply -f k8s/istio-ingress.yaml k8s/istio-mtls.yaml k8s/istio-phase5-comprehensive.yaml
10. kubectl apply -f k8s/monitoring/  →  deploy full monitoring stack
11. kubectl get pods -n banking -w  →  wait for all pods to show 2/2 Running
12. kubectl get pods -n monitoring -w  →  wait for monitoring pods to be Running
13. Open 4 port-forward terminals (Istio:8088, Grafana:3000, Prometheus:9090, Kiali:20001)
14. Invoke-WebRequest http://localhost:30080/actuator/health  →  verify API gateway
15. Open http://localhost:3000 (Grafana banking-performance dashboard)
16. Open http://localhost:20001/kiali (service graph)
17. k6 run -e BASE_URL=http://localhost:8088 performance/scripts/baseline-test.js
18. k6 run -e BASE_URL=http://localhost:8088 performance/scripts/load-test.js
19. Monitor Grafana dashboards during K6 test
20. Watch Kiali for service mesh visualization (run istio-visualization-test.js)
21. Check Jaeger at http://localhost:16686 for trace analysis
22. Review Grafana phase7-logging dashboard for application errors
23. Troubleshoot any issues using Section 16
24. kubectl rollout restart deployment -n banking  →  rolling restart if needed
25. Ctrl+C all K6 and port-forward terminals after testing
```

### Full Deployment Sequence (Copy-Paste)

```powershell
# Run from project root — applies everything in correct order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/banking-configmap.yaml
kubectl apply -f k8s/banking-secret.yaml
kubectl apply -f k8s/eureka/
kubectl apply -f k8s/api-gateway/
kubectl apply -f k8s/user-service/
kubectl apply -f k8s/account-service/
kubectl apply -f k8s/transaction-service/
kubectl apply -f k8s/fund-transfer/
kubectl apply -f k8s/sequence-generator/
kubectl apply -f k8s/istio-ingress.yaml
kubectl apply -f k8s/istio-mtls.yaml
kubectl apply -f k8s/istio-phase5-comprehensive.yaml
kubectl apply -f k8s/monitoring/

# Monitor deployment progress
kubectl get pods -n banking -w
```

---

## 21. 🧭 Quick Access Cheat Sheet

### Check Application

```powershell
kubectl get pods -n banking
```

### Watch Pods Live

```powershell
kubectl get pods -n banking -w
```

### Check Monitoring Stack

```powershell
kubectl get pods -n monitoring
```

### Check Istio

```powershell
kubectl get pods -n istio-system
```

### API Gateway (NodePort — always available)

```text
http://localhost:30080
http://localhost:30080/actuator/health
```

### Eureka Dashboard (NodePort — always available)

```text
http://localhost:30761
```

### Istio Ingress Gateway (K6 default entry point)

```powershell
kubectl port-forward -n istio-system svc/istio-ingressgateway 8088:80
# Access: http://localhost:8088
```

### Prometheus

```powershell
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Access: http://localhost:9090
```

### Grafana

```powershell
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Access: http://localhost:3000  (admin / admin)
```

### Kiali

```powershell
kubectl port-forward -n istio-system svc/kiali 20001:20001
# Access: http://localhost:20001/kiali
```

### Jaeger

```powershell
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
# Access: http://localhost:16686
```

### K6 Baseline Test

```powershell
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/baseline-test.js
```

### K6 Load Test

```powershell
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/load-test.js
```

### K6 Stress Test

```powershell
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/stress-test.js
```

### K6 Spike Test

```powershell
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/spike-test.js
```

### K6 Kiali Visualization

```powershell
k6 run -e BASE_URL=http://localhost:8088 performance/scripts/istio-visualization-test.js
```

### Restart All Banking Deployments

```powershell
kubectl rollout restart deployment -n banking
```

### All Events Sorted

```powershell
kubectl get events -A --sort-by='.lastTimestamp'
```

### All Warning Events

```powershell
kubectl get events -A --field-selector type=Warning
```

---

> **Generated by:** Full repository analysis of `Spring-Boot-Microservices-Banking-Application`
> **Date:** 2026-09-01
>
> **Files analyzed and verified:**
> - `k8s/namespace.yaml`, `k8s/banking-configmap.yaml`, `k8s/banking-secret.yaml`
> - `k8s/api-gateway/`, `k8s/eureka/`, `k8s/user-service/`, `k8s/account-service/`
> - `k8s/transaction-service/`, `k8s/fund-transfer/`, `k8s/sequence-generator/`
> - `k8s/istio-ingress.yaml`, `k8s/istio-mtls.yaml`, `k8s/istio-traffic-management.yaml`
> - `k8s/istio-phase5-comprehensive.yaml`, `k8s/istio-fault-injection.yaml`, `k8s/istio-local-overlay.yaml`
> - `k8s/monitoring/prometheus.yaml`, `k8s/monitoring/grafana.yaml`, `k8s/monitoring/loki.yaml`
> - `k8s/monitoring/jaeger.yaml`, `k8s/monitoring/kiali.yaml`, `k8s/monitoring/fluent-bit.yaml`
> - `k8s/monitoring/kube-state-metrics.yaml`, `k8s/monitoring/istio-telemetry.yaml`, `k8s/monitoring/istio-cm.yaml`
> - `grafana/provisioning/datasources/datasource.yml`, `grafana/provisioning/dashboards/` (9 dashboards)
> - `prometheus/prometheus.yml`
> - `performance/scripts/baseline-test.js`, `load-test.js`, `stress-test.js`, `spike-test.js`
> - `performance/scripts/canary-demo-test.js`, `istio-visualization-test.js`, `debug-test.js`
> - `performance/scripts/scenarios/safe-workflows.js`
> - `performance/config/test-config.example.js`
> - `docker-compose.yml`
