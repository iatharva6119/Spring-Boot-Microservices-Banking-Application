# Phase 1 — Kubernetes Foundation

---

## 1. Objective

### What we wanted to achieve

We wanted to prepare the Kubernetes environment so that it is ready to receive our banking application services in Phase 2.

Think of this phase like preparing an empty building before moving furniture in. We are not moving anything yet. We are making sure the building is structurally ready, the lights work, and we know which rooms go where.

### Why we needed it

Before deploying any application, Kubernetes needs:
- A working cluster (the server that runs and manages containers)
- A namespace (a logical boundary to keep our app separate from other things)
- A clear understanding of how images will be supplied to the cluster

Without these foundations, deploying services in Phase 2 would fail.

### How it fits into the project

Phase 1 sits between:
- Phase 0 (understanding the existing system)
- Phase 2 (actually moving the services into Kubernetes)

The work done here — the cluster, the namespace, the image strategy, the directory structure — is what Phase 2 will build on top of.

---

## 2. Starting Point

Before Phase 1, we had:
- kubectl v1.36.1 installed on Windows
- Docker Desktop installed, with Kubernetes NOT yet enabled
- No Kubernetes context configured
- All 7 application Docker images stored in the local Docker image cache
- No Kubernetes cluster running

---

## 3. What We Implemented

### 3.1 Enabled Docker Desktop Kubernetes

Docker Desktop includes a built-in Kubernetes cluster. We enabled it through the Docker Desktop Settings panel:
Docker Desktop → Settings (gear icon) → Kubernetes → Enable Kubernetes → Apply & Restart

The cluster took approximately 2–3 minutes to start. Once ready, Docker Desktop showed a green Kubernetes running indicator.

When Docker Desktop Kubernetes starts, it automatically:
- Creates a kubectl context called `docker-desktop`
- Sets that context as the active (current) context
- Creates the standard Kubernetes namespaces: `default`, `kube-system`, `kube-public`, `kube-node-lease`, `local-path-storage`

### 3.2 Verified the Kubernetes Cluster

We ran several verification commands to confirm the cluster is healthy and usable.

Results:
- kubectl client version: v1.36.1
- Kubernetes server version: v1.36.1
- Node name: desktop-control-plane
- Node status: Ready
- Node role: control-plane
- Node IP: 172.18.0.2 (inside the Docker Desktop VM)
- Container runtime: containerd://2.3.1
- OS on the node: Debian GNU/Linux 13 (trixie), running inside WSL2

### 3.3 Discovered the Image Strategy Challenge

An important finding in Phase 1:

Docker Desktop's Kubernetes cluster runs inside a virtual machine (WSL2). The Kubernetes node uses `containerd` as its container runtime. This is a completely separate image store from the Docker image cache.

This means: images built with `docker build` are NOT automatically visible to Kubernetes pods, even though they appear in `docker images`.

We verified this by creating a test pod with `imagePullPolicy: Never` and the pod failed with `ErrImageNeverPull`.

### 3.4 Set Up a Local Docker Registry

To solve the image access problem, we started a local Docker Registry container:

Image used: `registry:2` (the official Docker registry image)
Port: `5001` on the Windows host, forwarded to port `5000` inside the registry container

The registry is accessible from:
- Windows host: `http://localhost:5001`
- Inside Docker/Kubernetes: `http://localhost:5001` (Docker Desktop forwards localhost to the host)

We then:
1. Tagged all 7 application images to use the local registry name (`localhost:5001/banking/<service-name>:latest`)
2. Pushed all 7 images to the local registry
3. Verified all images exist in the registry via the registry catalog API
4. Tested that Kubernetes can successfully pull from the registry

The image pull test for `service-registry` completed with Status: Succeeded, confirming the image strategy works.

### 3.5 Created the banking Namespace

We created a dedicated Kubernetes namespace called `banking`.

A namespace is like a folder inside Kubernetes. All our application resources (Pods, Deployments, Services, ConfigMaps, Secrets) will live inside the `banking` namespace, keeping them separate from:
- Kubernetes system components (`kube-system`)
- Any other applications that might run on the cluster

