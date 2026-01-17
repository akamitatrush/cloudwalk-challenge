# CloudWalk Challenge - Task 3.1: A Jornada de um Analista de Monitoramento

## Sobre o Candidato

Meu nome é Sérgio, tenho 31 anos e estou me candidatando para a vaga de **Monitoring Intelligence Analyst (Night Shift)** na CloudWalk. Tenho mais de 14 anos de experiência em TI, incluindo quase 7 anos trabalhando com sistemas de pagamento na TIVIT/Cielo. Atualmente trabalho na Matera, uma fintech brasileira, no turno da noite monitorando sistemas críticos de transações financeiras.

A vaga da CloudWalk pede "bombeiros que usam código para apagar incêndios" - e é exatamente isso que faço todas as noites: monitoro, detecto anomalias e resolvo problemas em sistemas de pagamento.

---

## O Desafio Proposto (Task 3.1)

O Task 3.1 da CloudWalk era aparentemente simples: analisar dois arquivos CSV com dados de checkout (transações de pagamento) e identificar anomalias. Os requisitos eram:

1. Analisar os dados e apresentar conclusões
2. Criar queries SQL e gráficos
3. Explicar o comportamento anômalo encontrado

Os CSVs continham dados de transações por hora, comparando: transações de hoje, ontem, mesmo dia da semana passada, média dos últimos 7 dias e média do último mês.

---

## A Descoberta: Uma Anomalia Crítica

Ao analisar os dados do checkout_2.csv, identifiquei uma anomalia grave:

**Três horas consecutivas (15h, 16h e 17h) com ZERO transações durante o horário de pico comercial.**

Os números eram alarmantes:
- **15h**: 0 transações (esperado: ~22)
- **16h**: 0 transações (esperado: ~22)
- **17h**: 0 transações (esperado: ~18)

Isso representa aproximadamente **62 transações perdidas** em apenas 3 horas.

### Por que isso é uma anomalia e não é normal?

Uma pergunta importante surgiu durante a análise: "Mas às 3h e 4h da manhã também tem zero transações, isso não é anomalia também?"

A resposta está na **média esperada**:
- Às 3h da manhã: média esperada é 0.42 transações (quase zero) → Zero é NORMAL
- Às 15h da tarde: média esperada é 22.43 transações → Zero é ANOMALIA CRÍTICA

É como uma loja: sem clientes às 3h da manhã é normal (está fechada), mas sem clientes às 15h é um problema grave (deveria estar lotada).

### Evidência Estatística

Utilizei análise de Z-Score para confirmar a anomalia estatisticamente:
- Z-Score das horas 15h-17h: **-2.8** (valores abaixo de -2 indicam anomalia significativa)
- Desvio da média: **-100%** (zero transações quando deveria ter ~22)

### Hipótese da Causa

A análise revelou um padrão interessante: às 8h da manhã houve um **spike de +574%** acima do normal. Isso sugere que o sistema ficou fora do ar durante a tarde (15h-17h) e quando voltou, processou um backlog de transações represadas na manhã seguinte.

**Causa provável: Outage do sistema de pagamento.**

---

## As Ferramentas Utilizadas

Para este desafio, utilizei um arsenal completo de ferramentas de monitoramento:

### 1. Python + Pandas
Scripts de análise de dados com cálculos estatísticos (Z-Score, desvio percentual, thresholds).

### 2. SQL + Metabase
Quatro queries diferentes para detectar anomalias, com gráficos interativos mostrando a comparação entre "Hoje" vs "Média Esperada".

### 3. Grafana
Dashboard completo de monitoramento em tempo real com painéis de status, gráficos de transações por hora e tabela de anomalias por severidade.

### 4. Prometheus
Sistema de métricas e alertas configurado com exporter customizado e regras de alerta (Critical, High, Medium).

### 5. Alertmanager
Configuração de roteamento de alertas para Slack, PagerDuty e Email.

### 6. Google Colab
Notebook interativo para executar a análise completa e visualizar gráficos.

### 7. Docker
Stack completa containerizada com docker-compose.

---

## O Diferencial: Entrega 10x Além do Pedido

### O que a maioria dos candidatos provavelmente entrega:
- 1 script Python
- 1 gráfico
- 1 texto explicativo
- **Total: 3 arquivos**

### O que eu entreguei:
- 6 documentações completas
- 4 scripts Python
- 4 queries SQL + queries Metabase
- 2 dashboards (Grafana JSON + HTML interativo)
- 9 arquivos de infraestrutura Docker
- Notebook interativo no Colab
- Stack completa rodando (Grafana + Prometheus + Alertmanager + Metabase)
- Alertas FIRING em tempo real
- **Total: 43+ arquivos + infraestrutura funcionando**

---

## A Abordagem AI-First

Utilizei inteligência artificial (Claude) como ferramenta de aceleração durante todo o processo. Isso está **100% alinhado** com o que a CloudWalk pede na vaga:

> "Use artificial intelligence tools to accelerate insight generation, pattern recognition, and opportunity discovery"

A IA foi meu copiloto, mas o **piloto sempre fui eu**: identifiquei o problema, questionei os resultados, validei cada solução e entendi profundamente cada conceito.

---

## Conclusão

O Task 3.1 pediu uma análise simples de dados. Eu entreguei uma **solução completa de monitoramento de produção**.

Porque a vaga não pede alguém que apenas analisa dados - pede **"bombeiros que usam código para apagar incêndios"**.

**Este foi apenas o Task 3.1 - ainda vem mais no 3.2.**

---

## Métricas Finais

- **Arquivos criados**: 43+
- **Linhas de código**: ~9.500
- **Ferramentas integradas**: 8
- **Anomalia detectada**: 3 horas de outage
- **Transações perdidas**: ~62
- **Z-Score da anomalia**: -2.8
- **Entrega vs Pedido**: 10x além

---

*"We want firefighters that use code to stop the fire."*

**Este é o código. Este é o extintor. Estou pronto para a próxima chamada.** 🔥
