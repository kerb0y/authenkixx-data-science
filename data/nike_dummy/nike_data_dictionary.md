# Kamus Data Dummy Nike Authenkixx

Semua data di folder ini adalah DUMMY, dibuat dengan generator
`analysis/generate_nike_dummy.py` (seed 42, bisa dijalankan ulang
dan hasilnya sama). Ini BUKAN data resmi Nike dan BUKAN data
penjualan asli Authenkixx. Nama model (misalnya Air Force 1,
Pegasus, Terra Kiger) dipakai hanya sebagai label contoh katalog
untuk prototype, bukan klaim katalog resmi Nike. Harga, stok, dan
penjualan adalah angka dummy.

Sumber acuan model yang dicari: dataset Kaggle "Nike Shoes Sales"
(ulrikthygepedersen/nike-shoes-sales, diperbarui 2023-03-01, kolom
Product name, Product ID, Listing Price, Sales Price, Discount,
Brand, Description, Rating, Reviews, Image url). Dataset Kaggle itu
tidak diunduh dan tidak dipakai langsung, karena: butuh login Kaggle
untuk unduh, bentuknya snapshot listing produk (bukan inventory
dengan stok dan bukan riwayat penjualan harian per kanal), dan
tidak terstruktur per kategori trail running, running, sandal/clogs
seperti yang diminta Authenkixx. Jadi dataset Kaggle itu hanya jadi
acuan keluarga model, sedangkan dataset di sini dibuat dummy
khusus untuk use case inventory Authenkixx.

## File

- `nike_products_dummy.csv`: 120 produk, 1 baris per produk.
- `nike_sales_dummy.csv`: 86.400 baris, yaitu 120 produk x 4 kanal
  x 180 hari dummy (2026-01-01 sampai 2026-06-29).
- `nike_summary_dummy.json`: total yang sudah dihitung dari kedua
  file di atas, untuk pengecekan saja.

## nike_products_dummy.csv

| Kolom | Arti |
|---|---|
| product_id | ID dummy, NK-DUMMY-001 sampai NK-DUMMY-120 |
| brand | Selalu Nike (fokus toko ini) |
| category | Sneakers, Running, Trail Running, Sandal dan Clogs, Basketball, Training |
| model | Keluarga model contoh, misalnya Air Force 1 '07, Pegasus 41, Terra Kiger 10, Calm Slide |
| product_name | Nama produk contoh, selalu diakhiri (Contoh) |
| colourway | Warna contoh |
| gender | Pria, Wanita, atau Unisex (dummy) |
| price_dummy_idr | Harga dummy dalam rupiah, kelipatan Rp 1.000 |
| stock_dummy | Stok dummy saat ini |
| availability | habis kalau stok 0, menipis kalau stok 1-5, tersedia kalau stok di atas 5 |
| channels | Label kanal tempat produk ini dijual (dipisah titik koma), dari Instagram, Facebook, Carousell, Shopee. Ini label saja, bukan sinkronisasi otomatis. |
| size_range_eu | Rentang ukuran contoh |
| popularity_dummy | Faktor popularitas dummy yang dipakai generator penjualan, bukan rating asli |
| data_label | Selalu dummy |

Jumlah produk per kategori: Sneakers 48, Running 30, Trail Running
18, Sandal dan Clogs 12, Basketball 6, Training 6. Total 120.
Rentang harga dummy: Rp 513.000 sampai Rp 3.984.000. Stok dummy:
0 sampai 60, dengan 6 produk habis dan 24 produk menipis.

## nike_sales_dummy.csv

| Kolom | Arti |
|---|---|
| date_dummy | Tanggal dummy, 2026-01-01 sampai 2026-06-29 |
| product_id | Merujuk ke nike_products_dummy.csv |
| channel | Instagram, Facebook, Carousell, atau Shopee (label saja) |
| units_sold_dummy | Unit dummy terjual hari itu di kanal itu |
| price_dummy_idr | Harga dummy produk itu (sama sepanjang periode) |
| revenue_dummy_idr | units_sold_dummy x price_dummy_idr |
| data_label | Selalu dummy |

Total yang terverifikasi: 86.400 baris, 82.526 unit dummy,
revenue dummy Rp 186.375.340.000. Angka revenue ini besar karena
volume dummy-nya sengaja dibuat banyak untuk keperluan pemodelan
Data Science, bukan gambaran volume toko asli. Jangan dikutip
sebagai omzet Authenkixx.

Unit dummy per kategori: Sneakers 37.346, Running 21.849,
Trail Running 9.824, Sandal dan Clogs 7.082, Basketball 3.489,
Training 2.936.

Unit dummy per kanal: Instagram 23.254, Facebook 21.288,
Shopee 20.425, Carousell 17.559.

## Cara pakai dan batasan

- Untuk Full-Stack: `nike_products_dummy.csv` sudah dipakai
  sebagai inventory (`backend/data/inventory.json`, 120 produk,
  ID NK-DUMMY-001 sampai NK-DUMMY-120), dan
  `outputs/business_summary.json` serta
  `outputs/baseline_model.json` sudah dihitung ulang dari dataset
  ini (script `analysis/wrangle_analyze_nike.py` dan
  `analysis/baseline_model_nike.py`). Jadi angka baru dan angka
  lama tidak boleh dicampur: dataset 600 baris lama dan ringkasan
  lamanya sudah digantikan output-nya.
- Untuk Gen AI: nama model dan kategori di sini sudah dipakai
  sebagai katalog produk contoh (`gen-ai/data/dummy_products.csv`,
  120 produk Nike dummy yang sama), bukan stok atau harga asli.
- Tidak ada data customer, pesanan, pembayaran, atau pengiriman
  di dataset ini, sesuai scope use case.
- Kalau nanti ada data asli dari pemilik (Ade), dataset dummy ini
  diganti dan semua total dihitung ulang, bukan ditambal.
