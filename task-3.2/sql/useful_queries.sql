-- =============================================================================
-- 🔍 Transaction Guardian - Useful Queries for Monitoring
-- =============================================================================
-- Queries otimizadas para TimescaleDB
-- Úteis para Night Shift, investigação de incidentes e análise
-- =============================================================================

-- =============================================================================
-- 📊 1. VISÃO GERAL (Overview)
-- =============================================================================

-- 1.1 Contagem total de transações
SELECT COUNT(*) AS total_transactions FROM transactions;

-- 1.2 Distribuição por status
SELECT 
    status,
    COUNT(*) AS total,
    ROUND((COUNT(*)::numeric / SUM(COUNT(*)) OVER()) * 100, 2) AS percentage
FROM transactions
GROUP BY status
ORDER BY total DESC;

-- 1.3 Resumo das últimas 24 horas
SELECT 
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 2
    ) AS approval_rate_pct
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours';

-- =============================================================================
-- ⏰ 2. ANÁLISE TEMPORAL (Time-based Analysis)
-- =============================================================================

-- 2.1 Transações por hora (últimas 24h)
SELECT 
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- 2.2 Transações por minuto (última hora) - Para detectar spikes
SELECT 
    date_trunc('minute', timestamp) AS minute,
    COUNT(*) AS total
FROM transactions
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute DESC;

-- 2.3 Comparação hora atual vs mesma hora ontem
WITH current_hour AS (
    SELECT COUNT(*) AS count
    FROM transactions
    WHERE timestamp > date_trunc('hour', NOW())
),
yesterday_hour AS (
    SELECT COUNT(*) AS count
    FROM transactions
    WHERE timestamp BETWEEN 
        date_trunc('hour', NOW() - INTERVAL '1 day') 
        AND date_trunc('hour', NOW() - INTERVAL '1 day') + INTERVAL '1 hour'
)
SELECT 
    c.count AS current_hour,
    y.count AS yesterday_same_hour,
    ROUND(((c.count - y.count)::numeric / NULLIF(y.count, 0) * 100), 2) AS change_pct
FROM current_hour c, yesterday_hour y;

-- 2.4 Padrão por dia da semana
SELECT 
    EXTRACT(dow FROM timestamp) AS day_of_week,
    CASE EXTRACT(dow FROM timestamp)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Segunda'
        WHEN 2 THEN 'Terça'
        WHEN 3 THEN 'Quarta'
        WHEN 4 THEN 'Quinta'
        WHEN 5 THEN 'Sexta'
        WHEN 6 THEN 'Sábado'
    END AS day_name,
    COUNT(*) AS total,
    ROUND(AVG(COUNT(*)) OVER(), 0) AS avg_all_days
FROM transactions
GROUP BY day_of_week
ORDER BY day_of_week;

-- 2.5 Padrão por hora do dia (para identificar horários de pico)
SELECT 
    EXTRACT(hour FROM timestamp) AS hour_of_day,
    COUNT(*) AS total,
    ROUND(AVG(COUNT(*)) OVER(), 0) AS avg_all_hours
FROM transactions
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- =============================================================================
-- 🚨 3. DETECÇÃO DE ANOMALIAS (Anomaly Detection)
-- =============================================================================

-- 3.1 Horas com ZERO transações (outage detection)
SELECT 
    generate_series AS hour,
    COALESCE(tx.count, 0) AS transactions
FROM generate_series(
    date_trunc('hour', NOW() - INTERVAL '24 hours'),
    date_trunc('hour', NOW()),
    '1 hour'::interval
) 
LEFT JOIN (
    SELECT date_trunc('hour', timestamp) AS hour, COUNT(*) AS count
    FROM transactions
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY 1
) tx ON generate_series = tx.hour
WHERE COALESCE(tx.count, 0) = 0
ORDER BY hour;

-- 3.2 Calcular Z-Score para volume por hora (anomalias estatísticas)
WITH hourly_stats AS (
    SELECT 
        date_trunc('hour', timestamp) AS hour,
        COUNT(*) AS count
    FROM transactions
    WHERE timestamp > NOW() - INTERVAL '7 days'
    GROUP BY 1
),
stats AS (
    SELECT 
        AVG(count) AS avg_count,
        STDDEV(count) AS stddev_count
    FROM hourly_stats
)
SELECT 
    h.hour,
    h.count,
    ROUND(s.avg_count, 0) AS avg,
    ROUND(s.stddev_count, 2) AS stddev,
    ROUND((h.count - s.avg_count) / NULLIF(s.stddev_count, 0), 2) AS z_score,
    CASE 
        WHEN ABS((h.count - s.avg_count) / NULLIF(s.stddev_count, 0)) > 2.5 THEN '🚨 ANOMALIA'
        WHEN ABS((h.count - s.avg_count) / NULLIF(s.stddev_count, 0)) > 2 THEN '⚠️ ATENÇÃO'
        ELSE '✅ NORMAL'
    END AS status
