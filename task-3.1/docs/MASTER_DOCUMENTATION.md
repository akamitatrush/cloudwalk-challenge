# 🚀 CloudWalk Monitoring Analyst Challenge
## Task 3.1 - Complete Technical Delivery

<div align="center">

![CloudWalk](https://img.shields.io/badge/CloudWalk-Monitoring_Analyst-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge)
![Grafana](https://img.shields.io/badge/Grafana-10.1-orange?style=for-the-badge)
![Prometheus](https://img.shields.io/badge/Prometheus-2.47-red?style=for-the-badge)

**"Where there is data smoke, there is business fire."** — Thomas Redman

---

### 📋 Candidate Information

| Field | Value |
|-------|-------|
| **Name** | Sérgio |
| **Position** | Monitoring Intelligence Analyst (Night Shift) |
| **Challenge** | Task 3.1 - Anomaly Detection Analysis |
| **Delivery Date** | January 2026 |

</div>

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Story: A Night Shift Perspective](#2-the-story-a-night-shift-perspective)
3. [Technical Analysis](#3-technical-analysis)
4. [AI-Powered Methodology](#4-ai-powered-methodology)
5. [SQL Analysis & Queries](#5-sql-analysis--queries)
6. [Visualizations & Dashboards](#6-visualizations--dashboards)
7. [Production-Ready Infrastructure](#7-production-ready-infrastructure)
8. [Incident Response Framework](#8-incident-response-framework)
9. [Business Impact Assessment](#9-business-impact-assessment)
10. [Recommendations & Next Steps](#10-recommendations--next-steps)
11. [Deliverables Checklist](#11-deliverables-checklist)

---

## 1. Executive Summary

### 🎯 Challenge Objective

Analyze checkout transaction data from two CSV files to identify anomalous behavior, present findings through SQL queries and visualizations, and demonstrate the analytical mindset required for a Monitoring Intelligence Analyst role.

### 🔍 Key Discovery

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🚨 CRITICAL ANOMALY DETECTED                                                ║
║                                                                               ║
║   Dataset: checkout_2.csv                                                     ║
║   Affected Period: 15:00 - 17:59 (3 hours)                                    ║
║   Issue: ZERO TRANSACTIONS during peak business hours                         ║
║   Estimated Lost Transactions: ~62                                            ║
║   Probable Cause: System Outage (Payment Gateway / API Failure)               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### 📊 Comparative Analysis

| Metric | checkout_1.csv | checkout_2.csv | Delta |
|--------|----------------|----------------|-------|
| Total Transactions Today | 526 | 427 | -99 (-19%) |
| Total Transactions Yesterday | 523 | 526 | +3 |
| Critical Anomaly Hours | 0 | 3 | ⚠️ |
| Peak Hour Performance | Normal | **OUTAGE** | 🚨 |
| Data Health | ✅ Healthy | ❌ Anomalous | - |

### 💡 What Makes This Analysis Different

This delivery goes **far beyond** a simple data analysis. It provides:

1. **Production-Ready Infrastructure** - Complete Grafana + Prometheus stack
2. **Real-World Incident Response** - Full incident report, runbook, and communication templates
3. **AI-Augmented Analysis** - Demonstrating the use of AI tools as specified in the job requirements
4. **Night Shift Perspective** - Analysis structured as if responding to a real incident at 22:00

---

## 2. The Story: A Night Shift Perspective

### 🌙 Setting the Scene

*It's 22:00 on a regular Tuesday night. I've just started my shift as a Monitoring Intelligence Analyst at CloudWalk. My first task: review the daily checkout data and ensure everything is operating normally.*

### 📖 The Discovery Timeline

**22:00 - Shift Start**: Loading daily checkout reports. Two datasets need review.

**22:10 - Initial Scan**: `checkout_1.csv` looks normal. Expected patterns confirmed.

**22:15 - Anomaly Detection**: `checkout_2.csv` reveals critical issue:

| Hour | Today | Expected | Status |
|------|-------|----------|--------|
| 14h | 19 | 19.6 | ✅ Normal |
| 15h | **0** | 22.4 | 🚨 ZERO! |
| 16h | **0** | 21.6 | 🚨 ZERO! |
| 17h | **0** | 17.7 | 🚨 ZERO! |
| 18h | 13 | 16.9 | ⚠️ Recovering |

**Three consecutive hours of ZERO transactions during peak business hours.**

**22:20 - Statistical Confirmation**:
- Z-Score for 15h: -2.8 (significantly below normal)
- Z-Score for 16h: -2.7 (significantly below normal)
- Z-Score for 17h: -2.4 (significantly below normal)

**22:30 - Secondary Pattern Identified** (Morning Spike):

| Hour | Today | Expected | Deviation |
|------|-------|----------|-----------|
| 08h | 25 | 3.7 | +574% 📈 |
| 09h | 36 | 10.1 | +255% 📈 |

**Hypothesis**: Backlog processing from previous day's issues.

**22:45 - Full Picture**:
```
Timeline Reconstruction:
├── 00:00-07:00 ─── Normal overnight activity
├── 08:00-09:00 ─── 🔶 SPIKE: Backlog processing
├── 10:00-14:00 ─── Normal operations
├── 15:00-17:00 ─── 🔴 OUTAGE: Zero transactions (3 hours)
├── 18:00 ──────── 🟡 Recovery begins
└── 19:00-23:00 ─── Normal operations
```

**23:00 - Incident Report Filed**: Analysis complete, documentation ready.

---

## 3. Technical Analysis

### 3.1 Statistical Methods Applied

**Method 1: Percentage Deviation**
```python
deviation_pct = ((today - avg_last_week) / avg_last_week) * 100
```

**Method 2: Z-Score Analysis**
```python
z_score = (today - mean) / standard_deviation
```

**Method 3: Threshold Detection**
```python
is_anomaly = (today < avg * 0.5) OR (today > avg * 1.5) OR (today == 0 AND avg > 5)
```

### 3.2 Key Findings

**checkout_1.csv**: ✅ NORMAL - 526 transactions, all within expected range

**checkout_2.csv**: 🚨 CRITICAL - 427 transactions, 3 hours of complete outage

| Hour | Today | Avg Week | Deviation | Z-Score | Status |
|------|-------|----------|-----------|---------|--------|
| 15h | 0 | 22.43 | -100% | -2.8 | CRITICAL |
| 16h | 0 | 21.57 | -100% | -2.7 | CRITICAL |
| 17h | 0 | 17.71 | -100% | -2.4 | CRITICAL |

---

## 4. AI-Powered Methodology

The job description states: *"Use artificial intelligence tools to accelerate insight generation, pattern recognition, and opportunity discovery"*

### Human-AI Partnership Demonstrated:

| Task | AI Contribution | Human Contribution |
|------|-----------------|-------------------|
| Pattern Detection | Statistical algorithms | Business context |
| Anomaly Classification | Z-Score calculation | Severity assessment |
| Visualization | Chart generation | Insight interpretation |
| Documentation | Report structuring | Communication clarity |

---

## 5. SQL Analysis & Queries

### Query 1: Anomaly Detection
```sql
SELECT time, today, avg_last_week,
    ROUND(((today - avg_last_week) / NULLIF(avg_last_week, 0)) * 100, 2) AS deviation_pct,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL'
        WHEN today < avg_last_week * 0.5 THEN 'HIGH'
        ELSE 'NORMAL'
    END AS status
FROM checkout_data
WHERE today = 0 OR today < avg_last_week * 0.5;
```

### Query 2: Daily Summary
```sql
SELECT 
    SUM(today) AS total_today,
    SUM(yesterday) AS total_yesterday,
    ROUND(((SUM(today) - SUM(yesterday)) / SUM(yesterday)) * 100, 2) AS dod_change
FROM checkout_data;
```

---

## 6. Visualizations & Dashboards

### Delivered Visualizations:
1. **Multi-Panel Analysis Chart** - 4 views comparing datasets
2. **Timeline Focus** - Story of the outage
3. **Interactive HTML Dashboard** - Grafana-style web interface
4. **Grafana Dashboard JSON** - Import-ready for production

---

## 7. Production-Ready Infrastructure

### Complete Stack Delivered:

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
             └─────────────┘          └─────────────┘  └──────────┘
```

### Components:
- **Docker Compose** - One command deployment
- **Prometheus** - Metrics collection
- **Alertmanager** - Alert routing
- **Grafana** - Visualization
- **Custom Exporter** - CSV to metrics

### Alert Rules Configured:
- P1: Zero transactions during business hours
- P2: >50% drop from expected
- P3: >200% spike detected

---

## 8. Incident Response Framework

### Delivered Templates:
1. **INCIDENT_REPORT.md** - Formal incident documentation
2. **RUNBOOK.md** - Step-by-step response guide
3. **SLACK_TEMPLATES.md** - Communication ready to send

---

## 9. Business Impact Assessment

### Financial Impact:
- **Lost Transactions**: ~62 during outage
- **Outage Duration**: 3 hours
- **Timing**: Peak afternoon hours

### Risk Assessment:
- High Impact + Medium-High Likelihood = **CRITICAL**

---

## 10. Recommendations & Next Steps

### Immediate (24h):
1. Root cause investigation
2. System log analysis
3. Cross-team coordination

### Short-term (1 week):
1. Enhanced alerting rules
2. Dashboard improvements
3. Runbook updates

### Long-term (1 month):
1. ML-based anomaly detection
2. Automated response procedures
3. Observability enhancement

---

## 11. Deliverables Checklist

### ✅ Documentation
- [x] MASTER_DOCUMENTATION.md
- [x] ANALYSIS_REPORT.md
- [x] INCIDENT_REPORT.md
- [x] RUNBOOK.md
- [x] SLACK_TEMPLATES.md
- [x] PROMQL_CHEATSHEET.md

### ✅ Code
- [x] task_3_1_analysis.py
- [x] alert_system.py
- [x] checkout_exporter.py
- [x] sql_queries.sql

### ✅ Dashboards
- [x] checkout_monitoring.json (Grafana)
- [x] DASHBOARD.html (Interactive)

### ✅ Infrastructure
- [x] docker-compose.yml
- [x] prometheus.yml
- [x] checkout_alerts.yml
- [x] alertmanager.yml

### ✅ Visualizations
- [x] anomaly_analysis_chart.png
- [x] anomaly_timeline.png

---

<div align="center">

## 🎯 Final Note

This analysis demonstrates the **mindset** of a Monitoring Intelligence Analyst:

- **Proactive** detection
- **Systematic** investigation
- **Clear** communication
- **Production-ready** solutions
- **Business-aware** assessment

*"We want firefighters that use code to stop the fire."*

**This is what that looks like in practice.**

---

**CloudWalk Monitoring Analyst Challenge - Task 3.1**

</div>
