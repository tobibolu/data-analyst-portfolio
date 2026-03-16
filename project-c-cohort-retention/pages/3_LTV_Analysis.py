"""Page 3: Customer Lifetime Value Analysis"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="LTV Analysis", page_icon="💰", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('./tableau_ltv_data.csv')

df = load_data()

st.title("💰 Customer Lifetime Value Analysis")
st.markdown("I'm estimating 12-month customer lifetime value by segment, geography, and cohort.")

seg_colors = {
    'Champions': '#2ecc71', 'Loyal Customers': '#27ae60', 'Potential Loyalists': '#3498db',
    'Recent Customers': '#1abc9c', 'Need Attention': '#f39c12', 'About to Sleep': '#e67e22',
    'At Risk': '#e74c3c', 'Cant Lose Them': '#c0392b', 'Lost': '#95a5a6'
}

# ── Sidebar Filters ──
st.sidebar.header("Filters")

all_segments = sorted(df['segment'].unique())
seg_filter = st.sidebar.multiselect("Segment", options=all_segments, default=all_segments)

all_states = sorted(df['state'].dropna().unique())
state_filter = st.sidebar.multiselect("State", options=all_states, default=all_states)

ltv_range = st.sidebar.slider(
    "LTV Range (R$)",
    float(df['ltv_12m'].min()),
    min(float(df['ltv_12m'].quantile(0.99)), float(df['ltv_12m'].max())),
    (float(df['ltv_12m'].min()), min(float(df['ltv_12m'].quantile(0.99)), float(df['ltv_12m'].max())))
)

df_filtered = df[
    (df['segment'].isin(seg_filter)) &
    (df['state'].isin(state_filter)) &
    (df['ltv_12m'] >= ltv_range[0]) &
    (df['ltv_12m'] <= ltv_range[1])
]

# ── KPIs ──
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Customers", f"{len(df_filtered):,}")
with col2:
    st.metric("Avg LTV", f"R${df_filtered['ltv_12m'].mean():,.0f}")
with col3:
    st.metric("Median LTV", f"R${df_filtered['ltv_12m'].median():,.0f}")
with col4:
    st.metric("Total Revenue", f"R${df_filtered['total_revenue'].sum():,.0f}")
with col5:
    st.metric("Avg Order Value", f"R${df_filtered['avg_order_value'].mean():,.0f}")

st.divider()

# ── LTV by Segment ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Average LTV by Segment")
    seg_ltv = df_filtered.groupby('segment')['ltv_12m'].mean().sort_values(ascending=True)

    fig = go.Figure(data=[go.Bar(
        x=seg_ltv.values,
        y=seg_ltv.index,
        orientation='h',
        marker_color=[seg_colors.get(s, '#3498db') for s in seg_ltv.index],
        text=[f'R${v:,.0f}' for v in seg_ltv.values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Avg 12-Month LTV (R$)',
        height=400, showlegend=False, margin=dict(l=130)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Revenue Concentration by Segment")
    seg_rev = df_filtered.groupby('segment')['total_revenue'].sum().sort_values(ascending=False)

    fig = go.Figure(data=[go.Pie(
        labels=seg_rev.index,
        values=seg_rev.values,
        marker=dict(colors=[seg_colors.get(s, '#3498db') for s in seg_rev.index]),
        textinfo='label+percent',
        hole=0.35
    )])
    fig.update_layout(height=400, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── LTV by State ──
st.subheader("Average LTV by State")

col_map, col_bar = st.columns([1, 1])

with col_bar:
    state_ltv = df_filtered.groupby('state').agg(
        avg_ltv=('ltv_12m', 'mean'),
        customers=('customer_unique_id', 'nunique'),
        total_rev=('total_revenue', 'sum')
    ).sort_values('avg_ltv', ascending=False).head(20)

    fig = go.Figure(data=[go.Bar(
        x=state_ltv['avg_ltv'],
        y=state_ltv.index,
        orientation='h',
        marker_color='#9b59b6',
        text=[f'R${v:,.0f} ({c:,} cust)' for v, c in zip(state_ltv['avg_ltv'], state_ltv['customers'])],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title='Avg 12-Month LTV (R$)',
        height=550, showlegend=False, margin=dict(l=60),
        yaxis=dict(autorange='reversed')
    )
    st.plotly_chart(fig, use_container_width=True)

with col_map:
    st.markdown("**LTV vs Customer Volume by State**")
    state_scatter = df_filtered.groupby('state').agg(
        avg_ltv=('ltv_12m', 'mean'),
        customers=('customer_unique_id', 'nunique'),
        avg_review=('avg_review', 'mean')
    ).reset_index()

    fig = px.scatter(
        state_scatter,
        x='customers',
        y='avg_ltv',
        size='customers',
        color='avg_ltv',
        color_continuous_scale='Viridis',
        text='state',
        hover_data={'avg_review': ':.2f'}
    )
    fig.update_traces(textposition='top center', textfont_size=9)
    fig.update_layout(
        xaxis_title='Number of Customers',
        yaxis_title='Avg LTV (R$)',
        height=550, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── LTV by Cohort ──
st.subheader("Average LTV by Acquisition Cohort")

cohort_ltv = df_filtered.groupby('cohort').agg(
    avg_ltv=('ltv_12m', 'mean'),
    customers=('customer_unique_id', 'nunique')
).reset_index().sort_values('cohort')

fig = go.Figure()
fig.add_trace(go.Bar(
    x=cohort_ltv['cohort'],
    y=cohort_ltv['avg_ltv'],
    marker_color='#3498db',
    name='Avg LTV',
    text=[f'R${v:,.0f}' for v in cohort_ltv['avg_ltv']],
    textposition='auto'
))
fig.update_layout(
    xaxis_title='Acquisition Cohort',
    yaxis_title='Avg 12-Month LTV (R$)',
    height=400, showlegend=False,
    xaxis_tickangle=-45
)
st.plotly_chart(fig, use_container_width=True)

# ── LTV Distribution ──
st.subheader("LTV Distribution")

fig = go.Figure(data=[go.Histogram(
    x=df_filtered['ltv_12m'],
    nbinsx=50,
    marker_color='#3498db'
)])
fig.update_layout(
    xaxis_title='Estimated 12-Month LTV (R$)',
    yaxis_title='Number of Customers',
    height=350, showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

# ── Data Table ──
with st.expander("View Top 100 Highest-LTV Customers"):
    top_ltv = df_filtered.nlargest(100, 'ltv_12m')
    st.dataframe(top_ltv, use_container_width=True, height=400)
