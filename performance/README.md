# Phase 9: Performance Engineering & Bottleneck Analysis

This directory contains the `k6` performance testing framework for the Banking Application.

## Architecture & Safety
The scripts are explicitly designed to target the `API-Gateway` via the `istio-ingressgateway` using safe, read-only `GET` endpoints (`/api/users`, `/api/accounts`, `/api/transactions`, `/api/fund-transfers`).
Destructive operations (e.g., initiating fund transfers or mutating accounts) have been strictly excluded to preserve financial data integrity.

## Prerequisites
1. **k6**: Must be installed locally (e.g., `choco install k6` or downloaded from `k6.io`).
2. **Cluster Access**: Ensure `istio-ingressgateway` is port-forwarded (e.g., `8088:80`).
3. **Authentication**: If Keycloak enforces strict security, provide the token via environment variable.
4. **Data Verification**: Verify test data values in `config/test-config.example.js` using the SQL `SELECT` queries listed in the discovery report before running anything beyond a simple smoke test. Do not assume sample data is valid.

## Test Suites & Execution Commands

Before running any tests, ensure you are in the `performance` directory. You can run these tests using the following commands based on what you want to achieve:

### 1. Baseline Test
**Purpose:** Establishes P50/P95 response latency under minimal load. Use this to verify that the system is responsive and to get baseline metrics.
```powershell
k6 run scripts/baseline-test.js
```

### 2. Load Test
**Purpose:** Simulates standard production-level traffic scaling. Use this to verify that your system can handle expected day-to-day traffic.
```powershell
k6 run scripts/load-test.js
# Example with an explicit Auth Token:
# k6 run --env K6_TOKEN="your_jwt_here" scripts/load-test.js
```

### 3. Stress Test
**Purpose:** Applies an aggressive traffic ramp-up to identify resource saturation limits and breaking points.
```powershell
k6 run scripts/stress-test.js
```

### 4. Spike Test
**Purpose:** Tests the Horizontal Pod Autoscaler (HPA) and Istio Circuit Breakers via sudden, massive bursts of traffic.
```powershell
k6 run scripts/spike-test.js
```

### 5. Istio Traffic-Visualization Test
**Purpose:** Generates constant, moderate, mixed traffic across all services specifically to build a rich, stable service graph in Kiali. Run this while you have Kiali open.
```powershell
k6 run scripts/istio-visualization-test.js
```

### 6. Canary Demonstration Test
**Purpose:** Generates isolated Account Service traffic to clearly observe v1/v2 weighted splits (e.g., 90/10 routing) in Kiali during a canary deployment.
```powershell
k6 run scripts/canary-demo-test.js
```
