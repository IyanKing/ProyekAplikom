# Gradasi Agregat

Situs Streamlit untuk kalkulator optimasi gradasi, JMF, dan uji Marshall.

```
app.py              navigasi dan konfigurasi halaman
theme.py            CSS, ilustrasi SVG, dan potongan HTML (tanpa Streamlit)
ui.py               pembantu tampilan
beranda.py          halaman beranda
kalkulator.py       halaman kalkulator
data_tersimpan.py   perpustakaan file JSON data kalkulator
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

Data kalkulator dapat disimpan sebagai JSON dari halaman Kalkulator, lalu
ditinjau atau diunduh ulang melalui halaman Data Tersimpan. Muat berkas JSON
yang sama di Kalkulator untuk memulihkan data gradasi, JMF, dan Marshall;
hasilnya dihitung ulang secara otomatis.
