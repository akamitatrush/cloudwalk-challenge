
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
