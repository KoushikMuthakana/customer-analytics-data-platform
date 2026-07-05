SELECT

    discount_name,

    COUNT(*) AS total_discount_applications,

    COUNT(DISTINCT session_id) AS total_sessions,

    COUNT(DISTINCT customer_id) AS unique_customers,

    SUM(discount_amount) AS total_discount_amount,

    AVG(discount_amount) AS average_discount_amount

FROM {{ ref('int_session_discounts') }}

GROUP BY

    discount_name