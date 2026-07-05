# dbt Transformation Architecture

## Overview

The dbt layer transforms raw CDC data from the Bronze layer into clean, analytics-ready models using a layered architecture.

The transformation follows three logical layers:

- **Staging** – Reconstruct the latest business state from CDC events
- **Intermediate** – Normalize nested business entities
- **Marts** – Build business-ready analytical models

---

# Source Data Characteristics

## Profiles

The `profiles` dataset represents customers enrolled in the loyalty platform. It primarily contains customer information used for loyalty management, campaign targeting, and personalization rather than transactional activity.


### Business Observations

- Profiles represent customer master data.
- Customers may exist without shopping sessions.
- Shopping sessions may reference customer IDs that are not present in the provided profiles dataset.
- The sample data is not a complete relational extract, which explains the expected reconciliation differences between profile-based and session-based analytics.

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

## CDC Characteristics

Both source datasets contain **Change Data Capture (CDC)** events.

The Bronze layer preserves every event exactly as received.

The Staging layer reconstructs the latest business state by selecting the latest event for each business entity.

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
```

Each state transition generates a new CDC event while retaining the same business identifier.

---

# Materialization Strategy

All dbt models are materialized as **tables**.

| Layer | Materialization | Purpose |
|--------|-----------------|---------|
| Staging | Table | Reconstruct latest business state |
| Intermediate | Table | Normalize nested business entities |
| Marts | Table | Build analyst-ready reporting models |

Incremental processing is handled by the Python ingestion layer, which incrementally and idempotently loads CDC events into the Bronze layer.

The dbt layer rebuilds deterministic analytical tables from Bronze, keeping the transformation pipeline simple and maintainable.

---

# Modeling Decisions

| Observation | Decision |
|-------------|----------|
| Bronze stores CDC history | Reconstruct latest state in Staging |
| Shopping sessions contain nested products | Build `int_session_cart_items` |
| Discounts stored as JSON | Build `int_session_discounts` |
| Active offers stored as arrays | Build `int_customer_active_offers` |
| Anonymous shopping sessions exist | Model `customer_id` as nullable |
| Profiles and Sessions are not fully relational | Customer marts remain profile-centric and document reconciliation differences |

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

Therefore, `customer_id` is modeled as an optional attribute in the staging layer.

---

## Intermediate

| Model | Purpose |
|--------|---------|
| `int_session_cart_items` | Flatten purchased products |
| `int_session_discounts` | Flatten applied discounts |
| `int_customer_active_offers` | Flatten active customer offers |

---

## Marts

| Model | Purpose |
|--------|---------|
| `customer_summary` | Customer behavior and loyalty metrics |
| `customer_product_summary` | Customer purchasing behavior by product |
| `product_sales_summary` | Product sales performance |
| `channel_sales_summary` | Channel performance comparison |
| `discount_summary` | Discount and promotion performance |

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
         dbt Marts (Analytics Layer)
          ├── customer_summary
          ├── customer_product_summary
          ├── product_sales_summary
          ├── channel_sales_summary
          └── discount_summary
```

---

# Key Takeaways

- Bronze preserves every CDC event exactly as received.
- Python performs incremental and idempotent ingestion into Bronze.
- Staging reconstructs the latest business state from CDC events.
- Shopping sessions may exist without an associated customer profile.
- Intermediate models normalize nested business entities into reusable datasets.
- Gold marts provide business-ready analytical models for reporting and dashboards.
- The provided sample datasets are not fully relational, and reconciliation differences are documented where applicable.
- All dbt models are materialized as physical tables to keep the transformation layer deterministic, simple, and easy to maintain.