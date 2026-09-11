@echo off
set services=API-Gateway Account-Service Fund-Transfer Sequence-Generator Service-Registry Transaction-Service User-Service
for %%S in (%services%) do (
    echo Building %%S with Docker Maven...
    cd %%S
    call docker run --rm -v %cd%:/app -w /app maven:3.8.7-eclipse-temurin-17 mvn clean package -DskipTests
    cd ..
)
echo All services compiled.
