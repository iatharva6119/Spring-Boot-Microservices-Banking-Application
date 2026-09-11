import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spring Boot Microservices Banking Application - Architecture</title>
    <style>
        :root {
            --bg-page: #0d1117;
            --bg-panel: #161b22;
            --bg-node: #21262d;
            --border-color: #30363d;
            --border-highlight: #484f58;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            
            --color-k8s: #326ce5;
            --color-istio: #466bb0;
            --color-spring: #6db33f;
            --color-db: #e38c00;
            --color-security: #f0883e;
            --color-obs: #d2a8ff;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: var(--color-spring);
            margin-bottom: 5px;
            font-size: 2.2rem;
        }
        
        .header p {
            color: var(--text-muted);
            margin-top: 0;
            font-size: 1.1rem;
        }

        .layout-grid {
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 25px;
            max-width: 1600px;
            margin: 0 auto;
        }

        .box {
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        }

        .level-group {
            border: 2px dashed var(--border-highlight);
            border-radius: 12px;
            padding: 25px 20px 20px 20px;
            margin-bottom: 25px;
            position: relative;
            background: rgba(22, 27, 34, 0.4);
        }

        .level-title {
            position: absolute;
            top: -14px;
            left: 20px;
            background: var(--bg-page);
            padding: 0 12px;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.9rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-radius: 10px;
            border: 1px solid var(--border-highlight);
        }

        .k8s-cluster {
            border-color: var(--color-k8s);
        }
        
        .k8s-cluster .level-title {
            color: var(--color-k8s);
            border-color: var(--color-k8s);
        }

        .istio-mesh {
            border-color: var(--color-istio);
            border-style: solid;
            background: rgba(70, 107, 176, 0.05);
        }

        .istio-mesh .level-title {
            color: var(--color-istio);
            border-color: var(--color-istio);
            background: var(--bg-panel);
        }

        .flex-row {
            display: flex;
            justify-content: space-evenly;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 15px;
        }

        .flex-col {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }

        .node {
            background: var(--bg-node);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            min-width: 160px;
            position: relative;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        
        .node:hover {
            transform: translateY(-2px);
        }

        .node h4 {
            margin: 0 0 10px 0;
            font-size: 1.1rem;
        }

        .node ul {
            text-align: left;
            margin: 0;
            padding-left: 20px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .node-tag {
            font-size: 0.75rem;
            background: var(--border-highlight);
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 10px;
            display: inline-block;
        }

        .node-canary {
            background: rgba(227, 140, 0, 0.2);
            color: var(--color-db);
            border: 1px solid var(--color-db);
        }

        /* Colors for different node types */
        .node.external { border-color: #8b949e; }
        .node.external h4 { color: #ffffff; }
        
        .node.security { border-color: var(--color-security); }
        .node.security h4 { color: var(--color-security); }
        
        .node.gateway { border-color: var(--color-spring); border-width: 3px; }
        .node.gateway h4 { color: var(--color-spring); }
        
        .node.service { border-color: var(--color-spring); }
        .node.service h4 { color: var(--color-spring); }
        
        .node.db { border-color: var(--color-db); }
        .node.db h4 { color: var(--color-db); }
        
        .node.obs { border-color: var(--color-obs); }
        .node.obs h4 { color: var(--color-obs); }

        .arrow {
            color: var(--text-muted);
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .arrow-down { margin: 10px 0; }
        .arrow-right { margin: 0 10px; }

        .connection-line {
            width: 2px;
            height: 20px;
            background-color: var(--text-muted);
            margin: 0 auto;
        }

        .legend {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .line-solid { width: 30px; height: 2px; background: var(--text-muted); }
        .line-dashed { width: 30px; height: 2px; border-bottom: 2px dashed var(--text-muted); }
        .line-dotted { width: 30px; height: 2px; border-bottom: 2px dotted var(--text-muted); }

        .sidecar-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: var(--color-istio);
            color: white;
            font-size: 0.7rem;
            font-weight: bold;
            padding: 3px 6px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Observability Panels */
        .obs-pillar {
            background: var(--bg-node);
            border: 1px solid var(--border-highlight);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .obs-pillar h3 {
            color: var(--color-obs);
            margin-top: 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            font-size: 1rem;
        }
        
        .operations-bar {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        @media (max-width: 1200px) {
            .layout-grid { grid-template-columns: 1fr; }
        }
        
        @media print {
            body { background: white; color: black; }
            .box, .node, .level-group { background: white; box-shadow: none; border-color: #ccc; }
            .level-title { background: white; }
            h1, h2, h3, h4 { color: black !important; }
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>Spring Boot Microservices Banking Application</h1>
        <p>Cloud-Native Architecture Overview</p>
    </div>

    <div class="layout-grid">
        <!-- LEFT COLUMN: MAIN ARCHITECTURE -->
        <div class="main-arch">
            
            <!-- LEVEL 1: EXTERNAL -->
            <div class="level-group">
                <div class="level-title">External Access</div>
                <div class="flex-row">
                    <div class="node external">
                        <h4>Client</h4>
                        <div class="node-tag">Web / Mobile / Postman</div>
                    </div>
                    <div class="node external">
                        <h4>k6 Testing</h4>
                        <div class="node-tag">Baseline, Load, Stress, Spike</div>
                    </div>
                </div>
            </div>

            <div class="arrow arrow-down">↓</div>

            <!-- LEVEL 2: SECURITY & INGRESS -->
            <div class="level-group">
                <div class="level-title">Identity & Security</div>
                <div class="flex-row" style="align-items: stretch;">
                    <div class="flex-col" style="flex: 1;">
                        <div class="node security" style="width: 100%;">
                            <h4>Keycloak</h4>
                            <ul>
                                <li>Identity Management</li>
                                <li>OAuth2 / OIDC</li>
                                <li>JWT Token Issuance</li>
                            </ul>
                            <div class="node-tag">Host Machine :8571</div>
                        </div>
                    </div>
                    <div class="arrow arrow-right" style="align-self: center;">↔</div>
                    <div class="flex-col" style="flex: 1;">
                        <div class="node gateway" style="width: 100%;">
                            <h4>Istio Ingress Gateway</h4>
                            <ul>
                                <li>NodePort 31380</li>
                                <li>Entry to Service Mesh</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="arrow arrow-down">↓</div>

            <!-- LEVEL 3: KUBERNETES & ISTIO -->
            <div class="level-group k8s-cluster">
                <div class="level-title">Docker Desktop Kubernetes Cluster (banking namespace)</div>
                
                <div class="flex-row" style="margin-bottom: 20px;">
                    <div class="node" style="border-style: dotted;">
                        <h4>ConfigMap & Secrets</h4>
                        <div class="node-tag">Injected into Banking Workloads</div>
                    </div>
                </div>

                <div class="level-group istio-mesh">
                    <div class="level-title">ISTIO SERVICE MESH (STRICT mTLS)</div>
                    
                    <div class="flex-row" style="margin-bottom: 30px;">
                        <div class="node gateway">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>API Gateway</h4>
                            <ul>
                                <li>Port 8080 (NP 30080)</li>
                                <li>Central Entry Point</li>
                                <li>Request Routing</li>
                                <li>JWT Validation</li>
                            </ul>
                        </div>
                        <div class="node service" style="border-style: dashed;">
                            <h4>Netflix Eureka</h4>
                            <ul>
                                <li>Port 8761</li>
                                <li>Service Registry</li>
                                <li>Discovery for Gateway & Feign</li>
                            </ul>
                        </div>
                    </div>

                    <!-- BANKING MICROSERVICES -->
                    <div style="text-align: center; margin-bottom: 15px; color: var(--text-muted); font-weight: bold;">
                        Banking Services protected by Istio Envoy Sidecars<br>
                        <span style="font-size: 0.8rem; font-weight: normal;">(Routing, Load Balancing, Retries, Timeouts, Outlier Detection)</span>
                    </div>

                    <div class="flex-row">
                        <div class="node service">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>User Service</h4>
                            <ul>
                                <li>Port 8082</li>
                                <li>User Registration</li>
                                <li>Keycloak Admin API</li>
                            </ul>
                        </div>
                        
                        <div class="node service">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>Account Service</h4>
                            <ul>
                                <li>Port 8081</li>
                                <li>Account Management</li>
                                <li>Balance Lifecycle</li>
                            </ul>
                            <div class="node-tag node-canary">v1 Active / v2 Routing Supported</div>
                        </div>

                        <div class="node service">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>Sequence Gen</h4>
                            <ul>
                                <li>Port 8083</li>
                                <li>Unique Account Numbers</li>
                            </ul>
                        </div>

                        <div class="node service">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>Transaction Service</h4>
                            <ul>
                                <li>Port 8084</li>
                                <li>Deposit / Withdrawal</li>
                                <li>Transaction Records</li>
                            </ul>
                        </div>

                        <div class="node service">
                            <span class="sidecar-badge">Envoy</span>
                            <h4>Fund Transfer</h4>
                            <ul>
                                <li>Port 8085</li>
                                <li>Transfer Orchestration</li>
                                <li>Saga / Feign calls</li>
                            </ul>
                        </div>
                    </div>
                </div> <!-- End Istio Mesh -->
            </div> <!-- End K8s -->

            <div class="arrow arrow-down">↓</div>

            <!-- LEVEL 5: DATA LAYER -->
            <div class="level-group">
                <div class="level-title">MYSQL DATA LAYER (External to Kubernetes)</div>
                <div class="flex-row">
                    <div class="node db"><h4>User DB</h4></div>
                    <div class="node db"><h4>Account DB</h4></div>
                    <div class="node db"><h4>Sequence DB</h4></div>
                    <div class="node db"><h4>Transaction DB</h4></div>
                    <div class="node db"><h4>Transfer DB</h4></div>
                </div>
                <div style="text-align: center; margin-top: 10px; font-size: 0.85rem; color: var(--text-muted);">
                    Database-per-Service Architecture (Port 3306 on Host)
                </div>
            </div>

        </div> <!-- End Main Arch -->

        <!-- RIGHT COLUMN: OBSERVABILITY -->
        <div class="obs-panel">
            <div class="box">
                <h2 style="text-align: center; color: var(--color-obs); margin-top: 0;">Observability & Monitoring</h2>
                <div style="text-align: center; margin-bottom: 20px; font-size: 0.85rem; color: var(--text-muted);">
                    monitoring namespace
                </div>
                
                <div class="obs-pillar">
                    <h3>Metrics</h3>
                    <div class="flex-col">
                        <div class="node-tag">Micrometer + Actuator</div>
                        <div class="arrow arrow-down" style="font-size: 16px; margin: 2px;">↓</div>
                        <div class="node obs" style="width: 100%; min-width: 0;">Prometheus</div>
                        <div class="node-tag" style="background: transparent;">+ kube-state-metrics & Envoy</div>
                    </div>
                </div>

                <div class="obs-pillar">
                    <h3>Logs</h3>
                    <div class="flex-col">
                        <div class="node-tag">stdout / stderr</div>
                        <div class="arrow arrow-down" style="font-size: 16px; margin: 2px;">↓</div>
                        <div class="node obs" style="width: 100%; min-width: 0;">Fluent Bit</div>
                        <div class="arrow arrow-down" style="font-size: 16px; margin: 2px;">↓</div>
                        <div class="node obs" style="width: 100%; min-width: 0;">Loki</div>
                    </div>
                </div>

                <div class="obs-pillar">
                    <h3>Traces</h3>
                    <div class="flex-col">
                        <div class="node-tag">OTel Java Agent</div>
                        <div class="arrow arrow-down" style="font-size: 16px; margin: 2px;">↓</div>
                        <div class="node obs" style="width: 100%; min-width: 0;">Jaeger Collector</div>
                        <div class="node-tag" style="background: transparent;">100% Trace Sampling</div>
                    </div>
                </div>

                <div class="obs-pillar" style="background: rgba(210, 168, 255, 0.1); border-color: var(--color-obs);">
                    <h3 style="text-align: center;">Visualization</h3>
                    <div class="node obs" style="width: 100%; min-width: 0; margin-bottom: 10px;">
                        <h4>Grafana</h4>
                        <ul>
                            <li>8 Provisioned Dashboards</li>
                            <li>App, JVM, K8s, Istio, k6</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- FOOTER / OPERATIONS -->
    <div class="operations-bar">
        <div class="node" style="padding: 10px; min-width: 100px;">Docker Desktop</div>
        <div class="node" style="padding: 10px; min-width: 100px;">Local Registry :5001</div>
        <div class="node" style="padding: 10px; min-width: 100px;">kubectl</div>
        <div class="node" style="padding: 10px; min-width: 100px;">istioctl</div>
        <div class="node" style="padding: 10px; min-width: 100px; border-style: dashed;">Kiali (if enabled)</div>
    </div>

    <div class="legend">
        <div class="legend-item"><div class="line-solid"></div> Request / Data Flow</div>
        <div class="legend-item"><div class="line-dashed"></div> Registration / Discovery</div>
        <div class="legend-item"><div class="line-dotted"></div> Configuration Injection</div>
    </div>

    <div class="box" style="margin-top: 40px; max-width: 1600px; margin-left: auto; margin-right: auto;">
        <h3 style="margin-top: 0;">Architecture Summary</h3>
        <p style="margin-bottom: 0;">
            The Spring Boot Microservices Banking Application implements a true database-per-service pattern, protected by an Istio Service Mesh enforcing STRICT mTLS. The API Gateway serves as the single entry point, handling JWT validation via Keycloak before routing requests through Envoy sidecars. Synchronous inter-service communication is handled via OpenFeign and Eureka discovery. Comprehensive observability is built-in with Prometheus, Grafana, Loki, and Jaeger, alongside performance testing capabilities via k6. Canary infrastructure is configured for the Account Service, ready for v2 pod deployment. Rate limiting is <b>not</b> currently implemented.
        </p>
    </div>

</body>
</html>"""

mmd_content = """%% 1. High-Level Architecture
graph TD
    subgraph External
        Client[Client Web/Mobile]
        k6[k6 Perf Tests]
    end

    subgraph Security[Identity & Security]
        KC[Keycloak :8571]
    end

    subgraph K8s[Kubernetes Cluster]
        IG[Istio Ingress Gateway]
        AG[API Gateway]
        
        subgraph Mesh[Istio Service Mesh - banking ns]
            EU[Eureka Registry]
            US[User Service]
            AS[Account Service]
            SG[Sequence Generator]
            TS[Transaction Service]
            FT[Fund Transfer]
        end
    end

    subgraph Data[External MySQL Data Layer]
        DB_U[(User DB)]
        DB_A[(Account DB)]
        DB_S[(Seq DB)]
        DB_T[(Trans DB)]
        DB_F[(Fund DB)]
    end

    Client -->|Login| KC
    KC -.->|JWT| Client
    Client -->|API Request| IG
    k6 -->|Load Test| IG
    IG --> AG
    AG -.->|Validate JWT| KC
    AG -->|Route| Mesh
    
    US --> DB_U
    AS --> DB_A
    SG --> DB_S
    TS --> DB_T
    FT --> DB_F

%% 2. Banking Microservices Communication
graph TD
    AG[API Gateway]
    EU((Eureka))
    
    US[User Service]
    AS[Account Service]
    SG[Sequence Generator]
    TS[Transaction Service]
    FT[Fund Transfer Service]
    
    AG -.->|Discovery| EU
    US -.->|Register| EU
    AS -.->|Register| EU
    SG -.->|Register| EU
    TS -.->|Register| EU
    FT -.->|Register| EU
    
    AG -->|Route| US & AS & SG & TS & FT
    
    US -->|Feign GET| AS
    AS -->|Feign GET| US
    AS -->|Feign POST| SG
    AS -->|Feign GET| TS
    TS -->|Feign GET/PUT| AS
    FT -->|Feign GET/PUT| AS
    FT -->|Feign POST| TS

%% 3. Istio Service Mesh
graph LR
    subgraph Pod A [Client Pod]
        AppA[Application]
        EnvA[Envoy Sidecar]
        AppA <--> EnvA
    end
    
    subgraph Pod B [Target Pod]
        EnvB[Envoy Sidecar]
        AppB[Application]
        EnvB <--> AppB
    end
    
    EnvA <-->|STRICT mTLS| EnvB
    
    subgraph Istio Control Plane
        Istiod[istiod]
    end
    
    Istiod -.->|Configures| EnvA
    Istiod -.->|Configures| EnvB

%% 4. Observability Architecture
graph TD
    App[Spring Boot Service]
    
    subgraph Metrics
        App -->|Micrometer /actuator/prometheus| Prom[Prometheus]
        Envoy[Envoy Sidecar] -->|Merged Metrics| Prom
        KSM[kube-state-metrics] --> Prom
    end
    
    subgraph Logs
        App -->|stdout| FB[Fluent Bit]
        FB -->|tail /var/log/containers| Loki[Loki]
    end
    
    subgraph Traces
        App -->|OTel Java Agent| JC[Jaeger Collector]
    end
    
    Prom --> Grafana[Grafana Dashboards]
    Loki --> Grafana
    JC --> Grafana

%% 5. Fund Transfer Flow
sequenceDiagram
    participant Client
    participant AG as API Gateway
    participant FT as Fund Transfer
    participant AS as Account Service
    participant TS as Transaction Service
    
    Client->>AG: POST /api/fund-transfers (JWT)
    AG->>FT: Forward Request
    
    FT->>AS: GET Source Account (Verify)
    AS-->>FT: Account Data
    FT->>AS: GET Dest Account (Verify)
    AS-->>FT: Account Data
    
    FT->>AS: PUT Deduct from Source
    AS-->>FT: OK
    FT->>AS: PUT Add to Dest
    AS-->>FT: OK
    
    FT->>TS: POST 2 Internal Tx Records
    TS-->>FT: OK
    
    FT-->>AG: Transfer Success
    AG-->>Client: 200 OK

%% 6. Canary Infrastructure
graph TD
    Client --> IG[Istio Ingress]
    IG --> VS[VirtualService: account-service-route]
    
    VS -->|Weight: 50| DR_V1
    VS -->|Weight: 50| DR_V2
    
    subgraph DestinationRule
        DR_V1[Subset v1]
        DR_V2[Subset v2]
    end
    
    DR_V1 --> Pod_V1[Account Service Pod v1 <br/> ACTIVE]
    DR_V2 -.-> Pod_V2[Account Service Pod v2 <br/> NOT DEPLOYED YET]
    
    style Pod_V2 stroke-dasharray: 5 5
"""

presentation_content = """# BANKING_ARCHITECTURE_PRESENTATION.md

## SLIDE 1
**Title:** Spring Boot Microservices Banking Application
**Subtitle:** Cloud-Native Architecture

---

## SLIDE 2
**Business Overview**
- **What it does:** A comprehensive backend for banking operations including user management, account creation, transaction recording, and fund transfers.
- **Why microservices:** Decouples distinct business domains (Users, Accounts, Transactions) to enable independent scaling, isolated failures, and dedicated databases (database-per-service), avoiding monolithic bottlenecks.

---

## SLIDE 3
**Core Microservices**
- **API Gateway:** Central entry point and router (Port 8080)
- **Eureka:** Service Registry for discovery (Port 8761)
- **User Service:** User registration & Keycloak integration (Port 8082)
- **Account Service:** Account management & balance lifecycle (Port 8081)
- **Sequence Generator:** Unique account number generation (Port 8083)
- **Transaction Service:** Deposits, withdrawals & records (Port 8084)
- **Fund Transfer Service:** Saga orchestration for transfers (Port 8085)

---

## SLIDE 4
**Request Flow**
1. **Client** initiates request
2. **Istio Ingress Gateway** receives external K8s traffic
3. **API Gateway** validates and routes
4. **Eureka Discovery** resolves the target pod IP
5. **Microservice** processes business logic via Envoy sidecar
6. **Database** (MySQL) executes queries for that specific service

---

## SLIDE 5
**Security**
- **Keycloak:** External Identity and Access Management
- **JWT / OAuth2:** Token-based authentication
- **User Approval Flow:** Admins approve users in User Service, which integrates via Keycloak Admin API to enable accounts.
- **Gateway Security:** API Gateway validates JWTs using Keycloak's JWKS; backend services trust the Gateway.

---

## SLIDE 6
**Kubernetes Architecture**
- **Namespaces:** `banking`, `monitoring`, `istio-system`
- **Workloads:** 1-replica Deployments for all services, resulting in managed Pods
- **Networking:** ClusterIP Services (NodePort for Gateway)
- **Configuration:** Shared `ConfigMap` for env vars, `Secrets` for base64 credentials
- **Resilience:** Readiness and Liveness Probes configured across deployments

---

## SLIDE 7
**Istio Service Mesh**
- **Envoy Sidecars:** Intercept all pod traffic
- **STRICT mTLS:** Encrypted pod-to-pod communication
- **VirtualService & DestinationRule:** Control routing and subsets
- **Traffic Protection:** Configured Retries, Timeouts, and Outlier Detection (Circuit Breaking)
- **Canary Infrastructure:** Account Service configured with v1/v2 subsets and 50/50 traffic splitting (ready for v2 pod deployment)

---

## SLIDE 8
**Observability**
- **Metrics:** Micrometer -> Prometheus -> Grafana
- **Logs:** Pod stdout -> Fluent Bit -> Loki -> Grafana
- **Traces:** OTel Java Agent -> Trace Context -> Jaeger Collector -> Jaeger UI/Grafana
- *Provides unified visibility across application, JVM, K8s, and Istio layers.*

---

## SLIDE 9
**Performance Testing**
- **Tooling:** k6 framework
- **Scenarios:** Baseline, Load, Stress, Spike, and Canary visualization tests
- **Focus:** API Gateway edge testing against read-only (GET) endpoints
- **Analysis:** Real-time impact visible in Prometheus & Grafana dashboards

---

## SLIDE 10
**Project Achievements**
✓ Spring Boot Microservices
✓ API Gateway
✓ Eureka Service Discovery
✓ OpenFeign Communication
✓ Keycloak Integration
✓ Docker
✓ Kubernetes Deployment
✓ ConfigMaps and Secrets
✓ Istio Service Mesh
✓ STRICT mTLS
✓ Traffic Management
✓ Retries and Timeouts
✓ Outlier Detection
✓ Canary Infrastructure (Configured)
✓ Prometheus Monitoring
✓ Grafana Dashboards
✓ Centralized Logging
✓ Distributed Tracing
✓ k6 Performance Testing
"""

workspace = r"c:\Users\atde0626\Desktop\Spring-Boot-Microservices-Banking-Application"

with open(os.path.join(workspace, "banking-architecture.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

with open(os.path.join(workspace, "banking-architecture.mmd"), "w", encoding="utf-8") as f:
    f.write(mmd_content)

with open(os.path.join(workspace, "BANKING_ARCHITECTURE_PRESENTATION.md"), "w", encoding="utf-8") as f:
    f.write(presentation_content)

print("SUCCESS: Generated HTML, MMD, and Presentation deliverables.")
