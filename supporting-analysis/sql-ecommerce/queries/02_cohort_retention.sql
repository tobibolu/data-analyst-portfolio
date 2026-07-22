-- Customer Cohort & Retention Analysis
-- Tools: DuckDB | Dataset: Olist Brazilian E-Commerce

-- 2a. Full cohort retention matrix
WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', MIN(o.order_purchase_timestamp)) AS cohort_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
all_purchases AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS purchase_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),
cohort_activity AS (
    SELECT
        fp.cohort_month,
        DATEDIFF('month', fp.cohort_month, ap.purchase_month) AS months_since_first,
        COUNT(DISTINCT ap.customer_unique_id) AS active_customers
    FROM first_purchase fp
    JOIN all_purchases ap ON fp.customer_unique_id = ap.customer_unique_id
    GROUP BY 1, 2
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM first_purchase
    GROUP BY 1
)
SELECT
    ca.cohort_month,
    cs.cohort_size,
    ca.months_since_first,
    ca.active_customers,
    ROUND(ca.active_customers * 100.0 / cs.cohort_size, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
WHERE ca.months_since_first BETWEEN 0 AND 12
ORDER BY ca.cohort_month, ca.months_since_first;


-- 2b. Average retention curve across all cohorts
WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', MIN(o.order_purchase_timestamp)) AS cohort_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
all_purchases AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS purchase_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),
cohort_activity AS (
    SELECT
        fp.cohort_month,
        DATEDIFF('month', fp.cohort_month, ap.purchase_month) AS months_since_first,
        COUNT(DISTINCT ap.customer_unique_id) AS active_customers
    FROM first_purchase fp
    JOIN all_purchases ap ON fp.customer_unique_id = ap.customer_unique_id
    GROUP BY 1, 2
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM first_purchase
    GROUP BY 1
)
SELECT
    ca.months_since_first,
    ROUND(AVG(ca.active_customers * 100.0 / cs.cohort_size), 2) AS avg_retention_pct,
    COUNT(DISTINCT ca.cohort_month) AS num_cohorts
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
WHERE ca.months_since_first BETWEEN 0 AND 12
GROUP BY 1
ORDER BY 1;
