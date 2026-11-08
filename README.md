# Gradasi Agregat

Situs Streamlit untuk kalkulator optimasi gradasi, JMF, dan uji Marshall.

```
app.py              navigasi dan konfigurasi halaman
theme.py            CSS, ilustrasi SVG, dan potongan HTML (tanpa Streamlit)
ui.py               pembantu tampilan
beranda.py          halaman beranda
kalkulator.py       halaman kalkulator
data_tersimpan.py   perpustakaan file JSON data kalkulator
db.py               penyimpanan riwayat desain SQLite
perbandingan.py     perbandingan dua desain gradasi dan Marshall
laporan_pdf.py      pembuat laporan PDF dan Word dari data kalkulator
cara_kerja.py       halaman panduan
tentang.py          halaman tentang
gradasi.html        kalkulator (HTML + JavaScript), disesuaikan tema saat dimuat
logo.svg            logo aplikasi
.streamlit/config.toml
```

Jalankan: `pip install -r requirements.txt` lalu `streamlit run app.py`.
Butuh Streamlit 1.46 atau lebih baru (navigasi atas). Hapus folder `pages/` lama bila masih ada.
Untuk Streamlit Community Cloud, atur **Main file path** ke `app.py`.

Kalkulator menyediakan pilihan tema terang/gelap, ekspor Excel untuk hasil
gradasi, JMF, dan Marshall, serta unduhan PNG yang merangkum grafik gradasi
dan grafik Marshall yang tersedia.

Di halaman Kalkulator, data dapat disimpan dengan nama di penyimpanan browser
masing-masing, lalu dimuat atau dihapus dari browser tersebut. Data ini tidak
tersinkron ke perangkat lain. Data juga dapat diunduh sebagai JSON untuk
ditinjau atau diunduh ulang melalui halaman Data Tersimpan; muat berkas JSON
yang sama di Kalkulator untuk memulihkan data gradasi, JMF, dan Marshall.
Kalkulator juga dapat menghitung estimasi biaya material per ton campuran
dari harga aspal, agregat kasar, agregat halus, dan filler. Harga disimpan
bersama data kalkulator di browser dan dalam ekspor JSON.

Halaman Data Tersimpan dapat menyimpan unggahan JSON ke riwayat SQLite lokal
(`data/history.db`), lalu menampilkan, mengunduh, mencadangkan, atau menghapus
desain tersebut. Riwayat SQLite berada di server dan dibagikan oleh pengguna
aplikasi; jangan gunakan untuk data rahasia. Penyimpanan lokal Streamlit
Community Cloud dapat hilang saat aplikasi dimulai ulang atau di-deploy ulang,
jadi unduh cadangan secara berkala.

Halaman Laporan menerima file JSON dari Kalkulator, menghitung ulang
gradasi/JMF/Marshall yang tersedia, lalu menyediakan laporan PDF atau Word
(.docx) berisi ringkasan, tabel, grafik, dan kesimpulan. Laporan juga dapat
mengekspor grafik gradasi dan panel Marshall secara terpisah sebagai PNG
(150, 300, atau 600 DPI) atau SVG.

Halaman Perbandingan menerima dua file JSON atau dua desain dari Riwayat
SQLite, lalu menampilkan kurva gradasi, tabel gradasi, selisih persen lolos,
dan hasil Marshall berdampingan. Status dihitung terhadap batas pada tiap
desain; aplikasi tidak memberi verdict pemenang otomatis.
