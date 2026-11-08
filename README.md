# Gradasi Agregat

Aplikasi Streamlit untuk membantu analisis gradasi agregat, rancangan campuran
aspal (JMF), uji Marshall, estimasi biaya material, dan pembuatan laporan.
Aplikasi ini ditujukan untuk perhitungan awal dan pembelajaran; hasilnya perlu
ditinjau terhadap data laboratorium dan spesifikasi proyek yang berlaku.

## Fitur

- **Kalkulator** — menggabungkan fraksi agregat, mencari proporsi campuran,
  menampilkan grafik/tabel gradasi, menghitung JMF, parameter Marshall, KAO,
  dan estimasi biaya material.
- **Ekspor kalkulator** — menyimpan/memuat data JSON, mengunduh hasil Excel
  dan grafik PNG, atau mengunduh satu CSV gabungan untuk analisis di Excel,
  Python, R, dan perangkat lain.
- **Data Tersimpan** — melihat dan mengelola desain JSON yang disimpan ke
  riwayat SQLite aplikasi.
- **Perbandingan** — membandingkan dua desain dari JSON atau riwayat.
- **Laporan PDF** — membuat laporan PDF atau Word dari data JSON.
- **Cara Kerja** dan **Tentang** — penjelasan aplikasi.

## Menjalankan aplikasi

Gunakan Python dan pip, lalu dari direktori proyek jalankan:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Di Windows, aktifkan lingkungan virtual dengan
`.venv\Scripts\activate` setelah membuatnya. Buka alamat lokal yang dicetak
oleh Streamlit. Navigasi aplikasi memerlukan Streamlit 1.46 atau lebih baru.

`gradasi.html` adalah template kalkulator. `kalkulator.py` menyisipkan
`styles.css` dan `app.js` ke dalam template sebelum mengirimkannya ke iframe
Streamlit; ketiga berkas tersebut harus tetap berada di direktori yang sama.

## Alur penggunaan kalkulator

1. Pilih spesifikasi dan jumlah fraksi, lalu masukkan ukuran ayakan, batas
   spesifikasi, dan persen lolos tiap fraksi. Batas dapat disunting untuk
   menyesuaikan spesifikasi yang digunakan.
2. Pilih langkah pencarian dan berat total, lalu jalankan pencarian proporsi
   optimal. Hasil tetap dihitung proporsional jika jumlah persen proporsi
   tidak tepat 100%; aplikasi memberi peringatan untuk penyimpangan.
3. Tinjau target dan pengaturan JMF, lalu masukkan parameter serta data benda
   uji Marshall untuk melihat hasil per kadar aspal dan perkiraan KAO.
4. Untuk biaya, masukkan harga aspal, agregat kasar, agregat halus, dan filler
   dalam Rp/ton. Perhitungan biaya tersedia setelah komposisi JMF valid.
5. Simpan data di browser, unduh JSON sebagai cadangan yang dapat dimuat
   kembali, atau unduh CSV untuk mengolah data di perangkat lain.

### Ekspor CSV untuk pengguna teknis

Tombol **Unduh data mentah (.csv)** menghasilkan satu tabel UTF-8 dengan
header kolom stabil dan kolom `record_type` untuk membedakan jenis baris.
Jenis yang dapat muncul meliputi data gradasi per ayakan dan pan, ringkasan
JMF, data mentah dan hasil tiap benda uji Marshall, rata-rata per kadar aspal,
hasil/rentang KAO, serta harga dan estimasi biaya per material. CSV memuat
input yang tersedia; hasil turunan dibiarkan kosong jika datanya belum cukup
atau perhitungan tidak valid. Nilai numerik menggunakan titik desimal.

CSV ini untuk ekspor dan analisis lanjutan, bukan format untuk memuat ulang
data ke aplikasi. Gunakan **Unduh JSON** untuk menyimpan berkas yang dapat
dimuat kembali.

