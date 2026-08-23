# 🛡️ Security & Authentication Architecture Guide

This document provides an exhaustive, senior-engineer-level breakdown of the **Security, Authentication, and Authorization Architecture** implemented across the Spring Boot Microservices Banking Application. It includes internal system mechanics, JWT token lifecycles, configuration specifications, end-to-end sequences, Postman/cURL test flows, and production-hardening guidelines.

---

## 📋 Table of Contents

1. [Executive Summary & High-Level Architecture](#1-executive-summary--high-level-architecture)
2. [Identity & Access Management (IAM) — Keycloak Configuration](#2-identity--access-management-iam--keycloak-configuration)
3. [Component Security Mechanics](#3-component-security-mechanics)
   - [3.1 User Service & Keycloak Admin Client Integration](#31-user-service--keycloak-admin-client-integration)
   - [3.2 API Gateway as an OAuth2 / JWT Resource Server](#32-api-gateway-as-an-oauth2--jwt-resource-server)
   - [3.3 Downstream Microservice Isolation & Trust Model](#33-downstream-microservice-isolation--trust-model)
4. [User Lifecycle & Authentication State Machine](#4-user-lifecycle--authentication-state-machine)
5. [End-to-End Workflow & Sequence Diagrams](#5-end-to-end-workflow--sequence-diagrams)
6. [How to Check & Verify Authentication](#6-how-to-check--verify-authentication)
   - [6.1 Authentication Test Matrix & Scenarios](#61-authentication-test-matrix--scenarios)
   - [6.2 Step-by-Step Guide: How to Verify Authentication](#62-step-by-step-guide-how-to-verify-authentication)
7. [Complete Postman & cURL API Reference](#7-complete-postman--curl-api-reference)
   - [7.1 Postman Environment Setup](#71-postman-environment-setup)
   - [7.2 Automated Token Injection in Postman](#72-automated-token-injection-in-postman)
   - [7.3 Keycloak Authentication Requests](#73-keycloak-authentication-requests)
   - [7.4 User Service Endpoints](#74-user-service-endpoints)
   - [7.5 Account Service Endpoints](#75-account-service-endpoints)
   - [7.6 Transaction Service Endpoints](#76-transaction-service-endpoints)
   - [7.7 Fund Transfer Service Endpoints](#77-fund-transfer-service-endpoints)
   - [7.8 Sequence Generator Endpoints](#78-sequence-generator-endpoints)
8. [Security Assessment, Audit Findings & Hardening Recommendations](#8-security-assessment-audit-findings--hardening-recommendations)

---

## 1. Executive Summary & High-Level Architecture

The banking platform implements a **Centralized Identity & Perimeter-Secured Microservices Pattern**:

* **Identity Provider (IdP)**: [Keycloak](https://www.keycloak.org/) is the single source of truth for user identities, password hashing (PBKDF2/Argon2), credential storage, and JWT token issuance.
* **Perimeter Security**: [API-Gateway](file:///API-Gateway) (built on Spring Cloud Gateway & Spring WebFlux) acts as the entry point and OAuth2 Resource Server. It validates asymmetric cryptographic signatures on JSON Web Tokens (JWT) using Keycloak's JSON Web Key Set (JWKS).
* **Decoupled User Profiles**: [User-Service](file:///User-Service) synchronizes user identities between Keycloak and a local relational database (`user_service` MySQL schema), linking banking domain profile data to Keycloak's unique `authId` (UUID).
* **Internal Network Trust**: Downstream microservices (`Account-Service`, `Transaction-Service`, `Fund-Transfer`, `Sequence-Generator`) operate inside a secure internal network behind the API Gateway and Eureka Service Registry.

```
                                      ┌────────────────────────────────────────┐
                                      │           KEYCLOAK (IAM) :8571         │
                                      │  Realm: banking-service                │
                                      │  - Credential verification             │
                                      │  - Issues signed JWT Access Tokens     │
                                      │  - Exposes JWKS Public Keys (/certs)   │
                                      └───────────────────▲────────────────────┘
                                                          │
                    1. POST /protocol/openid-connect/token│ (Direct Access Grant)
                    2. Returns Signed Bearer JWT Token    │
                                                          │
┌─────────────────────────┐                               │
│       HTTP Client       ├───────────────────────────────┘
│  (Postman / Web / App)  │
└───────────┬─────────────┘
            │
            │ 3. API Request with Header: "Authorization: Bearer <JWT>"
            ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY :8080                                 │
│  Spring Cloud Gateway (Reactive WebFlux + OAuth2 Resource Server)            │
│  - Fetches and caches Keycloak JWKS public certs                             │
│  - Validates JWT signature, expiration (exp), issuer (iss)                   │
│  - Routes authorized traffic via Eureka service discovery                    │
└───────┬───────────────────────┬──────────────────────┬───────────────────────┘
        │ lb://user-service     │ lb://account-service │ lb://transaction-service
        ▼                       ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌────────────────────────┐
│   USER SERVICE   │   │ ACCOUNT SERVICE  │   │  TRANSACTION SERVICE   │
│      :8082       │   │      :8081       │   │         :8084          │
└────────┬─────────┘   └──────────────────┘   └────────────────────────┘
         │
         │ Keycloak Admin Client (client_credentials)
         ▼
┌──────────────────┐
│ KEYCLOAK REALM   │
│ User Management  │
└──────────────────┘
```

---

## 2. Identity & Access Management (IAM) — Keycloak Configuration

The system is configured around Keycloak running standalone or containerized on port `8571`.

### 2.1 Realm & Client Topology

| Entity | Value | Description |
| :--- | :--- | :--- |
| **Server URL** | `http://localhost:8571` | Keycloak server base URL |
| **Realm Name** | `banking-service` | Isolated tenant realm containing all banking domain identities and keys |
| **API Client** | `banking-service-client` | Client ID configured with **Direct Access Grants Enabled** for token requests via Postman and gateway authentication |
| **Client Secret** | `7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ` | Client secret for `banking-service-client` |
| **Service Admin Client** | `banking-service-api-client` | Client ID used by `User-Service` with `client_credentials` grant type and service account roles to manage users |
| **Admin Secret** | `ooZV25AjCo15w8A7Qum50VjrTbkie0EE` | Client secret used by `User-Service` Keycloak Admin SDK |

### 2.2 Keycloak OpenID Connect Endpoints

All OAuth2 / OIDC discovery endpoints are derived from the realm base URL:

* **Authorization Endpoint**:
  `http://localhost:8571/realms/banking-service/protocol/openid-connect/auth`
* **Token Endpoint**:
  `http://localhost:8571/realms/banking-service/protocol/openid-connect/token`
* **JWKS Certificates Endpoint (Public Keys)**:
  `http://localhost:8571/realms/banking-service/protocol/openid-connect/certs`
* **UserInfo Endpoint**:
  `http://localhost:8571/realms/banking-service/protocol/openid-connect/userinfo`

---

## 3. Component Security Mechanics

### 3.1 User Service & Keycloak Admin Client Integration

The `User-Service` acts as an administrative bridge between the banking application and Keycloak using the `org.keycloak:keycloak-admin-client` SDK.

#### 1. Configuration & Connection (`KeyCloakProperties.java` & `KeyCloakManager.java`)
`User-Service` initializes a singleton instance of the Keycloak client using the `client_credentials` grant flow:

```java
public Keycloak getKeycloakInstance() {
    if (keycloakInstance == null) {
        keycloakInstance = KeycloakBuilder.builder()
                .serverUrl(serverUrl)
                .realm(realm)
                .clientId(clientId)
                .clientSecret(clientSecret)
                .grantType("client_credentials")
                .build();
    }
    return keycloakInstance;
}
```

#### 2. Registration Flow (`UserServiceImpl.createUser`)
When a new customer registers:
1. `User-Service` queries Keycloak to verify if the email is already in use (`keycloakService.readUserByEmail`).
2. If available, a `UserRepresentation` is constructed with:
   - `username`: Email address
   - `email`: Email address
   - `enabled`: `false` *(Account cannot log in or generate tokens until approved)*
   - `emailVerified`: `false`
   - `credentials`: Non-temporary password string
3. `KeycloakService.createUser()` sends a REST request to Keycloak's Admin API (`POST /admin/realms/banking-service/users`).
4. Keycloak persists the user and returns HTTP `201 Created`.
5. `User-Service` queries Keycloak for the generated user ID (`authId` UUID) and saves the local entity in MySQL with status `PENDING`.

#### 3. Approval Flow (`UserServiceImpl.updateUserStatus`)
Banking compliance requires administrative verification before activating accounts:
1. An admin updates the user status to `APPROVED` (`PATCH /api/users/{id}`).
2. `User-Service` fetches the Keycloak user representation using `authId`.
3. Sets `enabled = true` and `emailVerified = true`.
4. Executes `keycloakService.updateUser(userRepresentation)`.
5. The customer is now activated in Keycloak and capable of acquiring OAuth2 tokens.

---

### 3.2 API Gateway as an OAuth2 / JWT Resource Server

The `API-Gateway` enforces token validation without maintaining session state.

#### 1. Dependencies (`API-Gateway/pom.xml`)
* `spring-boot-starter-oauth2-client`
* `spring-boot-starter-oauth2-resource-server`
* `spring-cloud-starter-gateway`

#### 2. Resource Server Configuration (`application.yml`)
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          jwk-set-uri: http://localhost:8571/realms/banking-service/protocol/openid-connect/certs
```

#### 3. Reactive Security Filter Chain (`SecurityConfig.java`)
```java
@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        http
            .authorizeExchange()
                // Public endpoint: Allow customer self-registration
                .pathMatchers("/api/users/register").permitAll()
                // All other endpoints
                .anyExchange().permitAll() // Note: In production, switch to .authenticated()
            .and()
                .csrf().disable()
                .oauth2Login()
            .and()
                .oauth2ResourceServer()
                .jwt(); // Validates cryptographic signatures against JWKS certs
        return http.build();
    }
}
```

#### How Token Verification Works at the Gateway:
1. The client supplies the header `Authorization: Bearer <JWT>`.
2. The Gateway extracts the JWT and inspects the `kid` (Key ID) header parameter.
3. The Gateway matches `kid` against the public keys cached from Keycloak's `jwk-set-uri`.
4. It cryptographically verifies the RSA-256 signature using Keycloak's public key.
5. It checks standard claims:
   - `exp`: Expiration timestamp (rejects expired tokens).
   - `nbf`: Not before timestamp.
   - `iss`: Issuer URI (must match the Keycloak realm).
6. If valid, the request is passed downstream to the appropriate microservice.

---

### 3.3 Downstream Microservice Isolation & Trust Model

In this architecture:
* Downstream services (`Account-Service`, `Transaction-Service`, `Fund-Transfer`, `Sequence-Generator`) sit behind the API Gateway on an internal network.
* Inter-service communication takes place over REST via **OpenFeign** clients registered with **Eureka Service Registry** (e.g., `Fund-Transfer` calling `Account-Service` and `Transaction-Service`).
* The Gateway acts as the security boundary, ensuring unauthenticated or invalid requests never penetrate into the microservice network.

---

## 4. User Lifecycle & Authentication State Machine

```
   [ Customer Registration ]
               │
               ▼
   Keycloak User Created (enabled: false)
   MySQL DB: Status = PENDING
               │
               ├──────────────────────────────────────────┐
               │                                          │
    Attempts Login prematurely                 Admin Approves User
               │                                          │
               ▼                                          ▼
   Keycloak Rejects Request                   Keycloak: enabled = true, emailVerified = true
   (400 Bad Request: "Account is disabled")   MySQL DB: Status = APPROVED
                                                          │
                                                          ▼
                                              Customer Logs in via Keycloak
                                                          │
                                                          ▼
                                              JWT Access Token Issued
                                                          │
                                                          ▼
                                              Authorized Banking Operations
```

---

## 5. End-to-End Workflow & Sequence Diagrams

### 5.1 Registration, Approval, and Login Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer / Admin
    participant Gateway as API Gateway (:8080)
    participant Keycloak as Keycloak IAM (:8571)
    participant UserService as User Service (:8082)
    participant DB as MySQL DB

    Note over Customer, DB: Phase 1: User Self-Registration
    Customer->>Gateway: POST /api/users/register (name, email, password)
    Gateway->>UserService: Forward to /api/users/register
    UserService->>Keycloak: Search user by email
    alt Email already exists
        UserService-->>Customer: 409 Conflict ("Email already registered")
    else Email available
        UserService->>Keycloak: POST /admin/realms/banking-service/users (enabled: false)
        Keycloak-->>UserService: 201 Created
        UserService->>Keycloak: GET /admin/.../users?email={email} (Fetch authId UUID)
        UserService->>DB: Save User (status: PENDING, authId: UUID)
        UserService-->>Customer: 200 OK ("User created successfully")
    end

    Note over Customer, DB: Phase 2: Administrative Approval
    Customer->>Gateway: PATCH /api/users/{userId} { "status": "APPROVED" }
    Gateway->>UserService: Forward status update
    UserService->>Keycloak: Update user (enabled: true, emailVerified: true)
    Keycloak-->>UserService: 204 No Content
    UserService->>DB: Update User status to APPROVED
    UserService-->>Customer: 200 OK ("User updated successfully")

    Note over Customer, Keycloak: Phase 3: Token Acquisition
    Customer->>Keycloak: POST /realms/banking-service/protocol/openid-connect/token<br/>(grant_type: password, username, password, client_id, client_secret)
    Keycloak-->>Customer: 200 OK { access_token: "eyJhbGciOi...", expires_in: 300, ... }

    Note over Customer, Gateway: Phase 4: Authenticated Request
    Customer->>Gateway: GET /accounts?accountNumber=0600140000001<br/>Header: Authorization: Bearer <access_token>
    Gateway->>Keycloak: Validate JWT signature against JWKS certs
    Gateway->>Gateway: Signature valid & not expired
    Gateway->>DB: Route request to Account Service & Return Data
    Gateway-->>Customer: 200 OK [ Account Details JSON ]
```

---

## 6. How to Check & Verify Authentication

Testing and verifying authentication ensures that only valid, active users with cryptographically signed tokens can access protected banking microservices.

### 6.1 Authentication Test Matrix & Scenarios

| Test Case | Request / Scenario | Credentials / Token | Expected Result | Why It Happens |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01: Valid Login** | `POST /protocol/openid-connect/token` | Approved user + valid password | `200 OK` + JWT access token | Credentials match and user `enabled: true` in Keycloak |
| **TC-02: Invalid Password** | `POST /protocol/openid-connect/token` | Valid username + wrong password | `400 Bad Request` (`invalid_grant`) | Keycloak password verification fails |
| **TC-03: Pending / Disabled User** | `POST /protocol/openid-connect/token` | Newly registered user (Pending) | `400 Bad Request` (`Account is disabled`) | User registered with `enabled: false` until admin approval |
| **TC-04: Authenticated API Call** | `GET /accounts?accountNumber=...` | Valid `Bearer <JWT>` | `200 OK` with account data | Gateway validates JWT against Keycloak JWKS certs |
| **TC-05: Missing Token (Unauthenticated)** | `GET /accounts?accountNumber=...` | No `Authorization` header | `401 Unauthorized` | Gateway rejects unauthenticated traffic on secured routes |
| **TC-06: Expired / Forged Token** | `GET /accounts?accountNumber=...` | Expired or tampered JWT string | `401 Unauthorized` (`Bearer error="invalid_token"`) | Cryptographic signature or expiration (`exp`) check fails |
| **TC-07: Public Endpoint** | `POST /api/users/register` | No token | `200 OK` / `201 Created` | Explicitly whitelisted via `.pathMatchers("/api/users/register").permitAll()` |

---

### 6.2 Step-by-Step Guide: How to Verify Authentication

#### Step 1: Test Login with a Newly Registered (Unapproved) User
1. Register a new user via `POST http://localhost:8080/api/users/register`.
2. Attempt to fetch a token from Keycloak (`POST http://localhost:8571/realms/banking-service/protocol/openid-connect/token`) using the new user's credentials.
3. **Verification**: Keycloak must reject the request with HTTP `400 Bad Request`:
   ```json
   {
     "error": "invalid_grant",
     "error_description": "Account is disabled"
   }
   ```

#### Step 2: Approve the User and Verify Token Issuance
1. As an admin, approve the user: `PATCH http://localhost:8080/api/users/{userId}` with `{ "status": "APPROVED" }`.
2. `User-Service` activates the account in Keycloak (`enabled: true`).
3. Re-run the token request in Postman.
4. **Verification**: Keycloak returns HTTP `200 OK` with a JSON payload containing `access_token` and `refresh_token`.

#### Step 3: Inspect and Decode the JWT Token
Copy the `access_token` value and paste it into [jwt.io](https://jwt.io) or decode it using base64 CLI tools.

* **JWT Header Inspection**:
  ```json
  {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "K_L9mP2q8v..."
  }
  ```
  *(Verify `alg` is `RS256` and `kid` matches one of Keycloak's keys at `http://localhost:8571/realms/banking-service/protocol/openid-connect/certs`)*

* **JWT Payload Claims Inspection**:
  ```json
  {
    "exp": 1724401500,
    "iat": 1724401200,
    "iss": "http://localhost:8571/realms/banking-service",
    "sub": "3f83737b-ec86-4f47-a8fe-3bcbe998797f",
    "preferred_username": "adamsanadi1234@gmail.com",
    "email": "adamsanadi1234@gmail.com",
    "azp": "banking-service-client"
  }
  ```
  *(Verify `iss` matches your realm URL and `exp` is in the future)*

#### Step 4: Verify Gateway Signature Validation
1. Send a request to any protected route (e.g. `GET http://localhost:8080/accounts/1`) with the header:
   ```http
   Authorization: Bearer <YOUR_ACCESS_TOKEN>
   ```
2. **Verification**: The API Gateway verifies the token signature against Keycloak JWKS and routes the request, returning `200 OK`.
3. Modify even a single character in the token payload or signature, and re-send.
4. **Verification**: The API Gateway immediately blocks the request with `401 Unauthorized`.

---

## 7. Complete Postman & cURL API Reference

### 7.1 Postman Environment Setup

Create a new Environment in Postman named **`Banking Microservices (Local)`** with the following key-value pairs:

| Variable Name | Initial Value | Current Value | Description |
| :--- | :--- | :--- | :--- |
| `base_url` | `http://localhost:8080` | `http://localhost:8080` | API Gateway base URL |
| `keycloak_host` | `http://localhost:8571` | `http://localhost:8571` | Keycloak IAM server URL |
| `keycloak_realm` | `banking-service` | `banking-service` | Keycloak realm name |
| `keycloak_client_id` | `banking-service-client` | `banking-service-client` | Postman / Gateway Client ID |
| `keycloak_client_secret` | `7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ` | `7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ` | Client secret key |
| `keycloak_username` | `super-user` | `super-user` | Username / email for login |
| `keycloak_password` | `atharva61` | `atharva61` | Password for login |
| `token` | *(leave empty)* | *(auto-populated)* | JWT Bearer access token |

---

### 7.2 Automated Token Injection in Postman

To avoid manually copying and pasting tokens across requests, add this script under the **Tests** tab of your **Get Token** request in Postman:

```javascript
// Postman Tests Script: Auto-save Token
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("token", jsonData.access_token);
    console.log("Access token successfully saved to environment variable 'token'");
} else {
    console.error("Failed to acquire token: " + pm.response.text());
}
```

Now, in all other requests, configure **Authorization**:
* **Type**: `Bearer Token`
* **Token**: `{{token}}`

---

### 7.3 Keycloak Authentication Requests

#### 1. Obtain JWT Access Token (Direct Access Grant)
* **Method**: `POST`
* **URL**: `{{keycloak_host}}/realms/{{keycloak_realm}}/protocol/openid-connect/token`
* **Body Type**: `x-www-form-urlencoded`

| Key | Value | Description |
| :--- | :--- | :--- |
| `grant_type` | `password` | Direct password grant flow |
| `client_id` | `{{keycloak_client_id}}` | OAuth2 Client ID |
| `client_secret` | `{{keycloak_client_secret}}` | OAuth2 Client Secret |
| `username` | `{{keycloak_username}}` | User login username/email |
| `password` | `{{keycloak_password}}` | User login password |
| `scope` | `openid offline_access` | Scopes requested |

**Postman Request JSON:**
```json
{
  "name": "Get JWT Access Token",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/x-www-form-urlencoded"
      }
    ],
    "body": {
      "mode": "urlencoded",
      "urlencoded": [
        { "key": "grant_type", "value": "password", "type": "text" },
        { "key": "client_id", "value": "{{keycloak_client_id}}", "type": "text" },
        { "key": "client_secret", "value": "{{keycloak_client_secret}}", "type": "text" },
        { "key": "username", "value": "{{keycloak_username}}", "type": "text" },
        { "key": "password", "value": "{{keycloak_password}}", "type": "text" },
        { "key": "scope", "value": "openid offline_access", "type": "text" }
      ]
    },
    "url": {
      "raw": "{{keycloak_host}}/realms/{{keycloak_realm}}/protocol/openid-connect/token",
      "host": ["{{keycloak_host}}"],
      "path": ["realms", "{{keycloak_realm}}", "protocol", "openid-connect", "token"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8571/realms/banking-service/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=banking-service-client" \
  -d "client_secret=7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ" \
  -d "username=super-user" \
  -d "password=atharva61" \
  -d "scope=openid offline_access"
```

**Expected Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "token_type": "Bearer",
  "not-before-policy": 0,
  "session_state": "4020c029-4567-4b12-9c11-7890abcdef12",
  "scope": "openid profile email offline_access"
}
```

---

### 7.4 User Service Endpoints

#### 1. Register New User (Public Endpoint)
* **Method**: `POST`
* **URL**: `{{base_url}}/api/users/register`
* **Headers**: `Content-Type: application/json`
* **Auth**: None (Public)

**Body (Raw JSON):**
```json
{
  "firstName": "Adam",
  "lastName": "Sanadi",
  "emailId": "adamsanadi1234@gmail.com",
  "contactNumber": "8547159267",
  "password": "Adam@1234"
}
```

**Postman Request JSON:**
```json
{
  "name": "Register User",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"firstName\": \"Adam\",\n    \"lastName\": \"Sanadi\",\n    \"emailId\": \"adamsanadi1234@gmail.com\",\n    \"contactNumber\": \"8547159267\",\n    \"password\": \"Adam@1234\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/api/users/register",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "register"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Adam",
    "lastName": "Sanadi",
    "emailId": "adamsanadi1234@gmail.com",
    "contactNumber": "8547159267",
    "password": "Adam@1234"
  }'
```

**Expected Response (`200 OK`):**
```json
{
  "responseCode": "200",
  "responseMessage": "User created successfully"
}
```

---

#### 2. Update User Status (Admin Approval)
* **Method**: `PATCH`
* **URL**: `{{base_url}}/api/users/1`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON):**
```json
{
  "status": "APPROVED"
}
```

**Postman Request JSON:**
```json
{
  "name": "Update User Status",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "PATCH",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"status\": \"APPROVED\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/api/users/1",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "1"]
    }
  }
}
```

**cURL:**
```bash
curl -X PATCH http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "status": "APPROVED"
  }'
```

**Expected Response (`200 OK`):**
```json
{
  "responseCode": "200",
  "responseMessage": "User updated successfully"
}
```

---

#### 3. Update User Profile Details
* **Method**: `PUT`
* **URL**: `{{base_url}}/api/users/1`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON):**
```json
{
  "firstName": "Kishan",
  "lastName": "Kulkarni",
  "contactNo": "9562148579",
  "address": "Behind Prasad Lodge, Extension Masari",
  "gender": "Male",
  "occupation": "Student",
  "martialStatus": "Single",
  "nationality": "Indian"
}
```

**Postman Request JSON:**
```json
{
  "name": "Update User Details",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "PUT",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"firstName\": \"Kishan\",\n    \"lastName\": \"Kulkarni\",\n    \"contactNo\": \"9562148579\",\n    \"address\": \"Behind Prasad Lodge, Extension Masari\",\n    \"gender\": \"Male\",\n    \"occupation\": \"Student\",\n    \"martialStatus\": \"Single\",\n    \"nationality\": \"Indian\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/api/users/1",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "1"]
    }
  }
}
```

**cURL:**
```bash
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "firstName": "Kishan",
    "lastName": "Kulkarni",
    "contactNo": "9562148579",
    "address": "Behind Prasad Lodge, Extension Masari",
    "gender": "Male",
    "occupation": "Student",
    "martialStatus": "Single",
    "nationality": "Indian"
  }'
```

**Expected Response (`200 OK`):**
```json
{
  "responseCode": "200",
  "responseMessage": "User details updated successfully"
}
```

---

#### 4. Read User by ID
* **Method**: `GET`
* **URL**: `{{base_url}}/api/users/1`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read User by ID",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/api/users/1",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "1"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/api/users/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (`200 OK`):**
```json
{
  "userId": 1,
  "firstName": "Adam",
  "lastName": "Sanadi",
  "emailId": "adamsanadi1234@gmail.com",
  "contactNumber": "8547159267",
  "status": "APPROVED",
  "authId": "3f83737b-ec86-4f47-a8fe-3bcbe998797f"
}
```

---

#### 5. Read All Users
* **Method**: `GET`
* **URL**: `{{base_url}}/api/users`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read All Users",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/api/users",
      "host": ["{{base_url}}"],
      "path": ["api", "users"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/api/users \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

#### 6. Read User by Keycloak Auth ID
* **Method**: `GET`
* **URL**: `{{base_url}}/api/users/auth/3f83737b-ec86-4f47-a8fe-3bcbe998797f`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read User by Auth ID",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/api/users/auth/3f83737b-ec86-4f47-a8fe-3bcbe998797f",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "auth", "3f83737b-ec86-4f47-a8fe-3bcbe998797f"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/api/users/auth/3f83737b-ec86-4f47-a8fe-3bcbe998797f \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

#### 7. Read User by Account Number
* **Method**: `GET`
* **URL**: `{{base_url}}/api/users/accounts/0600140000001`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read User by Account Number",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/api/users/accounts/0600140000001",
      "host": ["{{base_url}}"],
      "path": ["api", "users", "accounts", "0600140000001"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/api/users/accounts/0600140000001 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### 7.5 Account Service Endpoints

#### 1. Create Bank Account
* **Method**: `POST`
* **URL**: `{{base_url}}/accounts`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON):**
```json
{
  "accountType": "SAVINGS_ACCOUNT",
  "userId": "1"
}
```

**Postman Request JSON:**
```json
{
  "name": "Create Bank Account",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"accountType\": \"SAVINGS_ACCOUNT\",\n    \"userId\": \"1\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/accounts",
      "host": ["{{base_url}}"],
      "path": ["accounts"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8080/accounts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "accountType": "SAVINGS_ACCOUNT",
    "userId": "1"
  }'
```

**Expected Response (`201 Created`):**
```json
{
  "responseCode": "201",
  "responseMessage": "Account created successfully with Account Number 0600140000001"
}
```

---

#### 2. Read Account by Account Number
* **Method**: `GET`
* **URL**: `{{base_url}}/accounts?accountNumber=0600140000001`
* **Params**: `accountNumber` = `0600140000001`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read Account by Account Number",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/accounts?accountNumber=0600140000001",
      "host": ["{{base_url}}"],
      "path": ["accounts"],
      "query": [
        {
          "key": "accountNumber",
          "value": "0600140000001"
        }
      ]
    }
  }
}
```

**cURL:**
```bash
curl -X GET "http://localhost:8080/accounts?accountNumber=0600140000001" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (`200 OK`):**
```json
{
  "accountNumber": "0600140000001",
  "accountType": "SAVINGS_ACCOUNT",
  "accountStatus": "PENDING",
  "availableBalance": 0.0,
  "userId": 1
}
```

---

#### 3. Update Account Status (Activate Account)
* **Method**: `PATCH`
* **URL**: `{{base_url}}/accounts?accountNumber=0600140000001`
* **Params**: `accountNumber` = `0600140000001`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON):**
```json
{
  "accountStatus": "ACTIVE"
}
```

**Postman Request JSON:**
```json
{
  "name": "Update Account Status",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "PATCH",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"accountStatus\": \"ACTIVE\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/accounts?accountNumber=0600140000001",
      "host": ["{{base_url}}"],
      "path": ["accounts"],
      "query": [
        {
          "key": "accountNumber",
          "value": "0600140000001"
        }
      ]
    }
  }
}
```

**cURL:**
```bash
curl -X PATCH "http://localhost:8080/accounts?accountNumber=0600140000001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "accountStatus": "ACTIVE"
  }'
```

---

#### 4. Read Account by User ID
* **Method**: `GET`
* **URL**: `{{base_url}}/accounts/1`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Read Account by User ID",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/accounts/1",
      "host": ["{{base_url}}"],
      "path": ["accounts", "1"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/accounts/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

#### 5. Close Account
* **Method**: `PUT`
* **URL**: `{{base_url}}/accounts/closure?accountNumber=0600140000001`
* **Params**: `accountNumber` = `0600140000001`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Close Account",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "PUT",
    "header": [],
    "url": {
      "raw": "{{base_url}}/accounts/closure?accountNumber=0600140000001",
      "host": ["{{base_url}}"],
      "path": ["accounts", "closure"],
      "query": [
        {
          "key": "accountNumber",
          "value": "0600140000001"
        }
      ]
    }
  }
}
```

**cURL:**
```bash
curl -X PUT "http://localhost:8080/accounts/closure?accountNumber=0600140000001" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### 7.6 Transaction Service Endpoints

#### 1. Make a Transaction (Deposit / Withdrawal)
* **Method**: `POST`
* **URL**: `{{base_url}}/transactions`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON - Deposit):**
```json
{
  "accountId": "0600140000001",
  "transactionType": "DEPOSIT",
  "amount": 1000.00,
  "description": "Initial account deposit"
}
```

**Postman Request JSON:**
```json
{
  "name": "Make Transaction (Deposit)",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"accountId\": \"0600140000001\",\n    \"transactionType\": \"DEPOSIT\",\n    \"amount\": 1000.00,\n    \"description\": \"Initial account deposit\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/transactions",
      "host": ["{{base_url}}"],
      "path": ["transactions"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8080/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "accountId": "0600140000001",
    "transactionType": "DEPOSIT",
    "amount": "1000",
    "description": "Initial account deposit"
  }'
```

**Expected Response (`200 OK`):**
```json
{
  "responseCode": "200",
  "responseMessage": "Transaction executed successfully with Reference 0671cbe4-fefb-4a60-9e55-93bfb1d5895c"
}
```

---

#### 2. Get All Transactions for an Account
* **Method**: `GET`
* **URL**: `{{base_url}}/transactions?accountId=0600140000001`
* **Params**: `accountId` = `0600140000001`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Get Transactions for Account",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/transactions?accountId=0600140000001",
      "host": ["{{base_url}}"],
      "path": ["transactions"],
      "query": [
        {
          "key": "accountId",
          "value": "0600140000001"
        }
      ]
    }
  }
}
```

**cURL:**
```bash
curl -X GET "http://localhost:8080/transactions?accountId=0600140000001" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

#### 3. Get Transaction by Reference ID
* **Method**: `GET`
* **URL**: `{{base_url}}/transactions/0671cbe4-fefb-4a60-9e55-93bfb1d5895c`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Get Transaction by Reference ID",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/transactions/0671cbe4-fefb-4a60-9e55-93bfb1d5895c",
      "host": ["{{base_url}}"],
      "path": ["transactions", "0671cbe4-fefb-4a60-9e55-93bfb1d5895c"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/transactions/0671cbe4-fefb-4a60-9e55-93bfb1d5895c \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### 7.7 Fund Transfer Service Endpoints

#### 1. Transfer Funds Between Accounts
* **Method**: `POST`
* **URL**: `{{base_url}}/fund-transfers`
* **Headers**: `Content-Type: application/json`, `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Body (Raw JSON):**
```json
{
  "fromAccount": "0600140000001",
  "toAccount": "0600140000002",
  "amount": 500.00
}
```

**Postman Request JSON:**
```json
{
  "name": "Fund Transfer",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n    \"fromAccount\": \"0600140000001\",\n    \"toAccount\": \"0600140000002\",\n    \"amount\": \"500\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{base_url}}/fund-transfers",
      "host": ["{{base_url}}"],
      "path": ["fund-transfers"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8080/fund-transfers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "fromAccount": "0600140000001",
    "toAccount": "0600140000002",
    "amount": "500"
  }'
```

**Expected Response (`200 OK`):**
```json
{
  "responseCode": "200",
  "responseMessage": "Fund transfer completed successfully with Reference 950e07f5-09ce-4fee-be66-3377233458ad"
}
```

---

#### 2. Get Transfer Details by Reference ID
* **Method**: `GET`
* **URL**: `{{base_url}}/fund-transfers/950e07f5-09ce-4fee-be66-3377233458ad`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Get Transfer Details by Reference ID",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/fund-transfers/950e07f5-09ce-4fee-be66-3377233458ad",
      "host": ["{{base_url}}"],
      "path": ["fund-transfers", "950e07f5-09ce-4fee-be66-3377233458ad"]
    }
  }
}
```

**cURL:**
```bash
curl -X GET http://localhost:8080/fund-transfers/950e07f5-09ce-4fee-be66-3377233458ad \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

#### 3. Get All Fund Transfers from an Account
* **Method**: `GET`
* **URL**: `{{base_url}}/fund-transfers?accountId=0600140000001`
* **Params**: `accountId` = `0600140000001`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Get All Fund Transfers for Account",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{base_url}}/fund-transfers?accountId=0600140000001",
      "host": ["{{base_url}}"],
      "path": ["fund-transfers"],
      "query": [
        {
          "key": "accountId",
          "value": "0600140000001"
        }
      ]
    }
  }
}
```

**cURL:**
```bash
curl -X GET "http://localhost:8080/fund-transfers?accountId=0600140000001" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### 7.8 Sequence Generator Endpoints

#### Generate Account Number Sequence (Internal Service)
* **Method**: `POST`
* **URL**: `{{base_url}}/sequence`
* **Headers**: `Authorization: Bearer {{token}}`
* **Auth**: Bearer Token `{{token}}`

**Postman Request JSON:**
```json
{
  "name": "Generate Account Number Sequence",
  "request": {
    "auth": {
      "type": "bearer",
      "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
    },
    "method": "POST",
    "header": [],
    "url": {
      "raw": "{{base_url}}/sequence",
      "host": ["{{base_url}}"],
      "path": ["sequence"]
    }
  }
}
```

**cURL:**
```bash
curl -X POST http://localhost:8080/sequence \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (`200 OK`):**
```json
{
  "accountNumber": "0600140000006"
}
```

---

## 8. Security Assessment, Audit Findings & Hardening Recommendations

As a Senior Backend Engineer reviewing this system, the following audit items and architectural hardening recommendations must be noted for enterprise production deployments:

### 8.1 Immediate Code Hardening: Gateway Authorization Enforcement

> [!WARNING]
> In [`API-Gateway/src/main/java/org/training/api/gateway/config/SecurityConfig.java`](file:///API-Gateway/src/main/java/org/training/api/gateway/config/SecurityConfig.java#L20-L28), the configuration currently contains `.anyExchange().permitAll()`. While the OAuth2 Resource Server and JWT decoder are fully active, all requests are permitted through for local development convenience.

#### Production Remediation:
Update `SecurityConfig.java` to enforce authentication across all routes while whitelisting only public endpoints:

```java
@Bean
public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
    http
        .csrf().disable()
        .authorizeExchange()
            // Public endpoints (Registration & Actuator Health)
            .pathMatchers("/api/users/register").permitAll()
            .pathMatchers("/actuator/health", "/actuator/info", "/actuator/prometheus").permitAll()
            
            // Role-based restrictions (Example)
            .pathMatchers(HttpMethod.PATCH, "/api/users/**").hasAuthority("SCOPE_admin")
            
            // Enforce JWT authentication on every other endpoint
            .anyExchange().authenticated()
        .and()
        .oauth2ResourceServer()
            .jwt();

    return http.build();
}
```

---

### 8.2 Secrets & Credentials Management

* **Current State**: Hardcoded client secrets (e.g., `7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ`, `ooZV25AjCo15w8A7Qum50VjrTbkie0EE`) and database credentials exist in `application.yml` and Postman collections.
* **Production Recommendation**:
  1. Externalize all secrets using environment variables or a secret store like **HashiCorp Vault** or **AWS Secrets Manager**.
  2. Use Spring Cloud Vault or Kubernetes Secrets injection (`${KEYCLOAK_CLIENT_SECRET}`).

---

### 8.3 Inter-Service Token Propagation (Zero-Trust Model)

* **Current State**: Once past the API Gateway, inter-service Feign calls do not carry the original caller's JWT token.
* **Production Recommendation**:
  Implement a Feign `RequestInterceptor` in downstream services to forward the `Authorization` header:

```java
@Configuration
public class FeignClientSecurityConfig {

    @Bean
    public RequestInterceptor requestInterceptor() {
        return requestTemplate -> {
            ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes != null) {
                String authorization = attributes.getRequest().getHeader(HttpHeaders.AUTHORIZATION);
                if (authorization != null) {
                    requestTemplate.header(HttpHeaders.AUTHORIZATION, authorization);
                }
            }
        };
    }
}
```

---

### 8.4 Fine-Grained Role-Based Access Control (RBAC)

* **Recommendation**: Map Keycloak Realm Roles (`ROLE_CUSTOMER`, `ROLE_TELLER`, `ROLE_ADMIN`) into Spring Security authorities.
* Extract realm roles from JWT claims (`realm_access.roles`) using a custom `ReactiveJwtAuthenticationConverter` in the API Gateway or individual services to restrict endpoints such as Account Closure or User Approvals strictly to administrative users.

---

### 8.5 Defense in Depth & Network Security

1. **TLS / HTTPS Everywhere**: Terminate TLS at the reverse proxy / ingress controller, and enforce mTLS (mutual TLS) between microservices.
2. **Rate Limiting**: Enable Spring Cloud Gateway's `RequestRateLimiter` filter using Redis (`RedisRateLimiter`) on login and transfer endpoints to protect against brute-force and DDoS attacks.
3. **CORS Configuration**: Restrict allowed origins in the Gateway to trusted front-end domains instead of open wildcard origins.
