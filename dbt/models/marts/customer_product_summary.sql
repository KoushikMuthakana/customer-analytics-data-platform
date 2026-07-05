SELECT

    customer_id,

    sku,

    product_name,

    brand_name,

    category,

    department,

    product_type,

    country_state,

    COUNT(DISTINCT session_id) AS total_sessions,

    SUM(quantity) AS total_quantity,

    SUM(quantity * unit_price) AS total_spent

FROM {{ ref('int_session_cart_items') }}

WHERE customer_id IS NOT NULL

GROUP BY

    customer_id,

    sku,

    product_name,

    brand_name,

    category,

    department,

    product_type,

    country_state