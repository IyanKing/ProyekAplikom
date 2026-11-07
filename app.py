"""Titik masuk aplikasi: konfigurasi halaman dan navigasi atas.

Jalankan dengan:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Gradasi Agregat",
    page_icon=":material/grain:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.logo(str(Path(__file__).parent / "logo.svg"), size="large")

halaman = [
    st.Page("beranda.py", title="Beranda", default=True),
    st.Page("kalkulator.py", title="Kalkulator", url_path="kalkulator"),
    st.Page("cara_kerja.py", title="Cara Kerja", url_path="cara-kerja"),
    st.Page("tentang.py", title="Tentang", url_path="tentang"),
]
st.navigation(halaman, position="top").run()
