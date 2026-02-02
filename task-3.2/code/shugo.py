"""
守護 SHUGO - Prediction Engine
==============================
Phase 7: Predictive Anomaly Detection

"Vê o futuro, protege o presente"

Features:
- Time series forecasting
- Pattern recognition
- Seasonal detection
- Early warning alerts
"""

import os
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, field

SHUGO_LOGO = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   ███████╗██╗  ██╗██╗   ██╗ ██████╗  ██████╗         ║
║   ██╔════╝██║  ██║██║   ██║██╔════╝ ██╔═══██╗        ║
║   ███████╗███████║██║   ██║██║  ███╗██║   ██║        ║
║   ╚════██║██╔══██║██║   ██║██║   ██║██║   ██║        ║
║   ███████║██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝        ║
║   ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝         ║
║                                                       ║
║            守護 - PREDICTION ENGINE                   ║
║        "Vê o futuro, protege o presente"             ║
╚═══════════════════════════════════════════════════════╝
"""


@dataclass
class Prediction:
    """Resultado de uma predição"""
    timestamp: datetime
    predicted_volume: float
    confidence: float
    trend: str  # "up", "down", "stable"
    alert_probability: float
    warning_message: Optional[str] = None
    

@dataclass
class Pattern:
    """Padrão detectado"""
    name: str
    description: str
    frequency: str  # "hourly", "daily", "weekly"
    confidence: float
    impact: str  # "positive", "negative", "neutral"


class ShugoEngine:
    """
    守護 SHUGO - Prediction Engine
    
    Analisa padrões históricos e prevê anomalias
    antes que aconteçam.
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.history: deque = deque(maxlen=1000)
        self.hourly_patterns: Dict[int, List[float]] = {h: [] for h in range(24)}
        self.daily_patterns: Dict[int, List[float]] = {d: [] for d in range(7)}
        self.predictions: List[Prediction] = []
        self.detected_patterns: List[Pattern] = []
        
        print(SHUGO_LOGO)
        print("🛡️ Shugo Engine inicializado!")
    
    def add_observation(self, timestamp: datetime, volume: int, status: str) -> None:
        """Adiciona observação ao histórico"""
        observation = {
            "timestamp": timestamp,
            "volume": volume,
            "status": status,
            "hour": timestamp.hour,
            "weekday": timestamp.weekday()
        }
        self.history.append(observation)
        
        # Atualizar padrões
        self.hourly_patterns[timestamp.hour].append(volume)
        self.daily_patterns[timestamp.weekday()].append(volume)
        
        # Manter últimos 100 por padrão
        if len(self.hourly_patterns[timestamp.hour]) > 100:
            self.hourly_patterns[timestamp.hour] = self.hourly_patterns[timestamp.hour][-100:]
        if len(self.daily_patterns[timestamp.weekday()]) > 100:
            self.daily_patterns[timestamp.weekday()] = self.daily_patterns[timestamp.weekday()][-100:]
    
    def get_hourly_baseline(self, hour: int) -> Tuple[float, float]:
        """Retorna média e desvio padrão para uma hora específica"""
        data = self.hourly_patterns.get(hour, [])
        if len(data) < 5:
            return 100.0, 30.0  # Default
        return np.mean(data), np.std(data)
    
    def get_daily_baseline(self, weekday: int) -> Tuple[float, float]:
        """Retorna média e desvio padrão para um dia da semana"""
        data = self.daily_patterns.get(weekday, [])
        if len(data) < 5:
            return 100.0, 30.0  # Default
        return np.mean(data), np.std(data)
    
    def predict_next(self, minutes_ahead: int = 30) -> Prediction:
        """
        Prevê o volume para os próximos N minutos.
        
        Returns:
            Prediction com volume esperado e probabilidade de alerta
        """
        now = datetime.now()
        future_time = now + timedelta(minutes=minutes_ahead)
        future_hour = future_time.hour
        future_weekday = future_time.weekday()
        
        # Baseline por hora e dia
        hourly_mean, hourly_std = self.get_hourly_baseline(future_hour)
        daily_mean, daily_std = self.get_daily_baseline(future_weekday)
        
        # Peso: 60% hora, 40% dia
        predicted_volume = (hourly_mean * 0.6) + (daily_mean * 0.4)
        combined_std = (hourly_std * 0.6) + (daily_std * 0.4)
        
        # Calcular tendência baseado nas últimas observações
        trend = self._calculate_trend()
        
        # Ajustar predição pela tendência
        if trend == "up":
            predicted_volume *= 1.1
        elif trend == "down":
            predicted_volume *= 0.9
        
        # Calcular probabilidade de alerta
        alert_probability = self._calculate_alert_probability(
            predicted_volume, hourly_mean, hourly_std
        )
        
        # Calcular confiança
        data_points = len(self.hourly_patterns.get(future_hour, []))
        confidence = min(0.95, 0.5 + (data_points / 200))
        
        # Gerar warning se necessário
        warning = None
        if alert_probability > 0.7:
            warning = f"⚠️ ALERTA PREVISTO em {minutes_ahead}min: Alta probabilidade de anomalia"
        elif alert_probability > 0.5:
            warning = f"🔶 ATENÇÃO: Possível anomalia em {minutes_ahead}min"
        
        prediction = Prediction(
            timestamp=future_time,
            predicted_volume=predicted_volume,
            confidence=confidence,
            trend=trend,
            alert_probability=alert_probability,
            warning_message=warning
        )
        
        self.predictions.append(prediction)
        if len(self.predictions) > 100:
            self.predictions = self.predictions[-100:]
        
        return prediction
    
    def _calculate_trend(self) -> str:
        """Calcula tendência baseado nas últimas observações"""
        if len(self.history) < 10:
            return "stable"
        
        recent = list(self.history)[-10:]
        volumes = [o["volume"] for o in recent]
        
        # Regressão linear simples
        x = np.arange(len(volumes))
        slope = np.polyfit(x, volumes, 1)[0]
        
        if slope > 2:
            return "up"
        elif slope < -2:
            return "down"
        return "stable"
    
    def _calculate_alert_probability(
        self, predicted: float, mean: float, std: float
    ) -> float:
        """Calcula probabilidade de alerta baseado no desvio"""
        if std == 0:
            return 0.0
        
        # Quanto mais longe da média, maior a probabilidade
        z_score = abs(predicted - mean) / std
        
        # Converter z-score para probabilidade
        if z_score < 1:
            return 0.1
        elif z_score < 2:
            return 0.3
        elif z_score < 3:
            return 0.6
        else:
            return 0.9
    
    def detect_patterns(self) -> List[Pattern]:
        """Detecta padrões nos dados históricos"""
        patterns = []
        
        # Detectar padrão de horário de pico
        peak_hours = []
        for hour, volumes in self.hourly_patterns.items():
            if len(volumes) >= 10:
                mean = np.mean(volumes)
                overall_mean = np.mean([
                    np.mean(v) for v in self.hourly_patterns.values() 
                    if len(v) >= 5
                ] or [100])
                if mean > overall_mean * 1.3:
                    peak_hours.append(hour)
        
        if peak_hours:
            patterns.append(Pattern(
                name="Peak Hours",
                description=f"Alto volume detectado às {peak_hours}h",
                frequency="hourly",
                confidence=0.8,
                impact="neutral"
            ))
        
        # Detectar padrão de baixo volume
        low_hours = []
        for hour, volumes in self.hourly_patterns.items():
            if len(volumes) >= 10:
                mean = np.mean(volumes)
                overall_mean = np.mean([
                    np.mean(v) for v in self.hourly_patterns.values() 
                    if len(v) >= 5
                ] or [100])
                if mean < overall_mean * 0.5:
                    low_hours.append(hour)
        
        if low_hours:
            patterns.append(Pattern(
                name="Low Volume Hours",
                description=f"Baixo volume detectado às {low_hours}h",
                frequency="hourly",
                confidence=0.8,
                impact="negative"
            ))
        
        # Detectar padrão semanal
        weekday_means = {}
        for day, volumes in self.daily_patterns.items():
            if len(volumes) >= 5:
                weekday_means[day] = np.mean(volumes)
        
        if weekday_means:
            best_day = max(weekday_means, key=weekday_means.get)
            worst_day = min(weekday_means, key=weekday_means.get)
            days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            
            patterns.append(Pattern(
                name="Weekly Pattern",
                description=f"Melhor dia: {days[best_day]}, Pior dia: {days[worst_day]}",
                frequency="weekly",
                confidence=0.7,
                impact="neutral"
            ))
        
        self.detected_patterns = patterns
        return patterns
    
    def get_forecast(self, hours_ahead: int = 6) -> List[Dict]:
        """Gera forecast para as próximas N horas"""
        forecasts = []
        
        for minutes in range(0, hours_ahead * 60, 30):
            prediction = self.predict_next(minutes_ahead=minutes)
            forecasts.append({
                "time": prediction.timestamp.strftime("%H:%M"),
                "predicted_volume": round(prediction.predicted_volume, 1),
                "confidence": round(prediction.confidence * 100, 1),
                "trend": prediction.trend,
                "alert_probability": round(prediction.alert_probability * 100, 1),
                "warning": prediction.warning_message
            })
        
        return forecasts
    
    def get_status(self) -> Dict:
        """Retorna status do Shugo Engine"""
        return {
            "engine": "Shugo 守護",
            "version": "1.0.0",
            "observations": len(self.history),
            "patterns_detected": len(self.detected_patterns),
            "predictions_made": len(self.predictions),
            "hourly_coverage": sum(1 for h in self.hourly_patterns.values() if len(h) >= 5),
            "daily_coverage": sum(1 for d in self.daily_patterns.values() if len(d) >= 5),
            "status": "ready" if len(self.history) >= 50 else "warming_up"
        }


# Singleton
_shugo: Optional[ShugoEngine] = None

def get_shugo() -> ShugoEngine:
    """Retorna instância singleton do Shugo"""
    global _shugo
    if _shugo is None:
        _shugo = ShugoEngine()
    return _shugo
