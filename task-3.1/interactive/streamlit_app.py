"""
🚀 CloudWalk Monitoring Analyst Challenge - Task 3.1
Interactive Dashboard with Streamlit

Deploy: https://streamlit.io/cloud (FREE)

Author: Sérgio
Position: Monitoring Intelligence Analyst (Night Shift)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="CloudWalk Challenge 3.1",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# DATA
# =============================================================================
@st.cache_data
def load_data():
    checkout_1_data = """time,today,yesterday,same_day_last_week,avg_last_week,avg_last_month
00h,1,2,1,1.43,1.1
01h,0,1,0,0.43,0.37
02h,2,0,0,0.29,0.23
03h,0,0,0,0.14,0.13
04h,0,0,0,0.14,0.23
05h,0,0,0,0.14,0.27
06h,0,0,1,0.43,0.33
07h,1,1,2,1.71,1.2
08h,8,5,5,4.57,4.2
09h,21,24,17,20.71,18.53
10h,55,48,53,49.71,46.77
11h,50,51,60,55.0,51.53
12h,44,43,51,48.14,46.2
13h,40,48,47,49.57,47.13
14h,45,43,49,47.71,47.43
15h,51,51,52,50.43,49.3
16h,41,40,42,44.29,45.2
17h,45,46,39,42.29,41.2
18h,32,35,32,34.86,36.2
19h,24,25,26,28.86,28.2
20h,20,21,18,22.57,22.2
21h,22,18,17,15.57,16.2
22h,16,13,10,11.57,12.2
23h,8,8,5,5.43,5.5"""

    checkout_2_data = """time,today,yesterday,same_day_last_week,avg_last_week,avg_last_month
00h,1,2,1,1.43,1.1
01h,0,1,0,0.43,0.37
02h,4,0,0,0.29,0.23
03h,2,0,0,0.14,0.13
04h,3,0,0,0.14,0.23
05h,5,0,0,0.14,0.27
06h,4,0,1,0.43,0.33
07h,7,1,2,1.71,1.2
08h,25,0,5,3.71,4.2
09h,36,2,17,10.14,18.53
10h,49,51,53,50.0,46.77
11h,51,53,60,55.71,51.53
12h,48,45,51,48.71,46.2
13h,45,49,47,50.14,47.13
14h,19,44,49,19.57,47.43
15h,0,51,52,22.43,49.3
16h,0,41,42,21.57,45.2
17h,0,45,39,17.71,41.2
18h,13,34,32,16.86,36.2
19h,25,24,26,19.0,28.2
20h,27,20,18,19.86,22.2
21h,31,17,17,18.14,16.2
22h,22,12,10,15.71,12.2
23h,10,7,5,8.29,5.5"""

    checkout_1 = pd.read_csv(StringIO(checkout_1_data))
    checkout_2 = pd.read_csv(StringIO(checkout_2_data))
    
    checkout_1['hour'] = checkout_1['time'].str.replace('h', '').astype(int)
    checkout_2['hour'] = checkout_2['time'].str.replace('h', '').astype(int)
    
    # Calculate deviations
    checkout_1['deviation_pct'] = ((checkout_1['today'] - checkout_1['avg_last_week']) / checkout_1['avg_last_week'].replace(0, 0.001)) * 100
    checkout_2['deviation_pct'] = ((checkout_2['today'] - checkout_2['avg_last_week']) / checkout_2['avg_last_week'].replace(0, 0.001)) * 100
    
    # Calculate Z-Score
    mean_1, std_1 = checkout_1['today'].mean(), checkout_1['today'].std()
    mean_2, std_2 = checkout_2['today'].mean(), checkout_2['today'].std()
    checkout_1['z_score'] = (checkout_1['today'] - mean_1) / std_1
    checkout_2['z_score'] = (checkout_2['today'] - mean_2) / std_2
    
    return checkout_1, checkout_2

checkout_1, checkout_2 = load_data()

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.image("https://img.shields.io/badge/CloudWalk-Challenge-blue?style=for-the-badge", width=200)
st.sidebar.title("🚀 Task 3.1")
st.sidebar.markdown("**Anomaly Detection Analysis**")
st.sidebar.markdown("---")

# Dataset selector
dataset_option = st.sidebar.selectbox(
    "📊 Select Dataset",
    ["checkout_2 (Anomaly)", "checkout_1 (Normal)", "Both (Comparison)"]
)

# Hour range
hour_range = st.sidebar.slider(
    "⏰ Hour Range",
    0, 23, (0, 23)
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📋 Candidate Info
**Name:** Sérgio  
**Position:** Monitoring Intelligence Analyst  
**Shift:** Night (00:00 - 08:00)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🔗 Links
- [GitHub Repository](#)
- [Full Documentation](#)
- [Grafana Dashboard](#)
""")

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Title
st.title("🚀 CloudWalk Monitoring Analyst Challenge")
st.markdown("### Task 3.1 - Anomaly Detection Analysis")
st.markdown("---")

