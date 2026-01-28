#!/usr/bin/env python3
"""
Transaction Guardian v2.0 - CSV to TimescaleDB Migration
=========================================================
Script para migrar dados históricos de CSV para TimescaleDB.

Uso:
    python migrate_csv_to_timescale.py --csv-path ../data/transactions.csv
    
    # Com opções
    python migrate_csv_to_timescale.py \
        --csv-path ../data/transactions.csv \
        --batch-size 1000 \
        --dry-run
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Generator
import csv

# Adicionar path do módulo database
sys.path.insert(0, str(Path(__file__).parent))

from database import Database, Transaction


# =============================================================================
# CSV Parser
# =============================================================================

def parse_csv_row(row: Dict) -> Transaction:
    """
    Converte uma linha do CSV para objeto Transaction.
    Adapte os nomes das colunas conforme seu CSV.
    """
    # Tentar diferentes formatos de timestamp
    timestamp = None
    timestamp_fields = ['timestamp', 'time', 'datetime', 'created_at', 'date']
    
    for field in timestamp_fields:
        if field in row and row[field]:
            try:
                # Tentar diferentes formatos
                for fmt in [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%d/%m/%Y %H:%M:%S',
                    '%Y-%m-%d',
                ]:
                    try:
                        timestamp = datetime.strptime(row[field], fmt)
                        break
                    except ValueError:
                        continue
            except:
                pass
            if timestamp:
                break
    
    if not timestamp:
        timestamp = datetime.utcnow()
    
    # Mapear status
    status_raw = row.get('status', row.get('transaction_status', 'approved')).lower()
    status_map = {
        'approved': 'approved',
        'aprovado': 'approved',
        'denied': 'denied',
        'negado': 'denied',
        'failed': 'failed',
        'falha': 'failed',
        'reversed': 'reversed',
        'estornado': 'reversed',
    }
    status = status_map.get(status_raw, status_raw)
    
    # Amount
    amount = None
    amount_fields = ['amount', 'value', 'valor', 'transaction_amount']
    for field in amount_fields:
        if field in row and row[field]:
            try:
                amount = Decimal(str(row[field]).replace(',', '.').replace('R$', '').strip())
                break
            except:
                pass
    
    # Auth code
    auth_code = row.get('auth_code', row.get('authorization_code', row.get('codigo_autorizacao')))
    
    # Merchant
    merchant_id = row.get('merchant_id', row.get('merchant', row.get('lojista')))
    
    # Anomaly flags (se existirem no CSV)
    is_anomaly = str(row.get('is_anomaly', row.get('anomaly', 'false'))).lower() in ['true', '1', 'yes', 'sim']
    
    anomaly_score = None
    if 'anomaly_score' in row and row['anomaly_score']:
        try:
            anomaly_score = Decimal(str(row['anomaly_score']))
        except:
            pass
    
    return Transaction(
        timestamp=timestamp,
        status=status,
        amount=amount,
        auth_code=auth_code,
        merchant_id=merchant_id,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
    )


def read_csv_in_batches(csv_path: str, batch_size: int = 1000) -> Generator[List[Dict], None, None]:
    """Lê CSV em batches para não estourar memória."""
    batch = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # Detectar delimitador
        sample = f.read(4096)
        f.seek(0)
        
        if ';' in sample and ',' not in sample:
            delimiter = ';'
        else:
            delimiter = ','
        
        reader = csv.DictReader(f, delimiter=delimiter)
        
        for row in reader:
            batch.append(row)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch


def count_csv_rows(csv_path: str) -> int:
    """Conta total de linhas no CSV."""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        return sum(1 for _ in f) - 1  # -1 para header


# =============================================================================
# Migration
# =============================================================================

async def migrate_csv_to_timescale(
    csv_path: str,
    batch_size: int = 1000,
    dry_run: bool = False
) -> Dict:
    """
    Migra dados do CSV para TimescaleDB.
    
    Args:
        csv_path: Caminho do arquivo CSV
        batch_size: Tamanho do batch para inserção
        dry_run: Se True, apenas simula sem inserir
        
    Returns:
        Dict com estatísticas da migração
    """
    stats = {
        "total_rows": 0,
        "inserted": 0,
        "errors": 0,
        "status_counts": {},
        "duration_seconds": 0,
    }
    
    start_time = datetime.now()
    
    # Verificar arquivo
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"📂 Reading CSV: {csv_path}")
    total_rows = count_csv_rows(csv_path)
    print(f"📊 Total rows to migrate: {total_rows:,}")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be inserted")
    
    # Conectar ao banco
    db = Database()
    if not dry_run:
        await db.connect()
    
    try:
        batch_num = 0
        
        for batch in read_csv_in_batches(csv_path, batch_size):
            batch_num += 1
            transactions = []
            
            for row in batch:
                try:
                    tx = parse_csv_row(row)
                    transactions.append(tx)
                    
                    # Contar por status
                    stats["status_counts"][tx.status] = stats["status_counts"].get(tx.status, 0) + 1
                    stats["total_rows"] += 1
                    
                except Exception as e:
                    stats["errors"] += 1
                    print(f"⚠️ Error parsing row: {e}")
            
            # Inserir batch
            if not dry_run and transactions:
                try:
                    inserted = await db.insert_transactions_batch(transactions)
                    stats["inserted"] += inserted
                except Exception as e:
                    stats["errors"] += len(transactions)
                    print(f"❌ Error inserting batch: {e}")
            elif dry_run:
                stats["inserted"] += len(transactions)
            
            # Progress
            progress = (stats["total_rows"] / total_rows) * 100
            print(f"\r   Processing: {stats['total_rows']:,}/{total_rows:,} ({progress:.1f}%)", end="")
        
        print()  # New line after progress
        
    finally:
        if not dry_run:
            await db.close()
    
    stats["duration_seconds"] = (datetime.now() - start_time).total_seconds()
    
    return stats


# =============================================================================
# CLI
# =============================================================================

def print_stats(stats: Dict):
    """Imprime estatísticas da migração."""
    print("\n" + "=" * 50)
    print("📊 MIGRATION SUMMARY")
    print("=" * 50)
    print(f"   Total rows processed: {stats['total_rows']:,}")
    print(f"   Successfully inserted: {stats['inserted']:,}")
    print(f"   Errors: {stats['errors']:,}")
    print(f"   Duration: {stats['duration_seconds']:.2f} seconds")
    
    if stats['duration_seconds'] > 0:
        rate = stats['inserted'] / stats['duration_seconds']
        print(f"   Rate: {rate:.0f} rows/second")
    
    print("\n📈 Status Distribution:")
    for status, count in sorted(stats['status_counts'].items()):
        pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
        print(f"   {status}: {count:,} ({pct:.1f}%)")
    
    print("=" * 50)


async def main():
    parser = argparse.ArgumentParser(
        description="Migrate CSV data to TimescaleDB"
    )
    parser.add_argument(
        "--csv-path", "-f",
        required=True,
        help="Path to CSV file"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=1000,
        help="Batch size for insertion (default: 1000)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simulate migration without inserting"
    )
    
    args = parser.parse_args()
    
    print("🚀 Transaction Guardian - CSV to TimescaleDB Migration")
    print("=" * 50)
    
    try:
        stats = await migrate_csv_to_timescale(
            csv_path=args.csv_path,
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        print_stats(stats)
        
        if stats['errors'] > 0:
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
