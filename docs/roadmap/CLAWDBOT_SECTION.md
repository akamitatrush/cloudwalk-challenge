
---

## 10. Integração Clawdbot 🦞

### 10.1. Visão Geral

**Clawdbot** é um assistente AI open-source e self-hosted que se integra com plataformas de mensagens (WhatsApp, Telegram, Discord, Slack). Para um **Monitoring Intelligence Analyst no turno da noite**, isso significa:

- Receber alertas críticos direto no celular
- Consultar status do sistema via chat
- Executar runbooks sem abrir o laptop
- Briefings automáticos de início/fim de turno

**GitHub:** https://github.com/clawdbot/clawdbot

### 10.2. Arquitetura de Integração

```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN v2.0                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │   API    │───▶│  Kafka   │───▶│      Workers         │  │
│  │ FastAPI  │    │          │    │  (ML Detection)      │  │
│  └──────────┘    └──────────┘    └──────────┬───────────┘  │
│                                              │              │
│                                              ▼              │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │ Grafana  │◀───│Prometheus│◀───│   Alert Manager      │  │
│  └──────────┘    └──────────┘    └──────────┬───────────┘  │
│                                              │              │
│                                              ▼              │
│                                 ┌────────────────────────┐  │
│                                 │      CLAWDBOT 🦞       │  │
│                                 │                        │  │
│                                 │  ┌─────┐ ┌─────────┐  │  │
│                                 │  │Slack│ │WhatsApp │  │  │
│                                 │  └─────┘ └─────────┘  │  │
│                                 │  ┌────────┐ ┌──────┐  │  │
│                                 │  │Telegram│ │Discord│  │  │
│                                 │  └────────┘ └──────┘  │  │
│                                 └────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 10.3. Casos de Uso

#### 10.3.1. Canal de Alertas Pessoal
```
[Alertmanager] → [Webhook] → [Clawdbot] → [WhatsApp/Telegram]

Resultado no celular:
🚨 CRITICAL: Zero transactions detected
Sistema: Transaction Guardian
Hora: 15:32
Ação: Verificar API imediatamente
```

#### 10.3.2. Consulta de Status via Chat
```
Você (WhatsApp): "status do sistema"

Clawdbot: "✅ Transaction Guardian Status
├── API: healthy (uptime 99.97%)
├── Transações/min: 1,247
├── Taxa aprovação: 94.2%
├── Anomalias (1h): 0
├── Alertas ativos: 0
└── Último incidente: há 3 dias"
```

#### 10.3.3. Briefing Automático de Turno
```python
# Skill: shift_briefing.py
# Executa automaticamente às 00:00 (início do turno)

Clawdbot (00:00): "🌙 Briefing Turno Noturno

📊 Últimas 8 horas:
├── Total TX: 45,231
├── Aprovadas: 94.2%
├── Anomalias: 7 (5 resolvidas)
└── Incidentes: 0 P1, 1 P2

⚠️ Atenção:
├── Merchant XYZ com taxa de falha 12%
└── Alerta de volume baixo às 18h (resolvido)

📋 Pendências:
└── Nenhuma

Bom turno! 🦞"
```

#### 10.3.4. Execução de Runbooks
```
Você: "executar runbook restart-api"

Clawdbot: "🔄 Executando runbook: restart-api

[1/4] Verificando dependências... ✅
[2/4] Salvando estado atual... ✅
[3/4] Reiniciando API... ✅
[4/4] Health check... ✅

✅ Runbook concluído em 45s
API respondendo normalmente"
```

#### 10.3.5. Consulta de Métricas
```
Você: "anomalias últimas 2 horas"

Clawdbot: "🔍 Anomalias (últimas 2h):

14:32 - Volume baixo
├── Score ML: 0.87
├── Z-Score: -2.8
├── Status: Resolvido
└── Duração: 12min

15:45 - Spike detectado
├── Score ML: 0.78
├── Z-Score: 3.1
├── Status: Resolvido
└── Duração: 5min

Total: 2 anomalias, ambas resolvidas"
```

### 10.4. Skills Customizadas

```python
# skills/transaction_guardian/status.py
"""
Skill: Consulta de Status do Transaction Guardian
Trigger: "status", "como está o sistema", "health check"
"""

