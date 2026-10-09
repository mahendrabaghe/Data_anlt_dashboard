-- ============================================================
-- analysis_queries.sql
-- E-Commerce Analytics – MySQL Analytical Queries
-- Database: ecommerce_analytics
-- Table:    orders
-- ============================================================

USE ecommerce_analytics;

-- ────────────────────────────────────────────────────────────
-- 1. Total Revenue
-- ────────────────────────────────────────────────────────────
SELECT
    ROUND(SUM(sales), 2)  AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders;

-- ────────────────────────────────────────────────────────────
-- 2. Monthly Revenue & Profit
-- ────────────────────────────────────────────────────────────
SELECT
    DATE_FORMAT(order_date, '%Y-%m')  AS month,
    ROUND(SUM(sales),  2)             AS monthly_revenue,
    ROUND(SUM(profit), 2)             AS monthly_profit,
    COUNT(DISTINCT order_id)          AS order_count
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- ────────────────────────────────────────────────────────────
-- 3. Top 10 Products by Revenue
-- ────────────────────────────────────────────────────────────
SELECT
    product_id,
    product_name,
    category,
    ROUND(SUM(sales),    2) AS total_revenue,
    ROUND(SUM(profit),   2) AS total_profit,
    SUM(quantity)           AS units_sold
FROM orders
GROUP BY product_id, product_name, category
ORDER BY total_revenue DESC
LIMIT 10;

-- ────────────────────────────────────────────────────────────
-- 4. Top 10 Customers by Revenue
-- ────────────────────────────────────────────────────────────
SELECT
    customer_id,
    customer_name,
    city,
    state,
    ROUND(SUM(sales), 2)          AS total_revenue,
    COUNT(DISTINCT order_id)       AS total_orders,
    ROUND(AVG(sales), 2)           AS avg_order_value
FROM orders
GROUP BY customer_id, customer_name, city, state
ORDER BY total_revenue DESC
LIMIT 10;

-- ────────────────────────────────────────────────────────────
-- 5. Sales & Profit by Category
-- ────────────────────────────────────────────────────────────
SELECT
    category,
    ROUND(SUM(sales),  2)                               AS total_revenue,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0) * 100, 2) AS profit_margin_pct,
    SUM(quantity)                                        AS units_sold
FROM orders
GROUP BY category
ORDER BY total_revenue DESC;

-- ────────────────────────────────────────────────────────────
-- 6. Sales & Profit by Sub-Category
-- ────────────────────────────────────────────────────────────
SELECT
    category,
    sub_category,
    ROUND(SUM(sales),  2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity)          AS units_sold
FROM orders
GROUP BY category, sub_category
ORDER BY total_revenue DESC;

-- ────────────────────────────────────────────────────────────
-- 7. Revenue & Orders by State
-- ────────────────────────────────────────────────────────────
SELECT
    state,
    ROUND(SUM(sales),  2)    AS total_revenue,
    ROUND(SUM(profit), 2)    AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
GROUP BY state
ORDER BY total_revenue DESC;

-- ────────────────────────────────────────────────────────────
-- 8. Highest-Revenue Cities
-- ────────────────────────────────────────────────────────────
SELECT
    city,
    state,
    ROUND(SUM(sales),  2)    AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY city, state
ORDER BY total_revenue DESC
LIMIT 15;

-- ────────────────────────────────────────────────────────────
-- 9. Average Order Value (overall + by state)
-- ────────────────────────────────────────────────────────────
-- Overall
SELECT ROUND(AVG(order_total), 2) AS avg_order_value
FROM (
    SELECT order_id, SUM(sales) AS order_total
    FROM orders
    GROUP BY order_id
) t;

-- By state
SELECT
    state,
    ROUND(AVG(order_total), 2) AS avg_order_value
FROM (
    SELECT order_id, state, SUM(sales) AS order_total
    FROM orders
    GROUP BY order_id, state
) t
GROUP BY state
ORDER BY avg_order_value DESC;

-- ────────────────────────────────────────────────────────────
-- 10. Repeat Customers (ordered more than once)
-- ────────────────────────────────────────────────────────────
SELECT
    customer_id,
    customer_name,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(sales), 2)     AS lifetime_value
FROM orders
GROUP BY customer_id, customer_name
HAVING order_count > 1
ORDER BY order_count DESC, lifetime_value DESC
LIMIT 20;

