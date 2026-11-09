# Mengapa Aplikasi Ini Dibangun Seperti Ini

## Mengapa kalkulator memakai HTML dan JavaScript di iframe?

Kalkulator perlu memperbarui tabel dan grafik saat pengguna mengubah input.
Optimasi proporsi mencoba banyak kombinasi fraksi; menjalankannya di JavaScript
di dalam halaman menjaga interaksi tetap lokal tanpa meminta Streamlit
menjalankan ulang halaman untuk setiap perubahan. Streamlit tetap menjadi
kerangka navigasi dan halaman laporan/data.

## Mengapa preset spesifikasi disimpan di `specs.json`?

Batas gradasi dan Marshall merupakan data acuan, bukan logika hitung. Satu
berkas berversi membuat sumber batas dan asalnya terlihat, mengurangi duplikasi,
dan memungkinkan penambahan versi tanpa mengubah algoritme. Batas preset tetap
dapat disunting di kalkulator; hasil desain memakai batas yang tersimpan bersama
data, bukan mengganti diam-diam batas desain lama ketika aplikasi diperbarui.
Versi baru hanya boleh ditambahkan setelah memeriksa dokumen spesifikasi
resminya. Tidak ada nilai Bina Marga 2024/2025 yang diasumsikan tersedia.

## Mengapa ada tiga contoh kalkulator?

- **Contoh standar** menunjukkan alur dan hasil hitung memakai data ilustrasi.
- **Template data asli** mengosongkan pengukuran agar pengguna dapat mengisi
  data laboratorium sendiri dan membandingkannya dengan hitungan manual.
- **Skenario uji aneh** memuat input tidak wajar untuk melihat pesan validasi
  dan perilaku kalkulator; ini bukan data yang layak dipakai untuk desain.

Contoh-contoh tersebut bukan hasil pengujian laboratorium. Pengujian otomatis
perhitungan Python berada di `tests/`; contoh di browser tetap berguna untuk
memeriksa alur interaktif.

## Mengapa Pba/Pbe ditampilkan tanpa mengganti VMA?

Pba, Pbe, dan D/B memberi informasi tentang aspal terserap dan bagian pengikat
efektif. Metrik tersebut melengkapi hasil Marshall, tetapi tidak menjadi alasan
untuk mengganti rumus VMA yang digunakan aplikasi: VMA tetap memakai persen
agregat `Ps = 100 − KA`. Mengganti KA dengan Pbe pada rumus VMA akan mengubah
definisi perhitungannya. Rasio D/B 0,6–1,2 hanya ditampilkan sebagai acuan umum,
bukan batas lulus universal; spesifikasi proyek tetap menjadi rujukan.

## Mengapa laporan menghitung ulang data?

Laporan PDF/Word menghitung hasil dari data JSON yang diunggah, bukan
mengandalkan hasil lama yang mungkin sudah tidak sejalan dengan versi kode
terkini. File JSON menyimpan input, batas yang digunakan, dan ID versi preset
untuk membantu menelusuri sumbernya. Karena itu, laporan harus diperiksa
kembali jika algoritme atau data input berubah.

## Mengapa sensitivitas dan prediksi belum disediakan?

Aplikasi belum memiliki data ketidakpastian alat atau hasil pengukuran
berulang yang cukup untuk mengkalibrasi analisis sensitivitas secara statistik.
Margin asumsi saja dapat memberi kesan presisi yang tidak didukung data.
Prediksi rutting/fatigue atau machine learning untuk KAO juga memerlukan model
dan data validasi yang belum tersedia.

## Yang sengaja tidak ditambahkan

- **Prediksi rutting/fatigue**: memerlukan model kinerja yang tervalidasi.
- **Machine learning untuk KAO**: data proyek/laboratorium belum cukup untuk
  melatih dan menguji model yang dapat dipercaya.
- **Integrasi Civil 3D**: berada di luar alur dan lingkungan perangkat lunak
  aplikasi saat ini.
- **Autentikasi**: belum menjadi fitur; riwayat SQLite di server dapat terlihat
  oleh pengguna aplikasi lain. Jangan menyimpan data rahasia di sana.

Batasan ini dapat ditinjau ulang ketika ada kebutuhan, data validasi, dan
persyaratan privasi/operasional yang jelas.
