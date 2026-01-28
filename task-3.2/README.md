# 🛡️ Transaction Guardian v2.1

> **CloudWalk Monitoring Intelligence Challenge - Task 3.2**

Sistema de monitoramento de transações em tempo real com detecção automática de anomalias, cache de alta performance, e autenticação segura.

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

---

## 🏗️ Evolution Roadmap

### ✅ Phase 1: Foundation
> TimescaleDB + Data Migration

| Feature | Status |
|---------|--------|
| TimescaleDB | ✅ |
| 42,920 transactions migrated | ✅ |
| Hypertables & Continuous Aggregates | ✅ |
| pgAdmin | ✅ |

📄 [Phase 1 Documentation](docs/PHASE1_COMPLETE.md)

---

### ✅ Phase 2: Performance
> Redis Cache + Rate Limiting

| Feature | Status |
|---------|--------|
| Redis Cache (<10ms responses) | ✅ |
| Rate Limiting (100 req/min) | ✅ |
| Redis Commander UI | ✅ |
| Cache Stats endpoint | ✅ |

📄 [Phase 2 Documentation](docs/PHASE2_COMPLETE.md)

---

### ✅ Phase 3: Security ← ATUAL
> JWT + API Key Authentication

| Feature | Status |
|---------|--------|
| JWT Authentication | ✅ |
| API Key Authentication | ✅ |
| Role-based Access (RBAC) | ✅ |
| 3 Default Users | ✅ |

📄 [Phase 3 Documentation](docs/PHASE3_COMPLETE.md)

---

### 🔜 Future Phases

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 4 | MLOps (MLflow) | 📋 Planned |
| Phase 5 | Clawdbot (Telegram) | 📋 Planned |
| Phase 6 | Observability | 📋 Planned |

---

## 🔐 Authentication (Phase 3)

### JWT Login
```bash
# Get token
curl -X POST http://34.39.251.57:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token
curl -H "Authorization: Bearer <token>" \
  http://34.39.251.57:8001/auth/me
```

### API Key
```bash
curl -H "X-API-Key: guardian-api-key-2024" \
  http://34.39.251.57:8001/auth/me
```

### Default Users

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | admin |
| `operator` | `operator123` | operator |
| `viewer` | `viewer123` | viewer |

---

## 🎯 Task 3.2 Requirements

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Endpoint que recebe transações | ✅ | `POST /transaction` |
| Retorna recomendação de alerta | ✅ | `is_anomaly`, `alert_level`, `recommendation` |
| Query para organizar dados | ✅ | `GET /anomalies?level=CRITICAL` |
| Gráfico em tempo real | ✅ | Grafana (5 dashboards, 31 painéis) |
| Modelo de anomalias | ✅ | Isolation Forest + Rules + Z-Score |
| Sistema de notificação automática | ✅ | Alertmanager + Slack |

---

## 🚀 Quick Start
```bash
cd task-3.2/infrastructure

# Core services
docker compose up -d --build

# Phase 1: TimescaleDB
docker compose -f docker-compose.timescale.yml up -d

# Phase 2: Redis
docker compose -f docker-compose.redis.yml up -d
```

---

## 📁 Project Structure
```
task-3.2/
├── code/
│   ├── main.py              # FastAPI v2.1
│   ├── auth.py              # 🆕 JWT/API Key module
│   ├── auth_routes.py       # 🆕 Auth endpoints
│   ├── cache.py             # Redis cache
│   ├── anomaly_detector.py  # ML + Rules
│   └── alert_manager.py     # Notifications
├── dashboards/              # 5 Grafana dashboards
├── docs/
│   ├── PHASE1_COMPLETE.md
│   ├── PHASE2_COMPLETE.md
│   └── PHASE3_COMPLETE.md   # 🆕
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose.redis.yml
│   └── docker-compose.timescale.yml
└── README.md
```

---

## 🐳 Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| API | 8001 | FastAPI v2.1 |
| Grafana | 3002 | Dashboards |
| Prometheus | 9091 | Metrics |
| Alertmanager | 9093 | Alerts |
| Redis | 6379 | Cache |
| Redis Commander | 8081 | Redis UI |
| TimescaleDB | 5432 | Database |
| pgAdmin | 5050 | DB Admin |

---

## 🔍 Detection Methods

| Method | Weight | Description |
|--------|--------|-------------|
| Isolation Forest | 60% | Machine Learning |
| Z-Score | 40% | Statistical |
| Rule-based | Flags | Thresholds |

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

**Branch:** `phase3-security` | **Version:** 2.1.0
