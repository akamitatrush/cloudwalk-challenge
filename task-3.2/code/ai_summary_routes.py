"""
📊 AI Summary Routes
====================
Phase 6: API endpoints for AI reports
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from .ai_summary import get_generator, generate_daily_report

router = APIRouter(prefix="/ai", tags=["AI Summary"])


class ReportRequest(BaseModel):
    send_telegram: bool = True


@router.get("/report")
async def get_report():
    """📊 Gera relatório AI instantâneo"""
    generator = get_generator()
    
    stats = await generator.get_system_stats()
    anomalies = await generator.get_recent_anomalies()
    report = await generator.generate_report(stats, anomalies)
    
    return {
        "status": "success",
        "report": report,
        "generated_at": generator._generate_local_report.__name__
    }


@router.post("/report/send")
async def send_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """📤 Gera e envia relatório por Telegram"""
    background_tasks.add_task(generate_daily_report, request.send_telegram)
    
    return {
        "status": "queued",
        "message": "Relatório sendo gerado e enviado...",
        "send_telegram": request.send_telegram
    }


@router.get("/status")
async def ai_status():
    """📊 Status do AI Summary"""
    generator = get_generator()
    
    return {
        "claude_api_configured": bool(generator.api_key),
        "model": "claude-sonnet-4-20250514",
        "features": ["daily_report", "anomaly_analysis", "recommendations"]
    }
