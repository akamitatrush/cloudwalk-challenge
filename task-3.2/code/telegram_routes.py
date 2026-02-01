"""
🤖 Telegram Bot Routes
======================
Phase 5: API endpoints for Telegram Bot
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from .telegram_bot import get_bot, send_anomaly_alert, ALERT_SUBSCRIBERS

router = APIRouter(prefix="/telegram", tags=["Telegram Bot"])


class AlertRequest(BaseModel):
    alert_level: str = "WARNING"
    anomaly_score: float = 0.5
    message: Optional[str] = None
    current_count: int = 0
    rule_violations: list = []


@router.get("/status")
async def telegram_status():
    """📊 Status do bot Telegram"""
    bot = get_bot()
    return {
        "bot_running": bot.running,
        "subscribers": len(ALERT_SUBSCRIBERS),
        "subscriber_ids": list(ALERT_SUBSCRIBERS)
    }


@router.post("/start")
async def start_bot(background_tasks: BackgroundTasks):
    """▶️ Inicia o bot Telegram"""
    bot = get_bot()
    if not bot.running:
        bot.start()
        return {"status": "started", "message": "Bot iniciado!"}
    return {"status": "already_running", "message": "Bot já está rodando"}


@router.post("/stop")
async def stop_bot():
    """⏹️ Para o bot Telegram"""
    bot = get_bot()
    bot.stop()
    return {"status": "stopped", "message": "Bot parado"}


@router.post("/send-alert")
async def send_alert(request: AlertRequest):
    """📤 Envia alerta manual para inscritos"""
    if not ALERT_SUBSCRIBERS:
        raise HTTPException(status_code=400, detail="Nenhum inscrito para receber alertas")
    
    details = {
        "current_count": request.current_count,
        "running_mean": 100,
        "rule_violations": request.rule_violations or ["Manual alert"]
    }
    
    sent = await send_anomaly_alert(
        alert_level=request.alert_level,
        anomaly_score=request.anomaly_score,
        details=details
    )
    
    return {"status": "sent", "recipients": sent}


@router.post("/test")
async def test_bot():
    """🧪 Envia mensagem de teste"""
    bot = get_bot()
    
    if not ALERT_SUBSCRIBERS:
        return {"status": "no_subscribers", "message": "Envie /start no Telegram primeiro!"}
    
    sent = await bot.broadcast_alert("🧪 <b>TESTE</b>\n\n✅ Bot funcionando!")
    return {"status": "sent", "recipients": sent}
