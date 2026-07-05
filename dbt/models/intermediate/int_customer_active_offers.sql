

WITH customers AS (

    SELECT *
    FROM {{ ref('stg_profiles') }}
    LIMIT 10  --TODO REMOVE LIMIT 
),

customer_offers AS (

    SELECT
        p.customer_id,
        item.value AS offer
    FROM customers AS p
    CROSS JOIN LATERAL json_each(p.active_lta_offers) AS item

)

SELECT

    customer_id,

    offer ->> '$' AS active_offer

FROM customer_offers