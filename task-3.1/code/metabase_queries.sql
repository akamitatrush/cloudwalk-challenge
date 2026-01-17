-- QUERY 1: Detecção de Anomalias com Severidade
SELECT 
    time as Hora,
    today as Hoje,
    yesterday as Ontem,
    ROUND(avg_last_week, 2) as Media_Semana,
    ROUND(((today - avg_last_week) / avg_last_week) * 100, 1) as Desvio_Percentual,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN '🔴 CRITICAL'
        WHEN today < avg_last_week * 0.5 THEN '🟠 HIGH'
        WHEN today > avg_last_week * 2 THEN '🟡 SPIKE'
        ELSE '🟢 NORMAL'
    END as Status
FROM checkout_2
ORDER BY 
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 1
        WHEN today < avg_last_week * 0.5 THEN 2
        ELSE 3
    END,
    time;

-- QUERY 2: Hoje vs Média Esperada (para gráfico de barras)
SELECT 
    time as Hora,
    today as Hoje,
    ROUND(avg_last_week, 2) as Media_Esperada
FROM checkout_2
ORDER BY CAST(REPLACE(time, 'h', '') AS INTEGER);

-- QUERY 3: Classificação por Tipo de Horário
SELECT 
    time as Hora,
    today as Hoje,
    ROUND(avg_last_week, 2) as Media_Esperada,
    CASE 
        WHEN avg_last_week < 1 THEN '😴 Horário morto'
        WHEN avg_last_week >= 1 AND avg_last_week < 10 THEN '🔵 Movimento baixo'
        WHEN avg_last_week >= 10 THEN '🔥 Horário de pico'
    END as Tipo_Horario,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN '🔴 ANOMALIA!'
        ELSE '✅ OK'
    END as Status
FROM checkout_2
ORDER BY CAST(REPLACE(time, 'h', '') AS INTEGER);

-- QUERY 4: Resumo de Impacto
SELECT 
    'Resumo do Incidente' as Analise,
    SUM(CASE WHEN today = 0 AND avg_last_week > 5 THEN avg_last_week ELSE 0 END) as Transacoes_Perdidas,
    SUM(today) as Total_Hoje,
    SUM(yesterday) as Total_Ontem,
    ROUND((SUM(today) - SUM(yesterday)) * 100.0 / SUM(yesterday), 1) as Variacao_Percentual
FROM checkout_2;
EOF
