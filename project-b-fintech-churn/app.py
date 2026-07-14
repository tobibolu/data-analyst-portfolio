"""Exploratory dashboard for the leakage-safe MTN churn model audit."""

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="MTN Churn Model Audit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_artifacts():
    """Load customer-level demo scores and the executed notebook's metrics."""
    predictions = pd.read_csv(PROJECT_DIR / "predictions.csv")
    metrics = json.loads((PROJECT_DIR / "model_metrics.json").read_text())
    return predictions, metrics


st.title("📊 MTN Nigeria Churn Model Audit")
st.caption("Leakage-safe customer-level evaluation and exploratory score diagnostics")
st.markdown(
    "**Author:** Tobi Bolu · "
    "[LinkedIn](https://www.linkedin.com/in/tobibolu/) · "
    "[GitHub](https://github.com/tobibolu)"
)

try:
    df, metrics = load_artifacts()
except FileNotFoundError:
    st.warning("Model artifacts were not found.")
    st.info("Execute `03_churn_model.ipynb` from top to bottom, then refresh this page.")
    st.stop()

holdout = metrics["holdout_default_0_50"]
threshold_result = metrics["holdout_cost_selected"]
threshold_policy = metrics["threshold_policy"]

st.error(
    "**Audit result: not deployment-ready.** After removing post-outcome fields and "
    "preventing repeated customers from crossing the split, holdout ROC AUC is "
    f"{holdout['roc_auc']:.3f}. The exported scores below are exploratory—not validated "
    "retention decisions."
)

with st.expander("Why the previous high score was withdrawn", expanded=False):
    st.markdown(
        "The earlier model used `Reasons for Churn`, which is only known after the outcome, "
        "and split 974 rows even though they represented 496 unique customers. The rebuilt "
        "notebook aggregates first, excludes identifiers and temporally unsafe fields, and "
        "fits all preprocessing inside the training pipeline."
    )

st.header("Evaluation evidence")
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Mean CV ROC AUC",
    f"{metrics['cv']['roc_auc']['mean']:.3f}",
    help="Five-fold stratified cross-validation on training customers only.",
)
col2.metric(
    "Holdout ROC AUC",
    f"{holdout['roc_auc']:.3f}",
    help="Measured once on 124 untouched customers.",
)
col3.metric(
    "Holdout avg precision",
    f"{holdout['average_precision']:.3f}",
    help=f"Compare with holdout churn prevalence of {threshold_result['tp'] + threshold_result['fn']} / {metrics['holdout_customers']}.",
)
col4.metric("Untouched customers", f"{metrics['holdout_customers']:,}")

st.info(
    f"The illustrative 5:1 false-negative:false-positive policy selected a "
    f"{threshold_policy['selected_threshold']:.2f} threshold from out-of-fold training "
    f"predictions. On the holdout it flagged all {metrics['holdout_customers']} customers. "
    "That is evidence the current features cannot prioritise interventions effectively."
)

st.divider()
st.header("Exploratory customer scores")
st.caption(
    "Score bands are relative ranks from a full-data demonstration fit: top 10% Critical, "
    "next 15% High, next 25% Medium, and bottom 50% Low. They are not calibrated risk tiers."
)

st.sidebar.header("Filters")
risk_order = ["Critical", "High", "Medium", "Low"]
risk_filter = st.sidebar.multiselect(
    "Relative score band",
    options=risk_order,
    default=risk_order,
)
score_range = st.sidebar.slider(
    "Model score range",
    min_value=0.0,
    max_value=1.0,
    value=(0.0, 1.0),
)
states = sorted(df["state"].dropna().unique().tolist())
state_filter = st.sidebar.multiselect("State", options=states, default=states)

mask = (
    df["risk_level"].isin(risk_filter)
    & df["churn_probability"].between(*score_range)
    & df["state"].isin(state_filter)
)
filtered = df.loc[mask].copy()

summary1, summary2, summary3, summary4 = st.columns(4)
summary1.metric("Customers shown", f"{len(filtered):,}", f"of {len(df):,}")
summary2.metric(
    "Observed churn rate",
    f"{filtered['churn'].eq('Yes').mean():.1%}" if len(filtered) else "N/A",
)
summary3.metric(
    "Mean demo score",
    f"{filtered['churn_probability'].mean():.1%}" if len(filtered) else "N/A",
)
summary4.metric(
    "Top-band customers",
    f"{filtered['risk_level'].eq('Critical').sum():,}",
)

left, right = st.columns(2)
with left:
    band_counts = (
        filtered["risk_level"]
        .value_counts()
        .reindex(risk_order)
        .fillna(0)
        .rename_axis("score_band")
        .reset_index(name="customers")
    )
    fig = px.bar(
        band_counts,
        x="score_band",
        y="customers",
        category_orders={"score_band": risk_order},
        color="score_band",
        color_discrete_map={
            "Critical": "#d73027",
            "High": "#fc8d59",
            "Medium": "#fee08b",
            "Low": "#91cf60",
        },
        title="Relative score-band distribution",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.histogram(
        filtered,
        x="churn_probability",
        color="churn",
        nbins=30,
        barmode="overlay",
        opacity=0.65,
        title="Demo-score overlap by observed outcome",
        labels={"churn_probability": "Exploratory model score", "churn": "Observed churn"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Highest exploratory scores")
display_columns = [
    "Customer ID",
    "churn_probability",
    "score_percentile",
    "risk_level",
    "churn",
    "state",
    "age",
    "gender",
    "tenure_months",
    "primary_plan",
]
if filtered.empty:
    st.info("No customers match the current filters.")
else:
    table = filtered.nlargest(20, "churn_probability")[display_columns].copy()
    table["churn_probability"] = table["churn_probability"].map(lambda value: f"{value:.1%}")
    table["score_percentile"] = table["score_percentile"].map(lambda value: f"{value:.1%}")
    st.dataframe(table, use_container_width=True, hide_index=True)

st.sidebar.divider()
st.sidebar.download_button(
    "Download filtered exploratory scores",
    data=filtered.to_csv(index=False),
    file_name="mtn_churn_exploratory_scores.csv",
    mime="text/csv",
)

st.divider()
st.caption("Dashboard built with Streamlit · Data: MTN Nigeria Customer Churn")
