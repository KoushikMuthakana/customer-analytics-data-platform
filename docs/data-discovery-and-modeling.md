# dbt Transformation Architecture

## Overview

This project transforms raw Change Data Capture (CDC) JSON datasets into clean, analytics-ready models using dbt.

The objective is to reconstruct the latest business state from operational CDC events, normalize semi-structured data, and build reusable analytical models that enable analysts to answer questions such as:

- What products sell the most?
- How do online and offline sales compare?
- What impact do discounts have on sales?
- What customer purchasing patterns can be identified?

The solution follows a layered architecture:

- **Staging** – Reconstruct the latest business state from CDC events
- **Intermediate** – Normalize nested business entities
- **Marts** – Build business-ready analytical datasets

This layered approach separates technical processing from business logic while producing reusable analytical models.

---

# Understanding the Source Data

The source data consists of two JSON datasets exported from an operational system:

- `customer_sessions.json`
- `profiles.json`

Unlike a traditional relational export, both datasets are **Change Data Capture (CDC)** streams. Every insert, update, or delete on a database row generates a new event, meaning multiple versions of the same business entity may exist over time.

Therefore, the first responsibility of the transformation pipeline is reconstructing the latest business state before any analytical modeling can begin.

---

# customer_sessions.json

The `customer_sessions` dataset captures shopping activity across both online and in-store channels.

Each record represents a **shopping session**, not a completed order.

A session evolves throughout its lifecycle as customers interact with it, generating multiple CDC events.

Example lifecycle:

```text
OPEN
   │
   ├── Customer adds products
   ├── Customer removes products
   ├── Discounts applied
   ├── Rewards updated
   │
   ▼
CLOSED
(Purchase completed)

(optional)

▼
CANCELLED
(Session cancelled after checkout)
```

Every state transition produces another CDC event while retaining the same session identifier.

### Session Data Categories

| Category | Columns | Purpose |
|----------|---------|---------|
| **CDC metadata** | `id`, `__op`, `__deleted`, `__ts_ms` | Reconstruct the latest state of each shopping session. `id` is the primary key, while CDC metadata identifies inserts, updates, deletes, and event ordering. |
| **Session metadata** | `profileid`, `state`, `created`, `updated`, `closedat`, `firstsession`, `store_integration_id`, `total_float` | Describes the shopping session, including customer relationship, lifecycle state, timestamps, store, and transaction value. |
| **Nested business data** | `attributes`, `cartitems`, `discounts`, `additional_costs` | Semi-structured JSON objects and arrays containing business information such as channel, products, rewards, discounts, and additional costs. These require parsing and normalization. |
| **Operational metadata** | `applicationid`, `profileintegrationid`, `loyaltycards` | Operational fields primarily used for upstream systems and integrations rather than analytical reporting. |

### Key Observations

From exploring the raw session data, several modeling challenges became apparent:

- The dataset stores **CDC history**, so multiple records exist for the same session.
- Business attributes are embedded inside JSON (`attributes`).
- Products are stored as nested arrays (`cartitems`).
- Discounts are stored as JSON objects (`discounts`).
- Sessions reference customers through `profileid`.
- Shopping sessions can exist without a `customer_id`, representing anonymous or guest purchases.

These observations directly influenced the staging and intermediate models.

---

# profiles.json

The `profiles` dataset contains customer master data used for loyalty management, personalization, and campaign targeting.

Like customer sessions, profile records are emitted as CDC events whenever customer attributes change.

Each customer is uniquely identified by `id`.

Examples of customer attributes include:

- Loyalty Tier
- Preferred Store
- Active Loyalty Offers
- Military Membership
- Birth Month
- Birth Day
- Points to Next Reward

Some attributes are optional and may not appear in every event.

The dataset also contains nested arrays (`ActiveLTAOffers`) that require normalization.

### Business Observations

- Profiles represent customer master data rather than transactional activity.
- Customers may exist without shopping sessions.
- Some shopping sessions reference customer IDs that are not present in the provided profile dataset.
- The supplied datasets are not a complete relational snapshot, so reconciliation differences between sessions and profiles are expected.

---

# CDC Characteristics

Both source datasets contain **Change Data Capture (CDC)** events.

The Bronze layer preserves every event exactly as received.

The Staging layer reconstructs the latest business state by selecting the most recent event for each business entity using `__ts_ms`.

Example:

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

Every update produces another CDC event while retaining the same business identifier.

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

The structure of the raw data directly influenced the design of the dbt models.

| Observation | Modeling Decision |
|-------------|-------------------|
| Bronze stores CDC history | Reconstruct the latest business state in Staging using the latest `__ts_ms`. |
| Business timestamps are required for reporting | Preserve business timestamps throughout the pipeline. |
| Shopping sessions contain nested products | Build `int_session_cart_items`. |
| Discounts are stored as JSON objects | Build `int_session_discounts`. |
| Active loyalty offers are stored as arrays | Build `int_customer_active_offers`. |
| Business attributes are stored inside JSON | Parse JSON into typed relational columns during Staging. |
| Anonymous shopping sessions exist | Model `customer_id` as nullable. |
| Profiles and Sessions are not fully relational | Customer marts remain profile-centric while documenting reconciliation differences. |
| Reporting is focused on 2024 | Derive `order_year` in Gold models. |
| Analysts require flexible reporting | Preserve `order_status` to support both sales and operational reporting. |

---

# Final dbt Models

## Staging

The Staging layer reconstructs the latest business state while remaining close to the source schema.

| Model | Purpose |
|--------|---------|
| `stg_profiles` | Latest customer profile |
| `stg_customer_sessions` | Latest shopping session |

---

## Intermediate

The Intermediate layer normalizes nested business entities into reusable relational datasets.

| Model | Purpose |
|--------|---------|
| `int_session_cart_items` | One row per purchased product |
| `int_session_discounts` | One row per applied discount |
| `int_customer_active_offers` | One row per active customer offer |

---

## Marts

The Gold layer builds analyst-ready datasets that answer the business questions posed in the case study.

| Model | Purpose |
|--------|---------|
| `customer_summary` | Customer behavior and loyalty metrics |
| `customer_product_summary` | Customer purchasing behavior by product |
| `product_sales_summary` | Product sales performance |
| `channel_sales_summary` | Sales performance by channel |
| `discount_summary` | Discount and promotion performance |

---

# Reporting Dimensions

Business reporting dimensions are derived from business timestamps.

| Dimension | Purpose |
|-----------|---------|
| `order_year` | Supports yearly reporting, including the 2024 case study requirement |
| `order_status` | Enables both completed sales analysis and operational reporting |

The Streamlit dashboard defaults to:

- **Year = 2024**
- **Order Status = Closed**

while allowing analysts to explore other years and shopping session states.

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
- Staging reconstructs the latest business state from CDC events and converts JSON into typed relational columns.
- Intermediate models normalize nested business entities into reusable analytical datasets.
- Gold models provide business-ready reporting datasets that directly answer stakeholder questions.
- Business timestamps are preserved throughout the transformation pipeline.
- Shopping sessions may exist without an associated customer profile.
- The provided datasets are not a complete relational snapshot, and expected reconciliation differences are documented.
- The analytical layer supports both the **2024 reporting requirement** and broader operational reporting through `order_status`.
- The layered architecture keeps transformation logic modular, deterministic, and maintainable.
