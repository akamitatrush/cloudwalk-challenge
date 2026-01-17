# 🔥 RUNBOOK: Zero Transaction Alert

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│  ALERT: ZERO_TRANSACTIONS_DETECTED                         │
│  SEVERITY: P1 - CRITICAL                                   │
│  SLA: Acknowledge in 5min | Action in 15min                │
└────────────────────────────────────────────────────────────┘
```

---

## 🚨 WHEN THIS ALERT FIRES

You're seeing this because:
- Transactions dropped to **ZERO** for 15+ minutes
- This is happening during **business hours** (10h-22h)
- Historical average shows we should have **10+ transactions/hour**

**THIS IS NOT NORMAL. ACT NOW.**

---

## ⚡ IMMEDIATE ACTIONS (First 5 minutes)

### Step 1: Confirm the Alert
```bash
# Check current transaction count (last 15 min)
SELECT COUNT(*) as tx_count, 
       DATE_TRUNC('minute', created_at) as minute
FROM transactions 
WHERE created_at > NOW() - INTERVAL '15 minutes'
GROUP BY minute
ORDER BY minute DESC;
```

**If count = 0**: Continue to Step 2  
**If count > 0**: False alarm, check data pipeline

### Step 2: Check System Health
```bash
# Quick health check endpoints
curl -s https://api.cloudwalk.io/health | jq .
curl -s https://gateway.cloudwalk.io/status | jq .
curl -s https://db.cloudwalk.io/health | jq .
```

### Step 3: Notify On-Call
```
📱 Send to #incidents-critical:

🚨 [P1] Zero Transactions Alert
Time: [CURRENT_TIME]
Duration: [X] minutes
Last successful tx: [TIMESTAMP]
Investigating...
```

---

## 🔍 INVESTIGATION CHECKLIST

### A. Payment Gateway (Most Common Cause)
- [ ] Check provider status page
- [ ] Review gateway logs
- [ ] Test with sandbox transaction
- [ ] Check SSL certificate expiry

### B. Database Issues
- [ ] Connection pool exhausted?
- [ ] Deadlocks present?
- [ ] Disk space OK?
- [ ] Replication lag?

### C. Application Layer
- [ ] Pod/container crashes?
- [ ] Memory pressure?
- [ ] CPU throttling?
- [ ] Recent deployments?

### D. Network
- [ ] DNS resolution OK?
- [ ] Firewall changes?
- [ ] Load balancer health?

---

## 📊 KEY METRICS TO CHECK (Grafana)

```
Dashboard: Operations > Transaction Health

Panels to check:
1. Transactions per Minute (should be 1-5 tpm minimum)
2. Error Rate (should be < 1%)
3. Latency P99 (should be < 500ms)
4. Gateway Response Codes (look for 5xx spike)
```

### PromQL Queries
```promql
# Transaction rate (should be > 0)
rate(transactions_total[5m])

# Error rate spike
rate(transactions_failed_total[5m]) / rate(transactions_total[5m])

# Gateway latency
histogram_quantile(0.99, rate(gateway_latency_bucket[5m]))
```

---

## 🛠️ COMMON FIXES

### Fix 1: Restart Gateway Connection
```bash
# If gateway timeout detected
kubectl rollout restart deployment/payment-gateway -n production
```

### Fix 2: Clear Connection Pool
```bash
# If DB connection exhausted
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';"
```

### Fix 3: Scale Application
```bash
# If load-related
kubectl scale deployment/checkout-api --replicas=10 -n production
```

---

## 📞 ESCALATION MATRIX

| Time Since Alert | Action |
|-----------------|--------|
| 0-5 min | Acknowledge, start investigation |
| 5-15 min | Notify team lead via Slack |
| 15-30 min | Page on-call SRE |
| 30+ min | Escalate to Engineering Manager |
| 1h+ | Executive notification |

### Contact List
| Role | Slack | Phone |
|------|-------|-------|
| SRE On-Call | @sre-oncall | PagerDuty |
| DB Team | #database-support | - |
| Gateway Team | #payments-gateway | - |
| Eng Manager | @eng-manager | Emergency only |

---

## ✅ RESOLUTION CHECKLIST

When the issue is resolved:

- [ ] Confirm transactions are flowing again
- [ ] Monitor for 15 minutes for stability
- [ ] Update incident channel with resolution
- [ ] Create follow-up ticket for RCA
- [ ] Document what fixed the issue
- [ ] Schedule post-mortem if P1

### Resolution Message Template
```
✅ [RESOLVED] INC-XXXX
Duration: X hours Y minutes  
Root Cause: [BRIEF DESCRIPTION]
Fix Applied: [WHAT WAS DONE]
Customer Impact: [ESTIMATED]
RCA Ticket: [LINK]
```

---

## 📝 POST-INCIDENT

Within 24 hours:
1. Complete RCA document
2. Identify preventive measures
3. Create tickets for improvements
4. Update this runbook if needed

---

**Last Updated**: 2026-01-16  
**Owner**: Monitoring Team  
**Review Cycle**: Monthly
