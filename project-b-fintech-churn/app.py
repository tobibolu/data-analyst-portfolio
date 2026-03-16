"""
Streamlit Dashboard: MTN Nigeria Churn Risk Analytics
Author: Tobi Bolu | https://github.com/tobibolu
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Churn Risk Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load cleaned data and predictions."""
    try:
        df_clean = pd.read_csv('./cleaned_data.csv')
        df_predictions = pd.read_csv('./predictions.csv')
        return df_clean, df_predictions
    except FileNotFoundError:
        return None, None

# Main
st.title("📊 MTN Nigeria Customer Churn Risk Dashboard")
st.markdown("*Real-time risk analytics for customer retention*")
st.markdown("**Author:** Tobi Bolu | [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)")

df_clean, df_predictions = load_data()

if df_clean is None or df_predictions is None:
    st.warning("⚠️ Data files not found!")
    st.info("""
    **Setup Instructions:**
    1. Run `01_eda_cleaning.ipynb` to generate `cleaned_data.csv`
    2. Run `03_churn_model.ipynb` to generate `predictions.csv`
    3. Refresh this dashboard
    """)
else:
    # Merge data
    df = df_clean.copy()
    df = pd.concat([df, df_predictions[['churn_probability', 'risk_level']]], axis=1)

    # Detect churn column
    churn_col = [c for c in df.columns if 'churn' in c.lower() and c not in ['churn_probability', 'risk_level']]
    churn_col_name = churn_col[0] if churn_col else None

    # Detect state column for geographic filter
    state_col = [c for c in df.columns if 'state' in c.lower()]
    state_col_name = state_col[0] if state_col else None

    # Sidebar filters
    st.sidebar.header("Filters")
    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        options=['Critical', 'High', 'Medium', 'Low'],
        default=['Critical', 'High', 'Medium', 'Low']
    )
    prob_range = st.sidebar.slider(
        "Churn Probability Range",
        0.0, 1.0, (0.0, 1.0)
    )

    if state_col_name:
        all_states = sorted(df[state_col_name].dropna().unique().tolist())
        state_filter = st.sidebar.multiselect(
            "State",
            options=all_states,
            default=all_states
        )
    else:
        state_filter = None

    # Apply filters
    mask = (
        (df['risk_level'].isin(risk_filter)) &
        (df['churn_probability'] >= prob_range[0]) &
        (df['churn_probability'] <= prob_range[1])
    )
    if state_filter is not None and state_col_name:
        mask = mask & (df[state_col_name].isin(state_filter))

    df_filtered = df[mask]

    # Metrics row — all driven by filtered data
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Customers (Filtered)", f"{len(df_filtered):,}", delta=f"of {len(df):,} total")

    with col2:
        if churn_col_name:
            churn_rate = df_filtered[churn_col_name].map({'Yes': 1, 'No': 0}).mean() * 100
            st.metric("Churn Rate", f"{churn_rate:.1f}%")
        else:
            st.metric("Churn Rate", "N/A")

    with col3:
        if len(df_filtered) > 0:
            avg_prob = df_filtered['churn_probability'].mean()
            st.metric("Avg Risk Probability", f"{avg_prob:.2%}")
        else:
            st.metric("Avg Risk Probability", "N/A")

    with col4:
        critical_count = (df_filtered['risk_level'] == 'Critical').sum()
        st.metric("Critical Risk", f"{critical_count:,}")

    st.divider()

    # Charts — all driven by filtered data
    st.header("Risk Analytics")

    col_left, col_right = st.columns(2)

    # Risk distribution bar
    with col_left:
        risk_dist = df_filtered['risk_level'].value_counts().reindex(['Low', 'Medium', 'High', 'Critical']).fillna(0)
        colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e67e22', 'Critical': '#e74c3c'}
        fig_risk = go.Figure(data=[
            go.Bar(
                x=risk_dist.index,
                y=risk_dist.values,
                marker_color=[colors.get(x, '#3498db') for x in risk_dist.index],
                text=[int(v) for v in risk_dist.values],
                textposition='auto'
            )
        ])
        fig_risk.update_layout(
            title="Risk Level Distribution",
            xaxis_title="Risk Level",
            yaxis_title="Count",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    # Probability histogram
    with col_right:
        fig_hist = go.Figure(data=[
            go.Histogram(
                x=df_filtered['churn_probability'],
                nbinsx=40,
                marker_color='#3498db',
                name='Churn Probability'
            )
        ])
        fig_hist.update_layout(
            title="Distribution of Churn Probability Scores",
            xaxis_title="Churn Probability",
            yaxis_title="Frequency",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    # Geographic breakdown if state column exists
    if state_col_name and churn_col_name:
        st.header("Geographic Breakdown")

        col_geo1, col_geo2 = st.columns(2)

        with col_geo1:
            # Churn rate by state
            state_churn = df_filtered.groupby(state_col_name).apply(
                lambda x: x[churn_col_name].map({'Yes': 1, 'No': 0}).mean() * 100
            ).sort_values(ascending=False).head(15)

            fig_state = go.Figure(data=[
                go.Bar(
                    x=state_churn.values,
                    y=state_churn.index,
                    orientation='h',
                    marker_color=['#e74c3c' if v > 35 else '#f39c12' if v > 25 else '#2ecc71' for v in state_churn.values],
                    text=[f'{v:.1f}%' for v in state_churn.values],
                    textposition='auto'
                )
            ])
            fig_state.update_layout(
                title="Churn Rate by State (Top 15)",
                xaxis_title="Churn Rate (%)",
                showlegend=False,
                height=500,
                margin=dict(l=120)
            )
            st.plotly_chart(fig_state, use_container_width=True)

        with col_geo2:
            # Customer count by state
            state_counts = df_filtered[state_col_name].value_counts().head(15)
            fig_counts = go.Figure(data=[
                go.Bar(
                    x=state_counts.values,
                    y=state_counts.index,
                    orientation='h',
                    marker_color='#9b59b6',
                    text=state_counts.values,
                    textposition='auto'
                )
            ])
            fig_counts.update_layout(
                title="Customer Count by State (Top 15)",
                xaxis_title="Number of Customers",
                showlegend=False,
                height=500,
                margin=dict(l=120)
            )
            st.plotly_chart(fig_counts, use_container_width=True)

        st.divider()

    # Model performance summary
    st.header("Model Summary")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Model AUC", "0.9204")
    col_m2.metric("Accuracy", "93.3%")
    col_m3.metric("Precision", "97.8%")
    col_m4.metric("Recall", "78.9%")

    st.divider()

    # Top at-risk customers table
    st.header("At-Risk Customers")

    st.write(f"Showing top 20 highest-risk from {len(df_filtered):,} filtered customers")

    # Select columns to display
    display_cols = ['churn_probability', 'risk_level']
    if state_col_name:
        display_cols.append(state_col_name)
    for col in df_filtered.columns:
        if any(p in col.lower() for p in ['tenure', 'age', 'usage', 'complaint', 'balance', 'gender', 'subscription']):
            if col not in display_cols:
                display_cols.append(col)

    display_cols = display_cols[:10]

    if len(df_filtered) > 0:
        top_at_risk = df_filtered.nlargest(20, 'churn_probability')[display_cols].copy()
        top_at_risk['churn_probability'] = top_at_risk['churn_probability'].apply(lambda x: f'{x:.1%}')
        st.dataframe(top_at_risk, use_container_width=True, height=500)
    else:
        st.info("No customers match the current filters.")

    # Download results
    st.sidebar.divider()
    st.sidebar.header("Export")

    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Filtered Results (CSV)",
        data=csv,
        file_name="churn_risk_export.csv",
        mime="text/csv"
    )

st.divider()
st.markdown("*Dashboard built with Streamlit | Data: MTN Nigeria Customer Churn*")
