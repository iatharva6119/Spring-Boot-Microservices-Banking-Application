@echo off
set JAVA_HOME=C:\Program Files\Java\jdk-17
set services=API-Gateway Account-Service Fund-Transfer Sequence-Generator Service-Registry Transaction-Service User-Service
for %%S in (%services%) do (
    echo Building %%S...
    cd %%S
    call mvn clean package -DskipTests -T 1C
    cd ..
)
echo All services compiled.
