import streamlit as st

from database import query

st.set_page_config(
    page_title="Customer Analytics Platform",
    layout="wide",
)

# ----------------------------------------------------
# Title
# ----------------------------------------------------

st.title("Customer Analytics Platform")

st.markdown(
    """
A production-inspired analytics platform that ingests raw Change Data Capture (CDC) events,
reconstructs the latest business state, and delivers analyst-ready analytical marts
using **Python**, **DuckDB**, **dbt**, and **Streamlit**.
"""
)

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.title("Customer Analytics")

st.sidebar.markdown(
    """
### Technology Stack

- Python
- DuckDB
- dbt
- Streamlit
"""
)

st.sidebar.divider()

# ----------------------------------------------------
# Global Filters
# ----------------------------------------------------

st.sidebar.subheader("Analysis Filters")

years = query("""
SELECT DISTINCT order_year
FROM analytics.product_sales_summary
ORDER BY order_year DESC
""")["order_year"].tolist()

statuses = query("""
SELECT DISTINCT order_status
FROM analytics.product_sales_summary
ORDER BY order_status
""")["order_status"].tolist()

default_year = 2024 if 2024 in years else years[0]

default_status = (
    "closed"
    if "closed" in [s.lower() for s in statuses]
    else statuses[0]
)

selected_year = st.sidebar.selectbox(
    "Year",
    years,
    index=years.index(default_year),
)

selected_status = st.sidebar.selectbox(
    "Order Status",
    statuses,
    index=[s.lower() for s in statuses].index(default_status),
)

st.session_state["selected_year"] = selected_year
st.session_state["selected_status"] = selected_status

st.sidebar.divider()

st.sidebar.caption(
    "Use the navigation menu below to explore the analytical marts."
)

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

customer_count = query(f"""
SELECT COUNT(*) AS value
FROM analytics.customer_summary
WHERE order_year = {selected_year}
AND lower(order_status) = lower('{selected_status}')
""").iloc[0]["value"]

product_count = query(f"""
SELECT COUNT(*) AS value
FROM analytics.product_sales_summary
WHERE order_year = {selected_year}
AND lower(order_status) = lower('{selected_status}')
""").iloc[0]["value"]

channel_count = query(f"""
SELECT COUNT(*) AS value
FROM analytics.channel_sales_summary
WHERE order_year = {selected_year}
AND lower(order_status) = lower('{selected_status}')
""").iloc[0]["value"]

discount_count = query(f"""
SELECT COUNT(*) AS value
FROM analytics.discount_summary
WHERE order_year = {selected_year}
AND lower(order_status) = lower('{selected_status}')
""").iloc[0]["value"]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Customers", f"{customer_count:,}")
col2.metric("Products", f"{product_count:,}")
col3.metric("Channels", f"{channel_count:,}")
col4.metric("Discounts", f"{discount_count:,}")

st.divider()

# ----------------------------------------------------
# Architecture
# ----------------------------------------------------

st.subheader("Data Platform Architecture")

st.code(
    """
Raw NDJSON Files
        │
        ▼
Python Ingestion
(Generic • Incremental • Idempotent)
        │
        ▼
DuckDB Bronze Layer
        │
        ▼
dbt
├── Staging
├── Intermediate
└── Gold
        │
        ▼
Streamlit Dashboard
""",
    language="text",
)

# ----------------------------------------------------
# Available Analytics
# ----------------------------------------------------

st.subheader("Available Analytics")

st.markdown(
    f"""
Current dashboard filters:

- **Year:** {selected_year}
- **Order Status:** **{selected_status.title()}**

Available analytical views:

- **Customer Analytics** — Customer behaviour, loyalty, and spending
- **Customer Product Analytics** — Products purchased by each customer
- **Product Analytics** — Product sales performance
- **Channel Analytics** — Online vs Store sales comparison
- **Discount Analytics** — Promotion and discount effectiveness

Use the navigation menu on the left to explore each analytical mart.
"""
)

st.info(
    "The dashboard defaults to Year 2024 and Closed orders, matching the case study definition of completed purchases."
)