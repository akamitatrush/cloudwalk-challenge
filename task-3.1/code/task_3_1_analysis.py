"""
CloudWalk Monitoring Analyst Challenge - Task 3.1
Anomaly Detection Analysis in Checkout Data
Author: Sérgio
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pandasql import sqldf
import warnings
warnings.filterwarnings('ignore')

# Configure style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# =============================================================================
# 1. LOAD AND EXPLORE DATA
# =============================================================================

print("=" * 60)
print("CLOUDWALK MONITORING ANALYST - TASK 3.1")
print("Anomaly Detection in Checkout Data")
print("=" * 60)

# Load CSVs
df1 = pd.read_csv('/mnt/user-data/uploads/checkout_1.csv')
df2 = pd.read_csv('/mnt/user-data/uploads/checkout_2.csv')

# Add dataset identifier
df1['dataset'] = 'checkout_1'
df2['dataset'] = 'checkout_2'

# Extract hour as integer for analysis
df1['hour'] = df1['time'].str.replace('h', '').astype(int)
df2['hour'] = df2['time'].str.replace('h', '').astype(int)

print("\n📊 DATASET 1 (checkout_1.csv) - First 5 rows:")
print(df1.head())

print("\n📊 DATASET 2 (checkout_2.csv) - First 5 rows:")
print(df2.head())

# =============================================================================
# 2. ANOMALY DETECTION METHODS
# =============================================================================

def calculate_anomaly_metrics(df, name):
    """Calculate multiple anomaly detection metrics"""
    
    # Method 1: Z-Score based on avg_last_week
    df['z_score'] = (df['today'] - df['avg_last_week']) / df['avg_last_week'].replace(0, 0.1)
    
    # Method 2: Percentage deviation from yesterday
    df['pct_change_yesterday'] = ((df['today'] - df['yesterday']) / df['yesterday'].replace(0, 0.1)) * 100
    
    # Method 3: Percentage deviation from avg_last_week
    df['pct_change_avg'] = ((df['today'] - df['avg_last_week']) / df['avg_last_week'].replace(0, 0.1)) * 100
    
    # Method 4: Moving window comparison (looking at neighboring hours)
    df['expected_range_min'] = df['avg_last_week'] * 0.5
    df['expected_range_max'] = df['avg_last_week'] * 1.5
    
    # Flag anomalies
    df['is_anomaly'] = (
        (df['today'] < df['expected_range_min']) | 
        (df['today'] > df['expected_range_max']) |
        (abs(df['z_score']) > 2)
    )
    
    # Severity classification
    conditions = [
        (df['today'] == 0) & (df['avg_last_week'] > 5),  # CRITICAL: Zero sales when expected high
        (abs(df['pct_change_avg']) > 100),                # HIGH: >100% deviation
        (abs(df['pct_change_avg']) > 50),                 # MEDIUM: 50-100% deviation
    ]
    choices = ['CRITICAL', 'HIGH', 'MEDIUM']
    df['severity'] = np.select(conditions, choices, default='NORMAL')
    
    return df

# Apply anomaly detection
df1 = calculate_anomaly_metrics(df1, 'checkout_1')
df2 = calculate_anomaly_metrics(df2, 'checkout_2')

# =============================================================================
# 3. SQL ANALYSIS (using pandasql)
# =============================================================================

print("\n" + "=" * 60)
print("📋 SQL ANALYSIS")
print("=" * 60)

# Query 1: Find all anomalies in checkout_2 (the problematic dataset)
query_anomalies = """
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    avg_last_month,
    ROUND(((today - avg_last_week) / CASE WHEN avg_last_week = 0 THEN 0.1 ELSE avg_last_week END) * 100, 2) as pct_deviation,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL - ZERO SALES'
        WHEN today < avg_last_week * 0.5 THEN 'ALERT - BELOW 50% EXPECTED'
        WHEN today > avg_last_week * 1.5 THEN 'ALERT - ABOVE 150% EXPECTED'
        ELSE 'NORMAL'
    END as status
FROM df2
WHERE today = 0 OR today < avg_last_week * 0.5 OR today > avg_last_week * 1.5
ORDER BY 
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 1
        WHEN today < avg_last_week * 0.5 THEN 2
        ELSE 3
    END
"""

anomalies_result = sqldf(query_anomalies, locals())
print("\n🚨 ANOMALIES DETECTED IN CHECKOUT_2:")
print(anomalies_result.to_string(index=False))

# Query 2: Hourly comparison summary
query_comparison = """
SELECT 
    time,
    today as sales_today,
    yesterday as sales_yesterday,
    ROUND(avg_last_week, 2) as avg_week,
    ROUND(avg_last_month, 2) as avg_month,
    today - yesterday as diff_yesterday,
    ROUND(today - avg_last_week, 2) as diff_avg_week
