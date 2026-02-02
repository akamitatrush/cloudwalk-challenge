"""
📊 AI Summary Report
====================
Phase 6: AI-powered daily reports using Claude API
"""

import os
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional

# Claude API Config
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


class AISummaryGenerator:
    """Generates AI-powered summary reports"""
    
    def __init__(self):
        self.api_key = CLAUDE_API_KEY
        
    async def get_system_stats(self) -> Dict:
        """Coleta estatísticas do sistema"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://guardian-api:8000/stats") as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"❌ Erro ao coletar stats: {e}")
        return {}
    
    async def get_recent_anomalies(self, limit: int = 20) -> List[Dict]:
        """Coleta anomalias recentes"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://guardian-api:8000/anomalies?limit={limit}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("anomalies", [])
        except Exception as e:
            print(f"❌ Erro ao coletar anomalias: {e}")
        return []
    
    async def generate_report(self, stats: Dict, anomalies: List[Dict]) -> str:
        """Gera relatório"""
        return self._generate_local_report(stats, anomalies)
    
    def _generate_local_report(self, stats: Dict, anomalies: List[Dict]) -> str:
        """Gera relatório local"""
        
        # Mapear campos corretos
        total_tx = stats.get('total_processed', 0)
        total_anomalies = stats.get('total_anomalies', 0)
        anomaly_rate = stats.get('anomaly_rate', 0)
        
        # Status distribution
        status_dist = stats.get('status_distribution', {})
        approved = status_dist.get('approved', 0)
        denied = status_dist.get('denied', 0)
        failed = status_dist.get('failed', 0)
        reversed_tx = status_dist.get('reversed', 0)
        refunded = status_dist.get('refunded', 0)
        
        # Calcular taxa de aprovação
        approval_rate = approved / max(total_tx, 1)
        
        # Calcular score de saúde
        health_score = max(0, 100 - (anomaly_rate * 100) - ((1 - approval_rate) * 20))
        
        # Contar severidades das anomalias
        critical = sum(1 for a in anomalies if a.get('alert_level') == 'CRITICAL')
        warning = sum(1 for a in anomalies if a.get('alert_level') == 'WARNING')
        
        # Cache stats
        cache = stats.get('cache', {})
        cache_hits = cache.get('hits', 0)
        cache_misses = cache.get('misses', 0)
        hit_rate = cache.get('hit_rate', 0)
        
        report = f"""
📊 **RELATÓRIO DIÁRIO - TRANSACTION GUARDIAN**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📈 **RESUMO EXECUTIVO**
Processamos {total_tx:,} transações com taxa de aprovação de {approval_rate:.1%}.
Detectamos {total_anomalies:,} anomalias ({critical} críticas, {warning} warnings).

🚨 **PRINCIPAIS INCIDENTES**
- {critical} alertas CRITICAL detectados
- {warning} alertas WARNING detectados  
- Taxa de anomalia: {anomaly_rate:.2%}

📊 **DISTRIBUIÇÃO POR STATUS**
- ✅ Aprovadas: {approved:,}
- ❌ Negadas: {denied:,}
- ⚠️ Falhas: {failed:,}
- 🔄 Estornadas: {reversed_tx:,}
- 💰 Reembolsadas: {refunded:,}

📦 **CACHE PERFORMANCE**
- Hits: {cache_hits:,} | Misses: {cache_misses:,}
- Hit Rate: {hit_rate:.1f}%

💡 **RECOMENDAÇÕES**
1. {'⚠️ Investigar alertas CRITICAL imediatamente' if critical > 0 else '✅ Sem alertas críticos'}
2. {'📉 Analisar causa das negações' if denied > total_tx * 0.15 else '✅ Taxa de negação aceitável'}
3. {'🔧 Verificar falhas de sistema' if failed > total_tx * 0.05 else '✅ Taxa de falha normal'}

🎯 **SCORE DE SAÚDE: {health_score:.0f}/100**
{'🟢 Sistema saudável' if health_score >= 80 else '🟡 Atenção necessária' if health_score >= 60 else '🔴 Situação crítica'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Relatório gerado por Transaction Guardian
"""
        return report
    
    async def generate_and_send(self, send_telegram: bool = True) -> str:
        """Gera relatório e envia por Telegram"""
        
        print("📊 Gerando relatório AI...")
        
        stats = await self.get_system_stats()
        anomalies = await self.get_recent_anomalies()
        report = await self.generate_report(stats, anomalies)
        
        if send_telegram:
            try:
                from .telegram_bot import get_bot
                bot = get_bot()
                await bot.broadcast_alert(report)
                print("📤 Relatório enviado por Telegram!")
            except Exception as e:
                print(f"⚠️ Telegram indisponível: {e}")
        
        return report


# Singleton
_generator: Optional[AISummaryGenerator] = None

def get_generator() -> AISummaryGenerator:
    global _generator
    if _generator is None:
        _generator = AISummaryGenerator()
    return _generator


async def generate_daily_report(send_telegram: bool = True) -> str:
    generator = get_generator()
    return await generator.generate_and_send(send_telegram)
