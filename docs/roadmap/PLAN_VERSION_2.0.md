# 🚀 Transaction Guardian v2.0: Plano de Modernização Enterprise

**Autores:** Sérgio (Candidato) + Claude AI + Gemini AI  
**Data:** Janeiro 2025  
**Contexto:** Evolução do Desafio CloudWalk (Task 3.2) para Arquitetura de Produção

---

## 📋 Sumário Executivo

O projeto atual (v1.0) funciona perfeitamente como uma Prova de Conceito (PoC), demonstrando a detecção de anomalias em tempo real com:
- 3 métodos de detecção (ML + Z-Score + Rules)
- 5 dashboards Grafana com 31 painéis
- API FastAPI com 9 endpoints
- Stack completa em Docker

A **versão 2.0** visa transformar essa aplicação em um sistema **resiliente, escalável e seguro**, capaz de processar milhares de transações por segundo (TPS) e atender a requisitos de conformidade bancária.

---

## 📊 Comparativo de Versões

| Aspecto | v1.0 (Atual) | v2.0 (Proposta) |
|---------|--------------|-----------------|
| Processamento | Síncrono | Assíncrono (Event-Driven) |
| Persistência | CSV/Memória | TimescaleDB |
| Cache | Nenhum | Redis |
| Autenticação | Nenhuma | OAuth2 + JWT |
| Observabilidade | Prometheus/Grafana | + OpenTelemetry + Jaeger |
| ML Pipeline | Estático | MLflow + Airflow |
| CI/CD | Manual | GitHub Actions |
| Escala | Single instance | Horizontal (K8s ready) |

---

## 1. Arquitetura e Escalabilidade (Backend)

### 1.1. Arquitetura Orientada a Eventos (Async)

**Problema Atual:** O endpoint `POST /transaction` processa a detecção de forma síncrona. Se o modelo demorar, a API trava.

**Solução:** Desacoplar a ingestão do processamento usando filas.

**Stack Recomendada:**
- **Message Broker:** Apache Kafka (preferido para alta escala) ou RabbitMQ
- **Biblioteca:** `aiokafka` ou `aio-pika`

**Arquitetura Proposta:**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  API (Fast) │────▶│    Kafka    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
               ┌────▼────┐              ┌──────▼──────┐            ┌──────▼──────┐
               │ Worker 1│              │  Worker 2   │            │  Worker N   │
               │  (ML)   │              │    (ML)     │            │    (ML)     │
               └────┬────┘              └──────┬──────┘            └──────┬──────┘
                    │                          │                          │
                    └──────────────────────────┼──────────────────────────┘
                                               │
                                        ┌──────▼──────┐
                                        │ TimescaleDB │
                                        └─────────────┘
```

**Implementação:**

```python
# api/main.py - Ingestão Rápida (< 10ms)
@app.post("/transaction", status_code=202)
async def ingest_transaction(txn: TransactionSchema):
    """Apenas valida e enfileira - resposta imediata"""
    transaction_id = str(uuid.uuid4())
    await kafka_producer.send("transactions", {
        "id": transaction_id,
        "data": txn.dict(),
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"status": "queued", "transaction_id": transaction_id}

# workers/detector.py - Processamento Pesado
async def process_message(message):
    """Worker consome da fila e processa ML"""
    txn = json.loads(message.value)
    
    # Detecção ML (pode demorar)
    score = detector.predict(txn["data"])
    
    # Persistir resultado
    await db.insert("detections", {
        "transaction_id": txn["id"],
        "score": score,
        "is_anomaly": score > THRESHOLD
    })
    
    # Alertar se necessário
    if score > THRESHOLD:
        await alert_manager.notify(txn, score)
```

### 1.2. Persistência Time-Series

**Problema Atual:** Dados dependentes de CSV ou memória volátil.

**Solução:** Banco de dados otimizado para séries temporais.

**Stack Recomendada:**
- **Banco:** TimescaleDB (PostgreSQL com extensão de tempo)
- **ORM:** SQLAlchemy + asyncpg

**Schema Proposto:**

```sql
-- Hypertable para transações (particionado por tempo)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2),
    auth_code VARCHAR(10),
    merchant_id VARCHAR(50),
    card_bin VARCHAR(6),
    ml_score FLOAT,
    zscore FLOAT,
    is_anomaly BOOLEAN,
    alert_level VARCHAR(20)
);