FROM hourly_stats h, stats s
ORDER BY h.hour DESC
LIMIT 24;

-- 3.3 Taxa de falha por hora (detectar degradação)
SELECT 
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status IN ('failed', 'denied')) AS failures,
    ROUND(
        (COUNT(*) FILTER (WHERE status IN ('failed', 'denied'))::numeric / 
         NULLIF(COUNT(*), 0) * 100), 2
    ) AS failure_rate_pct,
    CASE 
        WHEN (COUNT(*) FILTER (WHERE status IN ('failed', 'denied'))::numeric / 
              NULLIF(COUNT(*), 0) * 100) > 20 THEN '🚨 CRÍTICO'
        WHEN (COUNT(*) FILTER (WHERE status IN ('failed', 'denied'))::numeric / 
              NULLIF(COUNT(*), 0) * 100) > 10 THEN '⚠️ ALTO'
        ELSE '✅ NORMAL'
    END AS alert_level
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- 3.4 Detectar gaps (períodos sem transações)
WITH time_series AS (
    SELECT generate_series(
        date_trunc('minute', NOW() - INTERVAL '4 hours'),
        date_trunc('minute', NOW()),
        '1 minute'::interval
    ) AS minute
),
tx_per_minute AS (
    SELECT 
        date_trunc('minute', timestamp) AS minute,
        COUNT(*) AS count
    FROM transactions
    WHERE timestamp > NOW() - INTERVAL '4 hours'
    GROUP BY 1
)
SELECT 
    ts.minute,
    COALESCE(tx.count, 0) AS transactions
FROM time_series ts
LEFT JOIN tx_per_minute tx ON ts.minute = tx.minute
WHERE COALESCE(tx.count, 0) = 0
ORDER BY ts.minute DESC;

-- =============================================================================
-- 📈 4. ANÁLISE DE PERFORMANCE (Performance Analysis)
-- =============================================================================

-- 4.1 Taxa de aprovação por hora
SELECT 
    date_trunc('hour', timestamp) AS hour,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 2
    ) AS approval_rate_pct
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- 4.2 Top 10 merchants por volume
SELECT 
    COALESCE(merchant_id, 'UNKNOWN') AS merchant,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 2
    ) AS approval_rate_pct
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY merchant_id
ORDER BY total_transactions DESC
LIMIT 10;

-- 4.3 Distribuição de transações por auth_code
SELECT 
    COALESCE(auth_code, 'NULL') AS auth_code,
    COUNT(*) AS total,
    ROUND((COUNT(*)::numeric / SUM(COUNT(*)) OVER()) * 100, 2) AS percentage
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY auth_code
ORDER BY total DESC
LIMIT 20;

-- =============================================================================
-- 🔄 5. CONTINUOUS AGGREGATES (Agregações Automáticas)
-- =============================================================================

-- 5.1 Usar agregação por minuto (view materializada)
SELECT * FROM transactions_per_minute
WHERE bucket > NOW() - INTERVAL '1 hour'
ORDER BY bucket DESC;

-- 5.2 Usar agregação por hora
SELECT * FROM transactions_per_hour
WHERE bucket > NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;

-- 5.3 Refresh manual das agregações (se necessário)
-- CALL refresh_continuous_aggregate('transactions_per_minute', NOW() - INTERVAL '1 hour', NOW());
-- CALL refresh_continuous_aggregate('transactions_per_hour', NOW() - INTERVAL '24 hours', NOW());

-- =============================================================================
-- 🆘 6. QUERIES PARA INCIDENTES (Incident Investigation)
-- =============================================================================

-- 6.1 O que aconteceu em um período específico?
-- Substitua os timestamps conforme necessário
SELECT 
    date_trunc('minute', timestamp) AS minute,
    status,
    COUNT(*) AS count
FROM transactions
WHERE timestamp BETWEEN '2025-01-27 15:00:00' AND '2025-01-27 18:00:00'
GROUP BY minute, status
ORDER BY minute, status;

-- 6.2 Primeira e última transação de um período
SELECT 
    'Primeira' AS tipo,
    MIN(timestamp) AS timestamp
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
    'Última' AS tipo,
    MAX(timestamp) AS timestamp
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours';

-- 6.3 Listar transações com anomalia
SELECT *
FROM transactions
WHERE is_anomaly = TRUE
ORDER BY timestamp DESC
LIMIT 100;

-- 6.4 Buscar transações por status específico
SELECT 
    timestamp,
    status,
    amount,
    merchant_id,
    auth_code
FROM transactions
WHERE status = 'failed'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 50;

-- =============================================================================
-- 📊 7. RELATÓRIOS (Reports)
-- =============================================================================

