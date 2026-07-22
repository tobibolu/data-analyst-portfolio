-- Seller Performance Ranking with Tiering
-- Tools: DuckDB | Dataset: Olist Brazilian E-Commerce

-- Seller scorecard with NTILE quartiles and PERCENT_RANK percentiles
WITH seller_metrics AS (
    SELECT
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_item_price,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        COUNT(DISTINCT r.review_id) AS review_count
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2, 3
    HAVING COUNT(DISTINCT oi.order_id) >= 5  -- minimum activity threshold
)
SELECT
    seller_id,
    seller_city,
    seller_state,
    total_orders,
    total_revenue,
    avg_item_price,
    avg_review_score,
    NTILE(4) OVER (ORDER BY total_revenue DESC) AS revenue_quartile,
    ROUND(PERCENT_RANK() OVER (ORDER BY total_revenue) * 100, 1) AS revenue_percentile,
    ROUND(PERCENT_RANK() OVER (ORDER BY avg_review_score) * 100, 1) AS review_percentile,
    CASE
        WHEN NTILE(4) OVER (ORDER BY total_revenue DESC) = 1
         AND avg_review_score >= 4.0 THEN 'Gold'
        WHEN NTILE(4) OVER (ORDER BY total_revenue DESC) <= 2 THEN 'Silver'
        WHEN avg_review_score < 3.0 THEN 'At Risk'
        ELSE 'Standard'
    END AS seller_tier
FROM seller_metrics
ORDER BY total_revenue DESC;
