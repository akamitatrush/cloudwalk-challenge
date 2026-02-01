#!/bin/bash
# Injetar 500.000 transações - Ultra Alto Volume
# Otimizado para não bater no rate limit

echo "🚀 Injeção de 500K transações"
echo "⏱️  Estimativa: ~2-3 horas"
echo ""

API_URL="http://localhost:8001/transaction"
TOTAL=500000
COUNT=0

START_TIME=$(date +%s)

while [ $COUNT -lt $TOTAL ]; do
    # Status variado
    RAND=$((RANDOM % 100))
    if [ $RAND -lt 70 ]; then
        STATUS="approved"
    elif [ $RAND -lt 85 ]; then
        STATUS="denied"
    elif [ $RAND -lt 93 ]; then
        STATUS="failed"
    elif [ $RAND -lt 97 ]; then
        STATUS="reversed"
    else
        STATUS="refunded"
    fi
    
    # Volume (5% anomalias)
    if [ $((RANDOM % 100)) -lt 5 ]; then
        VOLUME=$((RANDOM % 10 + 1))
    else
        VOLUME=$((50 + RANDOM % 150))
    fi
    
    # Enviar transação
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"status\": \"$STATUS\", \"count\": $VOLUME}" > /dev/null
    
    COUNT=$((COUNT + 1))
    
    # Progresso a cada 5000
    if [ $((COUNT % 5000)) -eq 0 ]; then
        ELAPSED=$(($(date +%s) - START_TIME + 1))
        RATE=$((COUNT / ELAPSED))
        REMAINING=$(( (TOTAL - COUNT) / (RATE + 1) ))
        echo "📊 $COUNT / $TOTAL ($RATE tx/s) - ETA: ${REMAINING}s"
    fi
    
    # Pausa para não bater rate limit (100 req/min = ~1.6/s)
    sleep 0.7
done

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo ""
echo "✅ Injeção completa!"
echo "📊 Total: $COUNT transações"
echo "⏱️  Tempo: ${TOTAL_TIME}s (~$((TOTAL_TIME/60)) min)"
