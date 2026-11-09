from html import escape
import json
from datetime import datetime
from pathlib import Path
import re
import sqlite3

import altair as alt
import pandas as pd
import streamlit as st

import db
import theme
import ui
from compute import compute_effective_asphalt, compute_gradation
from specs import load_specifications, specification_version_name

ui.inject()
SPECIFICATIONS = load_specifications()

if "data_tersimpan_mode" not in st.session_state:
    st.session_state.data_tersimpan_mode = "dark"

palette = {
    "dark": {
        "background": "#1b1815",
        "panel": "#251d16",
        "panel_alt": "#2f241b",
        "text": "#f1e8dc",
        "muted": "#b8a995",
        "line": "#51402e",
        "accent": "#e9b873",
        "grid": "#49392a",
        "header": "rgba(27,24,21,.84)",
        "series": ["#e9b873", "#71c1ce", "#f28d65", "#b3d58c", "#c5a0e8", "#f0d26f"],
    },
    "light": {
        "background": "#f4efe7",
        "panel": "#fffaf2",
        "panel_alt": "#f3eadc",
        "text": "#30251b",
        "muted": "#746659",
        "line": "#dfd1bd",
        "accent": "#9a6429",
        "grid": "#e6dac8",
        "header": "rgba(255,250,242,.92)",
        "series": ["#8d5b20", "#167c8c", "#b54a30", "#547d32", "#74509a", "#977100"],
    },
}
colors = palette[st.session_state.data_tersimpan_mode]

st.markdown(
    f"""
<style>
:root{{--bg:{colors["background"]};--panel:{colors["panel"]};--panel2:{colors["panel_alt"]};
--line:{colors["line"]};--gold:{colors["accent"]};--tan:{colors["accent"]};
--cream:{colors["panel_alt"]};--ink:{colors["text"]};--tx:{colors["text"]};--mu:{colors["muted"]}}}
.stApp{{background:radial-gradient(900px 480px at 88% -6%,rgba(201,138,58,.15),transparent 62%),var(--bg)}}
[data-testid="stAppViewContainer"]{{background:transparent}}
[data-testid="stHeader"]{{background:{colors["header"]};backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
.stApp,[data-testid="stMarkdownContainer"],[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"]{{color:var(--tx)}}
[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4,
[data-testid="stSubheader"]{{color:var(--tan)!important;line-height:1.35!important;overflow-wrap:anywhere}}
[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4{{margin-top:1.15rem!important;margin-bottom:.65rem!important}}
[data-testid="stAlert"]{{background:var(--panel)!important;color:var(--tx)!important;border:1px solid var(--line)}}
[data-testid="stAlert"] *{{color:var(--tx)!important;line-height:1.5}}
[data-testid="stAlert"] svg{{color:var(--gold)!important;fill:var(--gold)!important}}
[data-testid="stFileUploaderDropzone"]{{
 min-height:112px!important;padding:1rem 1.15rem!important;background:var(--panel)!important;
 border:1px dashed var(--line)!important;border-radius:16px!important
}}
[data-testid="stFileUploaderDropzoneInstructions"]{{
 min-width:0;color:var(--tx)!important;line-height:1.5!important;white-space:normal!important
}}
[data-testid="stFileUploaderDropzoneInstructions"] *{{
 color:var(--tx)!important;line-height:1.5!important;white-space:normal!important;
 overflow-wrap:anywhere!important
}}
[data-testid="stFileUploader"] small,[data-testid="stFileUploader"] span{{color:var(--mu)}}
[data-testid="stFileUploader"] button,[data-testid="stDownloadButton"] button,[data-testid="stButton"] button{{
 min-height:2.5rem;background:var(--panel2);color:var(--tx);border:1px solid var(--line);border-radius:999px;
 line-height:1.35;white-space:normal
}}
[data-testid="stFileUploader"] button:hover,[data-testid="stDownloadButton"] button:hover,[data-testid="stButton"] button:hover{{
 border-color:var(--gold);color:var(--gold)
}}
[data-testid="stExpander"]{{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden}}
[data-testid="stExpander"] summary{{
 display:flex!important;align-items:center!important;gap:.7rem!important;min-height:3rem;padding:.8rem 1rem!important;
 color:var(--tx)!important;line-height:1.45!important;white-space:normal!important
}}
[data-testid="stExpander"] summary *{{
 margin:0!important;color:var(--tx)!important;line-height:1.45!important;
 white-space:normal!important;overflow-wrap:anywhere!important
}}
[data-testid="stExpander"] summary svg{{flex:0 0 auto;color:var(--gold)!important}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{{padding:.5rem 1rem 1rem}}
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h3{{font-size:1.15rem!important}}
[data-testid="stMetric"]{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px}}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"],[data-testid="stMetricDelta"]{{color:var(--tx)}}
.gx-empty-state{{display:flex;align-items:flex-start;gap:.75rem;margin:.5rem 0 1rem;padding:1rem 1.1rem;
 background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:12px;
 color:var(--tx);line-height:1.55}}
.gx-empty-state p{{margin:0;color:var(--tx)}}
.gx-empty-state .gx-empty-icon{{color:var(--gold);font-size:1.2rem;line-height:1.2}}
.gx-data-table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:.35rem 0 1rem}}
.gx-data-table{{width:100%;border-collapse:collapse;color:var(--tx);font-size:.92rem}}
.gx-data-table th{{background:var(--panel2);color:var(--gold);font-weight:600;text-align:left;white-space:nowrap}}
.gx-data-table td,.gx-data-table th{{padding:.62rem .8rem;border-bottom:1px solid var(--line)}}
.gx-data-table tr:last-child td{{border-bottom:0}}
.gx-data-table tbody tr:nth-child(even){{background:color-mix(in srgb,var(--panel-alt) 42%,transparent)}}
.gx-theme-switch{{display:flex;justify-content:flex-end;margin-bottom:.3rem}}
@media(max-width:640px){{
 [data-testid="stFileUploaderDropzone"]{{min-height:0!important;padding:.85rem!important}}
 [data-testid="stExpander"] summary{{align-items:flex-start!important}}
 .gx-data-table{{font-size:.82rem}}.gx-data-table td,.gx-data-table th{{padding:.5rem .6rem}}
}}
</style>
""",
    unsafe_allow_html=True,
)

