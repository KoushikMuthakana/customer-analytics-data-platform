import streamlit as st
import plotly.express as px

from database import query

from filters import get_filters

year, status = get_filters()

st.set_page_config(
    page_title="Customer Analytics",
    layout="wide",
)

st.title("Customer Analytics")


metrics = query(f"""
SELECT
    COUNT(*) AS customers,
    SUM(total_sessions) AS sessions,
    SUM(total_spent) AS revenue,
    AVG(total_spent) AS avg_spend
FROM analytics.customer_summary
WHERE order_year = {year}
AND lower(order_status) = lower('{status}')
""").iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Customers", f"{int(metrics['customers']):,}")
c2.metric("Sessions", f"{int(metrics['sessions']):,}")
c3.metric("Revenue", f"${metrics['revenue']:,.2f}")
c4.metric("Average Spend", f"${metrics['avg_spend']:,.2f}")

st.divider()


left, right = st.columns(2)

with left:

    st.subheader("Customers by Loyalty Tier")

    df = query(f"""
    SELECT
        loyalty_tier,
        COUNT(*) AS customers
    FROM analytics.customer_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    GROUP BY loyalty_tier
    ORDER BY customers DESC
    """)

    fig = px.pie(
        df,
        names="loyalty_tier",
        values="customers",
    )

    st.plotly_chart(fig, width="stretch")

with right:

    st.subheader("Top 10 Customers by Spend")

    df = query(f"""
    SELECT
        customer_id,
        total_spent
    FROM analytics.customer_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY total_spent DESC
    LIMIT 10
    """)

    fig = px.bar(
        df,
        x="total_spent",
        y="customer_id",
        orientation="h",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("Customer Summary")

df = query(f"""
SELECT *
FROM analytics.customer_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
ORDER BY total_spent DESC
LIMIT 100
""")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)