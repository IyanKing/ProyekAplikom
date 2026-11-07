"""Pembantu tampilan untuk Streamlit."""
import streamlit as st

import theme


def html(markup: str) -> None:
    """Tampilkan HTML sebagai satu blok (tanpa baris kosong yang memutus parser markdown)."""
    st.markdown(theme.squash(markup), unsafe_allow_html=True)


def inject() -> None:
    """Pasang CSS situs. Dipanggil di awal setiap halaman."""
    html(f"<style>{theme.CSS}</style>")
