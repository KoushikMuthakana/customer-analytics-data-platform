import streamlit as st
import plotly.express as px

from database import query
from filters import get_filters

st.set_page_config(
    page_title="Product Analytics",
    layout="wide",
)

st.title("Product Analytics")

year, status = get_filters()


metrics = query(f"""
SELECT
    COUNT(*) AS products,
    SUM(total_quantity_sold) AS quantity_sold,
    SUM(total_revenue) AS revenue,
    SUM(unique_customers) AS customers
FROM analytics.product_sales_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
""").iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Products", f"{int(metrics['products']):,}")
c2.metric("Quantity Sold", f"{int(metrics['quantity_sold']):,}")
c3.metric("Revenue", f"${metrics['revenue']:,.2f}")
c4.metric("Customers", f"{int(metrics['customers']):,}")

st.divider()

# ----------------------------------------------------
# Charts
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Top 10 Products by Revenue")

    df = query(f"""
    SELECT
        product_name,
        total_revenue
    FROM analytics.product_sales_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY total_revenue DESC
    LIMIT 10
    """)

    fig = px.bar(
        df,
        x="total_revenue",
        y="product_name",
        orientation="h",
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    st.plotly_chart(fig, width="stretch")

with right:

    st.subheader("Revenue by Category")

    df = query(f"""
    SELECT
        category,
        SUM(total_revenue) AS revenue
    FROM analytics.product_sales_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    GROUP BY category
    ORDER BY revenue DESC
    LIMIT 10
    """)

    fig = px.bar(
        df,
        x="category",
        y="revenue",
    )

    st.plotly_chart(fig, width="stretch")

st.divider()


st.subheader("Product Sales Summary")

df = query(f"""
SELECT *
FROM analytics.product_sales_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
ORDER BY total_revenue DESC
LIMIT 100
""")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)