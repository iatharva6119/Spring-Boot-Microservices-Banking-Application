FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY target/*.jar app.jar
COPY opentelemetry-javaagent.jar opentelemetry-javaagent.jar

EXPOSE 8085

ENTRYPOINT ["java", "-javaagent:opentelemetry-javaagent.jar", "-jar", "app.jar"]
