"""Generate the dummy dataset used by this prototype repo.

Deterministic (seed 42). No real UMKM data: product names, prices,
channels, and sales numbers are invented examples with the same shape
as the inventory problem (products x channels x days). The output CSV
is labelled dummy everywhere it is used.
"""
import csv
import os
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "dummy_inventory_sales.csv")

PRODUCTS = [
    # (code, name, price, start stock, max units per channel-day, weekly restock)
    ("DUMMY-001", "Sepatu Sneakers Putih (Contoh)", 299000, 40, 2, 30),
    ("DUMMY-002", "Sepatu Sneakers Hitam (Contoh)", 329000, 35, 3, 40),
    ("DUMMY-003", "Sepatu Lari Ringan (Contoh)", 459000, 30, 4, 20),
    ("DUMMY-004", "Sepatu Kasual Cokelat (Contoh)", 279000, 45, 2, 50),
    ("DUMMY-005", "Sepatu Slip-On Abu (Contoh)", 249000, 30, 3, 25),
]
CHANNELS = ["Instagram", "Facebook", "Carousell", "Shopee"]


def main():
    rng = random.Random(42)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # Stock is tracked per product (shared across channels in this dummy
    # model); daily sales are per product x channel. Stock evolves day
    # by day from the starting stock, never below zero in the generator.
    stock = {code: start for code, _, _, start, _, _ in PRODUCTS}
    rows = []
    for day in range(1, 31):
        date = f"2026-09-{day:02d}"
        for code, name, price, _, max_units, restock in PRODUCTS:
            # Dummy weekly restock on days 8, 15, 22, 29 (labelled in data).
            restock_today = restock if day in (8, 15, 22, 29) else 0
            stock[code] += restock_today
            for channel in CHANNELS:
                units = rng.randint(0, max_units)
                units = min(units, stock[code])
                stock_start = stock[code]
                stock[code] -= units
                rows.append({
                    "date_dummy": date,
                    "product_code": code,
                    "product_name_dummy": name,
                    "channel_dummy": channel,
                    "units_sold_dummy": units,
                    "price_dummy_idr": price,
                    "stock_start_dummy": stock_start,
                    "stock_end_dummy": stock[code],
                    "restock_dummy": restock_today if channel == CHANNELS[0] else 0,
                })
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} dummy rows to {OUT}")


if __name__ == "__main__":
    main()
