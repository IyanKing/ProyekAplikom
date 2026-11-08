"""Compare two saved or uploaded mixture designs."""

import json
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import db
import theme
import ui
from compute import compute_gradation, compute_marshall


COUNT_FIELDS = (
    ("Gmb", "gmb"),
    ("VIM (%)", "vim"),
    ("VMA (%)", "vma"),
    ("VFA (%)", "vfa"),
    ("Stabilitas (kg)", "st"),
    ("Flow (mm)", "fl"),
    ("MQ (kg/mm)", "mq"),
)


def _number(value):
    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _validate_state(state):
    if not isinstance(state, dict) or not isinstance(state.get("rows"), list):
        raise ValueError("JSON harus berupa objek dengan daftar rows.")
    if not state["rows"] or any(not isinstance(row, dict) for row in state["rows"]):
        raise ValueError("Data harus memiliki baris ayakan berbentuk objek.")

    count = state.get("n")
    if isinstance(count, bool) or not isinstance(count, int) or count not in (2, 3, 4):
        raise ValueError("Jumlah fraksi harus 2, 3, atau 4.")
    proportions = state.get("p")
    if not isinstance(proportions, list) or len(proportions) < count:
        raise ValueError("Proporsi fraksi tidak lengkap.")
    if any(_number(value) is None for value in proportions[:count]):
        raise ValueError("Proporsi fraksi harus berupa angka.")
    numeric_proportions = [_number(value) for value in proportions[:count]]
    if any(value < 0 for value in numeric_proportions):
        raise ValueError("Proporsi fraksi tidak boleh negatif.")
    if sum(numeric_proportions) <= 0:
        raise ValueError("Total proporsi harus lebih besar dari 0%.")
    if not any(
        (sieve := _number(row.get("d"))) is not None and sieve > 0
        for row in state["rows"]
    ):
        raise ValueError("Tidak ada ukuran ayakan positif yang valid.")
    return state


def _read_uploaded_file(uploaded_file):
    try:
        state = json.loads(uploaded_file.getvalue().decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"JSON tidak dapat dibaca: {error}") from error
    return _validate_state(state)


def _format(value, digits=2):
    if value is None:
        return "—"
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _gradation_frame(gradation):
    return pd.DataFrame([
        {
            "Ayakan (mm)": _format(row["d"], 3),
            "Min (%)": _format(row["mn"]),
            "Maks (%)": _format(row["mx"]),
            "Gabungan (%)": _format(row["P"]),
            "Status": (
                "Data tidak lengkap" if row["P"] is None
                else "Memenuhi" if row["ok"]
                else "Di luar batas"
            ),
        }
        for row in gradation["rows"]
    ])


def _marshall_frame(marshall):
    return pd.DataFrame([
        {
            "KA (%)": _format(row["ka"]),
            "n": row["n"],
            **{
                label: _format(row[field], 3 if field == "gmb" else 2)
                for label, field in COUNT_FIELDS
            },
        }
        for row in marshall["A"]
    ])


def _comparison_chart(gradation_a, gradation_b, label_a, label_b):
    figure, axis = plt.subplots(figsize=(10, 5.5))
    for gradation, label, color, marker in (
        (gradation_a, label_a, "#0e6b78", "o"),
        (gradation_b, label_b, "#c8400d", "s"),
    ):
        valid_rows = [row for row in gradation["rows"] if row["P"] is not None]
        if valid_rows:
            axis.plot(
                [row["d"] for row in valid_rows],
                [row["P"] for row in valid_rows],
                color=color,
                marker=marker,
                linewidth=2,
                label=label,
            )
        bounded = [
            row for row in gradation["rows"]
            if row["mn"] is not None and row["mx"] is not None
        ]
        if len(bounded) > 1:
            axis.fill_between(
                [row["d"] for row in bounded],
                [row["mn"] for row in bounded],
                [row["mx"] for row in bounded],
                color=color,
                alpha=0.08,
                label=f"Batas {label}",
            )

    diameters = sorted({
        row["d"] for gradation in (gradation_a, gradation_b)
        for row in gradation["rows"] if row["d"] > 0
    }, reverse=True)
    if diameters:
        axis.set_xscale("log")
        axis.set_xlim(max(diameters), min(diameters))
        axis.set_xticks(diameters, [f"{value:g}" for value in diameters])
    axis.set_ylim(0, 100)
    axis.set_xlabel("Ukuran ayakan (mm, skala log)")
    axis.set_ylabel("% lolos")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend(fontsize=8, loc="best")
    axis.set_title("Perbandingan kurva gradasi")
    figure.tight_layout()
    return figure


def _comparison_delta(gradation_a, gradation_b):
    rows_a = {row["d"]: row for row in gradation_a["rows"]}
    rows_b = {row["d"]: row for row in gradation_b["rows"]}
    aligned_rows = []
    for sieve in sorted(rows_a.keys() | rows_b.keys(), reverse=True):
        row_a = rows_a.get(sieve)
        row_b = rows_b.get(sieve)
        passing_a = row_a["P"] if row_a else None
        passing_b = row_b["P"] if row_b else None
        aligned_rows.append({
            "Ayakan (mm)": _format(sieve, 3),
            "A (%)": _format(passing_a),
            "B (%)": _format(passing_b),
            "Selisih A − B (%)": (
                _format(passing_a - passing_b)
                if passing_a is not None and passing_b is not None
                else "—"
            ),
        })
    return pd.DataFrame(aligned_rows)


