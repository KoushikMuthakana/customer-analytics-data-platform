WITH profiles AS (

    SELECT
        customer_id,
        loyalty_tier,
        preferred_store_id,
        member_of_military,
        is_active
    FROM {{ ref('stg_profiles') }}

),

session_metrics AS (

    SELECT
        customer_id,
        COUNT(*) AS total_sessions
    FROM {{ ref('stg_customer_sessions') }}
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id

),

product_metrics AS (

    SELECT
        customer_id,
        COUNT(*) AS total_products,
        SUM(quantity) AS total_quantity,
        SUM(quantity * unit_price) AS total_spent
    FROM {{ ref('int_session_cart_items') }}
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id

),

offer_metrics AS (

    SELECT
        customer_id,
        COUNT(*) AS active_offer_count
    FROM {{ ref('int_customer_active_offers') }}
    GROUP BY customer_id

)

SELECT

    p.customer_id,

    p.loyalty_tier,

    p.preferred_store_id,

    p.member_of_military,

    p.is_active,

    COALESCE(s.total_sessions, 0) AS total_sessions,

    COALESCE(pm.total_products, 0) AS total_products,

    COALESCE(pm.total_quantity, 0) AS total_quantity,

    COALESCE(pm.total_spent, 0) AS total_spent,

    COALESCE(o.active_offer_count, 0) AS active_offer_count

FROM profiles AS p

LEFT JOIN session_metrics AS s
    ON p.customer_id = s.customer_id

LEFT JOIN product_metrics AS pm
    ON p.customer_id = pm.customer_id

LEFT JOIN offer_metrics AS o
    ON p.customer_id = o.customer_id