The namespace was defined in a YAML file (`k8s/namespace.yaml`) and applied with `kubectl apply`.

### 3.6 Created the k8s/ Directory Structure

We created the project's Kubernetes configuration directory:

`
k8s/
├── namespace.yaml          <- The banking namespace definition
├── eureka/                 <- Will hold Eureka (Service Registry) YAML files
├── user-service/           <- Will hold User Service YAML files
├── account-service/        <- Will hold Account Service YAML files
├── sequence-generator/     <- Will hold Sequence Generator YAML files
├── transaction-service/    <- Will hold Transaction Service YAML files
├── fund-transfer/          <- Will hold Fund Transfer YAML files
└── api-gateway/            <- Will hold API Gateway YAML files
`

Each subdirectory will receive Deployment and Service YAML files in Phase 2.

---

## 4. Architecture Before

Before Phase 1:

`
Windows Host
  |
  +-- Docker Desktop (Kubernetes DISABLED)
  |     No cluster, no context, no pods
  |
  +-- Docker image cache (7 images available, but not accessible to K8s)
  |
  +-- kubectl v1.36.1 installed (but no cluster to connect to)
`

---

## 5. Architecture After

After Phase 1:

`
Windows Host
  |
  +-- Docker Desktop
  |     |
  |     +-- Kubernetes ENABLED
  |     |     Node: desktop-control-plane (Ready, v1.36.1)
  |     |     Runtime: containerd://2.3.1
  |     |     Namespaces:
  |     |       - kube-system  (Kubernetes internals)
  |     |       - banking      (our application - CREATED in Phase 1)
  |     |       - default, kube-public, kube-node-lease, local-path-storage
  |     |
  |     +-- local-registry container (registry:2)
  |           Port: 5001 (host) -> 5000 (container)
  |           Images stored:
  |             localhost:5001/banking/service-registry:latest
  |             localhost:5001/banking/api-gateway:latest
  |             localhost:5001/banking/user-service:latest
  |             localhost:5001/banking/account-service:latest
  |             localhost:5001/banking/sequence-generator:latest
  |             localhost:5001/banking/transaction-service:latest
  |             localhost:5001/banking/fund-transfer:latest
  |
  +-- kubectl active context: docker-desktop
  |
  +-- Project k8s/ directory structure (empty YAML folders, ready for Phase 2)
`

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `k8s/namespace.yaml` | Defines the `banking` Kubernetes namespace |
| `k8s/eureka/` | Empty directory, will hold Eureka Deployment and Service YAML in Phase 2 |
| `k8s/user-service/` | Empty directory, will hold User Service YAML in Phase 2 |
| `k8s/account-service/` | Empty directory, will hold Account Service YAML in Phase 2 |
| `k8s/sequence-generator/` | Empty directory, will hold Sequence Generator YAML in Phase 2 |
| `k8s/transaction-service/` | Empty directory, will hold Transaction Service YAML in Phase 2 |
| `k8s/fund-transfer/` | Empty directory, will hold Fund Transfer YAML in Phase 2 |
| `k8s/api-gateway/` | Empty directory, will hold API Gateway YAML in Phase 2 |
| `docs/phase-01-kubernetes-foundation.md` | This document |

---

## 7. Files Modified

**No existing files were modified in Phase 1.**

We only created new files and directories. All existing application code, Docker configuration, and Docker Compose files remain exactly as they were.

---

## 8. Configuration Explained

### 8.1 namespace.yaml

The namespace YAML file is very simple:

`yaml
apiVersion: v1
kind: Namespace
metadata:
  name: banking
  labels:
    app.kubernetes.io/part-of: banking-application
    environment: development
`

- `apiVersion: v1` — This is the Kubernetes API version for basic resources like Namespaces.
- `kind: Namespace` — This tells Kubernetes what type of resource we are creating.
- `name: banking` — The name of our namespace. All future kubectl commands will use `-n banking` to target this namespace.
- `labels` — Labels are key-value pairs that describe and categorise the resource. They do not change how the namespace behaves but make it easier to find and manage it later.

