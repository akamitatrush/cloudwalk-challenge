"""
🔔 Alert Manager
================
Gerencia notificações de alertas:
- Slack webhooks
- Console logs
- Rate limiting

CloudWalk Task 3.2
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# ============== CONFIGURATION ==============

@dataclass
class AlertConfig:
    """Configuração de alertas"""
    slack_webhook: str = os.getenv("SLACK_WEBHOOK_URL", "")
    enable_slack: bool = True
    enable_console: bool = True
    rate_limit_seconds: int = 60  # Mínimo entre alertas similares

# ============== TEMPLATES ==============

TEMPLATES = {
    "CRITICAL": {
        "color": "#FF0000",
        "emoji": "🚨",
        "title": "ALERTA CRÍTICO - Anomalia de Transação"
    },
    "WARNING": {
        "color": "#FFA500",
        "emoji": "⚠️", 
        "title": "ALERTA - Padrão Incomum Detectado"
    },
    "NORMAL": {
        "color": "#00FF00",
        "emoji": "✅",
        "title": "RESOLVIDO - Sistema Normalizado"
    }
}

# ============== ALERT MANAGER ==============

class AlertManager:
    """
    Gerenciador de alertas multi-canal.
    """
    
    def __init__(self, config: Optional[AlertConfig] = None):
        self.config = config or AlertConfig()
        self.last_alerts: Dict[str, datetime] = {}
        self.history: List[Dict] = []
    
    def _should_send(self, alert_key: str) -> bool:
        """Verifica rate limiting"""
        now = datetime.now()
        
        if alert_key in self.last_alerts:
            elapsed = (now - self.last_alerts[alert_key]).total_seconds()
            if elapsed < self.config.rate_limit_seconds:
                return False
        
        self.last_alerts[alert_key] = now
        return True
    
    def _format_slack_message(
        self,
        level: str,
        violations: List[str],
        score: float,
        transaction: Dict
    ) -> Dict:
        """Formata mensagem para Slack"""
        template = TEMPLATES.get(level, TEMPLATES["WARNING"])
        
        violations_text = "\n".join([f"• {v}" for v in violations]) if violations else "Nenhuma violação específica"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{template['emoji']} {template['title']}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Nível:*\n{level}"},
                    {"type": "mrkdwn", "text": f"*Score:*\n{score:.2%}"},
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n{datetime.now().strftime('%H:%M:%S')}"},
                    {"type": "mrkdwn", "text": f"*Transações:*\n{transaction.get('count', 'N/A')}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Violações:*\n{violations_text}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🛡️ Transaction Guardian | Status: {transaction.get('status', 'N/A')}"
                    }
                ]
            }
        ]
        
        # Botões para alertas críticos
        if level == "CRITICAL":
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Dashboard"},
                        "url": "http://localhost:3000",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📋 API Docs"},
                        "url": "http://localhost:8000/docs"
                    }
                ]
            })
        
        return {
            "username": "Transaction Guardian",
            "icon_emoji": ":shield:",
            "attachments": [{"color": template["color"], "blocks": blocks}]
        }
    
    async def _send_slack(self, message: Dict) -> bool:
        """Envia alerta para Slack"""
        if not self.config.slack_webhook:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_webhook,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Erro Slack: {e}")
            return False
    
    def _log_console(
        self,
        level: str,
        violations: List[str],
        score: float,
        transaction: Dict
    ):
        """Log para console formatado"""
        template = TEMPLATES.get(level, TEMPLATES["WARNING"])
        
        border = "=" * 60
        print(f"\n{border}")
        print(f"{template['emoji']} {template['title']}")
        print(border)
        print(f"Hora:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Nível:       {level}")
        print(f"Score:       {score:.2%}")
        print(f"Transações:  {transaction.get('count', 'N/A')}")
        print(f"Status:      {transaction.get('status', 'N/A')}")
        print(f"\nViolações:")
        for v in violations:
            print(f"  • {v}")
        print(border + "\n")
    
    async def send_alert(
        self,
        level: str,
        violations: List[str],
        score: float,
        transaction: Dict
    ):
        """
        🔔 Envia alerta para todos os canais configurados.
        
        Args:
            level: NORMAL, WARNING ou CRITICAL
            violations: Lista de violações
            score: Score de anomalia
            transaction: Dados da transação
        """
        # Rate limiting
        alert_key = f"{level}:{','.join(sorted(violations)[:3])}"
        if not self._should_send(alert_key):
            return
        
        # Histórico
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "score": score,
            "violations": violations
        })
        if len(self.history) > 500:
            self.history = self.history[-300:]
        
        # Console
        if self.config.enable_console:
            self._log_console(level, violations, score, transaction)
        
        # Slack
        if self.config.enable_slack and self.config.slack_webhook:
            message = self._format_slack_message(level, violations, score, transaction)
            await self._send_slack(message)
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de alertas"""
        return self.history[-limit:]
    
    def get_stats(self) -> Dict:
        """Estatísticas de alertas"""
        if not self.history:
            return {"total": 0}
        
        levels = [a["level"] for a in self.history]
        return {
            "total": len(self.history),
            "critical": levels.count("CRITICAL"),
            "warning": levels.count("WARNING")
        }


# ============== TESTE ==============

if __name__ == "__main__":
    import asyncio
    
    async def test():
        manager = AlertManager()
        
        # Teste CRITICAL
        await manager.send_alert(
            level="CRITICAL",
            violations=["LOW_VOLUME: 10 < 50", "ZSCORE: -3.5"],
            score=0.92,
            transaction={"count": 10, "status": "approved", "auth_code": "00"}
        )
        
        # Teste WARNING
        await manager.send_alert(
            level="WARNING",
            violations=["VOLUME_SPIKE: 300 > 2x média"],
            score=0.65,
            transaction={"count": 300, "status": "approved", "auth_code": "00"}
        )
        
        print(f"\n✅ Testes concluídos!")
        print(f"Stats: {manager.get_stats()}")
    
    asyncio.run(test())
