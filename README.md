# 🏦 Spring Boot Microservices Banking Application

A complete backend banking application built using **Java 17, Spring Boot, Spring Cloud, Netflix Eureka, Spring Cloud Gateway, OpenFeign, MySQL, Keycloak, Docker, Prometheus, Grafana and cAdvisor**.

The application follows a **microservices architecture** where banking responsibilities are divided into independent services. Each business service owns its own database and communicates with other services through REST APIs using OpenFeign and Eureka service discovery.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Business Capabilities](#-business-capabilities)
- [Architecture](#-architecture)
- [Microservices](#-microservices)
- [Technology Stack](#-technology-stack)
- [Service Ports](#-service-ports)
- [Project Structure](#-project-structure)
- [Request Flow](#-request-flow)
- [Inter-Service Communication](#-inter-service-communication)
- [Database Architecture](#-database-architecture)
- [Security](#-security)
- [API Gateway](#-api-gateway)
- [Dockerization](#-dockerization)
- [Docker Compose](#-docker-compose)
- [Monitoring and Observability](#-monitoring-and-observability)
- [Grafana Dashboard](#-grafana-dashboard)
- [Performance Metrics](#-performance-metrics)
- [Alerting](#-alerting)
- [Logging and Exception Handling](#-logging-and-exception-handling)
- [Prerequisites](#-prerequisites)
- [Configuration](#-configuration)
- [Build the Project](#-build-the-project)
- [Run the Application](#-run-the-application)
- [Verify the Application](#-verify-the-application)
- [Docker Commands](#-docker-commands)
- [Monitoring Commands](#-monitoring-commands)
- [Important Design Decisions](#-important-design-decisions)
- [Current Limitations](#-current-limitations)
- [Future Improvements](#-future-improvements)
- [End-to-End Examples](#-end-to-end-examples)
- [Troubleshooting](#-troubleshooting)
- [Project Summary](#-project-summary)

---

# 📖 Project Overview

This project is a **Spring Boot based banking application implemented using microservices architecture**.

Instead of building one large monolithic application, the banking functionality is separated into multiple independently deployable services.

The application supports core banking operations such as:

- User registration and profile management
- User approval and account activation
- Bank account creation and lifecycle management
- Unique bank account number generation
- Balance enquiry
- Deposit
- Withdrawal
- Transaction history
- Internal fund transfer between accounts
- Authentication and identity management through Keycloak
- Dynamic service discovery through Eureka
- Centralized API routing through Spring Cloud Gateway
- Containerized deployment using Docker and Docker Compose
- Application and infrastructure monitoring using Actuator, Micrometer, Prometheus, Grafana and cAdvisor

The project also includes performance-oriented monitoring for:

- Request rate
- Response time
- P50/P90/P95/P99 latency
- HTTP error rates
- JVM memory
- Garbage collection
- JVM threads
- CPU usage
- Database connection pool usage
- Docker container resource utilization
- Service availability

---

# 💼 Business Capabilities

The system models a simplified digital banking backend.

### User Management

A customer can be registered through the User Service. The user identity is also created in Keycloak. The local database stores the application's user and profile information along with the Keycloak authentication ID.

### Account Management

After user registration and approval, a bank account can be created. Account Service validates the user, prevents duplicate accounts of the same type, requests a sequence number, constructs the account number and stores the account.

### Transactions

The Transaction Service handles:

- Deposits
- Withdrawals
- Internal transfer transaction records
- Transaction history

### Fund Transfers

Fund Transfer Service coordinates movement of money between two accounts. It validates the source account, validates available balance, validates the destination account, updates both balances and records the corresponding transaction entries.

---

# 🏗️ Architecture

## High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         │ Postman / Web / App  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    API Gateway       │
                         │      :8080           │
                         │ Routing + Security   │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └─────────────┐
                    ▼                                  ▼
             ┌──────────────┐                  ┌──────────────┐
             │    Eureka    │                  │   Keycloak   │
             │    :8761     │                  │    :8571     │
             │Service       │                  │ Identity /   │
             │Registry      │                  │ JWT          │
             └──────┬───────┘                  └──────────────┘
                    │
       ┌────────────┼────────────┬──────────────┬─────────────┐
       ▼            ▼            ▼              ▼             ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
 │  User    │ │ Account  │ │Sequence  │ │ Transaction  │ │Fund Transfer │
 │ Service  │ │ Service  │ │Generator │ │   Service    │ │   Service    │
 │  :8082   │ │  :8081   │ │  :8083   │ │    :8084     │ │    :8085     │
 └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘ └──────┬───────┘
      │             │             │              │                │
      ▼             ▼             ▼              ▼                ▼
   MySQL          MySQL         MySQL          MySQL            MySQL
 user_service account_service sequence_generator transaction_service fund_transfer_service

                         Monitoring Layer
        ┌────────────────────────────────────────────────┐
        │ Actuator → Micrometer → Prometheus → Grafana  │
        │                         ↑                       │
        │                     cAdvisor                   │
        └────────────────────────────────────────────────┘
```

## Main Architectural Components

| Component | Responsibility |
|---|---|
| API Gateway | Single entry point, request routing and OAuth2/JWT configuration |
| Eureka | Service registration and discovery |
| Keycloak | Identity management and JWT token provider |
| User Service | User and profile management |
| Account Service | Account lifecycle and balance management |
| Sequence Generator | Sequential account number generation |
| Transaction Service | Deposit, withdrawal and transaction records |
| Fund Transfer Service | Internal fund transfer orchestration |
| MySQL | Persistent data storage |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Actuator | Application health and metrics endpoints |
| Micrometer | Metrics instrumentation |
| Prometheus | Metrics collection and storage |
| Grafana | Metrics visualization |
| cAdvisor | Docker container metrics |

---

# 🧩 Microservices

## 1. Service Registry — Eureka

**Port:** `8761`

Eureka acts as the service registry for the application.

Every business microservice registers itself with Eureka. Other services can then discover a service using its logical name rather than using a hardcoded IP address.

### Responsibilities

- Maintain service registry
- Track service instances
- Receive service heartbeats
- Enable dynamic service discovery
- Support load-balanced service communication

### Example

```text
Account Service
      │
      │ "Where is user-service?"
      ▼
   Eureka
      │
      │ user-service → instance address
      ▼
Account Service calls User Service
```

---

## 2. API Gateway

**Port:** `8080`

The API Gateway is the single entry point for client requests.

It uses Spring Cloud Gateway and routes requests to backend services using Eureka-based service discovery.

### Responsibilities

- Central entry point
- URL-based request routing
- Service discovery integration
- Load-balanced routing using `lb://`
- OAuth2 resource server/JWT configuration
- Centralized API access layer

### Example Routes

```text
/api/users/**       → user-service
/accounts/**        → account-service
/sequence/**        → sequence-generator
/transactions/**    → transaction-service
/fund-transfers/**  → fund-transfer-service
```

---

## 3. User Service

**Port:** `8082`

User Service manages customer identity and profile information.

It also integrates with Keycloak using the Keycloak Admin Client.

### Responsibilities

- Register users
- Store user information
- Store user profile information
- Update user profile
- Update user status
- Enable approved users in Keycloak
- Find users by ID, authentication ID or account information

### Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/users/register` | Register a user |
| GET | `/api/users` | Get users |
| GET | `/api/users/{userId}` | Get user by ID |
| GET | `/api/users/auth/{authId}` | Get user by Keycloak ID |
| GET | `/api/users/accounts/{accountId}` | Find user by account |
| PATCH | `/api/users/{id}` | Update user status |
| PUT | `/api/users/{id}` | Update user profile |

### User Registration Flow

```text
Client
  ↓
API Gateway
  ↓
User Service
  ↓
Check email in Keycloak
  ↓
Create Keycloak user
  ↓
Create local User + UserProfile
  ↓
Save in user_service database
  ↓
Return response
```

---

## 4. Account Service

**Port:** `8081`

Account Service manages bank accounts and account balances.

### Responsibilities

- Create accounts
- Validate user existence
- Prevent duplicate accounts
- Generate account numbers
- Manage account status
- Check balances
- Update accounts
- Close accounts
- Retrieve transaction history

### Account States

```text
PENDING
   │
   ▼
ACTIVE
   │
   ├──► BLOCKED
   │
   └──► CLOSED
```

### Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/accounts` | Create account |
| GET | `/accounts?accountNumber=X` | Get account |
| GET | `/accounts/{userId}` | Get account by user |
| GET | `/accounts/balance?accountNumber=X` | Check balance |
| GET | `/accounts/{accountId}/transactions` | Get transactions |
| PUT | `/accounts?accountNumber=X` | Update account |
| PATCH | `/accounts?accountNumber=X` | Update status |
| PUT | `/accounts/closure?accountNumber=X` | Close account |

---

## 5. Sequence Generator Service

**Port:** `8083`

Sequence Generator provides sequential numbers used to construct unique bank account numbers.

### Flow

```text
Account Service
      │
      │ POST /sequence
      ▼
Sequence Generator
      │
      ▼
Read current sequence
      │
      ▼
Increment sequence
      │
      ▼
Save sequence
      │
      ▼
Return next number
```

Account Service uses the returned number with the configured prefix:

```text
Prefix + padded sequence

060014 + 0000001
        ↓
0600140000001
```

### Main API

```http
POST /sequence
```

---

## 6. Transaction Service

**Port:** `8084`

Transaction Service records and retrieves financial transactions.

### Supported Transaction Types

```text
DEPOSIT
WITHDRAWAL
INTERNAL_TRANSFER
EXTERNAL_TRANSFER
```

### Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/transactions` | Record deposit/withdrawal |
| POST | `/transactions/internal` | Record internal transfer legs |
| GET | `/transactions?accountId=X` | Get account transactions |
| GET | `/transactions/{referenceId}` | Get by reference |

### Deposit Flow

```text
Client
  ↓
Gateway
  ↓
Transaction Service
  ↓
Account Service → Get current account
  ↓
Calculate new balance
  ↓
Account Service → Update balance
  ↓
Save transaction
```

---

## 7. Fund Transfer Service

**Port:** `8085`

Fund Transfer Service orchestrates internal transfers between two accounts.

### Responsibilities

1. Validate source account
2. Check source account status
3. Check available balance
4. Validate destination account
5. Deduct source balance
6. Add destination balance
7. Create transaction records
8. Save fund transfer record
9. Return transfer reference

### Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/fund-transfers` | Transfer money |
| GET | `/fund-transfers/{referenceId}` | Get transfer |
| GET | `/fund-transfers?accountId=X` | Get transfers for account |

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Java 17 | Application development |
| Spring Boot 2.7.x | Microservice framework |
| Spring Cloud 2021.0.8 | Cloud/microservice components |
| Spring Cloud Gateway | API Gateway |
| Netflix Eureka | Service discovery |
| OpenFeign | Service-to-service communication |
| Spring Data JPA | Data access |
| Hibernate | ORM |
| MySQL | Database |
| Keycloak 21.0.1 | Identity and access management |
| OAuth2 | Authorization framework |
| JWT | Authentication token |
| ModelMapper | DTO/entity mapping |
| Lombok | Boilerplate reduction |
| Maven 3.9.x | Build and dependency management |
| Docker | Containerization |
| Docker Compose | Container orchestration |
| Spring Boot Actuator | Health and metrics |
| Micrometer | Metrics instrumentation |
| Prometheus 2.47.0 | Metrics collection |
| Grafana 10.1.0 | Monitoring dashboards |
| cAdvisor 0.47.2 | Container metrics |

> **Note:** Kubernetes is not part of the current implemented project. Docker Compose is used for multi-container orchestration.

---

# 🔌 Service Ports

| Component | Port |
|---|---:|
| API Gateway | `8080` |
| Account Service | `8081` |
| User Service | `8082` |
| Sequence Generator | `8083` |
| Transaction Service | `8084` |
| Fund Transfer Service | `8085` |
| Eureka Server | `8761` |
| Keycloak | `8571` |
| Prometheus | `9090` |
| Grafana | `3000` |
| cAdvisor | `8089` |

---

# 📁 Project Structure

```text
Spring-Boot-Microservices-Banking-Application/
│
├── API-Gateway/
│   ├── src/
│   ├── Dockerfile
│   └── pom.xml
│
├── Service-Registry/
│   ├── src/
│   ├── Dockerfile
│   └── pom.xml
│
├── User-Service/
│   ├── src/main/java/
│   │   └── org/training/user/service/
│   │       ├── controller/
│   │       ├── service/
│   │       ├── repository/
│   │       ├── model/
│   │       ├── exception/
│   │       ├── config/
│   │       ├── external/
│   │       └── utils/
│   ├── Dockerfile
│   └── pom.xml
│
├── Account-Service/
│   ├── src/main/java/
│   │   └── org/training/account/service/
│   │       ├── controller/
│   │       ├── service/
│   │       ├── repository/
│   │       ├── model/
│   │       ├── exception/
│   │       └── external/
│   ├── Dockerfile
│   └── pom.xml
│
├── Sequence-Generator/
│   ├── src/
│   ├── Dockerfile
│   └── pom.xml
│
├── Transaction-Service/
│   ├── src/
│   ├── Dockerfile
│   └── pom.xml
│
├── Fund-Transfer/
│   ├── src/
│   ├── Dockerfile
│   └── pom.xml
│
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
│       └── banking-alerts.yml
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       └── dashboards/
│           ├── dashboard.yml
│           └── banking-performance.json
│
├── docker-compose.yml
├── MONITORING.md
└── postman_collection/
```

---

# 🔄 Request Flow

## General Request Flow

```text
Client
  │
  ▼
API Gateway :8080
  │
  ├── JWT/OAuth2 configuration
  │
  ▼
Eureka Service Registry :8761
  │
  ▼
Target Microservice
  │
  ▼
Service Layer
  │
  ▼
Repository Layer
  │
  ▼
MySQL
```

For operations requiring other services:

```text
Service A
   │
   ▼
OpenFeign
   │
   ▼
Eureka
   │
   ▼
Service B
   │
   ▼
Service B Database
```

---

# 🔗 Inter-Service Communication

The project uses **OpenFeign** for declarative REST communication.

### Communication Map

```text
User Service
    │
    └──────► Account Service

Account Service
    ├──────► User Service
    ├──────► Sequence Generator
    └──────► Transaction Service

Transaction Service
    └──────► Account Service

Fund Transfer Service
    ├──────► Account Service
    └──────► Transaction Service
```

### Why Feign?

Instead of manually constructing HTTP requests, a service defines an interface:

```java
@FeignClient(name = "account-service")
public interface AccountService {

    @GetMapping("/accounts")
    ResponseEntity<Account> readByAccountNumber(
        @RequestParam String accountNumber
    );
}
```

Feign handles the HTTP communication while Eureka provides service discovery.

---

# 🗄️ Database Architecture

The application follows the **Database per Service** approach.

```text
User Service
     ↓
user_service
 ├── user
 └── user_profile

Account Service
     ↓
account_service
 └── account

Sequence Generator
     ↓
sequence_generator
 └── sequence

Transaction Service
     ↓
transaction_service
 └── transaction

Fund Transfer Service
     ↓
fund_transfer_service
 └── fund_transfer
```

Each service owns its business data instead of directly accessing another service's database.

## Database Tables

### `user`

Stores customer-level information.

Important fields include:

- `user_id`
- `email_id`
- `contact_no`
- `auth_id`
- `identification_number`
- `creation_on`
- `status`
- `user_profile_id`

### `user_profile`

Stores profile information such as:

- First name
- Last name
- Gender
- Address
- Occupation
- Nationality

### `account`

Stores:

- Account ID
- Account number
- Account type
- Account status
- Opening date
- Available balance
- User ID

### `sequence`

Stores the current account number sequence.

### `transaction`

Stores:

- Transaction ID
- Reference ID
- Account ID
- Transaction type
- Amount
- Transaction date
- Status
- Comments

### `fund_transfer`

Stores:

- Transfer ID
- Transaction reference
- Source account
- Destination account
- Amount
- Status
- Transfer type
- Transfer date

---

# 🔐 Security

The application integrates **Keycloak** for identity management.

## Authentication Flow

```text
User
  │
  │ Login
  ▼
Keycloak :8571
  │
  │ Access Token
  ▼
Client
  │
  │ Authorization: Bearer <JWT>
  ▼
API Gateway :8080
  │
  │ JWT / JWK validation configuration
  ▼
Microservice
```

Keycloak is also used directly by User Service through the Keycloak Admin Client for operations such as:

- Creating users
- Reading users
- Updating users
- Enabling approved users

### Important Current Configuration

The Gateway contains OAuth2 Resource Server/JWT configuration, but the current implementation uses `anyExchange().permitAll()` rather than enforcing authentication for every route.

Therefore, **JWT validation is configured but not fully enforced by the current authorization rule**.

For a production deployment, the intended rule should be changed to:

```java
.anyExchange().authenticated()
```

---

# 🚪 API Gateway

The Gateway uses `lb://service-name` routes.

Example:

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: account-service
          uri: lb://account-service
          predicates:
            - Path=/accounts/**
```

Here:

```text
lb://account-service
       │
       ▼
Spring Cloud Load Balancer
       │
       ▼
Eureka
       │
       ▼
Account Service instance
```

This means clients do not need to know the actual backend service address.

---

# 🐳 Dockerization

Every application service is containerized using Docker.

A typical Dockerfile uses Java 17:

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Docker Build Flow

```text
Java Source
    ↓
Maven Build
    ↓
Spring Boot JAR
    ↓
Docker Image
    ↓
Docker Container
    ↓
Running Microservice
```

Build the application first:

```bash
mvn clean package -DskipTests
```

Then build Docker images:

```bash
docker compose build
```

---

# 🐙 Docker Compose

Docker Compose is used to run the complete application stack.

The Compose environment contains:

### Application Components

- Service Registry
- API Gateway
- User Service
- Account Service
- Sequence Generator
- Transaction Service
- Fund Transfer Service

### Monitoring Components

- Prometheus
- Grafana
- cAdvisor

All containers communicate through the shared Docker network:

```text
banking-network
```

Inside Docker, services communicate using service names such as:

```text
http://service-registry:8761
http://account-service:8081
http://user-service:8082
http://transaction-service:8084
```

## MySQL and Keycloak

In the current setup, MySQL and Keycloak run on the host machine rather than as Docker containers.

Dockerized services access host resources using:

```text
host.docker.internal
```

Example:

```text
Docker Container
      │
      ▼
host.docker.internal:3306
      │
      ▼
MySQL on Host
```

---

# 📊 Monitoring and Observability

The project includes a complete monitoring stack:

```text
Spring Boot Services
       │
       ▼
Spring Boot Actuator
       │
       ▼
Micrometer
       │
       ▼
/actuator/prometheus
       │
       ▼
Prometheus
       │
       ▼
Grafana
```

For container-level metrics:

```text
Docker Containers
       │
       ▼
cAdvisor
       │
       ▼
Prometheus
       │
       ▼
Grafana
```

---

# ❤️ Spring Boot Actuator

The services expose Actuator endpoints for health and metrics.

Configured endpoints include:

```text
/actuator/health
/actuator/info
/actuator/metrics
/actuator/prometheus
```

### Health

```text
GET /actuator/health
```

Used to check whether the service is healthy.

### Metrics

```text
GET /actuator/metrics
```

Provides the available application metrics.

### Prometheus

```text
GET /actuator/prometheus
```

Exposes metrics in Prometheus-compatible format.

---

# 📈 Prometheus

Prometheus collects metrics from the Spring Boot services at regular intervals.

The configured monitoring setup uses a scrape interval of approximately:

```text
15 seconds
```

Prometheus stores the metrics as time-series data.

It is used to monitor:

- Request count
- Request duration
- Error rates
- JVM
- CPU
- Memory
- GC
- Threads
- HikariCP
- Service availability
- Container metrics

Prometheus UI:

```text
http://localhost:9090
```

---

# 📊 Grafana Dashboard

Grafana provides visualization on top of Prometheus.

Grafana:

```text
http://localhost:3000
```

The project contains a provisioned banking performance dashboard.

## Dashboard Areas

| Area | Purpose |
|---|---|
| Overall System | Overall traffic and health |
| Latency | P50/P90/P95/P99 and average latency |
| HTTP Status | 2xx/4xx/5xx monitoring |
| JVM Memory & GC | Heap and garbage collection |
| JVM Threads | Thread utilization |
| CPU | Application/system/container CPU |
| Memory | JVM and container memory |
| Per-Service Metrics | Service-level performance |
| Database Pool | HikariCP usage |
| Docker Containers | Container resource usage |
| Target Health | Service UP/DOWN status |

---

# ⚡ Performance Metrics

One of the important parts of the monitoring setup is latency analysis.

## P50

P50 is the median response time.

```text
50% of requests completed within P50
```

## P90

```text
90% of requests completed within P90
```

## P95

```text
95% of requests completed within P95
```

P95 is especially useful for understanding typical high-end user experience and SLA performance.

## P99

```text
99% of requests completed within P99
```

P99 helps identify occasional slow requests and tail latency.

### Example

If:

```text
P95 = 2 seconds
```

it means:

```text
95% of requests completed in 2 seconds or less.
```

If:

```text
P99 = 5 seconds
```

then approximately 1% of requests took longer than 5 seconds.

---

# 🧠 Important Prometheus Metrics

## HTTP Metrics

```text
http_server_requests_seconds_count
http_server_requests_seconds_sum
http_server_requests_seconds_bucket
```

Histogram buckets can be used to calculate latency percentiles.

## JVM Metrics

```text
jvm_memory_used_bytes
jvm_gc_pause_seconds
jvm_threads_live_threads
```

## Database Connection Pool

```text
hikaricp_connections_active
hikaricp_connections_pending
hikaricp_connections_timeout_total
```

These are useful for identifying database connection pool saturation.

---

# 🚨 Alerting

Prometheus alert rules are configured for important performance and availability conditions.

| Alert | Condition |
|---|---|
| ServiceDown | Target unavailable |
| HighP95Latency | P95 latency above threshold |
| CriticalP99Latency | P99 latency above threshold |
| High5xxErrorRate | High server error rate |
| CriticalErrorRate | Very high error rate |
| HighProcessCPU | High process CPU |
| CriticalProcessCPU | Critical CPU usage |
| HighJVMHeapUtilization | High JVM heap usage |
| CriticalJVMHeapUtilization | Critical JVM heap usage |
| HighGCPauseTime | High GC pause time |
| HighDBConnectionPoolUtil | High DB pool utilization |
| DBConnectionPoolExhaustion | DB pool close to exhaustion |

The current monitoring setup defines these rules in Prometheus.

**Alertmanager routing is not currently configured.**

---

# 📝 Logging and Exception Handling

The services use SLF4J logging through Lombok's `@Slf4j`.

Typical logging levels include:

```java
log.info(...)
log.error(...)
```

The services also use centralized exception handling through:

```java
@RestControllerAdvice
```

This allows application-specific exceptions to be converted into consistent HTTP responses.

Examples include:

- Resource not found
- Resource conflict
- Insufficient funds
- Invalid account status
- Account closing validation failures
- Empty required fields

---

# ✅ Validation

Validation is implemented using Spring Boot validation support.

DTOs and controller requests can use:

```java
@Valid
```

Business-level validation is also performed inside service methods.

Examples:

- User existence validation
- Duplicate account validation
- Account status validation
- Balance validation
- Minimum balance validation
- Required profile field validation

---

# 🔄 Transaction Management

The User Service uses `@Transactional` at the service implementation level.

This provides database transaction management for local database operations.

The application also demonstrates an important microservices consideration:

> A normal database transaction does not automatically span multiple independent microservices.

For example, a fund transfer updates accounts and then records transactions through separate service calls. These operations are not protected by one distributed database transaction.

This is an important area for future resilience improvements.

---

# 🧪 End-to-End Business Flows

## 1. User Registration

```text
Client
  ↓
API Gateway
  ↓
User Service
  ├──► Keycloak → Create Identity
  │
  └──► MySQL → Save User/Profile
  ↓
Response
```

---

## 2. Account Creation

```text
Client
  ↓
API Gateway
  ↓
Account Service
  │
  ├──► User Service → Validate User
  │
  ├──► Sequence Generator → Get Sequence
  │
  └──► MySQL → Save Account
  ↓
Response
```

---

## 3. Deposit

```text
Client
  ↓
Gateway
  ↓
Transaction Service
  │
  ├──► Account Service → Read Account
  │
  ├──► Calculate New Balance
  │
  ├──► Account Service → Update Balance
  │
  └──► Transaction DB → Save Transaction
  ↓
Response
```

---

## 4. Withdrawal

```text
Client
  ↓
Gateway
  ↓
Transaction Service
  │
  ├──► Account Service → Read Account
  │
  ├──► Check Account Status
  │
  ├──► Check Available Balance
  │
  ├──► Account Service → Update Balance
  │
  └──► Transaction DB → Save Transaction
  ↓
Response
```

---

## 5. Internal Fund Transfer

```text
Client
  ↓
API Gateway
  ↓
Fund Transfer Service
  │
  ├──► Account Service → Validate FROM account
  │
  ├──► Check source balance
  │
  ├──► Account Service → Validate TO account
  │
  ├──► Account Service → Deduct FROM balance
  │
  ├──► Account Service → Credit TO balance
  │
  ├──► Transaction Service → Save debit transaction
  │
  ├──► Transaction Service → Save credit transaction
  │
  └──► Fund Transfer DB → Save transfer record
  ↓
Response
```

The two transaction records share a transaction reference so they can be associated with the same transfer.

---

# 🧱 Microservice Design Principles

The project demonstrates several important microservices principles.

### Single Responsibility

Each service focuses on a defined business responsibility.

### Loose Coupling

Services communicate through APIs rather than directly accessing each other's databases.

### Database per Service

Each business service has its own database.

### Service Discovery

Eureka removes the need for hardcoded service addresses.

### API Gateway Pattern

Clients use one common entry point.

### Independent Deployment

Each service can be packaged and containerized independently.

### Observability

Actuator, Prometheus, Grafana and cAdvisor provide visibility into application and infrastructure behavior.

---

# ⚙️ Prerequisites

Install the following before running the project:

- **JDK 17**
- **Maven 3.9.x**
- **MySQL**
- **Docker Desktop**
- **Docker Compose**
- **Keycloak 21.0.1 or compatible configuration**
- Git
- Postman or another REST client for API testing

Verify Java:

```bash
java -version
```

Verify Maven:

```bash
mvn -version
```

Verify Docker:

```bash
docker --version
docker compose version
```

---

# ⚙️ Configuration

The application uses Spring Boot `application.yml` files for service configuration.

Important configuration areas include:

```text
server.port
spring.application.name
spring.datasource
spring.jpa
eureka.client
management.endpoints
management.metrics
spring.security.oauth2
```

When running inside Docker, environment variables override host-specific configuration where configured.

Example:

```text
EUREKA_CLIENT_SERVICEURL_DEFAULTZONE
SPRING_DATASOURCE_URL
MYSQL_HOST
MYSQL_PORT
MYSQL_DB_NAME
MYSQL_USER
MYSQL_PASSWORD
APP_CONFIG_KEYCLOAK_URL
```

---

# 🗄️ MySQL Setup

Create the required databases:

```sql
CREATE DATABASE user_service;
CREATE DATABASE account_service;
CREATE DATABASE sequence_generator;
CREATE DATABASE transaction_service;
CREATE DATABASE fund_transfer_service;
```

The application uses Hibernate/JPA to create or update the schema according to the configured `ddl-auto` behavior.

---

# 🔐 Keycloak Setup

Keycloak is expected to be available on:

```text
http://localhost:8571
```

The application uses the realm:

```text
banking-service
```

The User Service uses the Keycloak Admin Client to manage users.

The Gateway uses the Keycloak realm's JWK endpoint for JWT resource-server configuration.

---

# 🔨 Build the Project

Build each Maven project before creating the Docker images.

From each service directory:

```bash
mvn clean package -DskipTests
```

Or build the services individually from the project root according to the repository's Maven structure.

The resulting JAR files are placed under:

```text
target/
```

---

# 🐳 Run with Docker Compose

After building the JARs:

```bash
docker compose build
```

Start the complete stack:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Check logs:

```bash
docker logs <container-name>
```

Follow logs:

```bash
docker logs -f <container-name>
```

Stop the stack:

```bash
docker compose down
```

---

# 🔎 Verify the Application

## Eureka

Open:

```text
http://localhost:8761
```

Verify that the application services are registered.

Expected services include:

```text
API-GATEWAY
USER-SERVICE
ACCOUNT-SERVICE
SEQUENCE-GENERATOR
TRANSACTION-SERVICE
FUND-TRANSFER-SERVICE
```

## Gateway

Main entry point:

```text
http://localhost:8080
```

## Actuator

Example:

```text
http://localhost:8081/actuator/health
```

Prometheus endpoint:

```text
http://localhost:8081/actuator/prometheus
```

The same pattern applies to the other Spring Boot services.

## Prometheus

```text
http://localhost:9090
```

Check targets:

```text
http://localhost:9090/targets
```

## Grafana

```text
http://localhost:3000
```

The configured dashboard is provisioned from the repository's Grafana configuration.

---

# 🐳 Useful Docker Commands

### List containers

```bash
docker ps
```

### List all containers

```bash
docker ps -a
```

### View logs

```bash
docker logs <container>
```

### Follow logs

```bash
docker logs -f <container>
```

### Restart a service

```bash
docker compose restart account-service
```

### Rebuild a service

```bash
docker compose build account-service
docker compose up -d account-service
```

### View resource usage

```bash
docker stats
```

### Stop containers

```bash
docker compose down
```

---

# 📊 Useful Monitoring Checks

## Check Service Health

```text
/actuator/health
```

## Check Available Metrics

```text
/actuator/metrics
```

## Check Prometheus Metrics

```text
/actuator/prometheus
```

## Prometheus Target Health

```text
http://localhost:9090/targets
```

## Grafana

```text
http://localhost:3000
```

---

# 🚨 Troubleshooting

## Service Not Appearing in Eureka

Check:

```bash
docker logs <service-name>
```

Verify:

- Eureka container is running
- Eureka URL is correct
- Service application name is correct
- Service can reach `service-registry`
- Allow enough time for registration and heartbeat

---

## Database Connection Failure

Check:

```bash
docker logs account-service
```

Common causes:

- MySQL is not running
- Wrong database name
- Incorrect credentials
- Incorrect host configuration
- `host.docker.internal` connectivity issue

---

## Gateway Returns 503

Check:

1. Is the target service running?
2. Is it registered in Eureka?
3. Does the Gateway route match the requested path?
4. Is the service name correct?
5. Is the Docker network working?

---

## Prometheus Target DOWN

Check:

```text
http://localhost:9090/targets
```

Then verify the service endpoint:

```text
http://localhost:8081/actuator/prometheus
```

Also verify that Prometheus can reach the service using the Docker service name.

---

## Grafana Shows No Data

Check:

1. Prometheus is running.
2. Prometheus targets are UP.
3. Grafana datasource points to Prometheus.
4. The correct Prometheus URL is used from inside Docker:

```text
http://prometheus:9090
```

5. Generate API traffic and wait for Prometheus to scrape the metrics.

---

# ⚠️ Current Limitations

The following points describe the current implementation and should be considered before production deployment.

### 1. Gateway Authentication Enforcement

OAuth2/JWT support is configured, but the current Gateway authorization rule uses:

```java
.anyExchange().permitAll()
```

Therefore, routes are not currently forced to require authentication.

---

### 2. Credentials in Configuration

Some configuration contains database credentials and Keycloak client information.

For production, these should be moved to secure configuration such as:

- Environment variables
- Docker Secrets
- Kubernetes Secrets
- Vault
- Cloud secret-management services

---

### 3. No Circuit Breaker

OpenFeign calls do not currently have a circuit breaker/fallback mechanism such as Resilience4j.

A production implementation should add resilience patterns for service failures.

---

### 4. Distributed Transaction Consistency

A fund transfer spans multiple services and databases.

A failure between balance updates and transaction recording could result in inconsistent state.

A production-grade solution could use:

- Saga pattern
- Event-driven architecture
- Outbox pattern
- Compensation mechanisms

---

### 5. Sequence Generation Concurrency

The current sequence generator maintains a single sequence row and increments it.

Concurrent account creation should be protected with a database-level atomic mechanism to prevent duplicate sequence values.

---

### 6. Host-Based MySQL and Keycloak

MySQL and Keycloak currently run outside Docker.

Therefore, the environment is not completely self-contained.

---

### 7. Alert Routing

Prometheus alert rules are configured, but Alertmanager routing is not currently implemented.

---

### 8. Distributed Tracing

The current implementation does not provide complete distributed tracing across all service calls.

A tracing solution can be added later to simplify troubleshooting across multiple microservices.

---

# 🚀 Future Improvements

Potential production improvements include:

- Enforce JWT authentication on protected routes
- Move secrets to secure secret management
- Add Resilience4j circuit breakers
- Add retries and timeouts for Feign calls
- Introduce distributed tracing
- Add centralized log aggregation
- Add Alertmanager
- Containerize MySQL and Keycloak for a fully reproducible environment
- Improve sequence generation concurrency
- Introduce Saga/Outbox patterns for cross-service consistency
- Add automated integration tests
- Add CI/CD pipeline
- Add Kubernetes deployment for production orchestration
- Add horizontal scaling and autoscaling
- Add database indexes and query optimization based on performance testing

---

# 🎯 Important Design Decisions

## Why Microservices?

The application separates business responsibilities so individual services can be developed, deployed and scaled independently.

## Why Eureka?

Service addresses can change dynamically. Eureka provides service discovery without hardcoding IP addresses.

## Why API Gateway?

Clients use a single entry point rather than communicating with every backend service directly.

## Why OpenFeign?

Feign simplifies REST communication between microservices.

## Why Database per Service?

It reduces database-level coupling and allows each business capability to own its data.

## Why Docker?

Docker provides consistent runtime environments and isolates services.

## Why Docker Compose?

It provides a simple way to start the complete multi-container application locally.

## Why Prometheus?

Prometheus provides time-series metrics collection and querying.

## Why Grafana?

Grafana provides dashboards for understanding application performance and infrastructure health.

## Why cAdvisor?

cAdvisor exposes container-level CPU, memory, network and filesystem metrics that complement application-level metrics.

---

# 🧪 Performance Monitoring Approach

The monitoring setup is designed to help identify performance bottlenecks.

A typical investigation can follow:

```text
High Latency Detected
        ↓
Check P95 / P99
        ↓
Identify Slow Service
        ↓
Check CPU
        ↓
Check JVM Heap
        ↓
Check GC
        ↓
Check HikariCP
        ↓
Check HTTP Error Rate
        ↓
Check Service Logs
        ↓
Identify Root Cause
```

### Example

If Account Service P95 latency increases:

```text
Grafana
   ↓
Account Service P95 high
   ↓
Check CPU
   ↓
Check JVM / GC
   ↓
Check HikariCP active/pending
   ↓
Check database queries
   ↓
Check dependent Feign calls
```

This provides a practical performance-engineering workflow rather than looking only at response time.

---

# 📋 Project Quick Reference

| Item | Value |
|---|---|
| Architecture | Microservices |
| Language | Java 17 |
| Framework | Spring Boot 2.7.x |
| Cloud | Spring Cloud 2021.0.8 |
| Gateway | Spring Cloud Gateway |
| Discovery | Netflix Eureka |
| Communication | OpenFeign |
| Security | Keycloak + OAuth2/JWT |
| Database | MySQL |
| ORM | JPA/Hibernate |
| Build | Maven 3.9.x |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Monitoring | Actuator + Micrometer + Prometheus |
| Visualization | Grafana |
| Container Monitoring | cAdvisor |
| Kubernetes | Not currently implemented |

---

# 🌐 Main URLs

| Component | URL |
|---|---|
| API Gateway | `http://localhost:8080` |
| Eureka Dashboard | `http://localhost:8761` |
| Prometheus | `http://localhost:9090` |
| Prometheus Targets | `http://localhost:9090/targets` |
| Grafana | `http://localhost:3000` |
| Keycloak | `http://localhost:8571` |
| Account Actuator | `http://localhost:8081/actuator` |
| User Actuator | `http://localhost:8082/actuator` |
| Sequence Actuator | `http://localhost:8083/actuator` |
| Transaction Actuator | `http://localhost:8084/actuator` |
| Fund Transfer Actuator | `http://localhost:8085/actuator` |

---

# 🏁 Project Summary

This project demonstrates a complete **Spring Boot microservices banking backend** with:

- 7 application-level services/components
- Eureka service discovery
- Spring Cloud API Gateway
- OpenFeign service communication
- Keycloak identity management
- OAuth2/JWT integration
- Database-per-service architecture
- MySQL persistence
- Docker containerization
- Docker Compose orchestration
- Spring Boot Actuator
- Micrometer
- Prometheus monitoring
- Grafana dashboards
- cAdvisor container monitoring
- P50/P90/P95/P99 latency monitoring
- JVM, CPU, memory and GC monitoring
- HikariCP database pool monitoring
- Prometheus performance alerts
- Centralized exception handling
- Validation
- End-to-end banking flows

The overall architecture can be summarized as:

```text
                         CLIENT
                           │
                           ▼
                    ┌─────────────┐
                    │ API GATEWAY │
                    │    :8080    │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
          KEYCLOAK                   EUREKA
           :8571                     :8761
                                        │
         ┌──────────────┬───────────────┼──────────────┬──────────────┐
         ▼              ▼               ▼              ▼              ▼
      USER           ACCOUNT         SEQUENCE      TRANSACTION    FUND TRANSFER
     :8082            :8081           :8083           :8084           :8085
         │              │               │              │              │
         ▼              ▼               ▼              ▼              ▼
      MySQL           MySQL           MySQL          MySQL          MySQL

                              │
                              ▼
                  ┌─────────────────────────┐
                  │     OBSERVABILITY       │
                  │                         │
                  │ Actuator → Micrometer   │
                  │          ↓              │
                  │      Prometheus         │
                  │          ↓              │
                  │       Grafana            │
                  │                         │
                  │      cAdvisor            │
                  └─────────────────────────┘
```

---

## 👨‍💻 Project

**Spring Boot Microservices Banking Application**

Built to demonstrate practical implementation of:

**Microservices + Service Discovery + API Gateway + Inter-Service Communication + Security + Database-per-Service + Docker + Monitoring + Performance Engineering**

---

> **Note:** This README describes the implemented project architecture and functionality based on the provided project documentation. It intentionally does not claim Kubernetes, message queues, caching, config server, Alertmanager, or other components that are not part of the current implementation.