### 8.2 Local Registry Setup

The local registry runs as a Docker container:

`
docker run -d \
  --name local-registry \
  --restart=always \
  -p 5001:5000 \
  registry:2
`

- `-d` — Run in the background (detached mode)
- `--name local-registry` — Give the container a recognisable name
- `--restart=always` — Automatically restart if Docker Desktop restarts
- `-p 5001:5000` — Map port 5001 on the Windows host to port 5000 inside the container
- `registry:2` — The official Docker distribution registry image

### 8.3 Image Naming Convention

We chose this naming convention for images in the local registry:

`localhost:5001/banking/<service-name>:latest`

- `localhost:5001` — The address of our local registry
- `banking` — The repository group (matches our namespace name for clarity)
- `<service-name>` — Short, clear service name (e.g., `user-service`, `api-gateway`)
- `:latest` — The tag (we keep `latest` for now; a real production system would use git commit hashes or version numbers)

### 8.4 imagePullPolicy

In Phase 2, all Kubernetes Deployments will use:

`imagePullPolicy: IfNotPresent`

This means: if the image is already cached in the Kubernetes node's local image store, use the cached version. If not, pull from the registry.

This is appropriate for our local registry because:
- The first pull downloads from our local registry (fast, since it is on the same machine)
- Subsequent restarts use the cached version (even faster)
- We do NOT use `Always` (which would re-download the image every time a pod starts)
- We do NOT use `Never` (which requires the image to already exist in the node cache)

---

## 9. Commands Used

### Enable Kubernetes in Docker Desktop
This is done through the Docker Desktop UI, not a command. See Section 3.1 for the steps.

### Verify kubectl and cluster
`powershell
kubectl version
`
Shows both the kubectl client version and the Kubernetes server version. Both showed v1.36.1.

### Check kubectl contexts
`powershell
kubectl config get-contexts
`
Lists all configured Kubernetes clusters. After enabling Docker Desktop Kubernetes, this shows `docker-desktop` as the active context (marked with *).

### Check Kubernetes nodes
`powershell
kubectl get nodes -o wide
`
Shows the cluster's nodes. We have one node: `desktop-control-plane` with status `Ready`.

### Get cluster information
`powershell
kubectl cluster-info
`
Shows the Kubernetes control plane address and CoreDNS address.

### Start the local registry
`powershell
docker run -d --name local-registry --restart=always -p 5001:5000 registry:2
`
Starts a Docker Registry container. Uses `--restart=always` so it survives Docker Desktop restarts.

### Tag an image for the local registry
`powershell
docker tag spring-boot-microservices-banking-application-user-service:latest localhost:5001/banking/user-service:latest
`
Creates a new name/tag for an existing image. Does not copy or duplicate the image data.

### Push an image to the local registry
`powershell
docker push localhost:5001/banking/user-service:latest
`
Uploads the image from Docker's image cache into the local registry.

### Verify images in the registry
`powershell
Invoke-RestMethod -Uri "http://localhost:5001/v2/banking/user-service/tags/list"
`
Queries the registry's REST API to confirm an image exists.

### Create the banking namespace
`powershell
kubectl apply -f k8s\namespace.yaml
`
Reads the namespace.yaml file and creates the `banking` namespace in Kubernetes.

### Verify the namespace
`powershell
kubectl get namespace banking
kubectl describe namespace banking
`
Confirms the namespace exists and shows its details.

### Test image pull from registry (verification test)
`powershell
kubectl run registry-test --image=localhost:5001/banking/service-registry:latest --image-pull-policy=Always --restart=Never --namespace=banking --command -- echo "registry-accessible"
`
Ran a test pod to confirm Kubernetes can pull images from our local registry. Result: Succeeded.

---

## 10. Validation

### 10.1 Docker Desktop Kubernetes Enabled
**Action:** Check Docker Desktop status indicator and run `kubectl version`
**Expected result:** Green Kubernetes indicator, server version returned
**Actual result:** PASS — Server Version: v1.36.1

