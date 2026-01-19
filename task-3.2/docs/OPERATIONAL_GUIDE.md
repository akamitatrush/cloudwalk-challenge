# 🛠️ GUIA OPERACIONAL COMPLETO

**Transaction Guardian - Task 3.2**

Este guia contém TODOS os comandos necessários para operar o sistema.

---

## 📋 ÍNDICE

1. [Docker - Comandos Essenciais](#1-docker---comandos-essenciais)
2. [Logs e Monitoramento](#2-logs-e-monitoramento)
3. [Gerar Massa de Dados](#3-gerar-massa-de-dados)
4. [API - Comandos curl](#4-api---comandos-curl)
5. [Troubleshooting](#5-troubleshooting)
6. [Manutenção](#6-manutenção)
7. [Backup e Restore](#7-backup-e-restore)

---

## 1. DOCKER - COMANDOS ESSENCIAIS

### 🚀 Subir a Stack

```bash
# Navegar até a pasta
cd /home/akametatron/Projetos/cloudwalk-challenge/task-3.2/infrastructure

# Subir todos os containers (primeira vez ou após mudanças)
docker compose up -d --build

# Subir sem rebuild (mais rápido)
docker compose up -d

# Subir e ver logs em tempo real
docker compose up --build
```

### 🛑 Parar a Stack

```bash
# Parar todos os containers (mantém dados)
docker compose stop

# Parar e remover containers (mantém volumes)
docker compose down

# Parar e remover TUDO (containers + volumes + redes)
docker compose down -v --remove-orphans
```

### 🔄 Reiniciar

```bash
# Reiniciar todos
docker compose restart

# Reiniciar serviço específico
docker compose restart guardian-api
docker compose restart guardian-grafana
docker compose restart guardian-prometheus
```

### 📊 Status dos Containers

```bash
# Ver containers rodando
docker ps

# Ver apenas containers do projeto
docker ps | grep guardian

# Ver TODOS os containers (inclusive parados)
docker ps -a | grep guardian

# Ver uso de recursos (CPU/RAM)
docker stats

# Ver uso de recursos dos guardians
docker stats guardian-api guardian-grafana guardian-prometheus
```

### 🔍 Inspecionar Containers

```bash
# Ver detalhes de um container
docker inspect guardian-api

# Ver IP do container
docker inspect guardian-api | grep IPAddress

# Ver variáveis de ambiente
docker inspect guardian-api | grep -A 50 "Env"

# Ver volumes montados
docker inspect guardian-api | grep -A 10 "Mounts"
```

---

## 2. LOGS E MONITORAMENTO

### 📜 Ver Logs

```bash
# Logs de todos os containers
docker compose logs

# Logs em tempo real (follow)
docker compose logs -f

# Logs de um serviço específico
docker compose logs guardian-api
docker compose logs guardian-grafana
docker compose logs guardian-prometheus

# Logs em tempo real de um serviço
docker compose logs -f guardian-api

# Últimas 100 linhas
docker compose logs --tail=100 guardian-api

# Logs com timestamp
docker compose logs -t guardian-api

# Logs desde uma data específica
docker compose logs --since="2025-01-18T15:00:00" guardian-api

# Logs dos últimos 30 minutos
docker compose logs --since=30m guardian-api
```

### 🔎 Filtrar Logs

```bash
# Buscar erros
docker compose logs guardian-api | grep -i error

# Buscar anomalias
docker compose logs guardian-api | grep -i anomal

# Buscar alertas CRITICAL
docker compose logs guardian-api | grep CRITICAL

# Buscar por padrão específico
docker compose logs guardian-api | grep "🚨"

# Contar ocorrências
docker compose logs guardian-api | grep -c "ANOMALIA"
```

### 💾 Salvar Logs em Arquivo

```bash
# Salvar todos os logs
docker compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Salvar logs de um serviço
docker compose logs guardian-api > api_logs.txt

# Salvar e continuar acompanhando
docker compose logs -f guardian-api | tee api_logs.txt
```

---

## 3. GERAR MASSA DE DADOS

### 🎮 Usando o Simulador Python

```bash
# Navegar até o projeto
cd /home/akametatron/Projetos/cloudwalk-challenge/task-3.2

# Modo Stream (transações contínuas por 60 segundos)
python3 -m code.simulator --mode stream --duration 60 --api http://localhost:8001

# Modo Stream com intervalo customizado (1 transação por segundo)
python3 -m code.simulator --mode stream --duration 120 --interval 1 --api http://localhost:8001

# Modo CSV (replay dos dados reais)
python3 -m code.simulator --mode csv --csv data/transactions.csv --api http://localhost:8001

# Modo Incidente - Simular OUTAGE
python3 -m code.simulator --mode incident --incident outage --duration 30 --api http://localhost:8001

# Modo Incidente - Simular SPIKE
python3 -m code.simulator --mode incident --incident spike --duration 30 --api http://localhost:8001
```

### 🔄 Usando curl (Loop Simples)

```bash
# 50 transações normais (1 por segundo)
for i in {1..50}; do
  COUNT=$((100 + RANDOM % 30))
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}"
  echo " Tx $i: count=$COUNT"
  sleep 1
done

# 100 transações rápidas (sem delay)
for i in {1..100}; do
  COUNT=$((100 + RANDOM % 30))
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" &
done
wait
echo "✅ 100 transações enviadas!"
```

### 🚨 Simular Cenários de Anomalia

```bash
# OUTAGE - Volume muito baixo (sistema caiu)
for i in {1..20}; do
  echo "🚨 Injetando OUTAGE $i..."
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d '{"status": "approved", "count": 5, "auth_code": "00"}'
  echo ""
  sleep 1
done

# SPIKE - Volume muito alto (ataque/promoção viral)
for i in {1..20}; do
  echo "📈 Injetando SPIKE $i..."
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d '{"status": "approved", "count": 500, "auth_code": "00"}'
  echo ""
  sleep 1
done

# FALHAS - Transações com erro
for i in {1..10}; do
  echo "❌ Injetando FALHA $i..."
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d '{"status": "failed", "count": 100, "auth_code": "59"}'
  echo ""
  sleep 1
done

# MIX - Cenário realista (normal + anomalias)
for i in {1..30}; do
  if [ $((RANDOM % 10)) -lt 2 ]; then
    # 20% chance de anomalia
    COUNT=$((5 + RANDOM % 20))
    STATUS="failed"
  else
    # 80% normal
    COUNT=$((100 + RANDOM % 30))
    STATUS="approved"
  fi
  curl -s -X POST http://localhost:8001/transaction \
    -H "Content-Type: application/json" \
    -d "{\"status\": \"$STATUS\", \"count\": $COUNT, \"auth_code\": \"00\"}"
  echo " Tx $i: status=$STATUS count=$COUNT"
  sleep 1
done
```

---

## 4. API - COMANDOS CURL

### 📊 Health Check e Status

```bash
# Health check básico
curl http://localhost:8001/health

# Health check formatado
curl -s http://localhost:8001/health | jq

# Estatísticas detalhadas
curl -s http://localhost:8001/stats | jq

# Info da API
curl http://localhost:8001/
```

### 💳 Enviar Transações

```bash
# Transação normal
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 115, "auth_code": "00"}'

# Transação anômala (outage)
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "count": 5, "auth_code": "00"}'

# Transação com falha
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"status": "failed", "count": 100, "auth_code": "59"}'

# Batch (múltiplas transações)
curl -X POST http://localhost:8001/transactions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"status": "approved", "count": 110, "auth_code": "00"},
      {"status": "approved", "count": 115, "auth_code": "00"},
      {"status": "denied", "count": 5, "auth_code": "51"},
      {"status": "approved", "count": 120, "auth_code": "00"}
    ]
  }'
```

### 🔍 Consultar Dados

```bash
# Listar anomalias
curl -s http://localhost:8001/anomalies | jq

# Listar anomalias com filtro
curl -s "http://localhost:8001/anomalies?level=CRITICAL&limit=10" | jq

# Métricas Prometheus
curl http://localhost:8001/metrics

# Métricas em JSON
curl -s http://localhost:8001/metrics/json | jq
```

### 🔧 Administração

```bash
# Resetar sistema (CUIDADO!)
curl -X POST http://localhost:8001/reset

# Ver documentação Swagger
# Abrir no navegador: http://localhost:8001/docs
```

---

## 5. TROUBLESHOOTING

### ❌ Container não sobe

```bash
# Ver logs de erro
docker compose logs guardian-api

# Verificar se porta está em uso
sudo lsof -i :8001
sudo lsof -i :3002
sudo lsof -i :9091

# Matar processo usando a porta
sudo kill -9 $(sudo lsof -t -i:8001)

# Rebuild forçado
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### ❌ Grafana não mostra dados

```bash
# Verificar se Prometheus está coletando
curl "http://localhost:9091/api/v1/query?query=transaction_guardian_total"

# Verificar conectividade entre containers
docker exec guardian-grafana wget -qO- http://guardian-prometheus:9090/api/v1/query?query=up

# Reiniciar Grafana
docker restart guardian-grafana

# Ver logs do Grafana
docker logs guardian-grafana | tail -50
```

### ❌ API não responde

```bash
# Verificar se container está rodando
docker ps | grep guardian-api

# Ver logs de erro
docker logs guardian-api | tail -100

# Testar healthcheck interno
docker exec guardian-api curl -s http://localhost:8000/health

# Reiniciar API
docker restart guardian-api
```

### ❌ Prometheus não coleta métricas

```bash
# Verificar targets
curl http://localhost:9091/api/v1/targets | jq

# Verificar se API expõe métricas
curl http://localhost:8001/metrics

# Ver logs do Prometheus
docker logs guardian-prometheus | tail -50

# Recarregar config do Prometheus
curl -X POST http://localhost:9091/-/reload
```

### ❌ Erro de porta em uso

```bash
# Ver o que está usando a porta
sudo netstat -tlnp | grep 8001
sudo netstat -tlnp | grep 3002
sudo netstat -tlnp | grep 9091

# Alternativa com ss
ss -tlnp | grep 8001

# Matar processo específico
sudo kill -9 <PID>
```

### ❌ Erro de permissão

```bash
# Dar permissão na pasta
sudo chown -R $USER:$USER /home/akametatron/Projetos/cloudwalk-challenge/task-3.2

# Permissão em volumes Docker
sudo chmod -R 777 /home/akametatron/Projetos/cloudwalk-challenge/task-3.2/data
```

---

## 6. MANUTENÇÃO

### 🧹 Limpeza

```bash
# Remover containers parados
docker container prune -f

# Remover imagens não usadas
docker image prune -f

# Remover volumes não usados
docker volume prune -f

# Remover TUDO não usado (CUIDADO!)
docker system prune -af

# Ver uso de disco do Docker
docker system df
```

### 🔄 Atualizar Imagens

```bash
# Pull das imagens mais recentes
docker compose pull

# Rebuild com imagens novas
docker compose up -d --build --pull always
```

### 📊 Verificar Recursos

```bash
# Uso de CPU/RAM dos containers
docker stats --no-stream

# Uso de disco
df -h

# Processos do sistema
htop

# Uso de memória
free -h
```

---

## 7. BACKUP E RESTORE

### 💾 Backup dos Dados

```bash
# Backup do volume do Grafana
docker run --rm \
  -v infrastructure_guardian-grafana-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/grafana_backup_$(date +%Y%m%d).tar.gz /data

# Backup dos dashboards
cp -r dashboards/ dashboards_backup_$(date +%Y%m%d)/

# Backup da configuração
tar czf config_backup_$(date +%Y%m%d).tar.gz infrastructure/
```

### 📥 Restore

```bash
# Restore do volume Grafana
docker run --rm \
  -v infrastructure_guardian-grafana-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/grafana_backup_20250118.tar.gz -C /

# Restore das configs
tar xzf config_backup_20250118.tar.gz
```

---

## 8. COMANDOS RÁPIDOS (CHEAT SHEET)

```bash
# === INICIAR ===
cd /home/akametatron/Projetos/cloudwalk-challenge/task-3.2/infrastructure
docker compose up -d --build

# === VERIFICAR ===
docker ps | grep guardian
curl http://localhost:8001/health

# === LOGS ===
docker compose logs -f guardian-api

# === GERAR DADOS ===
for i in {1..50}; do curl -s -X POST http://localhost:8001/transaction -H "Content-Type: application/json" -d "{\"status\":\"approved\",\"count\":$((100+RANDOM%30)),\"auth_code\":\"00\"}"; sleep 1; done

# === PARAR ===
docker compose down

# === REINICIAR ===
docker compose restart

# === LIMPAR TUDO ===
docker compose down -v --remove-orphans
```

---

## 🌐 URLs DE ACESSO

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API Swagger | http://localhost:8001/docs | - |
| Grafana | http://localhost:3002 | admin / admin |
| Prometheus | http://localhost:9091 | - |
| Métricas | http://localhost:8001/metrics | - |

---

## 📞 SUPORTE

Se algo não funcionar:
1. Verifique os logs: `docker compose logs -f`
2. Reinicie a stack: `docker compose restart`
3. Rebuild completo: `docker compose down -v && docker compose up -d --build`

---

**Autor:** Sérgio  
**Versão:** 1.0  
**Data:** Janeiro 2025
