#!/usr/bin/env python3
"""Gera transações via API para aparecer no Prometheus"""

import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8001"
STATUSES = ['approved', 'denied', 'failed', 'reversed', 'refunded']

def generate_transaction():
    return {
        "timestamp": datetime.now().isoformat(),
        "status": random.choices(STATUSES, weights=[0.70, 0.12, 0.10, 0.05, 0.03])[0],
        "count": 1,
        "auth_code": f"{random.randint(0, 99):02d}"
    }

def main():
    print("🚀 Gerando tráfego na API...")
    print("   Pressione Ctrl+C para parar\n")
    
    count = 0
    while True:
        try:
            tx = generate_transaction()
            response = requests.post(f"{API_URL}/transaction", json=tx, timeout=5)
            count += 1
            
            if response.status_code == 200:
                print(f"✅ #{count} - {tx['status']}")
            else:
                print(f"⚠️ #{count} - Error: {response.status_code}")
            
            time.sleep(0.2)
            
        except KeyboardInterrupt:
            print(f"\n\n🎉 Total: {count} transações geradas!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
