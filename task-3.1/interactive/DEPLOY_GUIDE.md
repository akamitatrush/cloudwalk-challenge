# 🚀 GUIA DE DEPLOY - Infraestrutura Interativa

## CloudWalk Challenge Task 3.1 - Mostre na Prática!

Este guia te ajuda a subir infraestrutura REAL para impressionar a CloudWalk.

---

## 📋 OPÇÕES DE DEPLOY

| Plataforma | O que mostra | Tempo | Custo |
|------------|--------------|-------|-------|
| **GitHub Pages** | Dashboard HTML | 5 min | Grátis |
| **Google Colab** | Notebook interativo + SQL | 2 min | Grátis |
| **Streamlit Cloud** | Dashboard completo | 10 min | Grátis |
| **Docker Local** | Stack completo (Grafana+Prometheus) | 15 min | Grátis |

---

## 1️⃣ GITHUB PAGES (Dashboard HTML)

### O que é:
Hospedar o `DASHBOARD.html` como página web pública.

### Passos:

1. **No seu repositório GitHub:**
```bash
# Criar branch gh-pages ou usar main
git checkout -b gh-pages
```

2. **Copiar o dashboard para a raiz:**
```bash
cp task-3.1/dashboards/DASHBOARD.html index.html
```

3. **Commit e push:**
```bash
git add index.html
git commit -m "Add interactive dashboard"
git push origin gh-pages
```

4. **Ativar GitHub Pages:**
- Vá em Settings → Pages
- Source: Deploy from branch
- Branch: `gh-pages` (ou `main`)
- Folder: `/ (root)`
- Save

5. **Acesse em:**
```
https://SEU-USUARIO.github.io/NOME-DO-REPO/
```

### Resultado:
🌐 Dashboard interativo acessível por qualquer pessoa!

---

## 2️⃣ GOOGLE COLAB (Notebook Interativo)

### O que é:
Notebook Python onde a CloudWalk pode executar a análise e queries SQL.

### Passos:

1. **Acesse:** https://colab.research.google.com

2. **Upload do notebook:**
- File → Upload notebook
- Selecione: `CloudWalk_Challenge_3_1_Interactive.ipynb`

3. **Executar:**
- Runtime → Run all

4. **Compartilhar:**
- File → Save a copy in Drive (salva no seu Drive)
- Share → Anyone with the link can view

5. **Link para incluir no README:**
```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/SEU_FILE_ID)
```

### Resultado:
📓 Qualquer pessoa pode executar suas queries SQL e ver os gráficos!

---

## 3️⃣ STREAMLIT CLOUD (Dashboard Profissional)

### O que é:
Dashboard interativo profissional hospedado gratuitamente.

### Passos:

1. **Criar conta:** https://streamlit.io/cloud (login com GitHub)

2. **Estrutura no GitHub:**
```
seu-repo/
├── streamlit_app.py      # ou app.py
├── requirements.txt
└── README.md
```

3. **No Streamlit Cloud:**
- Click "New app"
- Repository: selecione seu repo
- Branch: main
- Main file: `task-3.1/interactive/streamlit_app.py`
- Click "Deploy!"

4. **Aguardar deploy (~2-3 min)**

5. **URL gerada:**
```
https://SEU-APP.streamlit.app
```

### Customização:
- Vá em Settings → Secrets para adicionar configs
- Tema pode ser customizado em `.streamlit/config.toml`

### Resultado:
🚀 Dashboard profissional com filtros interativos!

---

## 4️⃣ DOCKER LOCAL (Stack Completo)

### O que é:
Grafana + Prometheus + Alertmanager rodando localmente.

### Pré-requisitos:
- Docker instalado
- Docker Compose instalado

### Passos:

1. **Entrar na pasta de infraestrutura:**
```bash
cd task-3.1/infrastructure
```

2. **Subir a stack:**
```bash
docker-compose up -d
```

3. **Verificar se está rodando:**
```bash
docker-compose ps
```

4. **Acessar:**
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093
- **Métricas:** http://localhost:8000/metrics

5. **Importar dashboard no Grafana:**
- Dashboards → Import
- Upload `checkout_monitoring.json`
- Select Prometheus as datasource
- Import!

### Para demonstração remota:
Use **ngrok** para expor:
```bash
# Instalar ngrok
brew install ngrok  # ou baixe de ngrok.com

# Expor Grafana
ngrok http 3000
```

Isso gera uma URL pública tipo `https://abc123.ngrok.io`

### Resultado:
📊 Stack completo de monitoramento funcionando!

---

## 📝 COMO ADICIONAR NO README DO GITHUB

```markdown
## 🚀 Live Demo

### 🌐 Interactive Dashboard
[View Dashboard](https://seu-usuario.github.io/cloudwalk-challenge/)

### 📓 Google Colab (Execute SQL Queries)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/SEU_ID)

### 📊 Streamlit Dashboard
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-app.streamlit.app)

### 🐳 Run Locally
\`\`\`bash
cd task-3.1/infrastructure
docker-compose up -d
# Access Grafana: http://localhost:3000
\`\`\`
```

---

## 🎯 ORDEM RECOMENDADA DE DEPLOY

1. **GitHub Pages** (5 min) - Fácil e rápido
2. **Google Colab** (2 min) - Mostra SQL funcionando
3. **Streamlit Cloud** (10 min) - Dashboard profissional
4. **Docker** (local) - Para demonstração de video call

---

## 💡 DICA FINAL

Quando a CloudWalk perguntar: *"Você tem algo para mostrar?"*

Responda: 

> "Sim! Tenho um dashboard interativo no GitHub Pages, um notebook no Colab onde vocês podem executar as queries SQL, um app Streamlit profissional, e posso compartilhar minha tela com Grafana + Prometheus rodando via Docker."

**Isso é o que diferencia você dos outros candidatos.** 🔥

---

## 📞 Suporte

Qualquer dúvida no deploy, me chama!

*"Bombeiros que usam código para apagar incêndios."* 🚒
