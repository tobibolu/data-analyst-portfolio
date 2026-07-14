# Data Analyst Portfolio

A set of analytics projects covering SQL, statistical analysis, data pipeline development, dashboard design, and business-focused data storytelling.

## Projects

### [Project A: SQL Analytics Deep Dive](./project-a-sql-ecommerce/)
Advanced SQL analysis of 96K+ delivered e-commerce orders using DuckDB. Covers revenue breakdown with window functions, customer cohort retention, seller performance tiering, delivery funnel analysis, and LTV estimation. Every insight is generated through SQL, with business recommendations.

### [Project B: Nigerian Telecom Churn Pipeline](./project-b-fintech-churn/)
Leakage-safe audit of churn modelling for MTN Nigeria customers. The project finds and withdraws an invalid high score caused by a post-outcome feature and by repeated customers crossing the train/test split, then rebuilds the workflow at customer level with train-only preprocessing, stratified cross-validation, an untouched holdout, cost-sensitive threshold analysis, and a Streamlit evidence dashboard. The corrected model is documented as not deployment-ready, which shows why the next requirement is better timestamped behavioural data, not a more complex algorithm.

### [Project C: Cohort & Retention Deep Dive](./project-c-cohort-retention/)
Customer lifecycle analytics on the Olist e-commerce dataset. Covers cohort-based retention analysis, RFM segmentation (Recency/Frequency/Monetary scoring), 12-month LTV estimation by segment and geography, and churn risk flagging. Includes an interactive [Tableau Public dashboard](https://public.tableau.com/app/profile/tobi.bolu/viz/OlistE-CommerceCohortRetentionAnalytics/CohortRetentionHeatmap) and a multi-page Streamlit app.

## Tools & Technologies

Python, SQL (DuckDB, PostgreSQL, BigQuery), Pandas, Plotly, Tableau Public, Streamlit, Scikit-learn, Jupyter

## Author

**Tobi Bolu** · [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)
