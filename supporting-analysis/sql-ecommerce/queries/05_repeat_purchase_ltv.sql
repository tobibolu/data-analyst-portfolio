-- Repeat Purchase & LTV Signals
-- Tools: DuckDB | Dataset: Olist Brazilian E-Commerce

-- 5a. Repeat purchase rate distribution
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_spend,
        MIN(o.order_purchase_timestamp) AS first_order,
        MAX(o.order_purchase_timestamp) AS last_order,
        DATEDIFF('day', MIN(o.order_purchase_timestamp), MAX(o.order_purchase_timestamp)) AS days_between_first_last
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    CASE
        WHEN order_count = 1 THEN '1 order (one-time)'
        WHEN order_count = 2 THEN '2 orders'
        WHEN order_count BETWEEN 3 AND 5 THEN '3-5 orders'
        ELSE '6+ orders'
    END AS purchase_frequency,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
    ROUND(AVG(total_spend), 2) AS avg_total_spend,
    ROUND(AVG(days_between_first_last), 0) AS avg_days_active
FROM customer_orders
GROUP BY 1
ORDER BY MIN(order_count);


-- 5b. 12-month LTV estimate by customer state
WITH customer_metrics AS (
    SELECT
        c.customer_unique_id,
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_spend,
        DATEDIFF('month', MIN(o.order_purchase_timestamp), MAX(o.order_purchase_timestamp)) + 1 AS months_active
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2
)
SELECT
    customer_state AS state,
    COUNT(*) AS total_customers,
    ROUND(AVG(order_count), 2) AS avg_orders,
    ROUND(AVG(total_spend), 2) AS avg_spend,
    ROUND(AVG(total_spend / GREATEST(months_active, 1)) * 12, 2) AS estimated_12mo_ltv,
    ROUND(
        COUNT(CASE WHEN order_count > 1 THEN 1 END) * 100.0 / COUNT(*),
        1
    ) AS repeat_purchase_rate
FROM customer_metrics
GROUP BY 1
HAVING COUNT(*) >= 50
ORDER BY estimated_12mo_ltv DESC;


-- 5c. Repurchase gap analysis (LAG window function)
WITH customer_order_sequence AS (
    SELECT
        c.customer_unique_id,
        o.order_purchase_timestamp,
        LAG(o.order_purchase_timestamp) OVER (
            PARTITION BY c.customer_unique_id
            ORDER BY o.order_purchase_timestamp
        ) AS prev_order_date,
        DATEDIFF('day',
            LAG(o.order_purchase_timestamp) OVER (
                PARTITION BY c.customer_unique_id
                ORDER BY o.order_purchase_timestamp
            ),
            o.order_purchase_timestamp
        ) AS days_since_last_order
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT
    CASE
        WHEN days_since_last_order <= 30 THEN '0-30 days'
        WHEN days_since_last_order <= 60 THEN '31-60 days'
        WHEN days_since_last_order <= 90 THEN '61-90 days'
        WHEN days_since_last_order <= 180 THEN '91-180 days'
        ELSE '180+ days'
    END AS repurchase_window,
    COUNT(*) AS repurchase_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_repurchases
FROM customer_order_sequence
WHERE days_since_last_order IS NOT NULL
GROUP BY 1
ORDER BY MIN(days_since_last_order);
