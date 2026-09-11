# Phase 3 — Kubernetes Performance & Reliability

---

## 1. Objective

### What we wanted to achieve
In Phase 3, we focused on making our Kubernetes deployments production-ready. We aimed to ensure the stability of the cluster and individual services by adding resource limits and automated health checks to all 7 microservices.

### Why we needed it
- **Predictable Performance:** Without CPU and memory limits, a single misbehaving pod could consume all resources on the node, crashing the whole cluster (noisy neighbor problem).
- **Self-Healing:** Kubernetes doesn't intrinsically know if a Spring Boot app is internally deadlocked or still initializing. We needed to tell it exactly how to verify if the application is healthy and ready to serve traffic.

### How it fits into the project
This completes the authorized Kubernetes work for the application. The system is now structurally migrated (Phase 2) and hardened with basic reliability primitives (Phase 3). 

---

## 2. What We Implemented

For every microservice (`eureka`, `api-gateway`, `user-service`, `account-service`, `sequence-generator`, `transaction-service`, `fund-transfer`), we injected the following configurations into their `deployment.yaml`:

### 2.1 Resource Requests & Limits

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```
- **Requests:** Guarantees each pod gets at least 0.1 CPUs and 256MB of RAM. This is used by the Kubernetes scheduler to find a node with enough capacity.
- **Limits:** Hard caps each pod at 0.5 CPUs and 512MB of RAM. If a pod exceeds 512MB of memory, it will be killed (OOMKilled) to protect the node.

*Note: Combined with the `JAVA_TOOL_OPTIONS` setting (e.g., `-Xms256m -Xmx512m`) configured in Phase 2, the JVM is strictly constrained to match the container's physical limits.*

### 2.2 Readiness Probes

```yaml
readinessProbe:
  httpGet:
    path: /actuator/health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
```
- **Purpose:** Determines if the pod is ready to receive network traffic from Kubernetes Services or the API Gateway.
- **Behavior:** It waits 30 seconds before making the first check. It then hits `/actuator/health` every 10 seconds. The pod only receives traffic when this endpoint returns `HTTP 200 OK`.

### 2.3 Liveness Probes

```yaml
livenessProbe:
  httpGet:
    path: /actuator/health
    port: http
  initialDelaySeconds: 60
  periodSeconds: 15
