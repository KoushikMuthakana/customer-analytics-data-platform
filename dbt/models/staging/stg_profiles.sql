WITH latest_profiles AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY __ts_ms DESC
        ) AS rn
    FROM {{ source('bronze', 'profiles') }}

)

SELECT

    id AS customer_id,
    __ts_ms AS updated_at,
    CASE
        WHEN __op = 'd' THEN FALSE
        ELSE TRUE
    END AS is_active,
    TRY_CAST(attributes ->> '$.BirthDay' AS INTEGER) AS birth_day,
    TRY_CAST(attributes ->> '$.BirthMonth' AS INTEGER) AS birth_month,
    attributes ->> '$.LoyaltyTier' AS loyalty_tier,
    TRY_CAST(attributes ->> '$.PreferredStoreID' AS INTEGER)
        AS preferred_store_id,
    TRY_CAST(attributes ->> '$.AndMorePointsToNextReward' AS INTEGER)
        AS points_to_next_reward,
    TRY_CAST(attributes ->> '$.MemberOfMilitary' AS BOOLEAN)
        AS member_of_military,
    attributes -> '$.ActiveLTAOffers'
    AS active_lta_offers
FROM latest_profiles
WHERE rn = 1