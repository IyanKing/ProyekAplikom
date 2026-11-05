import streamlit as st

st.title("ℹ️ Tentang Aplikasi")
st.caption("Mengenal ProyekAplikom dan modul perhitungannya.")
st.divider()

with st.container(border=True):
    st.subheader("ProyekAplikom")
    st.write(
        "Aplikasi pendukung pembelajaran dan perhitungan untuk optimasi "
        "gradasi agregat. Antarmuka dibuat dengan Streamlit, sementara "
        "kalkulator interaktif dipertahankan dalam satu file HTML."
    )

st.subheader("Modul yang tersedia")
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### 📊 Optimasi gradasi")
        st.write(
            "Mengevaluasi campuran agregat terhadap rentang spesifikasi dan "
            "menampilkan ringkasan hasil dalam grafik serta tabel."
        )
with col2:
    with st.container(border=True):
        st.markdown("### 🧪 JMF dan Marshall")
        st.write(
            "Mendukung perhitungan rancangan campuran dan analisis data uji "
            "Marshall yang dimasukkan pengguna."
        )

st.info(
    "File `gradasi.html` memuat implementasi kalkulator secara utuh. "
    "Halaman ini hanya menampilkan ringkasan dan tidak mengubah logika "
    "perhitungan di dalamnya."
)
