WITH discounts AS (

    SELECT *
    FROM {{ ref('stg_customer_sessions') }}
    WHERE cartitems IS NOT NULL
),

session_discounts AS (

    SELECT
        s.session_id,
        s.customer_id,
        discount.key AS discount_name,
        discount.value AS discount_amount
    FROM discounts AS s
    CROSS JOIN LATERAL json_each(s.discounts) AS discount

)

SELECT

    session_id,

    customer_id,

    discount_name,

    TRY_CAST(
        discount_amount
        AS DOUBLE
    ) AS discount_amount

FROM session_discounts