switch_col, _ = st.columns([1, 5])
with switch_col:
    next_mode = "light" if st.session_state.data_tersimpan_mode == "dark" else "dark"
    switch_label = "☀️ Mode terang" if next_mode == "light" else "🌙 Mode gelap"
    if st.button(switch_label, key="data_tersimpan_toggle"):
        st.session_state.data_tersimpan_mode = next_mode
        st.rerun()

ui.html(theme.page_head(
    "Data tersimpan",
    "Tinjau berkas JSON dan simpan desain ke riwayat proyek di server.",
    "Perpustakaan data",
))
st.markdown(
    """
Unggah berkas **Unduh JSON** dari halaman Kalkulator untuk meninjau atau
menyimpannya ke riwayat proyek SQLite. Desain di riwayat dapat diunduh kembali
untuk dimuat di Kalkulator.
"""
)
with st.expander("Penting tentang privasi dan ketahanan data"):
    st.warning(
        "Riwayat ini disimpan bersama di server aplikasi: pengguna lain yang "
        "dapat membuka halaman ini juga dapat melihat, mengunduh, atau menghapus "
        "desain. Jangan simpan data rahasia. Di Streamlit Community Cloud, "
        "file SQLite dapat hilang saat aplikasi dimulai ulang atau di-deploy ulang; "
        "unduh cadangan secara berkala."
    )

