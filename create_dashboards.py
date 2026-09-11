import json
import os

dashboards = {
    "phase6-application": {
        "title": "Phase 6 - Application Metrics",
        "panels": [
            {"title": "Request Rate", "type": "timeseries", "targets": [{"expr": "rate(http_server_requests_seconds_count[1m])"}]},
            {"title": "Error Rate", "type": "timeseries", "targets": [{"expr": "rate(http_server_requests_seconds_count{status=~\"5..\"}[1m])"}]}
        ]
    },
    "phase6-kubernetes": {
        "title": "Phase 6 - Kubernetes Metrics",
        "panels": [
            {"title": "Pod Count", "type": "stat", "targets": [{"expr": "count(kube_pod_info{namespace=\"banking\"})"}]},
            {"title": "Pod Restarts", "type": "timeseries", "targets": [{"expr": "rate(kube_pod_container_status_restarts_total{namespace=\"banking\"}[5m])"}]}
        ]
    },
    "phase6-jvm": {
        "title": "Phase 6 - JVM Metrics",
        "panels": [
            {"title": "Heap Used", "type": "timeseries", "targets": [{"expr": "jvm_memory_used_bytes{area=\"heap\"}"}]},
            {"title": "GC Pause Time", "type": "timeseries", "targets": [{"expr": "rate(jvm_gc_pause_seconds_sum[1m])"}]}
        ]
    },
    "phase6-hpa": {
        "title": "Phase 6 - HPA Metrics",
        "panels": [
            {"title": "HPA Replicas", "type": "timeseries", "targets": [{"expr": "kube_horizontalpodautoscaler_status_current_replicas{namespace=\"banking\"}"}]},
            {"title": "HPA Target CPU", "type": "timeseries", "targets": [{"expr": "kube_horizontalpodautoscaler_spec_target_metric{namespace=\"banking\"}"}]}
        ]
    },
    "phase6-istio-envoy": {
        "title": "Phase 6 - Istio/Envoy Metrics",
        "panels": [
            {"title": "Envoy Request Rate", "type": "timeseries", "targets": [{"expr": "rate(istio_requests_total{reporter=\"destination\", namespace=\"banking\"}[1m])"}]},
            {"title": "Envoy P99 Latency", "type": "timeseries", "targets": [{"expr": "histogram_quantile(0.99, rate(istio_request_duration_milliseconds_bucket{reporter=\"destination\", namespace=\"banking\"}[1m]))"}]}
        ]
    }
}

base_dashboard = {
    "annotations": {"list": []},
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 0,
    "links": [],
    "liveNow": False,
    "refresh": "5s",
    "schemaVersion": 38,
    "style": "dark",
    "tags": ["phase6"],
    "templating": {"list": []},
    "time": {"from": "now-15m", "to": "now"},
    "timepicker": {},
    "timezone": "",
    "version": 1
}

out_dir = os.path.join("grafana", "provisioning", "dashboards")
os.makedirs(out_dir, exist_ok=True)

for name, data in dashboards.items():
    dash = base_dashboard.copy()
    dash["title"] = data["title"]
    dash["uid"] = name
    
    panels = []
    for i, p in enumerate(data["panels"]):
        panel = {
            "title": p["title"],
            "type": p["type"],
            "gridPos": {"h": 8, "w": 12, "x": (i%2)*12, "y": (i//2)*8},
            "id": i + 1,
            "targets": [{"expr": t["expr"], "refId": "A"} for t in p["targets"]]
        }
        panels.append(panel)
        
    dash["panels"] = panels
    
    with open(os.path.join(out_dir, f"{name}.json"), "w") as f:
        json.dump(dash, f, indent=2)
    print(f"Created {name}.json")
