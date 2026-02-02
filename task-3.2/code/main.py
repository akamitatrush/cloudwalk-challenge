"""
🛡️ Transaction Guardian API v2.0
=================================
CloudWalk Monitoring Intelligence - Task 3.2

Phase 2: Performance
- Redis Cache integration
- Rate Limiting
- Circuit Breaker ready

Author: Sérgio (Candidate for Monitoring Intelligence Analyst)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import sys
import os

# Import local modules
from .anomaly_detector import AnomalyDetector
from .alert_manager import AlertManager
from .cache import get_cache, RedisCache
from .auth_routes import router as auth_router
from .mlops_routes import router as mlops_router
from .telegram_bot import send_anomaly_alert, get_bot
from .telegram_routes import router as telegram_router
from .ai_summary_routes import router as ai_router
from .shugo_routes import router as shugo_router
from .shugo import get_shugo
from .auth import get_optional_user

# ============== FASTAPI APP ==============

app = FastAPI(
    title="🛡️ Transaction Guardian",
    description="""
## CloudWalk Monitoring Intelligence Challenge - Task 3.2

Sistema de monitoramento de transações em tempo real com detecção de anomalias.

### 🎯 Funcionalidades:
- **POST /transaction** - Recebe dados de transação e retorna análise
- **POST /transactions/batch** - Processa múltiplas transações
- **GET /anomalies** - Lista anomalias detectadas
- **GET /metrics** - Métricas Prometheus
- **GET /health** - Health check
- **GET /stream** - SSE real-time updates

### 🚀 Phase 2 Features:
- **Redis Cache** - Respostas em cache para performance
- **Rate Limiting** - Proteção contra abuso (100 req/min)
- **Cache Stats** - Métricas de cache (GET /cache/stats)

### 🔐 Phase 3 Features:
- **JWT Authentication** - Login com token (POST /auth/login)
- **API Key** - Autenticação por chave (X-API-Key header)
- **Role-based Access** - Controle por permissões (admin, operator, viewer)

