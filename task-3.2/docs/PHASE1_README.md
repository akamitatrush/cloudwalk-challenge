# 🏗️ Transaction Guardian v2.0 - Phase 1: Foundation

> **Migração de CSV para TimescaleDB**

## 📋 Overview

Esta fase implementa a migração do sistema de armazenamento de CSV para **TimescaleDB**, um banco de dados otimizado para time-series, proporcionando:

| Aspecto | Antes (CSV) | Depois (TimescaleDB) |
|---------|-------------|----------------------|
| Query latency | ~500ms | <50ms |
| Data retention | Session only | 90 dias automático |
| Agregações | Manual (Python) | Automatic (Continuous Aggregates) |
| Escalabilidade | Limitada | Horizontal |
| Compressão | Nenhuma | Automática (~90%) |

---

## 🚀 Quick Start

### 1. Subir o TimescaleDB

```bash
cd task-3.2/infrastructure

# Criar rede se não existir
docker network create monitoring 2>/dev/null || true

# Subir TimescaleDB + pgAdmin
docker compose -f docker-compose.timescale.yml up -d

# Verificar se subiu
docker ps | grep guardian-timescaledb
```

### 2. Verificar Schema

```bash
# Conectar ao banco
docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian

# Listar tabelas
\dt

# Ver estrutura da tabela transactions
\d transactions

# Sair
\q
```

### 3. Instalar dependências Python

```bash
cd task-3.2/code
pip install -r requirements-phase1.txt
```

### 4. Migrar dados existentes

```bash
# Dry run primeiro (simula sem inserir)
python migrate_csv_to_timescale.py --csv-path ../data/transactions.csv --dry-run

# Migrar de verdade
python migrate_csv_to_timescale.py --csv-path ../data/transactions.csv
```

### 5. Testar conexão

```bash
python database.py
```

---

## 📁 Estrutura dos Arquivos

```
task-3.2/
├── infrastructure/
│   ├── docker-compose.yml            # Stack original
│   ├── docker-compose.timescale.yml  # 🆕 TimescaleDB
│   └── timescaledb/
│       └── init/
│           └── 001_schema.sql        # 🆕 Schema otimizado
├── code/
│   ├── main.py                       # FastAPI (existente)
│   ├── database.py                   # 🆕 Módulo TimescaleDB
│   ├── migrate_csv_to_timescale.py   # 🆕 Script de migração
│   └── requirements-phase1.txt       # 🆕 Dependências
└── data/
    └── transactions.csv              # Dados originais
```

---

## 📊 Schema do Banco

### Tabelas Principais

| Tabela | Descrição | Retenção |
|--------|-----------|----------|
| `transactions` | Todas as transações | 90 dias |
| `anomalies` | Anomalias detectadas | 180 dias |
| `alerts` | Alertas disparados | 365 dias |
| `metrics_hourly` | Métricas agregadas | 90 dias |

### Continuous Aggregates (Views Materializadas)

| View | Granularidade | Refresh |
|------|---------------|---------|
| `transactions_per_minute` | 1 minuto | A cada 1 min |
| `transactions_per_hour` | 1 hora | A cada 1 hora |

### Funções Úteis

```sql
-- Taxa de aprovação das últimas 2 horas
SELECT * FROM get_approval_rate(NOW() - INTERVAL '2 hours', NOW());

-- Verificar anomalia de volume
SELECT * FROM check_volume_anomaly(60, 2.5);  -- janela 60min, threshold 2.5 std
```

---

## 💻 Uso no Código

### Básico

```python
from database import Database, Transaction

# Conectar
db = Database()
await db.connect()

# Inserir transação
tx = Transaction(
    status="approved",
    amount=Decimal("150.00"),
    merchant_id="MERCHANT_001"
)
tx_id = await db.insert_transaction(tx)

# Buscar estatísticas
stats = await db.get_stats(hours=1)
print(f"Taxa de aprovação: {stats.approval_rate}%")

# Fechar
await db.close()
```

### Com FastAPI

```python
from fastapi import FastAPI, Depends
from database import Database, get_database, Stats

app = FastAPI()

@app.get("/stats", response_model=Stats)
async def get_stats(hours: int = 1, db: Database = Depends(get_database)):
    return await db.get_stats(hours=hours)

@app.get("/health")
async def health(db: Database = Depends(get_database)):
    return await db.health_check()
```

---

## 🔌 Acessos

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| TimescaleDB | `localhost:5432` | `guardian` / `guardian_secure_2024` |
| pgAdmin | `http://localhost:5050` | `admin@guardian.local` / `admin` |

### Conexão via psql

```bash
docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian
```

### String de conexão

```
postgresql://guardian:guardian_secure_2024@localhost:5432/transaction_guardian
```

---

## 📈 Queries Úteis

### Transações por hora (últimas 24h)

```sql
SELECT * FROM transactions_per_hour 
WHERE bucket > NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;
```

### Top merchants por volume

```sql
SELECT 
    merchant_id,
    COUNT(*) as transactions,
    SUM(amount) as total_amount,
    ROUND(AVG(amount)::numeric, 2) as avg_amount
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY merchant_id
ORDER BY transactions DESC
LIMIT 10;
```

### Anomalias não resolvidas

```sql
SELECT * FROM anomalies 
WHERE status IN ('open', 'acknowledged')
ORDER BY severity, detected_at DESC;
```

### Taxa de aprovação por hora

```sql
SELECT 
    bucket,
    total,
    approved,
    ROUND((approved::numeric / NULLIF(total, 0) * 100), 2) as approval_rate
FROM transactions_per_hour
WHERE bucket > NOW() - INTERVAL '24 hours'
ORDER BY bucket DESC;
```

---

## ✅ Checklist da Fase 1

- [x] Docker Compose com TimescaleDB
- [x] Schema otimizado para time-series
- [x] Módulo Python async (asyncpg)
- [x] Script de migração CSV → TimescaleDB
- [x] Continuous Aggregates automáticos
- [x] Retention policies (90/180/365 dias)
- [x] Funções SQL para análise
- [ ] Integrar com FastAPI existente
- [ ] Atualizar dashboards Grafana
- [ ] Testes de integração

---

## 🔧 Troubleshooting

### Erro de conexão

```bash
# Verificar se o container está rodando
docker ps | grep timescaledb

# Ver logs
docker logs guardian-timescaledb

# Reiniciar
docker restart guardian-timescaledb
```

### Erro de permissão

```bash
# Verificar rede
docker network ls | grep monitoring

# Criar rede se não existir
docker network create monitoring
```

### Migração lenta

```bash
# Aumentar batch size
python migrate_csv_to_timescale.py --csv-path ../data/transactions.csv --batch-size 5000
```

---

## 📚 Referências

- [TimescaleDB Docs](https://docs.timescale.com/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Continuous Aggregates](https://docs.timescale.com/timescaledb/latest/how-to-guides/continuous-aggregates/)

---

**Phase 1 of Roadmap v2.0** | [Back to Roadmap](../../docs/roadmap/)
