# dbt Transformation Architecture

## Overview

The dbt layer transforms raw Change Data Capture (CDC) data from the Bronze layer into clean, analytics-ready models using a layered architecture.

The transformation follows three logical layers:

- **Staging** – Reconstruct the latest business state from CDC events
- **Intermediate** – Normalize nested business entities
- **Marts** – Build business-ready analytical models

This layered design separates technical processing from business logic while producing reusable analytical datasets.

---

# Source Data Characteristics

## Profiles

The `profiles` dataset represents customers enrolled in the loyalty platform. It primarily contains customer information used for loyalty management, campaign targeting, and personalization rather than transactional activity.

### Business Observations

- Profiles represent customer master data.
- Customers may exist without shopping sessions.
- Shopping sessions may reference customer IDs that are not present in the provided profiles dataset.
- The provided sample data is not a complete relational extract, which explains the expected reconciliation differences between profile-based and session-based analytics.

### Customer Attributes

The following business attributes are extracted from the profile JSON:

- Loyalty Tier
- Preferred Store
- Active Loyalty Offers
- Military Membership
- Birth Month
- Birth Day
- Points to Next Reward

These attributes are modeled in the customer analytical mart for customer segmentation and reporting.

---

## Customer Sessions

The `customer_sessions` dataset captures shopping activity.

Each record represents a business event generated during the lifecycle of a shopping session.

Important business attributes include:

- Customer
- Shopping Channel
- Order Status
- Cart Items
- Discounts
- Business timestamps (`created_at`, `ordered_at`, `updated_at`)

According to the case study:

- **`order_status = Closed`** represents a completed purchase.

The analytical layer preserves all order statuses while allowing sales reporting to focus on completed purchases.

---

# CDC Characteristics

Both source datasets contain **Change Data Capture (CDC)** events.

The Bronze layer preserves every event exactly as received.

The Staging layer reconstructs the latest business state by selecting the latest event for each business entity using the CDC timestamp.

Example lifecycle:

```text
Session Created
      ↓
Items Added
      ↓
Discount Applied
      ↓
Cart Updated
      ↓
Checkout
      ↓
Closed
```

Each state transition generates another CDC event while retaining the same business identifier.

---

# Materialization Strategy

All dbt models are materialized as **tables**.

| Layer | Materialization | Purpose |
|--------|-----------------|---------|
| Staging | Table | Reconstruct the latest business state |
| Intermediate | Table | Normalize reusable business entities |
| Marts | Table | Build analyst-ready reporting models |

Incremental processing is handled by the Python ingestion layer, which incrementally and idempotently loads CDC events into Bronze.

The dbt layer rebuilds deterministic analytical tables from Bronze, keeping the transformation pipeline simple, maintainable, and reproducible.

---

# Modeling Decisions

| Observation | Decision |
|-------------|----------|
| Bronze stores CDC history | Reconstruct latest state in Staging |
| Business timestamps are required for reporting | Preserve business timestamps through Staging and Intermediate |
| Shopping sessions contain nested products | Build `int_session_cart_items` |
| Discounts are stored as JSON | Build `int_session_discounts` |
| Active offers are stored as arrays | Build `int_customer_active_offers` |
| Anonymous shopping sessions exist | Model `customer_id` as nullable |
| Profiles and Sessions are not fully relational | Customer marts remain profile-centric and document reconciliation differences |
| Case study requires 2024 reporting | Derive `order_year` in Gold marts |
| Completed purchases are identified by `order_status = Closed` | Preserve `order_status` for analytical filtering and operational reporting |

---

# Final dbt Models

## Staging

| Model | Purpose |
|--------|---------|
| `stg_profiles` | Latest customer profile |
| `stg_customer_sessions` | Latest shopping session |

### Customer Association

Shopping sessions are not always associated with a customer profile.

Approximately **108K** shopping sessions contain a null `customer_id`, representing anonymous or guest shopping sessions.

Therefore, `customer_id` is modeled as an optional attribute.

---

## Intermediate

The Intermediate layer normalizes nested business entities into reusable analytical datasets while preserving business timestamps.

| Model | Purpose |
|--------|---------|
| `int_session_cart_items` | One row per purchased product |
| `int_session_discounts` | One row per applied discount |
| `int_customer_active_offers` | One row per active customer offer |

---

## Marts

The Gold layer derives reporting dimensions and builds analyst-ready datasets.

| Model | Purpose |
|--------|---------|
| `customer_summary` | Customer behavior and loyalty metrics by year and order status |
| `customer_product_summary` | Customer purchasing behavior by product, year, and order status |
| `product_sales_summary` | Product sales performance by year and order status |
| `channel_sales_summary` | Sales performance by channel, year, and order status |
| `discount_summary` | Discount and promotion performance by year and order status |

---

# Reporting Dimensions

The Gold layer derives business reporting dimensions from business timestamps.

| Dimension | Purpose |
|----------|---------|
| `order_year` | Supports year-based reporting, including the 2024 case study requirement |
| `order_status` | Enables analysis of completed and non-completed shopping sessions |

The Streamlit dashboard defaults to:

- **Year = 2024**
- **Order Status = Closed**

while allowing analysts to explore additional years and shopping session states.

---

# Final Architecture

```text
                    Raw NDJSON
                        │
                        ▼
              Python Ingestion
        (Incremental & Idempotent)
                        │
                        ▼
                  Bronze (Raw CDC)
                        │
                        ▼
      dbt Staging (Latest Business State)
          ├── stg_profiles
          └── stg_customer_sessions
                        │
                        ▼
     dbt Intermediate (Normalized Entities)
          ├── int_session_cart_items
          ├── int_session_discounts
          └── int_customer_active_offers
                        │
                        ▼
        dbt Gold (Analytical Marts)
          ├── customer_summary
          ├── customer_product_summary
          ├── product_sales_summary
          ├── channel_sales_summary
          └── discount_summary
                        │
                        ▼
      Streamlit Dashboard / BI Tools
```

---

# Key Takeaways

- Bronze preserves every CDC event exactly as received.
- Python performs incremental and idempotent ingestion into Bronze.
- Staging reconstructs the latest business state from CDC events.
- Intermediate models normalize nested business entities into reusable analytical datasets.
- Business timestamps are preserved through the transformation pipeline and reporting dimensions are derived in the Gold layer.
- Shopping sessions may exist without an associated customer profile.
- The provided sample datasets are not fully relational, and expected reconciliation differences are documented.
- The analytical layer supports both the **2024 sales reporting requirement** and broader operational reporting by preserving `order_status`.
- All dbt models are materialized as physical tables, resulting in a deterministic, simple, and maintainable transformation pipeline.
