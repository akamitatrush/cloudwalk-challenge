# 📘 RUNBOOK - TRANSACTION GUARDIAN v2.2

> Guia de Resposta a Incidentes - Atualizado Fevereiro 2026

---

## 📑 ÍNDICE

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [URLs e Acessos](#2-urls-e-acessos)
3. [Alertas e Respostas](#3-alertas-e-respostas)
4. [Shugo - Predição de Incidentes](#4-shugo---predição-de-incidentes)
5. [Procedimentos de Diagnóstico](#5-procedimentos-de-diagnóstico)
6. [Ações de Mitigação](#6-ações-de-mitigação)
7. [Ruby CLI - Comandos Úteis](#7-ruby-cli---comandos-úteis)
8. [Telegram Bot](#8-telegram-bot)
9. [Escalação](#9-escalação)
10. [Contatos](#10-contatos)

---

## 1. VISÃO GERAL DO SISTEMA

### 1.1 Arquitetura Completa
```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN v2.2                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐    ┌─────────────┐    ┌─────────────┐           │
│   │  Ruby    │───▶│   FastAPI   │───▶│   Shugo     │           │
│   │  CLI     │    │    :8001    │    │  守護       │           │
│   └──────────┘    └──────┬──────┘    └─────────────┘           │
│                          │                                      │
│        ┌─────────────────┼─────────────────┐                   │
│        ▼                 ▼                 ▼                   │
│   ┌─────────┐     ┌─────────────┐   ┌─────────────┐           │
│   │  Redis  │     │ TimescaleDB │   │   MLflow    │           │
│   │  :6379  │     │    :5432    │   │   :5000     │           │
│   └─────────┘     └─────────────┘   └─────────────┘           │
│        │                 │                 │                   │
│        └─────────────────┼─────────────────┘                   │
│                          ▼                                      │
│   ┌──────────┐    ┌─────────────┐   ┌─────────────┐           │
│   │Prometheus│───▶│   Grafana   │   │  Telegram   │           │
│   │  :9091   │    │   :3002     │   │    Bot      │           │
│   └────┬─────┘    └─────────────┘   └─────────────┘           │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────┐                                             │
│   │ Alertmanager │                                             │
│   │    :9093     │                                             │
│   └──────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Componentes

| Componente | Função | Criticidade |
|------------|--------|-------------|
| **FastAPI** | API principal | 🔴 CRÍTICO |
| **Redis** | Cache + Rate Limit | 🟡 ALTO |
| **TimescaleDB** | Persistência | 🟡 ALTO |
| **Shugo** | Predição de anomalias | 🟢 MÉDIO |
| **Prometheus** | Métricas | 🟢 MÉDIO |
| **Grafana** | Dashboards | 🟢 MÉDIO |
| **Telegram Bot** | Alertas | 🟢 MÉDIO |
| **MLflow** | ML versioning | 🔵 BAIXO |

---

## 2. URLS E ACESSOS

### 2.1 Produção (GCP)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **API Docs** | http://34.39.251.57:8001/docs | - |
| **Shugo Dashboard** | http://34.39.251.57:8001/shugo/dashboard | - |
| **Grafana** | http://34.39.251.57:3002 | Sob demanda |
| **Prometheus** | http://34.39.251.57:9091 | - |
| **Alertmanager** | http://34.39.251.57:9093 | - |
| **MLflow** | http://34.39.251.57:5000 | - |
| **Redis Commander** | http://34.39.251.57:8081 | - |
| **pgAdmin** | http://34.39.251.57:5050 | Sob demanda |
| **Telegram Bot** | @omega_transaction_bot | Senha requerida |

### 2.2 Local (Desenvolvimento)

| Serviço | URL |
|---------|-----|
| API | http://localhost:8001 |
| Grafana | http://localhost:3002 |
| Prometheus | http://localhost:9091 |

### 2.3 Autenticação API
```bash
# Login JWT
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "<senha>"}'

# Usar API Key
curl http://localhost:8001/stats \
  -H "X-API-Key: <api-key>"
```

---

## 3. ALERTAS E RESPOSTAS

### 🚨 CRITICAL: ZeroTransactions

**Condição:** `count == 0` por 1 minuto  
**Impacto:** Possível outage total  
**Severidade:** P1

#### Diagnóstico Rápido
```bash
# 1. Health check
curl http://localhost:8001/health

# 2. Verificar stats
curl http://localhost:8001/stats | jq

# 3. Verificar Shugo (previa alerta?)
curl http://localhost:8001/shugo/status

# 4. Logs
docker logs guardian-api --tail 50
```

#### Ações

1. ✅ Verificar se API responde (`/health`)
2. ✅ Verificar se Shugo previu o problema
3. ✅ Verificar upstream (gateway de pagamento)
4. ✅ Verificar rede/conectividade
5. ⚠️ Se não resolver em 5min, escalar para P1

---

### 🚨 CRITICAL: LowApprovalRate

**Condição:** `approval_rate < 70%` por 2 minutos  
**Impacto:** Perda de receita  
**Severidade:** P1

#### Diagnóstico
```bash
# Taxa atual
curl http://localhost:8001/stats | jq '.status_distribution'

# Anomalias recentes
curl http://localhost:8001/anomalies?limit=10 | jq

# Ruby CLI
./bin/guardian anomalies --limit 10 --level CRITICAL
```

#### Ações

1. ✅ Identificar qual status está aumentando
2. ✅ Verificar se Shugo alertou antes
3. ✅ Contatar equipe de payments
4. ⚠️ Escalar se persistir

---

### ⚠️ WARNING: LowVolume

**Condição:** `count < 50` por 2 minutos  
**Impacto:** Degradação do serviço  
**Severidade:** P2

#### Diagnóstico
```bash
# Verificar se Shugo previu
curl http://localhost:8001/shugo/predict?minutes=30 | jq

# Ver padrões (é horário esperado de baixo volume?)
curl http://localhost:8001/shugo/patterns | jq
```

#### Ações

1. ✅ Verificar se é horário de baixo movimento (Shugo patterns)
2. ✅ Comparar com previsão do Shugo
3. ✅ Se inesperado, verificar upstream
4. ⚠️ Se persistir 5+ min, escalar para CRITICAL

---

### ⚠️ WARNING: HighAnomalyRate

**Condição:** `anomalies / total > 30%`  
**Impacto:** Qualidade das transações  
**Severidade:** P2

#### Diagnóstico
```bash
# Anomalias recentes
curl http://localhost:8001/anomalies?limit=20 | jq

# Ruby CLI
./bin/guardian anomalies --limit 20

# Health score do Shugo
curl http://localhost:8001/shugo/status | jq
```

---

### ⚠️ WARNING: ShugoHighAlertProbability

**Condição:** `alert_probability > 60%`  
**Impacto:** Anomalia iminente  
**Severidade:** P2

> 🔮 **NOVO**: Este alerta vem do Shugo e indica que uma anomalia é **provável** nos próximos minutos.

#### Diagnóstico
```bash
# Ver predição
curl http://localhost:8001/shugo/predict?minutes=30 | jq

# Ver forecast completo
curl http://localhost:8001/shugo/forecast?hours=2 | jq

# Ruby CLI
./bin/guardian shugo predict 30
```

#### Ações

1. ✅ Verificar Dashboard Shugo: http://34.39.251.57:8001/shugo/dashboard
2. ✅ Preparar equipe para possível incidente
3. ✅ Monitorar próximos 30 minutos
4. ⚠️ Se alerta se concretizar, seguir procedimento correspondente

---

## 4. SHUGO - PREDIÇÃO DE INCIDENTES

### 4.1 O que é o Shugo?

**Shugo (守護)** = Guardião em japonês

O Shugo é um engine de predição que **antecipa anomalias** antes que aconteçam, analisando:
- Padrões por hora do dia
- Padrões por dia da semana
- Tendências recentes

### 4.2 Dashboard

**URL:** http://34.39.251.57:8001/shugo/dashboard

O dashboard mostra:
- 🎯 **Health Score**: Saúde do sistema (0-100)
- 🔮 **Predição**: Volume esperado em 30min
- 📈 **Forecast**: Gráfico de 6 horas
- 🔍 **Padrões**: Comportamentos detectados

### 4.3 Comandos Shugo
```bash
# Status
curl http://localhost:8001/shugo/status

# Predição 30 minutos
curl http://localhost:8001/shugo/predict?minutes=30

# Forecast 6 horas
curl http://localhost:8001/shugo/forecast?hours=6

# Padrões detectados
curl http://localhost:8001/shugo/patterns

# Treinar modelo
curl -X POST http://localhost:8001/shugo/train
```

### 4.4 Interpretando Alertas Shugo

| Alert Probability | Significado | Ação |
|-------------------|-------------|------|
| 0-30% | ✅ Normal | Monitoramento padrão |
| 31-60% | 🟡 Atenção | Aumentar vigilância |
| 61-100% | 🔴 Alto risco | Preparar para incidente |

---

## 5. PROCEDIMENTOS DE DIAGNÓSTICO

### 5.1 Health Check Completo
```bash
#!/bin/bash
echo "🔍 Transaction Guardian - Health Check"
echo "======================================="

# API
echo -n "API: "
curl -s http://localhost:8001/health | jq -r '.status'

# Shugo
echo -n "Shugo: "
curl -s http://localhost:8001/shugo/status | jq -r '.status'

# Cache
echo -n "Redis: "
curl -s http://localhost:8001/cache/stats | jq -r '.connected'

# Telegram
echo -n "Telegram: "
curl -s http://localhost:8001/telegram/status | jq -r '.status'

# Containers
echo ""
echo "Containers:"
docker ps --filter "name=guardian" --format "{{.Names}}: {{.Status}}"
```

### 5.2 Verificar Métricas
```bash
# Stats completos
curl http://localhost:8001/stats | jq

# Métricas Prometheus
curl http://localhost:8001/metrics

# Cache stats
curl http://localhost:8001/cache/stats | jq
```

### 5.3 Verificar Logs
```bash
# Logs da API
docker logs guardian-api --tail 100

# Filtrar erros
docker logs guardian-api 2>&1 | grep -i error

# Logs em tempo real
docker logs -f guardian-api
```

---

## 6. AÇÕES DE MITIGAÇÃO

### 6.1 Reiniciar API
```bash
docker restart guardian-api
sleep 5
curl http://localhost:8001/health
```

### 6.2 Reiniciar Stack Completa
```bash
cd ~/cloudwalk-challenge/task-3.2/infrastructure
docker compose restart
docker ps --filter "name=guardian"
```

### 6.3 Rebuild da API
```bash
cd ~/cloudwalk-challenge/task-3.2/infrastructure
docker compose up -d --build guardian-api
```

### 6.4 Limpar Cache Redis
```bash
docker exec guardian-redis redis-cli FLUSHALL
```

### 6.5 Re-treinar Shugo
```bash
curl -X POST http://localhost:8001/shugo/train
```

---

## 7. RUBY CLI - COMANDOS ÚTEIS

### 7.1 Instalação
```bash
cd ~/cloudwalk-challenge/task-3.2/ruby-sdk
gem install httparty thor terminal-table colorize
```

### 7.2 Comandos
```bash
# Status geral
./bin/guardian status --url http://localhost:8001

# Enviar transação
./bin/guardian transaction approved 150

# Listar anomalias
./bin/guardian anomalies --limit 10 --level CRITICAL

# Shugo status
./bin/guardian shugo status

# Shugo predição
./bin/guardian shugo predict 30

# Shugo forecast
./bin/guardian shugo forecast 6

# Shugo padrões
./bin/guardian shugo patterns

# Treinar Shugo
./bin/guardian shugo train
```

---

## 8. TELEGRAM BOT

### 8.1 Configuração

**Bot:** @omega_transaction_bot

### 8.2 Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start <senha>` | Autenticar |
| `/status` | Status do sistema |
| `/stats` | Estatísticas |
| `/anomalies` | Últimas anomalias |
| `/health` | Health check |
| `/subscribe` | Receber alertas |
| `/unsubscribe` | Parar alertas |

### 8.3 Gerenciamento
```bash
# Status do bot
curl http://localhost:8001/telegram/status

# Iniciar bot
curl -X POST http://localhost:8001/telegram/start

# Parar bot
curl -X POST http://localhost:8001/telegram/stop

# Enviar alerta manual
curl -X POST http://localhost:8001/telegram/send-alert \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste de alerta"}'
```

---

## 9. ESCALAÇÃO

### 9.1 Matriz de Escalação

| Severidade | Tempo para Ack | Tempo para Escalar | Para Quem |
|------------|----------------|-------------------|-----------|
| P1 (CRITICAL) | 5 min | 15 min | Tech Lead + Manager |
| P2 (WARNING) | 15 min | 30 min | Tech Lead |
| P3 (INFO) | 30 min | 2 horas | Equipe |

### 9.2 Quando Escalar

- ❌ Não identificou causa em 15 min
- ❌ Impacto em clientes confirmado
- ❌ Shugo previu e não conseguiu prevenir
- ❌ Precisa de acesso adicional
- ❌ Problema em sistema externo

### 9.3 Template de Escalação
```
🚨 ESCALAÇÃO - [SEVERIDADE]

Incidente: INC-YYYY-MMDD-XXX
Início: HH:MM
Duração: XX min

Impacto: [Descrição]
Shugo alertou antes? [Sim/Não]
Causa: [Identificada/Investigando]
Ações tomadas: [Lista]
Preciso de: [O que precisa]

Dashboard: http://34.39.251.57:8001/shugo/dashboard
```

---

## 10. CONTATOS

### 10.1 Desenvolvedor

| Função | Contato |
|--------|---------|
| **Sérgio Henrique** | sergio@lognullsec.com |
| LinkedIn | linkedin.com/in/akasergiosilva |
| GitHub | github.com/akamitatrush |

### 10.2 Canais

| Canal | Propósito |
|-------|-----------|
| Telegram Bot | Alertas automáticos |
| GitHub Issues | Bugs e features |

---

## 📋 CHECKLIST DE INCIDENTE

### Ao Receber Alerta

- [ ] Ler alerta e entender severidade
- [ ] Verificar se Shugo previu antes
- [ ] Acessar Dashboard Shugo
- [ ] Verificar dashboards Grafana
- [ ] Executar diagnóstico básico

### Durante Investigação

- [ ] Documentar timeline
- [ ] Coletar evidências (logs, métricas)
- [ ] Usar Ruby CLI para diagnóstico
- [ ] Identificar causa raiz
- [ ] Aplicar mitigação

### Pós-Resolução

- [ ] Confirmar métricas normalizadas
- [ ] Verificar Health Score do Shugo
- [ ] Documentar resolução
- [ ] Criar ticket de follow-up
- [ ] Agendar post-mortem se P1/P2

---

**Runbook Version:** 2.2  
**Last Updated:** 02 Fevereiro 2026  
**Owner:** Sérgio Henrique  
**Sistema:** Transaction Guardian + Shugo 守護
