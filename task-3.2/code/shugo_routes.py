"""
守護 SHUGO - API Routes
=======================
Phase 7: Prediction Engine Endpoints
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from .shugo import get_shugo, ShugoEngine

router = APIRouter(prefix="/shugo", tags=["🛡️ Shugo Prediction"])


@router.get("/status")
async def shugo_status():
    """🛡️ Status do Shugo Engine"""
    shugo = get_shugo()
    return shugo.get_status()


@router.get("/predict")
async def predict(minutes: int = 30):
    """
    🔮 Prevê volume para os próximos N minutos
    
    - **minutes**: Minutos no futuro (default: 30)
    """
    shugo = get_shugo()
    prediction = shugo.predict_next(minutes_ahead=minutes)
    
    return {
        "prediction": {
            "timestamp": prediction.timestamp.isoformat(),
            "predicted_volume": round(prediction.predicted_volume, 1),
            "confidence": round(prediction.confidence * 100, 1),
            "trend": prediction.trend,
            "alert_probability": round(prediction.alert_probability * 100, 1),
            "warning": prediction.warning_message
        }
    }


@router.get("/forecast")
async def forecast(hours: int = 6):
    """
    📈 Forecast para as próximas N horas
    
    - **hours**: Horas no futuro (default: 6)
    """
    shugo = get_shugo()
    forecasts = shugo.get_forecast(hours_ahead=hours)
    
    return {
        "forecast_hours": hours,
        "generated_at": datetime.now().isoformat(),
        "predictions": forecasts
    }


@router.get("/patterns")
async def detect_patterns():
    """🔍 Detecta padrões nos dados históricos"""
    shugo = get_shugo()
    patterns = shugo.detect_patterns()
    
    return {
        "patterns_detected": len(patterns),
        "patterns": [
            {
                "name": p.name,
                "description": p.description,
                "frequency": p.frequency,
                "confidence": round(p.confidence * 100, 1),
                "impact": p.impact
            }
            for p in patterns
        ]
    }


@router.get("/hourly-baseline")
async def hourly_baseline():
    """📊 Baseline por hora do dia"""
    shugo = get_shugo()
    
    baselines = {}
    for hour in range(24):
        mean, std = shugo.get_hourly_baseline(hour)
        baselines[f"{hour:02d}:00"] = {
            "mean": round(mean, 1),
            "std": round(std, 1),
            "data_points": len(shugo.hourly_patterns.get(hour, []))
        }
    
    return {"hourly_baselines": baselines}


@router.get("/daily-baseline")
async def daily_baseline():
    """📅 Baseline por dia da semana"""
    shugo = get_shugo()
    days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    baselines = {}
    for day in range(7):
        mean, std = shugo.get_daily_baseline(day)
        baselines[days[day]] = {
            "mean": round(mean, 1),
            "std": round(std, 1),
            "data_points": len(shugo.daily_patterns.get(day, []))
        }
    
    return {"daily_baselines": baselines}


@router.post("/train")
async def train_from_history():
    """
    🎯 Treina Shugo com dados históricos
    
    Popula os padrões com dados simulados para teste.
    """
    shugo = get_shugo()
    
    # Simular dados históricos para teste
    import random
    now = datetime.now()
    
    for i in range(500):
        # Timestamp aleatório nas últimas 24h
        ts = now - timedelta(hours=random.randint(0, 168))
        
        # Volume baseado na hora (padrão realista)
        hour = ts.hour
        if 9 <= hour <= 18:
            base_volume = 120  # Horário comercial
        elif 19 <= hour <= 23:
            base_volume = 80   # Noite
        else:
            base_volume = 40   # Madrugada
        
        volume = int(base_volume + random.gauss(0, 20))
        status = random.choice(["approved"] * 7 + ["denied"] * 2 + ["failed"])
        
        shugo.add_observation(ts, max(1, volume), status)
    
    return {
        "status": "trained",
        "observations_added": 500,
        "shugo_status": shugo.get_status()
    }