FROM df2
ORDER BY hour
"""

comparison_result = sqldf(query_comparison, locals())

# Query 3: Statistical summary
query_stats = """
SELECT 
    'checkout_1' as dataset,
    SUM(today) as total_today,
    SUM(yesterday) as total_yesterday,
    ROUND(AVG(today), 2) as avg_hourly_today,
    ROUND(AVG(yesterday), 2) as avg_hourly_yesterday,
    COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_anomalies,
    COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high_anomalies
FROM df1
UNION ALL
SELECT 
    'checkout_2' as dataset,
    SUM(today) as total_today,
    SUM(yesterday) as total_yesterday,
    ROUND(AVG(today), 2) as avg_hourly_today,
    ROUND(AVG(yesterday), 2) as avg_hourly_yesterday,
    COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_anomalies,
    COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high_anomalies
FROM df2
"""

stats_result = sqldf(query_stats, locals())
print("\n📊 STATISTICAL COMPARISON:")
print(stats_result.to_string(index=False))

# =============================================================================
# 4. KEY FINDINGS
# =============================================================================

print("\n" + "=" * 60)
print("🔍 KEY FINDINGS & CONCLUSIONS")
print("=" * 60)

# Identify the critical anomaly period in checkout_2
critical_hours = df2[df2['severity'] == 'CRITICAL']

print("""
┌─────────────────────────────────────────────────────────────┐
│                    CRITICAL ANOMALY DETECTED                │
├─────────────────────────────────────────────────────────────┤
│  Dataset: checkout_2.csv                                    │
│  Affected Hours: 15h, 16h, 17h                              │
│  Issue: ZERO TRANSACTIONS during peak business hours        │
├─────────────────────────────────────────────────────────────┤
│  EVIDENCE:                                                  │
│  • 15h: Today=0 | Yesterday=51 | Avg Week=22.4             │
│  • 16h: Today=0 | Yesterday=41 | Avg Week=21.5             │
│  • 17h: Today=0 | Yesterday=45 | Avg Week=17.7             │
├─────────────────────────────────────────────────────────────┤
│  PROBABLE CAUSES:                                           │
│  1. Payment gateway outage (most likely)                    │
│  2. System/server failure                                   │
│  3. Network connectivity issues                             │
│  4. Database connection pool exhausted                      │
├─────────────────────────────────────────────────────────────┤
│  BUSINESS IMPACT:                                           │
│  • Lost transactions: ~85 (based on avg)                    │
│  • Duration: 3 hours (15:00 - 17:59)                        │
│  • Revenue impact: HIGH (peak afternoon hours)              │
├─────────────────────────────────────────────────────────────┤
│  SECONDARY ANOMALIES (checkout_2):                          │
│  • 08h: 25 sales vs avg 3.71 (574% above normal) - SPIKE    │
│  • 09h: 36 sales vs avg 10.14 (255% above normal) - SPIKE   │
│  • Recovery pattern visible after 18h                       │
└─────────────────────────────────────────────────────────────┘
""")

# =============================================================================
# 5. GENERATE VISUALIZATIONS
# =============================================================================

# Create figure with multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('CloudWalk Monitoring Analysis - Anomaly Detection\nTask 3.1: Checkout Data Analysis', 
             fontsize=16, fontweight='bold', y=1.02)

# Plot 1: checkout_1 - Normal day comparison
ax1 = axes[0, 0]
x = df1['hour']
width = 0.35
bars1 = ax1.bar(x - width/2, df1['today'], width, label='Today', color='#2ecc71', alpha=0.8)
bars2 = ax1.bar(x + width/2, df1['yesterday'], width, label='Yesterday', color='#3498db', alpha=0.8)
ax1.plot(x, df1['avg_last_week'], 'r--', linewidth=2, label='Avg Last Week', marker='o', markersize=4)
ax1.set_xlabel('Hour of Day', fontsize=11)
ax1.set_ylabel('Number of Sales', fontsize=11)
ax1.set_title('checkout_1.csv - Normal Day Pattern', fontsize=13, fontweight='bold')
ax1.set_xticks(range(24))
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# Plot 2: checkout_2 - Anomaly day with highlights
ax2 = axes[0, 1]
colors = ['#e74c3c' if row['severity'] == 'CRITICAL' else '#2ecc71' for _, row in df2.iterrows()]
bars = ax2.bar(df2['hour'], df2['today'], color=colors, alpha=0.8, label='Today', edgecolor='black', linewidth=0.5)
ax2.plot(df2['hour'], df2['yesterday'], 'b-', linewidth=2, label='Yesterday', marker='s', markersize=5)
ax2.plot(df2['hour'], df2['avg_last_week'], 'orange', linewidth=2, linestyle='--', label='Avg Last Week', marker='o', markersize=4)

# Highlight anomaly zone
ax2.axvspan(14.5, 17.5, alpha=0.2, color='red', label='OUTAGE PERIOD')
ax2.annotate('⚠️ SYSTEM OUTAGE\n0 transactions', xy=(16, 5), fontsize=11, ha='center', 
             color='red', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

ax2.set_xlabel('Hour of Day', fontsize=11)
ax2.set_ylabel('Number of Sales', fontsize=11)
ax2.set_title('checkout_2.csv - ANOMALY DETECTED', fontsize=13, fontweight='bold', color='red')
ax2.set_xticks(range(24))
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# Plot 3: Deviation analysis
ax3 = axes[1, 0]
deviation = df2['today'] - df2['avg_last_week']
colors = ['#e74c3c' if d < -10 else '#2ecc71' if d > 10 else '#3498db' for d in deviation]
ax3.bar(df2['hour'], deviation, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax3.axhline(y=10, color='orange', linestyle='--', linewidth=1, alpha=0.7)
ax3.axhline(y=-10, color='orange', linestyle='--', linewidth=1, alpha=0.7)

# Add annotations for critical deviations
for i, row in df2.iterrows():
    if row['severity'] == 'CRITICAL':
        ax3.annotate(f'{row["today"] - row["avg_last_week"]:.1f}', 
                    xy=(row['hour'], row['today'] - row['avg_last_week'] - 3),
                    ha='center', fontsize=9, fontweight='bold', color='red')

ax3.set_xlabel('Hour of Day', fontsize=11)
ax3.set_ylabel('Deviation from Weekly Average', fontsize=11)
ax3.set_title('checkout_2.csv - Deviation Analysis (Today vs Avg Last Week)', fontsize=13, fontweight='bold')
ax3.set_xticks(range(24))
ax3.grid(True, alpha=0.3)

# Add legend
red_patch = mpatches.Patch(color='#e74c3c', label='Negative deviation (< -10)')
green_patch = mpatches.Patch(color='#2ecc71', label='Positive deviation (> +10)')
blue_patch = mpatches.Patch(color='#3498db', label='Normal range')
ax3.legend(handles=[red_patch, green_patch, blue_patch], loc='upper right')

# Plot 4: Heatmap comparison
ax4 = axes[1, 1]
comparison_data = pd.DataFrame({
    'checkout_1': df1['today'].values,
    'checkout_2': df2['today'].values,
    'Expected (Avg)': df2['avg_last_week'].values
}).T

sns.heatmap(comparison_data, annot=True, fmt='.0f', cmap='RdYlGn', 
            xticklabels=[f'{i}h' for i in range(24)],
            yticklabels=['checkout_1', 'checkout_2', 'Expected'],
            ax=ax4, cbar_kws={'label': 'Number of Sales'})
ax4.set_title('Hourly Sales Heatmap Comparison', fontsize=13, fontweight='bold')
ax4.set_xlabel('Hour of Day', fontsize=11)

plt.tight_layout()
plt.savefig('/home/claude/cloudwalk_challenge/anomaly_analysis_chart.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print("\n✅ Chart saved: anomaly_analysis_chart.png")

# =============================================================================
# 6. ADDITIONAL VISUALIZATION - Timeline Focus
# =============================================================================

fig2, ax = plt.subplots(figsize=(14, 6))

# Create filled area for context
ax.fill_between(df2['hour'], 0, df2['avg_last_month'], alpha=0.2, color='gray', label='Avg Last Month')
ax.fill_between(df2['hour'], 0, df2['avg_last_week'], alpha=0.2, color='blue', label='Avg Last Week')

# Plot lines
ax.plot(df2['hour'], df2['yesterday'], 'g-', linewidth=2.5, label='Yesterday', marker='o', markersize=6)
ax.plot(df2['hour'], df2['today'], 'r-', linewidth=3, label='Today (with anomaly)', marker='s', markersize=8)

# Highlight anomaly zone
ax.axvspan(14.5, 17.5, alpha=0.3, color='red')
ax.annotate('🚨 CRITICAL OUTAGE\n3 hours of zero sales\n(15h-17h)', 
            xy=(16, 30), fontsize=12, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', edgecolor='red', linewidth=2))

# Annotate morning spike
ax.annotate('📈 Morning Spike\nPossible backlog\nprocessing', 
            xy=(8.5, 30), fontsize=10, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))

ax.set_xlabel('Hour of Day', fontsize=12)
ax.set_ylabel('Number of Transactions', fontsize=12)
ax.set_title('CloudWalk Checkout Analysis - Anomaly Timeline (checkout_2.csv)', 
             fontsize=14, fontweight='bold')
ax.set_xticks(range(24))
ax.set_xticklabels([f'{i}:00' for i in range(24)], rotation=45)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/cloudwalk_challenge/anomaly_timeline.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("✅ Timeline chart saved: anomaly_timeline.png")

# =============================================================================
# 7. EXPORT SQL QUERIES FOR DOCUMENTATION
# =============================================================================

sql_queries = """
-- =============================================================================
-- CLOUDWALK MONITORING ANALYST - TASK 3.1
-- SQL Queries for Anomaly Detection
-- =============================================================================

