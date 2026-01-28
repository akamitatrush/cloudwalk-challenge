# 🛡️ Transaction Guardian - Task 3.2

> **CloudWalk Monitoring Intelligence Challenge**

Sistema de monitoramento de transações em tempo real com detecção automática de anomalias.

## 🆕 Phase 2: Performance (NEW!)

| Feature | Status | Descrição |
|---------|--------|-----------|
| **Redis Cache** | ✅ | Respostas em <10ms |
| **Rate Limiting** | ✅ | 100 req/min por IP |
| **Redis Commander** | ✅ | UI para visualizar cache |
| **Cache Stats** | ✅ | Métricas de hit/miss |

---

## 🎯 Requisitos Atendidos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Endpoint que recebe transações | ✅ | `POST /transaction` |
| Retorna recomendação de alerta | ✅ | `is_anomaly`, `alert_level`, `recommendation` |
| Query para organizar dados | ✅ | `GET /anomalies?level=CRITICAL&limit=10` |
| Gráfico em tempo real | ✅ | Grafana Dashboard (5 dashboards, 31 painéis) |
| Modelo de anomalias | ✅ | Isolation Forest (ML) + Rules + Z-Score |
| Sistema de notificação automática | ✅ | Slack + Console |
| Rule-based + Score-based | ✅ | Combinação dos dois métodos |

---

## 🌐 Live Demo (Online 24/7)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **API Docs** | http://34.39.251.57:8001/docs | - |
| **Grafana** | http://34.39.251.57:3002 | `admin` / `admin` |
| **Prometheus** | http://34.39.251.57:9091 | - |
| **Alertmanager** | http://34.39.251.57:9093 | - |
| **Redis Commander** | http://34.39.251.57:8081 | - |
| **pgAdmin** | http://34.39.251.57:5050 | `admin@example.com` / `admin` |
| **Metabase** | http://34.39.251.57:3003 | - |

---

## 🚀 Quick Start
```bash
cd task-3.2/infrastructure

# Subir todos os serviços
docker compose up -d --build

# Subir Redis (Phase 2)
docker compose -f docker-compose.redis.yml up -d

# Subir TimescaleDB (Phase 1)
docker compose -f docker-compose.timescale.yml up -d
```

**Acessar:**
- API Swagger: http://localhost:8001/docs
- Grafana: http://localhost:3002 (admin/admin)
- Prometheus: http://localhost:9091
- Redis Commander: http://localhost:8081

---

## 📁 Estrutura
```
task-3.2/
├── assets/              # Screenshots
├── code/                # Scripts Python
│   ├── main.py              # FastAPI v2.0 (com cache)
│   ├── main_v1.py           # Backup da v1.0
│   ├── cache.py             # 🆕 Redis Cache Module
│   ├── anomaly_detector.py  # ML + Rules detector
│   ├── alert_manager.py     # Sistema de notificações
│   └── simulator.py         # Gerador de transações
├── dashboards/          # 5 Dashboards Grafana (31 painéis)
├── data/                # CSVs do desafio
├── docs/                # Documentação detalhada
│   ├── PHASE1_COMPLETE.md   # Documentação Phase 1
│   └── PHASE2_COMPLETE.md   # 🆕 Documentação Phase 2
├── infrastructure/      # Docker, Prometheus, Grafana
│   ├── docker-compose.yml
│   ├── docker-compose.redis.yml      # 🆕 Redis
│   └── docker-compose.timescale.yml  # TimescaleDB
├── interactive/         # Notebook Colab
├── postman/             # Collection Postman (16 requests)
└── README.md
```

---

## 🚀 Phase 2: Performance Features

### Redis Cache
```bash
# Ver estatísticas do cache
curl http://34.39.251.57:8001/cache/stats
```

Response:
```json
{
  "connected": true,
  "hits": 150,
  "misses": 50,
  "hit_rate": 75.0,
  "redis_info": {
    "used_memory": "1.24M"
  }
}
```

### Rate Limiting

Cada resposta inclui headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 45
```

### Cached Responses
```bash
# Primeira chamada - processada
curl -X POST http://34.39.251.57:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-01-28T10:00:00", "status": "approved", "count": 100}'
# Response: "cached": false

# Segunda chamada - do cache (<10ms)
# Response: "cached": true
```

---

## 📊 DASHBOARDS GRAFANA (5 Total)

### 1. 🛡️ Transaction Guardian (Real-time)
- Total Transações
- Anomalias Detectadas
- Taxa de Aprovação (Gauge)
- Transações/Minuto
- Distribuição por Status

### 2. 📈 SLA/SLO Dashboard
- Uptime (SLA) - Meta 99.9%
- Latência Média
- P95/P99 Latência
- Taxa de Erro

### 3. 🚨 Alertas & Incidentes
- Total Alertas (Hoje)
- CRITICAL / WARNING
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

## 🔍 Métodos de Detecção

| Método | Peso | Descrição |
|--------|------|-----------|
| Machine Learning | 60% | Isolation Forest |
| Statistical | 40% | Z-Score |
| Rule-based | - | Thresholds configuráveis |

**Score Combinado:** `60% ML + 40% Z-Score`

---

## 📊 Portas

| Serviço | Porta | URL |
|---------|-------|-----|
| API | 8001 | http://localhost:8001/docs |
| Grafana | 3002 | http://localhost:3002 |
| Prometheus | 9091 | http://localhost:9091 |
| Alertmanager | 9093 | http://localhost:9093 |
| Redis | 6379 | Internal |
| Redis Commander | 8081 | http://localhost:8081 |
| TimescaleDB | 5432 | Internal |
| pgAdmin | 5050 | http://localhost:5050 |
| Metabase | 3003 | http://localhost:3003 |

---

## 📮 Postman

Collection em `postman/Transaction_Guardian_API.postman_collection.json`

**16+ Requests incluídas**

---

## 🏗️ Roadmap

| Phase | Status | Features |
|-------|--------|----------|
| Phase 1 | ✅ | TimescaleDB, Grafana Integration |
| Phase 2 | ✅ | Redis Cache, Rate Limiting |
| Phase 3 | 🔜 | Security (OAuth2, JWT) |
| Phase 4 | 📋 | MLOps (MLflow) |
| Phase 5 | 📋 | Clawdbot (Telegram/WhatsApp) |

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

*"Bombeiros que usam código para apagar incêndios." 🔥*
