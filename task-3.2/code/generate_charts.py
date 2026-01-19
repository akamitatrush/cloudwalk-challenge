#!/usr/bin/env python3
"""
Gera gráficos de análise para a pasta assets/
Transaction Guardian - Task 3.2
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os

# Configurações
plt.style.use('ggplot')
sns.set_palette("husl")

ASSETS_DIR = "assets"
DATA_DIR = "data"

def load_data():
    """Carrega os dados dos CSVs"""
    transactions = None
    
    # Tentar carregar transactions.csv
    csv_path = os.path.join(DATA_DIR, "transactions.csv")
    if os.path.exists(csv_path):
        print(f"📄 Carregando {csv_path}...")
        transactions = pd.read_csv(csv_path)
        
        # Debug: mostrar colunas
        print(f"   Colunas encontradas: {list(transactions.columns)}")
        
        # Converter timestamp para datetime
        if 'time' in transactions.columns:
            transactions['timestamp'] = pd.to_datetime(transactions['time'], errors='coerce')
        elif 'timestamp' in transactions.columns:
            transactions['timestamp'] = pd.to_datetime(transactions['timestamp'], errors='coerce')
        else:
            # Criar timestamps fictícios
            print("   ⚠️ Criando timestamps fictícios...")
            base_time = datetime.now() - timedelta(hours=24)
            transactions['timestamp'] = [base_time + timedelta(minutes=i) for i in range(len(transactions))]
        
        # Garantir que temos as colunas necessárias
        if 'status' not in transactions.columns:
            transactions['status'] = 'approved'
        if 'count' not in transactions.columns:
            if 'approved' in transactions.columns:
                transactions['count'] = transactions['approved']
            else:
                transactions['count'] = 100
        if 'auth_code' not in transactions.columns:
            transactions['auth_code'] = '00'
    
    # Se não houver dados, criar dados de exemplo
    if transactions is None or len(transactions) == 0:
        print("⚠️ Criando dados de exemplo...")
        np.random.seed(42)
        n_samples = 500
        
        base_time = datetime.now() - timedelta(hours=24)
        timestamps = [base_time + timedelta(minutes=i*2) for i in range(n_samples)]
        
        counts = []
        statuses = []
        for i in range(n_samples):
            if 100 <= i <= 120:
                counts.append(np.random.randint(5, 20))
                statuses.append('approved')
            elif 200 <= i <= 220:
                counts.append(np.random.randint(250, 400))
                statuses.append('approved')
            elif i % 20 == 0:
                counts.append(np.random.randint(80, 120))
                statuses.append(np.random.choice(['failed', 'denied', 'reversed']))
            else:
                counts.append(np.random.randint(90, 130))
                statuses.append('approved')
        
        transactions = pd.DataFrame({
            'timestamp': timestamps,
            'count': counts,
            'status': statuses,
            'auth_code': ['00' if s == 'approved' else '59' for s in statuses]
        })
    
    # Garantir que timestamp é datetime
    transactions['timestamp'] = pd.to_datetime(transactions['timestamp'], errors='coerce')
    
    # Preencher timestamps nulos
    if transactions['timestamp'].isna().any():
        print("   ⚠️ Preenchendo timestamps nulos...")
        base_time = datetime.now() - timedelta(hours=24)
        null_mask = transactions['timestamp'].isna()
        transactions.loc[null_mask, 'timestamp'] = [
            base_time + timedelta(minutes=i) 
            for i in range(null_mask.sum())
        ]
    
    return transactions

def create_analysis_chart(df):
    """Cria gráfico de análise multi-painel"""
    print("   Gerando anomaly_analysis_chart.png...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Transaction Guardian - Análise de Anomalias', fontsize=16, fontweight='bold')
    
    # Extrair hora
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    
    # Painel 1: Volume ao longo do tempo
    ax1 = axes[0, 0]
    ax1.plot(range(len(df)), df['count'].values, 'b-', alpha=0.7, linewidth=0.8)
    ax1.axhline(y=df['count'].mean(), color='g', linestyle='--', label=f'Média: {df["count"].mean():.1f}')
    ax1.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='Threshold Crítico (50)')
    ax1.set_title('Volume de Transações ao Longo do Tempo')
    ax1.set_xlabel('Amostra')
    ax1.set_ylabel('Transações/min')
    ax1.legend(loc='upper right')
    
    # Painel 2: Distribuição por Status
    ax2 = axes[0, 1]
    status_counts = df['status'].value_counts()
    colors_map = {'approved': '#2ecc71', 'failed': '#e74c3c', 'denied': '#f39c12', 'reversed': '#9b59b6'}
    pie_colors = [colors_map.get(s, '#95a5a6') for s in status_counts.index]
    ax2.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=pie_colors)
    ax2.set_title('Distribuição por Status')
    
    # Painel 3: Histograma de Volume
    ax3 = axes[1, 0]
    ax3.hist(df['count'], bins=30, color='steelblue', edgecolor='white', alpha=0.7)
    ax3.axvline(x=df['count'].mean(), color='green', linestyle='--', linewidth=2, label=f'Média: {df["count"].mean():.1f}')
    ax3.axvline(x=50, color='red', linestyle='--', linewidth=2, label='Threshold Crítico')
    ax3.set_title('Distribuição de Volume')
    ax3.set_xlabel('Transações/min')
    ax3.set_ylabel('Frequência')
    ax3.legend()
    
    # Painel 4: Volume por hora
    ax4 = axes[1, 1]
    hourly_mean = df.groupby('hour')['count'].mean()
    colors = ['red' if v < 50 else 'orange' if v < 80 else 'green' for v in hourly_mean.values]
    ax4.bar(hourly_mean.index, hourly_mean.values, color=colors, alpha=0.7)
    ax4.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Crítico')
    ax4.axhline(y=80, color='orange', linestyle='--', alpha=0.5, label='Warning')
    ax4.set_title('Volume Médio por Hora')
    ax4.set_xlabel('Hora')
    ax4.set_ylabel('Transações/min')
    ax4.legend()
    
    plt.tight_layout()
    
    output_path = os.path.join(ASSETS_DIR, 'anomaly_analysis_chart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Salvo: {output_path}")

def create_timeline_chart(df):
    """Cria gráfico de timeline focado em anomalias"""
    print("   Gerando anomaly_timeline.png...")
    
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    fig.suptitle('Transaction Guardian - Timeline de Anomalias', fontsize=16, fontweight='bold')
    
    df = df.copy()
    
    # Painel 1: Timeline com anomalias
    ax1 = axes[0]
    x = range(len(df))
    ax1.plot(x, df['count'].values, 'b-', linewidth=0.8, label='Volume')
    
    # Destacar anomalias
    low_mask = df['count'] < 50
    high_mask = df['count'] > 200
    
    if low_mask.any():
        ax1.scatter(np.array(x)[low_mask], df.loc[low_mask, 'count'].values, 
                   color='red', s=30, zorder=5, label=f'Outage ({low_mask.sum()})')
    if high_mask.any():
        ax1.scatter(np.array(x)[high_mask], df.loc[high_mask, 'count'].values, 
                   color='orange', s=30, zorder=5, label=f'Spike ({high_mask.sum()})')
    
    ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5)
    ax1.axhline(y=200, color='orange', linestyle='--', alpha=0.5)
    ax1.set_title('Timeline com Anomalias Destacadas')
    ax1.set_ylabel('Transações/min')
    ax1.legend(loc='upper right')
    
    # Painel 2: Taxa de aprovação
    ax2 = axes[1]
    df['is_approved'] = (df['status'] == 'approved').astype(int)
    df['rolling_approval'] = df['is_approved'].rolling(window=50, min_periods=1).mean() * 100
    
    ax2.plot(x, df['rolling_approval'].values, 'g-', linewidth=1.5)
    ax2.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='Warning (90%)')
    ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7, label='Target (95%)')
    ax2.fill_between(x, 0, df['rolling_approval'].values, 
                     where=df['rolling_approval'].values < 90, color='red', alpha=0.3)
    ax2.set_title('Taxa de Aprovação (Média Móvel)')
    ax2.set_ylabel('Taxa de Aprovação (%)')
    ax2.set_ylim(0, 105)
    ax2.legend(loc='lower right')
    
    # Painel 3: Distribuição de status ao longo do tempo
    ax3 = axes[2]
    df['hour'] = df['timestamp'].dt.hour
    status_counts = df.groupby(['hour', 'status']).size().unstack(fill_value=0)
    
    colors_map = {'approved': '#2ecc71', 'failed': '#e74c3c', 'denied': '#f39c12', 'reversed': '#9b59b6'}
    bottom = np.zeros(len(status_counts))
    
    for status in status_counts.columns:
        color = colors_map.get(status, 'gray')
        ax3.bar(status_counts.index, status_counts[status].values, bottom=bottom, 
               label=status, color=color, alpha=0.8)
        bottom += status_counts[status].values
    
    ax3.set_title('Distribuição de Status por Hora')
    ax3.set_xlabel('Hora')
    ax3.set_ylabel('Transações')
    ax3.legend()
    
    plt.tight_layout()
    
    output_path = os.path.join(ASSETS_DIR, 'anomaly_timeline.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Salvo: {output_path}")

def create_status_chart(df):
    """Cria gráfico de análise por status"""
    print("   Gerando status_analysis_chart.png...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Transaction Guardian - Análise por Status', fontsize=16, fontweight='bold')
    
    df = df.copy()
    df['hour'] = df['timestamp'].dt.hour
    
    colors_map = {'approved': '#2ecc71', 'failed': '#e74c3c', 'denied': '#f39c12', 'reversed': '#9b59b6'}
    
    # Painel 1: Barras por hora
    ax1 = axes[0, 0]
    hourly_counts = df.groupby('hour').size()
    hourly_errors = df[df['status'] != 'approved'].groupby('hour').size().reindex(hourly_counts.index, fill_value=0)
    
    x = np.arange(len(hourly_counts))
    width = 0.35
    
    ax1.bar(x - width/2, hourly_counts.values, width, label='Total', color='steelblue', alpha=0.7)
    ax1.bar(x + width/2, hourly_errors.values, width, label='Erros', color='red', alpha=0.7)
    ax1.set_title('Transações por Hora')
    ax1.set_xlabel('Hora')
    ax1.set_ylabel('Transações')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{h}h' for h in hourly_counts.index])
    ax1.legend()
    
    # Painel 2: Donut chart
    ax2 = axes[0, 1]
    status_counts = df['status'].value_counts()
    pie_colors = [colors_map.get(s, '#95a5a6') for s in status_counts.index]
    wedges, texts, autotexts = ax2.pie(status_counts.values, labels=status_counts.index,
                                        autopct='%1.1f%%', colors=pie_colors,
                                        pctdistance=0.75, wedgeprops=dict(width=0.5))
    ax2.set_title('Distribuição de Status')
    
    # Painel 3: Taxa de erro por hora
    ax3 = axes[1, 0]
    error_rate = (hourly_errors / hourly_counts * 100).fillna(0)
    colors = ['red' if r > 10 else 'orange' if r > 5 else 'green' for r in error_rate.values]
    ax3.bar(error_rate.index, error_rate.values, color=colors, alpha=0.7)
    ax3.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Warning (5%)')
    ax3.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Critical (10%)')
    ax3.set_title('Taxa de Erro por Hora')
    ax3.set_xlabel('Hora')
    ax3.set_ylabel('Taxa de Erro (%)')
    ax3.legend()
    
    # Painel 4: Tabela de resumo
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    total = len(df)
    approved = (df['status'] == 'approved').sum()
    failed = (df['status'] == 'failed').sum()
    denied = (df['status'] == 'denied').sum()
    reversed_tx = (df['status'] == 'reversed').sum()
    
    summary_data = [
        ['Total Transações', f'{total:,}'],
        ['Aprovadas', f'{approved:,} ({approved/total*100:.1f}%)'],
        ['Falhas', f'{failed:,} ({failed/total*100:.1f}%)'],
        ['Negadas', f'{denied:,} ({denied/total*100:.1f}%)'],
        ['Revertidas', f'{reversed_tx:,} ({reversed_tx/total*100:.1f}%)'],
        ['Volume Médio', f'{df["count"].mean():.1f} tx/min'],
        ['Anomalias (Vol<50)', f'{(df["count"] < 50).sum():,}'],
        ['Spikes (Vol>200)', f'{(df["count"] > 200).sum():,}'],
    ]
    
    table = ax4.table(cellText=summary_data, colLabels=['Métrica', 'Valor'],
                      loc='center', cellLoc='left',
                      colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    for i in range(2):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    ax4.set_title('Resumo Estatístico', pad=20)
    
    plt.tight_layout()
    
    output_path = os.path.join(ASSETS_DIR, 'status_analysis_chart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Salvo: {output_path}")

def main():
    """Função principal"""
    print("🎨 Transaction Guardian - Gerador de Gráficos")
    print("=" * 50)
    
    # Criar diretório de assets
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Carregar dados
    print("\n📊 Carregando dados...")
    df = load_data()
    print(f"   Registros carregados: {len(df)}")
    print(f"   Período: {df['timestamp'].min()} a {df['timestamp'].max()}")
    
    # Gerar gráficos
    print("\n🎨 Gerando gráficos...")
    
    create_analysis_chart(df)
    create_timeline_chart(df)
    create_status_chart(df)
    
    print("\n" + "=" * 50)
    print("✅ Todos os gráficos gerados com sucesso!")
    print(f"📁 Pasta: {ASSETS_DIR}/")
    for f in os.listdir(ASSETS_DIR):
        if f.endswith('.png'):
            size = os.path.getsize(os.path.join(ASSETS_DIR, f)) / 1024
            print(f"   - {f} ({size:.1f} KB)")

if __name__ == "__main__":
    main()
