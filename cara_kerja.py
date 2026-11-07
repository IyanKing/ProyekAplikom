import streamlit as st

import theme
import ui

ui.inject()
ui.html(theme.page_head(
    "Cara kerja",
    "Enam langkah dari data saringan sampai hasil yang bisa dilaporkan.",
    "Panduan",
))
ui.html(theme.steps())
ui.html('<div class="gx-sec" style="margin:2.4rem 0 0"></div>')
ui.html(f'<div class="gx-two">{theme.formulas()}{theme.checks()}</div>')

st.write("")
with st.container(key="cta-main"):
    st.page_link("kalkulator.py", label="Buka kalkulator")
