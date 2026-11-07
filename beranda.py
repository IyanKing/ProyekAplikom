import streamlit as st

import theme
import ui

ui.inject()

kiri, kanan = st.columns([1.05, 1], gap="large", vertical_alignment="center")
with kiri:
    ui.html(theme.hero_text())
    a, b, _ = st.columns([1.25, 1.2, 0.8], gap="small")
    with a, st.container(key="cta-main"):
        st.page_link("kalkulator.py", label="Buka kalkulator")
    with b, st.container(key="cta-alt"):
        st.page_link("cara_kerja.py", label="Lihat cara kerja")
    ui.html(theme.hero_note())
with kanan:
    ui.html(theme.hero_art())

ui.html(theme.section("Apa yang bisa dikerjakan"))
ui.html(theme.cards())

st.write("")
st.write("")
kiri, kanan = st.columns([1.1, 1], gap="large", vertical_alignment="center")
with kiri:
    ui.html(theme.sieve_art())
with kanan:
    ui.html(theme.split_text())
    with st.container(key="split"):
        st.page_link("kalkulator.py", label="Coba dengan data contoh")

ui.html(theme.strip())

ui.html(theme.section("Spesifikasi yang tersedia", rule=True))
ui.html(theme.spec_band())

with st.container(key="band"):
    teks, tombol = st.columns([2, 1], gap="large", vertical_alignment="center")
    with teks:
        ui.html(theme.band_text())
    with tombol:
        st.page_link("kalkulator.py", label="Buka kalkulator")
