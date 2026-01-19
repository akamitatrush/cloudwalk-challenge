"""
🛡️ Transaction Guardian API
============================
CloudWalk Monitoring Intelligence - Task 3.2

Real-time transaction monitoring with:
- ML-based anomaly detection (Isolation Forest)
- Rule-based threshold alerts
- Automatic notifications
- Prometheus metrics

Author: Sérgio (Candidate for Monitoring Intelligence Analyst)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
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

### 🔍 Métodos de Detecção:
- **Machine Learning**: Isolation Forest
- **Rule-based**: Thresholds configuráveis
- **Statistical**: Z-Score analysis
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== GLOBAL STATE ==============

class AppState:
    def __init__(self):
        self.detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        self.start_time = datetime.now()
        self.transactions_processed = 0
        self.anomalies_detected = 0
        self.recent_transactions: List[Dict] = []
        self.recent_anomalies: List[Dict] = []
        self.sse_clients: List[asyncio.Queue] = []
        
        # Metrics
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
    """Modelo de entrada para transação"""
    timestamp: Optional[str] = Field(default=None, description="Timestamp da transação")
    status: TransactionStatus = Field(..., description="Status da transação")
    count: int = Field(..., ge=0, description="Quantidade de transações")
    auth_code: Optional[str] = Field(default="00", description="Código de autorização")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-07-12T14:30:00",
                "status": "approved",
                "count": 125,
                "auth_code": "00"
            }
        }

class BatchInput(BaseModel):
    """Modelo para batch de transações"""
    transactions: List[TransactionInput]

class AnomalyResponse(BaseModel):
    """Resposta da análise de anomalia"""
    is_anomaly: bool
    alert_level: str
    anomaly_score: float
    rule_violations: List[str]
    recommendation: str
    metrics: Dict[str, Any]

# ============== HELPER FUNCTIONS ==============

def update_metrics(status: str, count: int, is_anomaly: bool):
    """Atualiza métricas globais"""
    state.metrics["total_transactions"] += 1
    state.metrics["status_counts"][status] = state.metrics["status_counts"].get(status, 0) + count
    state.metrics["current_count"] = count
    
    if is_anomaly:
        state.metrics["total_anomalies"] += 1
    
    # Calcular approval rate
    total = sum(state.metrics["status_counts"].values())
    if total > 0:
        state.metrics["approval_rate"] = state.metrics["status_counts"]["approved"] / total
    
    # Média móvel
    if state.recent_transactions:
        counts = [t.get("count", 0) for t in state.recent_transactions[-30:]]
        state.metrics["avg_count"] = sum(counts) / len(counts)

async def broadcast_sse(event_type: str, data: Dict):
    """Envia evento para todos os clientes SSE"""
    message = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
    for queue in state.sse_clients:
        try:
            await queue.put(message)
        except:
            pass

# ============== ENDPOINTS ==============

@app.get("/", tags=["Info"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "name": "🛡️ Transaction Guardian",
        "version": "1.0.0",
        "description": "CloudWalk Monitoring Intelligence - Task 3.2",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "transaction": "/transaction",
            "anomalies": "/anomalies",
            "metrics": "/metrics",
            "stream": "/stream"
        }
    }

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check com métricas atuais"""
    uptime = (datetime.now() - state.start_time).total_seconds()
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "transactions_processed": state.transactions_processed,
        "anomalies_detected": state.anomalies_detected,
        "metrics": state.metrics
    }

@app.post("/transaction", response_model=AnomalyResponse, tags=["Transactions"])
async def analyze_transaction(
    transaction: TransactionInput,
    background_tasks: BackgroundTasks
):
    """
    📊 Recebe uma transação e analisa se é anomalia.
    
    Retorna:
    - **is_anomaly**: Se a transação é anômala
    - **alert_level**: NORMAL, WARNING ou CRITICAL
    - **anomaly_score**: Score de anomalia (0-1)
    - **rule_violations**: Regras violadas
    - **recommendation**: Recomendação de ação
    """
    # Preparar dados
    tx_data = {
        "timestamp": transaction.timestamp or datetime.now().isoformat(),
        "status": transaction.status.value,
        "count": transaction.count,
        "auth_code": transaction.auth_code
    }
    
    # Histórico recente
    historical = [t.get("count", 100) for t in state.recent_transactions[-50:]]
    if not historical:
        historical = [100]  # Default
    
    # Analisar com detector
    result = state.detector.analyze(
        current_count=transaction.count,
        status=transaction.status.value,
        auth_code=transaction.auth_code,
        historical_counts=historical
    )
    
    # Atualizar estado
    state.transactions_processed += 1
    state.recent_transactions.append(tx_data)
    if len(state.recent_transactions) > 500:
        state.recent_transactions = state.recent_transactions[-300:]
    
    update_metrics(transaction.status.value, transaction.count, result["is_anomaly"])
    
    # Se anomalia, registrar e alertar
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
        
        # Enviar alerta em background
        background_tasks.add_task(
            state.alert_manager.send_alert,
            result["alert_level"],
            result["rule_violations"],
            result["anomaly_score"],
            tx_data
        )
    
    # Broadcast SSE
    background_tasks.add_task(
        broadcast_sse,
        "transaction",
        {
            "is_anomaly": result["is_anomaly"],
            "alert_level": result["alert_level"],
            "score": result["anomaly_score"],
            "count": transaction.count,
            "status": transaction.status.value
        }
    )
    
    return AnomalyResponse(
        is_anomaly=result["is_anomaly"],
        alert_level=result["alert_level"],
        anomaly_score=result["anomaly_score"],
        rule_violations=result["rule_violations"],
        recommendation=result["recommendation"],
        metrics=result["metrics"]
    )