def _load_design(label):
    st.subheader(f"Desain {label}")
    source = st.radio(
        f"Sumber Desain {label}",
        ("Unggah JSON", "Riwayat SQLite"),
        horizontal=True,
        key=f"compare_source_{label}",
        label_visibility="collapsed",
    )
    if source == "Unggah JSON":
        uploaded_file = st.file_uploader(
            f"Pilih file JSON — Desain {label}",
            type=["json"],
            key=f"compare_upload_{label}",
        )
        if uploaded_file is None:
            return None, None
        try:
            return _read_uploaded_file(uploaded_file), uploaded_file.name
        except ValueError as error:
            st.error(f"Desain {label}: {error}")
            return None, None

    try:
        designs = db.list_designs()
    except (OSError, sqlite3.Error) as error:
        st.error(f"Riwayat SQLite tidak dapat dibuka: {error}")
        return None, None
    if not designs:
        st.info("Belum ada desain di riwayat. Unggah file JSON atau simpan desain di Data Tersimpan.")
        return None, None

    design_ids = [design["id"] for design in designs]
    selected_id = st.selectbox(
        f"Pilih desain {label}",
        design_ids,
        format_func=lambda design_id: next(
            f"#{design_id} — {design['name']}"
            for design in designs if design["id"] == design_id
        ),
        key=f"compare_history_{label}",
    )
    try:
        selected = db.get_design(selected_id)
        if selected is None:
            st.error(f"Desain {label} sudah tidak ada di riwayat.")
            return None, None
        return _validate_state(selected["payload"]), selected["name"]
    except (OSError, sqlite3.Error, TypeError, ValueError) as error:
        st.error(f"Desain {label} tidak dapat dimuat: {error}")
        return None, None


ui.inject()
ui.html(theme.page_head(
    "Perbandingan desain",
    "Bandingkan kurva gradasi dan hasil Marshall dari dua alternatif campuran.",
    "Analisis desain",
))
st.markdown(
    "Pilih dua file JSON atau desain dari Riwayat SQLite. Data setiap desain "
    "dihitung ulang untuk perbandingan."
)

columns = st.columns(2)
with columns[0]:
    state_a, name_a = _load_design("A")
with columns[1]:
    state_b, name_b = _load_design("B")

if state_a is None or state_b is None:
    st.info("Pilih dua desain yang valid untuk menampilkan perbandingan.")
    st.stop()

try:
    gradation_a = compute_gradation(state_a)
    gradation_b = compute_gradation(state_b)
    marshall_a = compute_marshall(state_a)
    marshall_b = compute_marshall(state_b)
except (ArithmeticError, KeyError, TypeError, ValueError) as error:
    st.error(f"Data desain tidak dapat dihitung: {error}")
    st.stop()

if state_a.get("sp") != state_b.get("sp"):
    st.warning(
        "Desain memakai spesifikasi berbeda "
        f"(A: {state_a.get('sp', '—')}, B: {state_b.get('sp', '—')}). "
        "Status setiap desain dihitung memakai batas spesifikasinya sendiri; "
        "hasil bukan perbandingan langsung terhadap satu batas yang sama."
    )

st.subheader("Kurva gradasi")
st.caption("Kedua kurva ditumpuk agar perbedaan nilai lolos mudah terlihat.")
chart = _comparison_chart(gradation_a, gradation_b, name_a or "Desain A", name_b or "Desain B")
st.pyplot(chart, use_container_width=True)
plt.close(chart)

st.subheader("Gradasi berdampingan")
gradation_columns = st.columns(2)
with gradation_columns[0]:
    st.markdown(f"**Desain A — {name_a}**")
    st.dataframe(_gradation_frame(gradation_a), use_container_width=True, hide_index=True)
with gradation_columns[1]:
    st.markdown(f"**Desain B — {name_b}**")
    st.dataframe(_gradation_frame(gradation_b), use_container_width=True, hide_index=True)

st.markdown("#### Selisih persen lolos")
st.caption("Nilai positif berarti persen lolos Desain A lebih tinggi.")
st.dataframe(
    _comparison_delta(gradation_a, gradation_b),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Hasil Marshall berdampingan")
if marshall_a is None and marshall_b is None:
    st.info("Data Marshall yang cukup untuk dihitung tidak tersedia pada kedua desain.")
elif marshall_a is None or marshall_b is None:
    missing_design = "A" if marshall_a is None else "B"
    st.warning(
        f"Data Marshall Desain {missing_design} tidak lengkap; "
        "tabel Marshall hanya dapat ditampilkan untuk desain lainnya."
    )
    available = marshall_b or marshall_a
    st.dataframe(_marshall_frame(available), use_container_width=True, hide_index=True)
else:
    marshall_columns = st.columns(2)
    with marshall_columns[0]:
        st.markdown(f"**Desain A — {name_a}**")
        st.dataframe(_marshall_frame(marshall_a), use_container_width=True, hide_index=True)
    with marshall_columns[1]:
        st.markdown(f"**Desain B — {name_b}**")
        st.dataframe(_marshall_frame(marshall_b), use_container_width=True, hide_index=True)

st.caption(
    "Perbandingan bersifat informatif. Periksa kesesuaian spesifikasi, "
    "validasi laboratorium, biaya, dan ketersediaan material sebelum memilih desain."
)
