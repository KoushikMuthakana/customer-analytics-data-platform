import streamlit as st

from database import query


def get_filters():

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

    year = st.sidebar.selectbox(
        "Year",
        years,
        index=years.index(default_year),
    )

    status = st.sidebar.selectbox(
        "Order Status",
        statuses,
        index=[s.lower() for s in statuses].index(default_status),
    )

    return year, status