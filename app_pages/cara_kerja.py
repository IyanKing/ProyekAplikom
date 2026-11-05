import streamlit as st

st.title("🛠️ Cara Kerja")
st.caption("Ikuti langkah berikut untuk menyiapkan dan menjalankan analisis.")
st.divider()

steps = [
    (
        "Pilih spesifikasi dan fraksi",
        "Buka Kalkulator, pilih spesifikasi gradasi, lalu tentukan jumlah "
        "fraksi agregat yang akan dicampur.",
    ),
    (
        "Masukkan data saringan",
        "Isi persentase lolos untuk setiap ayakan pada tiap fraksi. Periksa "
        "kembali satuan dan urutan data sebelum menghitung.",
    ),
    (
        "Atur parameter campuran",
        "Tentukan langkah pencarian proporsi dan berat total campuran sesuai "
        "kebutuhan analisis.",
    ),
    (
        "Jalankan optimasi",
        "Pilih tombol Cari proporsi optimal, kemudian tinjau proporsi, grafik, "
        "dan tabel hasil yang ditampilkan.",
    ),
    (
        "Gunakan fitur lanjutan",
        "Pada bagian JMF dan Uji Marshall, masukkan data yang sesuai untuk "
        "melanjutkan perhitungan rancangan campuran dan evaluasi laboratorium.",
    ),
]

for index, (title, description) in enumerate(steps, start=1):
    with st.container(border=True):
        number_col, text_col = st.columns([1, 12])
        with number_col:
            st.markdown(f"## {index:02}")
        with text_col:
            st.markdown(f"### {title}")
            st.write(description)

st.subheader("Sebelum mulai")
with st.container(border=True):
    st.markdown(
        """
- Tombol **Muat contoh** dapat digunakan untuk mencoba alur kalkulator.
- Data contoh hanya ilustrasi, bukan pengganti data analisis atau laboratorium.
- Cocokkan seluruh hasil dengan spesifikasi yang ditetapkan untuk proyek.
"""
    )
    st.page_link(
        "app_pages/kalkulator.py",
        label="Mulai menggunakan kalkulator",
        icon=":material/arrow_forward:",
        use_container_width=True,
    )
