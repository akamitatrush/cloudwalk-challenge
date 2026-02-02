# 🚀 CloudWalk Monitoring Analyst Challenge

> **Sistema Enterprise de Monitoramento de Transações em Tempo Real**
>
> Desafio técnico para a posição de **Monitoring Intelligence Analyst (Night Shift)**

<!-- Badges de Tecnologia -->
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ruby](https://img.shields.io/badge/Ruby-3.0-CC342D?style=for-the-badge&logo=ruby&logoColor=white)](https://ruby-lang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<!-- Badges de Infraestrutura -->
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![PostgreSQL](https://img.shields.io/badge/TimescaleDB-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://timescale.com)

<!-- Badges de ML -->
[![Scikit-learn](https://img.shields.io/badge/ML-Isolation_Forest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![MLflow](https://img.shields.io/badge/MLOps-MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org)

<!-- Badges de Status -->
[![Task 3.1](https://img.shields.io/badge/Task_3.1-Complete-success?style=for-the-badge)](task-3.1/)
[![Task 3.2](https://img.shields.io/badge/Task_3.2-Complete-success?style=for-the-badge)](task-3.2/)
[![Shugo](https://img.shields.io/badge/🛡️_Shugo-Prediction_Engine-blueviolet?style=for-the-badge)](http://34.39.251.57:8001/shugo/dashboard)

<!-- Badges de Info -->
![Last Commit](https://img.shields.io/github/last-commit/akamitatrush/cloudwalk-challenge?style=for-the-badge)
![Repo Size](https://img.shields.io/github/repo-size/akamitatrush/cloudwalk-challenge?style=for-the-badge)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📦 Versões e Entregas

| Tag | Data | Descrição | Como acessar |
|-----|------|-----------|--------------|
| `v2.0.0` | 28 Jan 2026 | ✅ **Entrega Oficial Task 3.2** | `git checkout v2.0.0` |
| `main` | 02 Fev 2026 | 🚀 Entrega + Evoluções | Branch atual |

> 💡 **Para avaliadores:** A entrega oficial está na tag `v2.0.0`. As evoluções na `main` demonstram aprendizado contínuo e proatividade.

---

## 🌐 Live Demo

| Serviço | URL | Status |
|---------|-----|--------|
| 📚 **API Docs** | http://34.39.251.57:8001/docs | 🟢 Online |
| 🛡️ **Shugo Dashboard** | http://34.39.251.57:8001/shugo/dashboard | 🟢 Online |
| 📊 **Grafana** | http://34.39.251.57:3002 | 🟢 Online |
| 📈 **Prometheus** | http://34.39.251.57:9091 | 🟢 Online |
| 🧪 **MLflow** | http://34.39.251.57:5000 | 🟢 Online |
| 📱 **Telegram** | @omega_transaction_bot | 🟢 Online |

> ⚠️ Credenciais disponíveis sob demanda para avaliadores

---

## 🎯 Sobre o Projeto

O **Transaction Guardian** é um sistema completo de monitoramento que:

- 🔍 **Detecta** anomalias em tempo real (ML + Estatística + Regras)
- 🔮 **Prevê** incidentes antes que aconteçam (Shugo Engine)
- 🚨 **Alerta** operadores automaticamente (Telegram)
- 📊 **Visualiza** métricas em dashboards (Grafana)

### Mentalidade "Firefighter" 🔥

> *"Não apagamos incêndios - prevenimos que comecem."*

---

## ✨ Features

### 📦 Entrega Original (v2.0.0)

| Feature | Descrição |
|---------|-----------|
| 🔍 Anomaly Detection | Isolation Forest + Z-Score + Rules |
| 📊 Grafana Dashboards | 5+ dashboards customizados |
| 📈 Prometheus Metrics | 20+ métricas expostas |
| 🚨 Alertmanager | Gestão de alertas |
| 🐳 Docker Compose | Deploy completo |

### 🚀 Evoluções Adicionais (Demonstrando Proatividade)

| Phase | Feature | Tecnologia | Descrição |
|-------|---------|------------|-----------|
| **2** | ⚡ Cache | Redis | Respostas < 10ms |
| **3** | 🔐 Auth | JWT + API Keys | RBAC completo |
| **4** | 🧪 MLOps | MLflow | Model versioning |
| **5** | 📱 Bot | Telegram | Alertas real-time |
| **6** | 🤖 AI | Summary Reports | Relatórios automáticos |
| **7** | 🛡️ Shugo | Prediction Engine | **Prevê anomalias** |
| **8** | 💎 Ruby | SDK + CLI | Stack CloudWalk |

---

## 🛡️ Shugo 守護 - Prediction Engine

> *"Vê o futuro, protege o presente"*

O **Shugo** (守護 = Guardião) é o diferencial: prevê anomalias **ANTES** que aconteçam.
```
📊 Aprende padrões → 🔮 Prevê volume → ⚠️ Alerta antes do problema
```

**Dashboard:** http://34.39.251.57:8001/shugo/dashboard

---

## 💎 Ruby SDK & CLI

Demonstrando conhecimento em **Ruby** (stack CloudWalk):
```ruby
# Como biblioteca
client = Guardian::Client.new(api_url: "http://34.39.251.57:8001")
client.send_transaction(status: "approved", count: 150)
client.shugo.predict(minutes: 30)
```
```bash
# Como CLI
$ guardian status
$ guardian transaction approved 150
$ guardian shugo forecast 6
$ guardian anomalies --limit 10
```

---

## 🏗️ Arquitetura
```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN                      │
├─────────────────────────────────────────────────────────────┤
│   ┌─────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  Ruby   │───▶│   FastAPI   │───▶│   Shugo     │        │
│   │  CLI    │    │   (Python)  │    │  Prediction │        │
│   └─────────┘    └──────┬──────┘    └─────────────┘        │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│   ┌─────────┐    ┌─────────────┐  ┌─────────────┐          │
│   │  Redis  │    │ TimescaleDB │  │   MLflow    │          │
│   └─────────┘    └─────────────┘  └─────────────┘          │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│   ┌──────────┐   ┌─────────────┐  ┌─────────────┐          │
│   │Prometheus│   │   Grafana   │  │  Telegram   │          │
│   └──────────┘   └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start
```bash
# Clone
git clone https://github.com/akamitatrush/cloudwalk-challenge.git
cd cloudwalk-challenge/task-3.2/infrastructure

# Iniciar
docker compose up -d --build

# Verificar
curl http://localhost:8001/health

# Ruby CLI
cd ../ruby-sdk
./bin/guardian status
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [📖 DOCUMENTATION.md](task-3.2/docs/DOCUMENTATION.md) | Documentação técnica completa |
| [❓ FAQ_DETAILED.md](task-3.2/docs/FAQ_DETAILED.md) | Perguntas frequentes |
| [📋 RUNBOOK.md](task-3.2/docs/RUNBOOK.md) | Guia operacional |
| [💎 Ruby SDK](task-3.2/ruby-sdk/README.md) | SDK Ruby |

---

## 👤 Autor

**Sérgio Henrique**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/akasergiosilva)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akamitatrush)

---

<div align="center">

*Desenvolvido com 🔥 e mentalidade de bombeiro*

**Transaction Guardian v2.2** | CloudWalk Challenge 2026

</div>
