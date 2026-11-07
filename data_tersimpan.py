import json
from datetime import datetime

import pandas as pd
import streamlit as st

import theme
import ui

ui.inject()
ui.html(theme.page_head(
    "Data tersimpan",
    "Lihat ringkasan, periksa isi, dan unduh kembali data kalkulator dari berkas JSON.",
    "Perpustakaan data",
))

st.markdown(
    """
Unggah berkas **Simpan data (.json)** dari halaman Kalkulator untuk meninjau
data gradasi, pengaturan JMF, dan data Marshall. Berkas dapat dimuat kembali
melalui tombol **Muat data (.json)** pada halaman Kalkulator; hasil hitung
gradasi dan Marshall akan dihitung ulang dari data yang tersimpan.
"""
)

uploaded_files = st.file_uploader(
    "Unggah satu atau beberapa file data (.json)",
    type=["json"],
    accept_multiple_files=True,
)

parsed = []
for index, uploaded_file in enumerate(uploaded_files or []):
    raw = uploaded_file.getvalue()
    try:
        data = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
            raise ValueError("Format harus berupa objek JSON dengan properti rows.")
        if any(not isinstance(row, dict) for row in data["rows"]):
            raise ValueError("Setiap baris ayakan harus berupa objek.")
        parsed.append((index, uploaded_file.name, data, raw))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        st.error(f"{uploaded_file.name}: gagal dibaca ({error})")

if parsed:
    st.success(f"{len(parsed)} file berhasil dibaca.")
    summary = []
    for _, name, data, _ in parsed:
        fractions = data.get("p")
        summary.append({
            "File": name,
            "Spesifikasi": data.get("sp", "—"),
            "Jumlah fraksi": data.get("n", "—"),
            "Jumlah ayakan": len(data["rows"]),
            "Proporsi (%)": ", ".join(map(str, fractions)) if isinstance(fractions, list) and fractions else "—",
            "Ada JMF": isinstance(data.get("jm"), dict),
            "Ada Marshall": isinstance(data.get("mz"), dict) and bool(data["mz"].get("rows")),
        })

    st.subheader("Ringkasan")
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    for index, name, data, raw in parsed:
        with st.expander(f"Detail: {name}"):
            cols = st.columns(3)
            cols[0].metric("Spesifikasi", str(data.get("sp", "—")))
            cols[1].metric("Fraksi", str(data.get("n", "—")))
            cols[2].metric("Ayakan", len(data["rows"]))

            if data["rows"]:
                gradation_rows = []
                fraction_count = data.get("n", 0)
                if not isinstance(fraction_count, int) or isinstance(fraction_count, bool):
                    fraction_count = 0
                for row in data["rows"]:
                    passing = row.get("f")
                    passing = passing if isinstance(passing, list) else []
                    gradation_rows.append({
                        "Ayakan (mm)": row.get("d", ""),
                        "Min": row.get("mn", ""),
                        "Maks": row.get("mx", ""),
                        **{
                            f"Lolos {chr(65 + fraction_index)}": passing[fraction_index]
                            if fraction_index < len(passing) else ""
                            for fraction_index in range(min(max(fraction_count, 0), 4))
                        },
                    })
                st.markdown("**Data gradasi**")
                st.dataframe(pd.DataFrame(gradation_rows), use_container_width=True, hide_index=True)

            if isinstance(data.get("jm"), dict):
                st.markdown("**Pengaturan rancangan campuran (JMF)**")
                st.json(data["jm"])

            marshall = data.get("mz")
            if isinstance(marshall, dict):
                st.markdown("**Data Marshall**")
                st.json({key: value for key, value in marshall.items() if key != "rows"})
                if isinstance(marshall.get("rows"), list) and marshall["rows"]:
                    st.dataframe(pd.DataFrame(marshall["rows"]), use_container_width=True, hide_index=True)

            st.download_button(
                f"Unduh ulang {name}",
                data=raw,
                file_name=name,
                mime="application/json",
                key=f"download_{index}",
            )
else:
    st.info("Belum ada file yang diunggah.")

st.divider()
st.subheader("Template contoh")
st.markdown("Unduh template AC-WC untuk mulai mengisi data gradasi di Kalkulator.")

template = {
    "sp": "AC-WC",
    "n": 3,
    "rows": [
        {"d": "19", "mn": "100", "mx": "100", "f": ["100", "100", "100", ""]},
        {"d": "12.5", "mn": "90", "mx": "100", "f": ["95", "100", "100", ""]},
        {"d": "9.5", "mn": "77", "mx": "90", "f": ["82", "95", "100", ""]},
        {"d": "4.75", "mn": "53", "mx": "69", "f": ["60", "70", "80", ""]},
        {"d": "2.36", "mn": "33", "mx": "53", "f": ["40", "50", "60", ""]},
        {"d": "0.075", "mn": "4", "mx": "9", "f": ["6", "6", "6", ""]},
    ],
    "p": ["35", "35", "30"],
}
st.download_button(
    "Unduh template AC-WC.json",
    data=json.dumps(template, ensure_ascii=False, indent=2),
    file_name=f"template-ac-wc-{datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json",
)