### 10.2 kubectl Context Correctly Set
**Action:** `kubectl config get-contexts`
**Expected result:** `docker-desktop` context shown as current (*)
**Actual result:** PASS — Context `docker-desktop` is current

### 10.3 Kubernetes Node is Ready
**Action:** `kubectl get nodes -o wide`
**Expected result:** Node status = Ready
**Actual result:** PASS

| Node | Status | Role | Version | Runtime |
|------|--------|------|---------|---------|
| desktop-control-plane | Ready | control-plane | v1.36.1 | containerd://2.3.1 |

### 10.4 System Pods Running
**Action:** `kubectl get pods --all-namespaces`
**Expected result:** All kube-system pods running
**Actual result:** PASS — All system pods running (coredns x2, etcd, kindnet, kube-apiserver, kube-controller-manager, kube-proxy, kube-scheduler, local-path-provisioner)

### 10.5 Local Registry Running
**Action:** `docker ps --filter "name=local-registry"`
**Expected result:** Container is Up
**Actual result:** PASS — local-registry is Up, port 0.0.0.0:5001->5000/tcp

### 10.6 All 7 Images in Registry
**Action:** Queried registry REST API for each image
**Expected result:** All 7 images return `latest` tag
**Actual result:** PASS — All confirmed:
  - banking/service-registry:latest
  - banking/api-gateway:latest
  - banking/user-service:latest
  - banking/account-service:latest
  - banking/sequence-generator:latest
  - banking/transaction-service:latest
  - banking/fund-transfer:latest

### 10.7 Kubernetes Can Pull from Local Registry
**Action:** Created test pod using `localhost:5001/banking/service-registry:latest`
**Expected result:** Pod reaches Completed or Running state
**Actual result:** PASS — Pod status: Completed, Succeeded. Image pulled in 6.9 seconds.

### 10.8 banking Namespace Created
**Action:** `kubectl get namespace banking`
**Expected result:** Namespace exists with status Active
**Actual result:** PASS — namespace/banking Active

### 10.9 k8s/ Directory Structure Created
**Action:** `Get-ChildItem -Recurse k8s`
**Expected result:** namespace.yaml + 7 service subdirectories
**Actual result:** PASS — All directories present

---

## 11. Problems Encountered

### Problem 1: imagePullPolicy: Never did not work with Docker Desktop Kubernetes
**Problem:** When we set `imagePullPolicy: Never` and used the original Docker image names (e.g., `spring-boot-microservices-banking-application-service-registry:latest`), the pod failed with `ErrImageNeverPull`.
**Cause:** Docker Desktop's Kubernetes runs inside a WSL2 virtual machine. The Kubernetes node uses `containerd` as its container runtime. Docker's image cache and containerd's image cache are separate. Images built with `docker build` are not automatically copied into containerd's image store.
**Solution:** Set up a local Docker Registry container. Push all images to it. The registry is accessible from both the Windows host and from inside the Kubernetes VM via `localhost:5001`.

### Problem 2: Powershell pipe swallowed docker push output
**Problem:** When we used a pipeline (`docker push  | Tail-Object`) the push command output was lost and images were not pushed.
**Cause:** `Tail-Object` is not a PowerShell cmdlet. The pipe redirected the output to a non-existent command, which silently discarded it.
**Solution:** Ran `docker push` for each image individually without the pipe. All 7 images were pushed successfully.

---

## 12. Important Concepts

### Kubernetes
Kubernetes is a system that automatically manages containerised applications. It decides where to run containers, monitors their health, restarts them if they crash, and scales them up or down based on demand. Think of it as an operating system for containers.

### Namespace
A namespace is a way to divide a Kubernetes cluster into separate virtual sections. All the resources in one namespace are isolated from resources in other namespaces (unless explicitly connected). We create the `banking` namespace so all our services live together, separate from Kubernetes internals.

### Pod
A Pod is the smallest unit in Kubernetes. A Pod runs one or more containers together. When you deploy a Spring Boot application to Kubernetes, it runs inside a Pod. Pods are temporary — if a Pod crashes, Kubernetes creates a new one.

