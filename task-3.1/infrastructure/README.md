# 🚀 CloudWalk Monitoring Stack

## Grafana + Prometheus + Alertmanager Setup

Este projeto implementa uma stack completa de monitoramento para análise de transações de checkout, incluindo:

- **Grafana**: Dashboards e visualizações
- **Prometheus**: Coleta de métricas e alertas
- **Alertmanager**: Roteamento e notificação de alertas
- **Custom Exporter**: Conversão de dados CSV para métricas Prometheus

---

## 📋 Estrutura do Projeto

```
grafana_prometheus/
├── docker-compose.yml          # Orquestração dos containers
├── Dockerfile.exporter         # Build do exporter customizado
├── checkout_exporter.py        # Script que expõe métricas
├── data/
│   ├── checkout_1.csv          # Dados do POS 1 (normal)
│   └── checkout_2.csv          # Dados do POS 2 (com anomalia)
├── prometheus/
│   ├── prometheus.yml          # Config principal do Prometheus
│   └── checkout_alerts.yml     # Regras de alerta
├── alertmanager/
│   └── alertmanager.yml        # Config de notificações
└── grafana/
    ├── dashboards/
    │   └── checkout_monitoring.json  # Dashboard importável
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml       # Auto-config datasource
        └── dashboards/
            └── dashboards.yml        # Auto-load dashboards
```

---

## 🚀 Quick Start

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Portas disponíveis: 3000, 8000, 9090, 9093, 9100

### 2. Iniciar a Stack

```bash
# Clone ou copie os arquivos
cd grafana_prometheus

# Copie os CSVs para a pasta data
mkdir -p data
cp /path/to/checkout_1.csv data/
cp /path/to/checkout_2.csv data/

# Inicie todos os serviços
docker-compose up -d

# Verifique se estão rodando
docker-compose ps
```

### 3. Acessar os Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Alertmanager** | http://localhost:9093 | - |
| **Metrics Exporter** | http://localhost:8000/metrics | - |

### 4. Importar Dashboard (se não carregou automaticamente)

1. Acesse Grafana → Dashboards → Import
2. Upload do arquivo `grafana/dashboards/checkout_monitoring.json`
3. Selecione Prometheus como datasource
4. Click "Import"

---

## 📊 Métricas Disponíveis

### Métricas de Transações

| Métrica | Descrição | Labels |
|---------|-----------|--------|
| `checkout_transactions_hourly` | Transações por hora | hour, period, dataset |
| `checkout_transactions_current` | Transações hora atual | dataset |
| `checkout_transactions_avg_week` | Média semanal hora atual | dataset |
| `checkout_transactions_total_today` | Total do dia | dataset |
| `checkout_transactions_total_yesterday` | Total de ontem | dataset |

### Métricas de Anomalia

| Métrica | Descrição | Labels |
|---------|-----------|--------|
| `checkout_anomaly_status` | Status por hora | hour, status, dataset |
| `checkout_deviation_percentage` | Desvio da média (%) | hour, dataset |

---

## 🔔 Alertas Configurados

### Severidade CRITICAL (P1)

| Alerta | Condição | Ação |
|--------|----------|------|
| `ZeroTransactionsCritical` | TX = 0 em horário comercial | PagerDuty + Slack + Email |
| `TransactionDropCritical` | Queda > 90% | PagerDuty + Slack + Email |

### Severidade HIGH (P2)

| Alerta | Condição | Ação |
|--------|----------|------|
| `TransactionDropHigh` | Queda > 50% | Slack #incidents-critical |
| `ConsecutiveZeroTransactions` | 2+ horas com zero | Slack #incidents-critical |

### Severidade MEDIUM (P3)

| Alerta | Condição | Ação |
|--------|----------|------|
| `TransactionSpikeDetected` | Aumento > 200% | Slack #monitoring-alerts |
| `StatisticalAnomalyDetected` | Z-Score > 2.5 | Slack #monitoring-alerts |

---

## 📝 PromQL Queries Úteis

### Queries Básicas

```promql
# Transações da hora atual
checkout_transactions_current

# Desvio percentual da média
((checkout_transactions_current - checkout_transactions_avg_week) 
  / checkout_transactions_avg_week) * 100

# Total de transações hoje
sum(checkout_transactions_hourly{period="today"})
```

### Queries de Anomalia

```promql
# Horas com zero transações
checkout_transactions_hourly{period="today"} == 0

# Horas abaixo de 50% da média
checkout_transactions_hourly{period="today"} 
  < checkout_transactions_hourly{period="avg_last_week"} * 0.5

# Z-Score calculation
(checkout_transactions_current - avg_over_time(checkout_transactions_current[7d]))
  / stddev_over_time(checkout_transactions_current[7d])
```

### Queries de Agregação

```promql
# Média de transações por hora (últimas 24h)
avg_over_time(checkout_transactions_current[24h])

# Máximo de transações por hora (última semana)
max_over_time(checkout_transactions_hourly{period="today"}[7d])

# Taxa de variação (por minuto)
rate(checkout_transactions_total[5m]) * 60
```

---

## 🛠️ Customização

### Adicionar Novo Dataset

1. Copie o CSV para `data/`
2. Modifique `docker-compose.yml`:
   ```yaml
   checkout-exporter-new:
     # ... copie a config existente
     environment:
       - CSV_PATH=/data/novo_checkout.csv
       - DATASET_NAME=checkout_3
   ```
3. Adicione target em `prometheus/prometheus.yml`
4. Reinicie: `docker-compose up -d`

### Modificar Thresholds de Alerta

Edite `prometheus/checkout_alerts.yml`:
```yaml
# Exemplo: mudar threshold de zero transactions
- alert: ZeroTransactionsCritical
  expr: |
    checkout_transactions_current == 0 
    and ON() hour() >= 8          # Mudou de 10 para 8
    and ON() hour() <= 23         # Mudou de 22 para 23
```

### Configurar Notificações Reais

Edite `alertmanager/alertmanager.yml`:
```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/SEU/WEBHOOK/REAL'
  
receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#seu-canal-de-incidentes'
```

---

## 🔧 Troubleshooting

### Grafana não mostra dados

```bash
# Verificar se exporter está rodando
curl http://localhost:8000/metrics

# Verificar se Prometheus está coletando
curl http://localhost:9090/api/v1/targets
```

### Alertas não disparam

```bash
# Verificar regras carregadas
curl http://localhost:9090/api/v1/rules

# Verificar Alertmanager
curl http://localhost:9093/api/v2/alerts
```

### Reiniciar stack

```bash
docker-compose down
docker-compose up -d --build
```

---

## 📚 Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

---

## 👤 Autor

**Sérgio** - Monitoring Intelligence Analyst Challenge  
CloudWalk Technical Assessment - Task 3.1

---

*"Where there is data smoke, there is business fire." — Thomas Redman*
