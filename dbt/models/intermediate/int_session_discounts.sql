WITH discounts AS (

    SELECT *
    FROM {{ ref('stg_customer_sessions') }}
    WHERE discounts IS NOT NULL
),

session_discounts AS (
    SELECT
        s.session_id,
        s.customer_id,
        discount.key AS discount_name,
        discount.value AS discount_amount,
        s.ordered_at,
        s.created_at,
        s.updated_at,
        s.order_status
    FROM discounts AS s
    CROSS JOIN LATERAL json_each(s.discounts) AS discount

)

SELECT
    session_id,
    customer_id,
    ordered_at,
    created_at,
    updated_at,
    discount_name,
    order_status,
    TRY_CAST(
        discount_amount
        AS DOUBLE
    ) AS discount_amount

FROM session_discounts