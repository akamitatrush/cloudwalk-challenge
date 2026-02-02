#!/bin/bash
echo "🚀 Injeção rápida de transações"
API_URL="http://localhost:8001/transaction"
COUNT=0
while true; do
    RAND=$((RANDOM % 100))
    if [ $RAND -lt 70 ]; then STATUS="approved"
    elif [ $RAND -lt 85 ]; then STATUS="denied"
    elif [ $RAND -lt 93 ]; then STATUS="failed"
    else STATUS="reversed"; fi
    
    VOLUME=$((50 + RANDOM % 150))
    
    curl -s -X POST "$API_URL" -H "Content-Type: application/json" \
        -d "{\"status\": \"$STATUS\", \"count\": $VOLUME}" > /dev/null 2>&1
    
    COUNT=$((COUNT + 1))
    if [ $((COUNT % 100)) -eq 0 ]; then
        echo "📊 $COUNT transações"
    fi
    sleep 0.3
done
