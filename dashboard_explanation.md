# Comprehensive Guide to the Banking Performance Dashboard

Welcome to the detailed guide for the Banking Performance Dashboard. This document is designed for developers, DevOps, and Performance Engineers to deeply understand the metrics being collected, what they indicate about the system's health, and how to use them to diagnose and resolve performance bottlenecks in a Spring Boot Microservices architecture.

---

## 🌐 Row 1 — Overall System Health

This row provides a macroscopic view of the entire banking application. It serves as the primary "at-a-glance" health indicator during load tests or production monitoring.

### 1. Total RPS (Requests Per Second)
*   **What it measures:** The aggregate throughput of the entire system. It counts the number of HTTP requests arriving at the system every second.
*   **Performance Engineering Context:** 
    *   **Baseline:** You must establish a baseline RPS that the system can handle comfortably.
    *   **Capacity Planning:** By increasing load during testing, you monitor RPS. When you increase virtual users but the RPS flatlines or drops, you have found the system's maximum capacity (the saturation point).
    *   **Anomaly Detection:** A sudden drop in RPS in production usually indicates a severe bottleneck (e.g., database lock, network partition) preventing requests from entering the system.

### 2. Error Rate (5xx)
*   **What it measures:** The percentage of total requests that result in HTTP 5xx Server Errors (e.g., 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout).
*   **Performance Engineering Context:**
    *   **Reliability:** The target is always 0%. An acceptable SLA (Service Level Agreement) might be < 0.1%.
    *   **Stress Testing:** During stress testing, you push the system until the error rate spikes. This tells you *how* the system fails (e.g., does it gracefully degrade or catastrophically crash?).
    *   **Cascading Failures:** In microservices, one failing service can cause 5xx errors to cascade to dependent services.

### 3. Active Services
*   **What it measures:** The number of registered microservice instances currently reporting metrics to Prometheus.
*   **Performance Engineering Context:**
    *   **Auto-scaling Validation:** If you configure the system to scale out (add more instances) under load, this metric verifies that the new instances are successfully booting up and joining the cluster.
    *   **Availability:** Ensures that all required components of the banking system (Account, User, Transaction, Fund-Transfer, etc.) are up.

### 4. Avg Response Time
*   **What it measures:** The mean time taken to process all incoming requests across the system.
*   **Performance Engineering Context:** While useful for a very high-level view, average latency is highly susceptible to outliers (a few very slow requests can heavily skew the average). Therefore, percentiles (Row 2) are far more critical for performance engineering.

---

## ⏱️ Row 2 — Latency (Response Time Percentiles)

Latency is arguably the most critical performance metric. Percentiles describe the distribution of response times, ensuring we account for the slowest requests.

### p50, p90, p95, p99 Latency
*   **What it measures:** 
    *   **p50 (Median):** 50% of requests are faster than this value. It represents the "typical" user experience.
    *   **p90:** 90% of requests are faster; 10% are slower.
    *   **p95:** 95% of requests are faster; 5% are slower.
    *   **p99:** 99% of requests are faster; 1% are slower. This represents the "tail latency"—the worst experiences users are having.
*   **Performance Engineering Context:**
    *   **SLA Definition:** Service Level Agreements are almost always defined in percentiles (e.g., "99% of requests must complete in under 500ms").
    *   **The "Long Tail" Problem:** A system might have a great p50 (50ms) but a terrible p99 (3000ms). This means 1 in 100 users experiences a 3-second delay. In a high-traffic banking app, that translates to thousands of frustrated customers.
    *   **Troubleshooting:** If p50 is slow, the entire system or database is uniformly sluggish. If only p99 spikes, the issue might be intermittent garbage collection pauses, temporary network hiccups, or specific complex database queries locking tables occasionally.

---

## 📊 Row 3 — HTTP Status Distribution

This row provides a granular view of request outcomes.

### HTTP Status Rate
*   **What it measures:** The rate of specific HTTP status codes returned over time.
    *   **2xx (Success):** Everything is operating normally.
    *   **4xx (Client Error):** The client sent a bad request (e.g., 400 Bad Request, 404 Not Found, 401 Unauthorized). 
    *   **5xx (Server Error):** The server failed to fulfill a valid request.
*   **Performance Engineering Context:**
    *   **Load Test Validation:** If you run a load test simulating successful fund transfers and see a spike in 4xx errors, your test script might have a bug (e.g., using invalid account IDs).
    *   **Security:** A sudden spike in 401/403 errors could indicate a brute-force attack or a misconfigured security service.
    *   **Timeouts:** A spike in 504 Gateway Timeouts usually indicates that a downstream microservice or database is too slow, causing the API Gateway to give up waiting.

