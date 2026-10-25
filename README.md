# Prototype Data Science (Capstone Authenkixx)

Ini masih prototype, ya. Dibuat oleh Ade Bintang. Semua datanya
dummy. Nggak ada data asli UMKM, nggak ada data customer, nggak ada
password, dan nggak ada sinkronisasi otomatis ke platform lain.

## Yang berubah di Fase 1 (25 Oktober 2026)

- Kode analisisnya nggak berubah: output dummy-nya dijalankan ulang
  dan diverifikasi lagi di Fase 1 (633 unit dummy, revenue dummy
  Rp 203.667.000, accuracy baseline 0.7833, macro F1 0.7044), dan
  sekarang output itu disajikan ke web app oleh backend Full-Stack
  lewat `GET /api/v1/insights` (bagian `data_science`-nya). Buat
  bentuknya, lihat `API_CONTRACT.md`.
- Fase 1 ini sudah di-push ke GitHub.

## Masalahnya dan peran data di sini

Pemilik toko itu nggak bisa lihat dalam satu tempat, produk dummy
mana yang laku, kanal mana yang paling laku, atau stok mana yang
mulai menipis. Data menjawab itu dengan mengubah catatan
inventory/penjualan dummy jadi total, breakdown per kanal dan
produk, sinyal stok menipis, dan model baseline stok menipis yang
bisa dipakai tim lain dalam bentuk JSON. Keputusan beneran tetap
harus nunggu data asli yang diputuskan pemiliknya (Ade), nggak ada
pihak luar yang perlu ditunggu.

## Pertanyaan bisnis (dijawab pakai data dummy)

1. Kanal mana yang menjual unit dummy paling banyak?
2. Produk dummy mana yang paling laku, dan mana yang stoknya menipis?
3. Di hari atau minggu dummy mana stok paling rendah?

## Cara jalanin

```bash
pip install -r requirements.txt
python analysis/generate_dummy_data.py   # bikin ulang CSV dummy (seed 42)
python analysis/wrangle_analyze.py       # -> outputs/business_summary.json
python analysis/baseline_model.py        # -> outputs/baseline_model.json
streamlit run dashboard/app.py           # dashboard interaktif
```

## Data (cuma dummy, sudah dilabeli)

- `data/dummy_inventory_sales.csv`: 600 baris, tanggal dummy
  2026-09-01 sampai 2026-09-30, 5 produk dummy x 4 label kanal
  (Instagram, Facebook, Carousell, Shopee) x 30 hari.
- `data/data_dictionary.md`: definisi kolom lengkap, sumbernya
  (dibuat oleh `analysis/generate_dummy_data.py`, seed 42), dan
  batasannya. Nilai kanal itu cuma label, bukan bukti penjualan di
  kanal itu dan bukan sinkronisasi.
- Batasan: stok di generator itu dipakai bareng lintas kanal dan
  urutan kanal dalam satu hari itu acak, jadi baris stok per kanal
  bukan buku stok per kanal yang beneran. Di dataset ini sengaja
  nggak ada data customer, pesanan, pembayaran, atau pengiriman.

## Data wrangling

`analysis/wrangle_analyze.py`: parsing tanggal dummy, memastikan
nggak ada nilai yang hilang, menghitung revenue dummy (unit x harga
dummy) dan flag stok menipis (stock_end <= 5), terus diagregasi per
kanal, produk, dan hari.

## Temuan dan rekomendasi (data dummy saja)

Sudah diverifikasi dengan menjalankan `wrangle_analyze.py` di CSV
dummy:

- Total unit dummy terjual: 633. Total revenue dummy:
  Rp 203.667.000 (harga dummy x unit dummy, BUKAN revenue asli).
- Unit per kanal (dummy): Facebook 178, Shopee 153, Instagram 152,
  Carousell 150. Facebook paling tinggi di dataset dummy ini.
- Unit per produk (dummy): Sepatu Sneakers Hitam (Contoh) 166,
  Sepatu Sneakers Putih (Contoh) 122, Sepatu Kasual Cokelat (Contoh)
  119, Sepatu Slip-On Abu (Contoh) 116, Sepatu Lari Ringan (Contoh)
  110.
- Baris stok menipis (stock_end <= 5): 149 dari 600 baris.
- Stok akhir dummy: DUMMY-001: 41, DUMMY-002: 35, DUMMY-003: 5,
  DUMMY-004: 127, DUMMY-005: 14.

Rekomendasi (cuma sinyal dummy, konfirmasi dulu pakai data asli):
1. Restock produk dummy yang stok akhirnya menipis (terutama
   DUMMY-003 di angka 5) sebelum sampai nol.
2. Fokus cek restock ke kanal dengan unit dummy tertinggi, tapi
   jangan anggap ranking dummy ini sebagai ranking kanal yang asli.
3. Pertahankan satu data induk inventory supaya label kanal nggak
   saling melenceng, dan jangan tambahkan sinkronisasi otomatis di
   prototype ini.

## Model baseline (tanpa leakage)

`analysis/baseline_model.py`: memprediksi apakah minggu
produk-kanal akan berakhir di stok menipis minggu depannya
(stock_end <= 5 di minggu berikutnya). Fiturnya cuma dari minggu
sebelumnya (stok awal minggu, rata-rata unit harian, harga). Split
berdasarkan waktu (train minggu < 38, test minggu >= 38; train 40
baris, test 60 baris), dan scaler-nya cuma di-fit di data training,
jadi nggak ada informasi test yang bocor ke training. Modelnya:
LogisticRegression baseline.

Hasil terverifikasi (data dummy):
- Accuracy (test): 0.7833
- Macro F1 (test): 0.7044
- Test positive rate: 0.2000

Batasan: cuma data dummy, sampel mingguan kecil (60 baris test),
dan generator stoknya dipakai bareng lintas kanal, jadi baseline
ini cuma demo pipeline, bukan forecast yang bisa langsung dipakai
buat restock. Versi final wajib latih ulang di data yang sudah
diputuskan pemiliknya dan membandingkan model dengan benar.

## Dashboard

`dashboard/app.py` (Streamlit): indikator bisnis (total unit dummy,
total revenue dummy, baris stok menipis), filter kanal dan produk,
grafik unit dummy harian, dan jalur upload file buat mengganti CSV
dummy dengan file baru yang kolomnya sama, khusus buat sesi itu.
Dashboard ini masih kerangka buat versi final: belum tertanam di
web app Full-Stack (nempelinnya masih kerjaan terbuka, titik
konsumsi yang disepakati adalah `outputs/business_summary.json`
dan endpoint backend `/api/v1/insights`, yang sejak Fase 1 sudah
disajikan).

## Cara tim lain memakai output-nya

- Full-Stack: baca `outputs/business_summary.json` buat insights,
  atau sajikan lewat `/api/v1/insights` (Fase 1: sudah, lihat
  `API_CONTRACT.md`).
- Gen AI: pakai label produk/kanal dummy di
  `data/dummy_inventory_sales.csv` cuma sebagai konteks contoh,
  jangan pernah dianggap stok atau harga asli.
- Kamus data: `data/data_dictionary.md`.

## Disclaimer

Lihat CHECKLIST_STATUS.md di repo ini. Fase 1 bukan versi final.
Target akhirnya adalah menyesuaikan dokumen use case Authenkixx dan
memenuhi semua checklist Main Quest buat Full-Stack, Gen AI, dan
Data Science. Fase 1 belum mengklaim sudah memenuhi semuanya.
