"""Data wrangling + business analysis for dummy inventory/sales data.

Business questions (dummy data only):
  Q1. Which channel sells the most dummy units?
  Q2. Which dummy products sell the most, and which run low on stock?
  Q3. On which dummy days does stock run lowest?
Outputs: analysis/outputs/business_summary.json + printed findings.
No leakage concern here: this is descriptive analysis, not modelling.
"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "dummy_inventory_sales.csv")
OUT = os.path.join(BASE, "outputs", "business_summary.json")


def main():
    df = pd.read_csv(DATA, parse_dates=["date_dummy"])
    # Wrangling: types, no missing values expected, derived revenue column.
    assert df.isna().sum().sum() == 0, "Unexpected missing values in dummy data"
    df["revenue_dummy_idr"] = df["units_sold_dummy"] * df["price_dummy_idr"]
    df["low_stock_dummy"] = df["stock_end_dummy"] <= 5

    by_channel = df.groupby("channel_dummy")["units_sold_dummy"].sum().sort_values(ascending=False)
    by_product = df.groupby("product_name_dummy")["units_sold_dummy"].sum().sort_values(ascending=False)
    low_stock_days = int(df["low_stock_dummy"].sum())
    total_units = int(df["units_sold_dummy"].sum())
    total_revenue = int(df["revenue_dummy_idr"].sum())
    final_stock = df.sort_values("date_dummy").groupby("product_code")["stock_end_dummy"].last()

    summary = {
        "data_label": "dummy",
        "rows": int(len(df)),
        "date_range_dummy": [str(df["date_dummy"].min().date()), str(df["date_dummy"].max().date())],
        "total_units_sold_dummy": total_units,
        "total_revenue_dummy_idr": total_revenue,
        "units_by_channel_dummy": {k: int(v) for k, v in by_channel.items()},
        "units_by_product_dummy": {k: int(v) for k, v in by_product.items()},
        "low_stock_rows_dummy": low_stock_days,
        "final_stock_dummy": {k: int(v) for k, v in final_stock.items()},
        "findings_dummy": [
            f"Channel with most dummy units: {by_channel.index[0]} ({int(by_channel.iloc[0])} units).",
            f"Product with most dummy units: {by_product.index[0]} ({int(by_product.iloc[0])} units).",
            f"Low-stock rows (stock_end <= 5): {low_stock_days} of {len(df)} rows.",
        ],
        "recommendations_dummy": [
            "Restock the dummy products that end the period at low stock before they hit zero (dummy signal only).",
            "Focus restock checks on the channel with the highest dummy units, but confirm with real UMKM data before acting.",
            "Keep one master inventory record so channel labels do not drift apart; do not add automatic sync in the prototype.",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
