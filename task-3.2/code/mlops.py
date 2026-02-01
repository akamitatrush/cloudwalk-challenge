"""
🧠 MLOps Module
===============
Phase 4: MLOps - Transaction Guardian

Features:
- Model versioning with MLflow
- Experiment tracking
- Model registry
- Auto-retrain triggers
"""

import os
import json
import pickle
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import numpy as np

# MLflow imports
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️ MLflow not installed. Running without MLOps features.")

from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score


# ============== CONFIGURATION ==============

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://guardian-mlflow:5000")
EXPERIMENT_NAME = "transaction-guardian-anomaly"
MODEL_NAME = "anomaly-detector"


# ============== MLOPS MANAGER ==============

class MLOpsManager:
    """Gerencia ciclo de vida de modelos ML"""
    
    def __init__(self):
        self.client = None
        self.experiment_id = None
        self.connected = False
        
        if MLFLOW_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Conecta ao MLflow server"""
        try:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            self.client = MlflowClient()
            
            # Criar ou obter experimento
            experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
            else:
                self.experiment_id = experiment.experiment_id
            
            mlflow.set_experiment(EXPERIMENT_NAME)
            self.connected = True
            print(f"✅ MLflow conectado: {MLFLOW_TRACKING_URI}")
            print(f"📊 Experiment: {EXPERIMENT_NAME} (ID: {self.experiment_id})")
        except Exception as e:
            print(f"⚠️ MLflow não disponível: {e}")
            self.connected = False
    
    def train_model(
        self,
        X_train: np.ndarray,
        params: Dict[str, Any] = None,
        tags: Dict[str, str] = None
    ) -> Tuple[IsolationForest, str]:
        """
        Treina modelo e registra no MLflow.
        
        Returns:
            Tuple[model, run_id]
        """
        default_params = {
            "n_estimators": 100,
            "contamination": 0.1,
            "max_samples": "auto",
            "random_state": 42
        }
        
        if params:
            default_params.update(params)
        
        model = IsolationForest(**default_params)
        
        if not self.connected:
            model.fit(X_train)
            return model, None
        
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_params(default_params)
            
            # Log tags
            if tags:
                mlflow.set_tags(tags)
            mlflow.set_tag("model_type", "IsolationForest")
            mlflow.set_tag("phase", "training")
            
            # Train
            model.fit(X_train)
            
            # Log metrics
            train_scores = model.decision_function(X_train)
            train_predictions = model.predict(X_train)
            
            anomaly_ratio = (train_predictions == -1).sum() / len(train_predictions)
            mlflow.log_metric("anomaly_ratio", anomaly_ratio)
            mlflow.log_metric("mean_score", float(np.mean(train_scores)))
            mlflow.log_metric("std_score", float(np.std(train_scores)))
            mlflow.log_metric("training_samples", len(X_train))
            
            # Log model
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=MODEL_NAME
            )
            
            print(f"✅ Modelo treinado e registrado: {run.info.run_id}")
            return model, run.info.run_id
    
    def evaluate_model(
        self,
        model: IsolationForest,
        X_test: np.ndarray,
        y_true: np.ndarray = None,
        run_id: str = None
    ) -> Dict[str, float]:
        """
        Avalia modelo e registra métricas.
        """
        predictions = model.predict(X_test)
        scores = model.decision_function(X_test)
        
        metrics = {
            "test_samples": len(X_test),
            "anomaly_ratio": float((predictions == -1).sum() / len(predictions)),
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores))
        }
        
        # Se temos labels reais
        if y_true is not None:
            # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
            pred_binary = (predictions == -1).astype(int)
            
            metrics["precision"] = float(precision_score(y_true, pred_binary, zero_division=0))
            metrics["recall"] = float(recall_score(y_true, pred_binary, zero_division=0))
            metrics["f1_score"] = float(f1_score(y_true, pred_binary, zero_division=0))
        
        # Log to MLflow if connected
        if self.connected and run_id:
            with mlflow.start_run(run_id=run_id):
                for key, value in metrics.items():
                    mlflow.log_metric(f"eval_{key}", value)
        
        return metrics
    
    def load_production_model(self) -> Optional[IsolationForest]:
        """Carrega modelo em produção do registry"""
        if not self.connected:
            return None
        
        try:
            model_uri = f"models:/{MODEL_NAME}/Production"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"✅ Modelo de produção carregado: {MODEL_NAME}")
            return model
        except Exception as e:
            print(f"⚠️ Modelo de produção não encontrado: {e}")
            return None
    
    def load_latest_model(self) -> Optional[IsolationForest]:
        """Carrega versão mais recente do modelo"""
        if not self.connected:
            return None
        
        try:
            model_uri = f"models:/{MODEL_NAME}/latest"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"✅ Modelo mais recente carregado: {MODEL_NAME}")
            return model
        except Exception as e:
            print(f"⚠️ Nenhum modelo encontrado: {e}")
            return None
    
    def promote_to_production(self, version: int) -> bool:
        """Promove versão do modelo para produção"""
        if not self.connected:
            return False
        
        try:
            self.client.transition_model_version_stage(
                name=MODEL_NAME,
                version=version,
                stage="Production",
                archive_existing_versions=True
            )
            print(f"✅ Modelo v{version} promovido para Production")
            return True
        except Exception as e:
            print(f"❌ Erro ao promover modelo: {e}")
            return False
    
    def list_model_versions(self) -> List[Dict]:
        """Lista todas as versões do modelo"""
        if not self.connected:
            return []
        
        try:
            versions = self.client.search_model_versions(f"name='{MODEL_NAME}'")
            return [
                {
                    "version": v.version,
                    "stage": v.current_stage,
                    "status": v.status,
                    "created_at": v.creation_timestamp,
                    "run_id": v.run_id
                }
                for v in versions
            ]
        except Exception as e:
            print(f"⚠️ Erro ao listar versões: {e}")
            return []
    
    def get_experiment_runs(self, max_results: int = 10) -> List[Dict]:
        """Lista runs do experimento"""
        if not self.connected:
            return []
        
        try:
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                max_results=max_results,
                order_by=["start_time DESC"]
            )
            return runs.to_dict(orient="records")
        except Exception as e:
            print(f"⚠️ Erro ao listar runs: {e}")
            return []
    
    def check_model_drift(
        self,
        current_metrics: Dict[str, float],
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Verifica se houve drift no modelo.
        Compara métricas atuais com baseline.
        """
        result = {
            "drift_detected": False,
            "metrics_comparison": {},
            "recommendation": "OK"
        }
        
        if not self.connected:
            return result
        
        try:
            # Pegar métricas do último run de produção
            versions = self.client.search_model_versions(f"name='{MODEL_NAME}'")
            prod_versions = [v for v in versions if v.current_stage == "Production"]
            
            if not prod_versions:
                return result
            
            prod_run_id = prod_versions[0].run_id
            prod_run = self.client.get_run(prod_run_id)
            baseline_metrics = prod_run.data.metrics
            
            # Comparar métricas
            for key, current_value in current_metrics.items():
                baseline_key = f"eval_{key}" if not key.startswith("eval_") else key
                if baseline_key in baseline_metrics:
                    baseline_value = baseline_metrics[baseline_key]
                    diff = abs(current_value - baseline_value) / (baseline_value + 1e-10)
                    
                    result["metrics_comparison"][key] = {
                        "current": current_value,
                        "baseline": baseline_value,
                        "diff_pct": diff * 100
                    }
                    
                    if diff > threshold:
                        result["drift_detected"] = True
            
            if result["drift_detected"]:
                result["recommendation"] = "🔄 RETRAIN: Model drift detected. Consider retraining."
            
            return result
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar drift: {e}")
            return result
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do MLOps"""
        return {
            "connected": self.connected,
            "tracking_uri": MLFLOW_TRACKING_URI,
            "experiment_name": EXPERIMENT_NAME,
            "experiment_id": self.experiment_id,
            "model_name": MODEL_NAME,
            "model_versions": len(self.list_model_versions())
        }


# ============== SINGLETON ==============

_mlops_manager: Optional[MLOpsManager] = None

def get_mlops() -> MLOpsManager:
    """Retorna instância singleton do MLOpsManager"""
    global _mlops_manager
    if _mlops_manager is None:
        _mlops_manager = MLOpsManager()
    return _mlops_manager
