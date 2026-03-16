"""Page 1: Cohort Retention Analysis"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Cohort Retention", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    cohort = pd.read_csv('./tableau_cohort_retention.csv')
    return cohort

df = load_data()

st.title("📊 Cohort Retention Analysis")
st.markdown("I'm tracking customer repurchase behavior by acquisition month.")

# ── Sidebar Filters ──
st.sidebar.header("Filters")

all_cohorts = sorted(df['cohort'].unique())
cohort_filter = st.sidebar.multiselect(
    "Acquisition Cohort",
    options=all_cohorts,
    default=all_cohorts
)

max_period = int(df['cohort_period'].max())
period_range = st.sidebar.slider("Cohort Period (Months)", 0, max_period, (0, min(12, max_period)))

df_filtered = df[
    (df['cohort'].isin(cohort_filter)) &
    (df['cohort_period'] >= period_range[0]) &
    (df['cohort_period'] <= period_range[1])
]

# ── KPIs ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Cohorts", f"{df_filtered['cohort'].nunique()}")
with col2:
    avg_m1 = df_filtered[df_filtered['cohort_period'] == 1]['retention_rate'].mean()
    st.metric("Avg Month 1 Retention", f"{avg_m1:.2f}%" if not np.isnan(avg_m1) else "N/A")
with col3:
    avg_m3 = df_filtered[df_filtered['cohort_period'] == 3]['retention_rate'].mean()
    st.metric("Avg Month 3 Retention", f"{avg_m3:.2f}%" if not np.isnan(avg_m3) else "N/A")
with col4:
    total_acquired = df_filtered[df_filtered['cohort_period'] == 0]['customers'].sum()
    st.metric("Total Acquired", f"{total_acquired:,}")

st.divider()

# ── Retention Heatmap ──
st.subheader("Retention Heatmap")

pivot = df_filtered.pivot_table(index='cohort', columns='cohort_period', values='retention_rate', aggfunc='mean')
pivot = pivot.sort_index()

fig = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=[f'Month {int(c)}' for c in pivot.columns],
    y=[str(c) for c in pivot.index],
    colorscale='YlOrRd',
    reversescale=True,
    texttemplate='%{z:.1f}%',
    textfont={'size': 9},
    hovertemplate='Cohort: %{y}<br>Period: %{x}<br>Retention: %{z:.1f}%<extra></extra>',
    colorbar=dict(title='%')
))
fig.update_layout(
    xaxis_title='Months Since First Purchase',
    yaxis_title='Acquisition Cohort',
    height=max(400, len(pivot) * 25 + 100),
    yaxis=dict(autorange='reversed'),
    margin=dict(l=100)
)
st.plotly_chart(fig, use_container_width=True)

# ── Retention Curves ──
st.subheader("Retention Curves by Cohort")

# Let user pick specific cohorts to compare
compare_cohorts = st.multiselect(
    "Select cohorts to compare (leave empty for average)",
    options=all_cohorts,
    default=[]
)

fig = go.Figure()

if compare_cohorts:
    for cohort in compare_cohorts:
        cdata = df_filtered[df_filtered['cohort'] == cohort].sort_values('cohort_period')
        fig.add_trace(go.Scatter(
            x=cdata['cohort_period'],
            y=cdata['retention_rate'],
            mode='lines+markers',
            name=str(cohort),
            marker=dict(size=6)
        ))
else:
    avg = df_filtered.groupby('cohort_period')['retention_rate'].mean().reset_index()
    fig.add_trace(go.Scatter(
        x=avg['cohort_period'],
        y=avg['retention_rate'],
        mode='lines+markers',
        name='All Cohorts (Avg)',
        marker=dict(size=8, color='#e74c3c'),
        line=dict(width=2, color='#e74c3c')
    ))

fig.update_layout(
    xaxis_title='Months Since First Purchase',
    yaxis_title='Retention Rate (%)',
    height=400,
    legend=dict(orientation='h', y=-0.2)
)
st.plotly_chart(fig, use_container_width=True)

# ── Cohort Size Over Time ──
st.subheader("Cohort Sizes (New Customers Acquired Per Month)")

cohort_sizes = df_filtered[df_filtered['cohort_period'] == 0][['cohort', 'customers']].sort_values('cohort')

fig = go.Figure(data=[go.Bar(
    x=[str(c) for c in cohort_sizes['cohort']],
    y=cohort_sizes['customers'],
    marker_color='#3498db',
    text=cohort_sizes['customers'],
    textposition='auto'
)])
fig.update_layout(
    xaxis_title='Acquisition Month',
    yaxis_title='New Customers',
    height=350,
    showlegend=False,
    xaxis_tickangle=-45
)
st.plotly_chart(fig, use_container_width=True)

# ── Data Table ──
with st.expander("View Raw Cohort Data"):
    st.dataframe(df_filtered, use_container_width=True, height=400)
