"""Page 2: RFM Segmentation"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="RFM Segments", page_icon="🎯", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('./tableau_rfm_customers.csv')

df = load_data()

st.title("🎯 RFM Segmentation")
st.markdown("I've scored 93K+ customers on Recency, Frequency, and Monetary value.")

# ── Segment colors (shared) ──
seg_colors = {
    'Champions': '#2ecc71', 'Loyal Customers': '#27ae60', 'Potential Loyalists': '#3498db',
    'Recent Customers': '#1abc9c', 'Need Attention': '#f39c12', 'About to Sleep': '#e67e22',
    'At Risk': '#e74c3c', 'Cant Lose Them': '#c0392b', 'Lost': '#95a5a6'
}
seg_order = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'Recent Customers',
             'Need Attention', 'About to Sleep', 'At Risk', 'Cant Lose Them', 'Lost']

# ── Sidebar Filters ──
st.sidebar.header("Filters")

segment_filter = st.sidebar.multiselect(
    "RFM Segment",
    options=[s for s in seg_order if s in df['segment'].unique()],
    default=[s for s in seg_order if s in df['segment'].unique()]
)

all_states = sorted(df['state'].dropna().unique())
state_filter = st.sidebar.multiselect("State", options=all_states, default=all_states)

r_range = st.sidebar.slider("Recency Score", 1, 5, (1, 5))
f_range = st.sidebar.slider("Frequency Score", 1, 5, (1, 5))
m_range = st.sidebar.slider("Monetary Score", 1, 5, (1, 5))

df_filtered = df[
    (df['segment'].isin(segment_filter)) &
    (df['state'].isin(state_filter)) &
    (df['r_score'] >= r_range[0]) & (df['r_score'] <= r_range[1]) &
    (df['f_score'] >= f_range[0]) & (df['f_score'] <= f_range[1]) &
    (df['m_score'] >= m_range[0]) & (df['m_score'] <= m_range[1])
]

# ── KPIs ──
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Customers (Filtered)", f"{len(df_filtered):,}")
with col2:
    st.metric("Avg Recency", f"{df_filtered['recency'].mean():.0f} days")
with col3:
    st.metric("Avg Frequency", f"{df_filtered['frequency'].mean():.2f} orders")
with col4:
    st.metric("Avg Monetary", f"R${df_filtered['monetary'].mean():,.0f}")
with col5:
    st.metric("Avg Review", f"{df_filtered['avg_review'].mean():.2f} ★")

st.divider()

# ── Segment Distribution ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Segment Distribution")
    seg_counts = df_filtered['segment'].value_counts()
    seg_counts = seg_counts.reindex([s for s in seg_order if s in seg_counts.index])

    fig = go.Figure(data=[go.Bar(
        x=seg_counts.index,
        y=seg_counts.values,
        marker_color=[seg_colors.get(s, '#3498db') for s in seg_counts.index],
        text=[f'{v:,}' for v in seg_counts.values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Segment', yaxis_title='Customers',
        height=400, showlegend=False, xaxis_tickangle=-30
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Revenue by Segment")
    seg_revenue = df_filtered.groupby('segment')['total_revenue'].sum()
    seg_revenue = seg_revenue.reindex([s for s in seg_order if s in seg_revenue.index])

    fig = go.Figure(data=[go.Bar(
        x=seg_revenue.index,
        y=seg_revenue.values,
        marker_color=[seg_colors.get(s, '#3498db') for s in seg_revenue.index],
        text=[f'R${v:,.0f}' for v in seg_revenue.values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Segment', yaxis_title='Total Revenue (R$)',
        height=400, showlegend=False, xaxis_tickangle=-30
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Segment Profiles (Avg R/F/M) ──
st.subheader("Segment Profiles")

profile = df_filtered.groupby('segment').agg({
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': 'mean',
    'customer_unique_id': 'count'
}).round(1)
profile.columns = ['Avg Recency (days)', 'Avg Frequency', 'Avg Monetary (R$)', 'Count']
profile = profile.reindex([s for s in seg_order if s in profile.index])

st.dataframe(
    profile.style.format({
        'Avg Recency (days)': '{:.0f}',
        'Avg Frequency': '{:.2f}',
        'Avg Monetary (R$)': 'R${:,.0f}',
        'Count': '{:,}'
    }),
    use_container_width=True
)

st.divider()

# ── RFM Score Scatter (R vs M, sized by F) ──
st.subheader("RFM Scatter: Recency vs Monetary (sized by Frequency)")

# Sample for performance
sample = df_filtered.sample(min(5000, len(df_filtered)), random_state=42)

fig = px.scatter(
    sample,
    x='recency',
    y='monetary',
    size='frequency',
    color='segment',
    color_discrete_map=seg_colors,
    hover_data=['state', 'order_count', 'avg_review'],
    opacity=0.6,
    size_max=20
)
fig.update_layout(
    xaxis_title='Recency (days since last purchase)',
    yaxis_title='Monetary (total spend R$)',
    height=500,
    legend=dict(orientation='h', y=-0.2)
)
st.plotly_chart(fig, use_container_width=True)

# ── Geographic Breakdown ──
st.subheader("Segment Distribution by State (Top 15)")

top_states = df_filtered['state'].value_counts().head(15).index
state_seg = df_filtered[df_filtered['state'].isin(top_states)].groupby(
    ['state', 'segment']
).size().reset_index(name='count')

fig = px.bar(
    state_seg,
    x='state',
    y='count',
    color='segment',
    color_discrete_map=seg_colors,
    category_orders={'segment': seg_order}
)
fig.update_layout(
    xaxis_title='State', yaxis_title='Customers',
    height=450, barmode='stack',
    legend=dict(orientation='h', y=-0.25)
)
st.plotly_chart(fig, use_container_width=True)

# ── Data Table ──
with st.expander("View Customer-Level RFM Data"):
    display_cols = ['customer_unique_id', 'segment', 'r_score', 'f_score', 'm_score',
                    'recency', 'frequency', 'monetary', 'state', 'order_count', 'avg_review']
    st.dataframe(df_filtered[display_cols].head(500), use_container_width=True, height=400)
