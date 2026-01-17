#!/usr/bin/env python3
"""
CloudWalk Automated Alert System
Real-time anomaly detection for checkout transactions

This script monitors transaction data and triggers alerts when anomalies are detected.
Designed for Night Shift Monitoring Analysts.

Author: Sérgio
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

class AlertSeverity(Enum):
    CRITICAL = "P1"
    HIGH = "P2"
    MEDIUM = "P3"
    LOW = "P4"
    INFO = "P5"

@dataclass
class AlertConfig:
    """Alert thresholds configuration"""
    # Zero transaction threshold
    zero_tx_threshold_minutes: int = 15
    
    # Deviation thresholds
    critical_deviation_pct: float = -100.0  # Zero sales
    high_deviation_pct: float = -75.0       # 75% below normal
    medium_deviation_pct: float = -50.0     # 50% below normal
    
    # Spike thresholds
    spike_threshold_pct: float = 200.0      # 200% above normal
    
    # Z-Score threshold
    z_score_threshold: float = 2.0
    
    # Business hours (for alerting)
    business_hours_start: int = 10
    business_hours_end: int = 22


@dataclass
class Alert:
    """Alert data structure"""
    severity: AlertSeverity
    title: str
    message: str
    metric_name: str
    current_value: float
    expected_value: float
    deviation_pct: float
    timestamp: str
    hour: int


# =============================================================================
# ANOMALY DETECTION ENGINE
# =============================================================================

class AnomalyDetector:
    """Core anomaly detection logic"""
    
    def __init__(self, config: AlertConfig = AlertConfig()):
        self.config = config
        self.alerts: List[Alert] = []
    
    def calculate_z_score(self, value: float, mean: float, std: float) -> float:
        """Calculate Z-score for a value"""
        if std == 0 or pd.isna(std):
            return 0.0
        return (value - mean) / std
    
    def calculate_deviation(self, current: float, expected: float) -> float:
        """Calculate percentage deviation"""
        if expected == 0:
            if current == 0:
                return 0.0
            return 100.0  # Something vs nothing
        return ((current - expected) / expected) * 100
    
    def classify_severity(self, current: float, expected: float, 
                         deviation: float, hour: int) -> AlertSeverity:
        """Determine alert severity based on multiple factors"""
        
        is_business_hours = (self.config.business_hours_start <= hour <= 
                            self.config.business_hours_end)
        
        # CRITICAL: Zero during business hours when we expect transactions
        if current == 0 and expected > 5 and is_business_hours:
            return AlertSeverity.CRITICAL
        
        # HIGH: Severe drop during business hours
        if deviation <= self.config.high_deviation_pct and is_business_hours:
            return AlertSeverity.HIGH
        
        # MEDIUM: Significant drop or spike
        if deviation <= self.config.medium_deviation_pct:
            return AlertSeverity.MEDIUM
        
        if deviation >= self.config.spike_threshold_pct:
            return AlertSeverity.MEDIUM
        
        # LOW: Minor deviations outside business hours
        if abs(deviation) > 50:
            return AlertSeverity.LOW
        
        return AlertSeverity.INFO
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Alert]:
        """
        Main detection method
        Expects DataFrame with columns: time, today, avg_last_week
        """
        self.alerts = []
        
        # Calculate statistics
        df = df.copy()
        df['hour'] = df['time'].str.replace('h', '').astype(int)
        df['deviation'] = df.apply(
            lambda row: self.calculate_deviation(row['today'], row['avg_last_week']), 
            axis=1
        )
        
        # Calculate rolling statistics for Z-score
        std_dev = df['today'].std()
        mean_val = df['today'].mean()
        df['z_score'] = df['today'].apply(
            lambda x: self.calculate_z_score(x, mean_val, std_dev)
        )
        
        # Check each hour for anomalies
        for _, row in df.iterrows():
            severity = self.classify_severity(
                row['today'], 
                row['avg_last_week'],
                row['deviation'],
                row['hour']
            )
            
            # Only create alerts for significant events
            if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM]:
                alert = self._create_alert(row, severity)
                self.alerts.append(alert)
        
        return self.alerts
    
    def _create_alert(self, row: pd.Series, severity: AlertSeverity) -> Alert:
        """Create an alert object from a data row"""
        
        if row['today'] == 0:
            title = f"🚨 ZERO TRANSACTIONS @ {row['time']}"
            message = f"No transactions recorded at {row['time']}. Expected ~{row['avg_last_week']:.0f} based on weekly average."
        elif row['deviation'] < 0:
            title = f"⚠️ LOW TRANSACTIONS @ {row['time']}"
            message = f"Transactions at {row['time']} are {abs(row['deviation']):.1f}% below normal."
        else:
            title = f"📈 SPIKE DETECTED @ {row['time']}"
            message = f"Transactions at {row['time']} are {row['deviation']:.1f}% above normal."
        
        return Alert(
            severity=severity,
            title=title,
            message=message,
            metric_name="checkout_transactions",
            current_value=row['today'],
            expected_value=row['avg_last_week'],
            deviation_pct=row['deviation'],
            timestamp=datetime.now().isoformat(),
            hour=row['hour']
        )


# =============================================================================
# ALERT FORMATTER (for different outputs)
# =============================================================================

class AlertFormatter:
    """Format alerts for different output channels"""
    
    @staticmethod
    def to_slack(alert: Alert) -> str:
        """Format alert for Slack"""
        emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "⚡",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📊"
        }
        
        return f"""
{emoji[alert.severity]} [{alert.severity.value}] {alert.title}