### Node
A Node is a machine (real or virtual) where Kubernetes runs Pods. In Docker Desktop Kubernetes, we have one Node called `desktop-control-plane`. It runs inside the Docker Desktop VM (WSL2).

### Control Plane
The control plane is the brain of Kubernetes. It consists of several components:
- `kube-apiserver` — accepts all kubectl commands
- `kube-scheduler` — decides which node should run each Pod
- `kube-controller-manager` — watches the cluster and makes corrections
- `etcd` — stores the cluster's state (like a database)

In Docker Desktop Kubernetes, the single node runs BOTH the control plane and the application workloads.

### Container Runtime
The container runtime is the software that actually runs containers on a node. Docker Desktop Kubernetes uses `containerd` version 2.3.1 as its container runtime. This is different from Docker itself — which is why Docker images need to go through a registry to reach the Kubernetes node.

### imagePullPolicy
This tells Kubernetes how to handle container images:
- `Always` — always download the image from the registry, even if it is already cached
- `IfNotPresent` — use the cached image if available, download only if not present
- `Never` — never download; only use images already in the cache (we cannot use this with our registry setup)

### Container Registry
A container registry is a storage system for Docker/container images. Our local registry (running on port 5001) acts like a private mini-version of Docker Hub, accessible only on our machine.

### CoreDNS
CoreDNS is the DNS server built into Kubernetes. When a Pod needs to find another Pod or Service, it asks CoreDNS. For example, when a service says `eureka:8761`, CoreDNS translates that name into an IP address inside the cluster.

### kubectl context
A kubectl context is a saved connection profile that tells kubectl which cluster to connect to, and with what credentials. Docker Desktop automatically creates the `docker-desktop` context and sets it as active when Kubernetes is enabled.

---

## 13. Performance Engineering Relevance

Phase 1 matters for a Performance Engineer for several reasons:

### Resource Awareness
Docker Desktop Kubernetes allocates resources from the Windows host. We are running on:
- Intel i5-1145G7 (4 physical cores / 8 logical processors)
- 15.7 GB RAM (Docker Desktop allocated 7.4 GB)

The single Kubernetes node runs the control plane AND our application workloads together. This means every application Pod competes for resources with Kubernetes itself.

This is why Phase 3 will use conservative resource requests and limits.

### Single Node Architecture
In a real production Kubernetes cluster, you have separate nodes for the control plane and application workloads. Here we have one node for everything. This means:
- There is no true high availability
- Resource contention is possible between system pods and application pods
- Performance results should be interpreted with this in mind

### Image Size Observation
Each of our Docker images is 770–820 MB. This is because they use `eclipse-temurin:17-jdk` (the full JDK). In production, you would use a slim JRE base image (e.g., `eclipse-temurin:17-jre`) to reduce the image to ~200–300 MB. Smaller images:
- Pull faster from the registry
- Start faster (less to unpack into the container filesystem)
- Use less disk space on the node

For this project, we keep the existing images unchanged. The large image size is a known baseline.

### Registry Latency
Our local registry is on `localhost:5001`. Image pulls complete in ~6–7 seconds for an ~800 MB image. This only happens on the first pull — subsequent Pod starts reuse the cached image in containerd and start much faster.

---

## 14. Current Architecture

