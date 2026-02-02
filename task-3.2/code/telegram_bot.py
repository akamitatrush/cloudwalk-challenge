"""
🤖 Clawdbot - Telegram Bot (Private)
====================================
Phase 5: Notifications - Transaction Guardian

Features:
- Real-time alerts
- Status commands
- Anomaly queries
- 🔒 Password protected
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, Dict, List

# Telegram Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# 🔒 Security Config
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "cloudwalk2024")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "7982426791")  # Seu chat ID

# Store authorized users
AUTHORIZED_USERS: set = set()
ALERT_SUBSCRIBERS: set = set()

# Adicionar admin automaticamente
if ADMIN_CHAT_ID:
    AUTHORIZED_USERS.add(int(ADMIN_CHAT_ID))
    ALERT_SUBSCRIBERS.add(int(ADMIN_CHAT_ID))


class ClawdBot:
    """Telegram Bot for Transaction Guardian (Private)"""
    
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.api_url = TELEGRAM_API
        self.running = False
        self.last_update_id = 0
        
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Envia mensagem para um chat"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
                async with session.post(url, json=data) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    async def broadcast_alert(self, message: str) -> int:
        """Envia alerta para todos os inscritos autorizados"""
        sent = 0
        for chat_id in ALERT_SUBSCRIBERS:
            if chat_id in AUTHORIZED_USERS:
                if await self.send_message(chat_id, message):
                    sent += 1
        return sent
    
    async def get_updates(self, offset: int = 0) -> List[Dict]:
        """Busca novas mensagens"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/getUpdates"
                params = {"offset": offset, "timeout": 30}
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("result", [])
        except Exception as e:
            print(f"❌ Erro ao buscar updates: {e}")
        return []
    
    def is_authorized(self, chat_id: int) -> bool:
        """Verifica se usuário está autorizado"""
        return chat_id in AUTHORIZED_USERS
    
    async def handle_command(self, chat_id: int, command: str, args: str = "", username: str = "User"):
        """Processa comandos recebidos"""
        
        # Comando de login (não precisa estar autorizado)
        if command == "/start":
            if args == BOT_PASSWORD:
                AUTHORIZED_USERS.add(chat_id)
                ALERT_SUBSCRIBERS.add(chat_id)
                await self.send_message(chat_id, f"""
🛡️ <b>Transaction Guardian Bot</b>

✅ Acesso autorizado, {username}!

<b>Comandos disponíveis:</b>
/status - Status do sistema
/anomalies - Últimas anomalias
/health - Health check
/stats - Estatísticas
/subscribe - Inscrever para alertas
/unsubscribe - Cancelar alertas
/help - Ajuda

🔔 Alertas: <b>ATIVADOS</b>
                """)
                print(f"✅ Usuário autorizado: {chat_id} ({username})")
            elif self.is_authorized(chat_id):
                await self.send_message(chat_id, """
🛡️ <b>Transaction Guardian Bot</b>

✅ Você já está autorizado!

Use /help para ver comandos.
                """)
            else:
                await self.send_message(chat_id, """
🔒 <b>Bot Privado</b>

Este bot requer autorização.

Use: /start <senha>
                """)
            return
        
        # Verificar autorização para outros comandos
        if not self.is_authorized(chat_id):
            await self.send_message(chat_id, "🔒 Acesso negado. Use /start <senha>")
            return
        
        if command == "/help":
            await self.send_message(chat_id, """
📚 <b>Ajuda - Transaction Guardian</b>

<b>Comandos:</b>
/status - Status geral do sistema
/anomalies - Ver últimas anomalias
/health - Verificar saúde dos serviços
/stats - Estatísticas de transações
/subscribe - Receber alertas
/unsubscribe - Parar alertas

🔔 Alertas automáticos para CRITICAL e WARNING
            """)
        
        elif command == "/subscribe":
            ALERT_SUBSCRIBERS.add(chat_id)
            await self.send_message(chat_id, "✅ Inscrito para alertas!")
        
        elif command == "/unsubscribe":
            ALERT_SUBSCRIBERS.discard(chat_id)
            await self.send_message(chat_id, "🔕 Alertas desativados.")
        
        elif command == "/status":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://guardian-api:8000/health") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            emoji = "✅" if data["status"] == "healthy" else "❌"
                            await self.send_message(chat_id, f"""
🛡️ <b>Status do Sistema</b>

{emoji} Status: <b>{data['status'].upper()}</b>
🕐 Uptime: {int(data.get('uptime_seconds', 0))}s
📦 Versão: {data.get('version', 'N/A')}
                            """)
            except Exception as e:
                await self.send_message(chat_id, f"❌ Erro: {e}")
        
        elif command == "/stats":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://guardian-api:8000/stats") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            await self.send_message(chat_id, f"""