📊 Current: {alert.current_value:.0f} | Expected: {alert.expected_value:.1f}
📉 Deviation: {alert.deviation_pct:.1f}%
⏰ Time: {alert.timestamp}

{alert.message}
"""
    
    @staticmethod
    def to_json(alert: Alert) -> dict:
        """Format alert as JSON"""
        return {
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "metric": alert.metric_name,
            "current_value": alert.current_value,
            "expected_value": alert.expected_value,
            "deviation_percent": alert.deviation_pct,
            "timestamp": alert.timestamp,
            "hour": alert.hour
        }
    
    @staticmethod
    def to_prometheus(alert: Alert) -> str:
        """Format as Prometheus alertmanager compatible"""
        return f"""
- alert: {alert.metric_name}_anomaly
  expr: checkout_transactions_hourly{{hour="{alert.hour}"}} == {alert.current_value}
  for: 5m
  labels:
    severity: {alert.severity.name.lower()}
  annotations:
    summary: "{alert.title}"
    description: "{alert.message}"
"""


# =============================================================================
# NOTIFICATION SYSTEM (Mock Implementation)
# =============================================================================

class NotificationService:
    """Send notifications to various channels"""
    
    def __init__(self):
        self.sent_alerts: List[dict] = []
    
    def send_slack(self, alert: Alert, channel: str = "#incidents-critical"):
        """Send to Slack (mock)"""
        message = AlertFormatter.to_slack(alert)
        self.sent_alerts.append({
            "channel": "slack",
            "destination": channel,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[SLACK -> {channel}] Alert sent: {alert.title}")
        return True
    
    def send_pagerduty(self, alert: Alert):
        """Send to PagerDuty (mock)"""
        payload = AlertFormatter.to_json(alert)
        self.sent_alerts.append({
            "channel": "pagerduty",
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[PAGERDUTY] Page sent: {alert.title}")
        return True
    
    def send_email(self, alert: Alert, recipients: List[str]):
        """Send email (mock)"""
        self.sent_alerts.append({
            "channel": "email",
            "recipients": recipients,
            "subject": alert.title,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[EMAIL] Sent to {len(recipients)} recipients: {alert.title}")
        return True
    
    def route_alert(self, alert: Alert):
        """Route alert based on severity"""
        if alert.severity == AlertSeverity.CRITICAL:
            self.send_slack(alert, "#incidents-critical")
            self.send_pagerduty(alert)
            self.send_email(alert, ["oncall@cloudwalk.io", "manager@cloudwalk.io"])
        elif alert.severity == AlertSeverity.HIGH:
            self.send_slack(alert, "#incidents-critical")
            self.send_pagerduty(alert)
        elif alert.severity == AlertSeverity.MEDIUM:
            self.send_slack(alert, "#monitoring-alerts")
        else:
            self.send_slack(alert, "#monitoring-info")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_analysis(csv_path: str) -> Tuple[List[Alert], pd.DataFrame]:
    """Run full analysis on a CSV file"""
    
    print("=" * 60)
    print("CLOUDWALK AUTOMATED ALERT SYSTEM")
    print("=" * 60)
    print(f"\n📂 Loading data from: {csv_path}")
    
    # Load data
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows")
    
    # Initialize detector
    config = AlertConfig()
    detector = AnomalyDetector(config)
    
    # Run detection
    print("\n🔍 Running anomaly detection...")
    alerts = detector.detect_anomalies(df)
    
    # Print summary
    print(f"\n📊 DETECTION RESULTS")
    print("-" * 40)
    
    critical = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
    high = len([a for a in alerts if a.severity == AlertSeverity.HIGH])
    medium = len([a for a in alerts if a.severity == AlertSeverity.MEDIUM])
    
    print(f"🔴 CRITICAL (P1): {critical}")
    print(f"🟠 HIGH (P2): {high}")
    print(f"🟡 MEDIUM (P3): {medium}")
    
    # Send notifications
    if alerts:
        print("\n📤 SENDING NOTIFICATIONS")
        print("-" * 40)
        notifier = NotificationService()
        for alert in alerts:
            notifier.route_alert(alert)
    
    # Print detailed alerts
    print("\n📋 ALERT DETAILS")
    print("-" * 40)
    for alert in alerts:
        print(AlertFormatter.to_slack(alert))
    
    return alerts, df


if __name__ == "__main__":
    import sys
    
    # Default to checkout_2 (the one with anomalies)
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/checkout_2.csv"
    
    alerts, df = run_analysis(csv_path)
    
    # Export alerts to JSON
    if alerts:
        alerts_json = [AlertFormatter.to_json(a) for a in alerts]
        with open("/home/claude/cloudwalk_challenge/incident_report/alerts_export.json", "w") as f:
            json.dump(alerts_json, f, indent=2)
        print("\n✅ Alerts exported to alerts_export.json")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