-- Converter para hypertable (otimização TimescaleDB)
SELECT create_hypertable('transactions', 'timestamp');

-- Índices para queries frequentes
CREATE INDEX idx_transactions_status ON transactions (status, timestamp DESC);
CREATE INDEX idx_transactions_anomaly ON transactions (is_anomaly, timestamp DESC);

-- Políticas de retenção automática
SELECT add_retention_policy('transactions', INTERVAL '90 days');

-- Agregações contínuas (pré-calculadas)
CREATE MATERIALIZED VIEW hourly_stats
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    status,
    COUNT(*) as count,
    AVG(ml_score) as avg_score,
    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomaly_count
FROM transactions
GROUP BY hour, status;
```

### 1.3. Caching Distribuído (Redis)

**Problema Atual:** Contadores de regras residem na memória da aplicação.

**Solução:** Externalizar estado para Redis.

**Casos de Uso:**

```python
import aioredis

redis = aioredis.from_url("redis://redis:6379")

# 1. Contador de falhas por usuário (TTL 60s)
async def increment_failure_count(user_id: str) -> int:
    key = f"failed_count:{user_id}"
    count = await redis.incr(key)
    await redis.expire(key, 60)  # Reset após 1 minuto
    return count

# 2. Cache de estatísticas (TTL 30s)
async def get_cached_stats() -> dict:
    cached = await redis.get("stats:current")
    if cached:
        return json.loads(cached)
    
    stats = await calculate_stats()  # Query pesada
    await redis.setex("stats:current", 30, json.dumps(stats))
    return stats

# 3. Rate limiting por IP
async def check_rate_limit(ip: str, limit: int = 100) -> bool:
    key = f"rate:{ip}:{datetime.now().minute}"
    count = await redis.incr(key)
    await redis.expire(key, 60)
    return count <= limit

# 4. Distributed Lock (evitar processamento duplicado)
async def acquire_lock(txn_id: str, ttl: int = 30) -> bool:
    return await redis.set(f"lock:{txn_id}", "1", nx=True, ex=ttl)
```

### 1.4. Circuit Breaker Pattern

**Problema:** Serviço downstream falha e derruba toda a aplicação.

**Solução:** Parar de chamar serviço que está falhando.

```python
from circuitbreaker import circuit

