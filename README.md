# Gradasi Agregat

Situs Streamlit untuk kalkulator optimasi gradasi, JMF, dan uji Marshall.

```
app.py              navigasi dan konfigurasi halaman
theme.py            CSS, ilustrasi SVG, dan potongan HTML (tanpa Streamlit)
ui.py               pembantu tampilan
views/              satu berkas per halaman
gradasi.html        kalkulator (HTML + JavaScript), disesuaikan tema saat dimuat
assets/logo.svg
.streamlit/config.toml
```

Jalankan: `pip install -r requirements.txt` lalu `streamlit run app.py`.
Butuh Streamlit 1.46 atau lebih baru (navigasi atas). Hapus folder `pages/` lama bila masih ada.
