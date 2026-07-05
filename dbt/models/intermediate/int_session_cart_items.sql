WITH sessions AS (

    SELECT *
    FROM {{ ref('stg_customer_sessions') }}
    WHERE cartitems IS NOT NULL
),

cart_items AS (
    SELECT
        s.session_id,
        s.customer_id,
        item.value AS cart_item,
        s.ordered_at,
        s.created_at,
        s.updated_at,
        s.order_status
    FROM sessions AS s
    CROSS JOIN LATERAL json_each(s.cartitems) AS item -- Explodes the into multiple rows based on orders list
)

SELECT
    session_id,
    customer_id,
    cart_item ->> '$.sku' AS sku,
    cart_item ->> '$.attributes.ProductName' AS product_name,
    cart_item ->> '$.attributes.BrandName' AS brand_name,
    cart_item ->> '$.attributes.Category' AS category,
    cart_item ->> '$.attributes.Department' AS department,
    cart_item ->> '$.attributes.ProductType' AS product_type,
    cart_item ->> '$.attributes.CountryState' AS country_state,
    updated_at,
    ordered_at,
    created_at,
    TRY_CAST(
        cart_item ->> '$.quantity'
        AS INTEGER
    ) AS quantity,
    TRY_CAST(
        cart_item ->> '$.remainingQuantity'
        AS INTEGER
    ) AS remaining_quantity,
    TRY_CAST(
        cart_item ->> '$.returnedQuantity'
        AS INTEGER
    ) AS returned_quantity,
    TRY_CAST(
        cart_item ->> '$.price'
        AS DOUBLE
    ) AS unit_price,
    TRY_CAST(
        cart_item ->> '$.position'
        AS INTEGER
    ) AS line_position,
    order_status

FROM cart_items