@circuit(
    failure_threshold=5,      # Abre após 5 falhas
    recovery_timeout=30,      # Tenta novamente após 30s
    expected_exception=Exception
)
async def call_external_fraud_service(txn: dict) -> dict:
    """Chama serviço externo de fraude com proteção"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(FRAUD_API_URL, json=txn)
        return response.json()

# Uso com fallback
async def check_fraud(txn: dict) -> dict:
    try:
        return await call_external_fraud_service(txn)
    except CircuitBreakerError:
        # Fallback: usar modelo local
        logger.warning("Circuit breaker open, using local model")
        return {"score": local_model.predict(txn), "source": "fallback"}
```

---

## 2. Cibersegurança (Security by Design)

### 2.1. Autenticação e Autorização (OAuth2 + JWT)

**Problema Atual:** Endpoints críticos como `/reset` estão abertos.

**Solução:** Implementar fluxo OAuth2 com JWT e RBAC.

**Stack Recomendada:**
- **IdP:** Keycloak (self-hosted) ou Auth0 (SaaS)
- **Biblioteca:** `python-jose` + `passlib`

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "read": "Read access",
        "write": "Write access", 
        "admin": "Admin access"
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """Valida JWT e verifica scopes"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        
        # Verificar scopes necessários
        for scope in security_scopes.scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Not enough permissions. Required: {scope}"
                )
                
        return User(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception

# Endpoints protegidos
@app.get("/stats", dependencies=[Security(get_current_user, scopes=["read"])])
async def get_stats():
    return await calculate_stats()

@app.post("/reset", dependencies=[Security(get_current_user, scopes=["admin"])])
async def reset_system():
    return await perform_reset()
```

### 2.2. Gerenciamento de Segredos (Vault)

**Problema Atual:** Variáveis sensíveis em arquivos `.env` ou código.

**Solução:** Injeção de segredos em tempo de execução.

**Stack:** HashiCorp Vault

```python
import hvac

# Inicializar cliente Vault
vault_client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Buscar segredos no startup
def get_secrets():
    secrets = vault_client.secrets.kv.v2.read_secret_version(
        path="transaction-guardian/prod"
    )
    return {
        "db_password": secrets["data"]["data"]["db_password"],
        "jwt_secret": secrets["data"]["data"]["jwt_secret"],
        "kafka_password": secrets["data"]["data"]["kafka_password"]
    }

# Docker Compose com Vault Agent
# O container recebe segredos via volume temporário
```

### 2.3. Hardening da API

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, Field, validator
import re

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/transaction")
@limiter.limit("100/minute")
async def create_transaction(request: Request, txn: TransactionSchema):
    ...

# Validação Estrita com Pydantic
class TransactionSchema(BaseModel):
    status: str = Field(..., regex="^(approved|denied|failed|reversed)$")
    amount: float = Field(..., gt=0, le=1000000, description="Valor positivo até 1M")
    card_bin: str = Field(..., regex=r"^\d{6}$", description="BIN deve ter 6 dígitos")
    merchant_id: str = Field(..., min_length=1, max_length=50)
    
    @validator('card_bin')
    def validate_bin(cls, v):
        # Validar range de BINs conhecidos
        if not (400000 <= int(v) <= 499999 or 500000 <= int(v) <= 599999):
            raise ValueError('BIN fora do range válido')
        return v

# Headers de Segurança
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### 2.4. Data Masking para Logs

```python
import structlog
import re

def mask_sensitive_data(event_dict: dict) -> dict:
    """Mascara dados sensíveis antes de logar"""
    sensitive_patterns = {
        'card_number': (r'\d{16}', lambda m: f"****{m.group()[-4:]}"),
        'cvv': (r'"cvv":\s*"\d{3,4}"', '"cvv": "***"'),
        'password': (r'"password":\s*"[^"]*"', '"password": "***"'),
    }
    
    log_str = str(event_dict)
    for field, (pattern, replacement) in sensitive_patterns.items():
        if callable(replacement):
            log_str = re.sub(pattern, replacement, log_str)
        else:
            log_str = re.sub(pattern, replacement, log_str)
    
    return event_dict

structlog.configure(
    processors=[
        mask_sensitive_data,
        structlog.processors.JSONRenderer()
    ]
)
```

---

## 3. MLOps (Machine Learning Operations)

### 3.1. Model Registry (MLflow)

**Problema Atual:** O modelo IsolationForest é um arquivo estático ou treinado no boot.

**Solução:** Versionamento e gerenciamento de modelos.

```python
import mlflow
from mlflow.tracking import MlflowClient

# Configurar MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
client = MlflowClient()

# Treinar e registrar modelo
def train_and_register_model(X_train, model_name="anomaly_detector"):
    with mlflow.start_run():
        # Treinar
        model = IsolationForest(n_estimators=100, contamination=0.1)
        model.fit(X_train)
        
        # Métricas
        scores = model.decision_function(X_train)
        mlflow.log_metric("mean_score", scores.mean())
        mlflow.log_metric("std_score", scores.std())
        
        # Parâmetros
        mlflow.log_params(model.get_params())
        
        # Registrar modelo
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name=model_name
        )
        
    # Promover para produção
    client.transition_model_version_stage(
        name=model_name,
        version=latest_version,
        stage="Production"
    )

# Carregar modelo em produção
def load_production_model(model_name="anomaly_detector"):
    model_uri = f"models:/{model_name}/Production"
    return mlflow.sklearn.load_model(model_uri)
```

### 3.2. Pipeline de Re-treinamento (Airflow)

**Problema Atual:** Degradação do modelo ao longo do tempo (Concept Drift).

**Solução:** Pipeline automatizado de re-treinamento.

```python
# dags/retrain_model.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'retrain_anomaly_model',
    default_args=default_args,
    description='Re-treina modelo de anomalias semanalmente',
    schedule_interval='0 3 * * 0',  # Domingos 3AM
    catchup=False
)

def extract_data(**context):
    """Extrai dados da última semana"""
    query = """
        SELECT * FROM transactions 
        WHERE timestamp > NOW() - INTERVAL '7 days'
    """
    df = pd.read_sql(query, engine)
    df.to_parquet('/tmp/training_data.parquet')
    return len(df)

