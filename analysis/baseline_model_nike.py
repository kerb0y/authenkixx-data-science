"""Baseline model for the Nike dummy dataset: is a product low on stock?

Target: low_stock (current dummy stock <= 5), at product level.
Features: dummy price, total dummy units sold over 180 days, and
dummy units sold in the last 30 days. This is a NEW baseline, not
the old weekly low_stock_next_week model: the Nike sales file has
no daily stock trajectory, so a next-week stock target cannot be
computed honestly from it. Split is stratified 80/20, seed 42,
scaler fitted on training data only. LogisticRegression is a
simple baseline; it is not a production forecast.
"""
import json
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(BASE, "data", "nike_dummy", "nike_products_dummy.csv")
SALES = os.path.join(BASE, "data", "nike_dummy", "nike_sales_dummy.csv")
OUT = os.path.join(BASE, "outputs", "baseline_model.json")


def main():
    prod = pd.read_csv(PRODUCTS)
    df = pd.read_csv(SALES, parse_dates=["date_dummy"])
    total = df.groupby("product_id")["units_sold_dummy"].sum().rename("total_units")
    last_date = df["date_dummy"].max()
    recent = df[df["date_dummy"] > last_date - pd.Timedelta(days=30)].groupby("product_id")["units_sold_dummy"].sum().rename("recent_30d_units")
    feat = prod.set_index("product_id").join(total).join(recent)
    feat["low_stock"] = (feat["stock_dummy"] <= 5).astype(int)
    features = ["price_dummy_idr", "total_units", "recent_30d_units"]
    X_train, X_test, y_train, y_test = train_test_split(
        feat[features], feat["low_stock"], test_size=0.2, random_state=42, stratify=feat["low_stock"]
    )
    model = Pipeline(
        [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))]
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    result = {
        "data_label": "dummy",
        "features": features,
        "target": "low_stock (current dummy stock <= 5, product level)",
        "split": "stratified 80/20 split, random_state=42 (scaler fitted on train only); product-level snapshot, not a time-series forecast",
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "test_positive_rate": round(float(y_test.mean()), 4) if len(y_test) else None,
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "macro_f1": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
        "limitation": "Dummy data only, 120 products, product-level snapshot with no daily stock trajectory, so this baseline is a pipeline demo, not a forecast to act on. It is not comparable to the old weekly low_stock_next_week baseline.",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
