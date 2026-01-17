# 📊 PromQL Cheatsheet - CloudWalk Monitoring

## Quick Reference for Night Shift Analysts

---

## 🔍 BASIC QUERIES

### Instant Queries (Current Value)

```promql
# Current transactions
checkout_transactions_current

# All hourly data for today
checkout_transactions_hourly{period="today"}

# Specific hour
checkout_transactions_hourly{hour="15h", period="today"}

# Filter by dataset
checkout_transactions_hourly{dataset="checkout_2"}
```

### Range Queries (Over Time)

```promql
# Last 5 minutes
checkout_transactions_current[5m]

# Last 1 hour
checkout_transactions_current[1h]

# Last 24 hours
checkout_transactions_current[24h]

# Last 7 days
checkout_transactions_current[7d]
```

---

## 📈 AGGREGATION FUNCTIONS

### Basic Aggregations

```promql
# Sum all transactions
sum(checkout_transactions_hourly{period="today"})

# Average
avg(checkout_transactions_hourly{period="today"})

# Maximum
max(checkout_transactions_hourly{period="today"})

# Minimum (useful for finding zeros)
min(checkout_transactions_hourly{period="today"})

# Count of series
count(checkout_transactions_hourly{period="today"})
```

### Group By (by label)

```promql
# Sum by dataset
sum by (dataset) (checkout_transactions_hourly{period="today"})

# Average by hour
avg by (hour) (checkout_transactions_hourly)

# Without specific label
sum without (hour) (checkout_transactions_hourly{period="today"})
```

---

## 📉 RATE AND CHANGE FUNCTIONS

### Rate (for counters)

```promql
# Per-second rate over 5 minutes
rate(checkout_transactions_total[5m])

# Per-minute rate
rate(checkout_transactions_total[5m]) * 60

# Per-hour rate
rate(checkout_transactions_total[5m]) * 3600
```

### Increase

```promql
# Total increase over 1 hour
increase(checkout_transactions_total[1h])

# Increase over 24 hours
increase(checkout_transactions_total[24h])
```

### Delta (for gauges)

```promql
# Change over last hour
delta(checkout_transactions_current[1h])
```

---

## ⏱️ OVER TIME FUNCTIONS

### Aggregations Over Time

```promql
# Average over last 24 hours
avg_over_time(checkout_transactions_current[24h])

# Max over last week
max_over_time(checkout_transactions_current[7d])

# Min over last week (find lowest)
min_over_time(checkout_transactions_current[7d])

# Standard deviation
stddev_over_time(checkout_transactions_current[7d])

# Count of samples
count_over_time(checkout_transactions_current[1h])
```

### Specific Time Functions

```promql
# Last value in range
last_over_time(checkout_transactions_current[1h])

# First value in range
first_over_time(checkout_transactions_current[1h])

# Quantile (e.g., 95th percentile)
quantile_over_time(0.95, checkout_transactions_current[24h])
```

---

## 🚨 ANOMALY DETECTION QUERIES

### Zero Detection

```promql
# Find hours with zero transactions
checkout_transactions_hourly{period="today"} == 0

# Count of zero-transaction hours
count(checkout_transactions_hourly{period="today"} == 0)

# Zero during business hours (10-22)
checkout_transactions_hourly{period="today"} == 0 
  and ON() hour() >= 10 
  and ON() hour() <= 22
```

### Deviation Calculations

```promql
# Percentage deviation from average
((checkout_transactions_current - checkout_transactions_avg_week) 
  / checkout_transactions_avg_week) * 100

# Absolute deviation
checkout_transactions_current - checkout_transactions_avg_week

# Below 50% of expected
checkout_transactions_hourly{period="today"} 
  < checkout_transactions_hourly{period="avg_last_week"} * 0.5

# Above 200% of expected (spike)
checkout_transactions_hourly{period="today"} 
  > checkout_transactions_hourly{period="avg_last_week"} * 2
```

### Z-Score Calculation

