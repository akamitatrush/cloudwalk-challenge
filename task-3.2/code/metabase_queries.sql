-- ============================================================
-- TRANSACTION GUARDIAN - SQL QUERIES FOR METABASE
-- CloudWalk Task 3.2
-- ============================================================

-- ============================================================
-- 1. VISÃO GERAL - RESUMO DE TRANSAÇÕES
-- ============================================================

-- Query 1.1: Resumo geral
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'denied' THEN 1 ELSE 0 END) as denied,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN status = 'reversed' THEN 1 ELSE 0 END) as reversed,
    ROUND(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate_pct
FROM transactions;

-- Query 1.2: Transações por hora
SELECT 
    strftime('%H', timestamp) as hour,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status != 'approved' THEN 1 ELSE 0 END) as errors
FROM transactions
GROUP BY strftime('%H', timestamp)
ORDER BY hour;

-- ============================================================
-- 2. DETECÇÃO DE ANOMALIAS
-- ============================================================

-- Query 2.1: Horários com volume anômalo (baixo)
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour_bucket,
    COUNT(*) as transaction_count,
    AVG(count) as avg_volume,
    CASE 
        WHEN AVG(count) < 50 THEN '🚨 CRITICAL - Possível Outage'
        WHEN AVG(count) < 80 THEN '⚠️ WARNING - Volume Baixo'
        ELSE '✅ NORMAL'
    END as status
FROM transactions
GROUP BY hour_bucket
HAVING AVG(count) < 80
ORDER BY hour_bucket DESC;

-- Query 2.2: Horários com SPIKE
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour_bucket,
    AVG(count) as avg_volume,
    MAX(count) as max_volume,
    CASE 
        WHEN AVG(count) > 200 THEN '📈 SPIKE'
        ELSE '✅ NORMAL'
    END as status
FROM transactions
GROUP BY hour_bucket
HAVING AVG(count) > 150
ORDER BY avg_volume DESC;

-- Query 2.3: Transações problemáticas
SELECT 
    strftime('%Y-%m-%d %H:%M', timestamp) as time,
    status,
    count,
    auth_code,
    CASE 
        WHEN status = 'failed' THEN '❌ FALHA'
        WHEN status = 'denied' THEN '🚫 NEGADA'
        WHEN status = 'reversed' THEN '🔄 REVERTIDA'
    END as alert_type
FROM transactions
WHERE status IN ('failed', 'denied', 'reversed')
ORDER BY timestamp DESC
LIMIT 100;

-- Query 2.4: Z-Score para detecção de anomalias
WITH stats AS (
    SELECT 
        AVG(count) as mean_count,
        AVG(count * count) - AVG(count) * AVG(count) as variance
    FROM transactions
),
zscore_data AS (
    SELECT 
        t.timestamp,
        t.count,
        t.status,
        s.mean_count,
        SQRT(s.variance) as std_dev,
        (t.count - s.mean_count) / NULLIF(SQRT(s.variance), 0) as z_score
    FROM transactions t, stats s
)
SELECT 
    strftime('%Y-%m-%d %H:%M', timestamp) as time,
    count,
    status,
    ROUND(z_score, 2) as z_score,
    CASE 
        WHEN z_score < -2 THEN '🚨 MUITO BAIXO'
        WHEN z_score > 2 THEN '📈 MUITO ALTO'
        ELSE '✅ NORMAL'
    END as anomaly_status
FROM zscore_data
WHERE ABS(z_score) > 2
ORDER BY ABS(z_score) DESC
LIMIT 50;

-- ============================================================
-- 3. ANÁLISE POR STATUS
-- ============================================================

-- Query 3.1: Distribuição por status
SELECT 
    status,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
FROM transactions
GROUP BY status
ORDER BY total DESC;