-- 7.1 Relatório diário resumido
SELECT 
    date_trunc('day', timestamp) AS day,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    COUNT(*) FILTER (WHERE status = 'reversed') AS reversed,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 2
    ) AS approval_rate_pct
FROM transactions
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY day
ORDER BY day DESC;

-- 7.2 Relatório de SLA (uptime calculation)
WITH hourly_data AS (
    SELECT 
        date_trunc('hour', timestamp) AS hour,
        COUNT(*) AS count
    FROM transactions
    WHERE timestamp > NOW() - INTERVAL '30 days'
    GROUP BY 1
),
total_hours AS (
    SELECT COUNT(*) AS total FROM hourly_data
),
hours_with_data AS (
    SELECT COUNT(*) AS with_data FROM hourly_data WHERE count > 0
)
SELECT 
    h.with_data AS hours_operational,
    t.total AS total_hours,
    ROUND((h.with_data::numeric / NULLIF(t.total, 0) * 100), 3) AS uptime_pct
FROM hours_with_data h, total_hours t;

-- 7.3 Comparação semana atual vs semana passada
WITH this_week AS (
    SELECT COUNT(*) AS count
    FROM transactions
    WHERE timestamp > date_trunc('week', NOW())
),
last_week AS (
    SELECT COUNT(*) AS count
    FROM transactions
    WHERE timestamp BETWEEN 
        date_trunc('week', NOW() - INTERVAL '1 week')
        AND date_trunc('week', NOW())
)
SELECT 
    t.count AS this_week,
    l.count AS last_week,
    ROUND(((t.count - l.count)::numeric / NULLIF(l.count, 0) * 100), 2) AS change_pct
FROM this_week t, last_week l;

-- =============================================================================
-- 🛠️ 8. QUERIES DE MANUTENÇÃO (Maintenance)
-- =============================================================================

-- 8.1 Verificar tamanho das tabelas
SELECT 
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)) AS size
FROM timescaledb_information.hypertables;

-- 8.2 Verificar chunks (partições)
SELECT 
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(chunk_size) AS size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'transactions'
ORDER BY range_start DESC
LIMIT 10;

-- 8.3 Verificar continuous aggregates
SELECT 
    view_name,
    materialization_hypertable_name,
    view_definition
FROM timescaledb_information.continuous_aggregates;

-- 8.4 Verificar políticas de retenção
SELECT *
FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';

-- 8.5 Health check geral
SELECT 
    (SELECT COUNT(*) FROM transactions) AS total_transactions,
    (SELECT COUNT(*) FROM anomalies WHERE status = 'open') AS open_anomalies,
    (SELECT COUNT(*) FROM alerts WHERE status = 'firing') AS active_alerts,
    (SELECT MAX(timestamp) FROM transactions) AS last_transaction;

-- =============================================================================
-- 🎯 9. QUERIES PARA CLAWDBOT (Chat Commands)
-- =============================================================================

-- 9.1 Status rápido (comando: "status")
SELECT 
    'Transaction Guardian' AS system,
    CASE WHEN COUNT(*) > 0 THEN 'healthy' ELSE 'no_data' END AS status,
    COUNT(*) AS tx_last_hour,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 1
    ) AS approval_rate,
    COUNT(*) FILTER (WHERE is_anomaly = TRUE) AS anomalies
FROM transactions
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- 9.2 Alertas ativos (comando: "alerts")
SELECT 
    id,
    alert_name,
    severity,
    fired_at,
    EXTRACT(epoch FROM (NOW() - fired_at))/60 AS minutes_ago
FROM alerts
WHERE status = 'firing'
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        ELSE 4 
    END,
    fired_at DESC;

-- 9.3 Briefing de turno (comando: "briefing")
SELECT 
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
         NULLIF(COUNT(*), 0) * 100), 1
    ) AS approval_rate,
    COUNT(*) FILTER (WHERE is_anomaly = TRUE) AS anomalies_detected,
    (SELECT COUNT(*) FROM anomalies WHERE status = 'open') AS open_anomalies,
    (SELECT COUNT(*) FROM alerts WHERE status = 'firing') AS active_alerts
FROM transactions
WHERE timestamp > NOW() - INTERVAL '8 hours';

-- =============================================================================
-- 💡 DICAS DE USO
-- =============================================================================
-- 
-- 1. Para Night Shift: Use as queries da seção 3 (Anomaly Detection) regularmente
-- 
-- 2. Para investigar incidentes: Use a seção 6 alterando os timestamps
-- 
-- 3. Para relatórios: Use a seção 7
-- 
-- 4. Para Grafana: Todas as queries podem ser usadas como Data Source
-- 
-- 5. Para Clawdbot: As queries da seção 9 são formatadas para respostas de chat
--
-- =============================================================================
