# Gradasi Agregat

Aplikasi Streamlit untuk analisis gradasi agregat, rancangan campuran aspal (JMF), uji Marshall, estimasi biaya material, dan pembuatan laporan.

**Coba aplikasinya:** <https://gradasi-agregat.streamlit.app/>

> [!IMPORTANT]
> Aplikasi ini dibuat untuk perhitungan awal dan pembelajaran. Hasilnya harus ditinjau terhadap data laboratorium dan spesifikasi proyek yang berlaku, dan tidak menggantikan desain, pengujian, atau persetujuan engineer yang berwenang.

## Daftar isi

- [Fitur](#fitur)
- [Menjalankan aplikasi](#menjalankan-aplikasi)
- [Membuat aplikasi desktop Windows](#membuat-aplikasi-desktop-windows)
- [Versi spesifikasi](#versi-spesifikasi)
- [Alur penggunaan kalkulator](#alur-penggunaan-kalkulator)
- [Ekspor CSV untuk analisis lanjutan](#ekspor-csv-untuk-analisis-lanjutan)
- [Asumsi perhitungan](#asumsi-perhitungan)
- [Batasan dan kehati-hatian](#batasan-dan-kehati-hatian)
- [Struktur proyek](#struktur-proyek)

## Fitur

| Halaman / fitur | Kegunaan |
| --- | --- |
| **Kalkulator** | Menggabungkan fraksi agregat, mencari proporsi campuran, menampilkan grafik dan tabel gradasi, serta menghitung JMF, parameter Marshall, aspal terserap dan efektif (Pba/Pbe), rasio debu-aspal (D/B), KAO, dan estimasi biaya material. |
| **Tiga preset kalkulator** | *Contoh standar* untuk demonstrasi, *template kosong* untuk memasukkan hasil laboratorium Anda sendiri, dan *skenario uji tidak wajar* untuk melihat respons validasi. Template kosong bukan data hasil pengujian nyata. |
| **Ekspor kalkulator** | Simpan dan muat data JSON, unduh hasil Excel dan grafik PNG, atau unduh satu CSV gabungan untuk analisis di Excel, Python, R, dan perangkat lain. |
| **Data Tersimpan** | Melihat dan mengelola desain JSON yang tersimpan di riwayat SQLite aplikasi. |
| **Perbandingan** | Membandingkan dua desain, dari JSON atau dari riwayat. |
| **Laporan PDF** | Membuat laporan PDF atau Word dari data JSON. |
| **Cara Kerja** dan **Tentang** | Penjelasan singkat tentang aplikasi. |

## Menjalankan aplikasi

Pastikan Python dan pip sudah terpasang, lalu jalankan perintah berikut dari direktori proyek:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Di Windows, aktifkan lingkungan virtual dengan `.venv\Scripts\activate` setelah membuatnya. Buka alamat lokal yang ditampilkan Streamlit di browser.

Navigasi aplikasi memerlukan **Streamlit 1.46 atau lebih baru**.

## Membuat aplikasi desktop Windows

**Build lokal.** Jalankan `build_windows.bat` di Windows dengan Python 3.11 dan koneksi internet. Hasilnya ada di `dist/GradasiAgregat/`. Bagikan **seluruh folder** tersebut, bukan hanya berkas EXE-nya.

Saat dibuka, aplikasi menjalankan Streamlit secara lokal dan membuka browser, sehingga hosting publik tidak diperlukan. Riwayat desain disimpan di `%LOCALAPPDATA%/GradasiAgregat/history.db`.

> [!NOTE]
> Paket ini belum berupa installer. Uji dulu di komputer Windows lain sebelum dibagikan.

**Build lewat GitHub Actions.** Push perubahan ke GitHub, buka **Actions** → **Build Windows EXE** → **Run workflow**, lalu unduh artifact `GradasiAgregat-windows` dari halaman run yang sudah selesai. Workflow ini juga berjalan otomatis saat tag versi berawalan `v` dipush, misalnya `v1.0`.

**Catatan arsitektur.** `gradasi.html` adalah template kalkulator. `kalkulator.py` menyisipkan `styles.css`, `app.js`, dan data dari `specs.json` ke dalam template, lalu mengirimkannya ke iframe Streamlit. Berkas-berkas ini harus tetap berada di direktori yang sama.

## Versi spesifikasi

Preset awal berasal dari **Bina Marga 2018**. Pilih versi di Kalkulator untuk menerapkan batas gradasi dan batas Marshall dari versi tersebut. Batas yang sudah Anda sunting disimpan bersama data desain dan tidak berubah hanya karena preset aplikasi berganti.

Untuk menambah versi baru:

1. Tambahkan entri di `specs.json` dengan ID unik, nama, sumber dokumen, batas gradasi, dan batas Marshall yang sudah diverifikasi.
2. Atur `default_version` untuk menentukan preset bagi desain baru.
3. Perbarui tes jika struktur atau perilakunya berubah.

Jangan mengisi versi baru dengan angka perkiraan; periksa dokumen resminya. Data desain menyimpan `spec_version` agar preset asal tetap dapat ditelusuri, dan laporan juga mencantumkannya.

## Alur penggunaan kalkulator

1. **Masukkan data gradasi.** Pilih spesifikasi dan jumlah fraksi, lalu isi ukuran ayakan, batas spesifikasi, dan persen lolos tiap fraksi. Batas dapat disunting sesuai spesifikasi yang Anda pakai.
2. **Cari proporsi.** Pilih langkah pencarian dan berat total, lalu jalankan pencarian proporsi optimal. Jika jumlah proporsi tidak tepat 100%, hasil tetap dihitung secara proporsional dan aplikasi menampilkan peringatan.
3. **Tinjau JMF dan Marshall.** Periksa target dan pengaturan JMF, lalu isi parameter serta data benda uji Marshall untuk melihat hasil per kadar aspal dan perkiraan KAO.
4. **Hitung biaya.** Masukkan harga aspal, agregat kasar, agregat halus, dan filler dalam Rp/ton. Perhitungan biaya tersedia setelah komposisi JMF valid.
5. **Simpan data.** Simpan di browser, unduh JSON sebagai cadangan yang dapat dimuat kembali, atau unduh CSV untuk diolah di perangkat lain.

### Tombol preset

- **Muat contoh standar** memuat data ilustrasi bawaan.
- **Muat template data asli** mengosongkan nilai pengukuran agar dapat diisi dengan hasil praktikum atau laboratorium Anda. Proyek ini tidak menyertakan maupun memverifikasi data laboratorium nyata, sehingga perbandingan dengan perhitungan manual memerlukan data asli Anda.
- **Muat skenario uji aneh** memuat proporsi 110%, satu nilai persen lolos kosong, ayakan terbalik, beberapa data Marshall tidak wajar, dan hanya satu kadar aspal valid. Gunanya untuk menguji pesan validasi dan kondisi KAO.

## Ekspor CSV untuk analisis lanjutan

Tombol **Unduh data mentah (.csv)** menghasilkan satu tabel UTF-8 dengan header kolom yang stabil dan kolom `record_type` untuk membedakan jenis baris. Jenis baris yang dapat muncul:

- data gradasi per ayakan dan pan,
- ringkasan JMF,
- data mentah dan hasil tiap benda uji Marshall,
- rata-rata per kadar aspal,
- hasil dan rentang KAO,
- harga dan estimasi biaya per material.

CSV memuat input yang tersedia. Hasil turunan dikosongkan jika datanya belum cukup atau perhitungannya tidak valid. Nilai numerik memakai titik desimal.

> [!NOTE]
> CSV hanya untuk ekspor dan analisis lanjutan, bukan untuk memuat ulang data ke aplikasi. Gunakan **Unduh JSON** untuk berkas yang dapat dimuat kembali.

## Asumsi perhitungan

**Gradasi gabungan**
- Persen lolos gabungan adalah jumlah persen lolos tiap fraksi yang dibobot proporsinya. Bobot dinormalisasi terhadap jumlah proporsi yang dimasukkan.
- Pencarian proporsi mencoba kombinasi pada langkah yang dipilih (langkah minimum 0,5% untuk empat fraksi). Jika tidak ada kombinasi yang memenuhi semua batas, aplikasi menampilkan kombinasi dengan pelanggaran terkecil, yang **bukan** solusi yang memenuhi spesifikasi.

**Kadar aspal JMF**
- Target JMF memakai nilai tengah batas minimum dan maksimum, atau gradasi campuran, sesuai pilihan.
- Rumus kadar aspal Pb:

  ```text
  Pb = 0,035 × %CA + 0,045 × %FA + 0,18 × %FF + K
  ```

**Parameter Marshall**

```text
Gmb = berat kering / (berat SSD − berat dalam air)
Gmm = 100 / ((100 − KA) / Gse + KA / Gb)
VIM = 100 × (Gmm − Gmb) / Gmm
VMA = 100 − Gmb × Ps / Gsb          (Ps = 100 − KA)
VFA = 100 × (VMA − VIM) / VMA
```

- Stabilitas hasil adalah pembacaan dikali pengali stabilitas, dan MQ adalah stabilitas hasil dibagi Flow.
- KA dan persen gradasi dimasukkan dalam satuan persen.

**Aspal terserap, aspal efektif, dan rasio debu-aspal**

```text
Pba = 100 × (Gse − Gsb) / (Gse × Gsb) × Gb
Pbe = KA − (Pba / 100) × Ps
D/B = P200 / Pbe
```

- `P200` adalah persen lolos ayakan 0,075 mm dari gradasi gabungan.
- Pba dinyatakan terhadap berat agregat, sedangkan Pbe terhadap berat campuran.
- Rasio D/B 0,6–1,2 ditampilkan hanya sebagai acuan umum, bukan batas kelulusan. Periksa spesifikasi proyek.
- Penambahan Pba dan Pbe tidak mengubah rumus VMA dan VFA: VMA memakai persen agregat `Ps`, bukan mengganti KA dengan Pbe.
- Metode uji Marshall terkait mencakup ASTM D2726, D2041, D3203, dan D6927. Rujukan desain campuran mencakup Asphalt Institute MS-2.

**KAO**
- KAO adalah titik tengah rentang kadar aspal yang memenuhi batas pada kurva regresi parameter Marshall.
- Regresi merupakan pendekatan numerik dari data yang dimasukkan, bukan prediksi kinerja campuran.

**Biaya**
- Biaya adalah estimasi material per ton campuran, dihitung dari harga satuan yang dimasukkan dan proporsi JMF.
- Biaya tidak mencakup tenaga kerja, transportasi, pajak, kehilangan material, biaya produksi, atau faktor proyek lainnya.

## Batasan dan kehati-hatian

- Periksa sumber, satuan, konsistensi, dan kelengkapan data laboratorium. Peringatan validasi tidak menggantikan pemeriksaan teknis.
- Spesifikasi bawaan hanyalah nilai awal yang dapat diedit. Pastikan versi spesifikasi dan persyaratan kontrak yang berlaku sebelum memakai hasilnya. ID versi pada data mencatat preset asal, sedangkan batas aktual pada data tetap menjadi masukan hitung karena pengguna dapat menyuntingnya.
- Data contoh dan contoh harga hanya untuk ilustrasi. Harga contoh bukan penawaran atau survei harga terkini.
- Aplikasi tidak memprediksi rutting atau fatigue, dan tidak memakai machine learning untuk memprediksi KAO.
- Penyimpanan browser bersifat lokal pada browser dan perangkat yang dipakai.
- Riwayat SQLite disimpan di sisi server dan dapat dibagikan antar pengguna aplikasi, jadi **jangan mengunggah data rahasia**. Pada layanan hosting sementara, penyimpanan server dapat hilang saat aplikasi dimulai ulang atau di-deploy ulang. Simpan cadangan JSON secara berkala.

## Struktur proyek

| Berkas | Kegunaan |
| --- | --- |
| `app.py` | Konfigurasi dan navigasi Streamlit |
| `kalkulator.py`, `specs.py`, `specs.json` | Memuat dan memvalidasi preset spesifikasi berversi |
| `gradasi.html`, `styles.css`, `app.js` | Struktur, gaya, dan logika kalkulator |
| `compute.py` | Perhitungan gradasi, Marshall, dan KAO bersama |
| `data_tersimpan.py`, `db.py` | Antarmuka dan penyimpanan riwayat desain |
| `perbandingan.py` | Perbandingan dua desain |
| `laporan_pdf.py` | Pembuatan laporan PDF dan Word |
| `DESIGN.md` | Alasan desain, batasan, dan keputusan fitur |
| `theme.py`, `ui.py` | Tema dan pembantu antarmuka |
| `requirements.txt` | Dependensi Python |