```promql
# Z-Score (standard deviations from mean)
(checkout_transactions_current 
  - avg_over_time(checkout_transactions_current[7d]))
  / stddev_over_time(checkout_transactions_current[7d])

# Anomaly when Z-Score > 2 or < -2
abs(
  (checkout_transactions_current 
    - avg_over_time(checkout_transactions_current[7d]))
  / stddev_over_time(checkout_transactions_current[7d])
) > 2
```

---

## 🔧 COMPARISON OPERATORS

### Numeric Comparisons

```promql
# Equal to
checkout_transactions_current == 0

# Not equal
checkout_transactions_current != 0

# Greater than
checkout_transactions_current > 50

# Less than
checkout_transactions_current < 10

# Greater or equal
checkout_transactions_current >= 20

# Less or equal
checkout_transactions_current <= 5
```

### Boolean Logic

```promql
# AND (both conditions)
checkout_transactions_current > 0 and checkout_transactions_current < 50

# OR (either condition)
checkout_transactions_current == 0 or checkout_transactions_current > 100

# UNLESS (exclude)
checkout_transactions_hourly{period="today"} unless checkout_transactions_hourly{period="today"} > 10
```

---

## 📋 LABEL OPERATIONS

### Label Filtering

```promql
# Exact match
checkout_transactions_hourly{period="today"}

# Regex match
checkout_transactions_hourly{period=~"today|yesterday"}

# Negative match
checkout_transactions_hourly{period!="avg_last_week"}

# Regex negative
checkout_transactions_hourly{period!~"avg.*"}
```

### Label Functions

```promql
# Replace label value
label_replace(
  checkout_transactions_hourly,
  "new_label", "$1", "hour", "(.*)h"
)

# Join labels
label_join(
  checkout_transactions_hourly,
  "combined", "-", "dataset", "hour"
)
```

---

## 🎯 COMMON MONITORING PATTERNS

### SLI/SLO Patterns

```promql
# Availability (transactions > 0)
avg_over_time(
  (checkout_transactions_current > 0)[24h:1h]
) * 100

# Error rate (if you have error metric)
rate(checkout_errors_total[5m]) 
  / rate(checkout_transactions_total[5m]) * 100
```

### Alerting Patterns

```promql
# Alert: Zero transactions for 5+ minutes
checkout_transactions_current == 0

# Alert: 50% drop from yesterday
checkout_transactions_current 
  < checkout_transactions_hourly{period="yesterday"} * 0.5

# Alert: Sustained low volume (15 min)
avg_over_time(checkout_transactions_current[15m]) < 5
```

### Dashboard Patterns

```promql
# Today vs Yesterday comparison
checkout_transactions_hourly{period="today"} 
  - checkout_transactions_hourly{period="yesterday"}

# Trend (is it improving?)
deriv(checkout_transactions_current[1h])

# Moving average (smooth the line)
avg_over_time(checkout_transactions_current[30m])
```

---

## 💡 PRO TIPS

### 1. Use Offset for Past Comparisons
```promql
# Value from 1 hour ago
checkout_transactions_current offset 1h

# Value from yesterday
checkout_transactions_current offset 24h

# Value from last week
checkout_transactions_current offset 7d
```

### 2. Clamp Values to Avoid Division by Zero
```promql
# Safe division
checkout_transactions_current 
  / clamp_min(checkout_transactions_avg_week, 0.1) * 100
```

### 3. Use Subqueries for Complex Analysis
```promql
# Average of hourly maximums
avg_over_time(
  max_over_time(checkout_transactions_current[1h])[24h:1h]
)
```

### 4. Handle Missing Data
```promql
# Fill missing with 0
checkout_transactions_current or vector(0)

# Check if metric exists
absent(checkout_transactions_current)
```

---

## 🔗 Quick Reference Card

| What You Want | Query Pattern |
|--------------|---------------|
| Current value | `metric_name` |
| Filter by label | `metric{label="value"}` |
| Sum all | `sum(metric)` |
| Average | `avg(metric)` |
| Rate per second | `rate(counter[5m])` |
| Increase | `increase(counter[1h])` |
| Average over time | `avg_over_time(gauge[1h])` |
| Percentage change | `(new - old) / old * 100` |
| Z-Score | `(val - avg) / stddev` |

---

*Created for CloudWalk Monitoring Analyst Challenge*
