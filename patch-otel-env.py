import os
import yaml

services = ['api-gateway', 'account-service', 'fund-transfer', 'sequence-generator', 'service-registry', 'transaction-service', 'user-service']

otel_envs = [
    {"name": "OTEL_TRACES_EXPORTER", "value": "none"},
    {"name": "OTEL_METRICS_EXPORTER", "value": "none"},
    {"name": "OTEL_LOGS_EXPORTER", "value": "none"},
    {"name": "OTEL_PROPAGATORS", "value": "b3multi,tracecontext"}
]

for svc in services:
    if svc == 'api-gateway':
        dir_name = 'API-Gateway'
    elif svc == 'account-service':
        dir_name = 'Account-Service'
    elif svc == 'fund-transfer':
        dir_name = 'Fund-Transfer'
    elif svc == 'sequence-generator':
        dir_name = 'Sequence-Generator'
    elif svc == 'service-registry':
        dir_name = 'eureka'
    elif svc == 'transaction-service':
        dir_name = 'Transaction-Service'
    elif svc == 'user-service':
        dir_name = 'User-Service'

    deploy_path = f'k8s/{dir_name}/deployment.yaml'
    if os.path.exists(deploy_path):
        with open(deploy_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        
        for doc in docs:
            if doc and doc.get('kind') == 'Deployment':
                containers = doc['spec']['template']['spec']['containers']
                for c in containers:
                    if 'env' not in c:
                        c['env'] = []
                    
                    # Remove existing if any
                    c['env'] = [e for e in c['env'] if not e['name'].startswith('OTEL_')]
                    
                    # Add new
                    c['env'].extend(otel_envs)
                    
        with open(deploy_path, 'w') as f:
            yaml.safe_dump_all(docs, f, default_flow_style=False, sort_keys=False)
            print(f"Patched {deploy_path}")