### 🔍 Métodos de Detecção:
- **Machine Learning**: Isolation Forest
- **Rule-based**: Thresholds configuráveis
- **Statistical**: Z-Score analysis
    """,
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include auth routes (Phase 3)
app.include_router(auth_router)
app.include_router(mlops_router)
app.include_router(telegram_router)
app.include_router(ai_router)
app.include_router(shugo_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# Include auth routes (Phase 3)
app.include_router(auth_router)

# ============== GLOBAL STATE ==============

class AppState:
    def __init__(self):
        self.detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        self.cache: RedisCache = None
        self.start_time = datetime.now()
        self.transactions_processed = 0
        self.anomalies_detected = 0
        self.recent_transactions: List[Dict] = []
        self.recent_anomalies: List[Dict] = []
        self.sse_clients: List[asyncio.Queue] = []
        
        self.metrics = {
            "total_transactions": 0,
            "total_anomalies": 0,
            "status_counts": {"approved": 0, "denied": 0, "failed": 0, "reversed": 0, "refunded": 0},
            "current_count": 0,
            "avg_count": 0,
            "approval_rate": 0,
        }

state = AppState()

# ============== MODELS ==============

class TransactionStatus(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    FAILED = "failed"
    REVERSED = "reversed"
    REFUNDED = "refunded"

class TransactionInput(BaseModel):
    timestamp: Optional[str] = Field(None, description="Timestamp da transação")
    status: TransactionStatus = Field(..., description="Status da transação")
    count: int = Field(default=1, ge=0, description="Número de transações")
    auth_code: Optional[str] = Field(default="00", description="Código de autorização")

class BatchInput(BaseModel):
    transactions: List[TransactionInput]

class AnomalyResponse(BaseModel):
    is_anomaly: bool
    alert_level: str
    anomaly_score: float
    rule_violations: List[str]
    recommendation: str
    metrics: Dict[str, Any]
    cached: bool = False

# ============== HELPERS ==============

def update_metrics(status: str, count: int, is_anomaly: bool):
    state.metrics["total_transactions"] += 1
    state.metrics["status_counts"][status] = state.metrics["status_counts"].get(status, 0) + 1
    state.metrics["current_count"] = count
    
    if is_anomaly:
        state.metrics["total_anomalies"] += 1
    
    total = state.metrics["total_transactions"]
    approved = state.metrics["status_counts"].get("approved", 0)
    state.metrics["approval_rate"] = round(approved / max(total, 1), 4)
    
    if state.recent_transactions:
        counts = [t.get("count", 0) for t in state.recent_transactions[-100:]]
        state.metrics["avg_count"] = sum(counts) / len(counts)

async def broadcast_event(event_type: str, data: dict):
    for queue in state.sse_clients:
        await queue.put({"type": event_type, "data": data})

# ============== RATE LIMIT MIDDLEWARE ==============

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    if state.cache and state.cache.connected:
        rate_check = state.cache.check_rate_limit(client_id=client_ip, limit=100, window=60)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_check["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_check["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_check["reset_in"])
        
        if not rate_check["allowed"]:
            return Response(
                content=json.dumps({"error": "Rate limit exceeded", "retry_after": rate_check["reset_in"]}),
                status_code=429,
                media_type="application/json"
            )
        return response
    
    return await call_next(request)

# ============== ENDPOINTS ==============

@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "🛡️ Transaction Guardian",
        "version": "2.0.0",
        "phase": "Phase 2 - Performance",
        "cache": "Redis" if (state.cache and state.cache.connected) else "Disabled",
        "endpoints": {"docs": "/docs", "health": "/health", "transaction": "/transaction", "cache_stats": "/cache/stats"}
    }

@app.get("/health", tags=["Health"])
async def health_check():
    cache_status = "healthy" if (state.cache and state.cache.connected) else "disconnected"
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - state.start_time).total_seconds(),
        "components": {"api": "healthy", "detector": "healthy", "cache": cache_status},
        "version": "2.0.0"
    }

@app.post("/transaction", response_model=AnomalyResponse, tags=["Transactions"])
async def analyze_transaction(tx: TransactionInput, background_tasks: BackgroundTasks):
    tx_data = {
        "timestamp": tx.timestamp or datetime.now().isoformat(),
        "status": tx.status.value,
        "count": tx.count,
        "auth_code": tx.auth_code
    }
    
    # Check cache
    if state.cache and state.cache.connected:
        cached_result = state.cache.get_transaction_result(tx_data)
        if cached_result:
            cached_result["cached"] = True
            return AnomalyResponse(**cached_result)
    
    # Process
    historical = [t.get("count", 100) for t in state.recent_transactions[-50:]] or [100]
    result = state.detector.analyze(
        current_count=tx.count,
        status=tx.status.value,
        auth_code=tx.auth_code,
        historical_counts=historical
    )
    
    state.transactions_processed += 1
    state.recent_transactions.append(tx_data)
    if len(state.recent_transactions) > 1000:
        state.recent_transactions = state.recent_transactions[-500:]
    
    update_metrics(tx.status.value, tx.count, result["is_anomaly"])
    
    # Alimentar Shugo com observação
    get_shugo().add_observation(datetime.now(), tx.count, tx.status.value)
    
    if result["is_anomaly"]:
        state.anomalies_detected += 1
        anomaly_record = {
            "timestamp": tx_data["timestamp"],
            "alert_level": result["alert_level"],
            "score": result["anomaly_score"],
            "violations": result["rule_violations"],
            "transaction": tx_data
        }
        state.recent_anomalies.append(anomaly_record)
        if len(state.recent_anomalies) > 100:
            state.recent_anomalies = state.recent_anomalies[-50:]
        background_tasks.add_task(broadcast_event, "anomaly", anomaly_record)
        # Enviar alerta Telegram para CRITICAL e WARNING
        if result["alert_level"] in ["CRITICAL", "WARNING"]:
            background_tasks.add_task(send_anomaly_alert, result["alert_level"], result["anomaly_score"], {"current_count": tx.count, "running_mean": result["metrics"].get("running_mean", 100), "rule_violations": result["rule_violations"]})
    
    response_data = {
        "is_anomaly": result["is_anomaly"],
        "alert_level": result["alert_level"],
        "anomaly_score": result["anomaly_score"],
        "rule_violations": result["rule_violations"],
        "recommendation": result["recommendation"],
        "metrics": result["metrics"],
        "cached": False
    }
    
    # Save to cache
    if state.cache and state.cache.connected:
        state.cache.set_transaction_result(tx_data, response_data, ttl=60)
    
    return AnomalyResponse(**response_data)

@app.post("/transactions/batch", tags=["Transactions"])
async def analyze_batch(batch: BatchInput, background_tasks: BackgroundTasks):
    results = []
    anomaly_count = 0
    cache_hits = 0
    
    for tx in batch.transactions:
        tx_data = {"timestamp": tx.timestamp or datetime.now().isoformat(), "status": tx.status.value, "count": tx.count, "auth_code": tx.auth_code}
        
        cached = state.cache.get_transaction_result(tx_data) if (state.cache and state.cache.connected) else None
        if cached:
            cache_hits += 1
            if cached.get("is_anomaly"): anomaly_count += 1
            results.append({"timestamp": tx_data["timestamp"], "is_anomaly": cached["is_anomaly"], "alert_level": cached["alert_level"], "score": cached["anomaly_score"], "cached": True})
            continue
        
        historical = [t.get("count", 100) for t in state.recent_transactions[-50:]] or [100]
        result = state.detector.analyze(current_count=tx.count, status=tx.status.value, auth_code=tx.auth_code, historical_counts=historical)
        
        state.transactions_processed += 1
        state.recent_transactions.append(tx_data)
        update_metrics(tx.status.value, tx.count, result["is_anomaly"])
        
        if result["is_anomaly"]:
            anomaly_count += 1
            state.anomalies_detected += 1
        
        if state.cache and state.cache.connected:
            state.cache.set_transaction_result(tx_data, {"is_anomaly": result["is_anomaly"], "alert_level": result["alert_level"], "anomaly_score": result["anomaly_score"], "rule_violations": result["rule_violations"], "recommendation": result["recommendation"], "metrics": result["metrics"]}, ttl=60)
        
        results.append({"timestamp": tx_data["timestamp"], "is_anomaly": result["is_anomaly"], "alert_level": result["alert_level"], "score": result["anomaly_score"], "cached": False})
    
    return {"processed": len(results), "anomalies_found": anomaly_count, "anomaly_rate": anomaly_count / max(len(results), 1), "cache_hits": cache_hits, "results": results}

@app.get("/anomalies", tags=["Monitoring"])
async def get_anomalies(limit: int = 50, level: Optional[str] = None):
    anomalies = state.recent_anomalies[-limit:]
    if level:
        anomalies = [a for a in anomalies if a["alert_level"] == level.upper()]
    return {"total": len(anomalies), "anomalies": list(reversed(anomalies))}

@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def get_prometheus_metrics():
    cache_hits = state.cache.stats["hits"] if state.cache else 0
    cache_misses = state.cache.stats["misses"] if state.cache else 0
    
    lines = [
        "# HELP transaction_guardian_total Total transactions",
        "# TYPE transaction_guardian_total counter",
        f"transaction_guardian_total {state.metrics['total_transactions']}",
        "",
        "# HELP transaction_guardian_anomalies Total anomalies",
        "# TYPE transaction_guardian_anomalies counter",
        f"transaction_guardian_anomalies {state.metrics['total_anomalies']}",
        "",
        "# HELP transaction_guardian_cache_hits Cache hits",
        "# TYPE transaction_guardian_cache_hits counter",
        f"transaction_guardian_cache_hits {cache_hits}",
        "",
        "# HELP transaction_guardian_cache_misses Cache misses", 
        "# TYPE transaction_guardian_cache_misses counter",
        f"transaction_guardian_cache_misses {cache_misses}",
        "",
        "# HELP transaction_guardian_current_count Current transaction count",
        "# TYPE transaction_guardian_current_count gauge",
        f"transaction_guardian_current_count {state.metrics['current_count']}",
        "",
        "# HELP transaction_guardian_approval_rate Approval rate",
        "# TYPE transaction_guardian_approval_rate gauge",
        f"transaction_guardian_approval_rate {state.metrics['approval_rate']}",
        "",
        "# HELP transaction_guardian_avg_count Average transaction count",
        "# TYPE transaction_guardian_avg_count gauge",
        f"transaction_guardian_avg_count {state.metrics['avg_count']}",
        "",
        "# HELP transaction_guardian_by_status Transactions by status",
        "# TYPE transaction_guardian_by_status counter",
    ]
    for status, count in state.metrics["status_counts"].items():
        lines.append(f'transaction_guardian_by_status{{status="{status}"}} {count}')
    return "\n".join(lines)

@app.get("/metrics/json", tags=["Monitoring"])
async def get_metrics_json():
    return state.metrics

# ============== CACHE ENDPOINTS ==============

@app.get("/cache/stats", tags=["Cache"])
async def get_cache_stats():
    if not state.cache:
        return {"error": "Cache não inicializado"}
    return state.cache.get_stats()

@app.delete("/cache/flush", tags=["Cache"])
async def flush_cache():
    if state.cache and state.cache.connected:
        state.cache.client.flushdb()
        return {"message": "Cache limpo"}
    return {"error": "Cache não disponível"}

# ============== OTHER ENDPOINTS ==============

@app.get("/stream", tags=["Real-time"])
async def sse_stream():
    async def event_generator():
        queue = asyncio.Queue()
        state.sse_clients.append(queue)
        try:
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected to Transaction Guardian v2.0'})}\n\n"
            while True:
                event = await queue.get()
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
        except asyncio.CancelledError:
            state.sse_clients.remove(queue)
            raise
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

@app.get("/stats", tags=["Monitoring"])
async def get_stats():
    if not state.recent_transactions:
        return {"message": "Nenhuma transação processada"}
    counts = [t["count"] for t in state.recent_transactions]
    return {
        "total_processed": state.transactions_processed,
        "total_anomalies": state.anomalies_detected,
        "anomaly_rate": state.anomalies_detected / max(state.transactions_processed, 1),
        "transaction_stats": {"min": min(counts), "max": max(counts), "avg": sum(counts) / len(counts)},
        "status_distribution": state.metrics["status_counts"],
        "cache": state.cache.get_stats() if state.cache else {"connected": False},
        "uptime_seconds": (datetime.now() - state.start_time).total_seconds()
    }

@app.post("/reset", tags=["Admin"])
async def reset_system():
    state.transactions_processed = 0
    state.anomalies_detected = 0
    state.recent_transactions.clear()
    state.recent_anomalies.clear()
    state.detector.reset()
    state.metrics = {"total_transactions": 0, "total_anomalies": 0, "status_counts": {"approved": 0, "denied": 0, "failed": 0, "reversed": 0, "refunded": 0}, "current_count": 0, "avg_count": 0, "approval_rate": 0}
    if state.cache and state.cache.connected:
        state.cache.client.flushdb()
    return {"message": "Sistema resetado"}

# ============== STARTUP ==============

@app.on_event("startup")
async def startup():
    print("🛡️ Transaction Guardian v2.0 iniciando...")
    state.cache = get_cache()
    if state.cache.connected:
        print("🚀 Redis cache conectado!")
    else:
        print("⚠️ Redis não disponível - cache desabilitado")
    print("✅ Sistema pronto!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
