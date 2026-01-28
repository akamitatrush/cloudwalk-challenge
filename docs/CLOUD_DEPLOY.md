# ☁️ Transaction Guardian - Live Demo (Google Cloud)

> **Deploy realizado em Janeiro 2026 para demonstração 24/7 do projeto CloudWalk Challenge**

---

## 🔗 URLs de Acesso (Online 24/7)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **📊 API Docs (Swagger)** | http://34.39.251.57:8001/docs | - |
| **📈 Grafana** | http://34.39.251.57:3002 | `admin` / `admin` |
| **📉 Prometheus** | http://34.39.251.57:9091 | - |
| **🔔 Alertmanager** | http://34.39.251.57:9093 | - |
| **🗄️ pgAdmin** | http://34.39.251.57:5050 | `admin@example.com` / `admin` |
| **📊 Metabase** | http://34.39.251.57:3003 | - |

---

## 📊 Dashboard Principal (Recomendado)

**Transaction Guardian - Complete Dashboard:**

🔗 http://34.39.251.57:3002/d/dd143bad-ef42-4e2e-bdff-68fad25c9c92/transaction-guardian---complete

Este dashboard mostra:
- 📊 Total de Transações (42,920+)
- ✅ Transações Aprovadas
- ❌ Transações Negadas
- 💥 Transações com Falha
- 📈 Taxa de Aprovação (36.3%)
- 🚨 Anomalias Detectadas (538+)
- 📉 Gráfico temporal (últimas 24h)
- 🏢 Top 10 Merchants
- ⏰ Últimas transações em tempo real

---

## 🏗️ Arquitetura na Nuvem
```
┌─────────────────────────────────────────────────────────────┐
│           GOOGLE CLOUD PLATFORM                             │
│           Region: southamerica-east1 (São Paulo)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   VM: transaction-guardian                                  │
│   Specs: e2-medium (2 vCPU, 4GB RAM, 50GB SSD)             │
│   OS: Ubuntu 22.04 LTS                                      │
│   IP: 34.39.251.57                                          │
│                                                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │  FastAPI    │ │  Grafana    │ │ Prometheus  │          │
│   │  :8001      │ │  :3002      │ │  :9091      │          │
│   └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │Alertmanager │ │  pgAdmin    │ │  Metabase   │          │
│   │  :9093      │ │  :5050      │ │  :3003      │          │
│   └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│   ┌─────────────────────────────────────────────┐          │
│   │         TimescaleDB :5432                   │          │
│   │         42,920+ transactions                │          │
│   └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 Containers em Execução (7)

| Container | Imagem | Porta | Status |
|-----------|--------|-------|--------|
| guardian-api | Custom FastAPI | 8001 | ✅ Running |
| guardian-grafana | grafana/grafana:10.1.0 | 3002 | ✅ Running |
| guardian-prometheus | prom/prometheus:v2.47.0 | 9091 | ✅ Running |
| guardian-alertmanager | prom/alertmanager:v0.26.0 | 9093 | ✅ Running |
| guardian-timescaledb | timescale/timescaledb:latest-pg15 | 5432 | ✅ Running |
| guardian-pgadmin | dpage/pgadmin4:latest | 5050 | ✅ Running |
| guardian-metabase | metabase/metabase:latest | 3003 | ✅ Running |

---

## ✅ Requisitos do Desafio 3.2 - Todos Atendidos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Endpoint que recebe transações | ✅ | `POST /transaction` |
| Retorna recomendação de alerta | ✅ | `is_anomaly`, `alert_level`, `recommendation` |
| Query para organizar dados | ✅ | SQL no TimescaleDB + `/anomalies` endpoint |
| Gráfico em tempo real | ✅ | Grafana (5 dashboards, 31 painéis) |
| Modelo de anomalias | ✅ | Isolation Forest (ML) + Rules + Z-Score |
| Sistema de notificação automática | ✅ | Alertmanager + Slack |
| Alertar se failed acima do normal | ✅ | `"FAILED: Transação falhou"` |
| Alertar se reversed acima do normal | ✅ | `"REVERSED: Transação revertida"` |
| Alertar se denied acima do normal | ✅ | `"DENIED: Transação negada"` |

---

## 📡 API - Exemplo de Resposta

**Request:**
```bash
curl -X POST http://34.39.251.57:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-01-28T10:00:00", "status": "failed", "count": 1, "auth_code": "00"}'
```

**Response:**
```json
{
  "is_anomaly": true,
  "alert_level": "CRITICAL",
  "anomaly_score": 0.3,
  "rule_violations": [
    "LOW_VOLUME: 1 < 50 (possível outage)",
    "FAILED: Transação falhou"
  ],
  "recommendation": "🚨 CRÍTICO: Possível outage! Verificar conectividade."
}
```

---

## 🔧 Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `generate_realtime_data.py` | Gera dados no TimescaleDB | `python3 generate_realtime_data.py 10000 24` |
| `generate_api_traffic.py` | Gera tráfego na API (Prometheus) | `python3 generate_api_traffic.py` |
| `create_dashboard.py` | Cria dashboards no Grafana | `python3 create_dashboard.py` |

---

## 🚀 Como Reproduzir Localmente
```bash
# Clone o repositório
git clone https://github.com/akamitatrush/cloudwalk-challenge.git
cd cloudwalk-challenge/task-3.2/infrastructure

# Suba os containers
docker compose up -d

# Acesse
# API: http://localhost:8001/docs
# Grafana: http://localhost:3002
```

---

## 👤 Autor

**Sérgio Henrique**

| | |
|---|---|
| 📧 Email | sergio@lognullsec.com |
| 💼 LinkedIn | [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva) |
| 🐙 Repositório | [github.com/akamitatrush/cloudwalk-challenge](https://github.com/akamitatrush/cloudwalk-challenge) |

**Candidatura:** Monitoring Intelligence Analyst (Night Shift) - CloudWalk

---

*"Bombeiros que usam código para apagar incêndios." 🔥*
