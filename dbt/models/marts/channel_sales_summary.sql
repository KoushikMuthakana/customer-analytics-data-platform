WITH channel_metrics AS (
    SELECT
        EXTRACT(YEAR FROM s.created_at) AS order_year,
        s.channel,
        s.session_id,
        s.customer_id,
        c.quantity,
        c.unit_price,
        c.order_status
    FROM {{ ref('stg_customer_sessions') }} AS s
    INNER JOIN {{ ref('int_session_cart_items') }} AS c
        ON s.session_id = c.session_id
)

SELECT
    order_year,
    channel,
    order_status,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS total_quantity_sold,
    SUM(quantity * unit_price) AS total_revenue,
    ROUND(
        SUM(quantity * unit_price)
        / NULLIF(COUNT(DISTINCT session_id), 0),
        2
    ) AS average_order_value

FROM channel_metrics
WHERE channel IS NOT NULL
GROUP BY
    order_year,
    channel,
    order_status