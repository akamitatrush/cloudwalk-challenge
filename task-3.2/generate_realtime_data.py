#!/usr/bin/env python3
"""Gera transações com timestamps recentes para o TimescaleDB"""

import asyncio
import asyncpg
import random
from datetime import datetime, timedelta

# Configurações
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "guardian",
    "password": "guardian_secure_2024",
    "database": "transaction_guardian"
}

STATUSES = ['approved', 'denied', 'failed', 'reversed', 'refunded', 'backend_reversed']
STATUS_WEIGHTS = [0.70, 0.10, 0.08, 0.05, 0.04, 0.03]  # 70% aprovadas

async def generate_transactions(num_transactions: int, hours_back: int = 24):
    """Gera transações com timestamps das últimas N horas"""
    
    print(f"🚀 Gerando {num_transactions} transações das últimas {hours_back} horas...")
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    now = datetime.now()
    inserted = 0
    
    for i in range(num_transactions):
        # Timestamp aleatório nas últimas N horas
        random_minutes = random.randint(0, hours_back * 60)
        timestamp = now - timedelta(minutes=random_minutes)
        
        # Status com peso (maioria aprovada)
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        
        # Valores aleatórios
        amount = round(random.uniform(10, 5000), 2)
        merchant_id = f"merchant_{random.randint(1, 100):03d}"
        
        # Anomalia (5% de chance)
        is_anomaly = random.random() < 0.05
        
        await conn.execute("""
            INSERT INTO transactions (timestamp, status, amount, merchant_id, is_anomaly)
            VALUES ($1, $2, $3, $4, $5)
        """, timestamp, status, amount, merchant_id, is_anomaly)
        
        inserted += 1
        
        if inserted % 1000 == 0:
            print(f"   ✅ {inserted}/{num_transactions} inseridas...")
    
    await conn.close()
    
    print(f"\n🎉 {inserted} transações inseridas com sucesso!")
    print(f"   Período: últimas {hours_back} horas")

if __name__ == "__main__":
    import sys
    
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    
    asyncio.run(generate_transactions(num, hours))
