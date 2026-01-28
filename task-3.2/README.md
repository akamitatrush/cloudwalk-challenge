# 🛡️ Transaction Guardian v2.0

> **CloudWalk Monitoring Intelligence Challenge - Task 3.2**

Sistema de monitoramento de transações em tempo real com detecção automática de anomalias, cache de alta performance e arquitetura enterprise-ready.

---

## 🌐 Live Demo (Online 24/7)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **🔗 API Docs** | http://34.39.251.57:8001/docs | - |
| **📊 Grafana** | http://34.39.251.57:3002 | `admin` / `admin` |
| **📈 Prometheus** | http://34.39.251.57:9091 | - |
| **🚨 Alertmanager** | http://34.39.251.57:9093 | - |
| **🔴 Redis Commander** | http://34.39.251.57:8081 | - |
| **🐘 pgAdmin** | http://34.39.251.57:5050 | `admin@example.com` / `admin` |
| **📉 Metabase** | http://34.39.251.57:3003 | - |

---

## 🏗️ Evolution Roadmap

### ✅ Phase 1: Foundation (Complete)

Migração de CSV para banco de dados enterprise com TimescaleDB.

| Feature | Status | Descrição |
|---------|--------|-----------|
| TimescaleDB | ✅ | Banco otimizado para time-series |
| Data Migration | ✅ | 42,920 transações migradas |
| Hypertables | ✅ | Particionamento automático |
| Continuous Aggregates | ✅ | Views materializadas por minuto/hora |
| Retention Policies | ✅ | 90 dias automático |
| pgAdmin | ✅ | Interface de gerenciamento |
| 50+ SQL Queries | ✅ | Queries úteis para monitoramento |

**Documentação:** [docs/PHASE1_COMPLETE.md](docs/PHASE1_COMPLETE.md)

---

### ✅ Phase 2: Performance (Complete) ← ATUAL

Cache Redis para alta performance e proteção contra abuso.

| Feature | Status | Descrição |
|---------|--------|-----------|
| Redis Cache | ✅ | Respostas em **<10ms** |
| Rate Limiting | ✅ | 100 req/min por IP |
| Redis Commander | ✅ | UI para visualizar cache |
| Cache Stats | ✅ | Endpoint `/cache/stats` |
| TTL Configurável | ✅ | 60s para transações |
| Prometheus Metrics | ✅ | `cache_hits`, `cache_misses` |

**Documentação:** [docs/PHASE2_COMPLETE.md](docs/PHASE2_COMPLETE.md)

---

### 🔜 Phase 3: Security (Next)

| Feature | Status |
|---------|--------|
| OAuth2 / JWT | 📋 |
| HashiCorp Vault | 📋 |
| API Key Management | 📋 |

---

### 📋 Phase 4-6: Future

| Phase | Focus | Features |
|-------|-------|----------|
| Phase 4 | MLOps | MLflow, Model Versioning, A/B Testing |
| Phase 5 | Clawdbot | Telegram Bot, WhatsApp Alerts |
| Phase 6 | Observability | OpenTelemetry, Jaeger, SLOs |

---

## 🎯 Requisitos Atendidos (Task 3.2)

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Endpoint que recebe transações | ✅ | `POST /transaction` |
| Retorna recomendação de alerta | ✅ | `is_anomaly`, `alert_level`, `recommendation` |
| Query para organizar dados | ✅ | `GET /anomalies?level=CRITICAL&limit=10` |
| Gráfico em tempo real | ✅ | Grafana Dashboard (5 dashboards, 31 painéis) |
| Modelo de anomalias | ✅ | Isolation Forest (ML) + Rules + Z-Score |
| Sistema de notificação automática | ✅ | Alertmanager + Slack |
| Rule-based + Score-based | ✅ | Combinação dos dois métodos |

---

## 🚀 Quick Start

### Opção 1: Todos os serviços
```bash
cd task-3.2/infrastructure

# Core services (API, Grafana, Prometheus, Alertmanager)
docker compose up -d --build

# Phase 1: TimescaleDB
docker compose -f docker-compose.timescale.yml up -d

# Phase 2: Redis Cache
docker compose -f docker-compose.redis.yml up -d
```

### Opção 2: Script automatizado
```bash
cd task-3.2
chmod +x setup_all.sh
./setup_all.sh
```

**Acessar:**
- 📚 API Swagger: http://localhost:8001/docs
- 📊 Grafana: http://localhost:3002 (admin/admin)
- 🔴 Redis Commander: http://localhost:8081

---

