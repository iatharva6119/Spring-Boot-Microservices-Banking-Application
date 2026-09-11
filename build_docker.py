import os
import subprocess

services = ['API-Gateway', 'Account-Service', 'Fund-Transfer', 'Sequence-Generator', 'Service-Registry', 'Transaction-Service', 'User-Service']

for svc in services:
    print(f"Building {svc}...")
    abs_path = os.path.join(os.getcwd(), svc)
    # Using Docker to build the service with Java 17
    cmd = f'docker run --rm -v "{abs_path}:/app" -w /app maven:3.8.7-eclipse-temurin-17 mvn clean package -DskipTests'
    subprocess.run(cmd, shell=True)
    print(f"Finished {svc}")