---

## ☕ Row 4 & 4b — JVM (Java Virtual Machine) Metrics

Because this is a Spring Boot application, understanding the underlying JVM is critical. Java performance issues often stem from poor memory management.

### 1. JVM Heap Memory
*   **What it measures:** The amount of memory currently used by Java objects. The heap is divided into generations (Young, Old).
*   **Performance Engineering Context:**
    *   **Memory Leaks:** If the heap usage resembles a "staircase" pattern—constantly increasing and never returning to its baseline after Garbage Collection—the application has a memory leak and will eventually crash with an `OutOfMemoryError`.
    *   **Sizing:** Helps determine if the `-Xmx` (max heap size) is configured correctly. If the heap is consistently at 90%, it needs more memory.

### 2. GC (Garbage Collection) Pause Duration & Rate
*   **What it measures:** How frequently the JVM stops application threads to reclaim unused memory (Rate) and how long those pauses last (Duration). 
*   **Performance Engineering Context:**
    *   **Stop-the-World Pauses:** Most GC events completely pause the application. If a GC pause takes 2 seconds, every single request currently being processed is delayed by 2 seconds. This causes massive spikes in p99 latency.
    *   **Tuning:** If pauses are too long or too frequent, a performance engineer must tune the JVM (e.g., switching to the G1GC or ZGC collector, or adjusting generation sizes).

### 3. JVM Threads & Loaded Classes
*   **What it measures:** The number of active execution threads (e.g., Tomcat worker threads handling HTTP requests) and the number of Java classes loaded into memory.
*   **Performance Engineering Context:**
    *   **Thread Starvation:** If the application hits its maximum thread limit (e.g., Tomcat's default 200), new requests will queue up and eventually time out. This often happens if threads are "stuck" waiting for a slow database response.

---

## 💻 Row 5 & 6 — System Resources (CPU & Memory)

These rows look at the infrastructure level (the Docker containers or underlying OS).

### Process CPU & Memory
*   **What it measures:** The raw percentage of CPU time and physical RAM used by the application process.
*   **Performance Engineering Context:**
    *   **CPU Bound vs. I/O Bound:** 
        *   If CPU is at 100% but the database is idle, the application is doing heavy computations (CPU Bound). Optimizing code or scaling out is required.
        *   If CPU is at 15% but response times are terrible, the application is likely waiting on the network or database (I/O Bound). Adding more CPU will *not* help; you must fix the database or network.
    *   **Container Limits:** Ensures the application isn't hitting Docker memory limits (which would cause the OS to aggressively kill the container, resulting in an OOMKilled status).

---

## 🔗 Row 7 — Per-Microservice Latency & RPS

This row provides the critical breakdown necessary for a distributed architecture. 

### p95 Latency & Throughput Per Service
*   **What it measures:** The p95 response time and RPS isolated for each specific microservice (API Gateway, User Service, Transaction Service, etc.).
*   **Performance Engineering Context:**
    *   **Bottleneck Identification:** In a complex transaction (e.g., transferring funds), the API Gateway calls the Fund Transfer service, which might call the User, Account, and Transaction services. If the overall transaction is slow, this row tells you *exactly which service is causing the delay*.
    *   **Targeted Scaling:** If the `account-service` is struggling under load while the `user-service` is fine, you only need to scale out the `account-service`, saving infrastructure costs.

---

## 🗄️ Row 8 — Database Connection Pool (HikariCP)

The connection pool is the bridge between the application and the database. It is notoriously one of the most common sources of performance degradation.

### HikariCP Connection Pool (Active / Idle / Max)
*   **What it measures:**
    *   **Max:** The maximum number of database connections the application is allowed to open.
    *   **Active:** Connections currently executing a query against the database.
    *   **Idle:** Open connections sitting in the pool waiting to be used.
*   **Performance Engineering Context:**
    *   **Connection Exhaustion:** If `Active` connections reach the `Max` limit, the pool is exhausted. Any new request needing database access will be blocked (forced to wait). If it waits too long, it times out. This results in severe latency spikes and 500 errors.
    *   **Tuning the Pool:** 
        *   If exhaustion happens frequently, you might need to increase the `maximum-pool-size`. 
        *   However, making the pool *too large* can overwhelm the database server itself (CPU/Memory spikes on the MySQL server).
        *   The goal is to find the perfect balance where the pool is just large enough to handle peak load without crushing the database. This row is essential for finding that "sweet spot".