-- Query 3.2: Taxa de falha por hora
SELECT 
    strftime('%H', timestamp) as hour,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    ROUND(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as failure_rate
FROM transactions
GROUP BY hour
ORDER BY hour;

-- Query 3.3: Taxa de negação por hora
SELECT 
    strftime('%H', timestamp) as hour,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'denied' THEN 1 ELSE 0 END) as denied,
    ROUND(SUM(CASE WHEN status = 'denied' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as denial_rate
FROM transactions
GROUP BY hour
ORDER BY hour;

-- ============================================================
-- 4. ANÁLISE POR AUTH CODE
-- ============================================================

-- Query 4.1: Distribuição por auth_code
SELECT 
    auth_code,
    CASE auth_code
        WHEN '00' THEN 'Aprovado'
        WHEN '05' THEN 'Não autorizado'
        WHEN '14' THEN 'Cartão inválido'
        WHEN '51' THEN 'Saldo insuficiente'
        WHEN '59' THEN 'Suspeita de fraude'
        ELSE 'Outro'
    END as description,
    COUNT(*) as total
FROM transactions
GROUP BY auth_code
ORDER BY total DESC;

-- Query 4.2: Auth codes problemáticos por hora
SELECT 
    strftime('%H', timestamp) as hour,
    auth_code,
    COUNT(*) as occurrences
FROM transactions
WHERE auth_code != '00'
GROUP BY hour, auth_code
ORDER BY hour, occurrences DESC;

-- ============================================================
-- 5. ANÁLISE TEMPORAL
-- ============================================================

-- Query 5.1: Volume por minuto (últimas 2 horas)
SELECT 
    strftime('%Y-%m-%d %H:%M', timestamp) as minute,
    COUNT(*) as transactions,
    AVG(count) as avg_volume,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
FROM transactions
WHERE timestamp >= datetime('now', '-2 hours')
GROUP BY minute
ORDER BY minute;

-- Query 5.2: Comparação hora atual vs hora anterior
WITH current_hour AS (
    SELECT COUNT(*) as current_count
    FROM transactions
    WHERE strftime('%H', timestamp) = strftime('%H', 'now')
),
previous_hour AS (
    SELECT COUNT(*) as previous_count
    FROM transactions
    WHERE strftime('%H', timestamp) = strftime('%H', 'now', '-1 hour')
)
SELECT 
    c.current_count,
    p.previous_count,
    c.current_count - p.previous_count as difference,
    ROUND((c.current_count - p.previous_count) * 100.0 / NULLIF(p.previous_count, 0), 2) as change_pct
FROM current_hour c, previous_hour p;

-- Query 5.3: Padrão semanal
SELECT 
    CASE strftime('%w', timestamp)
        WHEN '0' THEN 'Domingo'
        WHEN '1' THEN 'Segunda'
        WHEN '2' THEN 'Terça'
        WHEN '3' THEN 'Quarta'
        WHEN '4' THEN 'Quinta'
        WHEN '5' THEN 'Sexta'
        WHEN '6' THEN 'Sábado'
    END as day_of_week,
    COUNT(*) as total_transactions,
    AVG(count) as avg_volume,
    ROUND(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate
FROM transactions
GROUP BY strftime('%w', timestamp)
ORDER BY strftime('%w', timestamp);

-- ============================================================
-- 6. ALERTAS E INCIDENTES
-- ============================================================

-- Query 6.1: Períodos de outage
SELECT 
    strftime('%Y-%m-%d %H:%M', timestamp) as period,
    AVG(count) as avg_volume,
    '🚨 POSSÍVEL OUTAGE' as alert
FROM transactions
GROUP BY strftime('%Y-%m-%d %H', timestamp)
HAVING AVG(count) < 50
ORDER BY period DESC;

-- Query 6.2: Alta taxa de erro
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    COUNT(*) as total,
    SUM(CASE WHEN status IN ('failed', 'denied', 'reversed') THEN 1 ELSE 0 END) as errors,
    ROUND(SUM(CASE WHEN status IN ('failed', 'denied', 'reversed') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as error_rate,
    CASE 
        WHEN SUM(CASE WHEN status IN ('failed', 'denied', 'reversed') THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 20 THEN '🚨 CRÍTICO'
        WHEN SUM(CASE WHEN status IN ('failed', 'denied', 'reversed') THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 10 THEN '⚠️ ALERTA'
        ELSE '✅ NORMAL'
    END as severity
FROM transactions
GROUP BY hour
HAVING error_rate > 5
ORDER BY error_rate DESC;

-- Query 6.3: Top 10 piores momentos
SELECT 
    strftime('%Y-%m-%d %H:%M', timestamp) as time,
    count as volume,
    status,
    '🚨 BAIXO VOLUME' as alert
FROM transactions
ORDER BY count ASC
LIMIT 10;

-- ============================================================
-- 7. KPIs EXECUTIVOS
-- ============================================================

-- Query 7.1: Dashboard KPIs
SELECT 'Total Transações' as metric, CAST(COUNT(*) AS TEXT) as value FROM transactions
UNION ALL
SELECT 'Taxa de Aprovação', ROUND(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) || '%' FROM transactions
UNION ALL
SELECT 'Taxa de Falha', ROUND(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) || '%' FROM transactions
UNION ALL
SELECT 'Volume Médio', CAST(ROUND(AVG(count), 0) AS TEXT) || ' tx/min' FROM transactions
UNION ALL
SELECT 'Anomalias (Volume < 50)', CAST(SUM(CASE WHEN count < 50 THEN 1 ELSE 0 END) AS TEXT) FROM transactions;

-- Query 7.2: Saúde do sistema
SELECT 
    CASE 
        WHEN AVG(count) < 50 THEN '🔴 CRITICAL'
        WHEN AVG(count) < 80 THEN '🟡 WARNING'
        ELSE '🟢 HEALTHY'
    END as system_status,
    COUNT(*) as total_transactions,
    ROUND(AVG(count), 2) as avg_volume,
    ROUND(SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate
FROM transactions;

-- ============================================================
-- 8. QUERIES PARA GRÁFICOS
-- ============================================================

-- Query 8.1: Linha do tempo de volume
SELECT 
    strftime('%H:%M', timestamp) as time,
    count as volume
FROM transactions
ORDER BY timestamp
LIMIT 200;

-- Query 8.2: Pizza de distribuição de status
SELECT 
    status,
    COUNT(*) as count
FROM transactions
GROUP BY status;

-- Query 8.3: Barras de volume por hora
SELECT 
    strftime('%H', timestamp) || 'h' as hour,
    AVG(count) as avg_volume,
    MAX(count) as max_volume,
    MIN(count) as min_volume
FROM transactions
GROUP BY strftime('%H', timestamp)
ORDER BY hour;
