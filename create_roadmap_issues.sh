#!/bin/bash

# =============================================================================
# 🚀 CloudWalk Challenge - Create Roadmap Issues
# =============================================================================
# Este script cria todas as labels e issues do Roadmap v2.0 no GitHub
# 
# Requisitos:
#   - GitHub CLI instalado (gh)
#   - Autenticado no GitHub (gh auth login)
#
# Uso:
#   chmod +x create_roadmap_issues.sh
#   ./create_roadmap_issues.sh
# =============================================================================

set -e

REPO="akamitatrush/cloudwalk-challenge"

echo "🚀 CloudWalk Challenge - Creating Roadmap Issues"
echo "================================================="
echo ""

# -----------------------------------------------------------------------------
# 1. Criar Labels
# -----------------------------------------------------------------------------
echo "📌 Creating labels..."

# Função para criar label (ignora se já existe)
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"
    
    if gh label create "$name" --repo "$REPO" --color "$color" --description "$description" 2>/dev/null; then
        echo "   ✅ Label '$name' created"
    else
        echo "   ⏭️  Label '$name' already exists"
    fi
}

create_label "roadmap" "0052CC" "Roadmap v2.0"
create_label "phase-1" "7057FF" "Phase 1: Foundation"
create_label "phase-2" "008672" "Phase 2: Performance"
create_label "phase-3" "D93F0B" "Phase 3: Security"
create_label "phase-4" "FBCA04" "Phase 4: MLOps"
create_label "phase-5" "E99695" "Phase 5: Clawdbot"
create_label "phase-6" "0E8A16" "Phase 6: Observability"

echo ""
echo "📝 Creating issues..."
echo ""

# -----------------------------------------------------------------------------
# 2. Issue #1 - Foundation
# -----------------------------------------------------------------------------
echo "   Creating Issue #1: Foundation..."

gh issue create --repo "$REPO" \
    --title "🏗️ [Roadmap] Phase 1: Foundation - Database & Infrastructure" \
    --label "roadmap,phase-1,enhancement" \
    --body '## 📋 Overview
Establish solid data infrastructure to support production-grade operations.

## 🎯 Objectives
- [ ] Migrate from CSV to **TimescaleDB** (time-series optimized)
- [ ] Implement **Redis** caching layer
- [ ] Structured JSON logging with correlation IDs
- [ ] Integration test suite (pytest + testcontainers)
- [ ] CI/CD pipeline (GitHub Actions)

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Query latency | ~500ms | <50ms |
| Data retention | Session only | 90 days |
| Test coverage | 0% | >80% |

## 🔗 Dependencies
- None (first phase)

## ⏱️ Estimated Timeline
2-3 weeks

