"""Wrangle + business analysis for the Nike dummy dataset.

This script replaces the old 600-row analysis for the current outputs.
Input:
  data/nike_dummy/nike_products_dummy.csv
  data/nike_dummy/nike_sales_dummy.csv
Output:
  outputs/business_summary.json

Definitions (different from the old 600-row analysis, stated honestly):
- low_stock_rows_dummy = sales rows belonging to products whose
  CURRENT dummy stock is <= 5. The Nike sales file has no daily
  stock trajectory, so a per-row stock_end flag cannot be computed
  the way the old script did.
- final_stock_dummy = current dummy stock per product from the
  catalogue file, not an end-of-period stock_end from sales.
All figures are dummy, seed 42 in the generator.
"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(BASE, "data", "nike_dummy", "nike_products_dummy.csv")
SALES = os.path.join(BASE, "data", "nike_dummy", "nike_sales_dummy.csv")
OUT = os.path.join(BASE, "outputs", "business_summary.json")


def main():
    prod = pd.read_csv(PRODUCTS)
    df = pd.read_csv(SALES, parse_dates=["date_dummy"])
    assert df.isna().sum().sum() == 0, "Unexpected missing values in Nike dummy sales"
    assert prod.isna().sum().sum() == 0, "Unexpected missing values in Nike dummy products"
    df["revenue_dummy_idr"] = df["units_sold_dummy"] * df["price_dummy_idr"]

    by_channel = df.groupby("channel")["units_sold_dummy"].sum().sort_values(ascending=False)
    prod_name = dict(zip(prod["product_id"], prod["product_name"]))
    df["product_name"] = df["product_id"].map(prod_name)
    by_product = df.groupby("product_name")["units_sold_dummy"].sum().sort_values(ascending=False)
    by_category = df.merge(prod[["product_id", "category"]], on="product_id").groupby("category")["units_sold_dummy"].sum().sort_values(ascending=False)

    low_ids = set(prod.loc[prod["stock_dummy"] <= 5, "product_id"])
    low_rows = int(df["product_id"].isin(low_ids).sum())
    final_stock = {r["product_id"]: int(r["stock_dummy"]) for _, r in prod.iterrows()}

    summary = {
        "data_label": "dummy",
        "source": "data/nike_dummy/nike_products_dummy.csv and data/nike_dummy/nike_sales_dummy.csv (generator: analysis/generate_nike_dummy.py, seed 42)",
        "rows": int(len(df)),
        "date_range_dummy": [str(df["date_dummy"].min().date()), str(df["date_dummy"].max().date())],
        "total_units_sold_dummy": int(df["units_sold_dummy"].sum()),
        "total_revenue_dummy_idr": int(df["revenue_dummy_idr"].sum()),
        "units_by_channel_dummy": {k: int(v) for k, v in by_channel.items()},
        "units_by_product_dummy": {k: int(v) for k, v in by_product.items()},
        "units_by_category_dummy": {k: int(v) for k, v in by_category.items()},
        "low_stock_rows_dummy": low_rows,
        "low_stock_rows_definition_dummy": "Sales rows for products whose current dummy stock is <= 5 (the Nike sales file has no daily stock trajectory).",
        "final_stock_dummy": final_stock,
        "final_stock_definition_dummy": "Current dummy stock per product from the catalogue file, not an end-of-period stock_end from sales.",
        "findings_dummy": [
            f"Channel with most dummy units: {by_channel.index[0]} ({int(by_channel.iloc[0])} units).",
            f"Product with most dummy units: {by_product.index[0]} ({int(by_product.iloc[0])} units).",
            f"Category with most dummy units: {by_category.index[0]} ({int(by_category.iloc[0])} units).",
            f"Low-stock sales rows (products with current stock <= 5): {low_rows} of {len(df)} rows.",
        ],
        "recommendations_dummy": [
            "Restock the dummy products that are at low stock before they hit zero (dummy signal only).",
            "Focus restock checks on the channel and category with the highest dummy units, but confirm with real UMKM data before acting.",
            "Keep one master inventory record so channel labels do not drift apart; do not add automatic sync in the prototype.",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: summary[k] for k in ["rows", "total_units_sold_dummy", "total_revenue_dummy_idr", "low_stock_rows_dummy"]}, indent=2))


if __name__ == "__main__":
    main()
