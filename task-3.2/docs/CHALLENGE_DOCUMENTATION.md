# 📋 TRANSACTION GUARDIAN - DOCUMENTAÇÃO DO DESAFIO

**CloudWalk Challenge - Task 3.2**  
**Candidato:** Sérgio  
**Vaga:** Monitoring Intelligence Analyst (Night Shift)  
**Data:** Janeiro 2025

---

## 📑 ÍNDICE

1. [O Problema Original](#1-o-problema-original)
2. [Requisitos vs Implementação](#2-requisitos-vs-implementação)
3. [Arquitetura da Solução](#3-arquitetura-da-solução)
4. [Fluxo de Processamento](#4-fluxo-de-processamento)
5. [Métodos de Detecção](#5-métodos-de-detecção)
6. [Componentes do Sistema](#6-componentes-do-sistema)
7. [Dashboards Grafana](#7-dashboards-grafana)
8. [Cenários de Uso](#8-cenários-de-uso)
9. [Funcionalidades Adicionais](#9-funcionalidades-adicionais)
10. [Como Executar](#10-como-executar)
11. [Conclusão](#11-conclusão)

---

## 1. O PROBLEMA ORIGINAL

### 1.1 Enunciado (Inglês)

> **3.2 - Solve the problem**
>
> Alert incident in transactions: Implement the concept of a simple monitoring with real time alert with notifications to teams.
>
> The monitoring works by receiving information about a transaction and inferring whether it is a failed or denied, or reversed or approved transaction.

### 1.2 Tradução (Português)

> **3.2 - Resolver o problema**
>
> **Alerta de incidentes em transações:** Implementar o conceito de um monitoramento simples com **alertas em tempo real** e **notificações para as equipes**.
>
> O monitoramento funciona **recebendo informações sobre uma transação** e **inferindo** se ela é uma transação **falha (failed)**, **negada (denied)**, **revertida (reversed)** ou **aprovada (approved)**.

### 1.3 Requisitos Mínimos

> 1. **Um endpoint** que recebe dados de transação e retorna recomendação para alertar anomalias
> 2. **Uma query** para organizar os dados
> 3. **Um gráfico** para ver os dados em tempo real
> 4. **Um modelo** para determinar anomalias
> 5. **Um sistema** para reportar anomalias automaticamente

### 1.4 Métodos Sugeridos

> - **rule-based** - regras pré-definidas para gerar alertas
> - **score-based** - modelo/método (pode usar ML) para determinar score de anomalia
> - **combinação dos dois**

### 1.5 Alertas Obrigatórios

> - Alertar se **FAILED** estiver acima do normal
> - Alertar se **REVERSED** estiver acima do normal
> - Alertar se **DENIED** estiver acima do normal

---

## 2. REQUISITOS VS IMPLEMENTAÇÃO

| # | REQUISITO | STATUS | IMPLEMENTAÇÃO |
|---|-----------|--------|---------------|
| 1 | Endpoint que recebe transações | ✅ | `POST /transaction` |
| 2 | Retorna recomendação de alerta | ✅ | `is_anomaly`, `alert_level`, `recommendation` |
| 3 | Query para organizar dados | ✅ | `GET /anomalies?level=CRITICAL&limit=10` |
| 4 | Gráfico em tempo real | ✅ | 5 Dashboards Grafana, 31 painéis |
| 5 | Modelo para anomalias | ✅ | Isolation Forest (ML) + Z-Score |
| 6 | Sistema de notificação | ✅ | AlertManager + Slack + Console |
| 7 | Alertar FAILED | ✅ | Regra `STATUS_ERROR` |
| 8 | Alertar REVERSED | ✅ | Regra `STATUS_ERROR` |
| 9 | Alertar DENIED | ✅ | Regra `STATUS_ERROR` |
| 10 | Rule-based | ✅ | 5 regras de threshold |
| 11 | Score-based (ML) | ✅ | Isolation Forest |
| 12 | Combinação | ✅ | 60% ML + 40% Z-Score |

**✅ TODOS OS REQUISITOS ATENDIDOS!**

---

## 3. ARQUITETURA DA SOLUÇÃO

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ENTRADA              PROCESSAMENTO           SAÍDA             │
│                                                                  │
│  ┌─────────┐         ┌─────────────┐        ┌─────────────┐     │
│  │ Postman │         │   FastAPI   │        │   Grafana   │     │
│  │  curl   │────────▶│   (8001)    │───────▶│   (3002)    │     │
│  │ Swagger │         │             │        │             │     │
│  └─────────┘         │  Detector:  │        │ 5 Dashboards│     │
│                      │  • ML       │        │ 31 Painéis  │     │
│                      │  • Rules    │        └─────────────┘     │
│                      │  • Z-Score  │                            │
│                      └──────┬──────┘        ┌─────────────┐     │
│                             │               │  Prometheus │     │
│                             └──────────────▶│   (9091)    │     │
│                                             └─────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Stack de Containers

| Container | Porta | Função |
|-----------|-------|--------|
| guardian-api | 8001 | API FastAPI |
| guardian-prometheus | 9091 | Métricas |
| guardian-grafana | 3002 | Dashboards |
| guardian-alertmanager | 9093 | Alertas |
| guardian-metabase | 3003 | SQL Analytics |

---

## 4. FLUXO DE PROCESSAMENTO

```
1. TRANSAÇÃO CHEGA
   POST /transaction
   {"status": "approved", "count": 115, "auth_code": "00"}
                    │
                    ▼
2. DETECTOR ANALISA
   ┌────────────────────────────────────────┐
   │  🤖 ML Score (Isolation Forest)        │
   │  📊 Z-Score (Estatística)              │
   │  📋 Regras de Threshold                │
   │  🧮 Score Combinado                    │
   └────────────────────────────────────────┘
                    │
                    ▼
3. DECISÃO
   Score > 0.85 ou 2+ violações → CRITICAL
   Score > 0.5 ou 1+ violação   → WARNING
   Caso contrário               → NORMAL
                    │
                    ▼
4. RESPOSTA + ALERTA
   {"is_anomaly": true, "alert_level": "CRITICAL", ...}
   + Notificação Slack/Console
   + Métricas Prometheus
   + Dashboard Grafana atualiza
```

---

## 5. MÉTODOS DE DETECÇÃO

### 5.1 Machine Learning (Isolation Forest)

- Algoritmo não-supervisionado
- 100 estimators, contamination=0.1
- Score 0-1 usando sigmoid

### 5.2 Regras de Threshold (Rule-based)

| Regra | Condição | Severidade |
|-------|----------|------------|
| LOW_VOLUME | count < 50 | CRITICAL |
| VOLUME_DROP | count < 50% média | CRITICAL |
| VOLUME_SPIKE | count > 200% média | WARNING |
| STATUS_ERROR | failed/denied/reversed | WARNING/CRITICAL |
| AUTH_ERROR | auth_code != "00" | WARNING |

### 5.3 Z-Score (Estatística)

- Threshold: |zscore| > 2.5 = Anomalia

### 5.4 Score Combinado

```python
combined_score = 0.6 * ml_score + 0.4 * min(abs(zscore) / 3, 1)
```

---

## 6. COMPONENTES DO SISTEMA

### API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/transaction` | POST | Analisa transação |
| `/transactions/batch` | POST | Processa múltiplas |
| `/anomalies` | GET | Lista anomalias |
| `/metrics` | GET | Métricas Prometheus |
| `/stats` | GET | Estatísticas |
| `/health` | GET | Status do sistema |
| `/stream` | GET | SSE real-time |

---

## 7. DASHBOARDS GRAFANA

| # | Dashboard | Painéis |
|---|-----------|---------|
| 1 | 🛡️ Transaction Guardian | 7 |
| 2 | 📈 SLA/SLO | 9 |
| 3 | 🚨 Alertas & Incidentes | 10 |
| 4 | 📊 Análise Histórica | 8 |
| 5 | 👔 Executive Summary | 11 |

**Total: 5 dashboards, 31 painéis**

---

## 8. CENÁRIOS DE USO

### Cenário 1: Transação Normal
```
Input:  {"status": "approved", "count": 115, "auth_code": "00"}
Output: {"is_anomaly": false, "alert_level": "NORMAL"}
```

### Cenário 2: Outage (Volume Baixo)
```
Input:  {"status": "approved", "count": 5, "auth_code": "00"}
Output: {"is_anomaly": true, "alert_level": "CRITICAL"}
Alerta: 🚨 Possível outage! Volume muito baixo.
```

### Cenário 3: Transação Falhou
```
Input:  {"status": "failed", "count": 100, "auth_code": "59"}
Output: {"is_anomaly": true, "alert_level": "CRITICAL"}
Alerta: 🚨 Alta taxa de falhas!
```

### Cenário 4: Spike de Volume
```
Input:  {"status": "approved", "count": 500, "auth_code": "00"}
Output: {"is_anomaly": true, "alert_level": "WARNING"}
Alerta: ⚠️ Spike de volume detectado
```

---

## 9. FUNCIONALIDADES ADICIONAIS

Além dos requisitos mínimos:

| # | Funcionalidade |
|---|----------------|
| 1 | 5 Dashboards Grafana (vs 1 pedido) |
| 2 | Collection Postman (16 requests) |
| 3 | Simulador Python (3 modos) |
| 4 | Docker Compose completo |
| 5 | Notebook Colab interativo |
| 6 | Guia Operacional completo |
| 7 | Rate Limiting de alertas |
| 8 | 8 Métricas Prometheus |
| 9 | SSE Endpoint (real-time) |
| 10 | Batch Processing |
| 11 | Swagger UI |
| 12 | Metabase + Queries SQL |

---

## 10. COMO EXECUTAR

### Subir a Stack

```bash
cd task-3.2/infrastructure
docker compose up -d --build
```

### URLs de Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API Swagger | http://localhost:8001/docs | - |
| Grafana | http://localhost:3002 | admin/admin |
| Prometheus | http://localhost:9091 | - |
| Alertmanager | http://localhost:9093 | - |
| Metabase | http://localhost:3003 | Criar conta |

### Testar

```bash
# Transação normal
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 115, "auth_code": "00"}'

# Simular outage
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 5, "auth_code": "00"}'
```

---

## 11. CONCLUSÃO

### Resumo da Entrega

O sistema **Transaction Guardian** atende **100% dos requisitos**:

✅ Endpoint que recebe transações e retorna alertas  
✅ Query para organizar dados  
✅ Gráficos em tempo real (5 dashboards)  
✅ Modelo de detecção (ML + Rules + Stats)  
✅ Sistema de notificação automática  
✅ Alertas para FAILED, DENIED e REVERSED  

### Conexão com a Vaga

| Requisito da Vaga | Demonstrado |
|-------------------|-------------|
| Grafana | ✅ 5 dashboards |
| Prometheus | ✅ 8 métricas |
| SQL | ✅ PromQL + Metabase |
| Python | ✅ ~1.500 linhas |
| AI/ML | ✅ Isolation Forest |
| Firefighter mindset | ✅ Alertas em tempo real |

---

> **"We want firefighters that use code to stop the fire."**
>
> O Transaction Guardian detecta incêndios (anomalias) antes que se espalhem! 🔥

---

**Sérgio**  
Candidato: Monitoring Intelligence Analyst (Night Shift)  
CloudWalk Challenge - Janeiro 2025
