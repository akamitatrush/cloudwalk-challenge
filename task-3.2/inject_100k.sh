#!/bin/bash
# Injetar 100.000 transações - Alto Volume

echo "🚀 Iniciando injeção de 100K transações..."
echo ""

API_URL="http://localhost:8001/transaction"
TOTAL=100000
COUNT=0
BATCH=100

START_TIME=$(date +%s)

while [ $COUNT -lt $TOTAL ]; do
    # Enviar em paralelo (10 por vez)
    for j in {1..10}; do
        STATUS_RAND=$((RANDOM % 100))
        
        if [ $STATUS_RAND -lt 70 ]; then
            STATUS="approved"
        elif [ $STATUS_RAND -lt 85 ]; then
            STATUS="denied"
        elif [ $STATUS_RAND -lt 93 ]; then
            STATUS="failed"
        elif [ $STATUS_RAND -lt 97 ]; then
            STATUS="reversed"
        else
            STATUS="refunded"
        fi
        
        # Volume variado
        if [ $((RANDOM % 100)) -lt 5 ]; then
            # 5% anomalias
            VOLUME=$((RANDOM % 10 + 1))
        else
            VOLUME=$((50 + RANDOM % 150))
        fi
        
        curl -s -X POST "$API_URL" \
            -H "Content-Type: application/json" \
            -d "{\"status\": \"$STATUS\", \"count\": $VOLUME}" > /dev/null &
    done
    
    wait
    COUNT=$((COUNT + 10))
    
    # Progresso a cada 1000
    if [ $((COUNT % 1000)) -eq 0 ]; then
        ELAPSED=$(($(date +%s) - START_TIME + 1))
        RATE=$((COUNT / ELAPSED))
        echo "📊 $COUNT / $TOTAL ($RATE tx/s)"
    fi
done

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME + 1))

echo ""
echo "✅ Injeção completa!"
echo "📊 Total: $COUNT transações"
echo "⏱️  Tempo: ${TOTAL_TIME}s"
echo "🚀 Taxa: $((COUNT / TOTAL_TIME)) tx/s"
