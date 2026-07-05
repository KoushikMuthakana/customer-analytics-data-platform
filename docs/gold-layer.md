# Gold Layer

## Overview

The Gold layer contains analyst-ready marts built on top of the normalized Intermediate layer.

Each mart represents a business-focused aggregation designed for reporting, dashboards, and ad-hoc analysis.

---

# Available Marts

| Mart | Grain | Purpose |
|------|-------|---------|
| `customer_summary` | One row per customer | Customer profile, loyalty, shopping activity, and spending metrics |
| `customer_product_summary` | One row per customer × product | Customer purchasing behaviour and product preferences |
| `product_sales_summary` | One row per product | Product sales performance and revenue metrics |
| `channel_sales_summary` | One row per sales channel | Sales performance across shopping channels |
| `discount_summary` | One row per discount | Discount usage and promotion effectiveness |

---

# Business Questions Supported

### Customer Analytics

- Who are the highest-value customers?
- How many shopping sessions has each customer completed?
- Which loyalty tiers generate the most revenue?
- How many active offers does each customer have?

---

### Customer Purchasing Behaviour

- Which products does each customer purchase most frequently?
- Which products generate the highest revenue per customer?
- What are the purchasing preferences of loyal customers?

---

### Product Analytics

- Which products sell the most?
- Which brands and categories generate the highest revenue?
- Which products are purchased by the most customers?

---

### Channel Analytics

- Which sales channel generates the highest revenue?
- How many customers shop through each channel?
- What is the average order value by channel?

---

### Promotion Analytics

- Which discounts are used most frequently?
- Which promotions provide the highest total discount?
- How effective are promotional campaigns?

---

# Architecture

```text
Intermediate
├── int_session_cart_items
├── int_session_discounts
└── int_customer_active_offers
        │
        ▼
Gold
├── customer_summary
├── customer_product_summary
├── product_sales_summary
├── channel_sales_summary
└── discount_summary
```

---

# Design Principles

- One mart represents one business entity or analytical subject area.
- Business metrics are pre-aggregated for fast analytical queries.
- Marts are independent and reusable across dashboards and reports.
- All marts are built from normalized Intermediate models.