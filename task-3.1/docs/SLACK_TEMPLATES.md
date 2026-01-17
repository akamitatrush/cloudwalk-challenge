# 📱 SLACK COMMUNICATION TEMPLATES

## For Night Shift Monitoring Analysts

---

## 🚨 INITIAL ALERT MESSAGE

**Channel**: #incidents-critical

```
🚨 [P1-CRITICAL] Transaction Outage Detected

⏰ Time: 2026-01-16 22:15 BRT
📍 Affected: POS Checkout System
⚠️ Issue: ZERO transactions from 15h to 17h

📊 Quick Stats:
• Duration: 3 hours
• Lost Transactions: ~62 estimated
• Current Status: Recovered (investigating root cause)

🔍 Evidence:
• checkout_2 shows 0 tx at 15h, 16h, 17h
• checkout_1 (control) shows normal pattern
• Recovery started at 18h

👤 Assigned: Sérgio (Night Shift)
📋 Incident: INC-2026-0116-001

Next update in 30 minutes.
```

---

## 📊 STATUS UPDATE MESSAGE

**Channel**: #incidents-critical

```
📊 [UPDATE] INC-2026-0116-001

⏰ Update Time: 22:45 BRT
📍 Status: INVESTIGATING

🔍 Investigation Progress:
✅ Data analysis complete
✅ Anomaly confirmed (Z-Score > 2)
✅ Visualizations generated
⏳ Reviewing system logs
⏳ Checking payment gateway status

📈 Key Finding:
The outage pattern (exact zero) suggests system failure, 
not gradual degradation. Most likely cause:
1. Payment gateway outage (70% probability)
2. API server crash (20%)
3. Database issue (10%)

🎯 Next Steps:
• Correlate with infrastructure metrics
• Check external service status pages
• Review deployment history for 14h-15h

Next update: 23:15 BRT
```

---

## ✅ RESOLUTION MESSAGE

**Channel**: #incidents-critical

```
✅ [RESOLVED] INC-2026-0116-001

⏰ Resolved: 2026-01-16 23:30 BRT
📍 Duration: [Total incident duration]

📋 Summary:
• Issue: Complete transaction outage (15h-17h)
• Impact: ~62 transactions lost
• Root Cause: [To be confirmed in RCA]

🛠️ Actions Taken:
1. Detected anomaly via automated analysis
2. Confirmed with statistical methods
3. Generated evidence documentation
4. Created incident report

📎 Documentation:
• Incident Report: [link]
• Analysis Charts: [link]
• RCA Ticket: JIRA-XXXX (to be completed)

📅 Post-Mortem: Scheduled for [DATE]

Thanks team! 🙏
```

---

## 📞 ESCALATION MESSAGE

**Channel**: DM to Manager or #escalations

```
📞 [ESCALATION] INC-2026-0116-001

Hi @manager,

Escalating a P1 incident that needs visibility:

🚨 Issue: 3-hour complete outage (15h-17h)
💰 Impact: ~62 lost transactions during peak hours
⏰ Detection: 22:15 (during data review)

Why escalating:
• High business impact (peak hours)
• Pattern suggests infrastructure issue
• May need cross-team coordination

Current status: Investigating root cause
Need: Approval to engage [Gateway Team/SRE/DB Team]

Documents attached for reference.

Sérgio (Night Shift)
```

---

## 🌅 SHIFT HANDOFF MESSAGE

**Channel**: #monitoring-handoff

```
🌅 NIGHT SHIFT HANDOFF - 2026-01-17 08:00

👤 From: Sérgio (Night)
👤 To: [Day Shift Analyst]

📋 ACTIVE INCIDENTS:
• INC-2026-0116-001 - Transaction Outage (INVESTIGATING)
  └─ RCA in progress, need log analysis for 15h-17h

📊 OVERNIGHT SUMMARY:
• checkout_1: Normal operation ✅
• checkout_2: Anomaly detected and documented 🚨
• Alerts triggered: 1 (P1)
• Alerts resolved: 0

📎 DOCUMENTS CREATED:
• Incident Report: [link]
• Analysis Charts: [link]
• SQL Queries: [link]
• Runbook updated: RUNBOOK.md

⚠️ ATTENTION NEEDED:
1. Complete RCA - need system logs
2. Verify payment gateway status history
3. Check if similar pattern in other POS groups

📞 I'm available on Slack until 09:00 for questions.

Have a good shift! ☀️
```

---

## 💡 BEST PRACTICES

### DO:
- Be concise and factual
- Use emojis for visual scanning
- Include time in BRT
- Tag relevant people
- Provide next update time

### DON'T:
- Speculate without data
- Use jargon without context
- Forget to update status
- Leave incidents hanging
- Skip the handoff message
