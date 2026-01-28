#!/usr/bin/env python3
import requests
import json

GRAFANA_URL = "http://localhost:3002"
DS_UID = "ab347962-10d1-47be-9e20-d6982edff4f0"

dashboard = {
    "dashboard": {
        "id": None,
        "title": "Transaction Guardian - Complete",
        "tags": ["timescaledb", "monitoring"],
        "timezone": "browser",
        "refresh": "10s",
        "panels": [
            {
                "id": 1, "title": "📊 Total Transações", "type": "stat",
                "gridPos": {"h": 5, "w": 6, "x": 0, "y": 0},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT COUNT(*) as total FROM transactions;", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "green"}}}
            },
            {
                "id": 2, "title": "✅ Aprovadas", "type": "stat",
                "gridPos": {"h": 5, "w": 6, "x": 6, "y": 0},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT COUNT(*) FROM transactions WHERE status='approved';", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "green"}}}
            },
            {
                "id": 3, "title": "❌ Negadas", "type": "stat",
                "gridPos": {"h": 5, "w": 6, "x": 12, "y": 0},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT COUNT(*) FROM transactions WHERE status='denied';", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "yellow"}}}
            },
            {
                "id": 4, "title": "💥 Falhas", "type": "stat",
                "gridPos": {"h": 5, "w": 6, "x": 18, "y": 0},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT COUNT(*) FROM transactions WHERE status='failed';", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "red"}}}
            },
            {
                "id": 5, "title": "📈 Taxa de Aprovação %", "type": "gauge",
                "gridPos": {"h": 7, "w": 8, "x": 0, "y": 5},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT ROUND((COUNT(*) FILTER (WHERE status = 'approved')::numeric / COUNT(*) * 100), 1) as taxa FROM transactions;", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"max": 100, "unit": "percent", "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 30}, {"color": "green", "value": 60}]}}}
            },
            {
                "id": 6, "title": "🚨 Anomalias", "type": "stat",
                "gridPos": {"h": 7, "w": 8, "x": 8, "y": 5},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT COUNT(*) as anomalias FROM transactions WHERE is_anomaly = true;", "format": "table", "refId": "A"}],
                "fieldConfig": {"defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "red", "value": 100}]}}}
            },
            {
                "id": 7, "title": "📊 Por Status", "type": "barchart",
                "gridPos": {"h": 7, "w": 8, "x": 16, "y": 5},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT status, COUNT(*) as total FROM transactions GROUP BY status ORDER BY total DESC;", "format": "table", "refId": "A"}]
            },
            {
                "id": 8, "title": "📈 Transações/Hora (24h)", "type": "timeseries",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT date_trunc('hour', timestamp) as time, COUNT(*) as total FROM transactions WHERE timestamp > NOW() - INTERVAL '24 hours' GROUP BY 1 ORDER BY 1;", "format": "time_series", "refId": "A"}]
            },
            {
                "id": 9, "title": "🏢 Top 10 Merchants", "type": "table",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT merchant_id, COUNT(*) as total, COUNT(*) FILTER (WHERE status='approved') as aprovadas FROM transactions GROUP BY merchant_id ORDER BY total DESC LIMIT 10;", "format": "table", "refId": "A"}]
            },
            {
                "id": 10, "title": "⏰ Últimas Transações", "type": "table",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20},
                "datasource": {"type": "postgres", "uid": DS_UID},
                "targets": [{"rawSql": "SELECT timestamp, status, amount, merchant_id, is_anomaly FROM transactions ORDER BY timestamp DESC LIMIT 10;", "format": "table", "refId": "A"}]
            }
        ]
    },
    "overwrite": True
}

r = requests.post(f"{GRAFANA_URL}/api/dashboards/db", auth=("admin","admin"), json=dashboard)
print(f"Status: {r.status_code}")
print(r.json())