```
- **Purpose:** Determines if the pod is alive. If the application is deadlocked or permanently broken, this probe will fail.
- **Behavior:** It waits 60 seconds (giving Spring Boot ample time to boot up) and checks every 15 seconds. If the probe fails 3 times consecutively, Kubernetes will automatically restart the pod.

---

## 3. Files Modified

We updated the `Deployment` manifests for all 7 services:
- `k8s/eureka/deployment.yaml`
- `k8s/api-gateway/deployment.yaml`
- `k8s/user-service/deployment.yaml`
- `k8s/account-service/deployment.yaml`
- `k8s/sequence-generator/deployment.yaml`
- `k8s/transaction-service/deployment.yaml`
- `k8s/fund-transfer/deployment.yaml`

---

## 4. Validation

- [x] Applied updated deployments to the cluster.
- [x] Verified that Kubernetes triggered a rolling update (terminating old pods and starting new ones).
- [x] Confirmed the new pods successfully reached the `Running` state and passed their readiness probes (1/1 Ready).
- [x] Inspected a pod description (`kubectl describe pod`) to verify that the `Requests`, `Limits`, `Liveness`, and `Readiness` constraints were correctly recognized by the cluster.

---

## 5. Horizontal Pod Autoscaler (HPA) Implementation

### What is HPA?
Horizontal Pod Autoscaler (HPA) automatically updates a workload resource (such as a Deployment or StatefulSet), with the aim of automatically scaling the workload to match demand based on observed metrics like CPU utilization.

### Why we needed it
We needed HPA to ensure our applications can handle varying loads dynamically without manual intervention, distributing traffic across multiple pods when under pressure to maintain performance and reliability.

### Why CPU was selected
CPU is the most direct indicator of active load for stateless microservices. Memory is often less reliable for autoscaling in JVM applications because Java tends to hold onto memory rather than releasing it back to the OS immediately.

### Replicas Configuration (minReplicas = 1, maxReplicas = 2)
Because this is a local laptop development environment (Intel i5, 15.7 GB RAM, ~7.4 GB allocated to Docker), HPA must be conservative. Setting `minReplicas: 1` saves resources during idle times, and `maxReplicas: 2` allows demonstrating autoscaling without exhausting the laptop's limited hardware resources.

### Selected Service
We selected `user-service` for this HPA demonstration. 
**Why:** It is a meaningful, stateless service with a clean, read-only endpoint (`/api/users`) that is safe for load testing. Stateful components or singleton services (like Sequence Generator or Eureka) are not ideal for simple autoscaling.

### How Kubernetes Metrics API provides CPU usage
HPA relies on the Kubernetes Metrics API, which is served by the Metrics Server. The Metrics Server continuously collects resource metrics (like CPU and memory usage) from the kubelet on each node and exposes them via the Metrics API for HPA to consume.

### How HPA decides to scale
The HPA controller periodically fetches metrics from the Metrics API. It calculates the ratio of current metric value to the target value (e.g., CPU 70%). If the average utilization across all pods exceeds the target, HPA increases the number of replicas to distribute the load and lower the average utilization.

### What happened during scale-up
During our controlled load test, the CPU usage for `user-service` exceeded the 70% threshold (reaching over 300% of the requested 100m CPU). HPA detected this sustained utilization and automatically scaled the deployment from 1 replica to 2 replicas to handle the load.

### What happened during scale-down
Once the load test was stopped, the CPU utilization began to drop back to idle levels (near 2-3%). After the stabilization window passed, HPA gracefully scaled the deployment back down to 1 replica to conserve resources.

---

## 6. Project Artifacts

### Files Created
- `k8s/user-service/hpa.yaml`

### Files Modified
- `components.yaml` (Metrics Server manifest downloaded and modified to include `--kubelet-insecure-tls` for Docker Desktop compatibility)

### Commands Used
- `kubectl apply -f components.yaml`
- `kubectl apply -f k8s/user-service/hpa.yaml`
- `kubectl get hpa -n banking -w`
- `kubectl top pods -n banking`
- `kubectl port-forward svc/user-service 8082:8082 -n banking`
- `cmd.exe /c "FOR /L %i IN (1,1,50000) DO curl.exe -s http://localhost:8082/api/users > NUL"` (Load testing)

---

## 7. Performance Engineering Relevance
HPA is a core concept in performance engineering. It demonstrates the system's elasticity—the ability to adapt to varying workloads dynamically. By configuring HPA correctly, we ensure that the system maintains low latency and high throughput during traffic spikes, while minimizing infrastructure costs during low-traffic periods.

---

## 8. Problems Encountered
**Problem:** The default `kubectl top pods` command failed with `error: Metrics API not available`. Docker Desktop does not come with the Metrics Server pre-installed, and the standard Metrics Server manifest fails due to missing kubelet certificates.
**Solution:** We downloaded the standard Kubernetes Metrics Server manifest (`components.yaml`) and manually injected the `--kubelet-insecure-tls` flag into the `metrics-server` deployment args to allow it to run securely on Docker Desktop.

---

## 9. Phase Completion Checklist
- [x] Metrics API available
- [x] kubectl top works
- [x] HPA manifest created
- [x] HPA applied
- [x] minReplicas = 1
- [x] maxReplicas = 2
- [x] CPU target configured
- [x] HPA reads actual CPU metrics
- [x] Normal state verified
- [x] Controlled scale-up verified
- [x] Scale-down verified
- [x] Application remains healthy
- [x] Existing readiness probes remain working
- [x] Existing liveness probes remain working
- [x] Existing resource requests/limits remain unchanged
- [x] No business logic changed

---

## 10. What Comes Next

You have successfully completed **Phase 0, Phase 1, Phase 2, and Phase 3**!

The banking microservices are now robustly deployed in a local Kubernetes cluster, complete with resource governance, automated health checks, and elasticity through Horizontal Pod Autoscaler. Phase 4 will likely involve observability or service mesh enhancements, as dictated by the plan.

---

Document updated: 2026-08-26
Phase: 3 — Kubernetes Performance & Reliability (with HPA)
Status: COMPLETE
