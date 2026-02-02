# 🛡️ Transaction Guardian v2.2

> **CloudWalk Monitoring Intelligence Challenge - Task 3.2**

Sistema de monitoramento de transações em tempo real com detecção de anomalias, ML, alertas inteligentes e relatórios automáticos por IA.

---

## 🌐 Live Demo (Online 24/7)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **🔗 API Docs** | http://34.39.251.57:8001/docs | - |
| **📊 Grafana** | http://34.39.251.57:3002 | - |
| **📈 Prometheus** | http://34.39.251.57:9091 | - |
| **🚨 Alertmanager** | http://34.39.251.57:9093 | - |
| **🔴 Redis Commander** | http://34.39.251.57:8081 | - |
| **🐘 pgAdmin** | http://34.39.251.57:5050 | - |
| **🧠 MLflow** | http://34.39.251.57:5000 | - |

---

## 🏗️ Evolution Roadmap

### ✅ Phase 1: Foundation
> TimescaleDB + Data Migration

- TimescaleDB para séries temporais
- 42,920+ transações migradas
- Hypertables & Continuous Aggregates

📄 [Phase 1 Documentation](docs/PHASE1_COMPLETE.md)

---

### ✅ Phase 2: Performance
> Redis Cache + Rate Limiting

- Redis Cache (<10ms responses)
- Rate Limiting (100 req/min)
- Cache Stats endpoint

📄 [Phase 2 Documentation](docs/PHASE2_COMPLETE.md)

---

### ✅ Phase 3: Security
> JWT + API Key Authentication

- JWT Authentication (24h expiration)
- API Key Authentication
- Role-based Access Control (RBAC)

📄 [Phase 3 Documentation](docs/PHASE3_COMPLETE.md)

---

### ✅ Phase 4: MLOps
> MLflow Model Management

- Model versioning & registry
- Experiment tracking
- Model promotion to Production
- Drift detection

📄 [Phase 4 Documentation](docs/PHASE4_COMPLETE.md)

---

### ✅ Phase 5: Telegram Bot
> Real-time Alerts via Telegram

- Bot: `@omega_transaction_bot`
- Auto-alerts on CRITICAL/WARNING
- Commands: `/status`, `/stats`, `/anomalies`, `/health`
- Password protected

📄 [Phase 5 Documentation](docs/PHASE5_COMPLETE.md)

---

### ✅ Phase 6: AI Summary
> AI-powered Daily Reports

- Automated daily reports
- Anomaly analysis & insights
- Health score calculation
- Recommendations

📄 [Phase 6 Documentation](docs/PHASE6_COMPLETE.md)

---

### 🔜 Future Phases

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 7 | Prediction Engine | 📋 Planned |
| Phase 8 | ChatOps (Slack) | 📋 Planned |
| Phase 9 | Kubernetes | 📋 Planned |

---

## 🔐 Authentication

### JWT Login
```bash
curl -X POST http://34.39.251.57:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "<password>"}'
```

### API Key
```bash
curl -H "X-API-Key: guardian-api-key-2024" \
  http://34.39.251.57:8001/auth/me
```

### Default Users

| Username | Password | Role |
|----------|----------|------|
| `admin` | `<password>` | admin |
| `operator` | `operator123` | operator |
| `viewer` | `viewer123` | viewer |

---

## 📱 Telegram Bot
```
Bot: @omega_transaction_bot
Senha: <password>

Comandos:
/start <senha> - Autenticar
/status        - Status do sistema
/stats         - Estatísticas
/anomalies     - Últimas anomalias
/health        - Health check
```

---

## 📊 AI Reports
```bash
# Gerar relatório
curl http://34.39.251.57:8001/ai/report

# Enviar por Telegram
curl -X POST http://34.39.251.57:8001/ai/report/send
```

---

## 🎯 Task 3.2 Requirements

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Endpoint transações | ✅ | `POST /transaction` |
| Recomendação de alerta | ✅ | `alert_level`, `recommendation` |
| Query para dados | ✅ | `GET /anomalies?level=CRITICAL` |
| Gráfico tempo real | ✅ | Grafana (5 dashboards) |
| Modelo anomalias | ✅ | Isolation Forest + Z-Score |
| Notificação automática | ✅ | Alertmanager + Telegram |

---

## 🐳 Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| API | 8001 | FastAPI v2.2 |
| Grafana | 3002 | Dashboards |
| Prometheus | 9091 | Metrics |
| Alertmanager | 9093 | Alerts |
| Redis | 6379 | Cache |
| Redis Commander | 8081 | Redis UI |
| TimescaleDB | 5432 | Database |
| pgAdmin | 5050 | DB Admin |
| MLflow | 5000 | ML Platform |

---

## 🔍 Detection Methods

| Method | Weight | Description |
|--------|--------|-------------|
| Isolation Forest | 60% | Machine Learning |
| Z-Score | 40% | Statistical |
| Rule-based | Flags | Thresholds |

---

## 📁 Project Structure
```
task-3.2/
├── code/
│   ├── main.py              # FastAPI v2.2
│   ├── auth.py              # JWT/API Key
│   ├── auth_routes.py       # Auth endpoints
│   ├── cache.py             # Redis cache
│   ├── mlops.py             # MLflow integration
│   ├── mlops_routes.py      # MLOps endpoints
│   ├── telegram_bot.py      # Telegram bot
│   ├── telegram_routes.py   # Telegram endpoints
│   ├── ai_summary.py        # AI reports
│   ├── ai_summary_routes.py # AI endpoints
│   ├── anomaly_detector.py  # ML detection
│   └── alert_manager.py     # Notifications
├── dashboards/              # Grafana dashboards
├── docs/                    # Phase documentation
└── infrastructure/          # Docker configs
```

---

## 🚀 Quick Start
```bash
cd task-3.2/infrastructure

# All services
docker compose up -d --build
docker compose -f docker-compose.redis.yml up -d
docker compose -f docker-compose.timescale.yml up -d
docker compose -f docker-compose.mlflow.yml up -d
```

---

## 👤 Author

**Sérgio Henrique**

| | |
|---|---|
| 📧 Email | sergio@lognullsec.com |
| 💼 LinkedIn | [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva) |
| 🐙 GitHub | [github.com/akamitatrush](https://github.com/akamitatrush) |

**Candidatura:** Monitoring Intelligence Analyst (Night Shift) - CloudWalk

---

*"Bombeiros que usam código para apagar incêndios." 🔥*

**Branch:** `phase6-ai-summary` | **Version:** 2.2.0