def train_model(**context):
    """Treina novo modelo"""
    df = pd.read_parquet('/tmp/training_data.parquet')
    # ... treinar modelo
    return model_version

def validate_model(**context):
    """Valida se novo modelo é melhor"""
    new_f1 = evaluate_model(new_model, test_set)
    current_f1 = evaluate_model(current_model, test_set)
    
    if new_f1 > current_f1 * 1.05:  # 5% melhor
        promote_to_production(new_model)
        return "promoted"
    return "rejected"

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model,
    dag=dag
)

extract_task >> train_task >> validate_task
```

### 3.3. Feature Store

```python
# Centralizar features para consistência entre treino e inferência
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Definir features
transaction_features = store.get_feature_view("transaction_features")

# Buscar features para inferência (online)
features = store.get_online_features(
    features=[
        "transaction_features:avg_amount_1h",
        "transaction_features:count_1h",
        "transaction_features:failure_rate_1h"
    ],
    entity_rows=[{"merchant_id": "merchant_123"}]
).to_dict()
```

---

## 4. Observabilidade Avançada

### 4.1. Tracing Distribuído (OpenTelemetry + Jaeger)

**Problema Atual:** Difícil saber onde está a latência (Banco? ML? Rede?).

**Solução:** Rastreamento ponta a ponta.

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Configurar tracer
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrumentar automaticamente
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)
RedisInstrumentor().instrument()

# Spans customizados
tracer = trace.get_tracer(__name__)

async def detect_anomaly(txn: dict) -> dict:
    with tracer.start_as_current_span("detect_anomaly") as span:
        span.set_attribute("transaction.id", txn["id"])
        
        with tracer.start_as_current_span("ml_prediction"):
            ml_score = model.predict(txn)
            span.set_attribute("ml.score", ml_score)
        
        with tracer.start_as_current_span("zscore_calculation"):
            zscore = calculate_zscore(txn)
            span.set_attribute("zscore.value", zscore)
        
        with tracer.start_as_current_span("rule_evaluation"):
            rule_result = evaluate_rules(txn)
        
        return combine_scores(ml_score, zscore, rule_result)
```

### 4.2. Logs Estruturados (JSON)

```python
import structlog
from datetime import datetime

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Uso
logger.info(
    "anomaly_detected",
    transaction_id="tx_12345",
    ml_score=0.95,
    zscore=3.2,
    alert_level="CRITICAL",
    merchant_id="merchant_abc",
    processing_time_ms=45
)

# Output JSON:
# {
#   "timestamp": "2025-01-25T10:30:00Z",
#   "level": "info",
#   "event": "anomaly_detected",
#   "transaction_id": "tx_12345",
#   "ml_score": 0.95,
#   "zscore": 3.2,
#   "alert_level": "CRITICAL",
#   "merchant_id": "merchant_abc",
#   "processing_time_ms": 45
# }
```

### 4.3. Métricas de Negócio (Custom Prometheus)

```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de negócio
TRANSACTIONS_TOTAL = Counter(
    'transactions_total',
    'Total de transações processadas',
    ['status', 'merchant_type']
)

ANOMALIES_DETECTED = Counter(
    'anomalies_detected_total',
    'Total de anomalias detectadas',
    ['alert_level', 'detection_method']
)

DETECTION_LATENCY = Histogram(
    'detection_latency_seconds',
    'Latência da detecção de anomalias',
    buckets=[.01, .025, .05, .075, .1, .25, .5, .75, 1.0]
)

ML_MODEL_SCORE = Histogram(
    'ml_model_score',
    'Distribuição dos scores do modelo ML',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

QUEUE_SIZE = Gauge(
    'processing_queue_size',
    'Tamanho atual da fila de processamento'
)

# Uso
@DETECTION_LATENCY.time()
async def process_transaction(txn):
    result = await detect_anomaly(txn)
    
    TRANSACTIONS_TOTAL.labels(
        status=txn["status"],
        merchant_type=txn.get("merchant_type", "unknown")
    ).inc()
    
    if result["is_anomaly"]:
        ANOMALIES_DETECTED.labels(
            alert_level=result["alert_level"],
            detection_method=result["primary_method"]
        ).inc()
    
    ML_MODEL_SCORE.observe(result["ml_score"])
```

### 4.4. SLOs e Error Budgets

