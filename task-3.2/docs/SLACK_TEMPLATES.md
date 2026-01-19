# 💬 SLACK TEMPLATES - TRANSACTION GUARDIAN

## Templates de Comunicação para Incidentes

---

## 📑 ÍNDICE

1. [Alertas Iniciais](#1-alertas-iniciais)
2. [Updates de Status](#2-updates-de-status)
3. [Resolução](#3-resolução)
4. [Post-Mortem](#4-post-mortem)
5. [Templates por Severidade](#5-templates-por-severidade)

---

## 1. ALERTAS INICIAIS

### 🚨 P1 - CRITICAL

```
🚨 [P1-CRITICAL] Transaction Volume Critical Drop

📊 Metrics:
• Volume: 12 tx/min (expected: ~115)
• ML Score: 0.92 (Anomaly)
• Z-Score: -3.2

⏰ Detected: 15:10 BRT
⏱️ Duration: 10 minutes

🔍 Status: Investigating
👤 On-Call: @sergio

Dashboard: http://localhost:3002/d/guardian
API Stats: http://localhost:8001/stats

cc: @sre-team @payments-oncall
```

---

### ⚠️ P2 - WARNING

```
⚠️ [P2-WARNING] Low Transaction Volume Detected

📊 Metrics:
• Volume: 45 tx/min (threshold: 50)
• Approval Rate: 88%

⏰ Detected: 14:30 BRT
⏱️ Duration: 5 minutes

🔍 Status: Monitoring
👤 On-Call: @sergio

Will escalate to P1 if persists > 15 min.
```

---

### ℹ️ P3 - INFO

```
ℹ️ [P3-INFO] Volume Spike Detected

📊 Metrics:
• Volume: 280 tx/min (avg: 115)
• All transactions approved

⏰ Time: 16:00 BRT

Likely cause: Marketing campaign active.
Monitoring for system stability.
```

---

## 2. UPDATES DE STATUS

### Update Template

```
📊 [UPDATE] INC-2025-0119-001

⏱️ Duration: 45 minutes
📈 Status: IDENTIFIED

Root Cause: Payment Gateway connection pool exhausted

Actions:
✅ Gateway team notified
✅ Investigating pool settings
🔄 Preparing fix

ETA for resolution: 30-60 minutes

Next update in 15 minutes or on status change.
```

---

### Escalation Update

```
⬆️ [ESCALATED] INC-2025-0119-001 → P1

Reason: Duration exceeded 30 min threshold
Impact: Customer-facing payment failures

Engaging: @engineering-manager @payments-lead

Previous actions:
• Gateway team investigating
• Connection pool issue identified
• Fix in progress

cc: @leadership
```

---

### Mitigation Update

```
🔧 [MITIGATING] INC-2025-0119-001

Fix being deployed:
• Connection pool size: 100 → 200
• Connection timeout: 30s → 10s

Deployment ETA: 10 minutes
Full recovery ETA: 20-30 minutes

Monitoring closely.
```

---

## 3. RESOLUÇÃO

### Resolution Announcement

```
✅ [RESOLVED] INC-2025-0119-001

⏱️ Total Duration: 2h 45min
📊 Impact: ~450 transactions affected

Root Cause: Payment Gateway connection pool exhaustion

Fix Applied:
• Increased pool size (100 → 200)
• Reduced timeout (30s → 10s)

Current Metrics:
• Volume: 112 tx/min ✅
• Approval Rate: 97% ✅
• All systems nominal

📋 Post-mortem scheduled: Tomorrow 10:00 BRT

Thread: [link to full incident thread]
```

---

### Quick Resolution

```
✅ [RESOLVED] LowVolume Alert

Duration: 8 minutes
Cause: Scheduled maintenance window (expected)

No action required. Systems healthy.
```

---

## 4. POST-MORTEM

### Post-Mortem Announcement

```
📋 [POST-MORTEM] INC-2025-0119-001

📅 Meeting: Tomorrow, 10:00 BRT
📍 Location: #incident-postmortems (Huddle)
📄 Doc: [link to post-mortem doc]

Attendees needed:
• @sre-team
• @payments-team
• @backend-team

Agenda:
1. Timeline review
2. Root cause analysis
3. Action items
4. Prevention measures

Please review the incident doc before the meeting.
```

---

### Post-Mortem Summary

```
📋 [POST-MORTEM COMPLETE] INC-2025-0119-001

Key Findings:
• Detection: Transaction Guardian detected in 10 min ✅
• Response: On-call acknowledged in 15 min ✅
• Gap: No circuit breaker for gateway failures

Action Items:
1. 🔴 Implement circuit breaker (Due: Jan 26)
2. 🟡 Add pool metrics to Grafana (Due: Jan 22)
3. ✅ Update runbook (Done)

Full report: [link]
```

---

## 5. TEMPLATES POR SEVERIDADE

### Template: Zero Transactions (P1)

```
🚨 [P1-CRITICAL] Zero Transactions Detected

📊 Alert: ZeroTransactions
• Current Volume: 0 tx/min
• Last transaction: 15:05 BRT

⏰ Detected: 15:10 BRT by Transaction Guardian

Possible causes:
• Complete gateway outage
• Network connectivity issue
• API failure

🔍 Investigating immediately.
👤 On-Call: @sergio

cc: @sre-oncall @payments-oncall @backend-oncall
```

---

### Template: High Failure Rate (P1)

```
🚨 [P1-CRITICAL] High Transaction Failure Rate

📊 Metrics:
• Failure Rate: 35% (threshold: 10%)
• Auth Code: 59 (Fraud Suspected) - 80%

⏰ Detected: 14:20 BRT
⏱️ Duration: 5 minutes

Possible causes:
• Fraud detection too aggressive
• Gateway issues
• Card network problems

🔍 Status: Investigating
👤 On-Call: @sergio

cc: @fraud-team @payments-oncall
```

---

### Template: Volume Spike (P2)

```
⚠️ [P2-WARNING] Volume Spike Detected

📊 Metrics:
• Current: 350 tx/min
• Average: 115 tx/min
• Increase: +204%

⏰ Detected: 16:00 BRT

Known events:
• ❓ Marketing campaign?
• ❓ Flash sale?
• ❓ Potential attack?

Checking with marketing team.
Monitoring system resources.

cc: @marketing @security
```

---

### Template: Low Approval Rate (P1)

```
🚨 [P1-CRITICAL] Low Approval Rate

📊 Metrics:
• Approval Rate: 72% (threshold: 90%)
• Denials: 25% (auth_code: 51)
• Failures: 3%

⏰ Detected: 11:30 BRT

Auth Code 51 = Insufficient Funds
Unusual spike - investigating.

Possible causes:
• Acquirer routing issue
• Fraud rules too strict
• Issuer problems

cc: @payments-oncall @risk-team
```

---

## 📝 QUICK REFERENCE

### Emoji Guide

| Emoji | Meaning |
|-------|---------|
| 🚨 | Critical/P1 |
| ⚠️ | Warning/P2 |
| ℹ️ | Info/P3 |
| ✅ | Resolved/Done |
| 🔄 | In Progress |
| 🔍 | Investigating |
| 📊 | Metrics/Data |
| ⏰ | Time |
| 👤 | Person |
| 📋 | Document |

### Status Keywords

| Status | When to Use |
|--------|-------------|
| INVESTIGATING | Just started looking |
| IDENTIFIED | Know the cause |
| MITIGATING | Fix in progress |
| MONITORING | Fix deployed, watching |
| RESOLVED | Fully recovered |

---

*Templates Version: 1.0*  
*Last Updated: 2025-01-19*
