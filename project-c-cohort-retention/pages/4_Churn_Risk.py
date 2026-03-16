"""Page 4: Churn Risk Analysis"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Churn Risk", page_icon="⚠️", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('./tableau_churn_risk.csv')

df = load_data()

st.title("⚠️ Churn Risk Analysis")
st.markdown("I'm identifying at-risk customers by inactivity patterns, purchase behavior, and geography.")

risk_order = ['Active', 'Warm', 'Cooling', 'At Risk (Repeat)', 'Churned (Was Repeat)', 'Churned (One-time)']
risk_colors = {
    'Active': '#2ecc71', 'Warm': '#f39c12', 'Cooling': '#e67e22',
    'At Risk (Repeat)': '#e74c3c', 'Churned (Was Repeat)': '#c0392b', 'Churned (One-time)': '#95a5a6'
}

seg_order = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'Recent Customers',
             'Need Attention', 'About to Sleep', 'At Risk', 'Cant Lose Them', 'Lost']

# ── Sidebar Filters ──
st.sidebar.header("Filters")

risk_filter = st.sidebar.multiselect(
    "Churn Risk Level",
    options=[r for r in risk_order if r in df['churn_risk'].unique()],
    default=[r for r in risk_order if r in df['churn_risk'].unique()]
)

segment_filter = st.sidebar.multiselect(
    "RFM Segment",
    options=[s for s in seg_order if s in df['segment'].unique()],
    default=[s for s in seg_order if s in df['segment'].unique()]
)

all_states = sorted(df['state'].dropna().unique())
state_filter = st.sidebar.multiselect("State", options=all_states, default=all_states)

min_orders = st.sidebar.number_input("Minimum Orders", min_value=1, max_value=20, value=1)

df_filtered = df[
    (df['churn_risk'].isin(risk_filter)) &
    (df['segment'].isin(segment_filter)) &
    (df['state'].isin(state_filter)) &
    (df['order_count'] >= min_orders)
]

# ── KPIs ──
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Customers (Filtered)", f"{len(df_filtered):,}")
with col2:
    active = (df_filtered['churn_risk'] == 'Active').sum()
    st.metric("Active", f"{active:,}", delta=f"{active/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%")
with col3:
    at_risk_repeat = (df_filtered['churn_risk'] == 'At Risk (Repeat)').sum()
    st.metric("At Risk (Repeat)", f"{at_risk_repeat:,}", delta="Priority", delta_color="inverse")
with col4:
    churned_repeat = (df_filtered['churn_risk'] == 'Churned (Was Repeat)').sum()
    st.metric("Churned (Was Repeat)", f"{churned_repeat:,}")
with col5:
    avg_days = df_filtered['days_since_last'].mean()
    st.metric("Avg Days Since Last", f"{avg_days:.0f}" if not np.isnan(avg_days) else "N/A")

st.divider()

# ── Risk Distribution ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Churn Risk Distribution")
    risk_counts = df_filtered['churn_risk'].value_counts().reindex(
        [r for r in risk_order if r in df_filtered['churn_risk'].values]
    ).fillna(0)

    fig = go.Figure(data=[go.Bar(
        x=risk_counts.index,
        y=risk_counts.values,
        marker_color=[risk_colors.get(r, '#3498db') for r in risk_counts.index],
        text=[f'{int(v):,}' for v in risk_counts.values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Risk Level', yaxis_title='Customers',
        height=400, showlegend=False, xaxis_tickangle=-20
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Revenue at Risk")
    risk_revenue = df_filtered.groupby('churn_risk')['total_revenue'].sum().reindex(
        [r for r in risk_order if r in df_filtered['churn_risk'].values]
    ).fillna(0)

    fig = go.Figure(data=[go.Bar(
        x=risk_revenue.index,
        y=risk_revenue.values,
        marker_color=[risk_colors.get(r, '#3498db') for r in risk_revenue.index],
        text=[f'R${v:,.0f}' for v in risk_revenue.values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Risk Level', yaxis_title='Total Revenue (R$)',
        height=400, showlegend=False, xaxis_tickangle=-20
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Risk x Segment Cross-Tab ──
st.subheader("Risk Level vs RFM Segment")

cross = pd.crosstab(df_filtered['churn_risk'], df_filtered['segment'])
cross = cross.reindex(index=[r for r in risk_order if r in cross.index],
                       columns=[s for s in seg_order if s in cross.columns])

fig = go.Figure(data=go.Heatmap(
    z=cross.values,
    x=cross.columns.tolist(),
    y=cross.index.tolist(),
    texttemplate='%{z:,}',
    textfont={'size': 10},
    colorscale='YlOrRd',
    hovertemplate='Risk: %{y}<br>Segment: %{x}<br>Count: %{z:,}<extra></extra>'
))
fig.update_layout(
    height=350,
    margin=dict(l=150),
    xaxis_tickangle=-30
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Geographic Risk ──
st.subheader("Churn Risk by State (Top 15 by Customer Volume)")

top_states = df_filtered['state'].value_counts().head(15).index
state_risk = df_filtered[df_filtered['state'].isin(top_states)]

state_risk_pct = pd.crosstab(state_risk['state'], state_risk['churn_risk'], normalize='index') * 100
state_risk_pct = state_risk_pct.reindex(columns=[r for r in risk_order if r in state_risk_pct.columns])

fig = go.Figure()
for risk_level in state_risk_pct.columns:
    fig.add_trace(go.Bar(
        y=state_risk_pct.index,
        x=state_risk_pct[risk_level],
        name=risk_level,
        orientation='h',
        marker_color=risk_colors.get(risk_level, '#3498db'),
        text=[f'{v:.0f}%' if v > 5 else '' for v in state_risk_pct[risk_level]],
        textposition='inside'
    ))

fig.update_layout(
    barmode='stack',
    xaxis_title='Percentage of Customers',
    height=500,
    legend=dict(orientation='h', y=-0.15),
    margin=dict(l=60)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Days Since Last Purchase Distribution ──
st.subheader("Days Since Last Purchase by Risk Level")

fig = go.Figure()
for risk in [r for r in risk_order if r in df_filtered['churn_risk'].values]:
    subset = df_filtered[df_filtered['churn_risk'] == risk]
    fig.add_trace(go.Box(
        y=subset['days_since_last'],
        name=risk,
        marker_color=risk_colors.get(risk, '#3498db'),
        boxmean=True
    ))

fig.update_layout(
    yaxis_title='Days Since Last Purchase',
    height=400,
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

# ── Priority Intervention List ──
st.divider()
st.subheader("🚨 Priority Intervention List")
st.markdown("Repeat customers who are at risk or recently churned — highest ROI for retention outreach.")

priority = df_filtered[
    df_filtered['churn_risk'].isin(['At Risk (Repeat)', 'Churned (Was Repeat)'])
].sort_values('total_revenue', ascending=False)

if len(priority) > 0:
    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        st.metric("Priority Customers", f"{len(priority):,}")
        st.metric("Revenue at Stake", f"R${priority['total_revenue'].sum():,.0f}")
        st.metric("Avg Orders", f"{priority['order_count'].mean():.1f}")
    with col_p2:
        display_cols = ['customer_unique_id', 'churn_risk', 'segment', 'state',
                        'order_count', 'total_revenue', 'days_since_last', 'avg_review']
        st.dataframe(priority[display_cols].head(50), use_container_width=True, height=350)
else:
    st.info("No priority customers match the current filters.")

# ── Full Data ──
with st.expander("View All Filtered Customer Data"):
    st.dataframe(df_filtered.head(500), use_container_width=True, height=400)
