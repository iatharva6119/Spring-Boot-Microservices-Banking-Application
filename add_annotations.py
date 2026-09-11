import os
import re

services = {
    'account-service': 8081,
    'api-gateway': 8080,
    'fund-transfer': 8083,
    'sequence-generator': 8085,
    'service-registry': 8761,
    'transaction-service': 8084,
    'user-service': 8082
}

for svc, port in services.items():
    dep_file = os.path.join('k8s', svc, 'deployment.yaml')
    if os.path.exists(dep_file):
        with open(dep_file, 'r') as f:
            content = f.read()
        
        # We need to insert annotations under spec.template.metadata
        # Usually it looks like:
        #   template:
        #     metadata:
        #       labels:
        #         app: ...
        
        annotation_block = f"""      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: "/actuator/prometheus"
        prometheus.io/port: "{port}"
"""
        # If it doesn't already have annotations, insert before labels:
        if 'prometheus.io/scrape' not in content:
            if '      labels:' in content:
                content = content.replace('      labels:', annotation_block + '      labels:', 1)
                with open(dep_file, 'w') as f:
                    f.write(content)
                print(f"Annotated {svc}")
            else:
                print(f"Could not find labels in {svc}")
