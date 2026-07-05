import streamlit as st
import plotly.express as px

from database import query
from filters import get_filters

st.set_page_config(
    page_title="Discount Analytics",
    layout="wide",
)

st.title("Discount Analytics")

year, status = get_filters()


metrics = query(f"""
SELECT
    COUNT(*) AS discounts,
    SUM(total_discount_applications) AS applications,
    SUM(total_discount_amount) AS amount,
    SUM(unique_customers) AS customers
FROM analytics.discount_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
""").iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Discounts", f"{int(metrics['discounts']):,}")
c2.metric("Applications", f"{int(metrics['applications']):,}")
c3.metric("Discount Amount", f"${metrics['amount']:,.2f}")
c4.metric("Customers", f"{int(metrics['customers']):,}")

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("Top Discounts by Usage")

    df = query(f"""
    SELECT
        discount_name,
        total_discount_applications
    FROM analytics.discount_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY total_discount_applications DESC
    LIMIT 10
    """)

    fig = px.bar(
        df,
        x="total_discount_applications",
        y="discount_name",
        orientation="h",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, width="stretch")

with right:

    st.subheader("Top Discounts by Amount")

    df = query(f"""
    SELECT
        discount_name,
        total_discount_amount
    FROM analytics.discount_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY total_discount_amount DESC
    LIMIT 10
    """)

    fig = px.bar(
        df,
        x="total_discount_amount",
        y="discount_name",
        orientation="h",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("Discount Summary")

df = query(f"""
SELECT *
FROM analytics.discount_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
ORDER BY total_discount_amount DESC
LIMIT 100
""")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)