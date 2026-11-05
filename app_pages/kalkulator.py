from pathlib import Path

import streamlit as st

html_path = Path(__file__).resolve().parents[1] / "gradasi.html"

if not html_path.is_file():
    st.error(f"File kalkulator tidak ditemukan: {html_path}")
    st.stop()

st.iframe(
    html_path,
    height=2400,
    alt="Kalkulator optimasi gradasi agregat",
)
