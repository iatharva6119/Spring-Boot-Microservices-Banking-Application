# CURRENT_PROJECT_ERROR_ANALYSIS

## 1. Executive Summary

- **Total compilation errors**: ~50+ (across 4 microservices during Maven build, driven primarily by Lombok)
- **Total warnings**: 3 (Lombok `callSuper`, 1 unused import)
- **Services affected**: Account-Service, User-Service, Transaction-Service, Fund-Transfer

## 2. Error-by-Error Analysis

| File | Line | Error | Root Cause | Correct Fix |
|---|---|---|---|---|
| `AccountClosingException.java` | 6 | `GlobalErrorCode cannot be resolved` (IDE) | IDE sync issue due to Maven build failing on Lombok + JDK 24. | Refresh Maven project after fixing Lombok version. |
| `AccountStatusException.java` | 5 | `GlobalErrorCode cannot be resolved` (IDE) | Incorrect argument order in `super(errorMessage, errorCode)`. `GlobalException` expects `(errorCode, errorMessage)`. | Swap arguments in `super()`. |
| `ResourceConflict.java` | 6, 10 | `GlobalErrorCode cannot be resolved` (IDE) | Incorrect argument order in `super()`. | Swap arguments in `super()`. |
| `ResourceNotFound.java` | 6, 10 | `GlobalErrorCode cannot be resolved` (IDE) | Incorrect argument order in `super()`. | Swap arguments in `super()`. |
| `InSufficientFunds.java` | 5, 9 | `GlobalErrorCode cannot be resolved` (IDE) | Incorrect argument order in `super()`. | Swap arguments in `super()`. |
| `GlobalExceptionHandler.java` | 38 | `ErrorResponse cannot be resolved` (IDE) | IDE sync issue (Lombok failure prevents builder/constructor generation). | Refresh Maven project after fixing Lombok. |
| `TransactionService.java` | 7 | `TransactionResponse cannot be resolved` | IDE sync issue (Lombok failure). Class exists in correct package. | Refresh Maven project after fixing Lombok. |
| `UserService.java` | 8 | `UserDto cannot be resolved` | IDE sync issue (Lombok failure). Class exists in correct package. | Refresh Maven project after fixing Lombok. |
| `UserMapper.java` | 22-40 | `cannot find symbol getUserProfileDto()` | Lombok is failing to generate getters/setters in `User-Service` due to JDK 24 incompatibility. | Upgrade Lombok to `1.18.36`. |
| `pom.xml` (Account-Service) | N/A | `Project configuration is not up-to-date` | IDE requires project update. Maven build fails with `TypeTag :: UNKNOWN` due to Lombok vs Java 24. | Upgrade Lombok to `1.18.36` in all POMs. |

## 3. Missing Classes Analysis

- **`GlobalErrorCode`**: 
  - **Exists in repo?** Yes. 
  - **Where?** `Account-Service/src/main/java/org/training/account/service/exception/GlobalErrorCode.java` (also in other services).
  - **Correct package?** Yes, `org.training.account.service.exception`.
  - **Action**: Fix argument order in exception classes calling `super()`.

- **`ErrorResponse`**:
  - **Exists in repo?** Yes.
  - **Where?** `Account-Service/src/main/java/org/training/account/service/exception/ErrorResponse.java` (also in other services).
  - **Correct package?** Yes.
  - **Action**: No code changes needed. It is a Lombok compilation issue masking it.

- **`TransactionResponse`**:
  - **Exists in repo?** Yes.
  - **Where?** `Account-Service/src/main/java/org/training/account/service/model/dto/external/TransactionResponse.java`.
  - **Correct package?** Yes.
  - **Action**: No code changes needed. It is a Lombok compilation issue masking it.

- **`UserDto`**:
  - **Exists in repo?** Yes.
  - **Where?** `Account-Service/src/main/java/org/training/account/service/model/dto/external/UserDto.java`.
  - **Correct package?** Yes.
  - **Action**: No code changes needed.

> **Note**: I will **NOT** create duplicate DTOs, as they already exist in the correct locations for Account-Service.

## 4. Dependency Analysis

- **Account-Service dependencies**: Uses Feign clients to communicate with Transaction-Service and User-Service.
- **DTO Sharing Approach**: The architecture currently duplicates DTOs across microservices (e.g., `UserDto` in User-Service and `UserDto` in Account-Service's `external` package). This is a valid microservices pattern (Loose Coupling) to avoid shared library dependencies.
- **Root Problem**: The environment is running JDK 24, but the POMs either rely on Spring Boot's default Lombok (`1.18.28`) or specify `1.18.32`. Both versions fail to compile on JDK 24 with `com.sun.tools.javac.code.TypeTag :: UNKNOWN`.

## 5. Proposed Change Plan

### Global Dependencies (All Services)
- **MODIFY**: `Account-Service/pom.xml`, `User-Service/pom.xml`, `Transaction-Service/pom.xml`, `Fund-Transfer/pom.xml`
  - **Reason**: Upgrade `lombok` version to `1.18.36` to fix `TypeTag :: UNKNOWN` and `cannot find symbol` errors caused by JDK 24 compilation failures.

### Account-Service
- **MODIFY**: `AccountStatusException.java`
  - **Reason**: Swap `super(errorMessage, GlobalErrorCode.BAD_REQUEST)` to `super(GlobalErrorCode.BAD_REQUEST, errorMessage)`.
- **MODIFY**: `ResourceConflict.java`
  - **Reason**: Swap arguments in `super()`.
- **MODIFY**: `ResourceNotFound.java`
  - **Reason**: Swap arguments in `super()`.
- **MODIFY**: `InSufficientFunds.java`
  - **Reason**: Swap arguments in `super()`.

### User-Service
- **MODIFY**: `GlobalException.java`
  - **Reason**: Add `@EqualsAndHashCode(callSuper = true)` to fix Lombok warning.

### Transaction-Service
- **MODIFY**: `GlobalException.java`
  - **Reason**: Add `@EqualsAndHashCode(callSuper = true)` to fix Lombok warning.
- **MODIFY**: `TransactionDto.java`
  - **Reason**: Remove unused import `org.training.transactions.model.TransactionType`.

### Fund-Transfer
- **MODIFY**: `GlobalException.java`
  - **Reason**: Add `@EqualsAndHashCode(callSuper = true)` to fix Lombok warning.
