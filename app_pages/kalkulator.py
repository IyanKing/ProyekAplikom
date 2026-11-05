from pathlib import Path

import streamlit as st

st.title("🧮 Kalkulator Gradasi")
st.caption(
    "Analisis gradasi agregat, rancangan campuran (JMF), dan uji Marshall."
)
st.divider()

feature_columns = st.columns(3)
features = [
    ("Optimasi gradasi", "Cari proporsi dan lihat evaluasi pada grafik."),
    ("Rancangan campuran", "Hitung kebutuhan bahan untuk JMF."),
    ("Uji Marshall", "Evaluasi data dan rentang kadar aspal optimum."),
]
for column, (title, description) in zip(feature_columns, features):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(description)

st.info(
    "Isi data dengan cermat dan sesuaikan spesifikasi di kalkulator dengan "
    "ketentuan yang digunakan."
)

html_path = Path(__file__).resolve().parents[1] / "gradasi.html"

if not html_path.is_file():
    st.error(f"File kalkulator HTML tidak ditemukan: `{html_path}`")
    st.stop()

st.iframe(
    html_path,
    height=2400,
    alt="Kalkulator interaktif optimasi gradasi agregat",
)
