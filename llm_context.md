# Project Files Detailed Information

## 1. docker-compose.yml
```yaml
version: '3.8'

services:
  service-registry:
    build:
      context: ./Service-Registry
    container_name: service-registry
    ports:
      - "8761:8761"
    networks:
      - banking-network

  api-gateway:
    build:
      context: ./API-Gateway
    container_name: api-gateway
    ports:
      - "8080:8080"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - APP_CONFIG_KEYCLOAK_URL=http://host.docker.internal:8571/
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  user-service:
    build:
      context: ./User-Service
    container_name: user-service
    ports:
      - "8082:8082"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - MYSQL_HOST=host.docker.internal
      - APP_CONFIG_KEYCLOAK_SERVER_URL=http://host.docker.internal:8571
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  account-service:
    build:
      context: ./Account-Service
    container_name: account-service
    ports:
      - "8081:8081"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/account_service
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  transaction-service:
    build:
      context: ./Transaction-Service
    container_name: transaction-service
    ports:
      - "8084:8084"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/transaction_service
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  fund-transfer:
    build:
      context: ./Fund-Transfer
    container_name: fund-transfer
    ports:
      - "8085:8085"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/fund_transfer_service
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  sequence-generator:
    build:
      context: ./Sequence-Generator
    container_name: sequence-generator
    ports:
      - "8083:8083"
    environment:
      - EUREKA_CLIENT_SERVICEURL_DEFAULTZONE=http://service-registry:8761/eureka
      - SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/sequence_generator
      - MANAGEMENT_METRICS_DISTRIBUTION_PERCENTILESHISTOGRAM_HTTP_SERVER_REQUESTS=true
    networks:
      - banking-network
    depends_on:
      - service-registry

  # ==========================================================
  # Performance Engineering Monitoring Stack
  # Added as an additional layer — no existing services changed
  # ==========================================================

  # ----------------------------------------------------------
  # Prometheus — Metrics collection and storage
  # UI:  http://localhost:9090
  # ----------------------------------------------------------
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - banking-network
    depends_on:
      - service-registry
      - api-gateway
      - user-service
      - account-service
      - transaction-service
      - fund-transfer
      - sequence-generator
    restart: unless-stopped

  # ----------------------------------------------------------
  # Grafana — Metrics visualization and dashboards
  # UI:       http://localhost:3000  (admin / admin)
  # ----------------------------------------------------------
  grafana:
    image: grafana/grafana:10.1.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/banking-performance.json
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources:ro
      - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro
    networks:
      - banking-network
    depends_on:
      - prometheus
    restart: unless-stopped



networks:
  banking-network:
    driver: bridge

volumes:
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
```

## 2. API-Gateway/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>apigateway</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>API Gateway</name>
    <description>API Gateway</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-gateway</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-client</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>
    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

## 3. Account-Service/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.15</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>accountService</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>Account Service</name>
    <description>Account Service</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

## 4. User-Service/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>userservice</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>User Service</name>
    <description>User Service</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
            <exclusions>
                <exclusion>
                    <groupId>javax.ws.rs</groupId>
                    <artifactId>jsr311-api</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <!-- https://mvnrepository.com/artifact/org.keycloak/keycloak-admin-client -->
        <dependency>
            <groupId>org.keycloak</groupId>
            <artifactId>keycloak-admin-client</artifactId>
            <version>21.0.1</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>
        <dependency>
            <groupId>org.modelmapper</groupId>
            <artifactId>modelmapper</artifactId>
            <version>3.1.1</version>
        </dependency>

    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

## 5. Transaction-Service/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.15</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>transactions</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>Transaction Service</name>
    <description>Transaction Service</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

## 6. Fund-Transfer/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>fundtransfer</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>Fund Transfer</name>
    <description>Fund Transfer</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>
    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

## 7. Sequence-Generator/pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.15</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>org.training</groupId>
    <artifactId>sequencegenerator</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>Sequence Generator</name>
    <description>Sequence Generator</description>
    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2021.0.8</spring-cloud.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <!-- Micrometer Prometheus Registry — for /actuator/prometheus endpoint -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

    </dependencies>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

## 8. API-Gateway SecurityConfig.java
```java
package org.training.api.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        http
                .authorizeExchange()
                //ALLOWING REGISTER API FOR DIRECT ACCESS
                .pathMatchers("/api/users/register").permitAll()

                //.anyExchange().permitAll()
                //ALL OTHER APIS ARE AUTHENTICATED
                .anyExchange().authenticated()
                .and()
                .csrf().disable()
                .oauth2Login()
                .and()
                .oauth2ResourceServer()
                .jwt();
        return http.build();
    }
}
```

## 9. Feign client classes - AccountService (User-Service)
```java
package org.training.user.service.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.cloud.openfeign.FeignClientProperties;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.training.user.service.model.external.Account;

@FeignClient(name = "account-service", configuration = FeignClientProperties.FeignClientConfiguration.class)
public interface AccountService {

    /**
     * Retrieves an account by its account number.
     *
     * @param  accountNumber  the account number to search for
     * @return                the ResponseEntity containing the account
     */
    @GetMapping("/accounts")
    ResponseEntity<Account> readByAccountNumber(@RequestParam String accountNumber);
}
```