## 📁 Estrutura do Projeto
```
task-3.2/
├── code/                    # Python Source Code
│   ├── main.py                  # FastAPI v2.0 (com cache)
│   ├── main_v1.py               # Backup v1.0 (original)
│   ├── cache.py                 # 🆕 Redis Cache Module
│   ├── anomaly_detector.py      # ML + Rules + Z-Score
│   ├── alert_manager.py         # Notificações
│   ├── database.py              # TimescaleDB connection
│   └── simulator.py             # Gerador de transações
│
├── dashboards/              # 5 Grafana Dashboards (31 painéis)
│   ├── transaction_guardian.json
│   ├── sla_slo_dashboard.json
│   ├── alerts_incidents_dashboard.json
│   ├── historical_analysis_dashboard.json
│   └── executive_summary_dashboard.json
│
├── docs/                    # Documentação
│   ├── PHASE1_COMPLETE.md       # Phase 1 docs
│   ├── PHASE2_COMPLETE.md       # Phase 2 docs
│   └── CLOUD_DEPLOY.md          # Deploy guide
│
├── infrastructure/          # Docker & Config
│   ├── docker-compose.yml           # Core services
│   ├── docker-compose.redis.yml     # 🆕 Redis
│   ├── docker-compose.timescale.yml # TimescaleDB
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/                    # CSVs do desafio
├── postman/                 # Collection (16 requests)
└── README.md
```

---

## 🔍 Métodos de Detecção

| Método | Peso | Descrição |
|--------|------|-----------|
| **Isolation Forest** | 60% | Machine Learning |
| **Z-Score** | 40% | Análise estatística |
| **Rule-based** | Flags | Thresholds configuráveis |

### Thresholds Configurados

| Regra | Threshold | Alerta |
|-------|-----------|--------|
| LOW_VOLUME | < 50 tx | CRITICAL (possível outage) |
| HIGH_VOLUME | > 200 tx | WARNING (pico de tráfego) |
| FAILED | status = failed | WARNING |
| DENIED | status = denied | WARNING |
| REVERSED | status = reversed | WARNING |
| Z-SCORE | > 2.5 std | Anomalia estatística |

---

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/transaction` | Analisa transação |
| `POST` | `/transactions/batch` | Processa batch |
| `GET` | `/anomalies` | Lista anomalias |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/stats` | Estatísticas |

### Cache Endpoints (Phase 2)

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/cache/stats` | Estatísticas do cache |
| `DELETE` | `/cache/flush` | Limpa o cache |
| `GET` | `/cache/keys` | Conta chaves |

### Exemplo de Uso
```bash
# Analisar transação
curl -X POST http://34.39.251.57:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 100}'

# Response
{
  "is_anomaly": false,
  "alert_level": "NORMAL",
  "recommendation": "✅ NORMAL: Métricas dentro dos parâmetros.",
  "cached": false
}
```

---

## 📊 Grafana Dashboards (5 Total)

### 1. 🛡️ Transaction Guardian (Real-time)
- Total Transações / Anomalias
- Taxa de Aprovação (Gauge)
- Volume em Tempo Real
- Distribuição por Status

### 2. 📈 SLA/SLO Dashboard
- Uptime (SLA) - Meta 99.9%
- Latência P95/P99
- Taxa de Erro

### 3. 🚨 Alertas & Incidentes
- CRITICAL / WARNING count
- MTTR / MTTA / MTBF
- Timeline de Alertas

### 4. 📊 Análise Histórica
- Comparação Dia a Dia
- Heatmap por Hora
- Tendência Semanal

### 5. 👔 Executive Summary
- Status Geral (Semáforo)
- KPIs Principais
- Meta do Período

---

## 🐳 Services & Ports

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| API (FastAPI) | 8001 | REST API v2.0 |
| Grafana | 3002 | Dashboards |
| Prometheus | 9091 | Métricas |
| Alertmanager | 9093 | Alertas |
| Redis | 6379 | Cache (interno) |
| Redis Commander | 8081 | Redis UI |
| TimescaleDB | 5432 | Database (interno) |
| pgAdmin | 5050 | Database UI |
| Metabase | 3003 | BI Tool |

---

## 📮 Postman Collection
```
postman/Transaction_Guardian_API.postman_collection.json
```

**16 Requests incluídas** - Todas as funcionalidades documentadas.

---

## 🔧 Tecnologias

| Categoria | Tecnologias |
|-----------|-------------|
| **API** | FastAPI, Uvicorn, Pydantic |
| **ML** | scikit-learn (Isolation Forest) |
| **Database** | TimescaleDB (PostgreSQL) |
| **Cache** | Redis |
| **Monitoring** | Prometheus, Grafana, Alertmanager |
| **Container** | Docker, Docker Compose |
| **Cloud** | Google Cloud Platform |

---

## 👤 Autor

**Sérgio Henrique**

| | |
|---|---|
| 📧 Email | sergio@lognullsec.com |
| 💼 LinkedIn | [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva) |
| 🐙 GitHub | [github.com/akamitatrush](https://github.com/akamitatrush) |

**Candidatura:** Monitoring Intelligence Analyst (Night Shift) - CloudWalk

---

## 📜 License

MIT License - Feel free to use and modify.

---

*"Bombeiros que usam código para apagar incêndios." 🔥*

**Branch:** `phase2-performance` | **Version:** 2.0.0