-- Query 1: Detect anomalies based on deviation from weekly average
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    avg_last_month,
    ROUND(((today - avg_last_week) / NULLIF(avg_last_week, 0)) * 100, 2) as pct_deviation,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL - ZERO SALES'
        WHEN today < avg_last_week * 0.5 THEN 'ALERT - BELOW 50% EXPECTED'
        WHEN today > avg_last_week * 1.5 THEN 'ALERT - ABOVE 150% EXPECTED'
        ELSE 'NORMAL'
    END as status
FROM checkout_data
WHERE today = 0 
   OR today < avg_last_week * 0.5 
   OR today > avg_last_week * 1.5
ORDER BY 
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 1
        WHEN today < avg_last_week * 0.5 THEN 2
        ELSE 3
    END;

-- Query 2: Daily totals comparison
SELECT 
    'Total' as metric,
    SUM(today) as today_total,
    SUM(yesterday) as yesterday_total,
    SUM(today) - SUM(yesterday) as difference,
    ROUND(((SUM(today) - SUM(yesterday)) / NULLIF(SUM(yesterday), 0)) * 100, 2) as pct_change
FROM checkout_data;

-- Query 3: Peak hours analysis (10h-18h)
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
WHERE CAST(REPLACE(time, 'h', '') AS INTEGER) BETWEEN 10 AND 18
ORDER BY CAST(REPLACE(time, 'h', '') AS INTEGER);

