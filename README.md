# 🚀 CloudWalk Monitoring Analyst Challenge

> **Sistema Enterprise de Monitoramento de Transações em Tempo Real**
>
> Desafio técnico para a posição de **Monitoring Intelligence Analyst (Night Shift)**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Ruby](https://img.shields.io/badge/Ruby-3.0-red?logo=ruby)](https://ruby-lang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-Cache-red?logo=redis)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Versões e Entregas](#-versões-e-entregas)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Arquitetura](#-arquitetura)
- [Quick Start](#-quick-start)
- [Documentação](#-documentação)

---

## 🎯 Sobre o Projeto

O **Transaction Guardian** é um sistema completo de monitoramento que detecta anomalias em transações financeiras em tempo real, prevê incidentes antes que aconteçam, e alerta operadores automaticamente.

### Mentalidade "Firefighter"

> *"Não apagamos incêndios - prevenimos que comecem."*

O sistema foi desenvolvido com a mentalidade de bombeiro: detectar sinais de fumaça (anomalias) antes que virem incêndios (outages).

---

## 📦 Versões e Entregas

| Tag | Data | Descrição | Status |
|-----|------|-----------|--------|
| `v2.0.0` | 28 Jan 2026 | **✅ Entrega Oficial Task 3.2** | Avaliação |
| `main` | 02 Fev 2026 | Entrega + Evoluções Adicionais | Atual |

### 🔍 Para avaliar a entrega oficial:
```bash
git checkout v2.0.0
```

### 🚀 Para ver todas as evoluções:
```bash
git checkout main
```

---

## 🌐 Live Demo

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 📚 **API Docs** | http://34.39.251.57:8001/docs | Swagger/OpenAPI |
| 🛡️ **Shugo Dashboard** | http://34.39.251.57:8001/shugo/dashboard | Predição de Anomalias |
| 📊 **Grafana** | http://34.39.251.57:3002 | Dashboards |
| 📈 **Prometheus** | http://34.39.251.57:9091 | Métricas |
| 🧪 **MLflow** | http://34.39.251.57:5000 | ML Platform |
| 📱 **Telegram Bot** | @omega_transaction_bot | Alertas |

> ⚠️ Credenciais disponíveis sob demanda para avaliadores

---

## ✨ Features

### 📦 Entrega Original (v2.0.0)

| Feature | Descrição |
|---------|-----------|
| 🔍 Detecção de Anomalias | ML (Isolation Forest) + Estatística (Z-Score) + Regras |
| 📊 Grafana Dashboards | Visualização em tempo real |
| 📈 Prometheus Metrics | Métricas customizadas |
| 🚨 Alertmanager | Gestão de alertas |
| 🐳 Docker Compose | Deploy containerizado |

### 🚀 Evoluções Adicionais

| Phase | Feature | Tecnologia |
|-------|---------|------------|
| **2** | ⚡ Redis Cache | Cache < 10ms, Rate Limiting |
| **3** | 🔐 Autenticação | JWT + API Keys + RBAC |
| **4** | 🧪 MLOps | MLflow model versioning |
| **5** | 📱 Telegram Bot | Alertas em tempo real |
| **6** | 🤖 AI Summary | Relatórios automáticos |
| **7** | 🛡️ Shugo 守護 | **Prediction Engine** |
| **8** | 💎 Ruby SDK | CLI + Client Library |

---

## 🛡️ Shugo 守護 - Prediction Engine

> *"Vê o futuro, protege o presente"*

O **Shugo** (守護 = Guardião em japonês) é o diferencial do projeto: um engine de predição que **antecipa anomalias antes que aconteçam**.

### Como funciona:
```
📊 Aprende padrões → 🔮 Prevê volume → ⚠️ Alerta antes
```

### Dashboard:

![Shugo Dashboard](task-3.2/code/static/shugo_preview.png)

Acesse: http://34.39.251.57:8001/shugo/dashboard

---

## 💎 Ruby SDK & CLI

Demonstrando conhecimento em **Ruby** (stack CloudWalk):
```ruby
# Como biblioteca
require 'guardian'

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
│                                                              │
│   ┌─────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  Ruby   │───▶│   FastAPI   │───▶│   Shugo     │        │
│   │   CLI   │    │   (Python)  │    │  Prediction │        │
│   └─────────┘    └──────┬──────┘    └─────────────┘        │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│   ┌─────────┐    ┌─────────────┐  ┌─────────────┐          │
│   │  Redis  │    │ TimescaleDB │  │   MLflow    │          │
│   │  Cache  │    │  (Postgres) │  │   (MLOps)   │          │
│   └─────────┘    └─────────────┘  └─────────────┘          │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│   ┌─────────┐    ┌─────────────┐  ┌─────────────┐          │
│   │Prometheus│   │   Grafana   │  │  Telegram   │          │
│   │(Metrics)│    │ (Dashboards)│  │    Bot      │          │
│   └─────────┘    └─────────────┘  └─────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

### Instalação
```bash
# Clone
git clone https://github.com/akamitatrush/cloudwalk-challenge.git
cd cloudwalk-challenge/task-3.2/infrastructure

# Iniciar
docker compose up -d --build

# Verificar
curl http://localhost:8001/health
```

### Ruby CLI
```bash
cd task-3.2/ruby-sdk
gem install httparty thor terminal-table colorize
./bin/guardian status --url http://localhost:8001
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [DOCUMENTATION.md](task-3.2/docs/DOCUMENTATION.md) | Documentação técnica completa |
| [FAQ_DETAILED.md](task-3.2/docs/FAQ_DETAILED.md) | Perguntas frequentes e decisões técnicas |
| [RUNBOOK.md](task-3.2/docs/RUNBOOK.md) | Guia operacional |
| [Ruby SDK README](task-3.2/ruby-sdk/README.md) | Documentação do SDK Ruby |

---

## 📊 Tecnologias

| Categoria | Tecnologias |
|-----------|-------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy |
| **Frontend** | React, Tailwind CSS, Chart.js |
| **Database** | TimescaleDB (PostgreSQL), Redis |
| **ML/AI** | Scikit-learn, MLflow |
| **Monitoring** | Prometheus, Grafana, Alertmanager |
| **DevOps** | Docker, Docker Compose |
| **SDK** | Ruby 3.0, Thor, HTTParty |

---

## 👤 Autor

**Sérgio Henrique**

- 💼 [LinkedIn](https://linkedin.com/in/akasergiosilva)
- 🐙 [GitHub](https://github.com/akamitatrush)
- 📧 sergio@lognullsec.com

---

## 📄 Licença

MIT License - CloudWalk Challenge 2026

---

*Desenvolvido com 🔥 e mentalidade de bombeiro*