```yaml
# slo-config.yaml
slos:
  - name: "API Availability"
    target: 99.9%
    window: 30d
    indicator:
      type: availability
      good_events: "sum(rate(http_requests_total{status!~'5..'}[5m]))"
      total_events: "sum(rate(http_requests_total[5m]))"

  - name: "Detection Latency"
    target: 95%
    window: 30d
    indicator:
      type: latency
      threshold: 200ms
      good_events: "sum(rate(detection_latency_seconds_bucket{le='0.2'}[5m]))"
      total_events: "sum(rate(detection_latency_seconds_count[5m]))"

  - name: "False Positive Rate"
    target: 98%
    window: 7d
    indicator:
      type: quality
      description: "Taxa de verdadeiros positivos nas detecções"
```

---

## 5. Qualidade e DevOps (CI/CD)

### 5.1. Pipeline GitHub Actions

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==================== QUALITY CHECKS ====================
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install ruff mypy
          
      - name: Lint with Ruff
        run: ruff check .
        
      - name: Type check with MyPy
        run: mypy --strict src/

  # ==================== TESTS ====================
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: timescale/timescaledb:latest-pg15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
          
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
        
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=80
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  # ==================== SECURITY SCAN ====================
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          
      - name: Run Bandit security linter
        run: |
          pip install bandit
          bandit -r src/ -ll

  # ==================== BUILD & PUSH ====================
  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ==================== DEPLOY ====================
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/transaction-guardian \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          kubectl rollout status deployment/transaction-guardian
```

### 5.2. Testes de Integração com Containers

```python
# tests/integration/test_api.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from httpx import AsyncClient

@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("timescale/timescaledb:latest-pg15") as pg:
        yield pg.get_connection_url()

@pytest.fixture(scope="module")
def redis():
    with RedisContainer() as r:
        yield r.get_connection_url()

@pytest.fixture
async def client(postgres, redis):
    app.state.db_url = postgres
    app.state.redis_url = redis
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_transaction_flow(client):
    # Criar transação
    response = await client.post("/transaction", json={
        "status": "approved",
        "amount": 100.00,
        "merchant_id": "test_merchant"
    })
    assert response.status_code == 202
    
    txn_id = response.json()["transaction_id"]
    
    # Verificar processamento
    await asyncio.sleep(1)  # Aguardar worker
    
    result = await client.get(f"/transaction/{txn_id}")
    assert result.json()["processed"] == True
```

### 5.3. Canary Deployments

```yaml
# kubernetes/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: transaction-guardian
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: {duration: 5m}
        - setWeight: 20
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: transaction-guardian
            
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.99
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

---

## 6. Incident Management

### 6.1. Incident Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INCIDENT LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐│
│  │ DETECT   │──▶│  TRIAGE  │──▶│ RESPOND  │──▶│ RESOLVE  │──▶│POSTMORT││
│  │          │   │          │   │          │   │          │   │        ││
│  │ • Alerts │   │ • P1-P4  │   │ • Runbook│   │ • Fix    │   │• RCA   ││
│  │ • Monitor│   │ • Assign │   │ • Escalar│   │ • Deploy │   │• Action││
│  │ • User   │   │ • Comm   │   │ • Mitigar│   │ • Verify │   │• Learn ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └────────┘│
│       │              │              │              │              │     │
│       │              │              │              │              │     │
│    < 5min         < 10min        < 30min        < 4hrs         < 48hrs │
│     MTTD          Classify        MTTR          Resolution    Postmortem│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2. Métricas de Incidente (SRE)

| Métrica | Target | Descrição |
|---------|--------|-----------|
| **MTTD** (Mean Time to Detect) | < 5 min | Tempo até o alerta disparar |
| **MTTA** (Mean Time to Acknowledge) | < 10 min | Tempo até alguém responder |
| **MTTR** (Mean Time to Resolve) | < 30 min (P1) | Tempo até resolver |
| **MTBF** (Mean Time Between Failures) | > 30 dias | Tempo entre incidentes |

### 6.3. Runbook Automation

