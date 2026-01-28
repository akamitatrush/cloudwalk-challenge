# 🏗️ Phase 1: Foundation - Complete Documentation

> **Transaction Guardian v2.0 - TimescaleDB Infrastructure**

## 📋 Overview

This phase migrates the Transaction Guardian from CSV-based storage to **TimescaleDB**, a time-series optimized database, providing production-grade data infrastructure.

### What Changed

| Aspect | Before (v1.0) | After (Phase 1) |
|--------|---------------|-----------------|
| Storage | CSV files | TimescaleDB |
| Query latency | ~500ms | <50ms |
| Data retention | Session only | 90 days (automatic) |
| Aggregations | Manual (Python) | Automatic (Continuous Aggregates) |
| Visualization | Prometheus metrics | SQL + Grafana |
| Scalability | Limited (memory) | Millions of records |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### 1. Start TimescaleDB

```bash
cd task-3.2/infrastructure

# Create network if not exists
docker network create monitoring 2>/dev/null || true

# Start TimescaleDB + pgAdmin
docker compose -f docker-compose.timescale.yml up -d

# Verify
docker ps | grep timescaledb
```

### 2. Connect to Grafana Network

```bash
# Connect TimescaleDB to Grafana's network
docker network connect infrastructure_guardian-network guardian-timescaledb
```

### 3. Migrate Data

```bash
cd task-3.2

# Install dependencies
pip install -r code/requirements-phase1.txt --break-system-packages

# Dry run (test without inserting)
python3 code/migrate_csv_to_timescale.py --csv-path data/transactions.csv --dry-run

# Migrate for real
python3 code/migrate_csv_to_timescale.py --csv-path data/transactions.csv
```

### 4. Verify Migration

```bash
# Check transaction count
docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian \
    -c "SELECT COUNT(*) FROM transactions;"

# Check status distribution
docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian \
    -c "SELECT status, COUNT(*) FROM transactions GROUP BY status;"
```

---

## 🔌 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **TimescaleDB** | `localhost:5432` | `guardian` / `guardian_secure_2024` |
| **pgAdmin** | http://localhost:5050 | `admin@example.com` / `admin` |
| **Grafana** | http://localhost:3002 | `admin` / `admin` |

### Connection Strings

```bash
# psql
docker exec -it guardian-timescaledb psql -U guardian -d transaction_guardian

# PostgreSQL URL
postgresql://guardian:guardian_secure_2024@localhost:5432/transaction_guardian
```

---

## 📁 Files Added

```
task-3.2/
├── infrastructure/
│   ├── docker-compose.timescale.yml    # TimescaleDB + pgAdmin
│   └── timescaledb/
│       └── init/
│           └── 001_schema.sql          # Optimized schema
├── code/
│   ├── database.py                     # Async Python module
│   ├── migrate_csv_to_timescale.py     # Migration script
│   └── requirements-phase1.txt         # Dependencies
├── sql/
│   └── useful_queries.sql              # 50+ monitoring queries
├── grafana/
│   └── dashboards/
│       └── timescaledb-dashboard.json  # Grafana dashboard
└── setup_phase1.sh                     # Automated setup script
```

---

## 📊 Database Schema

### Tables

| Table | Description | Retention |
|-------|-------------|-----------|
| `transactions` | All transactions (hypertable) | 90 days |
| `anomalies` | Detected anomalies | 180 days |
| `alerts` | Fired alerts | 365 days |
| `metrics_hourly` | Hourly aggregates | 90 days |

### Continuous Aggregates (Materialized Views)

| View | Granularity | Auto-Refresh |
|------|-------------|--------------|
| `transactions_per_minute` | 1 minute | Every 1 min |
| `transactions_per_hour` | 1 hour | Every 1 hour |

### Useful Functions

```sql
-- Get approval rate for a period
SELECT * FROM get_approval_rate(NOW() - INTERVAL '2 hours', NOW());

-- Check volume anomaly (Z-Score based)
SELECT * FROM check_volume_anomaly(60, 2.5);  -- 60 min window, 2.5 std threshold
```

---

## 🎨 Grafana Integration

### Add Data Source

1. Go to **Settings** → **Data Sources** → **Add data source**
2. Select **PostgreSQL**
3. Configure:
   - **Host:** `guardian-timescaledb:5432`
   - **Database:** `transaction_guardian`
   - **User:** `guardian`
   - **Password:** `guardian_secure_2024`
   - **TLS/SSL Mode:** `disable`
