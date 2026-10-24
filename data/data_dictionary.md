# Data Dictionary (Dummy Data Only)

Source: `data-science/analysis/generate_dummy_data.py` (seed 42).
This dataset is invented for the prototype. It is NOT real Authenkixx
data, NOT real sales, and NOT real prices. Do not use it for real
business decisions. The final version must replace it with primary
UMKM data only if the PIC confirms it.

File: `data/dummy_inventory_sales.csv` (600 rows, dummy dates 2026-09-01 to 2026-09-30)

| Column | Meaning |
|---|---|
| date_dummy | Dummy date of the sales row |
| product_code | Dummy product code, e.g. DUMMY-001 |
| product_name_dummy | Invented product name, always labelled (Contoh) |
| channel_dummy | Channel label only: Instagram, Facebook, Carousell, Shopee. Labels are not sync and not proof of a sale on that channel |
| units_sold_dummy | Invented units sold that day for that product and channel |
| price_dummy_idr | Invented unit price in IDR (dummy, not a real UMKM price) |
| stock_start_dummy | Dummy shared stock before that channel's sales that day |
| stock_end_dummy | Dummy shared stock after that channel's sales that day |
| restock_dummy | Dummy weekly restock on days 8, 15, 22, 29 (first channel row of the day only) |

Limitations:
- Stock is shared across channels in the generator and channel order
  within a day is arbitrary, so per-channel stock rows are not a real
  channel-level stock ledger.
- No customer data, no order IDs, no payment or shipping data exists
  in this dataset, by design (out of prototype scope).
- The 30-day dummy period is invented and has no relation to real
  Authenkixx trading dates.

How other teams consume the outputs:
- `outputs/business_summary.json`: totals and findings for the
  Full-Stack insights feature and for Gen AI context (dummy only).
- `outputs/baseline_model.json`: baseline low-stock model metrics.
- The Streamlit dashboard reads the same CSV, or a user-uploaded CSV
  with identical columns.
