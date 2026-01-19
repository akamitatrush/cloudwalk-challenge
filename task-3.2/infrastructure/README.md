# 🏗️ INFRASTRUCTURE - TRANSACTION GUARDIAN

## Docker Stack Configuration

---

## 📑 ÍNDICE

1. [Visão Geral](#1-visão-geral)
2. [Serviços](#2-serviços)
3. [Portas](#3-portas)
4. [Quick Start](#4-quick-start)
5. [Configuração](#5-configuração)
6. [Comandos Úteis](#6-comandos-úteis)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. VISÃO GERAL

Stack Docker para o Transaction Guardian contendo:
- API FastAPI com detector de anomalias
- Prometheus para métricas
- Grafana para dashboards
- Alertmanager para alertas
- Metabase para SQL analytics

### Arquitetura

```
┌─────────────────────────────────────────────────┐
│              Docker Network                      │
│            (guardian-network)                    │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   API    │  │Prometheus│  │ Grafana  │      │
│  │  :8001   │─▶│  :9091   │─▶│  :3002   │      │
│  └──────────┘  └────┬─────┘  └──────────┘      │
│                     │                           │
│               ┌─────▼─────┐  ┌──────────┐      │
│               │Alertmanager│  │ Metabase │      │
│               │   :9093   │  │  :3003   │      │
│               └───────────┘  └──────────┘      │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 2. SERVIÇOS

### guardian-api

| Property | Value |
|----------|-------|
| Image | Custom (Dockerfile) |
| Port | 8001:8000 |
| Health | /health |
| Docs | /docs (Swagger) |

### guardian-prometheus

| Property | Value |
|----------|-------|
| Image | prom/prometheus:v2.47.0 |
| Port | 9091:9090 |
| Config | prometheus/prometheus.yml |
| Alerts | prometheus/alerts.yml |

### guardian-grafana

| Property | Value |
|----------|-------|
| Image | grafana/grafana:10.1.0 |
| Port | 3002:3000 |
| User | admin |
| Password | admin |

### alertmanager

| Property | Value |
|----------|-------|
| Image | prom/alertmanager:v0.26.0 |
| Port | 9093:9093 |
| Config | alertmanager/alertmanager.yml |

### metabase

| Property | Value |
|----------|-------|
| Image | metabase/metabase:latest |
| Port | 3003:3000 |
| Setup | First access creates account |

---

## 3. PORTAS

| Service | Internal | External | URL |
|---------|----------|----------|-----|
| API | 8000 | 8001 | http://localhost:8001 |
| Prometheus | 9090 | 9091 | http://localhost:9091 |
| Grafana | 3000 | 3002 | http://localhost:3002 |
| Alertmanager | 9093 | 9093 | http://localhost:9093 |
| Metabase | 3000 | 3003 | http://localhost:3003 |

> **Nota**: Portas externas configuradas para não conflitar com Task 3.1

---

## 4. QUICK START

### Subir a Stack

```bash
# Build e start
docker compose up -d --build

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f
```

### Verificar Saúde

```bash
# API
curl http://localhost:8001/health

# Prometheus
curl http://localhost:9091/-/healthy

# Grafana
curl http://localhost:3002/api/health
```

### Parar a Stack

```bash
# Parar containers (mantém dados)
docker compose stop

# Remover containers (mantém volumes)
docker compose down

# Remover tudo (incluindo volumes)
docker compose down -v
```

---

## 5. CONFIGURAÇÃO

### Estrutura de Arquivos

```
infrastructure/
├── docker-compose.yml       # Main compose file
├── Dockerfile               # API image
├── prometheus/
│   ├── prometheus.yml       # Prometheus config
│   └── alerts.yml           # Alert rules
├── alertmanager/
│   └── alertmanager.yml     # Alertmanager config
└── grafana/
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml
        └── datasources/
            └── datasources.yml
```

### Variáveis de Ambiente

```bash
# .env (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

### Volumes

| Volume | Path | Purpose |
|--------|------|---------|
| grafana-data | /var/lib/grafana | Grafana data |
| prometheus-data | /prometheus | Metrics storage |
| metabase-data | /metabase-data | Metabase config |

---

## 6. COMANDOS ÚTEIS

### Logs

```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f guardian-api

# Últimas 100 linhas
docker compose logs --tail 100 guardian-api
```

### Restart

```bash
# Restart um serviço
docker compose restart guardian-api

# Restart todos
docker compose restart

# Rebuild e restart
docker compose up -d --build guardian-api
```

### Shell

```bash
# Entrar na API
docker exec -it guardian-api /bin/sh

# Entrar no Prometheus
docker exec -it guardian-prometheus /bin/sh
```

### Metrics

```bash
# Ver métricas da API
curl http://localhost:8001/metrics

# Query no Prometheus
curl 'http://localhost:9091/api/v1/query?query=transaction_guardian_total'
```

### Alertas

```bash
# Ver alertas ativos
curl http://localhost:9091/api/v1/alerts

# Ver alertas no Alertmanager
curl http://localhost:9093/api/v2/alerts
```

---

## 7. TROUBLESHOOTING

### Container não sobe

```bash
# Ver logs detalhados
docker compose logs guardian-api

# Verificar se porta está em uso
lsof -i :8001

# Rebuild forçado
docker compose build --no-cache guardian-api
```

### Prometheus não coleta métricas

```bash
# Verificar targets
curl http://localhost:9091/api/v1/targets

# Verificar config
docker exec guardian-prometheus cat /etc/prometheus/prometheus.yml

# Testar conectividade
docker exec guardian-prometheus wget -qO- http://guardian-api:8000/metrics
```

### Grafana sem dados

```bash
# Verificar datasource
curl -u admin:admin http://localhost:3002/api/datasources

# Verificar se Prometheus está acessível
curl http://localhost:9091/api/v1/query?query=up
```

### Alertmanager não envia alertas

```bash
# Verificar config
docker exec guardian-alertmanager cat /etc/alertmanager/alertmanager.yml

# Ver alertas pendentes
curl http://localhost:9093/api/v2/alerts

# Ver status
curl http://localhost:9093/api/v2/status
```

### Reset Completo

```bash
# Remover tudo e recomeçar
docker compose down -v
docker compose up -d --build
```

---

## 📋 CHECKLIST DE DEPLOY

- [ ] Variáveis de ambiente configuradas
- [ ] Portas disponíveis (8001, 9091, 3002, 9093, 3003)
- [ ] Docker e Docker Compose instalados
- [ ] Arquivos de dados em `../data/`
- [ ] Stack subiu sem erros
- [ ] API respondendo em /health
- [ ] Prometheus coletando métricas
- [ ] Grafana mostrando dashboards
- [ ] Alertmanager configurado

---

*Infrastructure Version: 1.0*  
*Last Updated: 2025-01-19*
