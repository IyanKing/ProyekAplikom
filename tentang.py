import theme
import ui

# Isi bila ingin menampilkan nama pengembang atau kelompok di halaman ini.
PENGEMBANG = ""

ui.inject()
ui.html(theme.page_head(
    "Tentang aplikasi",
    "Alat bantu komputasi untuk perancangan campuran beraspal.",
    "ProyekAplikom",
))
ui.html(theme.about(PENGEMBANG))
