# Prototype Data Science (Capstone Authenkixx)

Ini masih prototype, ya. Dibuat oleh Ade Bintang. Semua datanya
dummy. Nggak ada data asli UMKM, nggak ada data customer, nggak ada
password, dan nggak ada sinkronisasi otomatis ke platform lain.

## Yang berubah: data Nike dummy (25 Oktober 2026)

- Dataset lama 600 baris sudah diganti output-nya dengan dataset
  Nike dummy: 120 produk, 86.400 baris penjualan dummy
  (120 produk x 4 kanal x 180 hari dummy, 2026-01-01 sampai
  2026-06-29), total 82.526 unit dummy dan revenue dummy
  Rp 186.375.340.000. Script barunya:
  `analysis/wrangle_analyze_nike.py` dan
  `analysis/baseline_model_nike.py`, output-nya tetap ke
  `outputs/business_summary.json` dan `outputs/baseline_model.json`
  supaya backend Full-Stack nggak perlu diubah.
- Baseline-nya juga berubah definisi (jujur ditulis di bawah),
  karena dataset Nike nggak punya trayektori stok harian, jadi
  target minggu depan yang lama nggak bisa dihitung dari data ini.
- File dataset lama (`data/dummy_inventory_sales.csv` dan script
  lamanya) dibiarkan utuh sebagai arsip, bukan dihapus, tapi
  output yang dipakai sekarang adalah dari dataset Nike.

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
python analysis/generate_nike_dummy.py     # bikin ulang dataset Nike dummy (seed 42)
python analysis/wrangle_analyze_nike.py    # -> outputs/business_summary.json
python analysis/baseline_model_nike.py     # -> outputs/baseline_model.json
streamlit run dashboard/app.py             # dashboard interaktif (masih pakai data lama, lihat bawah)
```

## Data (cuma dummy, sudah dilabeli)

- `data/nike_dummy/nike_products_dummy.csv`: 120 produk Nike dummy
  (Sneakers 48, Running 30, Trail Running 18, Sandal dan Clogs 12,
  Basketball 6, Training 6), harga dummy Rp 513.000 sampai
  Rp 3.984.000, stok dummy 0 sampai 60.
- `data/nike_dummy/nike_sales_dummy.csv`: 86.400 baris, tanggal
  dummy 2026-01-01 sampai 2026-06-29, 120 produk x 4 label kanal
  (Instagram, Facebook, Carousell, Shopee) x 180 hari.
- `data/nike_dummy/nike_data_dictionary.md`: definisi kolom
  lengkap, sumbernya (dibuat oleh
  `analysis/generate_nike_dummy.py`, seed 42), dan batasannya.
  Nilai kanal itu cuma label, bukan bukti penjualan di kanal itu
  dan bukan sinkronisasi.
- Dataset lama `data/dummy_inventory_sales.csv` (600 baris,
  September 2026 dummy, 5 produk) masih ada sebagai arsip, tapi
  bukan lagi sumber output yang dipakai.
- Batasan: di dataset Nike ini, stok adalah stok dummy saat ini
  per produk, bukan trayektori stok harian, jadi nggak bisa
  menghitung stok akhir per hari dari file penjualan. Di dataset
  ini sengaja nggak ada data customer, pesanan, pembayaran, atau
  pengiriman.

## Data wrangling

`analysis/wrangle_analyze_nike.py`: parsing tanggal dummy,
memastikan nggak ada nilai yang hilang, menghitung revenue dummy
(unit x harga dummy), terus diagregasi per kanal, kategori, dan
produk. Stok menipis dihitung dari stok dummy saat ini per produk
(<= 5), bukan dari stok akhir harian, karena file penjualan Nike
nggak punya trayektori stok.

## Temuan dan rekomendasi (data dummy saja)

Sudah diverifikasi dengan menjalankan `wrangle_analyze_nike.py`
di dataset Nike dummy:

- Total unit dummy terjual: 82.526. Total revenue dummy:
  Rp 186.375.340.000 (harga dummy x unit dummy, BUKAN revenue asli,
  dan volumenya sengaja besar buat pemodelan, bukan gambaran toko
  asli).
- Unit per kanal (dummy): Instagram 23.254, Facebook 21.288,
  Shopee 20.425, Carousell 17.559. Instagram paling tinggi di
  dataset dummy ini.
- Unit per kategori (dummy): Sneakers 37.346, Running 21.849,
  Trail Running 9.824, Sandal dan Clogs 7.082, Basketball 3.489,
  Training 2.936.
- Baris penjualan untuk produk stok menipis dummy (stok saat ini
  <= 5): 21.600 dari 86.400 baris.
- Stok dummy saat ini: 120 produk, 90 tersedia, 24 menipis, 6 habis.

Rekomendasi (cuma sinyal dummy, konfirmasi dulu pakai data asli):
1. Restock produk dummy yang stoknya menipis atau habis sebelum
   makin banyak yang nol.
2. Fokus cek restock ke kanal dan kategori dengan unit dummy
   tertinggi, tapi jangan anggap ranking dummy ini sebagai ranking
   yang asli.
3. Pertahankan satu data induk inventory supaya label kanal nggak
   saling melenceng, dan jangan tambahkan sinkronisasi otomatis di
   prototype ini.

## Model baseline (tanpa leakage)

`analysis/baseline_model_nike.py`: memprediksi apakah sebuah
produk sedang stok menipis (stok dummy saat ini <= 5), dari harga
dummy, total unit dummy terjual 180 hari, dan unit dummy 30 hari
terakhir. Split stratified 80/20, random_state 42 (train 96 baris,
test 24 baris), dan scaler-nya cuma di-fit di data training, jadi
nggak ada informasi test yang bocor ke training. Modelnya:
LogisticRegression baseline.

Hasil terverifikasi (data dummy):
- Accuracy (test): 0.7500
- Macro F1 (test): 0.4286
- Test positive rate: 0.2500

Batasan yang jujur: accuracy 0.75 ini sama dengan sekadar menebak
semua produk tidak menipis (75 persen produk memang tidak menipis),
dan macro F1 yang rendah menunjukkan model ini praktis nggak
menangkap produk menipis. Itu masuk akal, karena di generator
dummy ini stok dibuat independen dari penjualan, jadi penjualan
nggak bisa memprediksi stok. Baseline ini cuma demo pipeline,
bukan forecast yang bisa langsung dipakai buat restock, dan
nggak bisa dibandingkan dengan baseline mingguan lama (accuracy
0.7833, macro F1 0.7044) karena target dan datanya sudah berubah.
Versi final wajib latih ulang di data yang sudah diputuskan
pemiliknya dan membandingkan model dengan benar.

## Dashboard

`dashboard/app.py` (Streamlit): indikator bisnis (total unit dummy,
total revenue dummy, baris stok menipis), filter kanal dan produk,
grafik unit dummy harian, dan jalur upload file buat mengganti CSV
dummy dengan file baru yang kolomnya sama, khusus buat sesi itu.
Catatan: dashboard ini masih membaca dataset lama, belum diperbarui
ke dataset Nike, jadi angkanya belum tentu sama dengan
`outputs/business_summary.json` yang baru. Dashboard ini masih
kerangka buat versi final: belum tertanam di web app Full-Stack
(nempelinnya masih kerjaan terbuka, titik konsumsi yang disepakati
adalah `outputs/business_summary.json` dan endpoint backend
`/api/v1/insights`, yang sudah disajikan).

## Cara tim lain memakai output-nya

- Full-Stack: baca `outputs/business_summary.json` buat insights,
  atau sajikan lewat `/api/v1/insights` (sudah, lihat
  `API_CONTRACT.md`).
- Gen AI: pakai label produk/kanal dummy di
  `data/nike_dummy/nike_products_dummy.csv` cuma sebagai konteks
  contoh, jangan pernah dianggap stok atau harga asli.
- Kamus data: `data/nike_dummy/nike_data_dictionary.md` (dataset
  Nike yang dipakai sekarang) dan `data/data_dictionary.md`
  (dataset lama, arsip).

## Disclaimer

Lihat CHECKLIST_STATUS.md di repo ini. Fase 1 bukan versi final.
Target akhirnya adalah menyesuaikan dokumen use case Authenkixx dan
memenuhi semua checklist Main Quest buat Full-Stack, Gen AI, dan
Data Science. Fase 1 belum mengklaim sudah memenuhi semuanya.
