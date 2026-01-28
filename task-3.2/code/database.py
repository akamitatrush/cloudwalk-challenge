"""
Transaction Guardian v2.0 - TimescaleDB Database Module
========================================================
Módulo para conexão e operações com TimescaleDB.

Uso:
    from database import Database, Transaction
    
    db = Database()
    await db.connect()
    
    # Inserir transação
    tx = Transaction(status="approved", amount=100.50)
    await db.insert_transaction(tx)
    
    # Buscar métricas
    stats = await db.get_stats(hours=1)
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from decimal import Decimal
import asyncpg
from contextlib import asynccontextmanager


# =============================================================================
# Configuration
# =============================================================================

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "guardian"),
    "password": os.getenv("DB_PASSWORD", "guardian_secure_2024"),
    "database": os.getenv("DB_NAME", "transaction_guardian"),
    "min_size": int(os.getenv("DB_POOL_MIN", 5)),
    "max_size": int(os.getenv("DB_POOL_MAX", 20)),
}


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Transaction:
    """Modelo de transação"""
    status: str  # approved, denied, failed, reversed
    amount: Optional[Decimal] = None
    currency: str = "BRL"
    auth_code: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None
    is_anomaly: bool = False
    anomaly_score: Optional[Decimal] = None
    ml_score: Optional[Decimal] = None
    zscore: Optional[Decimal] = None
    detection_method: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None


@dataclass
class Anomaly:
    """Modelo de anomalia detectada"""
    anomaly_type: str  # zero_transactions, spike, drop, pattern
    severity: str  # low, medium, high, critical
    combined_score: Optional[Decimal] = None
    ml_score: Optional[Decimal] = None
    zscore: Optional[Decimal] = None
    transaction_count: Optional[int] = None
    expected_count: Optional[int] = None
    time_window_minutes: int = 60
    status: str = "open"
    notes: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None


@dataclass
class Stats:
    """Estatísticas agregadas"""
    total_transactions: int = 0
    approved: int = 0
    denied: int = 0
    failed: int = 0
    reversed: int = 0
    approval_rate: float = 0.0
    anomaly_count: int = 0
    total_amount: Decimal = Decimal("0")
    avg_amount: Decimal = Decimal("0")
    transactions_per_minute: float = 0.0


# =============================================================================
# Database Class
# =============================================================================

class Database:
    """
    Classe principal para operações com TimescaleDB.
    
    Exemplo:
        db = Database()
        await db.connect()
        
        # Inserir transação
        tx = Transaction(status="approved", amount=100.50)
        tx_id = await db.insert_transaction(tx)
        
        # Buscar estatísticas
        stats = await db.get_stats(hours=1)
        print(f"Taxa de aprovação: {stats.approval_rate}%")
        
        await db.close()
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or DATABASE_CONFIG
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Conecta ao banco de dados e cria pool de conexões."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(**self.config)
            print(f"✅ Connected to TimescaleDB at {self.config['host']}:{self.config['port']}")
    
    async def close(self) -> None:
        """Fecha o pool de conexões."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("🔌 Disconnected from TimescaleDB")
    
    @asynccontextmanager
    async def connection(self):
        """Context manager para conexão."""
        async with self.pool.acquire() as conn:
            yield conn
    
    # =========================================================================
    # Transactions
    # =========================================================================
    
    async def insert_transaction(self, tx: Transaction) -> int:
        """Insere uma transação e retorna o ID."""
        query = """
            INSERT INTO transactions (
                timestamp, status, amount, currency, auth_code,
                merchant_id, merchant_category, is_anomaly, anomaly_score,
                ml_score, zscore, detection_method
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
        """
        async with self.connection() as conn:
            row = await conn.fetchrow(
                query,
                tx.timestamp, tx.status, tx.amount, tx.currency, tx.auth_code,
                tx.merchant_id, tx.merchant_category, tx.is_anomaly, tx.anomaly_score,
                tx.ml_score, tx.zscore, tx.detection_method
            )
            return row['id']
    
    async def insert_transactions_batch(self, transactions: List[Transaction]) -> int:
        """Insere múltiplas transações em batch. Retorna quantidade inserida."""
        query = """
            INSERT INTO transactions (
                timestamp, status, amount, currency, auth_code,
                merchant_id, merchant_category, is_anomaly, anomaly_score,
                ml_score, zscore, detection_method
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """
        data = [
            (tx.timestamp, tx.status, tx.amount, tx.currency, tx.auth_code,
             tx.merchant_id, tx.merchant_category, tx.is_anomaly, tx.anomaly_score,
             tx.ml_score, tx.zscore, tx.detection_method)
            for tx in transactions
        ]
        async with self.connection() as conn:
            await conn.executemany(query, data)
            return len(data)
    
    async def get_recent_transactions(
        self, 
        limit: int = 100, 
        status: Optional[str] = None,
        only_anomalies: bool = False
    ) -> List[Dict]:
        """Busca transações recentes."""
        query = """
            SELECT * FROM transactions
            WHERE 1=1
        """
        params = []
        param_idx = 1
        
        if status:
            query += f" AND status = ${param_idx}"
            params.append(status)
            param_idx += 1
        
        if only_anomalies:
            query += " AND is_anomaly = TRUE"
        
        query += f" ORDER BY timestamp DESC LIMIT ${param_idx}"
        params.append(limit)
        
        async with self.connection() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    # =========================================================================
    # Anomalies
    # =========================================================================
    
    async def insert_anomaly(self, anomaly: Anomaly) -> int:
        """Insere uma anomalia detectada."""
        query = """
            INSERT INTO anomalies (
                detected_at, anomaly_type, severity, combined_score,
                ml_score, zscore, transaction_count, expected_count,
                time_window_minutes, status, notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id
        """
        async with self.connection() as conn:
            row = await conn.fetchrow(
                query,
                anomaly.detected_at, anomaly.anomaly_type, anomaly.severity,
                anomaly.combined_score, anomaly.ml_score, anomaly.zscore,
                anomaly.transaction_count, anomaly.expected_count,
                anomaly.time_window_minutes, anomaly.status, anomaly.notes
            )
            return row['id']
    
    async def get_active_anomalies(self) -> List[Dict]:
        """Busca anomalias não resolvidas."""
        query = """
            SELECT * FROM anomalies
            WHERE status IN ('open', 'acknowledged')
            ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    ELSE 4 
                END,
                detected_at DESC
        """
        async with self.connection() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def resolve_anomaly(
        self, 
        anomaly_id: int, 
        resolved_by: str, 
        status: str = "resolved",
        notes: Optional[str] = None
    ) -> bool:
        """Marca uma anomalia como resolvida."""
        query = """
            UPDATE anomalies
            SET status = $1, resolved_at = NOW(), resolved_by = $2, notes = COALESCE($3, notes)
            WHERE id = $4
        """
        async with self.connection() as conn:
            result = await conn.execute(query, status, resolved_by, notes, anomaly_id)
            return result == "UPDATE 1"
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    async def get_stats(self, hours: int = 1) -> Stats:
        """Busca estatísticas agregadas das últimas N horas."""
        query = """
            SELECT 
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                COUNT(*) FILTER (WHERE status = 'denied') AS denied,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                COUNT(*) FILTER (WHERE status = 'reversed') AS reversed,
                COUNT(*) FILTER (WHERE is_anomaly = TRUE) AS anomalies,
                COALESCE(SUM(amount), 0) AS total_amount,
                COALESCE(AVG(amount), 0) AS avg_amount
            FROM transactions
            WHERE timestamp > NOW() - ($1 || ' hours')::INTERVAL
        """
        async with self.connection() as conn:
            row = await conn.fetchrow(query, str(hours))
            
            total = row['total'] or 0
            approved = row['approved'] or 0
            approval_rate = (approved / total * 100) if total > 0 else 0
            tx_per_min = total / (hours * 60) if hours > 0 else 0
            
            return Stats(
                total_transactions=total,
                approved=approved,
                denied=row['denied'] or 0,
                failed=row['failed'] or 0,
                reversed=row['reversed'] or 0,
                approval_rate=round(approval_rate, 2),
                anomaly_count=row['anomalies'] or 0,
                total_amount=row['total_amount'],
                avg_amount=row['avg_amount'],
                transactions_per_minute=round(tx_per_min, 2)
            )
    
    async def get_hourly_metrics(self, hours: int = 24) -> List[Dict]:
        """Busca métricas agregadas por hora."""
        query = """
            SELECT * FROM transactions_per_hour
            WHERE bucket > NOW() - ($1 || ' hours')::INTERVAL
            ORDER BY bucket DESC
        """
        async with self.connection() as conn:
            rows = await conn.fetch(query, str(hours))
            return [dict(row) for row in rows]
    
    async def get_minute_metrics(self, minutes: int = 60) -> List[Dict]:
        """Busca métricas agregadas por minuto."""
        query = """
            SELECT * FROM transactions_per_minute
            WHERE bucket > NOW() - ($1 || ' minutes')::INTERVAL
            ORDER BY bucket DESC
        """
        async with self.connection() as conn:
            rows = await conn.fetch(query, str(minutes))
            return [dict(row) for row in rows]
    
    # =========================================================================
    # Anomaly Detection Helpers
    # =========================================================================
    
    async def check_volume_anomaly(
        self, 
        window_minutes: int = 60, 
        threshold: float = 2.5
    ) -> Dict:
        """Verifica se há anomalia de volume usando função do banco."""
        query = "SELECT * FROM check_volume_anomaly($1, $2)"
        async with self.connection() as conn:
            row = await conn.fetchrow(query, window_minutes, threshold)
            return dict(row)
    
    async def get_approval_rate(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Calcula taxa de aprovação para período."""
        start = start_time or (datetime.utcnow() - timedelta(hours=1))
        end = end_time or datetime.utcnow()
        
        query = "SELECT * FROM get_approval_rate($1, $2)"
        async with self.connection() as conn:
            row = await conn.fetchrow(query, start, end)
            return dict(row)
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    async def health_check(self) -> Dict:
        """Verifica saúde da conexão com o banco."""
        try:
            async with self.connection() as conn:
                # Verificar conexão básica
                await conn.fetchval("SELECT 1")
                
                # Contar registros
                tx_count = await conn.fetchval("SELECT COUNT(*) FROM transactions")
                anomaly_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM anomalies WHERE status = 'open'"
                )
                
                return {
                    "status": "healthy",
                    "database": "connected",
                    "transactions_total": tx_count,
                    "open_anomalies": anomaly_count
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }


# =============================================================================
# Singleton Instance
# =============================================================================

_db_instance: Optional[Database] = None

async def get_database() -> Database:
    """Retorna instância singleton do banco."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        await _db_instance.connect()
    return _db_instance


# =============================================================================
# CLI para testes
# =============================================================================

async def main():
    """Teste básico da conexão."""
    db = Database()
    await db.connect()
    
    # Health check
    health = await db.health_check()
    print(f"Health: {health}")
    
    # Inserir transação de teste
    tx = Transaction(
        status="approved",
        amount=Decimal("150.00"),
        merchant_id="MERCHANT_001"
    )
    tx_id = await db.insert_transaction(tx)
    print(f"Inserted transaction ID: {tx_id}")
    
    # Buscar estatísticas
    stats = await db.get_stats(hours=1)
    print(f"Stats (1h): {stats}")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