with st.container(key="saved_file_upload"):
    st.markdown("**Unggah satu atau beberapa file data (.json)**")
    uploaded_files = st.file_uploader(
        "Pilih file JSON",
        type=["json"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )


def _show_table(frame):
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    body = []
    for row in frame.itertuples(index=False, name=None):
        cells = []
        for value in row:
            if value is None or pd.isna(value):
                rendered = "—"
            elif isinstance(value, bool):
                rendered = "Ya" if value else "Tidak"
            elif isinstance(value, (int, float)):
                rendered = _format(value, 3)
            else:
                rendered = str(value)
            cells.append(f"<td>{escape(rendered)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    ui.html(
        '<div class="gx-data-table-wrap"><table class="gx-data-table">'
        f"<thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody>"
        "</table></div>"
    )


def _show_line_chart(frame, x_field, y_fields, height=280, y_label=None):
    chart_data = frame.copy()
    chart_data[x_field] = chart_data[x_field].astype(str)
    if y_label is None:
        y_label = "% lolos" if x_field == "Ayakan (mm)" else y_fields[0]
    chart = (
        alt.Chart(chart_data)
        .transform_fold(y_fields, as_=["Seri", "Nilai"])
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=48), strokeWidth=2.5)
        .encode(
            x=alt.X(f"{x_field}:O", sort=None, title=x_field),
            y=alt.Y("Nilai:Q", title=y_label),
            color=alt.Color(
                "Seri:N",
                scale=alt.Scale(range=colors["series"]),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip(f"{x_field}:O", title=x_field),
                alt.Tooltip("Seri:N", title="Seri"),
                alt.Tooltip("Nilai:Q", format=".2f"),
            ],
        )
        .properties(height=height)
        .configure(
            background=colors["panel"],
            axis=alt.AxisConfig(
                labelColor=colors["muted"],
                titleColor=colors["text"],
                gridColor=colors["grid"],
                domainColor=colors["line"],
                tickColor=colors["line"],
            ),
            legend=alt.LegendConfig(labelColor=colors["text"], titleColor=colors["text"]),
            view=alt.ViewConfig(stroke=colors["line"]),
        )
    )
    st.altair_chart(chart, width="stretch")


def _number(value):
    if isinstance(value, bool) or value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if pd.notna(number) else None


def _format(value, digits=2):
    number = _number(value)
    if number is None:
        return "—"
    return f"{number:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _gradation_rows(data):
    count = data.get("n")
    if not isinstance(count, int) or isinstance(count, bool):
        count = 0
    count = min(max(count, 0), 4)
    result = []
    for row in data["rows"]:
        passing = row.get("f")
        passing = passing if isinstance(passing, list) else []
        result.append({
            "Ayakan (mm)": _number(row.get("d")),
            "Min (%)": _number(row.get("mn")),
            "Maks (%)": _number(row.get("mx")),
            **{
                f"Fraksi {chr(65 + index)} (%)": _number(passing[index])
                if index < len(passing) else None
                for index in range(count)
            },
        })
    return result


def _jmf_results(data, config):
    rows = []
    for row in data["rows"]:
        sieve = _number(row.get("d"))
        minimum = _number(row.get("mn"))
        maximum = _number(row.get("mx"))
        if sieve is None or sieve <= 0:
            continue
        passing = None
        if config.get("tg") == "blend":
            fractions = row.get("f")
            proportions = data.get("p")
            count = data.get("n")
            if (
                isinstance(fractions, list)
                and isinstance(proportions, list)
                and isinstance(count, int)
                and not isinstance(count, bool)
                and 0 < count <= 4
                and len(fractions) >= count
                and len(proportions) >= count
            ):
                values = [_number(fractions[i]) for i in range(count)]
                weights = [_number(proportions[i]) for i in range(count)]
                if all(value is not None for value in values + weights) and sum(weights) > 0:
                    passing = sum(value * weight for value, weight in zip(values, weights)) / sum(weights)
        elif minimum is not None and maximum is not None:
            passing = (minimum + maximum) / 2
        if passing is not None:
            rows.append({"Ayakan (mm)": sieve, "Min (%)": minimum, "Target (%)": passing, "Maks (%)": maximum})

    rows.sort(key=lambda row: row["Ayakan (mm)"], reverse=True)
    if not rows:
        return None

    retained = []
    previous = 100.0
    for row in rows:
        retained.append(previous - row["Target (%)"])
        previous = row["Target (%)"]
    pan = previous
    coarse = sum(amount for row, amount in zip(rows, retained) if row["Ayakan (mm)"] >= 4.75)
    fine = sum(amount for row, amount in zip(rows, retained) if row["Ayakan (mm)"] < 4.75)
    constant = _number(config.get("k"))
    if constant is None:
        return None
    binder = 0.035 * coarse + 0.045 * fine + 0.18 * pan + constant
    total_weight = _number(config.get("bt"))
    selected_group = str(config.get("kg", "2"))
    selected_binder = _number(config.get("ka"))
    group_binders = {1: 5.0, 2: 5.5, 3: 6.0, 4: 6.5}
    components = []
    for group, default_binder in group_binders.items():
        binder_percent = selected_binder if str(group) == selected_group and selected_binder is not None else default_binder
        aggregate_weight = total_weight * (100 - binder_percent) / 100 if total_weight is not None else None
        components.append({
            "Kelompok": f"Kelompok {group}",
            "Kadar aspal (%)": binder_percent,
            "Berat aspal (g)": total_weight * binder_percent / 100 if total_weight is not None else None,
            "Berat agregat (g)": aggregate_weight,
        })
        for row, amount in zip(rows, retained):
            row[f"Berat agregat K{group} (g)"] = (
                amount * aggregate_weight / 100 if aggregate_weight is not None else None
            )
    pan_row = {"Ayakan (mm)": "Pan", "Min (%)": None, "Target (%)": None, "Maks (%)": None}
    for component in components:
        group = int(component["Kelompok"].split()[-1])
        aggregate_weight = component["Berat agregat (g)"]
        pan_row[f"Berat agregat K{group} (g)"] = (
            pan * aggregate_weight / 100 if aggregate_weight is not None else None
        )
    rows.append(pan_row)

    return {
        "rows": rows,
        "components": components,
        "coarse": coarse,
        "fine": fine,
        "filler": pan,
        "binder_formula": binder,
        "binder_rounded": round(binder * 2) / 2,
    }


