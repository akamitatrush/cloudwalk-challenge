"""
🎮 Transaction Simulator
========================
Simula fluxo de transações em tempo real.
Pode reproduzir CSV ou gerar dados sintéticos.

CloudWalk Task 3.2
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List
import logging
import random
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== SIMULATOR ==============

class TransactionSimulator:
    """
    Simulador de transações para testes e demos.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.is_running = False
        self.sent = 0
        self.anomalies = 0
    
    def _generate_normal(self) -> dict:
        """Gera transação normal"""
        return {
            "status": "approved",
            "count": int(np.random.normal(115, 15)),
            "auth_code": "00"
        }
    
    def _generate_anomaly(self) -> dict:
        """Gera transação anômala"""
        scenario = random.choice(["outage", "spike", "failure", "denial"])
        
        if scenario == "outage":
            return {"status": "approved", "count": random.randint(5, 20), "auth_code": "00"}
        elif scenario == "spike":
            return {"status": "approved", "count": random.randint(300, 500), "auth_code": "00"}
        elif scenario == "failure":
            return {"status": "failed", "count": random.randint(80, 120), "auth_code": random.choice(["05", "51", "59"])}
        else:
            return {"status": "denied", "count": random.randint(80, 120), "auth_code": random.choice(["05", "14", "51"])}
    
    async def _send(self, session: aiohttp.ClientSession, data: dict) -> dict:
        """Envia transação para API"""
        try:
            async with session.post(
                f"{self.api_url}/transaction",
                json=data,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    self.sent += 1
                    result = await response.json()
                    if result.get("is_anomaly"):
                        self.anomalies += 1
                    return result
                return {"error": response.status}
        except Exception as e:
            return {"error": str(e)}
    
    async def replay_csv(self, csv_path: str, speed: float = 10.0):
        """
        📼 Reproduz transações de um arquivo CSV.
        
        Args:
            csv_path: Caminho do CSV
            speed: Multiplicador de velocidade (10 = 10x mais rápido)
        """
        df = pd.read_csv(csv_path)
        logger.info(f"📊 Carregadas {len(df)} linhas de {csv_path}")
        
        self.is_running = True
        self.sent = 0
        self.anomalies = 0
        
        async with aiohttp.ClientSession() as session:
            for idx, row in df.iterrows():
                if not self.is_running:
                    break
                
                data = {
                    "timestamp": row.get("timestamp", datetime.now().isoformat()),
                    "status": row.get("status", "approved"),
                    "count": int(row.get("count", 100)),
                    "auth_code": str(row.get("auth_code", "00")).zfill(2)
                }
                
                result = await self._send(session, data)
                
                # Log de progresso
                if self.sent % 100 == 0:
                    logger.info(f"📤 {self.sent} enviadas | 🚨 {self.anomalies} anomalias")
                
                # Detectar anomalia na resposta
                if result.get("is_anomaly"):
                    logger.warning(f"🚨 {result.get('alert_level')}: score={result.get('anomaly_score', 0):.2f}")
                
                await asyncio.sleep(1.0 / speed)
        
        logger.info(f"✅ Replay concluído: {self.sent} enviadas, {self.anomalies} anomalias")
        self.is_running = False
    
    async def generate_stream(
        self,
        interval: float = 1.0,
        anomaly_prob: float = 0.05,
        duration: Optional[int] = None
    ):
        """
        🎲 Gera stream contínuo de transações sintéticas.
        
        Args:
            interval: Segundos entre transações
            anomaly_prob: Probabilidade de anomalia (0-1)
            duration: Duração em segundos (None = infinito)
        """
        self.is_running = True
        self.sent = 0
        self.anomalies = 0
        start = datetime.now()
        
        logger.info(f"🚀 Iniciando stream (anomaly_prob={anomaly_prob:.1%})")
        
        async with aiohttp.ClientSession() as session:
            while self.is_running:
                # Verificar duração
                if duration:
                    elapsed = (datetime.now() - start).total_seconds()
                    if elapsed >= duration:
                        break
                
                # Gerar transação
                if random.random() < anomaly_prob:
                    data = self._generate_anomaly()
                else:
                    data = self._generate_normal()
                
                data["timestamp"] = datetime.now().isoformat()
                
                result = await self._send(session, data)
                
                # Log periódico
                if self.sent % 50 == 0:
                    logger.info(f"📤 {self.sent} | 🚨 {self.anomalies}")
                
                if result.get("is_anomaly"):
                    logger.warning(f"🚨 {result.get('alert_level')}: {result.get('rule_violations', [])}")
                
                await asyncio.sleep(interval)
        
        logger.info(f"✅ Stream finalizado: {self.sent} enviadas, {self.anomalies} anomalias")
        self.is_running = False
    
    async def inject_incident(self, incident_type: str, duration: int = 30):
        """
        💥 Injeta um incidente específico para teste.
        
        Args:
            incident_type: outage, spike, degradation, auth_errors
            duration: Duração em segundos
        """
        self.is_running = True
        self.sent = 0
        self.anomalies = 0
        
        logger.warning(f"💥 INJETANDO INCIDENTE: {incident_type} por {duration}s")
        
        async with aiohttp.ClientSession() as session:
            start = datetime.now()
            
            while self.is_running:
                elapsed = (datetime.now() - start).total_seconds()
                if elapsed >= duration:
                    break
                
                if incident_type == "outage":
                    data = {"status": "approved", "count": random.randint(0, 10), "auth_code": "00"}
                elif incident_type == "spike":
                    data = {"status": "approved", "count": random.randint(350, 500), "auth_code": "00"}
                elif incident_type == "degradation":
                    data = {"status": "approved", "count": random.randint(50, 70), "auth_code": "00"}
                elif incident_type == "auth_errors":
                    data = {"status": random.choice(["failed", "denied"]), 
                            "count": random.randint(80, 120),
                            "auth_code": random.choice(["05", "51", "59", "91"])}
                else:
                    data = self._generate_anomaly()
                
                data["timestamp"] = datetime.now().isoformat()
                
                result = await self._send(session, data)
                
                if result.get("is_anomaly"):
                    logger.warning(f"🚨 {result.get('alert_level')}")
                
                await asyncio.sleep(1.0)
        
        logger.warning(f"✅ INCIDENTE ENCERRADO: {incident_type}")
        self.is_running = False
    
    def stop(self):
        """Para o simulador"""
        self.is_running = False
        logger.info("🛑 Parando simulador...")


# ============== CLI ==============

async def main():
    parser = argparse.ArgumentParser(description="🎮 Transaction Simulator")
    parser.add_argument("--mode", choices=["csv", "stream", "incident"], default="stream",
                        help="Modo: csv (replay), stream (sintético), incident (teste)")
    parser.add_argument("--csv", type=str, help="Caminho do CSV para replay")
    parser.add_argument("--api", type=str, default="http://localhost:8000", help="URL da API")
    parser.add_argument("--speed", type=float, default=10.0, help="Velocidade do replay")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo entre transações")
    parser.add_argument("--anomaly-prob", type=float, default=0.05, help="Probabilidade de anomalia")
    parser.add_argument("--duration", type=int, default=None, help="Duração em segundos")
    parser.add_argument("--incident", type=str, choices=["outage", "spike", "degradation", "auth_errors"],
                        help="Tipo de incidente")
    
    args = parser.parse_args()
    
    sim = TransactionSimulator(api_url=args.api)
    
    try:
        if args.mode == "csv":
            if not args.csv:
                print("❌ Caminho do CSV necessário (--csv)")
                return
            await sim.replay_csv(args.csv, speed=args.speed)
        
        elif args.mode == "stream":
            await sim.generate_stream(
                interval=args.interval,
                anomaly_prob=args.anomaly_prob,
                duration=args.duration
            )
        
        elif args.mode == "incident":
            if not args.incident:
                print("❌ Tipo de incidente necessário (--incident)")
                return
            await sim.inject_incident(args.incident, duration=args.duration or 30)
    
    except KeyboardInterrupt:
        sim.stop()
        print("\n👋 Simulador interrompido")


if __name__ == "__main__":
    asyncio.run(main())
