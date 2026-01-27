# 🚀 CloudWalk Monitoring Analyst Challenge

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Grafana-Dashboards-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana">
  <img src="https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/ML-Isolation_Forest-FF6F00?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="ML">
  <img src="https://img.shields.io/badge/Task_3.1-Complete-success?style=for-the-badge" alt="Task 3.1">
  <img src="https://img.shields.io/badge/Task_3.2-Complete-success?style=for-the-badge" alt="Task 3.2">
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/akamitatrush/cloudwalk-challenge?style=flat-square" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/akamitatrush/cloudwalk-challenge?style=flat-square" alt="Repo Size">
</p>

---

**Candidato:** Sérgio  
**Vaga:** Monitoring Intelligence Analyst (Night Shift)

> *"We want firefighters that use code to stop the fire."* - CloudWalk

---

## 📋 Estrutura do Desafio

| Task | Descrição | Status |
|------|-----------|--------|
| 3.1 | Anomaly Detection Analysis | ✅ Completo |
| 3.2 | Real-Time Alert System | ✅ Completo |

---

## 🎯 Task 3.1 - Anomaly Detection

### Descoberta Principal
- **Anomalia:** 3 horas consecutivas (15h-17h) com ZERO transações
- **Impacto:** ~62 transações perdidas
- **Causa provável:** Outage do sistema de pagamento

### Ferramentas Utilizadas
- Grafana + Prometheus + Alertmanager
- Metabase + SQL
- Python + Docker

📂 [Ver documentação completa](./task-3.1/README.md)

---

## 🛡️ Task 3.2 - Transaction Guardian

### Sistema Desenvolvido
**Transaction Guardian** - Sistema de monitoramento em tempo real com:
- **API FastAPI** para receber transações
- **3 métodos de detecção:** ML (Isolation Forest) + Z-Score + Rules
- **5 Dashboards Grafana** com 31 painéis
- **Alertas automáticos** via Prometheus + Alertmanager

### Requisitos Atendidos
| Requisito | Status |
|-----------|--------|
| Endpoint que recebe transações | ✅ |
| Query para organizar dados | ✅ |
| Gráfico em tempo real | ✅ |
| Modelo para anomalias (ML) | ✅ |
| Sistema de notificação | ✅ |
| Alertar FAILED/DENIED/REVERSED | ✅ |

### Quick Start
```bash
cd task-3.2/infrastructure
docker compose up -d --build

# Acessar:
# API Swagger: http://localhost:8001/docs
# Grafana: http://localhost:3002 (admin/admin)
```

📂 [Ver documentação completa](./task-3.2/README.md)

---

## 🚀 Roadmap v2.0

Plano de evolução para produção enterprise:

| Fase | Descrição | Status |
|------|-----------|--------|
| 1. Foundation | TimescaleDB, Redis, CI/CD | 📋 Planejado |
| 2. Performance | Kafka, Workers Async | 📋 Planejado |
| 3. Security | OAuth2, Vault | 📋 Planejado |
| 4. MLOps | MLflow, Airflow | 📋 Planejado |
| 5. Clawdbot 🦞 | AI Assistant para Night Shift | 📋 Planejado |
| 6. Observability | OpenTelemetry, Jaeger | 📋 Planejado |

📂 [Ver roadmap completo](./docs/roadmap/)

---

## 📊 Números do Projeto

| Métrica | Valor |
|---------|-------|
| Dashboards Grafana | 5 |
| Painéis de monitoramento | 31 |
| Endpoints API | 9 |
| Documentos técnicos | 8+ |
| Linhas de código Python | ~1.500 |
| Tempo de detecção | < 30s |

---

## 🔗 Links Úteis

| Recurso | Link |
|---------|------|
| 📦 Release v1.0.0 | [Challenge Complete](https://github.com/akamitatrush/cloudwalk-challenge/releases/tag/1.0.0) |
| 📦 Release v2.0.0 | [Enterprise Roadmap](https://github.com/akamitatrush/cloudwalk-challenge/releases/tag/v2.0.0) |
| 🦞 Clawdbot | [github.com/clawdbot/clawdbot](https://github.com/clawdbot/clawdbot) |

---

## 💡 Filosofia

> *"Não entreguei só código - entreguei uma solução completa com documentação, dashboards e runbooks."*

Este projeto demonstra:
- ✅ Capacidade de análise de dados de transações
- ✅ Construção de sistemas de monitoramento completos
- ✅ Documentação profissional
- ✅ Visão de arquitetura enterprise
- ✅ Mentalidade de firefighter: prevenção > reação

---

**CloudWalk Challenge** - Janeiro 2025
