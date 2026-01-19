"""
🔍 Anomaly Detector
===================
Detecção híbrida de anomalias:
- Machine Learning (Isolation Forest)
- Rule-based (thresholds)
- Statistical (Z-Score)

CloudWalk Task 3.2
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# ============== CONFIGURATION ==============

@dataclass
class DetectorConfig:
    """Configuração do detector"""
    # Thresholds ML
    ml_threshold: float = 0.7
    
    # Thresholds de regras
    min_count: int = 50          # Abaixo = possível outage
    max_spike: float = 2.0       # Acima de 200% da média = spike
    drop_threshold: float = 0.5  # Queda de mais de 50%
    zscore_threshold: float = 2.5
    
    # Janela de análise
    window_size: int = 30

# ============== ANOMALY DETECTOR ==============

class AnomalyDetector:
    """
    Detector híbrido de anomalias.
    
    Combina:
    1. Isolation Forest (ML)
    2. Regras de threshold
    3. Z-Score estatístico
    """
    
    def __init__(self, config: Optional[DetectorConfig] = None):
        self.config = config or DetectorConfig()
        self.model = None
        self.is_trained = False
        
        # Histórico interno
        self.history: List[float] = []
        self.status_history: List[str] = []
        
        # Estatísticas móveis
        self.running_mean = 100.0
        self.running_std = 20.0
        self.alpha = 0.1  # Fator de suavização exponencial
        
        # Tentar carregar sklearn
        self._init_ml_model()
    
    def _init_ml_model(self):
        """Inicializa modelo ML se disponível"""
        try:
            from sklearn.ensemble import IsolationForest
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            logger.info("✅ Isolation Forest inicializado")
        except ImportError:
            logger.warning("⚠️ sklearn não disponível, usando apenas regras")
            self.model = None
    
    def reset(self):
        """Reseta o estado do detector"""
        self.history.clear()
        self.status_history.clear()
        self.running_mean = 100.0
        self.running_std = 20.0
        self.is_trained = False
    
    def _update_statistics(self, count: float):
        """Atualiza estatísticas com média móvel exponencial"""
        if len(self.history) > 10:
            self.running_mean = (1 - self.alpha) * self.running_mean + self.alpha * count
            variance = (count - self.running_mean) ** 2
            running_var = self.running_std ** 2
            new_var = (1 - self.alpha) * running_var + self.alpha * variance
            self.running_std = max(np.sqrt(new_var), 1.0)
    
    def _calc_zscore(self, count: float) -> float:
        """Calcula Z-Score"""
        if self.running_std == 0:
            return 0.0
        return (count - self.running_mean) / self.running_std
    
    def _ml_score(self, count: float, historical: List[float]) -> float:
        """
        Calcula score ML usando Isolation Forest.
        Retorna score entre 0 (normal) e 1 (anomalia).
        """
        if self.model is None or len(historical) < 20:
            return 0.0
        
        try:
            # Treinar se necessário
            if not self.is_trained and len(historical) >= 30:
                X_train = np.array(historical).reshape(-1, 1)
                self.model.fit(X_train)
                self.is_trained = True
                logger.info(f"🎓 Modelo treinado com {len(historical)} amostras")
            
            if not self.is_trained:
                return 0.0
            
            # Predição
            X_test = np.array([[count]])
            score = self.model.decision_function(X_test)[0]
            
            # Normalizar para 0-1 (sigmoid)
            normalized = 1 / (1 + np.exp(score))
            return float(normalized)
            
        except Exception as e:
            logger.error(f"Erro ML: {e}")
            return 0.0
    
    def _check_rules(self, count: int, status: str, auth_code: str) -> List[str]:
        """
        Verifica regras de threshold.
        Retorna lista de violações.
        """
        violations = []
        
        # Regra 1: Volume muito baixo (possível outage)
        if count < self.config.min_count:
            violations.append(f"LOW_VOLUME: {count} < {self.config.min_count} (possível outage)")
        
        # Regra 2: Spike de volume
        if self.running_mean > 0 and count > self.running_mean * self.config.max_spike:
            violations.append(f"VOLUME_SPIKE: {count} > {self.config.max_spike}x média ({self.running_mean:.0f})")
        
        # Regra 3: Queda brusca
        if self.running_mean > 0 and count < self.running_mean * self.config.drop_threshold:
            violations.append(f"VOLUME_DROP: {count} < 50% da média ({self.running_mean:.0f})")
        
        # Regra 4: Status não-aprovado
        if status == "denied":
            violations.append("DENIED: Transação negada")
        elif status == "failed":
            violations.append("FAILED: Transação falhou")
        elif status == "reversed":
            violations.append("REVERSED: Transação revertida")
        
        # Regra 5: Código de erro
        if auth_code != "00":
            violations.append(f"AUTH_ERROR: Código {auth_code} indica erro")
        
        # Regra 6: Z-Score extremo
        zscore = self._calc_zscore(count)
        if abs(zscore) > self.config.zscore_threshold:
            violations.append(f"ZSCORE: {zscore:.2f} excede threshold {self.config.zscore_threshold}")
        
        return violations
    
    def _determine_level(self, score: float, violations: List[str]) -> str:
        """Determina nível do alerta"""
        critical_keywords = ["FAILED", "LOW_VOLUME", "VOLUME_DROP", "AUTH_ERROR"]
        severe = sum(1 for v in violations if any(k in v for k in critical_keywords))
        
        if score > 0.85 or severe >= 2:
            return "CRITICAL"
        elif score > self.config.ml_threshold or len(violations) >= 2:
            return "WARNING"
        elif len(violations) >= 1:
            return "WARNING"
        return "NORMAL"
    
    def _get_recommendation(self, level: str, violations: List[str]) -> str:
        """Gera recomendação baseada na análise"""
        if level == "CRITICAL":
            if any("LOW_VOLUME" in v or "VOLUME_DROP" in v for v in violations):
                return "🚨 CRÍTICO: Possível outage! Verificar conectividade do gateway IMEDIATAMENTE."
            if any("FAILED" in v for v in violations):
                return "🚨 CRÍTICO: Alta taxa de falhas! Investigar processador de pagamentos."
            if any("AUTH_ERROR" in v for v in violations):
                return "🚨 CRÍTICO: Erros de autorização! Verificar conexão com adquirente."
            return "🚨 CRÍTICO: Múltiplas anomalias! Investigação imediata necessária."
        
        elif level == "WARNING":
            if any("SPIKE" in v for v in violations):
                return "⚠️ ALERTA: Spike de volume. Monitorar para possível sobrecarga ou tráfego legítimo."
            if any("DENIED" in v for v in violations):
                return "⚠️ ALERTA: Taxa de negação elevada. Verificar padrões de fraude."
            return "⚠️ ALERTA: Anomalia detectada. Continuar monitorando."
        
        return "✅ NORMAL: Métricas dentro dos parâmetros esperados."
    
    def analyze(
        self,
        current_count: int,
        status: str,
        auth_code: str,
        historical_counts: List[float]
    ) -> Dict[str, Any]:
        """
        🔍 Análise principal de anomalias.
        
        Args:
            current_count: Contagem atual de transações
            status: Status da transação
            auth_code: Código de autorização
            historical_counts: Histórico recente
            
        Returns:
            Dict com resultado da análise
        """
        # Atualizar histórico interno
        self.history.append(current_count)
        if len(self.history) > 500:
            self.history = self.history[-300:]
        
        self.status_history.append(status)
        if len(self.status_history) > 500:
            self.status_history = self.status_history[-300:]
        
        # Atualizar estatísticas
        self._update_statistics(current_count)
        
        # Calcular scores
        ml_score = self._ml_score(current_count, historical_counts)
        zscore = self._calc_zscore(current_count)
        violations = self._check_rules(current_count, status, auth_code)
        
        # Score combinado
        if ml_score > 0:
            combined = 0.6 * ml_score + 0.4 * min(abs(zscore) / 3, 1)
        else:
            combined = min(abs(zscore) / 3, 1)
        
        # Determinar nível
        level = self._determine_level(combined, violations)
        is_anomaly = level != "NORMAL"
        
        # Recomendação
        recommendation = self._get_recommendation(level, violations)
        
        # Taxa de aprovação recente
        recent = self.status_history[-30:] if self.status_history else []
        approval_rate = recent.count("approved") / max(len(recent), 1)
        
        result = {
            "is_anomaly": is_anomaly,
            "alert_level": level,
            "anomaly_score": round(combined, 4),
            "rule_violations": violations,
            "recommendation": recommendation,
            "metrics": {
                "current_count": current_count,
                "running_mean": round(self.running_mean, 2),
                "running_std": round(self.running_std, 2),
                "zscore": round(zscore, 2),
                "ml_score": round(ml_score, 4),
                "approval_rate": round(approval_rate, 4),
                "status": status,
                "auth_code": auth_code
            }
        }
        
        if is_anomaly:
            logger.warning(f"🚨 ANOMALIA: {level} | Score: {combined:.2f} | {violations}")
        
        return result


# ============== TESTE ==============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    detector = AnomalyDetector()
    
    print("🧪 Testando detector de anomalias...\n")
    
    # Simular transações normais
    print("📈 Transações normais:")
    for i in range(30):
        count = int(np.random.normal(115, 15))
        result = detector.analyze(count, "approved", "00", detector.history)
    print(f"   Processadas 30 transações normais")
    print(f"   Média: {detector.running_mean:.1f}, Std: {detector.running_std:.1f}\n")
    
    # Testar anomalias
    print("🚨 Testando cenários de anomalia:\n")
    
    # Teste 1: Volume baixo (outage)
    result = detector.analyze(10, "approved", "00", detector.history)
    print(f"1. Volume baixo (10):")
    print(f"   Nível: {result['alert_level']}")
    print(f"   Score: {result['anomaly_score']:.2f}")
    print(f"   Recomendação: {result['recommendation']}\n")
    
    # Teste 2: Transação falha
    result = detector.analyze(100, "failed", "59", detector.history)
    print(f"2. Transação falha:")
    print(f"   Nível: {result['alert_level']}")
    print(f"   Score: {result['anomaly_score']:.2f}")
    print(f"   Recomendação: {result['recommendation']}\n")
    
    # Teste 3: Spike
    result = detector.analyze(400, "approved", "00", detector.history)
    print(f"3. Spike de volume (400):")
    print(f"   Nível: {result['alert_level']}")
    print(f"   Score: {result['anomaly_score']:.2f}")
    print(f"   Recomendação: {result['recommendation']}\n")
    
    print("✅ Testes concluídos!")