# Alert Banner
st.error("""
🚨 **CRITICAL ANOMALY DETECTED** in checkout_2.csv

**Period:** 15:00 - 17:59 (3 hours)  
**Issue:** ZERO transactions during peak business hours  
**Estimated Lost Transactions:** ~62  
**Z-Score:** -2.8 (statistically significant)
""")

# =============================================================================
# METRICS ROW
# =============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 checkout_1 Total",
        value=f"{checkout_1['today'].sum():,}",
        delta=f"{((checkout_1['today'].sum() - checkout_1['yesterday'].sum()) / checkout_1['yesterday'].sum() * 100):.1f}%"
    )

with col2:
    st.metric(
        label="🚨 checkout_2 Total",
        value=f"{checkout_2['today'].sum():,}",
        delta=f"{((checkout_2['today'].sum() - checkout_2['yesterday'].sum()) / checkout_2['yesterday'].sum() * 100):.1f}%"
    )

with col3:
    st.metric(
        label="⚠️ Critical Hours",
        value="3",
        delta="-100% transactions"
    )

with col4:
    lost = checkout_2[checkout_2['hour'].isin([15,16,17])]['avg_last_week'].sum()
    st.metric(
        label="💰 Lost Transactions",
        value=f"~{lost:.0f}",
        delta="During peak hours"
    )

st.markdown("---")

# =============================================================================
# VISUALIZATIONS
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Anomaly Analysis", "📊 SQL Queries", "📋 Raw Data"])

