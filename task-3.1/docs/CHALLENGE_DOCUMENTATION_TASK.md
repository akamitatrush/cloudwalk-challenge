# 📋 CLOUDWALK CHALLENGE - TASK 3.1
## Documentação Completa do Desafio

**CloudWalk Challenge - Task 3.1**  
**Candidato:** Sérgio  
**Vaga:** Monitoring Intelligence Analyst (Night Shift)  
**Data:** Janeiro 2025

---

## 📑 ÍNDICE

1. [O Problema Original](#1-o-problema-original)
2. [Requisitos vs Implementação](#2-requisitos-vs-implementação)
3. [Análise Realizada](#3-análise-realizada)
4. [Metodologia](#4-metodologia)
5. [Queries SQL](#5-queries-sql)
6. [Visualizações](#6-visualizações)
7. [Anomalia Encontrada](#7-anomalia-encontrada)
8. [Infraestrutura Criada](#8-infraestrutura-criada)
9. [Funcionalidades Adicionais](#9-funcionalidades-adicionais)
10. [Estrutura do Projeto](#10-estrutura-do-projeto)
11. [Como Executar](#11-como-executar)
12. [Conclusão](#12-conclusão)

---

## 1. O PROBLEMA ORIGINAL

### 1.1 Enunciado Original (Inglês)

> **3.1 - Get your hands dirty**
>
> Using **this csv** and using **this csv** with hypothetical checkout data, imagine that you are trying to understand if there is any kind of anomaly behavior.
>
> 1. Analyze the data provided and present your conclusions.
> 2. In addition to the spreadsheet data, make a query in SQL and make a graphic of it and try to explain the anomaly behavior you found.
> 3. In this csv you have the number of sales of POS by hour comparing the same sales per hour from today, yesterday and the average of other days. So with this we can see the behavior from today and compare to other days.

### 1.2 Tradução para Português

> **3.1 - Mãos à obra**
>
> Usando **este CSV** e **este CSV** com dados hipotéticos de checkout, imagine que você está tentando entender se existe algum tipo de comportamento anômalo.
>
> 1. **Analise os dados** fornecidos e **apresente suas conclusões**.
> 2. Além dos dados da planilha, faça uma **query em SQL** e faça um **gráfico** dela e tente **explicar o comportamento anômalo** que você encontrou.
> 3. Neste CSV você tem o número de vendas de POS por hora comparando as mesmas vendas por hora de hoje, ontem e a média de outros dias. Assim podemos ver o comportamento de hoje e comparar com outros dias.

### 1.3 Entregáveis Solicitados

> - Você deve gerar um **documento explicando como o desafio foi executado** (pode ser PDF, slides ou texto) que a equipe usará para complementar a análise da sua execução, que deve ser incluído em um **repositório Github**.
> - Nossa equipe revisará todo o conteúdo da apresentação e do repositório, e se estiver dentro das expectativas, agendaremos uma entrevista onde faremos perguntas sobre o processo e uso de ferramentas no desafio.

---

## 2. REQUISITOS VS IMPLEMENTAÇÃO

| # | REQUISITO | STATUS | IMPLEMENTAÇÃO |
|---|-----------|--------|---------------|
| 1 | Analisar os dados fornecidos | ✅ | Análise estatística completa dos 2 CSVs |
| 2 | Apresentar conclusões | ✅ | ANALYSIS_REPORT.md + MASTER_DOCUMENTATION.md |
| 3 | Query em SQL | ✅ | 3 queries: Anomaly Detection, Peak Hours, Z-Score |
| 4 | Gráfico | ✅ | 2 visualizações: Multi-panel + Timeline |
| 5 | Explicar anomalia encontrada | ✅ | Outage de 3 horas (15h-17h) identificado |
| 6 | Documento explicativo | ✅ | 6 arquivos de documentação |
| 7 | Repositório Github | ✅ | Estrutura pronta para commit |

### ✅ TODOS OS REQUISITOS ATENDIDOS!

---

## 3. ANÁLISE REALIZADA

### 3.1 Datasets Analisados

| Arquivo | Descrição |
|---------|-----------|
| `checkout_1.csv` | Dados de checkout - dia normal |
| `checkout_2.csv` | Dados de checkout - dia com anomalia |

### 3.2 Estrutura dos Dados

| Coluna | Descrição |
|--------|-----------|
| `time` | Hora do dia (00h-23h) |
| `today` | Número de vendas no dia atual |
| `yesterday` | Vendas do dia anterior |
| `same_day_last_week` | Vendas do mesmo dia semana passada |
| `avg_last_week` | Média de vendas da última semana |
| `avg_last_month` | Média de vendas do último mês |

### 3.3 Resultados Comparativos

| Métrica | checkout_1 | checkout_2 | Análise |
|---------|------------|------------|---------|
| Total Vendas Hoje | 526 | 427 | -99 (-19%) |
| Total Vendas Ontem | 523 | 526 | Similar |
| Anomalias Críticas | 0 | 3 | ⚠️ |
| Status | ✅ Normal | 🚨 CRITICAL | - |

---

## 4. METODOLOGIA

### 4.1 Técnicas de Detecção Aplicadas

```
┌─────────────────────────────────────────────────────────────┐
│                  MÉTODOS DE ANÁLISE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. COMPARAÇÃO ESTATÍSTICA                                   │
│     → Hoje vs Ontem vs Média Semanal/Mensal                 │
│                                                              │
│  2. ANÁLISE Z-SCORE                                          │
│     → Medir desvios padrão do esperado                      │
│     → Threshold: |Z| > 2 = Anomalia                         │
│                                                              │
│  3. DETECÇÃO POR THRESHOLD                                   │
│     → Abaixo de 50% da média = ALERT                        │
│     → Acima de 150% da média = ALERT                        │
│     → Zero transações = CRITICAL                            │
│                                                              │
│  4. ANÁLISE DE PADRÃO TEMPORAL                               │
│     → Identificar padrões horários incomuns                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Ferramentas Utilizadas

| Ferramenta | Uso |
|------------|-----|
| Python 3 | Linguagem principal |
| Pandas | Manipulação de dados |
| pandasql | Queries SQL nos DataFrames |
| Matplotlib/Seaborn | Visualizações |
| Prometheus | Métricas (infraestrutura adicional) |
| Grafana | Dashboards (infraestrutura adicional) |

---

## 5. QUERIES SQL

### Query 1: Detecção de Anomalias

```sql
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    ROUND(((today - avg_last_week) / 
        NULLIF(avg_last_week, 0)) * 100, 2) as pct_deviation,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL - ZERO SALES'
        WHEN today < avg_last_week * 0.5 THEN 'ALERT - BELOW 50%'
        WHEN today > avg_last_week * 1.5 THEN 'ALERT - ABOVE 150%'
        ELSE 'NORMAL'
    END as status
FROM checkout_data
WHERE today = 0 
   OR today < avg_last_week * 0.5 
   OR today > avg_last_week * 1.5
ORDER BY pct_deviation;
```

**Resultado:**
| time | today | avg_last_week | pct_deviation | status |
|------|-------|---------------|---------------|--------|
| 15h | 0 | 22.4 | -100% | CRITICAL - ZERO SALES |
| 16h | 0 | 21.6 | -100% | CRITICAL - ZERO SALES |
| 17h | 0 | 17.7 | -100% | CRITICAL - ZERO SALES |

---

### Query 2: Análise de Horário de Pico

```sql
SELECT 
    time,
    today,
    yesterday,
    avg_last_week,
    CASE 
        WHEN today = 0 THEN 'OUTAGE'
        WHEN today > avg_last_week * 1.5 THEN 'SPIKE'
        WHEN today < avg_last_week * 0.5 THEN 'DROP'
        ELSE 'NORMAL'
    END as classification
FROM checkout_data
WHERE CAST(REPLACE(time, 'h', '') AS INT) BETWEEN 10 AND 18
ORDER BY CAST(REPLACE(time, 'h', '') AS INT);
```

---

### Query 3: Cálculo de Z-Score

```sql
SELECT 
    time,
    today,
    avg_last_week,
    ROUND((today - avg_last_week) / 
        NULLIF(STDDEV(today - avg_last_week) OVER (), 0), 2) as z_score,
    CASE 
        WHEN ABS((today - avg_last_week) / 
            NULLIF(STDDEV(today - avg_last_week) OVER (), 0)) > 2 
        THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as z_score_status
FROM checkout_data;
```

---

## 6. VISUALIZAÇÕES

### 6.1 Gráficos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `anomaly_analysis_chart.png` | Gráfico multi-painel com 4 visões |
| `anomaly_timeline.png` | Timeline focada no período de outage |

### 6.2 Multi-Panel Analysis Chart

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐           │
│  │    checkout_1       │  │    checkout_2       │           │
│  │    (Normal Day)     │  │  (Anomaly Day)      │           │
│  │  Today vs Yesterday │  │  OUTAGE VISIBLE     │           │
│  └─────────────────────┘  └─────────────────────┘           │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐           │
│  │  Deviation Analysis │  │      Heatmap        │           │
│  │   (Bar Chart)       │  │  (Side-by-Side)     │           │
│  └─────────────────────┘  └─────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Timeline Focus

```
14:00 ████████████████████ 19 tx (Normal)
15:00                      0 tx  🚨 OUTAGE START
16:00                      0 tx  🚨 OUTAGE
17:00                      0 tx  🚨 OUTAGE
18:00 █████████████        13 tx ⚠️ Recovery
19:00 ████████████████████ 32 tx ✅ Normal
```

---

## 7. ANOMALIA ENCONTRADA

### 7.1 Descrição do Incidente

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚨 ANOMALIA CRÍTICA DETECTADA                               ║
║                                                               ║
║   Dataset: checkout_2.csv                                     ║
║   Período Afetado: 15:00 - 17:59 (3 horas)                   ║
║   Problema: ZERO TRANSAÇÕES durante horário de pico          ║
║   Transações Perdidas: ~62 (estimado pela média semanal)     ║
║   Causa Provável: Outage do Sistema (Gateway / API)          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 7.2 Evidências

| Hora | Hoje | Ontem | Média Semana | Desvio | Status |
|------|------|-------|--------------|--------|--------|
| **15h** | **0** | 51 | 22.4 | -100% | 🔴 CRITICAL |
| **16h** | **0** | 41 | 21.6 | -100% | 🔴 CRITICAL |
| **17h** | **0** | 45 | 17.7 | -100% | 🔴 CRITICAL |

### 7.3 Análise Z-Score

| Hora | Z-Score | Interpretação |
|------|---------|---------------|
| 15h | -2.8 | Significativamente abaixo do normal |
| 16h | -2.7 | Significativamente abaixo do normal |
| 17h | -2.4 | Significativamente abaixo do normal |

**Threshold:** |Z-Score| > 2 = Anomalia

### 7.4 Anomalia Secundária (Morning Spike)

| Hora | Hoje | Média Semana | Desvio |
|------|------|--------------|--------|
| 08h | 25 | 3.7 | +574% 📈 |
| 09h | 36 | 10.1 | +255% 📈 |

**Hipótese:** Processamento de backlog do dia anterior.

### 7.5 Hipóteses de Causa Raiz

| Hipótese | Probabilidade | Evidência |
|----------|---------------|-----------|
| Payment Gateway Outage | 70% | Transações caíram para ZERO exato |
| Server/API Failure | 20% | Spike matinal sugere backlog |
| Database Issue | 10% | Recuperação gradual |

**Descartados:**
- Baixa demanda (dados históricos mostram pico)
- Janela de manutenção (não ocorreria em horário de pico)
- Erro de coleta de dados (outras horas registradas normalmente)

---

## 8. INFRAESTRUTURA CRIADA

### 8.1 Stack Completa (Adicional)

Além da análise pedida, foi criada uma **infraestrutura de monitoramento completa**:

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITETURA                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐          │
│  │  CSV Data │────▶│ Exporter  │────▶│Prometheus │          │
│  └───────────┘     └───────────┘     └─────┬─────┘          │
│                                            │                │
│                    ┌───────────────────────┼───────┐        │
│                    │                       │       │        │
│                    ▼                       ▼       ▼        │
│             ┌───────────┐          ┌───────────┐ ┌─────┐    │
│             │  Grafana  │          │Alertmanager│ │Slack│    │
│             └───────────┘          └───────────┘ └─────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Componentes Docker

| Container | Porta | Função |
|-----------|-------|--------|
| checkout-exporter | 8000 | Expõe métricas do CSV |
| prometheus | 9090 | Coleta métricas |
| grafana | 3001 | Dashboards |
| alertmanager | 9093 | Gestão de alertas |

### 8.3 Alertas Configurados

| Severidade | Condição | Ação |
|------------|----------|------|
| P1 CRITICAL | Zero transações em horário comercial | PagerDuty + Slack |
| P2 HIGH | Queda > 50% do esperado | Slack |
| P3 MEDIUM | Spike > 200% do esperado | Slack |

---

## 9. FUNCIONALIDADES ADICIONAIS

Além dos requisitos mínimos, foram implementados:

| # | Adicional | Descrição |
|---|-----------|-----------|
| 1 | **Stack Prometheus/Grafana** | Infraestrutura completa de monitoramento |
| 2 | **Docker Compose** | Deploy com um comando |
| 3 | **INCIDENT_REPORT.md** | Relatório formal de incidente |
| 4 | **RUNBOOK.md** | Guia de resposta a incidentes |
| 5 | **SLACK_TEMPLATES.md** | Templates de comunicação |
| 6 | **PROMQL_CHEATSHEET.md** | Referência de queries |
| 7 | **Dashboard Grafana** | JSON pronto para importar |
| 8 | **Dashboard HTML** | Versão interativa standalone |
| 9 | **Exporter Python** | CSV para métricas Prometheus |
| 10 | **Sistema de Alertas** | Alertas automáticos configurados |

---

## 10. ESTRUTURA DO PROJETO

```
task-3.1/
├── docs/                              # 📚 DOCUMENTAÇÃO
│   ├── CHALLENGE_DOCUMENTATION.md        # Este documento
│   ├── MASTER_DOCUMENTATION.md           # Documentação técnica completa
│   ├── ANALYSIS_REPORT.md                # Relatório de análise
│   ├── INCIDENT_REPORT.md                # Relatório de incidente
│   ├── RUNBOOK.md                        # Guia de resposta
│   ├── SLACK_TEMPLATES.md                # Templates comunicação
│   └── PROMQL_CHEATSHEET.md              # Referência PromQL
│
├── code/                              # 🐍 CÓDIGO
│   ├── task_3_1_analysis.py              # Script principal de análise
│   ├── alert_system.py                   # Sistema de alertas
│   ├── checkout_exporter.py              # Exporter Prometheus
│   └── sql_queries.sql                   # Queries SQL
│
├── dashboards/                        # 📊 DASHBOARDS
│   ├── checkout_monitoring.json          # Dashboard Grafana
│   └── DASHBOARD.html                    # Dashboard interativo
│
├── data/                              # 📄 DADOS
│   ├── checkout_1.csv                    # Dataset 1 (normal)
│   └── checkout_2.csv                    # Dataset 2 (anomalia)
│
├── assets/                            # 🖼️ VISUALIZAÇÕES
│   ├── anomaly_analysis_chart.png        # Gráfico multi-painel
│   └── anomaly_timeline.png              # Timeline do outage
│
├── infrastructure/                    # 🐳 DOCKER
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   ├── alertmanager.yml
│   └── checkout_alerts.yml
│
└── README.md
```

---

## 11. COMO EXECUTAR

### 11.1 Análise Básica (Python)

```bash
# Instalar dependências
pip install pandas numpy matplotlib seaborn pandasql

# Rodar análise
cd task-3.1/code
python task_3_1_analysis.py
```

### 11.2 Stack Completa (Docker)

```bash
# Navegar até infraestrutura
cd task-3.1/infrastructure

# Subir todos os containers
docker compose up -d

# Acessar:
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# Exporter: http://localhost:8000/metrics
```

### 11.3 Verificar Dados

```bash
# Ver métricas expostas
curl http://localhost:8000/metrics

# Testar query no Prometheus
curl 'http://localhost:9090/api/v1/query?query=checkout_transactions_hourly'
```

---

## 12. CONCLUSÃO

### 12.1 Resumo da Entrega

O desafio **Task 3.1** foi completado com **todos os requisitos atendidos**:

| Requisito | Status |
|-----------|--------|
| ✅ Analisar dados | Análise completa dos 2 CSVs |
| ✅ Apresentar conclusões | Documentação detalhada |
| ✅ Query SQL | 3 queries implementadas |
| ✅ Gráfico | 2 visualizações criadas |
| ✅ Explicar anomalia | Outage de 3h identificado e documentado |
| ✅ Documento explicativo | 7 arquivos de documentação |

### 12.2 Anomalia Principal Encontrada

```
🚨 OUTAGE CRÍTICO
   Período: 15:00 - 17:59 (3 horas)
   Impacto: ~62 transações perdidas
   Causa: Provável falha de Payment Gateway
```

### 12.3 Diferenciais da Entrega

1. **Infraestrutura Production-Ready** - Stack Prometheus + Grafana completa
2. **Documentação Profissional** - 7 documentos cobrindo todos os aspectos
3. **Perspectiva Night Shift** - Análise estruturada como resposta real a incidente
4. **Templates Operacionais** - Runbook e templates de comunicação

### 12.4 Conexão com a Vaga

| Requisito da Vaga | Demonstrado |
|-------------------|-------------|
| Grafana | ✅ Dashboard completo |
| Prometheus | ✅ Stack configurada |
| SQL | ✅ 3 queries de análise |
| Python | ✅ Scripts de análise |
| Data Analysis | ✅ Múltiplos métodos estatísticos |
| Firefighter mindset | ✅ Incident Report + Runbook |

---

### 12.5 Frase Final

> **"Where there is data smoke, there is business fire."** — Thomas Redman
>
> Esta análise demonstra não apenas a capacidade de detectar anomalias, mas todo o mindset de um Monitoring Intelligence Analyst: detectar, investigar, documentar e comunicar.

---

**Sérgio**  
Candidato: Monitoring Intelligence Analyst (Night Shift)  
CloudWalk Challenge - Janeiro 2025

*"Bombeiros que usam código para apagar incêndios."* 🔥
