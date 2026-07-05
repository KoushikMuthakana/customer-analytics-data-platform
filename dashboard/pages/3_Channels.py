import streamlit as st
import plotly.express as px

from database import query
from filters import get_filters

year, status = get_filters()

st.set_page_config(
    page_title="Channel Analytics",
    layout="wide",
)

st.title("Channel Analytics")

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

metrics = query(f"""
SELECT
    COUNT(*) AS channels,
    SUM(total_sessions) AS sessions,
    SUM(total_revenue) AS revenue,
    AVG(average_order_value) AS avg_order
FROM analytics.channel_sales_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
""").iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Channels", f"{int(metrics['channels'])}")
c2.metric("Sessions", f"{int(metrics['sessions']):,}")
c3.metric("Revenue", f"${metrics['revenue']:,.2f}")
c4.metric("Avg Order Value", f"${metrics['avg_order']:,.2f}")

st.divider()

# ----------------------------------------------------
# Charts
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Revenue by Channel")

    df = query(f"""
    SELECT
        channel,
        total_revenue
    FROM analytics.channel_sales_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY total_revenue DESC
    """)

    fig = px.bar(
        df,
        x="channel",
        y="total_revenue",
    )

    st.plotly_chart(fig, width="stretch")

with right:

    st.subheader("Average Order Value")

    df = query(f"""
    SELECT
        channel,
        average_order_value
    FROM analytics.channel_sales_summary
    WHERE order_year = {year}
      AND lower(order_status) = lower('{status}')
    ORDER BY average_order_value DESC
    """)

    fig = px.bar(
        df,
        x="channel",
        y="average_order_value",
    )

    st.plotly_chart(fig, width="stretch")

st.divider()

# ----------------------------------------------------
# Table
# ----------------------------------------------------

st.subheader("Channel Sales Summary")

df = query(f"""
SELECT *
FROM analytics.channel_sales_summary
WHERE order_year = {year}
  AND lower(order_status) = lower('{status}')
ORDER BY total_revenue DESC
""")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)