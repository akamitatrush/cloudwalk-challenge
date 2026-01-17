# 🚀 CloudWalk Monitoring Analyst Challenge

**Candidato:** Sérgio  
**Vaga:** Monitoring Intelligence Analyst (Night Shift)

---

## 📋 Estrutura do Desafio

| Task | Descrição | Status |
|------|-----------|--------|
| **3.1** | Anomaly Detection Analysis | ✅ Completo |
| **3.2** | Em breve | 🔄 Em andamento |

---

## 🎯 Task 3.1 - Anomaly Detection

### Descoberta Principal
- **Anomalia:** 3 horas consecutivas (15h-17h) com ZERO transações
- **Impacto:** ~62 transações perdidas
- **Causa provável:** Outage do sistema de pagamento

### Ferramentas Utilizadas
- Grafana + Prometheus + Alertmanager
- Metabase + SQL
- Python + Docker
- Google Colab

### 📂 [Ver documentação completa](./task-3.1/docs/MASTER_DOCUMENTATION.md)

---

## 🚀 Quick Start (Task 3.1)
```bash
cd task-3.1/infrastructure
docker compose up -d

# Acessar:
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

---

*"Bombeiros que usam código para apagar incêndios."* 🔥
