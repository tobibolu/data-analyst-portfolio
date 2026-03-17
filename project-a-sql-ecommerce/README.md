# Brazilian E-Commerce SQL Analytics Deep Dive

An advanced SQL analysis of 96K+ delivered orders (R\$15.4M in revenue) from the Olist Brazilian e-commerce marketplace, exploring revenue performance, customer retention, seller quality, delivery operations, and customer lifetime value.

Every insight is generated through SQL queries executed via [DuckDB](https://duckdb.org/), demonstrating proficiency in CTEs, window functions (LAG, NTILE, PERCENT_RANK, SUM OVER), cohort analysis, and business-oriented data storytelling.

## Dataset

[Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 9 linked tables covering 99K orders, 93K customers, 3K sellers, 33K products, 100K payments, and 99K reviews for a Brazilian e-commerce marketplace (Sept 2016 to Aug 2018).

## Key Findings

**R\$15.4M in revenue with strong growth, but geographically concentrated.** Sao Paulo drives 37% of total revenue (R\$5.77M), but per-customer spend is actually higher in smaller states: BA (R\$187), GO (R\$176), and SC (R\$173) all outperform SP's R\$147. Health & Beauty leads category revenue at 9.3%, with no single category exceeding 10%, indicating healthy diversification.

**97% of customers never return, the single biggest growth opportunity.** The cohort retention matrix shows average retention crashing to 5.45% by month 1 and below 1% by month 2. This is partly structural (marketplace aggregator model where customers don't realize they're buying through Olist), but the 3% who do return spend 1.8x to 5.2x more than one-time buyers. Even a modest retention improvement would compound into significant revenue.

**304 Gold-tier sellers anchor the marketplace, but 32 sellers are actively damaging the brand.** Of 1,766 qualified sellers, the tiering framework (based on NTILE revenue quartiles and review scores) identifies a clear quality spectrum. At Risk sellers (sub-3.0 review scores) need intervention or removal to protect customer experience.

**Late deliveries destroy satisfaction in a near-linear pattern.** On-time orders average 4.29 stars (9.2% negative reviews). Late by 1-7 days: 3.06 stars (39.7% negative). Late by 7+ days: 1.70 stars (79.2% negative). Northern states face 2-3x longer transit times than SP, with Amapa averaging 27.2 days versus SP's 8.7.

**The re-engagement window is 30 days.** 50.3% of repeat purchases happen within 30 days of the previous order, and 61.8% within 60 days. After 90 days, return probability drops significantly. This defines exactly when automated retention campaigns should fire.

## Analysis Sections

| Section | SQL Concepts | Business Focus |
|---------|-------------|----------------|
| Revenue Breakdown | LAG, SUM OVER, RANK, running totals | MoM growth, category performance, state revenue |
| Cohort Retention | CTEs, DATEDIFF, cohort grouping, pivoting | Retention matrix, average retention curve |
| Seller Performance | NTILE, PERCENT_RANK, CASE tiering | Seller scorecard, quality tiers, risk flagging |
| Delivery Funnel | Stage timing, conditional aggregation | Fulfillment bottlenecks, late delivery impact on reviews |
| Repeat Purchase & LTV | LAG (order sequences), GREATEST, segmentation | Purchase frequency, 12-month LTV, repurchase gap |

## Recommended Actions

1. Launch a 21-day and 45-day post-purchase re-engagement campaign targeting the 30-day window where 50% of repeat purchases occur
2. Implement the seller tier system with a minimum 3.5 review score threshold, with improvement plans for At Risk sellers
3. Investigate logistics partnerships for northern states where transit times are 2-3x the platform average
4. Increase marketing investment in high-LTV states (PB, AC, RO, AL) showing R\$2,800+ estimated 12-month LTV, nearly double SP's R\$1,719
5. Surface the Olist brand identity at point of purchase to address the structural retention problem

## How to Run

```bash
pip install duckdb kagglehub matplotlib seaborn pandas jupyter
```

Open `analysis.ipynb` in Jupyter and run all cells. The notebook downloads the dataset automatically via `kagglehub` (requires a [Kaggle API key](https://www.kaggle.com/docs/api) at `~/.kaggle/kaggle.json`).

Standalone SQL queries are available in the `queries/` folder for reference or adaptation to other SQL engines.

## Tools

Python, DuckDB, Matplotlib, Seaborn, Pandas, Jupyter

## Author

**Tobi Bolu** — [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)
