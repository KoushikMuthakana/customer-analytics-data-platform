

WITH customers AS (

    SELECT *
    FROM {{ ref('stg_profiles') }}
),

customer_offers AS (

    SELECT
        p.customer_id,
        item.value AS offer,
        p.cdc_updated_at
    FROM customers AS p
    CROSS JOIN LATERAL json_each(p.active_lta_offers) AS item

)

SELECT
    DISTINCT
    customer_id,
    cdc_updated_at,
    offer ->> '$' AS active_offer

FROM customer_offers