#!/usr/bin/env python3
"""Generate a large, clearly labelled DUMMY Nike dataset for Authenkixx.

This is NOT Nike official data and NOT real Authenkixx sales data.
Model family names are well-known Nike line names used here only as
example catalogue labels for a student prototype. Every price, stock
figure, and sales figure in the output is generated with seed 42 and
must be labelled dummy wherever it is shown.

Output:
  data/nike_dummy/nike_products_dummy.csv   (120 products)
  data/nike_dummy/nike_sales_dummy.csv      (120 products x 4 channels
                                             x 180 dummy days)
  data/nike_dummy/nike_summary_dummy.json   (totals, for checking only)

Run from data-science/:
  python analysis/generate_nike_dummy.py
"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "nike_dummy"
OUT.mkdir(parents=True, exist_ok=True)

CHANNELS = ["Instagram", "Facebook", "Carousell", "Shopee"]
COLOURWAYS = [
    "Putih/Hitam", "Hitam/Putih", "Hitam", "Putih", "Merah/Hitam",
    "Biru Navy", "Abu-abu", "Cokelat", "Krem", "Hijau Army",
    "Kuning", "Ungu", "Pink", "Oranye", "Biru Muda",
    "Hitam/Merah", "Putih/Merah", "Abu-abu/Hitam", "Hijau Mint",
    "Cokelat Muda",
]

# category -> (model families, price range IDR dummy, count, daily popularity)
CATEGORIES = {
    "Sneakers": (
        ["Air Force 1 '07", "Air Max 90", "Air Max 270", "Dunk Low",
         "Blazer Mid '77", "Cortez", "Air Jordan 1 Mid", "Air Max 97",
         "Air Max SC", "P-6000", "Air Max Pulse", "Dunk High"],
        (1_299_000, 3_499_000), 48, 1.00,
    ),
    "Running": (
        ["Pegasus 41", "Pegasus 40", "Vomero 17", "Invincible 3",
         "Structure 25", "Winflo 11", "React Infinity 4", "Zoom Fly 5",
         "Streakfly", "Alphafly 3"],
        (1_499_000, 2_999_000), 30, 0.85,
    ),
    "Trail Running": (
        ["Pegasus Trail 5", "Terra Kiger 10", "Zegama 2", "Wildhorse 9",
         "Ultrafly", "Trail 4", "Juniper Trail 3"],
        (1_799_000, 3_299_000), 18, 0.60,
    ),
    "Sandal dan Clogs": (
        ["Calm Slide", "Offcourt Slide", "Victori One Slide",
         "Calm Mule", "Calm Sandal", "Asuna 2 Slide"],
        (499_000, 1_199_000), 12, 0.70,
    ),
    "Basketball": (
        ["G.T. Cut 3", "Ja 3", "Sabrina 3", "LeBron 22", "KD 17",
         "Book 1"],
        (1_799_000, 3_999_000), 6, 0.75,
    ),
    "Training": (
        ["Metcon 9", "Free Metcon 6", "SuperRep Go 3", "Zoom Metcon",
         "MC Trainer 3", "Flex Experience 12"],
        (1_299_000, 2_499_000), 6, 0.55,
    ),
}

GENDERS = ["Pria", "Wanita", "Unisex"]
CHANNEL_WEIGHTS = {"Instagram": 1.15, "Facebook": 1.05, "Shopee": 1.00, "Carousell": 0.80}


def main():
    rng = random.Random(SEED)
    products = []
    pid = 0
    for category, (models, (lo, hi), count, popularity) in CATEGORIES.items():
        for i in range(count):
            pid += 1
            model = models[i % len(models)]
            colour = COLOURWAYS[rng.randrange(len(COLOURWAYS))]
            price = rng.randrange(lo, hi + 1, 1000)
            # Stock: a spread that includes out-of-stock and low-stock cases.
            stock = rng.choices(
                [0, 1, 2, 3, 4, 5, 8, 12, 18, 25, 35, 50, 60],
                weights=[4, 3, 3, 4, 4, 5, 12, 16, 16, 14, 10, 6, 3],
            )[0]
            availability = "habis" if stock == 0 else ("menipis" if stock <= 5 else "tersedia")
            n_channels = rng.choice([2, 2, 3, 3, 4])
            channels = rng.sample(CHANNELS, n_channels)
            products.append({
                "product_id": f"NK-DUMMY-{pid:03d}",
                "brand": "Nike",
                "category": category,
                "model": model,
                "product_name": f"Nike {model} (Contoh)",
                "colourway": colour,
                "gender": rng.choice(GENDERS),
                "price_dummy_idr": price,
                "stock_dummy": stock,
                "availability": availability,
                "channels": ";".join(channels),
                "size_range_eu": "36-47" if category != "Sandal dan Clogs" else "36-46",
                "popularity_dummy": round(popularity * rng.uniform(0.6, 1.4), 3),
                "data_label": "dummy",
            })

    with open(OUT / "nike_products_dummy.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(products[0].keys()))
        w.writeheader()
        w.writerows(products)

    # Daily sales, dummy dates 2026-01-01 to 2026-06-29 (180 days).
    start = date(2026, 1, 1)
    days = 180
    by_id = {p["product_id"]: p for p in products}
    total_units = 0
    total_revenue = 0
    sales_path = OUT / "nike_sales_dummy.csv"
    with open(sales_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date_dummy", "product_id", "channel", "units_sold_dummy",
                    "price_dummy_idr", "revenue_dummy_idr", "data_label"])
        for day_offset in range(days):
            day = start + timedelta(days=day_offset)
            # Weekend dummy boost, plus a gentle mid-period dummy peak.
            dow = 1.25 if day.weekday() >= 5 else 1.0
            season = 1.0 + 0.15 * (1 if 60 <= day_offset < 120 else 0)
            for p in products:
                lam = p["popularity_dummy"] * dow * season * 0.9
                for ch in CHANNELS:
                    # Poisson-like draw via Knuth's method, capped for sanity.
                    mean = lam * CHANNEL_WEIGHTS[ch]
                    # Simple approximation: use random choices around mean.
                    units = min(12, max(0, round(rng.gauss(mean, max(1.0, mean * 0.8)))))
                    revenue = units * p["price_dummy_idr"]
                    total_units += units
                    total_revenue += revenue
                    w.writerow([day.isoformat(), p["product_id"], ch, units,
                                p["price_dummy_idr"], revenue, "dummy"])

    summary = {
        "data_label": "dummy",
        "generator": "analysis/generate_nike_dummy.py",
        "seed": SEED,
        "products": len(products),
        "products_by_category": {
            cat: sum(1 for p in products if p["category"] == cat)
            for cat in CATEGORIES
        },
        "sales_rows": len(products) * len(CHANNELS) * days,
        "sales_date_range_dummy": ["2026-01-01", "2026-06-29"],
        "sales_days_dummy": days,
        "channels": CHANNELS,
        "total_units_sold_dummy": total_units,
        "total_revenue_dummy_idr": total_revenue,
        "out_of_stock_products_dummy": sum(1 for p in products if p["stock_dummy"] == 0),
        "low_stock_products_dummy": sum(1 for p in products if 0 < p["stock_dummy"] <= 5),
        "note": "All figures are dummy, generated with seed 42. Not Nike official data and not real Authenkixx sales.",
    }
    with open(OUT / "nike_summary_dummy.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
