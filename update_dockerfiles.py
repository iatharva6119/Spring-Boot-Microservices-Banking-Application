import os
import re

services = ['API-Gateway', 'Account-Service', 'Fund-Transfer', 'Sequence-Generator', 'Service-Registry', 'Transaction-Service', 'User-Service']

for svc in services:
    dockerfile_path = os.path.join(svc, 'Dockerfile')
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        if 'opentelemetry-javaagent.jar' not in content:
            # Insert COPY opentelemetry-javaagent.jar opentelemetry-javaagent.jar
            content = content.replace('COPY target/*.jar app.jar', 'COPY target/*.jar app.jar\nCOPY opentelemetry-javaagent.jar opentelemetry-javaagent.jar')
            
            # Update ENTRYPOINT
            content = content.replace('ENTRYPOINT ["java", "-jar", "app.jar"]', 'ENTRYPOINT ["java", "-javaagent:opentelemetry-javaagent.jar", "-jar", "app.jar"]')
            
            with open(dockerfile_path, 'w') as f:
                f.write(content)
            print(f"Updated Dockerfile for {svc}")