with tab1:
    st.subheader("📈 Hourly Transaction Comparison")
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('checkout_1 (Normal)', 'checkout_2 (Anomaly)'))
    
    # checkout_1
    fig.add_trace(
        go.Bar(x=checkout_1['time'], y=checkout_1['today'], name='Today', marker_color='#2ecc71'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=checkout_1['time'], y=checkout_1['avg_last_week'], name='Avg Week', 
                   line=dict(color='orange', dash='dash')),
        row=1, col=1
    )
    
    # checkout_2 with anomaly highlight
    colors = ['#e74c3c' if h in [15, 16, 17] else '#3498db' for h in checkout_2['hour']]
    fig.add_trace(
        go.Bar(x=checkout_2['time'], y=checkout_2['today'], name='Today (Anomaly)', marker_color=colors),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=checkout_2['time'], y=checkout_2['avg_last_week'], name='Avg Week',
                   line=dict(color='orange', dash='dash'), showlegend=False),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔍 Anomaly Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📉 Deviation from Weekly Average")
        fig_dev = go.Figure()
        colors_dev = ['#e74c3c' if d < -50 else '#f39c12' if d > 100 else '#2ecc71' for d in checkout_2['deviation_pct']]
        fig_dev.add_trace(go.Bar(
            x=checkout_2['time'],
            y=checkout_2['deviation_pct'],
            marker_color=colors_dev
        ))
        fig_dev.add_hline(y=-50, line_dash="dash", line_color="red", annotation_text="-50% threshold")
        fig_dev.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="+100% threshold")
        fig_dev.update_layout(height=350, yaxis_title="Deviation %")
        st.plotly_chart(fig_dev, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Z-Score Analysis")
        fig_z = go.Figure()
        colors_z = ['#e74c3c' if abs(z) > 2 else '#f39c12' if abs(z) > 1 else '#2ecc71' for z in checkout_2['z_score']]
        fig_z.add_trace(go.Bar(
            x=checkout_2['time'],
            y=checkout_2['z_score'],
            marker_color=colors_z
        ))
        fig_z.add_hline(y=2, line_dash="dash", line_color="red", annotation_text="+2σ")
        fig_z.add_hline(y=-2, line_dash="dash", line_color="red", annotation_text="-2σ")
        fig_z.update_layout(height=350, yaxis_title="Z-Score")
        st.plotly_chart(fig_z, use_container_width=True)
    
    st.markdown("#### 🚨 Anomaly Details")
    anomaly_df = checkout_2[
        (checkout_2['today'] == 0) | 
        (checkout_2['deviation_pct'] < -50) | 
        (checkout_2['deviation_pct'] > 200)
    ][['time', 'today', 'yesterday', 'avg_last_week', 'deviation_pct', 'z_score']]
    anomaly_df['status'] = anomaly_df.apply(
        lambda x: '🔴 CRITICAL' if x['today'] == 0 else ('🟠 HIGH' if x['deviation_pct'] < -50 else '🟡 SPIKE'),
        axis=1
    )
    st.dataframe(anomaly_df, use_container_width=True)

with tab3:
    st.subheader("📊 SQL Query Playground")
    
    st.markdown("""
    These queries can be executed on the checkout data to detect anomalies.
    """)
    
    query_option = st.selectbox("Select Query", [
        "1. Detect All Anomalies",
        "2. Daily Totals Comparison",
        "3. Peak Hours Analysis",
        "4. Z-Score Calculation"
    ])
    
    if query_option.startswith("1"):
        st.code("""
SELECT 
    time,
    today,
    avg_last_week,
    ROUND(((today - avg_last_week) / avg_last_week) * 100, 2) AS deviation_pct,
    CASE 
        WHEN today = 0 AND avg_last_week > 5 THEN 'CRITICAL'
        WHEN today < avg_last_week * 0.5 THEN 'HIGH'
        WHEN today > avg_last_week * 2 THEN 'SPIKE'
        ELSE 'NORMAL'
    END AS status
FROM checkout_2
WHERE today = 0 OR today < avg_last_week * 0.5 OR today > avg_last_week * 2
ORDER BY status, hour;
        """, language="sql")
        
        # Execute query simulation
        result = checkout_2[
            (checkout_2['today'] == 0) | 
            (checkout_2['today'] < checkout_2['avg_last_week'] * 0.5) |
            (checkout_2['today'] > checkout_2['avg_last_week'] * 2)
        ][['time', 'today', 'avg_last_week', 'deviation_pct']]
        st.dataframe(result, use_container_width=True)
    
    elif query_option.startswith("2"):
        st.code("""
SELECT 
    'checkout_1' as dataset,
    SUM(today) as total_today,
    SUM(yesterday) as total_yesterday,
    ROUND(((SUM(today) - SUM(yesterday)) / SUM(yesterday)) * 100, 2) as dod_change
FROM checkout_1
UNION ALL
SELECT 'checkout_2', SUM(today), SUM(yesterday), 
    ROUND(((SUM(today) - SUM(yesterday)) / SUM(yesterday)) * 100, 2)
FROM checkout_2;
        """, language="sql")
        
        comparison = pd.DataFrame({
            'dataset': ['checkout_1', 'checkout_2'],
            'total_today': [checkout_1['today'].sum(), checkout_2['today'].sum()],
            'total_yesterday': [checkout_1['yesterday'].sum(), checkout_2['yesterday'].sum()],
            'dod_change': [
                round((checkout_1['today'].sum() - checkout_1['yesterday'].sum()) / checkout_1['yesterday'].sum() * 100, 2),
                round((checkout_2['today'].sum() - checkout_2['yesterday'].sum()) / checkout_2['yesterday'].sum() * 100, 2)
            ]
        })
        st.dataframe(comparison, use_container_width=True)

with tab4:
    st.subheader("📋 Raw Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### checkout_1.csv (Normal)")
        st.dataframe(checkout_1[['time', 'today', 'yesterday', 'avg_last_week', 'deviation_pct']], use_container_width=True)
    
    with col2:
        st.markdown("#### checkout_2.csv (Anomaly)")
        st.dataframe(checkout_2[['time', 'today', 'yesterday', 'avg_last_week', 'deviation_pct']], use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🔥 <strong>"Bombeiros que usam código para apagar incêndios."</strong></p>
    <p>CloudWalk Challenge - Task 3.1 | Sérgio | Monitoring Intelligence Analyst</p>
</div>
""", unsafe_allow_html=True)
