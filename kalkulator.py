import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from specs import load_specifications
import theme
import ui

ui.inject()
ui.html(theme.page_head(
    "Kalkulator",
    "Optimasi gradasi, rancangan campuran (JMF), dan uji Marshall dalam satu halaman.",
    "Alat hitung",
))

BERKAS = Path(__file__).resolve().parent / "gradasi.html"
STYLESHEET = BERKAS.with_name("styles.css")
SCRIPT = BERKAS.with_name("app.js")
SPECS = BERKAS.with_name("specs.json")

missing_files = [
    path for path in (BERKAS, STYLESHEET, SCRIPT, SPECS) if not path.is_file()
]
if missing_files:
    st.error(
        "Berkas kalkulator tidak ditemukan: "
        + ", ".join(f"`{path}`" for path in missing_files)
    )
    st.stop()


try:
    load_specifications(SPECS)
except ValueError as error:
    st.error(f"File spesifikasi tidak valid: {error}")
    st.stop()


@st.cache_data(show_spinner=False)
def muat(versi_berkas: tuple[int, int, int, int]) -> str:
    """Gabungkan template, CSS, dan JavaScript untuk iframe srcdoc Streamlit."""
    html = BERKAS.read_text(encoding="utf-8")
    styles = STYLESHEET.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    specifications = load_specifications(SPECS)
    versi_terbaca = tuple(
        path.stat().st_mtime_ns
        for path in (BERKAS, STYLESHEET, SCRIPT, SPECS)
    )
    if versi_terbaca != versi_berkas:
        raise RuntimeError("Berkas kalkulator berubah saat dimuat; muat ulang halaman.")
    if html.count("<!-- STYLES_PLACEHOLDER -->") != 1:
        raise ValueError("Placeholder stylesheet tidak ditemukan tepat satu kali.")
    if html.count("<!-- APP_SCRIPT_PLACEHOLDER -->") != 1:
        raise ValueError("Placeholder JavaScript tidak ditemukan tepat satu kali.")
    if html.count("<!-- SPECS_PLACEHOLDER -->") != 1:
        raise ValueError("Placeholder spesifikasi tidak ditemukan tepat satu kali.")
    html = html.replace(
        "<!-- STYLES_PLACEHOLDER -->", f"<style>\n{styles}\n</style>", 1
    )
    serialized_specs = json.dumps(
        specifications, ensure_ascii=False, allow_nan=False
    ).replace("<", "\\u003c")
    html = html.replace(
        "<!-- SPECS_PLACEHOLDER -->",
        f'<script id="spec-data" type="application/json">{serialized_specs}</script>',
        1,
    )
    html = html.replace(
        "<!-- APP_SCRIPT_PLACEHOLDER -->", f"<script>\n{script}\n</script>", 1
    )
    return theme.sesuaikan_kalkulator(html)


with st.container(key="calc"):
    # Tinggi awal saja; skrip di dalam halaman menyesuaikannya dengan isi.
    versi = (
        BERKAS.stat().st_mtime_ns,
        STYLESHEET.stat().st_mtime_ns,
        SCRIPT.stat().st_mtime_ns,
        SPECS.stat().st_mtime_ns,
    )
    components.html(muat(versi), height=2400, scrolling=True)
