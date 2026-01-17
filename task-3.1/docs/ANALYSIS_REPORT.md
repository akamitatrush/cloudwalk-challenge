# CloudWalk Monitoring Analyst Challenge
## Task 3.1 - Anomaly Detection Analysis

**Candidate:** Sérgio  
**Date:** January 2026  
**Position:** Monitoring Intelligence Analyst (Night Shift)

---

## 1. Executive Summary

This analysis examines two checkout datasets to identify anomalous behavior patterns. The investigation revealed a **critical 3-hour system outage** in `checkout_2.csv` during peak afternoon hours (15h-17h), resulting in zero transactions and an estimated loss of ~62 transactions.

### Key Findings at a Glance

| Metric | checkout_1 | checkout_2 |
|--------|------------|------------|
| Total Sales Today | 526 | 427 |
| Total Sales Yesterday | 523 | 526 |
| Critical Anomalies | 1 | 3 |
| Status | ✅ Normal | 🚨 CRITICAL |

---

## 2. Methodology

### 2.1 Data Analysis Approach

The analysis employed multiple anomaly detection techniques:

1. **Statistical Comparison**: Today vs Yesterday vs Weekly/Monthly averages
2. **Z-Score Analysis**: Measuring standard deviations from expected values
3. **Threshold-Based Detection**: Flagging values outside ±50% of weekly average
4. **Temporal Pattern Analysis**: Identifying unusual hourly patterns

### 2.2 Tools & Technologies Used

- **Python 3** with Pandas for data manipulation
- **SQL (pandasql)** for structured queries
- **Matplotlib/Seaborn** for visualizations
- **Statistical methods**: Z-Score, percentage deviation, moving averages

---

## 3. Data Analysis

### 3.1 Dataset Structure

Both CSV files contain hourly checkout data with the following columns:

| Column | Description |
|--------|-------------|
| `time` | Hour of day (00h-23h) |
| `today` | Number of sales in current day |
| `yesterday` | Number of sales previous day |
| `same_day_last_week` | Sales from same weekday last week |
| `avg_last_week` | Average sales for that hour (last 7 days) |
| `avg_last_month` | Average sales for that hour (last 30 days) |

### 3.2 checkout_1.csv Analysis (Normal Day)

**Status: ✅ NORMAL BEHAVIOR**

The first dataset shows typical daily patterns:
- Morning ramp-up (05h-10h)
- Peak hours (10h-17h) with 30-55 transactions/hour
- Evening decline (18h-23h)
- Values align closely with historical averages

### 3.3 checkout_2.csv Analysis (Anomaly Detected)

**Status: 🚨 CRITICAL ANOMALY**

#### Primary Anomaly: System Outage

| Hour | Today | Yesterday | Avg Week | Deviation | Status |
|------|-------|-----------|----------|-----------|--------|
| **15h** | **0** | 51 | 22.4 | -100% | 🚨 CRITICAL |
| **16h** | **0** | 41 | 21.6 | -100% | 🚨 CRITICAL |
| **17h** | **0** | 45 | 17.7 | -100% | 🚨 CRITICAL |

**Analysis:**
- 3 consecutive hours of ZERO transactions
- Occurred during peak business hours
- Expected ~62 transactions based on weekly average
- This pattern strongly indicates a **system failure/outage**

#### Secondary Anomaly: Morning Spike

| Hour | Today | Yesterday | Avg Week | Deviation |
|------|-------|-----------|----------|-----------|
| 08h | 25 | 0 | 3.7 | +574% |
| 09h | 36 | 2 | 10.1 | +255% |

**Possible Explanation:**
This morning spike could indicate:
- Backlog processing from previous day's issues
- Batch processing of delayed transactions
- System recovery behavior

---

## 4. SQL Queries

### Query 1: Anomaly Detection

```sql
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    ROUND(((today - avg_last_week) / 
        NULLIF(avg_last_week, 0)) * 100, 2) as pct_deviation,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL - ZERO SALES'
        WHEN today < avg_last_week * 0.5 THEN 'ALERT - BELOW 50%'
        WHEN today > avg_last_week * 1.5 THEN 'ALERT - ABOVE 150%'
        ELSE 'NORMAL'
    END as status
FROM checkout_data
WHERE today = 0 
   OR today < avg_last_week * 0.5 
   OR today > avg_last_week * 1.5
ORDER BY pct_deviation;
```

### Query 2: Peak Hours Analysis