def _marshall_results(marshall, p200=None):
    specific_gravity = marshall.get("g")
    if not isinstance(specific_gravity, dict):
        specific_gravity = {}
    bulk = _number(specific_gravity.get("gsb"))
    effective = _number(specific_gravity.get("gse"))
    asphalt = _number(specific_gravity.get("gb"))
    multiplier = _number(specific_gravity.get("pg")) or 1
    if not (bulk and effective and asphalt and bulk > 0 and effective > 0 and asphalt > 0):
        return []
    results = []
    raw_rows = marshall.get("rows")
    if not isinstance(raw_rows, list):
        return results

    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        values = {key: _number(row.get(key)) for key in ("ka", "a", "b", "c", "st", "fl")}
        ka, dry, ssd, immersed = values["ka"], values["a"], values["b"], values["c"]
        if (
            ka is None or not 0 <= ka < 100
            or dry is None or dry <= 0
            or ssd is None or immersed is None or ssd <= immersed
        ):
            continue
        gmb = dry / (ssd - immersed)
        gmm = None
        if effective and asphalt and (100 - ka) / effective + ka / asphalt != 0:
            gmm = 100 / ((100 - ka) / effective + ka / asphalt)
        vim = 100 * (gmm - gmb) / gmm if gmm else None
        vma = 100 - gmb * (100 - ka) / bulk if bulk else None
        vfa = 100 * (vma - vim) / vma if vma else None
        stability = values["st"] * multiplier if values["st"] is not None else None
        flow = values["fl"]
        effective_asphalt = compute_effective_asphalt(
            bulk, effective, asphalt, ka, p200
        )
        results.append({
            "KA (%)": ka,
            "Berat kering (g)": dry,
            "Berat SSD (g)": ssd,
            "Berat dalam air (g)": immersed,
            "Gmb": gmb,
            "Gmm": gmm,
            "VIM (%)": vim,
            "VMA (%)": vma,
            "VFA (%)": vfa,
            "Stabilitas (kg)": stability,
            "Flow (mm)": flow,
            "MQ (kg/mm)": stability / flow if stability is not None and flow else None,
            "Pba (%)": effective_asphalt["pba"] if effective_asphalt else None,
            "Pbe (%)": effective_asphalt["pbe"] if effective_asphalt else None,
            "P200 (%)": effective_asphalt["p200"] if effective_asphalt else None,
            "D/B": effective_asphalt["db_ratio"] if effective_asphalt else None,
        })
    return results


