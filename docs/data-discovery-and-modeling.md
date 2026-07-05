# CDC Strategy

Both source datasets contain Change Data Capture (CDC) events.

The Bronze layer preserves every CDC event exactly as received without applying any business logic.

The dbt layer reconstructs the latest business state by selecting the most recent event for each business entity.

---

# Materialization Strategy

All dbt models are materialized as **tables**.

| Layer | Materialization | Purpose |
|--------|-----------------|---------|
| Staging | Table | Reconstruct the latest business state from Bronze |
| Intermediate | Table | Normalize nested business entities |
| Marts | Table | Build analyst-ready analytical tables |

Incremental processing is handled by the Python ingestion layer, which incrementally and idempotently loads CDC events into the Bronze layer.

The dbt transformation layer rebuilds analytical tables from Bronze, keeping the implementation simple, deterministic, and easy to maintain.

---

# Final dbt Models

## Staging

| Model | Purpose |
|--------|---------|
| `stg_profiles` | Latest customer profile |
| `stg_customer_sessions` | Latest shopping session |

### Customer Association

A shopping session is not always associated with a customer profile.

Approximately **108K** session records in the sample dataset contain a null `profileid`, indicating that anonymous or unlinked shopping sessions are supported by the source system.

Therefore, `customer_id` is modeled as an optional attribute in the staging layer.

---

## Intermediate

| Model | Purpose |
|--------|---------|
| `int_cart_items` | Flatten purchased products |
| `int_discounts` | Flatten applied discounts |
| `int_customer_offers` | Flatten active customer offers |

---

## Marts

| Model | Purpose |
|--------|---------|
| `customer_summary` | Customer behaviour and loyalty metrics |
| `product_sales_summary` | Product sales performance |
| `channel_sales_summary` | Online vs Store sales comparison |
| `discount_summary` | Discount and promotion performance |

---

# Final Architecture

```text
                    Raw JSON
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
      dbt Intermediate (Normalized)
          ├── int_cart_items
          ├── int_discounts
          └── int_customer_offers
                        │
                        ▼
          dbt Marts (Analytics)
          ├── customer_summary
          ├── product_sales_summary
          ├── channel_sales_summary
          └── discount_summary
```

---

# Key Takeaways

- Bronze preserves every CDC event exactly as received.
- The Python ingestion layer performs incremental and idempotent loading into Bronze.
- Staging reconstructs the latest business state for each business entity.
- Shopping sessions may exist without an associated customer profile, so `customer_id` is modeled as optional.
- Intermediate models normalize nested business entities into reusable analytical tables.
- Marts provide analyst-ready aggregated tables for reporting and downstream analysis.
- All dbt models are materialized as physical tables to keep the transformation layer simple, deterministic, and easy to maintain.