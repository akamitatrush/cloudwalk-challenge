# 🛡️ Transaction Guardian - Task 3.2

**CloudWalk Monitoring Intelligence Challenge**

Sistema de monitoramento de transações em tempo real com detecção automática de anomalias.

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

## 🚀 Quick Start

```bash
cd infrastructure
docker compose up -d --build

# Acessar:
# API Swagger: http://localhost:8001/docs
# Grafana:     http://localhost:3002 (admin/admin)
# Prometheus:  http://localhost:9091
```

---

## 📁 Estrutura

```
task-3.2/
├── assets/              # Screenshots
├── code/                # Scripts Python (4 arquivos, ~1.300 linhas)
│   ├── main.py              # FastAPI (9 endpoints)
│   ├── anomaly_detector.py  # ML + Rules detector
│   ├── alert_manager.py     # Sistema de notificações
│   └── simulator.py         # Gerador de transações
├── dashboards/          # 5 Dashboards Grafana (31 painéis)
│   ├── transaction_guardian.json     # Real-time Monitoring
│   ├── sla_slo_dashboard.json        # SLA/SLO
│   ├── alerts_incidents_dashboard.json # Alertas & Incidentes
│   ├── historical_analysis_dashboard.json # Análise Histórica
│   └── executive_summary_dashboard.json   # Executive Summary
├── data/                # CSVs do desafio
├── docs/                # Documentação detalhada
├── infrastructure/      # Docker, Prometheus, Grafana
├── interactive/         # Notebook Colab
├── media/               # Vídeos (NotebookLM)
├── postman/             # Collection Postman (16 requests)
├── prompts/             # Prompts para IA
├── README.md
└── README_GITHUB.md
```

---

## 📊 DASHBOARDS GRAFANA (5 Total)

### 1. 🛡️ Transaction Guardian (Real-time)
- Total Transações
- Anomalias Detectadas
- Taxa de Aprovação (Gauge)
- Transações/Minuto
- Volume em Tempo Real
- Distribuição por Status
- Taxa de Anomalias

### 2. 📈 SLA/SLO Dashboard
- Uptime (SLA) - Meta 99.9%
- Latência Média
- Taxa de Erro
- SLA Compliance (Semáforo)
- Uptime ao Longo do Tempo
- Taxa de Erro por Hora
- P95/P99 Latência
- Taxa de Sucesso

### 3. 🚨 Alertas & Incidentes
- Total Alertas (Hoje)
- CRITICAL / WARNING
- MTTR (Mean Time To Recovery)
- Timeline de Alertas
- Incidentes por Severidade (Pie)
- Histórico Stacked
- MTTA / MTBF
- Incidentes Ativos

### 4. 📊 Análise Histórica
- Comparação Dia a Dia
- Heatmap por Hora
- Tendência Semanal
- Média Histórica / Pico / Vale
- Variação %
- Análise de Sazonalidade

### 5. 👔 Executive Summary
- Status Geral (Semáforo)
- KPIs Principais (4 cards)
- Volume (Gráfico)
- Distribuição por Status
- Variação vs Período Anterior
- Meta do Período

---

## 🔍 Métodos de Detecção

### 1. Machine Learning (Isolation Forest)
### 2. Rule-based (Thresholds)
### 3. Statistical (Z-Score)

**Score Combinado:** `60% ML + 40% Z-Score`

---

## 📊 Portas (Task 3.2)

| Serviço | Porta | URL |
|---------|-------|-----|
| API | 8001 | http://localhost:8001/docs |
| Grafana | 3002 | http://localhost:3002 |
| Prometheus | 9091 | http://localhost:9091 |

---

## 📮 Postman

Collection em `postman/Transaction_Guardian_API.postman_collection.json`

**16 Requests incluídas**

---

## 👤 Autor

**Sérgio**  
Candidato: Monitoring Intelligence Analyst (Night Shift)  
CloudWalk Challenge - January 2025

---

*"Bombeiros que usam código para apagar incêndios."* 🔥
