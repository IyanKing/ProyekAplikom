import streamlit as st

st.title("🏗️ Optimasi Gradasi Agregat")
st.caption("Alat bantu analisis gradasi agregat dan rancangan campuran.")
st.divider()

with st.container(border=True):
    st.subheader("Selamat datang!")
    st.write(
        "Gunakan kalkulator interaktif untuk mengevaluasi gradasi, mencari "
        "proporsi campuran agregat, dan menyiapkan perhitungan campuran."
    )
    st.page_link(
        "app_pages/kalkulator.py",
        label="Buka kalkulator",
        icon=":material/calculate:",
        use_container_width=True,
    )

st.subheader("Jelajahi aplikasi")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🧮 Optimasi gradasi")
        st.write(
            "Cari proporsi fraksi yang memenuhi batas spesifikasi, lalu tinjau "
            "hasil pada grafik dan tabel."
        )

with col2:
    with st.container(border=True):
        st.markdown("### 📋 Rancangan campuran")
        st.write(
            "Hitung kebutuhan agregat berdasarkan target gradasi dan berat "
            "benda uji."
        )

with col3:
    with st.container(border=True):
        st.markdown("### 🧪 Uji Marshall")
        st.write(
            "Masukkan data laboratorium untuk melihat parameter Marshall dan "
            "rentang kadar aspal optimum."
        )

col_help, col_note = st.columns(2)
with col_help:
    st.info(
        "📖 **Butuh panduan?** Buka halaman **Cara Kerja** untuk langkah "
        "penggunaan kalkulator."
    )
with col_note:
    st.warning(
        "Periksa kembali data masukan dan sesuaikan batas spesifikasi dengan "
        "ketentuan proyek atau materi kuliah yang digunakan."
    )
