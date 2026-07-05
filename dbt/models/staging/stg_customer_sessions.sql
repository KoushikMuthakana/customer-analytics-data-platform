WITH latest_sessions AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY __ts_ms DESC
        ) AS rn
    FROM {{ source('bronze', 'customer_sessions') }}

)

SELECT

    id AS session_id,

    profileid AS customer_id,

    __ts_ms AS updated_at,

    CASE
        WHEN __op = 'd' THEN FALSE
        ELSE TRUE
    END AS is_active,

    attributes ->> '$.Channel' AS channel,

    attributes ->> '$.OrderSource' AS order_source,

    attributes ->> '$.OrderType' AS order_type,

    TRY_CAST(
        attributes ->> '$.RewardTotal'
        AS DOUBLE
    ) AS reward_total,

    TRY_CAST(
        attributes ->> '$.availableRewardAmt'
        AS DOUBLE
    ) AS available_reward_amount,

    TRY_CAST(
        attributes ->> '$.EmployeeDiscount'
        AS DOUBLE
    ) AS employee_discount,

    attributes ->> '$.ShippingMethod'
        AS shipping_method,

    cartitems,
    discounts,
    additional_costs

FROM latest_sessions

WHERE rn = 1