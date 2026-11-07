from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import theme
import ui

ui.inject()
ui.html(theme.page_head(
    "Kalkulator",
    "Optimasi gradasi, rancangan campuran (JMF), dan uji Marshall dalam satu halaman.",
    "Alat hitung",
))

BERKAS = Path(__file__).resolve().parent / "gradasi.html"

if not BERKAS.is_file():
    st.error(f"Berkas kalkulator tidak ditemukan: `{BERKAS}`")
    st.stop()


@st.cache_data(show_spinner=False)
def muat(terakhir_diubah: float) -> str:
    """Baca gradasi.html lalu selaraskan dengan tema situs. Cache dibuang bila berkas berubah."""
    return theme.sesuaikan_kalkulator(BERKAS.read_text(encoding="utf-8"))


with st.container(key="calc"):
    # Tinggi awal saja; skrip di dalam halaman menyesuaikannya dengan isi.
    components.html(muat(BERKAS.stat().st_mtime), height=2400, scrolling=True)
