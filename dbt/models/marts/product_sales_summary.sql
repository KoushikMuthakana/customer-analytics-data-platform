SELECT
    EXTRACT(YEAR FROM created_at) AS order_year,
    order_status,
    sku,
    product_name,
    brand_name,
    category,
    department,
    product_type,
    country_state,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS total_quantity_sold,
    SUM(quantity * unit_price) AS total_revenue
FROM {{ ref('int_session_cart_items') }}
GROUP BY
    EXTRACT(YEAR FROM created_at),
    order_status,
    sku,
    product_name,
    brand_name,
    category,
    department,
    product_type,
    country_state