@app.post("/transactions/batch", tags=["Transactions"])
async def analyze_batch(batch: BatchInput, background_tasks: BackgroundTasks):
    """
    📦 Processa múltiplas transações de uma vez.
    
    Útil para replay de dados históricos.
    """
    results = []
    anomaly_count = 0
    
    for tx in batch.transactions:
        # Processar cada transação
        historical = [t.get("count", 100) for t in state.recent_transactions[-50:]]
        if not historical:
            historical = [100]
        
        result = state.detector.analyze(
            current_count=tx.count,
            status=tx.status.value,
            auth_code=tx.auth_code,
            historical_counts=historical
        )
        
        tx_data = {
            "timestamp": tx.timestamp or datetime.now().isoformat(),
            "status": tx.status.value,
            "count": tx.count,
            "auth_code": tx.auth_code
        }
        
        state.transactions_processed += 1
        state.recent_transactions.append(tx_data)
        update_metrics(tx.status.value, tx.count, result["is_anomaly"])
        
        if result["is_anomaly"]:
            anomaly_count += 1
            state.anomalies_detected += 1
        
        results.append({
            "timestamp": tx_data["timestamp"],
            "is_anomaly": result["is_anomaly"],
            "alert_level": result["alert_level"],
            "score": result["anomaly_score"]
        })
    
    return {
        "processed": len(results),
        "anomalies_found": anomaly_count,
        "anomaly_rate": anomaly_count / max(len(results), 1),
        "results": results
    }

@app.get("/anomalies", tags=["Monitoring"])
async def get_anomalies(limit: int = 50, level: Optional[str] = None):
    """
    🚨 Lista anomalias detectadas recentemente.
    
    - **limit**: Número máximo de resultados
    - **level**: Filtrar por nível (WARNING, CRITICAL)
    """
    anomalies = state.recent_anomalies[-limit:]
    
    if level:
        anomalies = [a for a in anomalies if a["alert_level"] == level.upper()]
    
    return {
        "total": len(anomalies),
        "anomalies": list(reversed(anomalies))
    }

@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def get_prometheus_metrics():
    """
    📊 Métricas em formato Prometheus.
    """
    lines = [
        "# HELP transaction_guardian_total Total de transações processadas",
        "# TYPE transaction_guardian_total counter",
        f"transaction_guardian_total {state.metrics['total_transactions']}",
        "",
        "# HELP transaction_guardian_anomalies Total de anomalias detectadas",
        "# TYPE transaction_guardian_anomalies counter",
        f"transaction_guardian_anomalies {state.metrics['total_anomalies']}",
        "",
        "# HELP transaction_guardian_current_count Contagem atual de transações",
        "# TYPE transaction_guardian_current_count gauge",
        f"transaction_guardian_current_count {state.metrics['current_count']}",
        "",
        "# HELP transaction_guardian_avg_count Média de transações",
        "# TYPE transaction_guardian_avg_count gauge",
        f"transaction_guardian_avg_count {state.metrics['avg_count']}",
        "",
        "# HELP transaction_guardian_approval_rate Taxa de aprovação",
        "# TYPE transaction_guardian_approval_rate gauge",
        f"transaction_guardian_approval_rate {state.metrics['approval_rate']}",
        "",
        "# HELP transaction_guardian_by_status Transações por status",
        "# TYPE transaction_guardian_by_status counter",
    ]
    
    for status, count in state.metrics["status_counts"].items():
        lines.append(f'transaction_guardian_by_status{{status="{status}"}} {count}')
    
    return "\n".join(lines)

@app.get("/metrics/json", tags=["Monitoring"])
async def get_metrics_json():
    """Métricas em formato JSON"""
    return state.metrics

@app.get("/stream", tags=["Real-time"])
async def sse_stream():
    """
    📡 Server-Sent Events para atualizações em tempo real.
    
    Conecte para receber:
    - Novas transações
    - Alertas de anomalia
    """
    async def event_generator():
        queue = asyncio.Queue()
        state.sse_clients.append(queue)
        try:
            # Enviar evento inicial
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected to Transaction Guardian'})}\n\n"
            
            while True:
                event = await queue.get()
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
        except asyncio.CancelledError:
            state.sse_clients.remove(queue)
            raise
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/stats", tags=["Monitoring"])
async def get_stats():
    """📈 Estatísticas detalhadas do sistema"""
    if not state.recent_transactions:
        return {"message": "Nenhuma transação processada ainda"}
    
    counts = [t["count"] for t in state.recent_transactions]
    
    return {
        "total_processed": state.transactions_processed,
        "total_anomalies": state.anomalies_detected,
        "anomaly_rate": state.anomalies_detected / max(state.transactions_processed, 1),
        "transaction_stats": {
            "min": min(counts),
            "max": max(counts),
            "avg": sum(counts) / len(counts),
            "window_size": len(counts)
        },
        "status_distribution": state.metrics["status_counts"],
        "uptime_seconds": (datetime.now() - state.start_time).total_seconds()
    }

@app.post("/reset", tags=["Admin"])
async def reset_system():
    """🔄 Reset do sistema (para testes)"""
    state.transactions_processed = 0
    state.anomalies_detected = 0
    state.recent_transactions.clear()
    state.recent_anomalies.clear()
    state.detector.reset()
    state.metrics = {
        "total_transactions": 0,
        "total_anomalies": 0,
        "status_counts": {"approved": 0, "denied": 0, "failed": 0, "reversed": 0, "refunded": 0},
        "current_count": 0,
        "avg_count": 0,
        "approval_rate": 0,
    }
    return {"message": "Sistema resetado com sucesso"}

# ============== STARTUP ==============

@app.on_event("startup")
async def startup():
    print("🛡️ Transaction Guardian iniciando...")
    print("📊 Detector de anomalias carregado")
    print("✅ Sistema pronto!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
