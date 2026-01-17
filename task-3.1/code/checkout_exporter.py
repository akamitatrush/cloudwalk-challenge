#!/usr/bin/env python3
"""
CloudWalk Checkout Metrics Exporter
Exposes checkout CSV data as Prometheus metrics

This exporter reads checkout data from CSV files and exposes them
as Prometheus metrics for scraping.

Author: Sérgio
Version: 1.0

Usage:
    python checkout_exporter.py [--port 8000] [--csv-path /path/to/csv]

Metrics exposed:
    - checkout_transactions_hourly{hour, period, dataset}
    - checkout_transactions_current
    - checkout_transactions_avg_week
    - checkout_transactions_total_today
    - checkout_transactions_total_yesterday
    - checkout_anomaly_status{hour, status}
    - checkout_last_update_timestamp
"""

import time
import argparse
from datetime import datetime
from typing import Dict, List
import pandas as pd
from prometheus_client import start_http_server, Gauge, Info, Counter, REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

# =============================================================================
# METRICS DEFINITIONS
# =============================================================================

# Hourly transactions by period
HOURLY_TRANSACTIONS = Gauge(
    'checkout_transactions_hourly',
    'Hourly transaction count',
    ['hour', 'period', 'dataset']
)

# Current hour transactions
CURRENT_TRANSACTIONS = Gauge(
    'checkout_transactions_current',
    'Current hour transaction count',
    ['dataset']
)

# Weekly average for current hour
AVG_WEEK_TRANSACTIONS = Gauge(
    'checkout_transactions_avg_week',
    'Weekly average for current hour',
    ['dataset']
)

# Daily totals
TOTAL_TODAY = Gauge(
    'checkout_transactions_total_today',
    'Total transactions today',
    ['dataset']
)

TOTAL_YESTERDAY = Gauge(
    'checkout_transactions_total_yesterday',
    'Total transactions yesterday',
    ['dataset']
)

# Anomaly status
ANOMALY_STATUS = Gauge(
    'checkout_anomaly_status',
    'Anomaly status by hour (1=anomaly, 0=normal)',
    ['hour', 'status', 'dataset']
)

# Deviation percentage
DEVIATION_PCT = Gauge(
    'checkout_deviation_percentage',
    'Deviation from weekly average (%)',
    ['hour', 'dataset']
)

# Last update timestamp
LAST_UPDATE = Gauge(
    'checkout_last_update_timestamp',
    'Timestamp of last data update'
)

# Exporter info
EXPORTER_INFO = Info(
    'checkout_exporter',
    'Information about the checkout exporter'
)


# =============================================================================
# DATA PROCESSING
# =============================================================================

def load_csv_data(csv_path: str) -> pd.DataFrame:
    """Load and process CSV data"""
    df = pd.read_csv(csv_path)
    df['hour'] = df['time'].str.replace('h', '').astype(int)
    return df


def calculate_anomaly_status(row: pd.Series) -> str:
    """Determine anomaly status for a row"""
    if row['today'] == 0 and row['avg_last_week'] > 5:
        return 'CRITICAL'
    
    if row['avg_last_week'] > 0:
        deviation = ((row['today'] - row['avg_last_week']) / row['avg_last_week']) * 100
        if deviation < -50:
            return 'HIGH'
        elif deviation > 200:
            return 'SPIKE'
    
    return 'NORMAL'


def calculate_deviation(row: pd.Series) -> float:
    """Calculate percentage deviation from weekly average"""
    if row['avg_last_week'] == 0:
        return 0.0
    return ((row['today'] - row['avg_last_week']) / row['avg_last_week']) * 100


def update_metrics(df: pd.DataFrame, dataset_name: str):
    """Update all Prometheus metrics from DataFrame"""
    
    current_hour = datetime.now().hour
    
    # Clear previous metrics for this dataset
    # (In production, you'd want more sophisticated metric management)
    
    # Update hourly metrics
    for _, row in df.iterrows():
        hour_str = f"{row['hour']:02d}h"
        
        # Transactions by period
        HOURLY_TRANSACTIONS.labels(
            hour=hour_str, 
            period='today', 
            dataset=dataset_name
        ).set(row['today'])
        
        HOURLY_TRANSACTIONS.labels(
            hour=hour_str, 
            period='yesterday', 
            dataset=dataset_name
        ).set(row['yesterday'])
        
        HOURLY_TRANSACTIONS.labels(
            hour=hour_str, 
            period='same_day_last_week', 
            dataset=dataset_name
        ).set(row['same_day_last_week'])
        
        HOURLY_TRANSACTIONS.labels(
            hour=hour_str, 
            period='avg_last_week', 
            dataset=dataset_name
        ).set(row['avg_last_week'])
        
        HOURLY_TRANSACTIONS.labels(
            hour=hour_str, 
            period='avg_last_month', 
            dataset=dataset_name
        ).set(row['avg_last_month'])
        
        # Anomaly status
        status = calculate_anomaly_status(row)
        ANOMALY_STATUS.labels(
            hour=hour_str, 
            status=status, 
            dataset=dataset_name
        ).set(row['today'])
        
        # Deviation percentage
        deviation = calculate_deviation(row)
        DEVIATION_PCT.labels(
            hour=hour_str, 
            dataset=dataset_name
        ).set(deviation)
    
    # Current hour metrics (simulate with a specific hour for demo)
    # In production, use: current_row = df[df['hour'] == current_hour].iloc[0]
    # For demo, we'll use hour 16 to show the anomaly
    demo_hour = 16
    current_row = df[df['hour'] == demo_hour].iloc[0]
    
    CURRENT_TRANSACTIONS.labels(dataset=dataset_name).set(current_row['today'])
    AVG_WEEK_TRANSACTIONS.labels(dataset=dataset_name).set(current_row['avg_last_week'])
    
    # Daily totals
    TOTAL_TODAY.labels(dataset=dataset_name).set(df['today'].sum())
    TOTAL_YESTERDAY.labels(dataset=dataset_name).set(df['yesterday'].sum())
    
    # Update timestamp
    LAST_UPDATE.set(time.time())


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Checkout Metrics Exporter')
    parser.add_argument('--port', type=int, default=8000, help='Port to expose metrics')
    parser.add_argument('--csv-path', type=str, default='/data/checkout_2.csv', 
                       help='Path to CSV file')
    parser.add_argument('--dataset-name', type=str, default='checkout_2',
                       help='Dataset name label')
    parser.add_argument('--refresh-interval', type=int, default=60,
                       help='Refresh interval in seconds')
    args = parser.parse_args()
    
    # Set exporter info
    EXPORTER_INFO.info({
        'version': '1.0.0',
        'csv_path': args.csv_path,
        'dataset': args.dataset_name
    })
    
    # Start HTTP server
    print(f"Starting Checkout Metrics Exporter on port {args.port}")
    start_http_server(args.port)
    
    print(f"Loading data from {args.csv_path}")
    print(f"Refresh interval: {args.refresh_interval}s")
    print(f"Metrics available at http://localhost:{args.port}/metrics")
    
    # Main loop
    while True:
        try:
            df = load_csv_data(args.csv_path)
            update_metrics(df, args.dataset_name)
            print(f"[{datetime.now().isoformat()}] Metrics updated successfully")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error updating metrics: {e}")
        
        time.sleep(args.refresh_interval)


if __name__ == '__main__':
    main()