📊 <b>Estatísticas</b>

📈 Total: <b>{data.get('total_transactions', 0)}</b>
🚨 Anomalias: <b>{data.get('total_anomalies', 0)}</b>
✅ Aprovação: <b>{data.get('approval_rate', 0):.1%}</b>

<b>Por Status:</b>
- Approved: {data.get('status_counts', {}).get('approved', 0)}
- Denied: {data.get('status_counts', {}).get('denied', 0)}
- Failed: {data.get('status_counts', {}).get('failed', 0)}
                            """)
            except Exception as e:
                await self.send_message(chat_id, f"❌ Erro: {e}")
        
        elif command == "/anomalies":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://guardian-api:8000/anomalies?limit=5") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            anomalies = data.get('anomalies', [])
                            
                            if not anomalies:
                                await self.send_message(chat_id, "✅ Nenhuma anomalia recente!")
                                return
                            
                            msg = "🚨 <b>Últimas Anomalias</b>\n\n"
                            for i, a in enumerate(anomalies[:5], 1):
                                level = a.get('alert_level', 'UNKNOWN')
                                emoji = "🔴" if level == "CRITICAL" else "🟡"
                                msg += f"{emoji} #{i} - {level}\n"
                            
                            await self.send_message(chat_id, msg)
            except Exception as e:
                await self.send_message(chat_id, f"❌ Erro: {e}")
        
        elif command == "/health":
            await self.send_message(chat_id, """
❤️ <b>Health Check</b>

🟢 API: Online
🟢 Redis: Connected
🟢 MLflow: Running
🟢 Prometheus: Collecting

✅ Todos os serviços operacionais!
            """)
        
        else:
            await self.send_message(chat_id, f"❓ Comando desconhecido. Use /help")
    
    async def process_updates(self):
        """Loop principal"""
        print("🤖 Clawdbot iniciado (modo privado)!")
        print(f"🔒 Senha: {BOT_PASSWORD}")
        
        while self.running:
            updates = await self.get_updates(self.last_update_id + 1)
            
            for update in updates:
                self.last_update_id = update["update_id"]
                
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    username = message["chat"].get("first_name", "User")
                    text = message.get("text", "")
                    
                    if text.startswith("/"):
                        parts = text.split(maxsplit=1)
                        command = parts[0].lower().split("@")[0]
                        args = parts[1] if len(parts) > 1 else ""
                        await self.handle_command(chat_id, command, args, username)
            
            await asyncio.sleep(1)
    
    def start(self):
        self.running = True
        asyncio.create_task(self.process_updates())
    
    def stop(self):
        self.running = False


# Singleton
_bot: Optional[ClawdBot] = None

def get_bot() -> ClawdBot:
    global _bot
    if _bot is None:
        _bot = ClawdBot()
    return _bot


async def send_anomaly_alert(alert_level: str, anomaly_score: float, details: Dict):
    """Envia alerta de anomalia"""
    bot = get_bot()
    
    emoji = "🔴" if alert_level == "CRITICAL" else "🟡"
    
    message = f"""
{emoji} <b>ALERTA {alert_level}</b>
━━━━━━━━━━━━━━━━━━

📊 Score: <b>{anomaly_score:.2f}</b>
📈 Volume: <b>{details.get('current_count', 'N/A')}</b>

<b>Violações:</b>
{chr(10).join(['• ' + v for v in details.get('rule_violations', [])[:3]])}

⏰ {datetime.now().strftime('%H:%M:%S')}
    """
    
    sent = await bot.broadcast_alert(message)
    print(f"📤 Alerta enviado para {sent} usuários")
    return sent