## 📚 References
- [TimescaleDB Docs](https://docs.timescale.com/)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #1 created"

# -----------------------------------------------------------------------------
# 3. Issue #2 - Performance
# -----------------------------------------------------------------------------
echo "   Creating Issue #2: Performance..."

gh issue create --repo "$REPO" \
    --title "⚡ [Roadmap] Phase 2: Performance - Event-Driven Architecture" \
    --label "roadmap,phase-2,enhancement" \
    --body '## 📋 Overview
Scale the system to handle production transaction volumes with event-driven architecture.

## 🎯 Objectives
- [ ] Introduce **Apache Kafka** for async processing
- [ ] Create dedicated **Worker services** for ML detection
- [ ] Implement **Circuit Breaker** pattern (resilience4j)
- [ ] Configure **Kubernetes HPA** (Horizontal Pod Autoscaler)
- [ ] Connection pooling optimization

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Throughput | ~100 tx/min | 10,000+ tx/min |
| Processing | Synchronous | Event-driven |
| Latency P99 | ~500ms | <100ms |

## 🔗 Dependencies
- Phase 1: Foundation (TimescaleDB, Redis)

## ⏱️ Estimated Timeline
2-3 weeks

## 🏗️ Architecture
```
API → Kafka → Workers → TimescaleDB
              ↓
         Alertmanager
```

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #2 created"

# -----------------------------------------------------------------------------
# 4. Issue #3 - Security
# -----------------------------------------------------------------------------
echo "   Creating Issue #3: Security..."

gh issue create --repo "$REPO" \
    --title "🔒 [Roadmap] Phase 3: Security - Enterprise Authentication & Secrets" \
    --label "roadmap,phase-3,enhancement" \
    --body '## 📋 Overview
Implement enterprise-grade security for production deployment.

## 🎯 Objectives
- [ ] Implement **OAuth2 + JWT** authentication
- [ ] Configure **HashiCorp Vault** for secrets management
- [ ] Add **Rate Limiting** per client
- [ ] Implement **PII Data Masking** in logs
- [ ] Security audit logging

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Authentication | None | OAuth2 + JWT |
| Secrets | .env files | Vault |
| Rate Limiting | None | 1000 req/min |

## 🔗 Dependencies
- Phase 1: Foundation
- Phase 2: Performance (for rate limiting at scale)

## ⏱️ Estimated Timeline
2 weeks

## 🔐 Security Checklist
- [ ] OWASP Top 10 compliance
- [ ] API authentication
- [ ] Secrets rotation
- [ ] Audit trail

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #3 created"

# -----------------------------------------------------------------------------
# 5. Issue #4 - MLOps
# -----------------------------------------------------------------------------
echo "   Creating Issue #4: MLOps..."

gh issue create --repo "$REPO" \
    --title "🤖 [Roadmap] Phase 4: MLOps - Production ML Pipeline" \
    --label "roadmap,phase-4,enhancement" \
    --body '## 📋 Overview
Establish production-grade ML pipeline with model versioning, automated retraining, and drift monitoring.

## 🎯 Objectives
- [ ] Configure **MLflow** for model versioning & registry
- [ ] Create **Airflow DAGs** for automated retraining
- [ ] Implement **A/B testing** framework for models
- [ ] Monitor **model drift** with alerts
- [ ] Implement **Feature Store**

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Model versioning | None | MLflow |
| Retraining | Manual | Automated (weekly) |
| Model comparison | None | A/B testing |
| Drift detection | None | Automated alerts |

## 🔗 Dependencies
- Phase 1: Foundation (TimescaleDB for feature store)
- Phase 2: Performance (Kafka for real-time features)

## ⏱️ Estimated Timeline
2-3 weeks

## 🔄 ML Pipeline
```
Data → Feature Store → Training → MLflow → A/B Test → Production
                         ↑
                    Airflow (scheduled)
```

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #4 created"

# -----------------------------------------------------------------------------
# 6. Issue #5 - Clawdbot
# -----------------------------------------------------------------------------
echo "   Creating Issue #5: Clawdbot 🦞..."

gh issue create --repo "$REPO" \
    --title "🦞 [Roadmap] Phase 5: Clawdbot Integration - AI Operations Assistant" \
    --label "roadmap,phase-5,enhancement" \
    --body '## 📋 Overview
Integrate Clawdbot as an AI-powered operations assistant for night shift monitoring via mobile.

## 🎯 Objectives
- [ ] Install and configure **Clawdbot** locally
- [ ] Create custom **skills** for Transaction Guardian
  - [ ] Status check skill
  - [ ] Alerts listing skill
  - [ ] Runbook execution skill
  - [ ] Shift briefing skill
- [ ] Integrate with **Alertmanager** (webhook)
- [ ] Configure **automatic briefings** at shift changes
- [ ] Setup channels: **WhatsApp** / **Telegram**

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Mobile alerts | None | WhatsApp/Telegram |
| Status check | Dashboard only | Chat command |
| Runbook execution | SSH/Manual | Chat command |
| Shift handoff | Manual notes | Auto briefing |

## 🦞 Example Interaction
```
You (03:00 WhatsApp): "status"

Clawdbot: "✅ Transaction Guardian
├── API: healthy
├── TX/min: 847
├── Approval rate: 95.1%
└── Active alerts: 0

All systems nominal! 🦞"
```

## 🔗 Dependencies
- Phase 1: Foundation (API endpoints)
- Alertmanager configured

## ⏱️ Estimated Timeline
1-2 weeks

## 📚 References
- [Clawdbot GitHub](https://github.com/clawdbot/clawdbot)
- [CLAWDBOT_SECTION.md](./docs/roadmap/CLAWDBOT_SECTION.md)

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #5 created"

# -----------------------------------------------------------------------------
# 7. Issue #6 - Observability
# -----------------------------------------------------------------------------
echo "   Creating Issue #6: Observability..."

gh issue create --repo "$REPO" \
    --title "🔭 [Roadmap] Phase 6: Observability - Distributed Tracing & SLOs" \
    --label "roadmap,phase-6,enhancement" \
    --body '## 📋 Overview
Implement comprehensive observability with distributed tracing and SLO-based alerting.

## 🎯 Objectives
- [ ] Integrate **OpenTelemetry** instrumentation
- [ ] Configure **Jaeger** for distributed tracing
- [ ] Define **SLOs** (Service Level Objectives)
- [ ] Create **SLI dashboards** (Service Level Indicators)
- [ ] Implement **Error Budgets** tracking

## 📊 Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Tracing | None | Full distributed |
| SLO tracking | None | 99.9% availability |
| Error budget | None | Automated alerts |
| MTTD | ~30s | <10s |

## 🔗 Dependencies
- Phase 2: Performance (for tracing across services)
- All previous phases for complete observability

## ⏱️ Estimated Timeline
1-2 weeks

## 📊 SLO Example
```yaml
SLO: Transaction Processing
- Availability: 99.9%
- Latency P99: <200ms
- Error rate: <0.1%
- Error budget: 43.2 min/month
```

---
**Part of Roadmap v2.0** | [View full roadmap](./docs/roadmap/)'

echo "   ✅ Issue #6 created"

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
echo ""
echo "================================================="
echo "🎉 All done!"
echo ""
echo "Created:"
echo "   ✅ 7 labels"
echo "   ✅ 6 issues"
echo ""
echo "View your issues at:"
echo "   https://github.com/$REPO/issues"
echo ""
echo "Next step: Create a Project Board to visualize the roadmap!"
echo "================================================="
