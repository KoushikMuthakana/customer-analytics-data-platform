from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "warehouse"
    / "customer_analytics.duckdb"
)


@st.cache_resource
def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)


def query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    return conn.execute(sql).df()