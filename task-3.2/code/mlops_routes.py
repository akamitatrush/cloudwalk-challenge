"""
🧠 MLOps Routes
===============
Phase 4: MLOps - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import numpy as np

from .mlops import get_mlops, MLOpsManager
from .auth import get_current_user, require_permission

router = APIRouter(prefix="/mlops", tags=["MLOps"])


# ============== MODELS ==============

class TrainRequest(BaseModel):
    n_estimators: int = 100
    contamination: float = 0.1
    description: Optional[str] = None

class PromoteRequest(BaseModel):
    version: int


# ============== ENDPOINTS ==============

@router.get("/status")
async def mlops_status():
    """📊 Status do MLOps e MLflow"""
    mlops = get_mlops()
    return mlops.get_status()


@router.get("/models")
async def list_models():
    """📋 Lista todas as versões do modelo"""
    mlops = get_mlops()
    versions = mlops.list_model_versions()
    return {
        "model_name": "anomaly-detector",
        "total_versions": len(versions),
        "versions": versions
    }


@router.get("/experiments")
async def list_experiments(limit: int = 10):
    """📊 Lista runs do experimento"""
    mlops = get_mlops()
    runs = mlops.get_experiment_runs(max_results=limit)
    return {
        "experiment": "transaction-guardian-anomaly",
        "total_runs": len(runs),
        "runs": runs
    }


@router.post("/train")
async def train_model(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_permission("admin"))
):
    """
    🎯 Treina novo modelo (apenas admin).
    
    O treino roda em background.
    """
    mlops = get_mlops()
    
    if not mlops.connected:
        raise HTTPException(
            status_code=503,
            detail="MLflow não está disponível"
        )
    
    # Gerar dados sintéticos para treino (em produção, usar dados reais)
    np.random.seed(42)
    X_train = np.random.randn(1000, 5)  # 1000 samples, 5 features
    
    # Adicionar algumas anomalias
    X_anomalies = np.random.uniform(low=-4, high=4, size=(50, 5))
    X_train = np.vstack([X_train, X_anomalies])
    
    params = {
        "n_estimators": request.n_estimators,
        "contamination": request.contamination
    }
    
    tags = {
        "triggered_by": user.get("username", "api"),
        "description": request.description or "API training"
    }
    
    model, run_id = mlops.train_model(X_train, params, tags)
    
    return {
        "status": "success",
        "message": "Modelo treinado e registrado",
        "run_id": run_id,
        "params": params
    }


@router.post("/promote")
async def promote_model(
    request: PromoteRequest,
    user: dict = Depends(require_permission("admin"))
):
    """
    🚀 Promove modelo para produção (apenas admin).
    """
    mlops = get_mlops()
    
    if not mlops.connected:
        raise HTTPException(
            status_code=503,
            detail="MLflow não está disponível"
        )
    
    success = mlops.promote_to_production(request.version)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao promover modelo v{request.version}"
        )
    
    return {
        "status": "success",
        "message": f"Modelo v{request.version} promovido para Production",
        "promoted_by": user.get("username", "unknown")
    }


@router.get("/drift")
async def check_drift():
    """
    🔍 Verifica drift do modelo.
    
    Compara métricas atuais com baseline de produção.
    """
    mlops = get_mlops()
    
    if not mlops.connected:
        return {
            "drift_detected": False,
            "message": "MLflow não disponível para verificação de drift"
        }
    
    # Métricas simuladas (em produção, calcular com dados reais)
    current_metrics = {
        "anomaly_ratio": 0.12,
        "mean_score": -0.15,
        "std_score": 0.08
    }
    
    result = mlops.check_model_drift(current_metrics)
    return result


@router.get("/health")
async def mlops_health():
    """❤️ Health check do MLOps"""
    mlops = get_mlops()
    
    return {
        "status": "healthy" if mlops.connected else "degraded",
        "mlflow_connected": mlops.connected,
        "tracking_uri": "http://guardian-mlflow:5000"
    }