def _show_marshall(marshall, data):
    st.markdown("#### Pengaturan dan batas Marshall")
    specification_names = {
        "AC-WC": "AC-WC",
        "AC-BC": "AC-BC",
        "AC-Base": "AC-Base",
        "Kustom": "Kustom",
    }
    spec = marshall.get("sp", "AC-WC")
    st.caption(f"Spesifikasi: **{specification_names.get(spec, spec)}**")
    version_id = data.get("spec_version")
    st.caption(
        "Preset versi: "
        + (
            specification_version_name(SPECIFICATIONS, version_id)
            if version_id else "tidak dicatat (data lama)"
        )
        + ". Batas pada file tetap menjadi sumber perhitungan."
    )

    gravity = marshall.get("g")
    if not isinstance(gravity, dict):
        gravity = {}
    bulk = _number(gravity.get("gsb"))
    effective = _number(gravity.get("gse"))
    if bulk is not None and effective is not None and effective < bulk:
        st.warning(
            "Gse lebih kecil dari Gsb; Pba/Pbe dan rasio D/B tidak dapat dihitung."
        )
    gravity_labels = {
        "gsb": "BJ bulk agregat (Gsb)",
        "gse": "BJ efektif agregat (Gse)",
        "gb": "BJ aspal (Gb)",
        "pg": "Pengali stabilitas",
    }
    _show_table(pd.DataFrame([
        {"Parameter": label, "Nilai": gravity.get(field, "—")}
        for field, label in gravity_labels.items()
    ]))

    limits = marshall.get("lim")
    if isinstance(limits, dict) and limits:
        limit_labels = {
            "vi1": ("VIM minimum", "%"),
            "vi2": ("VIM maksimum", "%"),
            "vma": ("VMA minimum", "%"),
            "vfa": ("VFA minimum", "%"),
            "st": ("Stabilitas minimum", "kg"),
            "fl1": ("Flow minimum", "mm"),
            "fl2": ("Flow maksimum", "mm"),
            "mq": ("MQ minimum", "kg/mm"),
        }
        _show_table(pd.DataFrame([
            {"Batas": label, "Nilai": limits.get(field, "—"), "Satuan": unit}
            for field, (label, unit) in limit_labels.items()
            if field in limits
        ]))

    sample_rows = marshall.get("rows")
    sample_rows = sample_rows if isinstance(sample_rows, list) else []
    labels = {
        "ka": "KA (%)",
        "a": "Berat kering (g)",
        "b": "Berat SSD (g)",
        "c": "Berat dalam air (g)",
        "st": "Stabilitas (baca)",
        "fl": "Flow (mm)",
    }
    raw_table = [
        {label: row.get(field, "") for field, label in labels.items()}
        for row in sample_rows if isinstance(row, dict)
    ]
    st.markdown("#### Data benda uji")
    if raw_table:
        _show_table(pd.DataFrame(raw_table))
    else:
        st.info("Belum ada data benda uji Marshall pada berkas ini.")

    gradation = None
    gradation_error = None
    try:
        gradation = compute_gradation(data)
    except (KeyError, TypeError, ValueError) as error:
        gradation_error = error
    p200 = None
    if gradation:
        p200_row = next(
            (
                row for row in gradation["rows"]
                if abs(row["d"] - 0.075) < 0.001
            ),
            None,
        )
        p200 = p200_row["P"] if p200_row else None
    results = _marshall_results(marshall, p200)
    if not results:
        st.info("Hasil Marshall belum dapat dihitung. Lengkapi data benda uji dan nilai Gsb, Gse, serta Gb.")
        return

    st.markdown("#### Hasil perhitungan Marshall")
    _show_table(pd.DataFrame(results))
    st.caption(
        "Pba = 100·(Gse−Gsb)/(Gse·Gsb)·Gb; "
        "Pbe = Pb−(Pba/100)·Ps; D/B = P200/Pbe. "
        "Rujukan perancangan: Asphalt Institute MS-2. "
        "D/B 0,6–1,2 adalah acuan umum, bukan batas otomatis."
    )
    if p200 is None:
        if gradation_error is not None:
            st.warning(f"Gradasi gabungan tidak dapat dihitung untuk P200: {gradation_error}")
        else:
            st.warning(
                "P200 tidak tersedia dari gradasi gabungan; D/B tidak dapat dihitung. "
                "Pastikan ayakan 0,075 mm tersedia."
            )
    average_columns = [
        "Gmb", "VIM (%)", "VMA (%)", "VFA (%)",
        "Pba (%)", "Pbe (%)", "P200 (%)", "D/B",
        "Stabilitas (kg)", "Flow (mm)", "MQ (kg/mm)",
    ]
    averages = pd.DataFrame(results).groupby("KA (%)", as_index=False)[average_columns].mean().sort_values("KA (%)")
    if averages["KA (%)"].nunique() > 1:
        st.markdown("#### Grafik hasil Marshall")
        chart_specs = [
            ("VIM (%)", "VIM (%)"),
            ("VMA (%)", "VMA (%)"),
            ("VFA (%)", "VFA (%)"),
            ("Stabilitas (kg)", "Stabilitas (kg)"),
            ("Flow (mm)", "Flow (mm)"),
            ("MQ (kg/mm)", "MQ (kg/mm)"),
        ]
        for start in range(0, len(chart_specs), 2):
            columns = st.columns(2)
            for column, (field, label) in zip(columns, chart_specs[start:start + 2]):
                with column:
                    st.caption(label)
                    _show_line_chart(
                        averages[["KA (%)", field]],
                        "KA (%)",
                        [field],
                        height=230,
                        y_label=label,
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
        if "spec_version" in data and not isinstance(data["spec_version"], str):
            raise ValueError("Versi spesifikasi harus berupa teks.")
        parsed.append((index, uploaded_file.name, data, raw))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        st.error(f"{uploaded_file.name}: gagal dibaca ({error})")

if parsed:
    st.success(f"{len(parsed)} file berhasil dibaca.")
    st.subheader("Simpan desain ke riwayat")
    selected_upload = st.selectbox(
        "Pilih file yang akan disimpan",
        range(len(parsed)),
        format_func=lambda index: parsed[index][1],
        key="history_upload_selection",
    )
    _, upload_name, upload_data, _ = parsed[selected_upload]
    with st.form("save_design_to_history"):
        design_name = st.text_input(
            "Nama desain",
            value=Path(upload_name).stem[:100],
            max_chars=100,
        )
        design_notes = st.text_area(
            "Catatan (opsional)",
            max_chars=2000,
            placeholder="Misalnya: sumber agregat atau catatan revisi.",
        )
        save_submitted = st.form_submit_button(
            "Simpan ke riwayat",
            type="primary",
        )
    if save_submitted:
        try:
            new_id = db.save_design(design_name, upload_data, design_notes)
        except (OSError, sqlite3.Error, TypeError, ValueError) as error:
            st.error(f"Desain tidak dapat disimpan: {error}")
        else:
            st.success(f"Desain berhasil disimpan dengan ID #{new_id}.")

try:
    db.init_db()
    history = db.list_designs()
except (OSError, sqlite3.Error) as error:
    history = []
    st.error(f"Riwayat SQLite tidak dapat dibuka: {error}")

st.subheader("Riwayat desain")
if not history:
    st.info("Belum ada desain di riwayat. Unggah file JSON di atas lalu simpan.")
else:
    history_table = pd.DataFrame([
        {
            "ID": design["id"],
            "Nama": design["name"],
            "Spesifikasi": design["spec"] or "—",
            "Fraksi": design["num_fractions"] or "—",
            "Ayakan": design["num_sieves"],
            "Dibuat (UTC)": design["created_at"],
            "Catatan": design["notes"] or "—",
        }
        for design in history
    ])
    _show_table(history_table)

    backup = []
    try:
        for design in history:
            stored = db.get_design(design["id"])
            if stored is None:
                continue
            backup.append({
                "id": stored["id"],
                "name": stored["name"],
                "created_at": stored["created_at"],
                "notes": stored["notes"],
                "payload": stored["payload"],
            })
    except (OSError, sqlite3.Error, ValueError) as error:
        st.error(f"Cadangan riwayat tidak dapat disiapkan: {error}")
    else:
        st.download_button(
            "Unduh cadangan semua desain",
            data=json.dumps(backup, ensure_ascii=False, indent=2),
            file_name=f"cadangan-desain-{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            disabled=not backup,
            key="download_design_backup",
        )

    selected_design_id = st.selectbox(
        "Pilih desain dari riwayat",
        [design["id"] for design in history],
        format_func=lambda design_id: (
            f"#{design_id} — "
            f"{next(item['name'] for item in history if item['id'] == design_id)}"
        ),
        key="history_design_selection",
    )
    try:
        selected_design = db.get_design(selected_design_id)
    except (OSError, sqlite3.Error, ValueError) as error:
        selected_design = None
        st.error(f"Desain tidak dapat dibaca: {error}")

    if selected_design is not None:
        safe_name = re.sub(
            r"[^A-Za-z0-9._-]+", "-", selected_design["name"]
        ).strip(".-") or "desain"
        history_columns = st.columns(2)
        with history_columns[0]:
            st.download_button(
                "Unduh desain JSON",
                data=json.dumps(
                    selected_design["payload"], ensure_ascii=False, indent=2
                ),
                file_name=f"{safe_name}.json",
                mime="application/json",
                key=f"download_design_{selected_design_id}",
            )
        with history_columns[1]:
            confirm_delete = st.checkbox(
                "Saya yakin ingin menghapus desain ini",
                key=f"confirm_delete_design_{selected_design_id}",
            )
            if st.button(
                "Hapus desain",
                disabled=not confirm_delete,
                key=f"delete_design_{selected_design_id}",
            ):
                try:
                    deleted = db.delete_design(selected_design_id)
                except (OSError, sqlite3.Error) as error:
                    st.error(f"Desain tidak dapat dihapus: {error}")
                else:
                    if deleted:
                        st.success("Desain berhasil dihapus.")
                        st.rerun()
                    else:
                        st.warning("Desain sudah tidak ada di riwayat.")

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
    _show_table(pd.DataFrame(summary))

    for index, name, data, raw in parsed:
        with st.expander(f"Detail: {name}"):
            cols = st.columns(3)
            cols[0].metric("Spesifikasi", str(data.get("sp", "—")))
            cols[1].metric("Fraksi", str(data.get("n", "—")))
            cols[2].metric("Ayakan", len(data["rows"]))

            if data["rows"]:
                st.subheader("Data gradasi")
                gradation = _gradation_rows(data)
                _show_table(pd.DataFrame(gradation))
                count_value = data.get("n", 0)
                count = (
                    min(max(count_value, 0), 4)
                    if isinstance(count_value, int) and not isinstance(count_value, bool)
                    else 0
                )
                sieve_rows = [
                    row for row in data["rows"]
                    if _number(row.get("d")) is not None and _number(row.get("d")) > 0
                ]
                if sieve_rows:
                    sieve_rows.sort(key=lambda row: _number(row.get("d")), reverse=True)
                    chart_data = pd.DataFrame({
                        "Ayakan (mm)": [str(row.get("d", "")) for row in sieve_rows],
                        "Batas minimum": [_number(row.get("mn")) for row in sieve_rows],
                        "Batas maksimum": [_number(row.get("mx")) for row in sieve_rows],
                    })
                    proportions = data.get("p")
                    for fraction_index in range(count):
                        chart_data[f"Fraksi {chr(65 + fraction_index)}"] = [
                            _number(row["f"][fraction_index])
                            if isinstance(row.get("f"), list) and len(row["f"]) > fraction_index else None
                            for row in sieve_rows
                        ]
                    if (
                        isinstance(proportions, list)
                        and len(proportions) >= count
                        and count
                        and all(_number(proportions[i]) is not None for i in range(count))
                        and sum(_number(proportions[i]) for i in range(count)) > 0
                    ):
                        weights = [_number(proportions[i]) for i in range(count)]
                        chart_data["Campuran"] = [
                            sum(
                                _number(row["f"][fraction_index]) * weights[fraction_index]
                                for fraction_index in range(count)
                            ) / sum(weights)
                            if isinstance(row.get("f"), list)
                            and len(row["f"]) >= count
                            and all(_number(value) is not None for value in row["f"][:count])
                            else None
                            for row in sieve_rows
                        ]
                    series = list(chart_data.columns[1:])
                    if chart_data[series].notna().any().any():
                        st.markdown("#### Grafik gradasi")
                        _show_line_chart(chart_data, "Ayakan (mm)", series, height=300)

            config = data.get("jm")
            if isinstance(config, dict):
                st.subheader("Pengaturan rancangan campuran (JMF)")
                target_labels = {"mid": "Nilai tengah spesifikasi", "blend": "Campuran fraksi"}
                setting_rows = [
                    ("Kelompok", f"Kelompok {config.get('kg', '2')}"),
                    ("Kadar aspal (%)", config.get("ka", "—")),
                    ("Konstanta K", config.get("k", "—")),
                    ("Berat benda uji (g)", config.get("bt", "—")),
                    ("Target gradasi", target_labels.get(config.get("tg"), config.get("tg", "—"))),
                ]
                _show_table(pd.DataFrame([
                    {"Pengaturan": label, "Nilai": value}
                    for label, value in setting_rows
                ]))
                jmf = _jmf_results(data, config)
                if jmf:
                    jmf_cols = st.columns(4)
                    jmf_cols[0].metric("Pb (rumus)", f"{_format(jmf['binder_formula'])}%")
                    jmf_cols[1].metric("Pembulatan 0,5%", f"{_format(jmf['binder_rounded'])}%")
                    jmf_cols[2].metric("%CA / %FA", f"{_format(jmf['coarse'])} / {_format(jmf['fine'])}")
                    jmf_cols[3].metric("%Filler", f"{_format(jmf['filler'])}%")
                    st.markdown("#### Rincian gradasi dan berat JMF")
                    jmf_table = pd.DataFrame(jmf["rows"])
                    jmf_table["Ayakan (mm)"] = jmf_table["Ayakan (mm)"].map(
                        lambda value: "Pan" if value == "Pan" else _format(value, 3)
                    )
                    _show_table(jmf_table)
                    st.markdown("#### Berat tiap kelompok")
                    _show_table(pd.DataFrame(jmf["components"]))
                else:
                    st.info("Rincian JMF belum dapat dihitung. Periksa target gradasi, ayakan, dan pengaturan JMF.")

            marshall = data.get("mz")
            if isinstance(marshall, dict):
                st.subheader("Data Marshall")
                _show_marshall(marshall, data)

            st.download_button(
                f"Unduh ulang {name}",
                data=raw,
                file_name=name,
                mime="application/json",
                key=f"download_{index}",
            )
if not parsed:
    ui.html(
        '<div class="gx-empty-state"><span class="gx-empty-icon">ⓘ</span>'
        "<p>Belum ada file yang diunggah. Pilih berkas JSON di atas untuk melihat "
        "data gradasi, JMF, dan Marshall.</p></div>"
    )

st.divider()
st.subheader("Template contoh")
st.markdown("Unduh template AC-WC untuk mulai mengisi data gradasi di Kalkulator.")

SPEC_VERSION = SPECIFICATIONS["default_version"]
SPEC_VERSION_DATA = SPECIFICATIONS["versions"][SPEC_VERSION]
TEMPLATE_PASSING = {
    19: [100, 100, 100],
    12.5: [95, 100, 100],
    9.5: [82, 95, 100],
    4.75: [60, 70, 80],
    2.36: [40, 50, 60],
    0.075: [6, 6, 6],
}
template = {
    "spec_version": SPEC_VERSION,
    "sp": "AC-WC",
    "n": 3,
    "rows": [],
    "p": ["35", "35", "30"],
}
for sieve, minimum, maximum in SPEC_VERSION_DATA["gradation"]["AC-WC"]:
    passing = [
        min(maximum, max(minimum, value))
        for value in TEMPLATE_PASSING.get(
            sieve, [minimum, (minimum + maximum) / 2, maximum]
        )
    ]
    template["rows"].append({
        "d": str(sieve),
        "mn": str(minimum),
        "mx": str(maximum),
        "f": [str(value) for value in passing] + [""],
    })
st.download_button(
    "Unduh template AC-WC.json",
    data=json.dumps(template, ensure_ascii=False, indent=2),
    file_name=f"template-ac-wc-{datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json",
)
