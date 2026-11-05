import streamlit as st

st.set_page_config(
    page_title="Optimasi Gradasi Agregat",
    page_icon="🏗️",
    layout="wide",
)

pages = {
    "Utama": [
        st.Page(
            "app_pages/beranda.py",
            title="Beranda",
            icon=":material/home:",
            default=True,
        ),
        st.Page(
            "app_pages/kalkulator.py",
            title="Kalkulator",
            icon=":material/calculate:",
        ),
    ],
    "Informasi": [
        st.Page(
            "app_pages/cara_kerja.py",
            title="Cara Kerja",
            icon=":material/help:",
        ),
        st.Page(
            "app_pages/tentang.py",
            title="Tentang",
            icon=":material/info:",
        ),
    ],
}

navigation = st.navigation(pages)
navigation.run()