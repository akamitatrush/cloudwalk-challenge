# CloudWalk Challenge - Task 3.2: Transaction Guardian

## Contexto do Candidato

Este é o Task 3.2 de um desafio técnico para a vaga de **Monitoring Intelligence Analyst (Night Shift)** na CloudWalk. O candidato é Sérgio, 31 anos, com mais de 14 anos de experiência em TI, incluindo quase 7 anos trabalhando com sistemas de pagamento na TIVIT/Cielo.

---

## O Desafio Proposto

O enunciado pedia:
1. **Um endpoint** que recebe dados de transação e retorna recomendação de alerta
2. **Uma query** para organizar os dados
3. **Um gráfico** para ver dados em tempo real
4. **Um modelo** para determinar anomalias
5. **Um sistema** para reportar anomalias automaticamente

Métodos sugeridos: rule-based, score-based (ML), ou combinação dos dois.

---

## A Solução: Transaction Guardian

### Arquitetura
```
Transação → API FastAPI → Detector (ML+Rules+Stats) → Alertas (Slack/Console)
                ↓
           Prometheus → Grafana (Dashboard real-time)
```

### Componentes Principais

**1. API FastAPI (main.py)**
- 9 endpoints
- Swagger automático em /docs
- SSE para streaming real-time

**2. Detector Híbrido (anomaly_detector.py)**
- Machine Learning: Isolation Forest (sklearn)
- Rule-based: 5 regras de threshold
- Estatístico: Z-Score

**3. AlertManager (alert_manager.py)**
- Notificações Slack
- Rate limiting
- Console logging

**4. Dashboard Grafana**
- 7 painéis
- Refresh 5 segundos
- Thresholds coloridos

**5. Collection Postman**
- 16 requests prontas
- Organizadas por categoria
- Documentação embutida

---

## Métricas do Projeto

- **Linhas de código:** ~1.300
- **Arquivos Python:** 4
- **Endpoints API:** 9
- **Painéis Grafana:** 7
- **Requests Postman:** 16
- **Métodos detecção:** 3 (ML + Rules + Z-Score)

---

## Diferencial da Entrega

| Pedido | Entregue |
|--------|----------|
| 1 endpoint | 9 endpoints + SSE |
| 1 query | API completa com filtros |
| 1 gráfico | Dashboard 7 painéis |
| 1 modelo | 3 métodos combinados |
| 1 sistema alerta | Slack + Console + Rate Limiting |

---

## Conexão com a Vaga

A vaga pede:
- Grafana ✅
- Prometheus ✅
- SQL ✅ (queries estruturadas)
- Python ✅
- AI tools ✅ (Isolation Forest)
- Firefighter mindset ✅ (detecta e alerta incêndios)

---

## Frase que Resume

**"Bombeiros que usam código para apagar incêndios."** 🔥

O sistema não só detecta problemas, mas tem toda a infraestrutura pronta para quando o alarme disparar.

---

**Sérgio**
Candidato: Monitoring Intelligence Analyst (Night Shift)
CloudWalk Challenge - January 2025