`
+------------------------------------------------------------------+
|  Windows Host - Intel i5-1145G7, 15.7 GB RAM                     |
|                                                                   |
|  MySQL 3306 (directly on Windows)                                 |
|                                                                   |
|  Docker Desktop (7.4 GB allocated)                                |
|  |                                                                |
|  +-- Kubernetes ENABLED (docker-desktop context)                  |
|  |     Node: desktop-control-plane (Ready, v1.36.1)               |
|  |     Runtime: containerd://2.3.1 (WSL2 VM)                      |
|  |     Namespaces:                                                 |
|  |       kube-system     <- Kubernetes internals                  |
|  |       banking         <- Our application (EMPTY - Phase 2)     |
|  |       default, kube-public, kube-node-lease                    |
|  |       local-path-storage                                        |
|  |                                                                |
|  +-- local-registry (registry:2)                                  |
|  |     Port: 5001 (host) -> 5000 (container)                     |
|  |     Images available:                                           |
|  |       localhost:5001/banking/service-registry:latest           |
|  |       localhost:5001/banking/api-gateway:latest                |
|  |       localhost:5001/banking/user-service:latest               |
|  |       localhost:5001/banking/account-service:latest            |
|  |       localhost:5001/banking/sequence-generator:latest         |
|  |       localhost:5001/banking/transaction-service:latest        |
|  |       localhost:5001/banking/fund-transfer:latest              |
|  |                                                                |
|  +-- keycloak (quay.io/keycloak/keycloak:24.0)                   |
|        Port: 8571 (host) -> 8080 (container)                     |
+------------------------------------------------------------------+

Project k8s/ structure:
  k8s/
    namespace.yaml     <- Applied, banking namespace Active
    eureka/            <- Ready for Phase 2
    user-service/      <- Ready for Phase 2
    account-service/   <- Ready for Phase 2
    sequence-generator/<- Ready for Phase 2
    transaction-service/<- Ready for Phase 2
    fund-transfer/     <- Ready for Phase 2
    api-gateway/       <- Ready for Phase 2
`

---

## 15. Completion Checklist

- [x] Docker Desktop Kubernetes enabled
- [x] kubectl client version confirmed: v1.36.1
- [x] Kubernetes server version confirmed: v1.36.1
- [x] kubectl context set to docker-desktop
- [x] Kubernetes node (desktop-control-plane) is Ready
- [x] All kube-system pods are Running
- [x] Discovered image access challenge (Docker vs containerd image stores)
- [x] Local registry started on port 5001
- [x] All 7 images tagged for local registry
- [x] All 7 images pushed to local registry
- [x] All 7 images verified in registry via REST API
- [x] Image pull test from Kubernetes succeeded (Status: Completed)
- [x] banking namespace created from namespace.yaml
- [x] banking namespace is Active
- [x] k8s/ directory structure created (7 service subdirectories + namespace.yaml)
- [x] Created this documentation

---

## 16. What Comes Next

**Phase 2 — Kubernetes Application Migration**

In Phase 2, we will actually deploy all 7 Spring Boot services into the `banking` namespace.

For each service, we will create:
- A **Deployment** — tells Kubernetes how many copies of the service to run and what Docker image to use
- A **Service** — gives the Deployment a stable network address so other pods can reach it

We will also address several important challenges:
- **MySQL connectivity** — Pods cannot use `localhost` to reach MySQL on Windows. We will use `host-gateway` or the host IP.
- **Keycloak connectivity** — Same challenge as MySQL.
- **Eureka registration** — Services need to find each other through Eureka inside Kubernetes.
- **Feign calls** — We need to confirm that service-to-service calls through Eureka still work.
- **Actuator health** — We need to confirm the health endpoints are reachable.
- **End-to-end flow** — We will test the full banking flow: Client → Gateway → Fund Transfer → Account → Transaction → MySQL.

We will NOT start Phase 2 until you explicitly approve.

---

## 17. Learning Summary

**What did we actually accomplish in Phase 1?**

We turned on the Kubernetes cluster that was built into Docker Desktop.

We discovered that Docker Desktop Kubernetes uses a different image system than regular Docker, and we solved this by setting up a local private registry — a small image server running on our own machine. We pushed all 7 of our application images into this registry and proved that Kubernetes can pull from it.

We created a dedicated namespace called `banking` that will hold all our application resources. And we created a clean directory structure (`k8s/`) where all our Kubernetes YAML configuration files will live.

The cluster is ready. The images are ready. The namespace is ready. The directory structure is ready. Phase 1 is complete.

---

Document created: 2026-08-25
Phase: 1 — Kubernetes Foundation
Status: COMPLETE — Waiting for approval to proceed to Phase 2
