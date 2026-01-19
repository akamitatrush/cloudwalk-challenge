# 📘 RUNBOOK - TRANSACTION GUARDIAN

## Guia de Resposta a Incidentes

---

## 📑 ÍNDICE

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Alertas e Respostas](#2-alertas-e-respostas)
3. [Procedimentos de Diagnóstico](#3-procedimentos-de-diagnóstico)
4. [Ações de Mitigação](#4-ações-de-mitigação)
5. [Escalação](#5-escalação)
6. [Contatos](#6-contatos)

---

## 1. VISÃO GERAL DO SISTEMA

### 1.1 Arquitetura

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   API       │───▶│ Prometheus  │───▶│  Grafana    │
│  (8001)     │    │   (9091)    │    │   (3002)    │
└─────────────┘    └──────┬──────┘    └─────────────┘
                         │
                   ┌─────▼─────┐
                   │Alertmanager│
                   │   (9093)   │
                   └───────────┘
```

### 1.2 URLs de Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API Swagger | http://localhost:8001/docs | - |
| Grafana | http://localhost:3002 | admin/admin |
| Prometheus | http://localhost:9091 | - |
| Alertmanager | http://localhost:9093 | - |

### 1.3 Métricas Principais

| Métrica | Descrição | Threshold |
|---------|-----------|-----------|
| `transaction_guardian_total` | Total de transações | - |
| `transaction_guardian_anomalies` | Anomalias detectadas | < 10% |
| `transaction_guardian_current_count` | Volume atual | > 50 |
| `transaction_guardian_approval_rate` | Taxa de aprovação | > 90% |

---

## 2. ALERTAS E RESPOSTAS

### 🚨 ALERT: ZeroTransactions

**Severidade:** CRITICAL (P1)  
**Condição:** `count == 0` por 1 minuto  
**Impacto:** Possível outage total

#### Diagnóstico

```bash
# 1. Verificar se API está respondendo
curl http://localhost:8001/health

# 2. Verificar métricas
curl http://localhost:8001/stats | jq

# 3. Verificar logs
docker logs guardian-api --tail 50
```

#### Ações Imediatas

1. ✅ Verificar status da API (`/health`)
2. ✅ Verificar upstream (payment gateway)
3. ✅ Verificar rede/conectividade
4. ✅ Verificar logs de erro
5. ⚠️ Se necessário, escalar para P1

#### Comando de Verificação Rápida

```bash
# Verificação completa
curl -s http://localhost:8001/health && \
curl -s http://localhost:8001/stats | jq '.metrics'
```

---

### ⚠️ ALERT: LowVolume

**Severidade:** WARNING (P2)  
**Condição:** `count < 50` por 2 minutos  
**Impacto:** Degradação do serviço

#### Diagnóstico

```bash
# Ver histórico de volume
curl "http://localhost:9091/api/v1/query?query=transaction_guardian_current_count[5m]"

# Ver tendência
curl "http://localhost:9091/api/v1/query?query=rate(transaction_guardian_total[5m])"
```

#### Ações Imediatas

1. ✅ Verificar se é horário de baixo movimento
2. ✅ Comparar com histórico (mesmo dia/hora semana passada)
3. ✅ Verificar status dos gateways upstream
4. ⚠️ Se persistir por 5+ min, escalar para CRITICAL

---

### ⚠️ ALERT: HighAnomalyRate

**Severidade:** WARNING (P2)  
**Condição:** `anomalias / total > 10%`  
**Impacto:** Qualidade das transações

#### Diagnóstico

```bash
# Ver anomalias recentes
curl "http://localhost:8001/anomalies?limit=20" | jq

# Ver distribuição por tipo
curl http://localhost:8001/stats | jq '.metrics.status_counts'
```

#### Ações Imediatas

1. ✅ Identificar tipo predominante de anomalia
2. ✅ Verificar se é spike ou problema contínuo
3. ✅ Analisar padrão (horário, tipo de transação)
4. ⚠️ Investigar causa raiz

---

### 🚨 ALERT: LowApprovalRate

**Severidade:** CRITICAL (P1)  
**Condição:** `approval_rate < 90%` por 2 minutos  
**Impacto:** Perda de receita

#### Diagnóstico

```bash
# Ver taxa de aprovação atual
curl http://localhost:8001/stats | jq '.metrics.approval_rate'

# Ver distribuição de status
curl http://localhost:8001/stats | jq '.metrics.status_counts'
```

#### Ações Imediatas

1. ✅ Verificar qual status está aumentando (failed/denied/reversed)
2. ✅ Verificar auth_codes mais frequentes
3. ✅ Contatar equipe de payments
4. ⚠️ Escalar se necessário

---

### ⚠️ ALERT: VolumeSpike

**Severidade:** WARNING (P2)  
**Condição:** `count > 200% da média`  
**Impacto:** Possível sobrecarga ou ataque

#### Diagnóstico

```bash
# Ver pico vs média
curl http://localhost:8001/stats | jq '{current: .metrics.current_count, avg: .metrics.avg_count}'

# Verificar se é legítimo (promoção, etc)
curl "http://localhost:8001/anomalies?limit=10" | jq
```

#### Ações Imediatas

1. ✅ Verificar se há campanha/promoção ativa
2. ✅ Verificar se é tráfego legítimo
3. ✅ Monitorar recursos (CPU, memória)
4. ⚠️ Se suspeito, investigar possível ataque

---

## 3. PROCEDIMENTOS DE DIAGNÓSTICO

### 3.1 Verificação de Saúde Geral

```bash
#!/bin/bash
# health_check.sh

echo "🔍 Transaction Guardian - Health Check"
echo "======================================="

# API
echo -n "API: "
curl -s http://localhost:8001/health | jq -r '.status'

# Prometheus
echo -n "Prometheus: "
curl -s http://localhost:9091/-/healthy && echo "OK" || echo "FAIL"

# Grafana
echo -n "Grafana: "
curl -s http://localhost:3002/api/health | jq -r '.database'

# Containers
echo ""
echo "Containers:"
docker ps --filter "name=guardian" --format "{{.Names}}: {{.Status}}"
```

### 3.2 Verificar Métricas

```bash
# Todas as métricas
curl http://localhost:8001/metrics

# Estatísticas formatadas
curl http://localhost:8001/stats | jq

# Query específica no Prometheus
curl "http://localhost:9091/api/v1/query?query=transaction_guardian_approval_rate"
```

### 3.3 Verificar Logs

```bash
# Logs da API
docker logs guardian-api --tail 100

# Logs com filtro de erro
docker logs guardian-api 2>&1 | grep -i error

# Logs do Prometheus
docker logs guardian-prometheus --tail 50

# Logs do Alertmanager
docker logs guardian-alertmanager --tail 50
```

### 3.4 Verificar Alertas Ativos

```bash
# No Prometheus
curl http://localhost:9091/api/v1/alerts | jq

# No Alertmanager
curl http://localhost:9093/api/v2/alerts | jq
```

---

## 4. AÇÕES DE MITIGAÇÃO

### 4.1 Reiniciar API

```bash
docker restart guardian-api

# Verificar se voltou
sleep 5
curl http://localhost:8001/health
```

### 4.2 Reiniciar Stack Completa

```bash
cd task-3.2/infrastructure
docker compose restart

# Verificar todos os serviços
docker ps --filter "name=guardian"
```

### 4.3 Rebuild da API

```bash
cd task-3.2/infrastructure
docker compose up -d --build guardian-api
```

### 4.4 Reset de Métricas

```bash
# Reset contadores (cuidado em produção!)
curl -X POST http://localhost:8001/reset
```

### 4.5 Forçar Reload do Prometheus

```bash
curl -X POST http://localhost:9091/-/reload
```

---

## 5. ESCALAÇÃO

### Matriz de Escalação

| Severidade | Tempo para Ack | Tempo para Escalar | Para Quem |
|------------|----------------|-------------------|-----------|
| P1 (CRITICAL) | 5 min | 15 min | Tech Lead + Manager |
| P2 (WARNING) | 15 min | 30 min | Tech Lead |
| P3 (INFO) | 30 min | 2 horas | Equipe |

### Quando Escalar

- ❌ Não conseguiu identificar a causa em 15 min
- ❌ Impacto em clientes confirmado
- ❌ Precisa de acesso/permissão adicional
- ❌ Problema em sistema externo (gateway, etc)

### Template de Escalação

```
🚨 ESCALAÇÃO - [SEVERIDADE]

Incidente: INC-YYYY-MMDD-XXX
Início: HH:MM
Duração: XX min

Impacto: [Descrição]
Causa: [Identificada/Investigando]
Ações tomadas: [Lista]
Preciso de: [O que precisa]

cc: @oncall @techleads
```

---

## 6. CONTATOS

### Equipe On-Call

| Função | Contato | Horário |
|--------|---------|---------|
| SRE On-Call | #sre-oncall | 24/7 |
| Payments Team | #payments | Business hours |
| Backend Team | #backend | Business hours |

### Canais Slack

| Canal | Propósito |
|-------|-----------|
| #incidents | Incidentes ativos |
| #incidents-critical | Apenas P1 |
| #monitoring-alerts | Alertas automáticos |
| #transaction-guardian | Discussões do sistema |

---

## 📋 CHECKLIST DE INCIDENTE

### Ao Receber Alerta

- [ ] Ler alerta e entender severidade
- [ ] Verificar dashboards no Grafana
- [ ] Executar diagnóstico básico
- [ ] Comunicar no canal apropriado

### Durante Investigação

- [ ] Documentar timeline
- [ ] Coletar evidências (logs, métricas)
- [ ] Identificar causa raiz
- [ ] Aplicar mitigação

### Pós-Resolução

- [ ] Confirmar métricas normalizadas
- [ ] Atualizar canal com resolução
- [ ] Criar ticket de follow-up
- [ ] Agendar post-mortem se P1/P2

---

*Runbook Version: 1.0*  
*Last Updated: 2025-01-19*  
*Owner: Monitoring Team*