```python
# runbooks/high_error_rate.py
"""
Runbook: Alta Taxa de Erros
Trigger: error_rate > 5% por 5 minutos
"""

async def execute_runbook(alert: Alert) -> RunbookResult:
    steps = []
    
    # Step 1: Coletar informações
    steps.append(await collect_diagnostics())
    
    # Step 2: Verificar dependências
    deps_status = await check_dependencies()
    if deps_status.has_failure:
        steps.append(await restart_failed_dependency(deps_status))
    
    # Step 3: Escalar se necessário
    if alert.duration > timedelta(minutes=15):
        await pagerduty.escalate(alert)
        steps.append("Escalated to on-call engineer")
    
    # Step 4: Auto-remediation
    if alert.error_type == "database_connection":
        await restart_connection_pool()
        steps.append("Restarted database connection pool")
    
    return RunbookResult(
        success=True,
        steps=steps,
        duration=timer.elapsed()
    )
```

### 6.4. On-Call Rotation

```yaml
# pagerduty-config.yaml
schedules:
  - name: "Transaction Guardian On-Call"
    timezone: "America/Sao_Paulo"
    layers:
      - name: "Primary"
        rotation_type: "weekly"
        start: "2025-01-01T00:00:00"
        users:
          - sergio@company.com
          - engineer2@company.com
          - engineer3@company.com
      
      - name: "Secondary (Escalation)"
        rotation_type: "weekly"
        start: "2025-01-01T00:00:00"
        users:
          - tech-lead@company.com
          - manager@company.com

escalation_policies:
  - name: "Transaction Guardian"
    rules:
      - escalation_delay_in_minutes: 5
        targets:
          - type: "schedule"
            id: "primary"
      - escalation_delay_in_minutes: 15
        targets:
          - type: "schedule"
            id: "secondary"
      - escalation_delay_in_minutes: 30
        targets:
          - type: "user"
            id: "cto@company.com"
```

---

## 7. Infraestrutura como Código

### 7.1. Docker Compose v2.0

```yaml
# docker-compose.v2.yml
version: '3.8'

services:
  # ============ API ============
  api:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@timescaledb:5432/guardian
      - REDIS_URL=redis://redis:6379
      - KAFKA_BROKERS=kafka:9092
      - OTEL_EXPORTER_JAEGER_ENDPOINT=http://jaeger:14268/api/traces
    depends_on:
      - timescaledb
      - redis
      - kafka
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  # ============ WORKERS ============
  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - KAFKA_BROKERS=kafka:9092
      - DATABASE_URL=postgresql://user:pass@timescaledb:5432/guardian
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      - kafka
      - timescaledb
    deploy:
      replicas: 5

  # ============ DATA LAYER ============
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=guardian
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      - ZOOKEEPER_CLIENT_PORT=2181

  # ============ OBSERVABILITY ============
  prometheus:
    image: prom/prometheus:v2.47.0
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:10.1.0
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"

  jaeger:
    image: jaegertracing/all-in-one:1.50
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Collector

  # ============ MLOPS ============
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    command: mlflow server --host 0.0.0.0 --port 5000
    volumes:
      - mlflow_data:/mlflow
    ports:
      - "5000:5000"

volumes:
  timescale_data:
  redis_data:
  prometheus_data:
  grafana_data:
  mlflow_data:
```

### 7.2. Kubernetes Manifests

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transaction-guardian-api
  labels:
    app: transaction-guardian
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transaction-guardian
      component: api
  template:
    metadata:
      labels:
        app: transaction-guardian
        component: api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api
          image: ghcr.io/company/transaction-guardian:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: guardian-secrets
                  key: database-url
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: transaction-guardian-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transaction-guardian-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
```

---

## 8. Roadmap de Implementação

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

### Fase 5: Observability (1-2 semanas)
- [ ] Integrar OpenTelemetry
- [ ] Configurar Jaeger
- [ ] Definir SLOs
- [ ] Criar dashboards de SLI

---

## 9. Referências

- [The Twelve-Factor App](https://12factor.net/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [MLOps: Continuous delivery for ML](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

## 📝 Notas Finais

Este documento representa a evolução natural do Transaction Guardian de uma PoC para um sistema de produção enterprise-grade. As melhorias foram priorizadas considerando:

1. **Impacto na vaga CloudWalk**: Foco em observabilidade e incident management
2. **Custo-benefício**: Começar com melhorias de maior ROI
3. **Complexidade incremental**: Evitar big-bang, preferir evolução gradual

> *"A system is never finished, only released."*

---

**Versão:** 2.0  
**Última atualização:** Janeiro 2025  
**Próxima revisão:** Abril 2025

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
