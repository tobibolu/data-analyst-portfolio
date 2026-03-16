# Project C: Cohort & Retention Deep Dive

> **Interactive charts?** View this notebook on [nbviewer](https://nbviewer.org/github/tobibolu/data-analyst-portfolio/blob/main/project-c-cohort-retention/analysis.ipynb) — GitHub strips JavaScript from Plotly charts.

## Overview

Customer lifecycle analytics on the Olist Brazilian e-commerce dataset, covering cohort-based retention, RFM segmentation, lifetime value estimation, and churn risk flagging. Complements Project A's SQL analytics by shifting from transaction-level queries to customer-level behavioral modeling.

An interactive **Tableau Public** dashboard is published alongside the notebook analysis.

## Dataset

[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — same dataset as Project A, reanalyzed from a customer lifecycle perspective.

- ~96K delivered orders
- ~93K unique customers
- Date range: Oct 2016 – Aug 2018

## Key Findings

**Cohort Retention:** Average Month 1 retention is in the low single digits, dropping below 1% by Month 3. This is structural — Olist operates as a marketplace aggregator where customers don't realize they purchased through Olist. The pattern is consistent across all acquisition cohorts.

**RFM Segmentation:** The vast majority of customers fall into "Lost" or "About to Sleep" segments (single purchase, long ago). The small Champions and Loyal Customers segments drive an outsized share of revenue relative to headcount.

**Lifetime Value:** Smaller, remote states (PB, AC, RO) show the highest per-customer LTV — likely inflated by freight costs. Sao Paulo, the highest-volume state, has one of the lowest per-customer LTV figures. Retention spend per customer should vary by geography.

**Churn Risk:** "At Risk (Repeat)" customers are the highest-priority intervention group — they've already demonstrated willingness to repurchase and have since gone quiet. "Churned (One-time)" is the largest segment but hardest to reactivate.

## Tableau Public Dashboard

**[View the dashboard →](https://public.tableau.com/views/OlistE-CommerceCohortRetentionAnalytics/Story1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)**

The Tableau story includes:
1. **Cohort Retention** — heatmap and retention curves by acquisition month
2. **RFM Segments** — customer distribution, segment profiles, geographic breakdown
3. **LTV Analysis** — lifetime value by segment, state, and cohort
4. **Churn Risk** — risk tier distribution, at-risk customer profiles, state-level patterns

## Files

| File | Description |
|------|-------------|
| `analysis.ipynb` | Full analysis notebook (cohort, RFM, LTV, churn risk) |
| `tableau_cohort_retention.csv` | Cohort retention data in long format |
| `tableau_rfm_customers.csv` | Customer-level RFM scores and segments |
| `tableau_ltv_data.csv` | LTV estimates by customer with segment and geography |
| `tableau_churn_risk.csv` | Churn risk flags with RFM and behavioral data |

## Tools

Python (Pandas, Plotly), Tableau Public, Kaggle API (kagglehub)

## How to Run

```bash
cd project-c-cohort-retention
jupyter notebook analysis.ipynb
# Run all cells — generates 4 Tableau-ready CSV exports
```

---
*Analysis by Tobi Bolu | [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)*
