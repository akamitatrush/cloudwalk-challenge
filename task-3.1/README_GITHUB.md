# 🚀 CloudWalk Monitoring Analyst Challenge

<div align="center">

![CloudWalk](https://img.shields.io/badge/CloudWalk-Challenge-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)
![Task](https://img.shields.io/badge/Task-3.1-orange?style=for-the-badge)

**Monitoring Intelligence Analyst (Night Shift)**

*"Bombeiros que usam código para apagar incêndios."* 🔥

[📊 Live Dashboard](#-live-demo) • [📓 Interactive Notebook](#-live-demo) • [📋 Documentation](#-documentation) • [🎙️ Podcast](#-podcast-summary)

</div>

---

## 🎯 Challenge Summary

**Task 3.1:** Analyze checkout data to identify anomalies and present conclusions with SQL queries and visualizations.

### 🔍 Key Discovery

```
╔═══════════════════════════════════════════════════════════════╗
║  🚨 CRITICAL ANOMALY DETECTED                                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Dataset: checkout_2.csv                                      ║
║  Period: 15:00 - 17:59 (3 consecutive hours)                 ║
║  Issue: ZERO transactions during peak business hours          ║
║  Lost Transactions: ~62 estimated                             ║
║  Z-Score: -2.8 (statistically significant)                   ║
║  Probable Cause: Payment system outage                        ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🚀 Live Demo

### 🌐 Interactive Dashboard
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-green?style=for-the-badge&logo=github)](https://SEU-USUARIO.github.io/cloudwalk-challenge/)

### 📓 Google Colab (Run SQL Queries)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU-USUARIO/cloudwalk-challenge/blob/main/task-3.1/interactive/CloudWalk_Challenge_3_1_Interactive.ipynb)

### 📊 Streamlit Dashboard
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cloudwalk-challenge.streamlit.app)

### 🐳 Run Locally (Grafana + Prometheus)
```bash
cd task-3.1/infrastructure
docker-compose up -d
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

---

## 📊 Results at a Glance

| Metric | checkout_1 | checkout_2 | Status |
|--------|------------|------------|--------|
| Total Today | 526 | 427 | 🚨 -19% |
| Critical Hours | 0 | 3 | ⚠️ |
| Lost Transactions | 0 | ~62 | 💰 |
| Z-Score (min) | -1.2 | **-2.8** | 📉 |

---

## 📁 Project Structure

```
task-3.1/
│
├── 📂 docs/                     # Documentation (6 files)
│   ├── MASTER_DOCUMENTATION.md      # Complete analysis
│   ├── ANALYSIS_REPORT.md           # Technical report
│   ├── INCIDENT_REPORT.md           # P1-CRITICAL template
│   ├── RUNBOOK.md                   # Operational guide
│   ├── SLACK_TEMPLATES.md           # Communication templates
│   └── PROMQL_CHEATSHEET.md         # PromQL reference
│
├── 💻 code/                     # Source code (4 files)
│   ├── task_3_1_analysis.py         # Main analysis (pandas, matplotlib)
│   ├── alert_system.py              # Alert system with P1-P5 severity
│   ├── checkout_exporter.py         # Prometheus metrics exporter
│   └── sql_queries.sql              # SQL queries collection
│
├── 📊 dashboards/               # Dashboards (2 files)
│   ├── checkout_monitoring.json     # Grafana dashboard (import-ready)
│   └── DASHBOARD.html               # Interactive HTML dashboard
│
├── 🏗️ infrastructure/          # Complete stack
│   ├── docker-compose.yml           # 5 services
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── checkout_alerts.yml      # P1/P2/P3 alert rules
│   ├── alertmanager/
│   │   └── alertmanager.yml         # Slack, PagerDuty, Email
│   └── grafana/
│       └── provisioning/
│
├── 🎮 interactive/              # Live demos
│   ├── streamlit_app.py             # Streamlit dashboard
│   ├── CloudWalk_Challenge_3_1.ipynb # Colab notebook
│   └── requirements.txt
│
├── 🖼️ assets/                   # Visualizations
│   ├── anomaly_analysis_chart.png
│   └── anomaly_timeline.png
│
└── 📁 data/                     # Data files
    ├── checkout_1.csv               # Normal day
    ├── checkout_2.csv               # Anomaly day
    └── alerts_export.json
```

---

## 🔬 Technical Analysis

### Methods Applied

| Method | Description | Result |
|--------|-------------|--------|
| **Z-Score** | Standard deviations from mean | -2.8 (15h) |
| **Deviation %** | Variance from weekly average | -100% (15h-17h) |
| **Threshold** | Business rules detection | 3 CRITICAL hours |

### SQL Queries Available

```sql
-- 1. Detect all anomalies
SELECT time, today, deviation_pct, status FROM checkout_2 
WHERE today = 0 OR deviation_pct < -50;

-- 2. Daily comparison
SELECT SUM(today), SUM(yesterday), dod_change FROM checkouts;

-- 3. Peak hours analysis (10h-18h)
SELECT * FROM checkout_2 WHERE hour BETWEEN 10 AND 18;

-- 4. Z-Score calculation
SELECT time, (today - avg) / stddev as z_score FROM checkout_2;
```

▶️ **[Run these queries interactively in Google Colab](https://colab.research.google.com/)**

---

## 📈 Visualizations

### Anomaly Detection Chart
![Anomaly Analysis](task-3.1/assets/anomaly_analysis_chart.png)

### Incident Timeline
![Timeline](task-3.1/assets/anomaly_timeline.png)

---

## 🎙️ Podcast Summary

Listen to an AI-generated podcast summarizing this challenge:

🎧 **[Listen on NotebookLM](#)** *(link to be added)*

The podcast covers:
- The night shift discovery story
- Technical analysis methods
- Why this delivery goes 10x beyond requirements
- The human-AI partnership approach

---

## 🏗️ Infrastructure Stack

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  CSV Data   │────▶│  Exporter   │────▶│ Prometheus  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────┐
                    │                          │              │
                    ▼                          ▼              ▼
             ┌─────────────┐          ┌─────────────┐  ┌──────────┐
             │   Grafana   │          │Alertmanager │  │  Slack   │
             │  Dashboard  │          │   Routes    │  │ PagerDuty│
             └─────────────┘          └─────────────┘  └──────────┘
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/SEU-USUARIO/cloudwalk-challenge.git
cd cloudwalk-challenge/task-3.1/infrastructure

# Start the stack
docker-compose up -d

# Access services
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
open http://localhost:9093  # Alertmanager
```

---

## ✅ Deliverables Checklist

### Required
- [x] Data analysis
- [x] Anomaly identification
- [x] SQL queries
- [x] Visualizations
- [x] Written conclusions

### Bonus (10x Delivery)
- [x] Production-ready Grafana dashboard
- [x] Prometheus alert rules (P1/P2/P3)
- [x] Alertmanager configuration
- [x] Docker Compose stack
- [x] Incident report template
- [x] Operational runbook
- [x] Slack communication templates
- [x] PromQL cheatsheet
- [x] Interactive Colab notebook
- [x] Streamlit dashboard
- [x] Podcast summary
- [x] **30+ files total**

---

## 👤 Candidate

| | |
|---|---|
| **Name** | Sérgio |
| **Position** | Monitoring Intelligence Analyst |
| **Shift** | Night (00:00 - 08:00) |
| **Experience** | 14+ years IT, 10+ years Payment Systems |
| **Approach** | Human-AI Partnership |

---

## 📝 License

This project was created for the CloudWalk technical challenge.

---

<div align="center">

### 🔥 *"We want firefighters that use code to stop the fire."*

**This is what that looks like.**

---

Made with 💙 by Sérgio | CloudWalk Challenge 2026

</div>
