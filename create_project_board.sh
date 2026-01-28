#!/bin/bash

OWNER="akamitatrush"
REPO="akamitatrush/cloudwalk-challenge"

echo "🎯 Creating Project Board for Roadmap v2.0"
echo ""

# Criar o Projeto
echo "📋 Creating project..."
gh project create --owner "$OWNER" --title "Roadmap v2.0 - Transaction Guardian"

echo ""
echo "⚠️  Agora preciso do número do projeto."
echo "    Vá em: https://github.com/users/akamitatrush/projects"
echo "    E veja o número do projeto criado (ex: 1, 2, 3...)"
echo ""
read -p "Digite o número do projeto: " PROJECT_NUMBER

# Adicionar Issues
echo ""
echo "📎 Adding issues to project..."

for i in 1 2 3 4 5 6; do
    echo "   Adding issue #$i..."
    gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "https://github.com/$REPO/issues/$i"
done

echo ""
echo "🎉 Done! View at: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
