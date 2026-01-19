# 📚 MASTER DOCUMENTATION - Task 3.2

**Transaction Guardian: Real-time Monitoring System**

---

## 1. Visão Geral do Sistema

### 1.1 Objetivo
Sistema de monitoramento de transações em tempo real com alertas automáticos, conforme especificado no Task 3.2 do desafio CloudWalk.

### 1.2 Componentes

| Componente | Tecnologia | Responsabilidade |
|------------|------------|------------------|
| API | FastAPI | Recebe transações, expõe endpoints |
| Detector | Python + Scikit-learn | ML + Rules para detecção |
| Alerter | Python + aiohttp | Notificações Slack |
| Metrics | Prometheus | Coleta e armazenamento |
| Dashboard | Grafana | Visualização real-time |
| Simulator | Python + asyncio | Geração de dados para testes |

---

## 2. Arquivos do Projeto

### 2.1 `code/main.py` (~400 linhas)
**API FastAPI com 9 endpoints:**

```python
POST /transaction      # Analisa transação
POST /transactions/batch  # Processa batch
GET  /anomalies       # Lista anomalias
GET  /metrics         # Métricas Prometheus
GET  /metrics/json    # Métricas JSON
GET  /health          # Health check
GET  /stats           # Estatísticas
GET  /stream          # SSE real-time
POST /reset           # Reset sistema
```

### 2.2 `code/anomaly_detector.py` (~280 linhas)
**3 métodos de detecção:**

1. **Isolation Forest (ML)**
   - 100 estimadores
   - Contamination: 10%
   - Score: 0-1 via sigmoid

2. **Rule-based (Thresholds)**
   - LOW_VOLUME: count < 50
   - VOLUME_SPIKE: count > 2x média
   - VOLUME_DROP: count < 50% média
   - FAILED/DENIED: status não-aprovado
   - AUTH_ERROR: auth_code != "00"

3. **Z-Score (Estatística)**
   - Threshold: |zscore| > 2.5

**Score Combinado:**
```
score = 0.6 * ml_score + 0.4 * zscore_normalized
```

### 2.3 `code/alert_manager.py` (~180 linhas)
**Sistema de notificações:**

- Console: sempre ativo
- Slack: via webhook (opcional)
- Rate limiting: 60s entre alertas similares
- Histórico: últimos 500 alertas

### 2.4 `code/simulator.py` (~250 linhas)
**3 modos de operação:**

```bash
# Stream sintético
python -m code.simulator --mode stream --api http://localhost:8001

# Replay CSV
python -m code.simulator --mode csv --csv data/transactions.csv

# Injetar incidente
python -m code.simulator --mode incident --incident outage
```

---

## 3. Detecção de Anomalias

### 3.1 Fluxo de Análise

```
Transação → ML Score → Regras → Z-Score → Score Combinado → Decisão
```

### 3.2 Níveis de Alerta

| Nível | Condição | Ação |
|-------|----------|------|
| NORMAL | score < 0.5, sem violações | Log apenas |
| WARNING | score > 0.5 ou 1 violação | Alerta + Log |
| CRITICAL | score > 0.85 ou 2+ violações | Alerta urgente |

### 3.3 Recomendações Geradas

```python
CRITICAL + outage:
  "🚨 CRÍTICO: Possível outage! Verificar gateway IMEDIATAMENTE."

CRITICAL + failures:
  "🚨 CRÍTICO: Alta taxa de falhas! Investigar processador."

WARNING + spike:
  "⚠️ ALERTA: Spike de volume. Monitorar sobrecarga."

NORMAL:
  "✅ NORMAL: Métricas dentro dos parâmetros."
```

---

## 4. Infraestrutura

### 4.1 Docker Compose

```yaml
services:
  guardian-api:        # FastAPI (8001)
  guardian-prometheus: # Métricas (9091)
  guardian-grafana:    # Dashboard (3002)
```

### 4.2 Métricas Prometheus

```promql
transaction_guardian_total           # Contador total
transaction_guardian_anomalies       # Anomalias detectadas
transaction_guardian_current_count   # Volume atual
transaction_guardian_avg_count       # Média móvel
transaction_guardian_approval_rate   # Taxa aprovação
transaction_guardian_by_status       # Por status
```

### 4.3 Dashboard Grafana

**7 Painéis:**
1. Total Transações (Stat)
2. Anomalias Detectadas (Stat)
3. Taxa de Aprovação (Gauge)
4. Transações/Minuto (Stat)
5. Volume Tempo Real (Time Series)
6. Distribuição por Status (Pie)
7. Taxa de Anomalias (Time Series)

---

## 5. Dados Analisados

### 5.1 transactions.csv
- **Registros:** 25.922
- **Período:** 12-15 de julho 2025
- **Campos:** timestamp, status, count

### 5.2 Anomalia Identificada
- **Período:** 17:10 - 17:28 (12/07)
- **Duração:** 18 minutos
- **Comportamento:** Volume caiu de ~115 para ~70 (-40%)
- **Causa provável:** Degradação do sistema

---

## 6. Postman Collection

### 6.1 Requests Incluídas (16 total)

**📊 Monitoring:**
- Health Check
- Estatísticas
- Métricas Prometheus
- Listar Anomalias

**💳 Transações Normais:**
- Count 100, 115, 130

**🚨 Anomalias Volume:**
- Outage (count=5)
- Degradação (count=40)
- Spike (count=400)

**🚨 Anomalias Status:**
- Failed + auth_code 59
- Denied + auth_code 51
- Auth Error (code 05)

**📦 Batch:**
- 10 transações mistas

**🔧 Admin:**
- Reset sistema

---

## 7. Como Executar

### 7.1 Com Docker
```bash
cd infrastructure
docker compose up -d --build
```

### 7.2 Desenvolvimento Local
```bash
pip install -r infrastructure/requirements.txt
cd code
uvicorn main:app --reload --port 8001
```

### 7.3 Testar com Curl
```bash
# Normal
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status":"approved","count":115,"auth_code":"00"}'

# Anomalia
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status":"approved","count":5,"auth_code":"00"}'
```

---

## 8. Requisitos Atendidos

| Requisito | Implementação |
|-----------|---------------|
| Endpoint transações | `POST /transaction` |
| Recomendação alerta | `is_anomaly`, `alert_level`, `recommendation` |
| Query dados | `/anomalies?level=CRITICAL&limit=10` |
| Gráfico real-time | Grafana 7 painéis, refresh 5s |
| Modelo anomalias | Isolation Forest (sklearn) |
| Notificação automática | Slack + Console |
| Rule-based | 5 regras de threshold |
| Score-based | ML score 0-1 |
| Combinação | 60% ML + 40% Stats |

---

## 9. Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| Arquivos Python | 4 |
| Linhas de código | ~1.300 |
| Endpoints API | 9 |
| Painéis Grafana | 7 |
| Métodos detecção | 3 |
| Containers Docker | 3 |
| Requests Postman | 16 |

---

**Autor:** Sérgio  
**Desafio:** CloudWalk Monitoring Intelligence Analyst  
**Data:** Janeiro 2025