import httpx
from datetime import datetime

async def get_system_status() -> str:
    """Retorna status formatado do sistema"""
    
    # Consultar API
    async with httpx.AsyncClient() as client:
        health = await client.get("http://localhost:8001/health")
        stats = await client.get("http://localhost:8001/stats")
        
    health_data = health.json()
    stats_data = stats.json()
    
    # Formatar resposta
    status_emoji = "✅" if health_data["status"] == "healthy" else "🚨"
    
    return f"""
{status_emoji} **Transaction Guardian Status**

├── API: {health_data["status"]}
├── Uptime: {health_data["uptime"]}
├── Transações/min: {stats_data["transactions_per_minute"]:,}
├── Taxa aprovação: {stats_data["approval_rate"]:.1f}%
├── Anomalias (1h): {stats_data["anomalies_last_hour"]}
├── Alertas ativos: {stats_data["active_alerts"]}
└── Último check: {datetime.now().strftime("%H:%M:%S")}
"""


# skills/transaction_guardian/alerts.py
"""
Skill: Listar alertas ativos
Trigger: "alertas", "alerts", "problemas"
"""

async def get_active_alerts() -> str:
    """Lista alertas ativos do Alertmanager"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9093/api/v2/alerts")
    
    alerts = response.json()
    
    if not alerts:
        return "✅ Nenhum alerta ativo no momento!"
    
    result = f"🚨 **{len(alerts)} Alertas Ativos**\n\n"
    
    for alert in alerts:
        severity = alert["labels"].get("severity", "unknown")
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")
        
        result += f"""
{emoji} **{alert["labels"]["alertname"]}**
├── Severidade: {severity}
├── Início: {alert["startsAt"][:19]}
└── Descrição: {alert["annotations"].get("description", "N/A")}
"""
    
    return result


# skills/transaction_guardian/runbook.py
"""
Skill: Executar Runbooks
Trigger: "runbook <nome>", "executar <nome>"
"""

import subprocess
import asyncio

RUNBOOKS = {
    "restart-api": [
        ("Verificando dependências", "curl -s http://localhost:8001/health"),
        ("Reiniciando API", "docker restart guardian-api"),
        ("Aguardando startup", "sleep 10"),
        ("Health check", "curl -s http://localhost:8001/health"),
    ],
    "clear-cache": [
        ("Conectando ao Redis", "redis-cli ping"),
        ("Limpando cache", "redis-cli FLUSHDB"),
        ("Verificando", "redis-cli DBSIZE"),
    ],
    "scale-workers": [
        ("Status atual", "docker ps | grep worker"),
        ("Escalando para 5", "docker compose up -d --scale worker=5"),
        ("Verificando", "docker ps | grep worker"),
    ],
}

async def execute_runbook(runbook_name: str) -> str:
    """Executa runbook passo a passo"""
    
    if runbook_name not in RUNBOOKS:
        return f"❌ Runbook '{runbook_name}' não encontrado.\n\nDisponíveis: {', '.join(RUNBOOKS.keys())}"
    
    steps = RUNBOOKS[runbook_name]
    result = f"🔄 **Executando runbook: {runbook_name}**\n\n"
    
    for i, (description, command) in enumerate(steps, 1):
        result += f"[{i}/{len(steps)}] {description}... "
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode == 0:
                result += "✅\n"
            else:
                result += "❌\n"
                return result + f"\n⚠️ Runbook interrompido no passo {i}"
                
        except Exception as e:
            result += f"❌ ({e})\n"
            return result + f"\n⚠️ Runbook interrompido no passo {i}"
    
    result += f"\n✅ **Runbook concluído com sucesso!**"
    return result
```

### 10.5. Configuração do Alertmanager

```yaml
# alertmanager/alertmanager.yml
# Adicionar receiver para Clawdbot

receivers:
  - name: 'clawdbot-critical'
    webhook_configs:
      - url: 'http://localhost:18789/webhook/alertmanager'
        send_resolved: true
        http_config:
          bearer_token: '${CLAWDBOT_TOKEN}'

route:
  receiver: 'slack-monitoring'
  routes:
    # Alertas críticos vão para Clawdbot (celular pessoal)
    - match:
        severity: critical
      receiver: 'clawdbot-critical'
      continue: true
```

### 10.6. Comandos Disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `status` | Status geral do sistema | "status do sistema" |
| `alertas` | Lista alertas ativos | "mostra alertas" |
| `anomalias [período]` | Lista anomalias | "anomalias última hora" |
| `métricas [nome]` | Consulta métrica específica | "taxa de aprovação" |
| `runbook [nome]` | Executa runbook | "runbook restart-api" |
| `incidente [desc]` | Cria ticket de incidente | "incidente API lenta" |
| `briefing` | Gera briefing do turno | "briefing" |
| `ajuda` | Lista comandos | "ajuda" |

### 10.7. Benefícios para Night Shift

| Cenário | Sem Clawdbot | Com Clawdbot |
|---------|--------------|--------------|
| Alerta crítico 3AM | Email/Slack (pode não ver) | WhatsApp com som alto ✅ |
| Verificar sistema | Abrir laptop, VPN, Grafana | "status" no celular ✅ |
| Restart emergencial | SSH, comandos manuais | "runbook restart-api" ✅ |
| Handoff de turno | Documento manual | Briefing automático ✅ |
| Histórico de problemas | Pesquisar logs | "anomalias últimas 24h" ✅ |

### 10.8. Requisitos de Instalação

```bash
# Pré-requisitos
- Node.js >= 22
- Conta Anthropic (Claude API)
- WhatsApp Business ou Telegram Bot

# Instalação
npm install -g clawdbot@latest
clawdbot onboard --install-daemon

# Configurar canal (WhatsApp exemplo)
clawdbot channel add whatsapp

# Instalar skills do Transaction Guardian
clawdbot skill install ./skills/transaction_guardian
```

---

## 8. Roadmap de Implementação (Atualizado)

### Fase 1: Foundation (2-3 semanas)
- [ ] Migrar CSV para TimescaleDB
- [ ] Implementar Redis para cache
- [ ] Estruturar logs em JSON
- [ ] Adicionar testes de integração

### Fase 2: Performance (2-3 semanas)
- [ ] Introduzir Kafka para processamento assíncrono
- [ ] Criar Workers separados
- [ ] Implementar Circuit Breaker
- [ ] Configurar HPA no Kubernetes

### Fase 3: Security (2 semanas)
- [ ] Implementar OAuth2 + JWT
- [ ] Configurar Vault para segredos
- [ ] Adicionar Rate Limiting
- [ ] Implementar Data Masking

### Fase 4: MLOps (2-3 semanas)
- [ ] Configurar MLflow
- [ ] Criar pipeline Airflow
- [ ] Implementar A/B testing de modelos
- [ ] Monitorar model drift

### Fase 5: Clawdbot Integration 🦞 (1-2 semanas)
- [ ] Instalar e configurar Clawdbot
- [ ] Criar skills de status e alertas
- [ ] Integrar com Alertmanager (webhook)
- [ ] Implementar runbooks via chat
- [ ] Configurar briefings automáticos
- [ ] Testar canais (WhatsApp/Telegram)

### Fase 6: Observability (1-2 semanas)
- [ ] Integrar OpenTelemetry
- [ ] Configurar Jaeger
- [ ] Definir SLOs
- [ ] Criar dashboards de SLI

---

## 11. Por que Clawdbot é Perfeito para Night Shift?

> *"We want firefighters that use code to stop the fire."*

O Clawdbot transforma seu celular em um **painel de controle portátil**:

1. **Alertas que acordam** - Notificações críticas chegam no WhatsApp/Telegram
2. **Zero fricção** - Não precisa abrir laptop para verificar status
3. **Ação rápida** - Execute runbooks pelo chat enquanto investiga
4. **Contexto persistente** - O bot lembra conversas anteriores
5. **Proativo** - Briefings automáticos no início/fim do turno

Para um **Monitoring Intelligence Analyst** no turno da noite, isso significa:
- Menos tempo de resposta (MTTR)
- Melhor qualidade de vida (não ficar grudado no laptop)
- Documentação automática das ações
- Handoff de turno mais eficiente

---

*"The best monitoring system is the one that comes to you, not the one you have to go to."*
