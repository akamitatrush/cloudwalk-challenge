# 📊 PROMQL CHEATSHEET - TRANSACTION GUARDIAN

## Guia Rápido de Queries Prometheus

---

## 📑 ÍNDICE

1. [Métricas Disponíveis](#1-métricas-disponíveis)
2. [Queries Básicas](#2-queries-básicas)
3. [Queries de Taxa](#3-queries-de-taxa)
4. [Queries de Agregação](#4-queries-de-agregação)
5. [Queries de Alerta](#5-queries-de-alerta)
6. [Queries Avançadas](#6-queries-avançadas)
7. [Funções Úteis](#7-funções-úteis)

---

## 1. MÉTRICAS DISPONÍVEIS

### Transaction Guardian Metrics

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `transaction_guardian_total` | Counter | Total de transações processadas |
| `transaction_guardian_anomalies` | Counter | Total de anomalias detectadas |
| `transaction_guardian_current_count` | Gauge | Volume atual de transações |
| `transaction_guardian_avg_count` | Gauge | Média de volume |
| `transaction_guardian_approval_rate` | Gauge | Taxa de aprovação (0-1) |
| `transaction_guardian_by_status` | Gauge | Contagem por status |

### Labels Disponíveis

```
{job="guardian-api", instance="guardian-api:8000"}
```

---

## 2. QUERIES BÁSICAS

### Volume Atual

```promql
# Volume atual de transações
transaction_guardian_current_count

# Com label específico
transaction_guardian_current_count{job="guardian-api"}
```

### Total de Transações

```promql
# Total absoluto
transaction_guardian_total

# Incremento nos últimos 5 minutos
increase(transaction_guardian_total[5m])
```

### Taxa de Aprovação

```promql
# Taxa de aprovação (0-1)
transaction_guardian_approval_rate

# Em porcentagem
transaction_guardian_approval_rate * 100
```

### Anomalias

```promql
# Total de anomalias
transaction_guardian_anomalies

# Novas anomalias nos últimos 5 minutos
increase(transaction_guardian_anomalies[5m])
```

---

## 3. QUERIES DE TAXA

### Taxa de Transações por Segundo

```promql
# Taxa por segundo nos últimos 5 minutos
rate(transaction_guardian_total[5m])

# Taxa por segundo nos últimos 1 minuto (mais sensível)
rate(transaction_guardian_total[1m])
```

### Taxa de Anomalias

```promql
# Taxa de anomalias por segundo
rate(transaction_guardian_anomalies[5m])

# Percentual de anomalias
rate(transaction_guardian_anomalies[5m]) / rate(transaction_guardian_total[5m]) * 100
```

### irate vs rate

```promql
# rate: média no período (mais estável)
rate(transaction_guardian_total[5m])

# irate: taxa instantânea (mais reativo)
irate(transaction_guardian_total[5m])
```

---

## 4. QUERIES DE AGREGAÇÃO

### Média

```promql
# Média do volume nos últimos 5 minutos
avg_over_time(transaction_guardian_current_count[5m])

# Média por hora
avg_over_time(transaction_guardian_current_count[1h])
```

### Máximo e Mínimo

```promql
# Máximo nos últimos 5 minutos
max_over_time(transaction_guardian_current_count[5m])

# Mínimo nos últimos 5 minutos
min_over_time(transaction_guardian_current_count[5m])
```

### Desvio Padrão

```promql
# Desvio padrão do volume
stddev_over_time(transaction_guardian_current_count[5m])
```

### Quantis

```promql
# Percentil 95 do volume
quantile_over_time(0.95, transaction_guardian_current_count[5m])

# Percentil 99
quantile_over_time(0.99, transaction_guardian_current_count[5m])
```

---

## 5. QUERIES DE ALERTA

### Zero Transactions

```promql
# Alerta: volume zero
transaction_guardian_current_count == 0

# Volume zero por mais de 1 minuto
transaction_guardian_current_count == 0
```

### Low Volume

```promql
# Volume abaixo de 50
transaction_guardian_current_count < 50

# Volume 50% abaixo da média
transaction_guardian_current_count < (transaction_guardian_avg_count * 0.5)
```

### High Anomaly Rate

```promql
# Taxa de anomalias > 10%
(transaction_guardian_anomalies / transaction_guardian_total) > 0.1

# Usando rate para período específico
(rate(transaction_guardian_anomalies[5m]) / rate(transaction_guardian_total[5m])) > 0.1
```

### Low Approval Rate

```promql
# Taxa de aprovação < 90%
transaction_guardian_approval_rate < 0.9
```

### Volume Spike

```promql
# Volume acima de 200% da média
transaction_guardian_current_count > (transaction_guardian_avg_count * 2)
```

---

## 6. QUERIES AVANÇADAS

### Comparação com Histórico

```promql
# Volume atual vs mesma hora ontem
transaction_guardian_current_count 
  - transaction_guardian_current_count offset 1d

# Percentual de mudança vs ontem
(transaction_guardian_current_count 
  - transaction_guardian_current_count offset 1d) 
  / transaction_guardian_current_count offset 1d * 100
```

### Detecção de Tendência

```promql
# Derivada (tendência de mudança)
deriv(transaction_guardian_current_count[5m])

# Se negativo = volume caindo
# Se positivo = volume subindo
```

### Delta (Mudança Absoluta)

```promql
# Mudança no volume nos últimos 5 minutos
delta(transaction_guardian_current_count[5m])
```

### Predict Linear

```promql
# Prever valor em 1 hora baseado em tendência
predict_linear(transaction_guardian_current_count[1h], 3600)
```

### Z-Score Manual

```promql
# Z-Score do volume atual
(transaction_guardian_current_count 
  - avg_over_time(transaction_guardian_current_count[1h]))
/ stddev_over_time(transaction_guardian_current_count[1h])
```

---

## 7. FUNÇÕES ÚTEIS

### Funções de Agregação

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `sum()` | Soma | `sum(transaction_guardian_total)` |
| `avg()` | Média | `avg(transaction_guardian_current_count)` |
| `min()` | Mínimo | `min(transaction_guardian_current_count)` |
| `max()` | Máximo | `max(transaction_guardian_current_count)` |
| `count()` | Contagem | `count(transaction_guardian_total)` |

### Funções Over Time

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `avg_over_time()` | Média no período | `avg_over_time(metric[5m])` |
| `max_over_time()` | Máximo no período | `max_over_time(metric[5m])` |
| `min_over_time()` | Mínimo no período | `min_over_time(metric[5m])` |
| `sum_over_time()` | Soma no período | `sum_over_time(metric[5m])` |
| `count_over_time()` | Amostras no período | `count_over_time(metric[5m])` |
| `quantile_over_time()` | Percentil | `quantile_over_time(0.95, metric[5m])` |
| `stddev_over_time()` | Desvio padrão | `stddev_over_time(metric[5m])` |

### Funções de Taxa

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `rate()` | Taxa por segundo (média) | `rate(counter[5m])` |
| `irate()` | Taxa instantânea | `irate(counter[5m])` |
| `increase()` | Incremento total | `increase(counter[5m])` |
| `delta()` | Diferença | `delta(gauge[5m])` |
| `deriv()` | Derivada | `deriv(gauge[5m])` |

### Funções Matemáticas

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `abs()` | Valor absoluto | `abs(metric)` |
| `ceil()` | Arredonda pra cima | `ceil(metric)` |
| `floor()` | Arredonda pra baixo | `floor(metric)` |
| `round()` | Arredonda | `round(metric, 0.1)` |
| `clamp_max()` | Limita máximo | `clamp_max(metric, 100)` |
| `clamp_min()` | Limita mínimo | `clamp_min(metric, 0)` |

---

## 📋 QUERIES PRONTAS PARA GRAFANA

### Dashboard: Volume Overview

```promql
# Painel: Volume Atual
transaction_guardian_current_count

# Painel: Tendência de Volume
rate(transaction_guardian_total[5m]) * 60

# Painel: Volume vs Média
transaction_guardian_current_count
transaction_guardian_avg_count
```

### Dashboard: Anomalias

```promql
# Painel: Total de Anomalias
transaction_guardian_anomalies

# Painel: Taxa de Anomalias (%)
(transaction_guardian_anomalies / transaction_guardian_total) * 100

# Painel: Novas Anomalias (últimos 5 min)
increase(transaction_guardian_anomalies[5m])
```

### Dashboard: Saúde do Sistema

```promql
# Painel: Taxa de Aprovação (%)
transaction_guardian_approval_rate * 100

# Painel: Status do Sistema (1=OK, 0=Problem)
transaction_guardian_approval_rate > 0.9 and transaction_guardian_current_count > 50
```

---

## 🔧 TESTANDO QUERIES

### Via curl

```bash
# Query simples
curl 'http://localhost:9091/api/v1/query?query=transaction_guardian_total'

# Query com range
curl 'http://localhost:9091/api/v1/query_range?query=transaction_guardian_current_count&start=2025-01-19T10:00:00Z&end=2025-01-19T12:00:00Z&step=60s'

# Query formatada
curl -s 'http://localhost:9091/api/v1/query?query=transaction_guardian_approval_rate' | jq
```

### Via Prometheus UI

1. Acesse: http://localhost:9091/graph
2. Digite a query
3. Clique em "Execute"
4. Alterne entre "Table" e "Graph"

---

*PromQL Cheatsheet Version: 1.0*  
*Last Updated: 2025-01-19*
