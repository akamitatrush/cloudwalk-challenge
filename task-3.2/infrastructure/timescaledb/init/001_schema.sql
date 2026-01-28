-- =============================================================================
-- Transaction Guardian v2.0 - TimescaleDB Schema
-- =============================================================================
-- Este script cria o schema otimizado para time-series
-- Executado automaticamente pelo docker-entrypoint
-- =============================================================================

-- Habilitar extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- =============================================================================
-- 1. Tabela Principal: Transações
-- =============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Dados da transação
    status VARCHAR(20) NOT NULL,  -- approved, denied, failed, reversed
    amount DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'BRL',
    auth_code VARCHAR(10),
    
    -- Merchant info
    merchant_id VARCHAR(50),
    merchant_category VARCHAR(50),
    
    -- Detecção de anomalias
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score DECIMAL(5, 4),
    ml_score DECIMAL(5, 4),
    zscore DECIMAL(10, 4),
    detection_method VARCHAR(20),  -- ml, zscore, rules, combined
    
    -- Metadados
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (id, timestamp)
);

-- Converter para hypertable (time-series otimizado)
SELECT create_hypertable('transactions', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- =============================================================================
-- 2. Tabela de Anomalias Detectadas
-- =============================================================================
CREATE TABLE IF NOT EXISTS anomalies (
    id BIGSERIAL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Detalhes da anomalia
    anomaly_type VARCHAR(50) NOT NULL,  -- zero_transactions, spike, drop, pattern
    severity VARCHAR(20) NOT NULL,       -- low, medium, high, critical
    
    -- Scores
    combined_score DECIMAL(5, 4),
    ml_score DECIMAL(5, 4),
    zscore DECIMAL(10, 4),
    
    -- Contexto
    transaction_count INTEGER,
    expected_count INTEGER,
    time_window_minutes INTEGER DEFAULT 60,
    
    -- Resolução
    status VARCHAR(20) DEFAULT 'open',  -- open, acknowledged, resolved, false_positive
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(100),
    notes TEXT,
    
    PRIMARY KEY (id, detected_at)
);

SELECT create_hypertable('anomalies', 'detected_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- =============================================================================
-- 3. Tabela de Métricas Agregadas (para dashboards rápidos)
-- =============================================================================
CREATE TABLE IF NOT EXISTS metrics_hourly (
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Contadores
    total_transactions INTEGER DEFAULT 0,
    approved_count INTEGER DEFAULT 0,
    denied_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    reversed_count INTEGER DEFAULT 0,
    
    -- Taxas
    approval_rate DECIMAL(5, 2),
    anomaly_rate DECIMAL(5, 2),
    
    -- Valores
    total_amount DECIMAL(20, 2),
    avg_amount DECIMAL(15, 2),
    
    -- Performance
    avg_latency_ms DECIMAL(10, 2),
    p99_latency_ms DECIMAL(10, 2),
    
    PRIMARY KEY (timestamp)
);

SELECT create_hypertable('metrics_hourly', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- =============================================================================
-- 4. Tabela de Alertas
-- =============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL,
    fired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Detalhes do alerta
    alert_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'firing',  -- firing, resolved
    
    -- Contexto
    description TEXT,
    labels JSONB,
    annotations JSONB,
    
    -- Resolução
    resolved_at TIMESTAMPTZ,
    
    PRIMARY KEY (id, fired_at)
);

SELECT create_hypertable('alerts', 'fired_at',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- =============================================================================
-- 5. Índices para Performance
-- =============================================================================

-- Transações
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_anomaly ON transactions (is_anomaly, timestamp DESC) WHERE is_anomaly = TRUE;
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions (merchant_id, timestamp DESC);

-- Anomalias
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies (severity, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies (status, detected_at DESC);

-- Alertas
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status, fired_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts (severity, fired_at DESC);

-- =============================================================================
-- 6. Continuous Aggregates (Materialized Views automáticas)
-- =============================================================================

-- Agregação por minuto (para dashboards real-time)
CREATE MATERIALIZED VIEW IF NOT EXISTS transactions_per_minute
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 minute', timestamp) AS bucket,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    COUNT(*) FILTER (WHERE is_anomaly = TRUE) AS anomalies,
    AVG(amount) AS avg_amount,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY bucket
WITH NO DATA;

-- Policy para refresh automático
SELECT add_continuous_aggregate_policy('transactions_per_minute',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE
);

-- Agregação por hora (para análise histórica)
CREATE MATERIALIZED VIEW IF NOT EXISTS transactions_per_hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'denied') AS denied,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    COUNT(*) FILTER (WHERE is_anomaly = TRUE) AS anomalies,
    ROUND(AVG(amount)::numeric, 2) AS avg_amount,
    SUM(amount) AS total_amount,
    ROUND((COUNT(*) FILTER (WHERE status = 'approved')::numeric / 
           NULLIF(COUNT(*), 0) * 100)::numeric, 2) AS approval_rate
FROM transactions
GROUP BY bucket
WITH NO DATA;

SELECT add_continuous_aggregate_policy('transactions_per_hour',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- =============================================================================
-- 7. Retention Policy (manter 90 dias de dados)
-- =============================================================================

SELECT add_retention_policy('transactions', INTERVAL '90 days', if_not_exists => TRUE);
SELECT add_retention_policy('anomalies', INTERVAL '180 days', if_not_exists => TRUE);
SELECT add_retention_policy('alerts', INTERVAL '365 days', if_not_exists => TRUE);

-- =============================================================================
-- 8. Funções Úteis
-- =============================================================================

-- Função para calcular taxa de aprovação
CREATE OR REPLACE FUNCTION get_approval_rate(
    start_time TIMESTAMPTZ DEFAULT NOW() - INTERVAL '1 hour',
    end_time TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    total_transactions BIGINT,
    approved BIGINT,
    denied BIGINT,
    failed BIGINT,
    approval_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT AS total_transactions,
        COUNT(*) FILTER (WHERE status = 'approved')::BIGINT AS approved,
        COUNT(*) FILTER (WHERE status = 'denied')::BIGINT AS denied,
        COUNT(*) FILTER (WHERE status = 'failed')::BIGINT AS failed,
        ROUND((COUNT(*) FILTER (WHERE status = 'approved')::DECIMAL / 
               NULLIF(COUNT(*), 0) * 100), 2) AS approval_rate
    FROM transactions
    WHERE timestamp BETWEEN start_time AND end_time;
END;
$$ LANGUAGE plpgsql;

-- Função para detectar anomalias por volume
CREATE OR REPLACE FUNCTION check_volume_anomaly(
    window_minutes INTEGER DEFAULT 60,
    threshold_stddev DECIMAL DEFAULT 2.5
)
RETURNS TABLE (
    is_anomaly BOOLEAN,
    current_count BIGINT,
    avg_count DECIMAL,
    stddev_count DECIMAL,
    zscore DECIMAL
) AS $$
DECLARE
    v_current BIGINT;
    v_avg DECIMAL;
    v_stddev DECIMAL;
    v_zscore DECIMAL;
BEGIN
    -- Contar transações na janela atual
    SELECT COUNT(*) INTO v_current
    FROM transactions
    WHERE timestamp > NOW() - (window_minutes || ' minutes')::INTERVAL;
    
    -- Calcular média e desvio padrão histórico (últimos 7 dias, mesma hora)
    SELECT 
        AVG(cnt)::DECIMAL,
        STDDEV(cnt)::DECIMAL
    INTO v_avg, v_stddev
    FROM (
        SELECT COUNT(*) AS cnt
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '7 days'
        GROUP BY time_bucket((window_minutes || ' minutes')::INTERVAL, timestamp)
    ) subq;
    
    -- Calcular Z-Score
    IF v_stddev > 0 THEN
        v_zscore := (v_current - v_avg) / v_stddev;
    ELSE
        v_zscore := 0;
    END IF;
    
    RETURN QUERY
    SELECT 
        ABS(v_zscore) > threshold_stddev AS is_anomaly,
        v_current AS current_count,
        v_avg AS avg_count,
        v_stddev AS stddev_count,
        v_zscore AS zscore;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. Grants (permissões)
-- =============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO guardian;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO guardian;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO guardian;

-- =============================================================================
-- Pronto! Schema inicializado.
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Transaction Guardian TimescaleDB schema initialized!';
    RAISE NOTICE '📊 Tables: transactions, anomalies, metrics_hourly, alerts';
    RAISE NOTICE '📈 Continuous Aggregates: transactions_per_minute, transactions_per_hour';
    RAISE NOTICE '🕐 Retention: 90 days (transactions), 180 days (anomalies), 365 days (alerts)';
END $$;