## Asumsi perhitungan

- Gradasi gabungan adalah jumlah persen lolos tiap fraksi yang dibobot oleh
  proporsinya. Bobot dinormalisasi terhadap jumlah proporsi yang dimasukkan.
- Pencarian proporsi mencoba kombinasi pada langkah yang dipilih (langkah
  minimum 0,5% untuk empat fraksi). Jika tidak ada kombinasi yang memenuhi
  semua batas, aplikasi menampilkan kombinasi dengan pelanggaran terkecil,
  bukan solusi yang memenuhi spesifikasi.
- Target JMF menggunakan nilai tengah batas minimum/maksimum atau gradasi
  campuran, sesuai pilihan. Rumus kadar aspal Pb yang ditampilkan:
  `0,035 × %CA + 0,045 × %FA + 0,18 × %FF + K`.
- Untuk Marshall, `Gmb = berat kering / (berat SSD - berat dalam air)`;
  `Gmm = 100 / ((100 - KA) / Gse + KA / Gb)`;
  `VIM = 100 × (Gmm - Gmb) / Gmm`;
  `VMA = 100 - Gmb × (100 - KA) / Gsb`;
  `VFA = 100 × (VMA - VIM) / VMA`.
  Stabilitas hasil adalah pembacaan dikali pengali stabilitas; `MQ` adalah
  stabilitas hasil dibagi Flow. Rumus menganggap KA dan persen gradasi
  dimasukkan dalam satuan persen.
- KAO adalah titik tengah rentang kadar aspal yang memenuhi batas pada kurva
  regresi parameter Marshall. Regresi merupakan pendekatan numerik dari data
  yang dimasukkan, bukan prediksi kinerja campuran.
- Biaya adalah estimasi material per ton campuran dari harga satuan yang
  dimasukkan dan proporsi JMF. Biaya tidak mencakup tenaga kerja, transportasi,
  pajak, kehilangan material, biaya produksi, atau faktor proyek lainnya.

## Batasan dan kehati-hatian

- Periksa sumber, satuan, konsistensi, dan kelengkapan data laboratorium.
  Peringatan validasi tidak menggantikan pemeriksaan teknis.
- Spesifikasi bawaan adalah nilai awal yang dapat diedit; pastikan versi
  spesifikasi dan persyaratan kontrak yang berlaku sebelum memakai hasil.
- Data contoh dan contoh harga hanya untuk ilustrasi. Harga contoh bukan
  penawaran atau survei harga terkini.
- Aplikasi tidak memprediksi rutting atau fatigue dan tidak menggunakan
  machine learning untuk memprediksi KAO. Hasil tidak menggantikan desain,
  pengujian, atau persetujuan engineer yang berwenang.
- Penyimpanan browser bersifat lokal pada browser/perangkat tersebut.
  Riwayat SQLite disimpan di sisi server dan dapat dibagikan oleh pengguna
  aplikasi; jangan unggah data rahasia. Pada layanan hosting sementara,
  penyimpanan server dapat hilang saat aplikasi dimulai ulang atau di-deploy
  ulang. Simpan cadangan JSON secara berkala.

## Struktur proyek

| Berkas | Kegunaan |
| --- | --- |
| `app.py` | Konfigurasi dan navigasi Streamlit |
| `kalkulator.py` | Memuat template dan aset kalkulator |
| `gradasi.html`, `styles.css`, `app.js` | Struktur, gaya, dan logika kalkulator |
| `compute.py` | Perhitungan gradasi, Marshall, dan KAO bersama |
| `data_tersimpan.py`, `db.py` | Antarmuka dan penyimpanan riwayat desain |
| `perbandingan.py` | Perbandingan dua desain |
| `laporan_pdf.py` | Pembuatan laporan PDF dan Word |
| `theme.py`, `ui.py` | Tema dan pembantu antarmuka |
| `requirements.txt` | Dependensi Python |
