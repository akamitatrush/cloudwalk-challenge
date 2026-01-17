# 🚀 CloudWalk Monitoring Analyst Challenge - Task 3.1
## Complete Delivery Package

<div align="center">

**Candidate:** Sérgio  
**Position:** Monitoring Intelligence Analyst (Night Shift)  
**Date:** January 2026

---

### 🎯 Quick Navigation

| Section | Description |
|---------|-------------|
| 📄 [docs/](./docs/) | Complete documentation |
| 💻 [code/](./code/) | Python scripts & SQL |
| 📊 [dashboards/](./dashboards/) | Grafana & HTML dashboards |
| 🏗️ [infrastructure/](./infrastructure/) | Docker stack for Grafana+Prometheus |
| 🖼️ [assets/](./assets/) | Visualization images |
| 📁 [data/](./data/) | CSV files & exports |
| 🎬 [prompts/](./prompts/) | NotebookLM video prompt |

</div>

---

## 📋 Executive Summary

**Challenge:** Analyze checkout data to identify anomalies  
**Discovery:** 3-hour system outage (15h-17h) with ZERO transactions  
**Impact:** ~62 lost transactions during peak hours  
**Delivery:** 15+ files including production-ready monitoring stack

---

## 🔥 What Makes This Submission Different

Most candidates deliver: A script and a chart.

**This submission delivers:**

✅ Complete statistical analysis with multiple detection methods  
✅ Production-ready Grafana dashboard  
✅ Prometheus alert rules (P1/P2/P3 severity)  
✅ Alertmanager configuration  
✅ Docker Compose stack (one command to run)  
✅ Incident response framework  
✅ PromQL cheatsheet  
✅ NotebookLM video prompt  

---

## 📂 File Structure

```
cloudwalk_task_3.1_delivery/
│
├── 📄 docs/
│   ├── MASTER_DOCUMENTATION.md    # Complete analysis document
│   ├── ANALYSIS_REPORT.md         # Technical report
│   ├── INCIDENT_REPORT.md         # Incident template
│   ├── RUNBOOK.md                 # Operational guide
│   ├── SLACK_TEMPLATES.md         # Communication templates
│   └── PROMQL_CHEATSHEET.md       # Query reference
│
├── 💻 code/
│   ├── task_3_1_analysis.py       # Main analysis script
│   ├── alert_system.py            # Automated alerts
│   ├── checkout_exporter.py       # Prometheus exporter
│   └── sql_queries.sql            # SQL query collection
│
├── 📊 dashboards/
│   ├── checkout_monitoring.json   # Grafana dashboard (import-ready)
│   └── DASHBOARD.html             # Interactive web dashboard
│
├── 🏗️ infrastructure/
│   ├── docker-compose.yml         # Full stack deployment
│   ├── Dockerfile.exporter        # Custom exporter image
│   ├── README.md                  # Setup instructions
│   ├── prometheus/
│   │   ├── prometheus.yml         # Prometheus config
│   │   └── checkout_alerts.yml    # Alert rules
│   ├── alertmanager/
│   │   └── alertmanager.yml       # Alert routing
│   └── grafana/
│       └── provisioning/          # Auto-config
│
├── 🖼️ assets/
│   ├── anomaly_analysis_chart.png # Multi-panel visualization
│   └── anomaly_timeline.png       # Timeline focus chart
│
├── 📁 data/
│   ├── checkout_1.csv             # Normal dataset
│   ├── checkout_2.csv             # Anomalous dataset
│   └── alerts_export.json         # Generated alerts
│
├── 🎬 prompts/
│   └── NOTEBOOKLM_PROMPT.md       # Video generation prompt
│
└── 📖 README.md                   # This file
```

---

## 🚀 Quick Start

### Option 1: View Analysis Results
```bash
# Open the main documentation
open docs/MASTER_DOCUMENTATION.md

# View visualizations
open assets/anomaly_analysis_chart.png
```

### Option 2: Run Python Analysis
```bash
cd code
pip install pandas numpy matplotlib seaborn pandasql
python task_3_1_analysis.py
```

### Option 3: Full Monitoring Stack
```bash
cd infrastructure
docker-compose up -d

# Access:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Alertmanager: http://localhost:9093
```

---

## 📊 Key Findings

| Metric | checkout_1 | checkout_2 |
|--------|------------|------------|
| Total Today | 526 | 427 |
| Status | ✅ Normal | 🚨 Anomaly |
| Critical Hours | 0 | 3 |
| Lost Transactions | 0 | ~62 |

### The Anomaly

```
Hour | Today | Expected | Status
-----|-------|----------|--------
15h  |   0   |   22.4   | 🚨 CRITICAL
16h  |   0   |   21.6   | 🚨 CRITICAL
17h  |   0   |   17.7   | 🚨 CRITICAL
```

---

## 🎬 Generate Video Summary

1. Go to [NotebookLM](https://notebooklm.google.com)
2. Upload `docs/MASTER_DOCUMENTATION.md`
3. Use the prompt in `prompts/NOTEBOOKLM_PROMPT.md`
4. Generate audio/video summary

---

## 📝 Challenge Requirements Met

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Analyze data for anomalies | ✅ | Multiple detection methods |
| Present conclusions | ✅ | MASTER_DOCUMENTATION.md |
| SQL queries | ✅ | sql_queries.sql |
| Graphics | ✅ | 2 PNG + HTML dashboard |
| Explain anomaly behavior | ✅ | Detailed in documentation |

**BONUS deliverables:**
- Production Grafana dashboard
- Prometheus alert rules
- Docker infrastructure
- Incident response framework
- Video generation prompt

---

<div align="center">

### 🎯 *"We want firefighters that use code to stop the fire."*

**This submission is the answer to that call.**

---

**CloudWalk Monitoring Analyst Challenge - Task 3.1**

</div>