## 9. Feign client classes - AccountService (Transaction-Service)
```java
package org.training.transactions.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.training.transactions.configuration.FeignClientConfiguration;
import org.training.transactions.model.external.Account;
import org.training.transactions.model.response.Response;

@FeignClient(name = "account-service", configuration = FeignClientConfiguration.class)
public interface AccountService {

    /**
     * Retrieves an account by account number.
     *
     * @param accountNumber The account number.
     * @return The account matching the account number.
     */
    @GetMapping("/accounts")
    ResponseEntity<Account> readByAccountNumber(@RequestParam String accountNumber);

    /**
     * Update an account with the given account number.
     *
     * @param accountNumber The account number of the account to be updated.
     * @param account The updated account information.
     * @return The response entity containing the response.
     */
    @PutMapping("/accounts")
    ResponseEntity<Response> updateAccount(@RequestParam String accountNumber, @RequestBody Account account);
}
```

## 9. Feign client classes - AccountService (Fund-Transfer)
```java
package org.training.fundtransfer.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.training.fundtransfer.configuration.FeignClientConfiguration;
import org.training.fundtransfer.model.dto.Account;
import org.training.fundtransfer.model.dto.response.Response;

@FeignClient(name = "account-service", configuration = FeignClientConfiguration.class)
public interface AccountService {

    /**
     * Retrieves an account by account number.
     *
     * @param accountNumber The account number to search for.
     * @return The account matching the account number.
     */
    @GetMapping("/accounts")
    ResponseEntity<Account> readByAccountNumber(@RequestParam String accountNumber);

    /**
     * Updates an account with the given account number.
     *
     * @param accountNumber The account number of the account to be updated.
     * @param account The updated account details.
     * @return The response entity containing the response.
     */
    @PutMapping("/accounts")
    ResponseEntity<Response> updateAccount(@RequestParam String accountNumber, @RequestBody Account account);
}
```

## 9. Feign client classes - TransactionService (Fund-Transfer)
```java
package org.training.fundtransfer.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.training.fundtransfer.configuration.FeignClientConfiguration;
import org.training.fundtransfer.model.dto.Transaction;
import org.training.fundtransfer.model.dto.response.Response;

import java.util.List;

@FeignClient(name = "transaction-service", configuration = FeignClientConfiguration.class)
public interface TransactionService {

    /**
     * Endpoint to make a transaction.
     *
     * @param transaction The transaction object containing the details of the transaction.
     * @return The ResponseEntity containing the response of the transaction.
     */
    @PostMapping("/transactions")
    ResponseEntity<Response> makeTransaction(@RequestBody Transaction transaction);

    /**
     * Make internal transactions.
     *
     * @param transactions         The list of transactions to be processed.
     * @param transactionReference The reference for the transaction.
     * @return The response entity containing the response.
     */
    @PostMapping("/transactions/internal")
    ResponseEntity<Response> makeInternalTransactions(@RequestBody List<Transaction> transactions,@RequestParam String transactionReference);
}
```

## 9. Feign client classes - UserService (Account-Service)
```java
package org.training.account.service.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.training.account.service.configuration.FeignConfiguration;
import org.training.account.service.model.dto.external.UserDto;

@FeignClient(name = "user-service", configuration = FeignConfiguration.class)
public interface UserService {

    /**
     * Retrieves a user by their ID.
     *
     * @param userId the ID of the user to retrieve
     * @return a ResponseEntity containing the user DTO if found, or an empty body with a not found status code
     */
    @GetMapping("/api/users/{userId}")
    ResponseEntity<UserDto> readUserById(@PathVariable Long userId);
}
```

## 9. Feign client classes - TransactionService (Account-Service)
```java
package org.training.account.service.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.training.account.service.configuration.FeignConfiguration;
import org.training.account.service.model.dto.external.TransactionResponse;

import java.util.List;

@FeignClient(name = "transaction-service", configuration = FeignConfiguration.class)
public interface TransactionService {

    /**
     * Retrieves a list of transactions from the specified account ID.
     *
     * @param accountId the ID of the account
     * @return a list of transaction responses
     */
    @GetMapping("/transactions")
    List<TransactionResponse> getTransactionsFromAccountId(@RequestParam String accountId);
}
```

## 9. Feign client classes - SequenceService (Account-Service)
```java
package org.training.account.service.external;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.training.account.service.model.dto.external.SequenceDto;

@FeignClient(name = "sequence-generator")
public interface SequenceService {

    /**
     * Generates a new account number.
     *
     * @return the generated account number as a SequenceDto object.
     */
    @PostMapping("/sequence")
    SequenceDto generateAccountNumber();
}
```