-- ────────────────────────────────────────────────────────────
-- 11. Repeat Customer Rate
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(DISTINCT customer_id)                               AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)         AS repeat_customers,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
        / COUNT(DISTINCT customer_id) * 100, 2
    )                                                         AS repeat_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
) t;

-- ────────────────────────────────────────────────────────────
-- 12. Cancelled Orders — Revenue Lost
-- ────────────────────────────────────────────────────────────
SELECT
    order_status,
    COUNT(DISTINCT order_id)   AS order_count,
    ROUND(SUM(sales), 2)       AS revenue,
    ROUND(COUNT(DISTINCT order_id) / (
        SELECT COUNT(DISTINCT order_id) FROM orders
    ) * 100, 2) AS pct_of_total
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

-- ────────────────────────────────────────────────────────────
-- 13. Most Profitable Products (with margin)
-- ────────────────────────────────────────────────────────────
SELECT
    product_name,
    category,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(SUM(sales),  2)                               AS total_revenue,
    ROUND(SUM(profit) / NULLIF(SUM(sales),0) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY product_name, category
ORDER BY total_profit DESC
LIMIT 15;

-- ────────────────────────────────────────────────────────────
-- 14. Impact of Discount on Profit Margin
-- ────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN discount = 0           THEN '0% (No Discount)'
        WHEN discount < 0.10        THEN '1-9%'
        WHEN discount < 0.20        THEN '10-19%'
        WHEN discount < 0.30        THEN '20-29%'
        ELSE '30%+'
    END AS discount_band,
    COUNT(DISTINCT order_id)                            AS orders,
    ROUND(AVG(profit_margin), 2)                        AS avg_profit_margin,
    ROUND(SUM(sales),  2)                               AS total_revenue,
    ROUND(SUM(profit), 2)                               AS total_profit
FROM orders
GROUP BY discount_band
ORDER BY avg_profit_margin DESC;

-- ────────────────────────────────────────────────────────────
-- 15. Monthly Revenue YoY Comparison (window function)
-- ────────────────────────────────────────────────────────────
WITH monthly_rev AS (
    SELECT
        YEAR(order_date)                       AS yr,
        MONTH(order_date)                      AS mo,
        ROUND(SUM(sales), 2)                   AS revenue
    FROM orders
    GROUP BY yr, mo
)
SELECT
    yr,
    mo,
    revenue,
    LAG(revenue) OVER (PARTITION BY mo ORDER BY yr) AS prev_year_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY mo ORDER BY yr))
        / NULLIF(LAG(revenue) OVER (PARTITION BY mo ORDER BY yr), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM monthly_rev
ORDER BY yr, mo;

-- ────────────────────────────────────────────────────────────
-- 16. Running Total Revenue by Month (window function)
-- ────────────────────────────────────────────────────────────
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    ROUND(SUM(sales), 2)             AS monthly_revenue,
    ROUND(SUM(SUM(sales)) OVER (
        ORDER BY DATE_FORMAT(order_date, '%Y-%m')
    ), 2)                            AS running_total
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- ────────────────────────────────────────────────────────────
-- 17. Customer Lifetime Value — CTE
-- ────────────────────────────────────────────────────────────
WITH clv AS (
    SELECT
        customer_id,
        customer_name,
        COUNT(DISTINCT order_id)    AS orders,
        ROUND(SUM(sales), 2)        AS lifetime_value,
        MIN(order_date)             AS first_order,
        MAX(order_date)             AS last_order,
        DATEDIFF(MAX(order_date), MIN(order_date)) AS customer_lifespan_days
    FROM orders
    GROUP BY customer_id, customer_name
)
SELECT
    *,
    CASE
        WHEN lifetime_value >= 50000  THEN 'Platinum'
        WHEN lifetime_value >= 20000  THEN 'Gold'
        WHEN lifetime_value >= 5000   THEN 'Silver'
        ELSE                               'Bronze'
    END AS clv_tier
FROM clv
ORDER BY lifetime_value DESC
LIMIT 20;

-- ────────────────────────────────────────────────────────────
-- 18. Product Revenue Rank within each Category
-- ────────────────────────────────────────────────────────────
SELECT
    category,
    product_name,
    ROUND(SUM(sales), 2) AS revenue,
    RANK() OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC
    ) AS rank_in_category
FROM orders
GROUP BY category, product_name
ORDER BY category, rank_in_category;
