"""Streamlit dashboard skeleton (prototype, dummy data only).

Run: streamlit run dashboard/app.py
Features: business indicators, channel/product filters, date filter,
and a file-upload path to replace the dummy CSV with a new file.
Uploaded files are treated as user-supplied data for the session;
they are never claimed to be real UMKM data unless the user confirms
that themselves in the final version.
"""
import os

import pandas as pd
import streamlit as st

DEFAULT_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "dummy_inventory_sales.csv",
)

st.set_page_config(page_title="Authenkixx Prototype Dashboard", layout="wide")
st.title("Authenkixx Prototype Dashboard")
st.warning(
    "Prototype only. The default dataset is DUMMY data (see data_dictionary.md). "
    "Do not use these numbers for real business decisions."
)

uploaded = st.file_uploader(
    "Upload a CSV with the same columns as dummy_inventory_sales.csv",
    type=["csv"],
)
if uploaded is not None:
    df = pd.read_csv(uploaded, parse_dates=["date_dummy"])
    st.info("Showing uploaded file (session only, not saved as UMKM data).")
else:
    df = pd.read_csv(DEFAULT_DATA, parse_dates=["date_dummy"])

channels = st.multiselect(
    "Filter channel", sorted(df["channel_dummy"].unique()),
    default=sorted(df["channel_dummy"].unique()),
)
products = st.multiselect(
    "Filter product", sorted(df["product_name_dummy"].unique()),
    default=sorted(df["product_name_dummy"].unique()),
)
filtered = df[df["channel_dummy"].isin(channels) & df["product_name_dummy"].isin(products)]

col1, col2, col3 = st.columns(3)
col1.metric("Total dummy units", int(filtered["units_sold_dummy"].sum()))
col2.metric(
    "Total dummy revenue (IDR)",
    int((filtered["units_sold_dummy"] * filtered["price_dummy_idr"]).sum()),
)
col3.metric(
    "Low-stock rows (dummy)",
    int((filtered["stock_end_dummy"] <= 5).sum()),
)

st.subheader("Dummy units by channel")
st.bar_chart(filtered.groupby("channel_dummy")["units_sold_dummy"].sum())

st.subheader("Dummy units by product")
st.bar_chart(filtered.groupby("product_name_dummy")["units_sold_dummy"].sum())

st.subheader("Daily dummy units")
daily = filtered.groupby("date_dummy")["units_sold_dummy"].sum()
st.line_chart(daily)

st.subheader("Filtered data (dummy)")
st.dataframe(filtered.head(100))
