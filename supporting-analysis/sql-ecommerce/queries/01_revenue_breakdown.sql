-- Revenue Breakdown: Monthly revenue with MoM growth, category rankings, state analysis
-- Tools: DuckDB | Dataset: Olist Brazilian E-Commerce

-- 1a. Monthly revenue with month-over-month growth (LAG window function)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    order_month,
    total_orders,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY order_month))
        / NULLIF(LAG(total_revenue) OVER (ORDER BY order_month), 0) * 100,
        1
    ) AS mom_growth_pct,
    SUM(total_revenue) OVER (ORDER BY order_month) AS running_total
FROM monthly
ORDER BY order_month;


-- 1b. Revenue by product category (Top 15) with RANK
WITH category_sales AS (
    SELECT
        COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS order_count,
        ROUND(AVG(oi.price), 2) AS avg_order_value
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    category,
    total_revenue,
    order_count,
    avg_order_value,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    ROUND(total_revenue / SUM(total_revenue) OVER () * 100, 1) AS pct_of_total
FROM category_sales
ORDER BY total_revenue DESC
LIMIT 15;


-- 1c. Revenue by customer state with per-customer comparison
SELECT
    c.customer_state AS state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
    ROUND(SUM(oi.price + oi.freight_value) / COUNT(DISTINCT c.customer_unique_id), 2) AS revenue_per_customer
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 10;
