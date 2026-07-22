-- Delivery Funnel Analysis
-- Tools: DuckDB | Dataset: Olist Brazilian E-Commerce

-- 4a. Overall delivery funnel metrics
SELECT
    COUNT(*) AS total_orders,
    COUNT(CASE WHEN order_approved_at IS NOT NULL THEN 1 END) AS approved,
    COUNT(CASE WHEN order_delivered_carrier_date IS NOT NULL THEN 1 END) AS shipped,
    COUNT(CASE WHEN order_delivered_customer_date IS NOT NULL THEN 1 END) AS delivered,

    ROUND(AVG(DATEDIFF('hour', order_purchase_timestamp, order_approved_at)), 1) AS avg_hours_to_approval,
    ROUND(AVG(DATEDIFF('hour', order_approved_at, order_delivered_carrier_date)) / 24.0, 1) AS avg_days_to_ship,
    ROUND(AVG(DATEDIFF('hour', order_delivered_carrier_date, order_delivered_customer_date)) / 24.0, 1) AS avg_days_in_transit,
    ROUND(AVG(DATEDIFF('hour', order_purchase_timestamp, order_delivered_customer_date)) / 24.0, 1) AS avg_total_days,

    ROUND(
        COUNT(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 END) * 100.0
        / NULLIF(COUNT(CASE WHEN order_delivered_customer_date IS NOT NULL THEN 1 END), 0),
        1
    ) AS pct_delivered_late
FROM orders
WHERE order_status = 'delivered';


-- 4b. Delivery performance by customer state
SELECT
    c.customer_state AS state,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(DATEDIFF('day', o.order_purchase_timestamp, o.order_delivered_customer_date)), 1) AS avg_delivery_days,
    ROUND(AVG(DATEDIFF('day', o.order_delivered_carrier_date, o.order_delivered_customer_date)), 1) AS avg_transit_days,
    ROUND(
        COUNT(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 END) * 100.0
        / COUNT(*),
        1
    ) AS pct_late
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1
HAVING COUNT(*) >= 50
ORDER BY avg_delivery_days DESC;


-- 4c. Impact of late delivery on review scores
SELECT
    CASE
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On Time'
        WHEN DATEDIFF('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) <= 7 THEN 'Late (1-7 days)'
        ELSE 'Late (7+ days)'
    END AS delivery_status,
    COUNT(*) AS order_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    ROUND(COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_negative_reviews
FROM orders o
JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1
ORDER BY avg_review_score DESC;