4. Click **Save & test**

### Import Dashboard

1. Go to **Dashboards** → **Import**
2. Upload `grafana/dashboards/timescaledb-dashboard.json`
3. Select **TimescaleDB** as data source
4. Click **Import**

### Dashboard Panels

| Panel | Type | Query |
|-------|------|-------|
| Distribuição por Status | Bar Chart | `SELECT status, COUNT(*) FROM transactions GROUP BY status` |
| Total Transações | Stat | `SELECT COUNT(*) FROM transactions` |
| Taxa de Aprovação | Gauge | `SELECT ROUND((COUNT(*) FILTER (WHERE status='approved')::numeric / COUNT(*) * 100), 1)` |
| Pie Chart | Pie | `SELECT status, COUNT(*) FROM transactions GROUP BY status` |

---

## 🔧 Troubleshooting

### Connection Error in Grafana

**Problem:** `failed to connect to server`

**Solution:** Containers are on different networks

```bash
# Connect TimescaleDB to Grafana's network
docker network connect infrastructure_guardian-network guardian-timescaledb
```

### pgAdmin Email Validation Error

**Problem:** `admin@guardian.local does not appear to be a valid email`

**Solution:** Use a valid email format

```bash
# Edit docker-compose.timescale.yml
sed -i 's/admin@guardian.local/admin@example.com/g' docker-compose.timescale.yml

# Recreate container
docker stop guardian-pgadmin && docker rm guardian-pgadmin
docker compose -f docker-compose.timescale.yml up -d
```

### Migration Shows 0 Recent Transactions

**Problem:** `check_volume_anomaly` returns null values

**Reason:** CSV data has old timestamps. The function queries `NOW() - INTERVAL`

**Solution:** Update timestamps to recent dates (optional)

```sql
UPDATE transactions 
SET timestamp = NOW() - (random() * INTERVAL '24 hours');
```

### pip Installation Error

**Problem:** `externally-managed-environment`

**Solution:** Use `--break-system-packages` flag

```bash
pip install -r requirements-phase1.txt --break-system-packages
```

---

## 📈 Useful Queries

### Quick Status Check

```sql
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    ROUND((COUNT(*) FILTER (WHERE status = 'approved')::numeric / COUNT(*) * 100), 2) AS approval_rate
FROM transactions;
```

### Transactions Per Hour (Last 24h)

```sql
SELECT 
    date_trunc('hour', timestamp) AS hour,
    COUNT(*) AS total
FROM transactions
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

### Detect Anomalies (Z-Score)

```sql
SELECT * FROM check_volume_anomaly(60, 2.5);
```

### Health Check

```sql
SELECT 
    (SELECT COUNT(*) FROM transactions) AS total_transactions,
    (SELECT COUNT(*) FROM anomalies WHERE status = 'open') AS open_anomalies,
    (SELECT MAX(timestamp) FROM transactions) AS last_transaction;
```

> See `sql/useful_queries.sql` for 50+ monitoring queries

---

## ✅ Phase 1 Checklist

- [x] Docker Compose with TimescaleDB
- [x] Optimized schema with hypertables
- [x] Continuous Aggregates (per minute/hour)
- [x] Retention policies (90/180/365 days)
- [x] Async Python module (asyncpg)
- [x] CSV migration script
- [x] pgAdmin for database management
- [x] Grafana data source configured
- [x] Grafana dashboard with 4 panels
- [x] 50+ useful SQL queries
- [x] Complete documentation

---

## 🔜 Next Steps (Phase 2+)

| Phase | Focus | Key Items |
|-------|-------|-----------|
| **Phase 2** | Performance | Kafka, Workers, Circuit Breaker |
| **Phase 3** | Security | OAuth2, Vault, Rate Limiting |
| **Phase 4** | MLOps | MLflow, Airflow, A/B Testing |
| **Phase 5** | Clawdbot | AI Assistant, Telegram, WhatsApp |
| **Phase 6** | Observability | OpenTelemetry, Jaeger, SLOs |

---

## 📚 References

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Grafana PostgreSQL Data Source](https://grafana.com/docs/grafana/latest/datasources/postgres/)
- [Continuous Aggregates](https://docs.timescale.com/timescaledb/latest/how-to-guides/continuous-aggregates/)

---

**Phase 1 Complete** ✅ | Part of [Roadmap v2.0](../docs/roadmap/)
