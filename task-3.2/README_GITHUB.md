# 🛡️ Transaction Guardian

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CloudWalk Monitoring Intelligence Challenge - Task 3.2**  
> Sistema de monitoramento de transações em tempo real com detecção automática de anomalias usando Machine Learning e regras.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Detecção de Anomalias](#-detecção-de-anomalias)
- [Dashboard Grafana](#-dashboard-grafana)
- [Postman Collection](#-postman-collection)

---

## 🎯 Visão Geral

**Transaction Guardian** é um sistema completo de monitoramento de transações financeiras que:

- ✅ Recebe transações via API REST
- ✅ Detecta anomalias usando **ML (Isolation Forest)** + **Regras** + **Z-Score**
- ✅ Alerta automaticamente via **Slack** e **Console**
- ✅ Visualiza métricas em tempo real no **Grafana**
- ✅ Expõe métricas para **Prometheus**

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │Simulator │───▶│ FastAPI  │───▶│ Detector │───▶│ Alerter  │ │
│   │ /Postman │    │  :8001   │    │ ML+Rules │    │  Slack   │ │
│   └──────────┘    └────┬─────┘    └──────────┘    └──────────┘ │
│                        │                                        │
│                        ▼                                        │
│                  ┌──────────┐         ┌──────────┐              │
│                  │Prometheus│────────▶│ Grafana  │              │
│                  │  :9091   │         │  :3002   │              │
│                  └──────────┘         └──────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11+ (opcional, para desenvolvimento)

### Subir a Stack

```bash
cd infrastructure
docker compose up -d --build
```

### Acessar

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **API Swagger** | http://localhost:8001/docs | - |
| **Grafana** | http://localhost:3002 | admin/admin |
| **Prometheus** | http://localhost:9091 | - |

### Testar

```bash
# Health check
curl http://localhost:8001/health

# Enviar transação normal
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 115, "auth_code": "00"}'

# Enviar transação anômala (outage)
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 5, "auth_code": "00"}'
```

---

## 📡 API Reference

### `POST /transaction`

Analisa uma transação e retorna recomendação de alerta.

**Request:**
```json
{
  "timestamp": "2025-07-12T14:30:00",
  "status": "approved",
  "count": 125,
  "auth_code": "00"
}
```

**Response:**
```json
{
  "is_anomaly": false,
  "alert_level": "NORMAL",
  "anomaly_score": 0.12,
  "rule_violations": [],
  "recommendation": "✅ NORMAL: Métricas dentro dos parâmetros esperados.",
  "metrics": {
    "current_count": 125,
    "running_mean": 115.5,
    "running_std": 18.2,
    "zscore": 0.52,
    "ml_score": 0.08,
    "approval_rate": 0.95
  }
}
```

### Outros Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/transactions/batch` | POST | Processa múltiplas transações |
| `/anomalies` | GET | Lista anomalias com filtros |
| `/metrics` | GET | Métricas Prometheus |
| `/health` | GET | Status do sistema |
| `/stats` | GET | Estatísticas detalhadas |
| `/stream` | GET | Server-Sent Events |

---

## 🔍 Detecção de Anomalias

### Método Híbrido (3 técnicas combinadas)

#### 1. Machine Learning (Isolation Forest)
```python
from sklearn.ensemble import IsolationForest
model = IsolationForest(contamination=0.1, n_estimators=100)
```

#### 2. Rule-based (Thresholds)
| Regra | Condição | Severidade |
|-------|----------|------------|
| LOW_VOLUME | count < 50 | CRITICAL |
| VOLUME_DROP | count < 50% média | CRITICAL |
| VOLUME_SPIKE | count > 200% média | WARNING |
| FAILED | status == "failed" | CRITICAL |
| AUTH_ERROR | auth_code != "00" | WARNING |

#### 3. Statistical (Z-Score)
```python
zscore = (count - running_mean) / running_std
if abs(zscore) > 2.5:
    flag_anomaly()
```

### Score Combinado
```python
combined_score = 0.6 * ml_score + 0.4 * min(abs(zscore) / 3, 1)
```

### Níveis de Alerta
| Nível | Cor | Condição |
|-------|-----|----------|
| 🟢 NORMAL | Verde | score < 0.5, sem violações |
| 🟡 WARNING | Amarelo | score > 0.5 ou 1+ violações |
| 🔴 CRITICAL | Vermelho | score > 0.85 ou 2+ violações graves |

---

## 📊 Dashboard Grafana

7 painéis em tempo real:

1. **Total Transações** - Contador
2. **Anomalias Detectadas** - Contador com thresholds
3. **Taxa de Aprovação** - Gauge (verde >90%)
4. **Transações/Minuto** - Valor atual
5. **Volume (Tempo Real)** - Gráfico com média móvel
6. **Distribuição por Status** - Pie chart
7. **Taxa de Anomalias** - Time series

---

## 📮 Postman Collection

Importe `postman/Transaction_Guardian_API.postman_collection.json`

**16 requests prontas:**
- 📊 Monitoring (Health, Stats, Metrics, Anomalias)
- 💳 Transações Normais (3 variações)
- 🚨 Anomalias de Volume (Outage, Degradação, Spike)
- 🚨 Anomalias de Status (Failed, Denied, Auth Error)
- 📦 Batch (10 transações de uma vez)
- 🔧 Admin (Reset, Info)

---

## 📁 Estrutura do Projeto

```
task-3.2/
├── code/                # 4 scripts Python (~1.300 linhas)
├── dashboards/          # Grafana dashboard JSON
├── data/                # CSVs do desafio
├── docs/                # Documentação
├── infrastructure/      # Docker + Prometheus + Grafana
├── postman/             # Collection (16 requests)
├── prompts/             # NotebookLM prompts
└── README.md
```

---

## 👤 Autor

**Sérgio**  
Candidato: Monitoring Intelligence Analyst (Night Shift)  
CloudWalk Challenge - January 2025

---

*"We want firefighters that use code to stop the fire."* 🔥
