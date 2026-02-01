#!/bin/bash
# Injetar 5000 transações variadas

echo "🚀 Iniciando injeção de 5000 transações..."
echo ""

API_URL="http://localhost:8001/transaction"
TOTAL=5000
COUNT=0

# Função para gerar transação
generate_transaction() {
    local hour=$((RANDOM % 24))
    local status_rand=$((RANDOM % 100))
    local count
    local status
    
    # Distribuição realista de status
    if [ $status_rand -lt 70 ]; then
        status="approved"
    elif [ $status_rand -lt 85 ]; then
        status="denied"
    elif [ $status_rand -lt 93 ]; then
        status="failed"
    elif [ $status_rand -lt 97 ]; then
        status="reversed"
    else
        status="refunded"
    fi
    
    # Volume baseado na hora (padrão realista)
    if [ $hour -ge 9 ] && [ $hour -le 18 ]; then
        # Horário comercial - alto volume
        count=$((80 + RANDOM % 120))
    elif [ $hour -ge 19 ] && [ $hour -le 23 ]; then
        # Noite - volume médio
        count=$((50 + RANDOM % 80))
    else
        # Madrugada - baixo volume
        count=$((10 + RANDOM % 40))
    fi
    
    # 5% de chance de anomalia (volume muito alto ou baixo)
    if [ $((RANDOM % 100)) -lt 5 ]; then
        if [ $((RANDOM % 2)) -eq 0 ]; then
            count=$((200 + RANDOM % 100))  # Spike
        else
            count=$((1 + RANDOM % 10))      # Drop
        fi
    fi
    
    echo "{\"status\": \"$status\", \"count\": $count}"
}

# Loop de injeção
START_TIME=$(date +%s)

for i in $(seq 1 $TOTAL); do
    TX=$(generate_transaction)
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$TX" > /dev/null
    
    COUNT=$((COUNT + 1))
    
    # Mostrar progresso a cada 100
    if [ $((COUNT % 100)) -eq 0 ]; then
        ELAPSED=$(($(date +%s) - START_TIME))
        RATE=$((COUNT / (ELAPSED + 1)))
        echo "📊 Progresso: $COUNT/$TOTAL ($RATE tx/s)"
    fi
    
    # Pequena pausa para não sobrecarregar
    if [ $((COUNT % 50)) -eq 0 ]; then
        sleep 0.1
    fi
done

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo ""
echo "✅ Injeção completa!"
echo "📊 Total: $COUNT transações"
echo "⏱️  Tempo: ${TOTAL_TIME}s"
echo "🚀 Taxa: $((COUNT / (TOTAL_TIME + 1))) tx/s"
