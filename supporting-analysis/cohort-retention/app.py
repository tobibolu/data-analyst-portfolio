"""
Streamlit Dashboard: Olist Cohort & Retention Analytics
Multi-page app with Cohort Retention, RFM, LTV, and Churn Risk pages.
Author: Tobi Bolu | https://github.com/tobibolu
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Cohort & Retention Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Shared data loading (cached across all pages) ──
@st.cache_data
def load_all_data():
    cohort = pd.read_csv('./tableau_cohort_retention.csv')
    rfm = pd.read_csv('./tableau_rfm_customers.csv')
    ltv = pd.read_csv('./tableau_ltv_data.csv')
    churn = pd.read_csv('./tableau_churn_risk.csv')
    return cohort, rfm, ltv, churn

cohort_df, rfm_df, ltv_df, churn_df = load_all_data()

# ── Landing Page ──
st.title("📈 Olist E-Commerce: Cohort & Retention Analytics")
st.markdown("**Author:** Tobi Bolu | [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)")
st.markdown("*I've analyzed 93K+ customers across four dimensions: cohort retention, RFM segmentation, lifetime value, and churn risk.*")

st.divider()

# ── Top-level KPIs ──
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Customers", f"{len(rfm_df):,}")
with col2:
    repeat_pct = (rfm_df['order_count'] > 1).sum() / len(rfm_df) * 100
    st.metric("Repeat Rate", f"{repeat_pct:.1f}%")
with col3:
    avg_ltv = ltv_df['ltv_12m'].mean()
    st.metric("Avg 12-Mo LTV", f"R${avg_ltv:,.0f}")
with col4:
    champions = (rfm_df['segment'] == 'Champions').sum()
    st.metric("Champions", f"{champions:,}")
with col5:
    at_risk = churn_df['churn_risk'].isin(['At Risk (Repeat)', 'Churned (Was Repeat)']).sum()
    st.metric("At Risk (Repeat)", f"{at_risk:,}")

st.divider()

# ── Quick Overview Row ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("RFM Segment Breakdown")
    seg_counts = rfm_df['segment'].value_counts()
    seg_order = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'Recent Customers',
                 'Need Attention', 'About to Sleep', 'At Risk', 'Cant Lose Them', 'Lost']
    seg_counts = seg_counts.reindex([s for s in seg_order if s in seg_counts.index])

    seg_colors = {
        'Champions': '#2ecc71', 'Loyal Customers': '#27ae60', 'Potential Loyalists': '#3498db',
        'Recent Customers': '#1abc9c', 'Need Attention': '#f39c12', 'About to Sleep': '#e67e22',
        'At Risk': '#e74c3c', 'Cant Lose Them': '#c0392b', 'Lost': '#95a5a6'
    }

    fig = go.Figure(data=[go.Pie(
        labels=seg_counts.index,
        values=seg_counts.values,
        marker=dict(colors=[seg_colors.get(s, '#3498db') for s in seg_counts.index]),
        textinfo='label+percent',
        hole=0.4
    )])
    fig.update_layout(height=400, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Churn Risk Distribution")
    risk_order = ['Active', 'Warm', 'Cooling', 'At Risk (Repeat)', 'Churned (Was Repeat)', 'Churned (One-time)']
    risk_colors = {
        'Active': '#2ecc71', 'Warm': '#f39c12', 'Cooling': '#e67e22',
        'At Risk (Repeat)': '#e74c3c', 'Churned (Was Repeat)': '#c0392b', 'Churned (One-time)': '#95a5a6'
    }
    risk_counts = churn_df['churn_risk'].value_counts().reindex(
        [r for r in risk_order if r in churn_df['churn_risk'].values]
    ).fillna(0)

    fig = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker=dict(colors=[risk_colors.get(r, '#3498db') for r in risk_counts.index]),
        textinfo='label+percent',
        hole=0.4
    )])
    fig.update_layout(height=400, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Average Retention Curve (quick preview) ──
st.subheader("Average Retention Curve")
avg_ret = cohort_df.groupby('cohort_period')['retention_rate'].mean().reset_index()
avg_ret = avg_ret[avg_ret['cohort_period'] <= 12]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=avg_ret['cohort_period'],
    y=avg_ret['retention_rate'],
    mode='lines+markers+text',
    marker=dict(size=8, color='#e74c3c'),
    line=dict(width=2, color='#e74c3c'),
    text=[f'{v:.1f}%' for v in avg_ret['retention_rate']],
    textposition='top center'
))
fig.update_layout(
    xaxis_title='Months Since First Purchase',
    yaxis_title='Retention Rate (%)',
    height=350,
    showlegend=False,
    margin=dict(t=10)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("👈 **Use the sidebar** to navigate to detailed pages: Cohort Retention, RFM Segments, LTV Analysis, and Churn Risk.")
st.markdown("---")
st.markdown("*Dashboard built with Streamlit & Plotly | Dataset: Olist Brazilian E-Commerce (Kaggle)*")
