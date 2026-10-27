"""Streamlit dashboard (prototype, dummy data only).

Run: streamlit run dashboard/app.py
Features: business indicators, channel/product filters,
and a file-upload path to replace the dummy CSV with a new file.
Uploaded files are treated as user-supplied data for the session;
they are never claimed to be real UMKM data unless the user confirms
that themselves in the final version.

Default data: the Nike dummy dataset in data/nike_dummy/
(nike_sales_dummy.csv joined to nike_products_dummy.csv for product
names). The old 600-row dummy_inventory_sales.csv stays in data/ as
an archive only and is no longer read here. Low-stock counts come
from the products file (stock_dummy <= 5, product level), not from
sales rows, because the Nike sales file has no stock column.
"""
import os

import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "nike_dummy",
)
DEFAULT_SALES = os.path.join(DATA_DIR, "nike_sales_dummy.csv")
DEFAULT_PRODUCTS = os.path.join(DATA_DIR, "nike_products_dummy.csv")

# Old-schema column names accepted from uploaded files, mapped to the
# Nike schema so an old-format upload does not crash the dashboard.
OLD_TO_NEW_COLUMNS = {
    "channel_dummy": "channel",
    "product_name_dummy": "product_name",
}


def load_products(path):
    products = pd.read_csv(path)
    return products[["product_id", "product_name", "stock_dummy"]]


def normalize_sales(sales, products):
    """Return sales with product_name and revenue_dummy_idr columns."""
    df = sales.copy()
    df = df.rename(columns=OLD_TO_NEW_COLUMNS)
    if "product_name" not in df.columns and "product_id" in df.columns:
        df = df.merge(products, on="product_id", how="left")
    if "product_name" not in df.columns and "product_id" in df.columns:
        df["product_name"] = df["product_id"]
    if (
        "revenue_dummy_idr" not in df.columns
        and "units_sold_dummy" in df.columns
        and "price_dummy_idr" in df.columns
    ):
        df["revenue_dummy_idr"] = (
            df["units_sold_dummy"] * df["price_dummy_idr"]
        )
    return df


st.set_page_config(page_title="Authenkixx Prototype Dashboard", layout="wide")
st.title("Authenkixx Prototype Dashboard")
st.warning(
    "Prototype only. The default dataset is DUMMY data "
    "(see data/nike_dummy/nike_data_dictionary.md). "
    "Do not use these numbers for real business decisions."
)

products = load_products(DEFAULT_PRODUCTS)

uploaded = st.file_uploader(
    "Upload a CSV with the same columns as nike_sales_dummy.csv",
    type=["csv"],
)
if uploaded is not None:
    sales = pd.read_csv(uploaded, parse_dates=["date_dummy"])
    st.info("Showing uploaded file (session only, not saved as UMKM data).")
else:
    sales = pd.read_csv(DEFAULT_SALES, parse_dates=["date_dummy"])

df = normalize_sales(sales, products)

channels = st.multiselect(
    "Filter channel", sorted(df["channel"].unique()),
    default=sorted(df["channel"].unique()),
)
product_names = st.multiselect(
    "Filter product", sorted(df["product_name"].unique()),
    default=sorted(df["product_name"].unique()),
)
filtered = df[df["channel"].isin(channels) & df["product_name"].isin(product_names)]

col1, col2, col3 = st.columns(3)
col1.metric("Total dummy units", int(filtered["units_sold_dummy"].sum()))
col2.metric(
    "Total dummy revenue (IDR)",
    int(filtered["revenue_dummy_idr"].sum()),
)
selected_products = products[products["product_name"].isin(product_names)]
col3.metric(
    "Low/out-of-stock products (dummy)",
    int((selected_products["stock_dummy"] <= 5).sum()),
)
st.caption(
    "Low/out-of-stock counts products, not sales rows: stock comes from "
    "nike_products_dummy.csv, because the Nike sales file has no stock column."
)

st.subheader("Dummy units by channel")
st.bar_chart(filtered.groupby("channel")["units_sold_dummy"].sum())

st.subheader("Dummy units by product")
st.bar_chart(filtered.groupby("product_name")["units_sold_dummy"].sum())

st.subheader("Daily dummy units")
daily = filtered.groupby("date_dummy")["units_sold_dummy"].sum()
st.line_chart(daily)

st.subheader("Filtered data (dummy)")
st.dataframe(filtered.head(100))