## 10. application.yml - API-Gateway
```yaml
server:
  port: 8080

app:
  config:
    keycloak:
      url: http://localhost:8571/
      realm: banking-service

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka

spring:
  application:
    name: api-gateway

  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
        - id: fund-transfer-service
          uri: lb://fund-transfer-service
          predicates:
            - Path=/api/fund-transfers/**
        - id: account-service
          uri: lb://account-service
          predicates:
            - Path=/accounts/**
        - id: sequence-generator
          uri: lb://sequence-generator
          predicates:
            - Path=/sequence/**
        - id: transaction-service
          uri: lb://transaction-service
          predicates:
            - Path=/transactions/**
        - id: fund-transfer-service
          uri: lb://fund-transfer-service
          predicates:
            - Path=/fund-transfers/**

  security:
    oauth2:
      client:
        provider:
          keycloak:
            token-uri: ${app.config.keycloak.url}/realms/${app.config.keycloak.realm}/protocol/openid-connect/token
            authorization-uri: ${app.config.keycloak.url}/realms/${app.config.keycloak.realm}/protocol/openid-connect/auth
            user-name-attribute: preferred_username
            user-info-uri: ${app.config.keycloak.url}/realms/${app.config.keycloak.realm}/protocol/openid-connect/userinfo
            jwk-set-uri: ${app.config.keycloak.url}/realms/${app.config.keycloak.realm}/protocol/openid-connect/certs
            user-info-authentication-method: header
        registration:
          banking-service-client:
            provider: keycloak
            client-id: banking-service-client
            client-secret: 7ZXjz5ZBz9EzoBBr1reNOVfmd2XqQSwJ
            authorization-grant-type: authorization_code
            redirect-uri: http://localhost:8571/login/oauth2/code/keycloak
            scope: openid
      resourceserver:
        jwt:
          jwk-set-uri: ${app.config.keycloak.url}/realms/${app.config.keycloak.realm}/protocol/openid-connect/certs

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x / Spring Cloud Gateway (WebFlux) syntax
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - Account-Service
```yaml
spring:
  application:
    name: account-service
    bad_request: 400
    conflict: 409
    ok: 200
    not_found: 404

  datasource:
    url: jdbc:mysql://localhost:3306/account_service
    username: root
    password: Netcracker@123

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
eureka:
  client:
    service-url:
      defaultZone: http://service-registry:8761/eureka/

server:
  port: 8081

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - User-Service
```yaml
server:
  port: 8082

spring:
  application:
    name: user-service
    bad_request: 400
    conflict: 409
    success: 200
    not_found: 404

  datasource:
    url: jdbc:mysql://${MYSQL_HOST:localhost}:${MYSQL_PORT:3306}/${MYSQL_DB_NAME:user_service}
    username: ${MYSQL_USER:root}
    password: ${MYSQL_PASSWORD:Netcracker@123}
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true


eureka:
  client:
    service-url:
      defaultZone: http://service-registry:8761/eureka/


app:
  config:
    keycloak:
      server-url: ${APP_CONFIG_KEYCLOAK_SERVER_URL:http://localhost:8571}
      realm: banking-service
      client-id: banking-service-api-client
      client-secret: ooZV25AjCo15w8A7Qum50VjrTbkie0EE

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - Transaction-Service
```yaml
spring:
  application:
    name: transaction-service
    bad_request: 400
    conflict: 409
    ok: 200

  datasource:
    url: jdbc:mysql://localhost:3306/transaction_service
    username: root
    password: Netcracker@123

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true

eureka:
  client:
    service-url:
      defaultZone: http://service-registry:8761/eureka/

server:
  port: 8084

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - Fund-Transfer
```yaml
server:
  port: 8085

spring:
  application:
    name: fund-transfer-service
    bad_request: 400
    ok: 200

  datasource:
    url: jdbc:mysql://localhost:3306/fund_transfer_service
    username: root
    password: Netcracker@123

  jpa:
    hibernate:
      ddl-auto: update

    show-sql: true

    properties:
      hibernate:
        format_sql: true

eureka:
  client:
    service-url:
      defaultZone: http://service-registry:8761/eureka/

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - Sequence-Generator
```yaml
spring:
  application:
    name: sequence-generator

  datasource:
    url: jdbc:mysql://localhost:3306/sequence_generator
    username: root
    password: Netcracker@123

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
eureka:
  client:
    service-url:
      defaultZone: http://service-registry:8761/eureka/

server:
  port: 8083

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus

  endpoint:
    health:
      show-details: always

  metrics:
    export:
      prometheus:
        enabled: true

    tags:
      application: ${spring.application.name}

    distribution:
      percentiles-histogram:
        all: true

      percentiles:
        http.server.requests: 0.50,0.95,0.99

      slo:
        http.server.requests: 100ms,250ms,500ms,1s,2s,5s
```

## 10. application.yml - Service-Registry
```yaml
server:
  port: 8761

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka
    register-with-eureka: false
    fetch-registry: false

spring:
  application:
    name: SERVICE-REGISTRY

# ============================================================
# Performance Engineering Monitoring — Actuator + Prometheus
# Spring Boot 2.7.x syntax (management.metrics.export.prometheus)
# ============================================================
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
```

