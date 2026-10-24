"""Baseline model: will a product-channel week end in low stock?

Target: low_stock_next_week (stock_end <= 5 in the following week).
Features (from the PREVIOUS week only): stock at week start,
average daily units sold in the previous week, and price.
No leakage: the target week is never used as a feature, the split is
by time (first 2 weeks train, last 2 weeks test), and the scaler /
model are fitted on training data only. A LogisticRegression is used
as a simple baseline; it is not a production forecast.
"""
import json
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "dummy_inventory_sales.csv")
OUT = os.path.join(BASE, "outputs", "baseline_model.json")


def weekly_features(df):
    df = df.copy()
    df["week"] = df["date_dummy"].dt.isocalendar().week.astype(int)
    weekly = []
    grouped = df.groupby(["product_code", "channel_dummy", "week"])
    for (code, channel, week), g in grouped:
        weekly.append({
            "product_code": code,
            "channel_dummy": channel,
            "week": week,
            "stock_start": int(g["stock_start_dummy"].iloc[0]),
            "avg_daily_units": float(g["units_sold_dummy"].mean()),
            "price": int(g["price_dummy_idr"].iloc[0]),
            "stock_end": int(g["stock_end_dummy"].iloc[-1]),
        })
    w = pd.DataFrame(weekly).sort_values(["product_code", "channel_dummy", "week"])
    # Target = next week's low-stock state for the same product+channel.
    w["low_stock_next_week"] = (
        w.groupby(["product_code", "channel_dummy"])["stock_end"]
        .shift(-1)
        .le(5)
        .astype("Int64")
    )
    w = w.dropna(subset=["low_stock_next_week"])
    w["low_stock_next_week"] = w["low_stock_next_week"].astype(int)
    return w


def main():
    df = pd.read_csv(DATA, parse_dates=["date_dummy"])
    w = weekly_features(df)
    features = ["stock_start", "avg_daily_units", "price"]
    weeks = sorted(w["week"].unique())
    split_week = weeks[len(weeks) // 2]
    train = w[w["week"] < split_week]
    test = w[w["week"] >= split_week]
    model = Pipeline(
        [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))]
    )
    model.fit(train[features], train["low_stock_next_week"])
    pred = model.predict(test[features])
    result = {
        "data_label": "dummy",
        "features": features,
        "target": "low_stock_next_week (stock_end <= 5 in following week)",
        "split": f"time split: train weeks < {split_week}, test weeks >= {split_week} (no leakage: features from previous week only, scaler fitted on train only)",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_positive_rate": round(float(test["low_stock_next_week"].mean()), 4) if len(test) else None,
        "accuracy": round(float(accuracy_score(test["low_stock_next_week"], pred)), 4),
        "macro_f1": round(float(f1_score(test["low_stock_next_week"], pred, average="macro", zero_division=0)), 4),
        "limitation": "Dummy data only, tiny weekly sample, and stock in the generator is shared across channels, so this baseline is a pipeline demo, not a forecast to act on.",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