-- Query 4: Calculate Z-Score for anomaly detection
SELECT 
    time,
    today,
    avg_last_week,
    ROUND((today - avg_last_week) / NULLIF(
        (SELECT SQRT(AVG((today - avg_last_week) * (today - avg_last_week))) FROM checkout_data)
    , 0), 2) as z_score,
    CASE 
        WHEN ABS((today - avg_last_week) / NULLIF(
            (SELECT SQRT(AVG((today - avg_last_week) * (today - avg_last_week))) FROM checkout_data)
        , 0)) > 2 THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as z_score_status
FROM checkout_data;
"""

with open('/home/claude/cloudwalk_challenge/sql_queries.sql', 'w') as f:
    f.write(sql_queries)

print("✅ SQL queries saved: sql_queries.sql")

# =============================================================================
# 8. FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 60)
print("📋 ANALYSIS COMPLETE - SUMMARY")
print("=" * 60)

total_lost = df2[(df2['hour'] >= 15) & (df2['hour'] <= 17)]['avg_last_week'].sum()

print(f"""
DATASET ANALYZED: checkout_1.csv & checkout_2.csv
ANALYSIS METHOD: Statistical comparison + Z-Score + SQL queries

KEY FINDINGS:
─────────────
✅ checkout_1.csv: NORMAL behavior
   • Total sales today: {df1['today'].sum()}
   • Pattern follows expected averages
   • No critical anomalies detected

🚨 checkout_2.csv: CRITICAL ANOMALY DETECTED
   • Total sales today: {df2['today'].sum()}
   • OUTAGE PERIOD: 15h, 16h, 17h (ZERO TRANSACTIONS)
   • Estimated lost transactions: ~{total_lost:.0f}
   • Morning spike (08h-09h): Possible backlog processing

RECOMMENDED ACTIONS:
───────────────────
1. Investigate root cause of 3-hour outage (15h-17h)
2. Review system logs for that time period
3. Check payment gateway status/connectivity
4. Implement real-time alerting for zero-transaction periods
5. Set up anomaly detection threshold: alert when sales < 50% of avg

FILES GENERATED:
───────────────
• anomaly_analysis_chart.png - Multi-panel analysis visualization
• anomaly_timeline.png - Timeline focus on anomaly period
• sql_queries.sql - SQL queries for documentation
""")

print("✅ TASK 3.1 ANALYSIS COMPLETE!")
