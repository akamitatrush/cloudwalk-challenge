# 🎬 NotebookLM Video Generation Prompt

## Instructions
Upload the MASTER_DOCUMENTATION.md file to NotebookLM, then use this prompt to generate an engaging video summary.

---

## 📋 MAIN PROMPT (Copy this)

```
Create an engaging 8-10 minute video podcast summary of this CloudWalk Monitoring Analyst technical challenge. The tone should be professional yet conversational, like two tech colleagues discussing impressive work.

STRUCTURE:

1. OPENING HOOK (30 seconds)
Start dramatically: "Imagine starting your night shift at a billion-dollar fintech company. You open the daily reports and immediately spot something wrong - three consecutive hours of ZERO transactions during peak business hours. That's exactly what this candidate discovered in their CloudWalk technical challenge."

2. THE CHALLENGE (1 minute)
- CloudWalk is a Brazilian fintech unicorn
- They want "firefighters who use code to stop the fire"
- Simple task: analyze checkout CSVs for anomalies
- But this candidate delivered something extraordinary

3. THE DISCOVERY - TELL THE STORY (2 minutes)
- Night shift perspective at 22:00
- checkout_1.csv looks normal
- checkout_2.csv reveals the problem: 15h, 16h, 17h = ZERO transactions
- This isn't a slow day - complete system outage
- 62 lost transactions during peak hours
- Z-Scores of -2.4 to -2.8 confirming statistical significance

4. THE TECHNICAL DEPTH (2 minutes)
- Multiple detection methods: deviation analysis, Z-Score, thresholds
- SQL queries any analyst could use immediately
- Morning spike discovery at 08h-09h (+574%) - backlog processing
- Shows pattern recognition skills beyond the obvious

5. WHAT MAKES THIS EXTRAORDINARY (2 minutes)
Most candidates submit: a Python script and a chart.
This candidate delivered:
- Complete Grafana dashboard (production-ready)
- Prometheus alert rules with P1/P2/P3 severity
- Alertmanager for Slack, PagerDuty, Email
- Docker Compose stack - one command to run
- Incident report template
- Operational runbook
- Slack communication templates
- PromQL cheatsheet

This isn't a challenge submission - it's an entire monitoring toolkit!

6. AI-AUGMENTED APPROACH (1 minute)
The job asks for AI tool usage. This analysis demonstrates the perfect human-AI partnership:
- AI: Pattern detection, statistical analysis, documentation
- Human: Business context, judgment, communication

7. BUSINESS AWARENESS (1 minute)
Not just technical - business impact:
- Lost transactions = lost revenue (~62 transactions)
- Customer impact during peak hours
- SLA compliance implications
Shows business acumen, not just technical skills

8. CLOSING (1 minute)
"If CloudWalk is looking for someone who doesn't just analyze data but builds complete monitoring ecosystems, who thinks like an operator on the night shift, who sees a simple CSV and envisions the entire incident response framework - they've found that person. This submission transforms a basic data analysis task into a comprehensive demonstration of what a world-class Monitoring Intelligence Analyst delivers."

KEY DATA POINTS TO USE:
- 3-hour outage (15h-17h)
- 62 lost transactions
- Z-Score of -2.8
- +574% morning spike
- 15+ deliverables
- 5 infrastructure components

TONE: Impressed but analytical. Use specific numbers. Make clear this is exceptional work.
```

---

## 🎯 SHORT VERSION (5 minutes)

```
Create a 5-minute podcast about this CloudWalk technical challenge:

1. HOOK: Night shift analyst discovers 3 hours of ZERO transactions
2. TECHNICAL: Z-Scores, SQL queries, statistical methods used
3. EXTRAORDINARY: Complete Grafana + Prometheus + Alertmanager stack delivered
4. INSIGHT: Candidate went from "analyze a CSV" to "here's your monitoring infrastructure"
5. CLOSE: Perfect fit for "firefighters who use code to stop the fire"

Use numbers: 62 lost transactions, Z-Score -2.8, 3-hour outage, 15+ deliverables.
```

---

## 📊 Key Facts Reference

| Fact | Value |
|------|-------|
| Outage Duration | 3 hours (15h-17h) |
| Lost Transactions | ~62 |
| Z-Score Peak | -2.8 |
| Morning Spike | +574% at 08h |
| Total Deliverables | 15+ files |
| Stack Services | 5 (Grafana, Prometheus, Alertmanager, Exporter, Node) |

---

## 📁 Files to Upload

1. MASTER_DOCUMENTATION.md (primary)
2. ANALYSIS_REPORT.md (technical details)
3. INCIDENT_REPORT.md (operational view)

Good luck, irmão! 🚀
