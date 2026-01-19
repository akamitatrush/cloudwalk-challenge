# 🚀 CloudWalk Monitoring Analyst Challenge

**Candidato:** Sérgio  
**Vaga:** Monitoring Intelligence Analyst (Night Shift)

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

📂 [Ver documentação completa](./task-3.2/README.md)

---

## 🚀 Quick Start

### Task 3.1
```bash
cd task-3.1/infrastructure
docker compose up -d

# Acessar:
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# Metabase: http://localhost:3001
```

### Task 3.2
```bash
cd task-3.2/infrastructure
docker compose up -d --build

# Acessar:
# API Swagger: http://localhost:8001/docs
# Grafana: http://localhost:3002 (admin/admin)
# Prometheus: http://localhost:9091
# Alertmanager: http://localhost:9093
```

---

## 📊 Tecnologias Utilizadas

| Tecnologia | Task 3.1 | Task 3.2 |
|------------|----------|----------|
| Python | ✅ | ✅ |
| Grafana | ✅ | ✅ |
| Prometheus | ✅ | ✅ |
| Alertmanager | ✅ | ✅ |
| Docker | ✅ | ✅ |
| FastAPI | - | ✅ |
| Machine Learning | - | ✅ |
| Metabase | ✅ | ✅ |

---

## 📁 Estrutura do Repositório
```
cloudwalk-challenge/
├── task-3.1/                    # Anomaly Detection Analysis
│   ├── assets/                  # Gráficos gerados
│   ├── code/                    # Scripts Python e SQL
│   ├── dashboards/              # Dashboards Grafana
│   ├── docs/                    # Documentação completa
│   ├── infrastructure/          # Docker stack
│   └── README.md
│
├── task-3.2/                    # Transaction Guardian
│   ├── assets/                  # Gráficos gerados
│   ├── code/                    # API FastAPI + Detector
│   ├── dashboards/              # 5 Dashboards Grafana
│   ├── docs/                    # Documentação completa
│   ├── infrastructure/          # Docker stack
│   ├── postman/                 # Collection Postman
│   └── README.md
│
└── README.md                    # Este arquivo
```

---

## 👤 Sobre o Candidato

**Sérgio** - System Analyst com 14+ anos de experiência em TI, sendo quase 7 anos em sistemas de pagamento (TIVIT/Cielo). Especializado em monitoramento, infraestrutura e resposta a incidentes.

> *"We want firefighters that use code to stop the fire."*
>
> O **Transaction Guardian** detecta incêndios antes que se espalhem! 🔥

---

*CloudWalk Challenge - Janeiro 2025*