```sql
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    CASE 
        WHEN today = 0 THEN 'OUTAGE'
        WHEN today > avg_last_week * 1.5 THEN 'SPIKE'
        WHEN today < avg_last_week * 0.5 THEN 'DROP'
        ELSE 'NORMAL'
    END as classification
FROM checkout_data
WHERE CAST(REPLACE(time, 'h', '') AS INT) BETWEEN 10 AND 18
ORDER BY CAST(REPLACE(time, 'h', '') AS INT);
```

### Query 3: Z-Score Calculation

```sql
SELECT 
    time,
    today,
    avg_last_week,
    ROUND((today - avg_last_week) / 
        NULLIF(STDDEV(today - avg_last_week) OVER (), 0), 2) as z_score,
    CASE 
        WHEN ABS((today - avg_last_week) / 
            NULLIF(STDDEV(today - avg_last_week) OVER (), 0)) > 2 
        THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as z_score_status
FROM checkout_data;
```

---

## 5. Visualizations

### 5.1 Multi-Panel Analysis Chart

![Anomaly Analysis Chart](anomaly_analysis_chart.png)

The chart shows four perspectives:
1. **checkout_1**: Normal day pattern comparison
2. **checkout_2**: Anomaly visualization with highlighted outage period
3. **Deviation Analysis**: Bar chart showing variation from weekly average
4. **Heatmap**: Side-by-side hourly comparison

### 5.2 Timeline Focus

![Anomaly Timeline](anomaly_timeline.png)

This visualization clearly shows:
- The 3-hour gap (15h-17h) where transactions dropped to zero
- The recovery pattern starting at 18h
- The morning spike that preceded the outage

---

## 6. Root Cause Hypothesis

Based on the data patterns, the most likely causes for the anomaly are:

### Primary Hypothesis: Payment Gateway Outage

**Evidence:**
- Transactions dropped to exactly zero (not just low)
- Duration matches typical outage patterns (2-4 hours)
- Recovery was gradual, not instant

### Secondary Hypothesis: System/Server Failure

**Evidence:**
- Morning spike suggests backlog processing
- Pattern indicates complete system unavailability
- Not a network issue (would show partial transactions)

### Ruled Out:

- **Low demand**: Historical data shows peak hours consistently
- **Maintenance window**: Would not occur during peak hours
- **Data collection error**: Other hours recorded correctly

---

## 7. Recommendations

### Immediate Actions

1. **Investigate Logs**: Review system logs for 15:00-17:59 timeframe
2. **Check External Services**: Verify payment gateway status history
3. **Confirm Data Integrity**: Ensure no data collection gaps

### Monitoring Improvements

1. **Real-time Zero-Transaction Alert**: Trigger alarm if transactions = 0 for >15 minutes during business hours (10h-22h)

2. **Threshold-Based Alerts**:
   - Alert if current hour < 50% of hourly average
   - Alert if deviation > 2 standard deviations (Z-Score)

3. **Trend Monitoring**: Track 15-minute rolling windows to catch rapid drops

### Suggested Alert Rules

```python
# Rule 1: Zero Transaction Alert
if current_transactions == 0 and hour_of_day >= 10 and hour_of_day <= 22:
    trigger_alert(severity="CRITICAL", message="Zero transactions detected")

# Rule 2: Below Threshold Alert
if current_transactions < (hourly_average * 0.5):
    trigger_alert(severity="HIGH", message="Transactions below 50% of expected")

# Rule 3: Z-Score Alert
if abs(z_score) > 2:
    trigger_alert(severity="MEDIUM", message="Statistical anomaly detected")
```

---

## 8. Conclusion

The analysis successfully identified a **critical 3-hour system outage** in `checkout_2.csv` during peak afternoon hours. The combination of statistical analysis, SQL queries, and visualizations provides clear evidence of the anomaly and its business impact.

**Key Takeaways:**

- **checkout_1.csv**: Normal operational day ✅
- **checkout_2.csv**: Critical outage (15h-17h) 🚨
- **Estimated Impact**: ~62 lost transactions
- **Recommended Action**: Implement real-time monitoring with multi-threshold alerting

---

## 9. Appendix

### A. Files Delivered

| File | Description |
|------|-------------|
| `task_3_1_analysis.py` | Complete Python analysis script |
| `sql_queries.sql` | Standalone SQL queries |
| `anomaly_analysis_chart.png` | Multi-panel visualization |
| `anomaly_timeline.png` | Timeline focus chart |
| `ANALYSIS_REPORT.md` | This document |

### B. Environment

- Python 3.x
- Libraries: pandas, numpy, matplotlib, seaborn, pandasql
- Analysis performed on Ubuntu Linux

---

*"Where there is data smoke, there is business fire." — Thomas Redman*
