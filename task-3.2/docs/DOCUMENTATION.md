# 🛡️ Transaction Guardian - Documentação Completa

> **CloudWalk Monitoring Intelligence Challenge - Task 3.2**
> 
> Sistema Enterprise de Monitoramento de Transações em Tempo Real com Detecção de Anomalias, Machine Learning, Alertas Inteligentes e Predição de Incidentes.

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Requisitos e Instalação](#3-requisitos-e-instalação)
4. [Fases do Projeto](#4-fases-do-projeto)
   - [Phase 1: Foundation](#phase-1-foundation---timescaledb)
   - [Phase 2: Performance](#phase-2-performance---redis-cache)
   - [Phase 3: Security](#phase-3-security---autenticação)
   - [Phase 4: MLOps](#phase-4-mlops---mlflow)
   - [Phase 5: Telegram Bot](#phase-5-telegram-bot)
   - [Phase 6: AI Summary](#phase-6-ai-summary)
   - [Phase 7: Shugo Prediction](#phase-7-shugo-prediction-engine)
5. [API Reference](#5-api-reference)
6. [Monitoramento e Dashboards](#6-monitoramento-e-dashboards)
7. [Detecção de Anomalias](#7-detecção-de-anomalias)
8. [Guia de Operação](#8-guia-de-operação)
9. [Troubleshooting](#9-troubleshooting)
10. [Roadmap Futuro](#10-roadmap-futuro)

---

## 1. Visão Geral

### 1.1 O que é o Transaction Guardian?

O **Transaction Guardian** é um sistema completo de monitoramento de transações financeiras desenvolvido como resposta ao desafio técnico da CloudWalk para a posição de **Monitoring Intelligence Analyst (Night Shift)**.

O sistema foi projetado com mentalidade de "bombeiro" - detectar e alertar sobre problemas ANTES que se tornem incêndios.

### 1.2 Principais Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Detecção de Anomalias** | Combinação de ML (Isolation Forest) + Estatística (Z-Score) + Regras |
| **Alertas em Tempo Real** | Telegram, Alertmanager, Grafana |
| **Predição de Incidentes** | Shugo Engine prevê anomalias antes de acontecerem |
| **Relatórios AI** | Geração automática de relatórios com insights |
| **Cache Inteligente** | Redis para respostas < 10ms |
| **MLOps** | Versionamento de modelos com MLflow |
| **Autenticação** | JWT + API Keys com RBAC |

### 1.3 Tecnologias Utilizadas

```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION GUARDIAN                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend         │  React, Tailwind CSS, Chart.js          │
│  Backend          │  FastAPI (Python 3.11)                   │
│  Database         │  TimescaleDB (PostgreSQL)                │
│  Cache            │  Redis                                   │
│  ML Platform      │  MLflow, Scikit-learn                    │
│  Monitoring       │  Prometheus, Grafana, Alertmanager       │
│  Notifications    │  Telegram Bot API                        │
│  Container        │  Docker, Docker Compose                  │
│  Cloud            │  Google Cloud Platform (GCP)             │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 URLs do Sistema (Live Demo)

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **API Docs** | http://34.39.251.57:8001/docs | Swagger/OpenAPI |
| **Shugo Dashboard** | http://34.39.251.57:8001/shugo/dashboard | Dashboard de Predição |
| **Grafana** | http://34.39.251.57:3002 | Dashboards de Monitoramento |
| **Prometheus** | http://34.39.251.57:9091 | Métricas |
| **Alertmanager** | http://34.39.251.57:9093 | Gestão de Alertas |
| **MLflow** | http://34.39.251.57:5000 | ML Platform |
| **Redis Commander** | http://34.39.251.57:8081 | Admin do Redis |
| **pgAdmin** | http://34.39.251.57:5050 | Admin do PostgreSQL |

---

## 2. Arquitetura do Sistema

### 2.1 Diagrama de Arquitetura

```
                                    ┌─────────────────┐
                                    │   Telegram Bot  │
                                    │ @omega_trans... │
                                    └────────▲────────┘
                                             │
┌─────────────┐    ┌─────────────────────────┴─────────────────────────┐
│   Cliente   │───▶│                 FastAPI v2.2                       │
│  (curl/web) │    │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
└─────────────┘    │  │  Auth   │ │ Anomaly │ │  Shugo  │ │   AI    │ │
                   │  │  JWT/   │ │Detector │ │Predict  │ │ Summary │ │
                   │  │ API Key │ │  ML+Stats│ │ Engine  │ │ Report  │ │
                   │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │
                   └───────┼──────────┼──────────┼──────────┼────────┘
                           │          │          │          │
              ┌────────────┴──────────┴──────────┴──────────┴────────┐
              │                                                       │
              ▼                                                       ▼
      ┌──────────────┐                                      ┌──────────────┐
      │    Redis     │                                      │  TimescaleDB │
      │    Cache     │                                      │   (Postgres) │
      └──────────────┘                                      └──────────────┘
              │                                                       │
              └───────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │    Prometheus      │
                           │    (Métricas)      │
                           └─────────┬──────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             ┌──────────┐    ┌──────────────┐  ┌──────────┐
             │ Grafana  │    │ Alertmanager │  │  MLflow  │
             │Dashboards│    │   (Alertas)  │  │ (MLOps)  │
             └──────────┘    └──────────────┘  └──────────┘
```

### 2.2 Fluxo de Dados

```
1. Transação chega via POST /transaction
                    │
                    ▼
2. Verifica cache Redis (hit = retorna imediato)
                    │
                    ▼
3. Processa com Anomaly Detector
   ├── Isolation Forest (60% peso)
   ├── Z-Score (40% peso)
   └── Rule-based (flags)
                    │
                    ▼
4. Alimenta Shugo Engine (aprendizado)
                    │
                    ▼
5. Classifica: NORMAL / WARNING / CRITICAL
                    │
                    ▼
6. Se anomalia:
   ├── Salva em state.recent_anomalies
   ├── Envia alerta Telegram
   ├── Atualiza métricas Prometheus
   └── Dispara Alertmanager (se configurado)
                    │
                    ▼
7. Retorna resposta JSON com recomendação
```

### 2.3 Portas e Serviços

| Porta | Serviço | Interno Docker |
|-------|---------|----------------|
| 8001 | FastAPI | 8000 |
| 3002 | Grafana | 3000 |
| 9091 | Prometheus | 9090 |
| 9093 | Alertmanager | 9093 |
| 6379 | Redis | 6379 |
| 8081 | Redis Commander | 8081 |
| 5432 | TimescaleDB | 5432 |
| 5050 | pgAdmin | 80 |
| 5000 | MLflow | 5000 |

---

## 3. Requisitos e Instalação

### 3.1 Requisitos de Sistema

```
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo (8GB recomendado)
- 20GB espaço em disco
- Conexão com internet (para imagens Docker)
```

### 3.2 Clone do Repositório

```bash
git clone https://github.com/akamitatrush/cloudwalk-challenge.git
cd cloudwalk-challenge
```

### 3.3 Estrutura de Branches

```
main                 → Entrega original (intocada)
phase2-performance   → Redis + Rate Limiting
phase3-security      → JWT + API Keys
phase4-mlops         → MLflow Integration
phase5-clawdbot      → Telegram Bot
phase6-ai-summary    → AI Reports
phase7-shugo         → Prediction Engine + Dashboard
```

### 3.4 Instalação Completa

```bash
# Navegar para o diretório
cd task-3.2/infrastructure

# Iniciar serviços principais
docker compose up -d --build

# Iniciar Redis
docker compose -f docker-compose.redis.yml up -d

# Iniciar TimescaleDB
docker compose -f docker-compose.timescale.yml up -d

# Iniciar MLflow
docker compose -f docker-compose.mlflow.yml up -d

# Verificar status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 3.5 Verificação da Instalação

```bash
# Health check
curl http://localhost:8001/health

# Resposta esperada:
{
  "status": "healthy",
  "version": "2.2.0",
  "uptime_seconds": 123.45
}
```

---

## 4. Fases do Projeto

---

### Phase 1: Foundation - TimescaleDB

**Branch:** `main` (incluído na base)

**Objetivo:** Estabelecer a base de dados temporal para armazenamento de transações.

#### 4.1.1 O que é TimescaleDB?

TimescaleDB é uma extensão do PostgreSQL otimizada para séries temporais. Perfeito para dados de transações que têm timestamp.

#### 4.1.2 Configuração

```yaml
# docker-compose.timescale.yml
services:
  guardian-timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: guardian-timescaledb
    environment:
      POSTGRES_USER: guardian
      POSTGRES_PASSWORD: guardian123
      POSTGRES_DB: transactions
    ports:
      - "5432:5432"
    volumes:
      - timescale_data:/var/lib/postgresql/data
```

#### 4.1.3 Schema do Banco

```sql
-- Criar extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tabela de transações
CREATE TABLE transactions (
    id SERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,
    count INTEGER NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    alert_level VARCHAR(20),
    anomaly_score FLOAT,
    PRIMARY KEY (id, timestamp)
);

-- Converter para hypertable (otimização temporal)
SELECT create_hypertable('transactions', 'timestamp');

-- Índices
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_anomaly ON transactions(is_anomaly);
```

#### 4.1.4 Dados Migrados

- **42,920+ transações** históricas
- Continuous Aggregates para métricas horárias
- Compression policy para dados antigos

---

### Phase 2: Performance - Redis Cache

**Branch:** `phase2-performance`

**Objetivo:** Adicionar cache para respostas ultra-rápidas e rate limiting.

#### 4.2.1 Arquitetura do Cache

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Request   │────▶│    Redis    │────▶│   Response  │
│             │     │   (Cache)   │     │   < 10ms    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    Cache Miss?
                           │
                           ▼
                    ┌─────────────┐
                    │   Process   │
                    │  (Detector) │
                    └─────────────┘
```

#### 4.2.2 Arquivo: `cache.py`

```python
class RedisCache:
    def __init__(self, host: str = "guardian-redis", port: int = 6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.connected = self._test_connection()
    
    def get_transaction_result(self, tx_data: dict) -> Optional[dict]:
        """Busca resultado em cache"""
        key = self._generate_key(tx_data)
        cached = self.client.get(key)
        if cached:
            self.stats["hits"] += 1
            return json.loads(cached)
        self.stats["misses"] += 1
        return None
    
    def set_transaction_result(self, tx_data: dict, result: dict, ttl: int = 300):
        """Salva resultado em cache"""
        key = self._generate_key(tx_data)
        self.client.setex(key, ttl, json.dumps(result))
        self.stats["sets"] += 1
```

#### 4.2.3 Rate Limiting

```python
# Configuração: 100 requests por minuto
RATE_LIMIT = 100
RATE_WINDOW = 60  # segundos

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, RATE_WINDOW)
    
    if current > RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": RATE_WINDOW}
        )
    
    return await call_next(request)
```

#### 4.2.4 Métricas de Cache

```bash
# Endpoint de estatísticas
curl http://localhost:8001/cache/stats

# Resposta:
{
  "connected": true,
  "host": "guardian-redis:6379",
  "hits": 1523,
  "misses": 456,
  "sets": 456,
  "hit_rate": 76.9,
  "redis_info": {
    "used_memory": "2.5M",
    "connected_clients": 3
  }
}
```

---

### Phase 3: Security - Autenticação

**Branch:** `phase3-security`

**Objetivo:** Implementar autenticação JWT e API Keys com controle de acesso.

#### 4.3.1 Métodos de Autenticação

| Método | Uso | Expiração |
|--------|-----|-----------|
| **JWT** | Login interativo | 24 horas |
| **API Key** | Integrações/Scripts | Sem expiração |

#### 4.3.2 Arquivo: `auth.py`

```python
# Configuração JWT
JWT_SECRET = os.getenv("JWT_SECRET", "guardian-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24  # horas

# Usuários padrão
DEFAULT_USERS = {
    "admin": {
        "password": hash_password("admin123"),
        "roles": ["read", "write", "admin"]
    },
    "operator": {
        "password": hash_password("operator123"),
        "roles": ["read", "write"]
    },
    "viewer": {
        "password": hash_password("viewer123"),
        "roles": ["read"]
    }
}

def create_jwt_token(username: str, roles: list) -> str:
    """Cria token JWT"""
    payload = {
        "sub": username,
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

#### 4.3.3 Endpoints de Autenticação

```bash
# Login (obter JWT)
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Resposta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "username": "admin",
    "roles": ["read", "write", "admin"]
  }
}

# Usar JWT
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Usar API Key
curl http://localhost:8001/auth/me \
  -H "X-API-Key: guardian-api-key-2024"
```

#### 4.3.4 RBAC (Role-Based Access Control)

| Role | Permissões |
|------|------------|
| `read` | GET endpoints |
| `write` | POST/PUT endpoints |
| `admin` | DELETE, /admin/*, gerenciamento |

```python
def require_role(required_role: str):
    """Decorator para verificar role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = get_current_user()
            if required_role not in user.roles:
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/admin/users")
@require_role("admin")
async def create_user(user: UserCreate):
    ...
```

---

### Phase 4: MLOps - MLflow

**Branch:** `phase4-mlops`

**Objetivo:** Implementar versionamento e gerenciamento de modelos ML.

#### 4.4.1 O que é MLflow?

MLflow é uma plataforma open-source para gerenciar o ciclo de vida de ML:
- **Tracking:** Registra experimentos, parâmetros, métricas
- **Models:** Versionamento e registro de modelos
- **Registry:** Promove modelos entre estágios (Staging → Production)

#### 4.4.2 Arquivo: `mlops.py`

```python
class MLOpsManager:
    def __init__(self):
        mlflow.set_tracking_uri("http://guardian-mlflow:5000")
        mlflow.set_experiment("transaction-guardian-anomaly")
    
    def train_model(self, n_estimators: int = 100, contamination: float = 0.1):
        """Treina modelo e registra no MLflow"""
        with mlflow.start_run():
            # Treinar Isolation Forest
            model = IsolationForest(
                n_estimators=n_estimators,
                contamination=contamination,
                random_state=42
            )
            model.fit(training_data)
            
            # Logar parâmetros
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("contamination", contamination)
            
            # Logar métricas
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            
            # Registrar modelo
            mlflow.sklearn.log_model(model, "anomaly-detector")
            
            return mlflow.active_run().info.run_id
    
    def promote_to_production(self, version: int):
        """Promove modelo para produção"""
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name="anomaly-detector",
            version=version,
            stage="Production"
        )
```

#### 4.4.3 Endpoints MLOps

```bash
# Status
curl http://localhost:8001/mlops/status

# Listar modelos
curl http://localhost:8001/mlops/models

# Treinar novo modelo (requer auth admin)
curl -X POST http://localhost:8001/mlops/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"n_estimators": 150, "contamination": 0.08}'

# Promover para produção
curl -X POST http://localhost:8001/mlops/promote \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"version": 2}'

# Verificar drift
curl http://localhost:8001/mlops/drift
```

#### 4.4.4 Interface MLflow

Acesse http://34.39.251.57:5000 para:
- Ver todos os experimentos
- Comparar runs
- Visualizar métricas
- Gerenciar modelos registrados

---

### Phase 5: Telegram Bot

**Branch:** `phase5-clawdbot`

**Objetivo:** Alertas em tempo real via Telegram.

#### 4.5.1 Configuração do Bot

1. Fale com @BotFather no Telegram
2. Crie novo bot: `/newbot`
3. Obtenha o token
4. Configure no docker-compose:

```yaml
environment:
  - TELEGRAM_TOKEN=seu_token_aqui
```

#### 4.5.2 Arquivo: `telegram_bot.py`

```python
class ClawdBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.authorized_users = set()
        self.subscribers = set()
    
    async def handle_command(self, chat_id: int, command: str, args: str):
        """Processa comandos do bot"""
        
        if command == "/start":
            if args == BOT_PASSWORD:
                self.authorized_users.add(chat_id)
                self.subscribers.add(chat_id)
                await self.send_message(chat_id, "✅ Autorizado!")
            else:
                await self.send_message(chat_id, "🔒 Senha necessária")
        
        elif command == "/status":
            # Busca status da API
            status = await self.get_api_status()
            await self.send_message(chat_id, format_status(status))
        
        elif command == "/anomalies":
            anomalies = await self.get_recent_anomalies()
            await self.send_message(chat_id, format_anomalies(anomalies))
    
    async def broadcast_alert(self, message: str):
        """Envia alerta para todos os inscritos"""
        for chat_id in self.subscribers:
            await self.send_message(chat_id, message)
```

#### 4.5.3 Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/start <senha>` | Autenticar no bot |
| `/status` | Status do sistema |
| `/stats` | Estatísticas de transações |
| `/anomalies` | Últimas 5 anomalias |
| `/health` | Health check |
| `/subscribe` | Receber alertas |
| `/unsubscribe` | Parar alertas |

#### 4.5.4 Formato de Alertas

```
🔴 ALERTA CRITICAL
━━━━━━━━━━━━━━━━━━

📊 Score: 0.85
📈 Volume: 5
📉 Média: 100.0

Violações:
• Volume drop detected
• LOW_VOLUME: 5 < 50

⏰ 16:00:50
━━━━━━━━━━━━━━━━━━
```

---

### Phase 6: AI Summary

**Branch:** `phase6-ai-summary`

**Objetivo:** Relatórios automáticos com análise inteligente.

#### 4.6.1 Arquivo: `ai_summary.py`

```python
class AISummaryGenerator:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY", "")
    
    async def generate_report(self, stats: dict, anomalies: list) -> str:
        """Gera relatório de análise"""
        
        # Calcular métricas
        total_tx = stats.get('total_processed', 0)
        total_anomalies = stats.get('total_anomalies', 0)
        approval_rate = stats.get('approval_rate', 0)
        
        # Health score
        health_score = max(0, 100 - (anomaly_rate * 100))
        
        report = f"""
📊 **RELATÓRIO DIÁRIO - TRANSACTION GUARDIAN**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📈 **RESUMO EXECUTIVO**
Processamos {total_tx:,} transações com taxa de aprovação de {approval_rate:.1%}.
Detectamos {total_anomalies:,} anomalias.

🚨 **PRINCIPAIS INCIDENTES**
• {critical} alertas CRITICAL
• {warning} alertas WARNING

💡 **RECOMENDAÇÕES**
1. {recomendacao_1}
2. {recomendacao_2}
3. {recomendacao_3}

🎯 **SCORE DE SAÚDE: {health_score:.0f}/100**
        """
        
        return report
```

#### 4.6.2 Endpoints AI

```bash
# Gerar relatório
curl http://localhost:8001/ai/report

# Enviar por Telegram
curl -X POST http://localhost:8001/ai/report/send

# Status
curl http://localhost:8001/ai/status
```

---

### Phase 7: Shugo Prediction Engine

**Branch:** `phase7-shugo`

**Objetivo:** Prever anomalias ANTES que aconteçam.

#### 4.7.1 O que é Shugo?

**Shugo (守護)** significa "Guardião" em japonês. É um sistema de predição que:
- Analisa padrões históricos por hora e dia da semana
- Detecta tendências (subindo/caindo/estável)
- Calcula probabilidade de anomalia futura
- Alerta antes do problema acontecer

#### 4.7.2 Arquivo: `shugo.py`

```python
class ShugoEngine:
    def __init__(self, window_size: int = 100):
        self.history = deque(maxlen=1000)
        self.hourly_patterns = {h: [] for h in range(24)}
        self.daily_patterns = {d: [] for d in range(7)}
    
    def add_observation(self, timestamp: datetime, volume: int, status: str):
        """Adiciona observação ao histórico"""
        observation = {
            "timestamp": timestamp,
            "volume": volume,
            "status": status,
            "hour": timestamp.hour,
            "weekday": timestamp.weekday()
        }
        self.history.append(observation)
        self.hourly_patterns[timestamp.hour].append(volume)
        self.daily_patterns[timestamp.weekday()].append(volume)
    
    def predict_next(self, minutes_ahead: int = 30) -> Prediction:
        """Prevê volume para os próximos N minutos"""
        future_time = datetime.now() + timedelta(minutes=minutes_ahead)
        
        # Baselines
        hourly_mean, hourly_std = self.get_hourly_baseline(future_time.hour)
        daily_mean, daily_std = self.get_daily_baseline(future_time.weekday())
        
        # Predição ponderada
        predicted_volume = (hourly_mean * 0.6) + (daily_mean * 0.4)
        
        # Tendência
        trend = self._calculate_trend()
        
        # Probabilidade de alerta
        alert_probability = self._calculate_alert_probability(
            predicted_volume, hourly_mean, hourly_std
        )
        
        return Prediction(
            timestamp=future_time,
            predicted_volume=predicted_volume,
            confidence=self._calculate_confidence(),
            trend=trend,
            alert_probability=alert_probability
        )
    
    def detect_patterns(self) -> List[Pattern]:
        """Detecta padrões nos dados"""
        patterns = []
        
        # Detectar horários de pico
        peak_hours = self._find_peak_hours()
        if peak_hours:
            patterns.append(Pattern(
                name="Peak Hours",
                description=f"Alto volume às {peak_hours}h",
                confidence=0.8
            ))
        
        # Detectar horários de baixo volume
        low_hours = self._find_low_hours()
        if low_hours:
            patterns.append(Pattern(
                name="Low Volume Hours",
                description=f"Baixo volume às {low_hours}h",
                confidence=0.8
            ))
        
        return patterns
```

#### 4.7.3 Endpoints Shugo

```bash
# Status
curl http://localhost:8001/shugo/status

# Predição (30 minutos)
curl http://localhost:8001/shugo/predict?minutes=30

# Forecast (6 horas)
curl http://localhost:8001/shugo/forecast?hours=6

# Padrões detectados
curl http://localhost:8001/shugo/patterns

# Treinar com dados simulados
curl -X POST http://localhost:8001/shugo/train

# Baseline por hora
curl http://localhost:8001/shugo/hourly-baseline

# Baseline por dia
curl http://localhost:8001/shugo/daily-baseline
```

#### 4.7.4 Dashboard Shugo

Acesse: http://34.39.251.57:8001/shugo/dashboard

**Features do Dashboard:**
- 🎯 Health Gauge visual
- 📈 Gráfico de forecast 6 horas
- 🔍 Padrões detectados
- ❓ Tooltips explicativos
- 📖 Guia interativo
- 🎯 Botão treinar modelo
- 🔄 Auto-refresh 15 segundos

---

## 5. API Reference

### 5.1 Endpoints Principais

#### Transações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/transaction` | Processar transação |
| POST | `/transactions/batch` | Processar lote |
| GET | `/anomalies` | Listar anomalias |
| GET | `/stats` | Estatísticas gerais |
| GET | `/health` | Health check |

#### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/login` | Login (JWT) |
| GET | `/auth/me` | Info do usuário |
| POST | `/auth/api-keys` | Criar API key |
| GET | `/auth/api-keys` | Listar API keys |

#### Shugo

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/shugo/status` | Status do engine |
| GET | `/shugo/predict` | Predição |
| GET | `/shugo/forecast` | Forecast |
| GET | `/shugo/patterns` | Padrões |
| POST | `/shugo/train` | Treinar |

#### AI

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/ai/report` | Gerar relatório |
| POST | `/ai/report/send` | Enviar por Telegram |
| GET | `/ai/status` | Status |

#### Telegram

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/telegram/status` | Status do bot |
| POST | `/telegram/start` | Iniciar bot |
| POST | `/telegram/stop` | Parar bot |
| POST | `/telegram/send-alert` | Enviar alerta |

### 5.2 Exemplos de Requisições

```bash
# Processar transação
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "count": 150
  }'

# Resposta:
{
  "is_anomaly": false,
  "alert_level": "NORMAL",
  "anomaly_score": 0.23,
  "rule_violations": [],
  "recommendation": "✅ Transação normal.",
  "metrics": {
    "current_count": 150,
    "running_mean": 120.5,
    "running_std": 45.2,
    "zscore": 0.65,
    "ml_score": 0.18,
    "approval_rate": 0.72
  },
  "cached": false
}

# Processar lote
curl -X POST http://localhost:8001/transactions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"status": "approved", "count": 100},
      {"status": "denied", "count": 50},
      {"status": "approved", "count": 200}
    ]
  }'

# Listar anomalias
curl "http://localhost:8001/anomalies?limit=10&level=CRITICAL"

# Estatísticas
curl http://localhost:8001/stats
```

---

## 6. Monitoramento e Dashboards

### 6.1 Grafana

**URL:** http://34.39.251.57:3002

#### Dashboards Disponíveis:

1. **Transaction Overview**
   - Volume de transações por minuto
   - Taxa de aprovação
   - Distribuição por status

2. **Anomaly Detection**
   - Anomalias por hora
   - Score médio de anomalia
   - Alertas por severidade

3. **System Health**
   - Uptime da API
   - Latência de requisições
   - Uso de memória/CPU

4. **Cache Performance**
   - Hit rate
   - Memória utilizada
   - Operações por segundo

### 6.2 Prometheus

**URL:** http://34.39.251.57:9091

#### Métricas Expostas:

```
# Transações
transactions_total{status="approved"}
transactions_total{status="denied"}
transactions_total{status="failed"}

# Anomalias
anomalies_total{level="CRITICAL"}
anomalies_total{level="WARNING"}
anomaly_score_histogram

# Cache
cache_hits_total
cache_misses_total
cache_hit_rate

# API
http_requests_total
http_request_duration_seconds
```

### 6.3 Alertmanager

**URL:** http://34.39.251.57:9093

#### Regras de Alerta Configuradas:

```yaml
groups:
  - name: transaction-guardian
    rules:
      - alert: HighAnomalyRate
        expr: rate(anomalies_total[5m]) > 0.3
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Alta taxa de anomalias detectada"
      
      - alert: CriticalAnomaly
        expr: anomalies_total{level="CRITICAL"} > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Anomalia crítica detectada!"
      
      - alert: APIDown
        expr: up{job="guardian-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API Guardian está fora do ar"
```

---

## 7. Detecção de Anomalias

### 7.1 Algoritmos Utilizados

#### Isolation Forest (60% peso)

```python
# Machine Learning - detecta outliers isolando pontos
model = IsolationForest(
    n_estimators=100,      # Número de árvores
    contamination=0.1,     # % esperado de anomalias
    random_state=42
)

# Score: -1 (anomalia) a +1 (normal)
ml_score = model.decision_function(features)
```

#### Z-Score (40% peso)

```python
# Estatístico - quantos desvios padrão da média
z_score = (valor - media) / desvio_padrao

# |z| > 2: possível anomalia
# |z| > 3: provável anomalia
```

#### Rule-Based (Flags)

```python
RULES = {
    "LOW_VOLUME": lambda count, mean: count < 50,
    "HIGH_VOLUME": lambda count, mean: count > mean * 3,
    "VOLUME_DROP": lambda count, mean: count < mean * 0.5,
    "VOLUME_SPIKE": lambda count, mean: count > mean * 2,
    "DENIED": lambda status: status == "denied",
    "FAILED": lambda status: status == "failed",
}
```

### 7.2 Classificação de Alertas

| Nível | Critério | Ação Recomendada |
|-------|----------|------------------|
| **NORMAL** | Score < 0.3, sem violações | Monitoramento padrão |
| **WARNING** | 0.3 ≤ Score < 0.5 ou 1-2 violações | Aumentar vigilância |
| **CRITICAL** | Score ≥ 0.5 ou 3+ violações | Investigar imediatamente |

### 7.3 Exemplo de Detecção

```python
def detect_anomaly(tx_data: dict) -> dict:
    features = extract_features(tx_data)
    
    # ML Score
    ml_score = isolation_forest.decision_function([features])[0]
    ml_normalized = (ml_score + 1) / 2  # 0 a 1
    
    # Z-Score
    z_score = (tx_data["count"] - running_mean) / running_std
    z_normalized = min(1, abs(z_score) / 4)  # 0 a 1
    
    # Score combinado
    anomaly_score = (ml_normalized * 0.6) + (z_normalized * 0.4)
    
    # Verificar regras
    violations = check_rules(tx_data)
    
    # Classificar
    if anomaly_score >= 0.5 or len(violations) >= 3:
        alert_level = "CRITICAL"
    elif anomaly_score >= 0.3 or len(violations) >= 1:
        alert_level = "WARNING"
    else:
        alert_level = "NORMAL"
    
    return {
        "is_anomaly": alert_level != "NORMAL",
        "alert_level": alert_level,
        "anomaly_score": anomaly_score,
        "rule_violations": violations,
        "recommendation": generate_recommendation(alert_level, violations)
    }
```

---

## 8. Guia de Operação

### 8.1 Iniciar Sistema Completo

```bash
cd ~/cloudwalk-challenge/task-3.2/infrastructure

# Iniciar todos os serviços
docker compose up -d --build
docker compose -f docker-compose.redis.yml up -d
docker compose -f docker-compose.timescale.yml up -d
docker compose -f docker-compose.mlflow.yml up -d

# Verificar status
docker ps

# Iniciar bot Telegram
curl -X POST http://localhost:8001/telegram/start

# Treinar Shugo
curl -X POST http://localhost:8001/shugo/train
```

### 8.2 Injetar Dados de Teste

```bash
cd ~/cloudwalk-challenge/task-3.2

# Script de injeção contínua
cat > inject_fast.sh << 'EOF'
#!/bin/bash
while true; do
    STATUS=$(shuf -e approved approved approved denied failed -n 1)
    VOLUME=$((50 + RANDOM % 150))
    curl -s -X POST "http://localhost:8001/transaction" \
        -H "Content-Type: application/json" \
        -d "{\"status\": \"$STATUS\", \"count\": $VOLUME}" > /dev/null
    sleep 0.3
done
EOF
chmod +x inject_fast.sh

# Rodar em background
nohup ./inject_fast.sh > inject_log.txt 2>&1 &
```

### 8.3 Monitorar Sistema

```bash
# Logs da API
docker logs -f guardian-api

# Estatísticas
watch -n 5 'curl -s http://localhost:8001/stats | jq .'

# Shugo status
watch -n 10 'curl -s http://localhost:8001/shugo/status | jq .'

# Ver anomalias recentes
curl http://localhost:8001/anomalies?limit=5 | jq .
```

### 8.4 Parar Sistema

```bash
# Parar injeção
pkill -f inject_fast

# Parar containers
cd ~/cloudwalk-challenge/task-3.2/infrastructure
docker compose down
docker compose -f docker-compose.redis.yml down
docker compose -f docker-compose.timescale.yml down
docker compose -f docker-compose.mlflow.yml down
```

---

## 9. Troubleshooting

### 9.1 API não responde

```bash
# Verificar se container está rodando
docker ps | grep guardian-api

# Ver logs
docker logs guardian-api --tail 50

# Reiniciar
docker compose restart guardian-api
```

### 9.2 Rate Limit (429)

```bash
# Aguardar reset (60 segundos)
sleep 60

# Ou reduzir velocidade de injeção
# Alterar sleep no script de 0.3 para 1.0
```

### 9.3 Telegram não envia

```bash
# Verificar se bot está rodando
curl http://localhost:8001/telegram/status

# Reiniciar bot
curl -X POST http://localhost:8001/telegram/stop
curl -X POST http://localhost:8001/telegram/start

# Verificar token
docker logs guardian-api | grep -i telegram
```

### 9.4 Shugo com poucos dados

```bash
# Treinar com dados simulados
curl -X POST http://localhost:8001/shugo/train

# Verificar cobertura
curl http://localhost:8001/shugo/status | jq '.hourly_coverage, .daily_coverage'
```

### 9.5 Redis não conecta

```bash
# Verificar container
docker ps | grep redis

# Reiniciar
docker compose -f docker-compose.redis.yml restart

# Testar conexão
docker exec guardian-redis redis-cli ping
```

---

## 10. Roadmap Futuro

### 10.1 Próximas Fases Planejadas

| Phase | Feature | Descrição |
|-------|---------|-----------|
| **8** | ChatOps Slack | Comandos via Slack |
| **9** | Kubernetes | Deploy em K8s |
| **10** | OpenTelemetry | Tracing distribuído |
| **11** | Kafka Streaming | Processamento em tempo real |
| **12** | Mobile App | App React Native |

### 10.2 Melhorias Técnicas

- [ ] WebSocket para updates em tempo real
- [ ] GraphQL API
- [ ] Autenticação OAuth2
- [ ] Multi-tenancy
- [ ] Horizontal scaling
- [ ] Disaster recovery

### 10.3 Melhorias de ML

- [ ] Prophet para séries temporais
- [ ] LSTM para padrões complexos
- [ ] AutoML para otimização
- [ ] Explicabilidade (SHAP)
- [ ] A/B testing de modelos

---

## 📞 Contato

**Desenvolvedor:** Sérgio Henrique

| | |
|---|---|
| 📧 Email | sergio@lognullsec.com |
| 💼 LinkedIn | [linkedin.com/in/akasergiosilva](https://linkedin.com/in/akasergiosilva) |
| 🐙 GitHub | [github.com/akamitatrush](https://github.com/akamitatrush) |

---

## 📄 Licença

Este projeto foi desenvolvido como parte do processo seletivo da CloudWalk para a posição de **Monitoring Intelligence Analyst (Night Shift)**.

---

*"Bombeiros que usam código para apagar incêndios." 🔥*

**Transaction Guardian v2.2** | **2026**
