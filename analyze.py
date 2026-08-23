import os
import re

def analyze_repo(root_dir):
    out = []
    
    # Files to directly include
    direct_files = ['docker-compose.yml']
    
    for root, dirs, files in os.walk(root_dir):
        if any(ignored in root for ignored in ['.git', '.idea', 'target', 'node_modules']):
            continue
            
        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, root_dir)
            
            if file in direct_files or file == 'application.yml' or file == 'pom.xml' or file.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 10000 and file != 'docker-compose.yml':
                            content = content[:10000] + "...(truncated)"
                        out.append(f"--- FILE: {rel_path} ---\n{content}\n")
                except Exception as e:
                    pass
            elif file.endswith('.java'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Only include if it's a Controller, FeignClient, Entity, Service, Config, or Security
                        if any(x in content for x in ['@RestController', '@FeignClient', '@Entity', '@Service', '@Configuration', 'SecurityConfig', '@Repository']):
                            out.append(f"--- FILE: {rel_path} ---\n{content}\n")
                except Exception as e:
                    pass

    with open('analysis_output.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(out))
        
if __name__ == '__main__':
    analyze_repo('.')
