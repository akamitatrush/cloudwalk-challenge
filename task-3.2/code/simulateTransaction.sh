#!/bin/bash

echo "🚀 SIMULAÇÃO DE MASSA DE DADOS - 500 EVENTOS"
echo "============================================="
echo ""

API="http://localhost:8001/transaction"

# Contadores
TOTAL=0
NORMAL=0
OUTAGE=0
SPIKE=0
FAILED=0
DENIED=0
REVERSED=0

# FASE 1: Tráfego normal inicial (100 transações)
echo "📊 FASE 1: Tráfego normal (100 transações)..."
for i in {1..100}; do
  COUNT=$((100 + RANDOM % 30))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((NORMAL++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 2: Spike de volume (50 transações)
echo "📈 FASE 2: SPIKE de volume (50 transações)..."
for i in {1..50}; do
  COUNT=$((300 + RANDOM % 200))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((SPIKE++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 3: Volta ao normal (50 transações)
echo "📊 FASE 3: Recuperação (50 transações)..."
for i in {1..50}; do
  COUNT=$((200 + RANDOM % 30))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((NORMAL++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 4: OUTAGE - Volume muito baixo (30 transações)
echo "🚨 FASE 4: OUTAGE simulado (30 transações)..."
for i in {1..30}; do
  COUNT=$((1 + RANDOM % 10))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((OUTAGE++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.2
done
echo ""

# FASE 5: Transações FAILED (40 transações)
echo "❌ FASE 5: Transações FAILED (40 transações)..."
for i in {1..40}; do
  COUNT=$((150 + RANDOM % 40))
  AUTH_CODES=("59" "14" "05" "51")
  AUTH=${AUTH_CODES[$RANDOM % 4]}
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"failed\", \"count\": $COUNT, \"auth_code\": \"$AUTH\"}" > /dev/null
  ((FAILED++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 6: Transações DENIED (40 transações)
echo "🚫 FASE 6: Transações DENIED (40 transações)..."
for i in {1..40}; do
  COUNT=$((80 + RANDOM % 40))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"denied\", \"count\": $COUNT, \"auth_code\": \"51\"}" > /dev/null
  ((DENIED++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 7: Transações REVERSED (30 transações)
echo "🔄 FASE 7: Transações REVERSED (30 transações)..."
for i in {1..30}; do
  COUNT=$((80 + RANDOM % 40))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"reversed\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((REVERSED++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 8: Mix caótico (60 transações)
echo "🎲 FASE 8: Mix caótico (60 transações)..."
for i in {1..60}; do
  RAND=$((RANDOM % 100))
  if [ $RAND -lt 50 ]; then
    # Normal
    COUNT=$((100 + RANDOM % 30))
    STATUS="approved"
    AUTH="00"
    ((NORMAL++))
  elif [ $RAND -lt 65 ]; then
    # Failed
    COUNT=$((80 + RANDOM % 40))
    STATUS="failed"
    AUTH="59"
    ((FAILED++))
  elif [ $RAND -lt 80 ]; then
    # Denied
    COUNT=$((80 + RANDOM % 40))
    STATUS="denied"
    AUTH="51"
    ((DENIED++))
  elif [ $RAND -lt 90 ]; then
    # Low volume
    COUNT=$((5 + RANDOM % 20))
    STATUS="approved"
    AUTH="00"
    ((OUTAGE++))
  else
    # Spike
    COUNT=$((250 + RANDOM % 150))
    STATUS="approved"
    AUTH="00"
    ((SPIKE++))
  fi
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"$STATUS\", \"count\": $COUNT, \"auth_code\": \"$AUTH\"}" > /dev/null
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

# FASE 9: Recuperação final (50 transações normais)
echo "✅ FASE 9: Recuperação final (50 transações)..."
for i in {1..50}; do
  COUNT=$((100 + RANDOM % 30))
  curl -s -X POST $API -H "Content-Type: application/json" \
    -d "{\"status\": \"approved\", \"count\": $COUNT, \"auth_code\": \"00\"}" > /dev/null
  ((NORMAL++))
  ((TOTAL++))
  echo -ne "\r   Progresso: $TOTAL/500"
  sleep 0.1
done
echo ""

echo ""
echo "============================================="
echo "🎉 SIMULAÇÃO COMPLETA!"
echo "============================================="
echo ""
echo "📊 RESUMO:"
echo "   Total:     $TOTAL transações"
echo "   ✅ Normal:   $NORMAL"
echo "   📈 Spike:    $SPIKE"
echo "   🚨 Outage:   $OUTAGE"
echo "   ❌ Failed:   $FAILED"
echo "   🚫 Denied:   $DENIED"
echo "   🔄 Reversed: $REVERSED"
echo ""
echo "🔗 Verificar:"
echo "   Prometheus: http://localhost:9091/alerts"
echo "   Grafana:    http://localhost:3002"
echo "   API Stats:  curl http://localhost:8001/stats | jq"
echo ""