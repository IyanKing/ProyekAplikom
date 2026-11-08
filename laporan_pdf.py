import json
from datetime import datetime
from html import escape
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import theme
import ui
from compute import compute_gradation, compute_marshall, find_kao


ACCENT = colors.HexColor("#0e6b78")
MUTED = colors.HexColor("#5a6772")
LIGHT = colors.HexColor("#e1e7ea")
BORDER = colors.HexColor("#cdd3d8")
DANGER = colors.HexColor("#b3261e")
KAS = {1: 5.0, 2: 5.5, 3: 6.0, 4: 6.5}
GRADATION_ORDER_TOL = 0.01
MONTHS = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)

ui.inject()
st.markdown(
    """
<style>
:root{color-scheme:dark}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
 background:radial-gradient(900px 480px at 88% -6%,rgba(201,138,58,.15),transparent 62%),#1b1815;
 color:#f1e8dc
}
[data-testid="stHeader"]{background:rgba(27,24,21,.92);border-bottom:1px solid rgba(233,184,115,.28)}
[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"],
[data-testid="stMarkdownContainer"] li{color:#f1e8dc}
[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4{
 color:#ecc994;line-height:1.35;overflow:visible;overflow-wrap:anywhere
}
[data-testid="stMarkdownContainer"] h1{margin-top:.25rem;margin-bottom:.75rem}
[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4{margin-top:1.1rem;margin-bottom:.6rem}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] *{color:#d2c3ad!important}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] span{
 color:#f1e8dc!important;line-height:1.45;white-space:normal;overflow-wrap:anywhere
}
[data-testid="stRadio"] [role="radiogroup"]{gap:.65rem}
[data-testid="stRadio"] label,[data-testid="stRadio"] label *{
 color:#f1e8dc!important;line-height:1.45;white-space:normal;overflow-wrap:anywhere
}
[data-testid="stRadio"] label{
 min-height:2.6rem;padding:.45rem .8rem;border:1px solid rgba(233,184,115,.28);
 border-radius:999px;background:#251d16
}
[data-testid="stRadio"] label:has(input:checked){border-color:#e9b873;background:#33271c}
[data-testid="stFileUploaderDropzone"]{
 min-height:100px;padding:1rem;background:#251d16!important;
 border:1px dashed rgba(233,184,115,.42)!important;border-radius:16px
}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] *{
 color:#f1e8dc!important;line-height:1.5!important;white-space:normal!important;
 overflow-wrap:anywhere!important
}
[data-testid="stFileUploader"] label{color:#f1e8dc!important;line-height:1.45}
[data-testid="stFileUploader"] small{color:#d2c3ad!important}
[data-testid="stAlert"]{
 background:#251d16!important;color:#f1e8dc!important;border:1px solid rgba(233,184,115,.28)
}
[data-testid="stAlert"] *{color:#f1e8dc!important;line-height:1.5}
[data-testid="stAlert"] svg{color:#e9b873!important;fill:#e9b873!important}
[data-testid="stExpander"]{
 background:#251d16;border:1px solid rgba(233,184,115,.28);border-radius:16px;overflow:hidden
}
[data-testid="stExpander"] summary{
 min-height:3rem;padding:.8rem 1rem;color:#f1e8dc!important;
 line-height:1.45;white-space:normal
}
[data-testid="stExpander"] summary *{
 color:#f1e8dc!important;line-height:1.45!important;white-space:normal!important;
 overflow-wrap:anywhere!important
}
[data-testid="stExpander"] summary svg{color:#e9b873!important;flex:0 0 auto}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{padding:.35rem 1rem 1rem}
[data-testid="stMetric"]{
 min-width:0;height:100%;padding:1rem;background:#251d16;
 border:1px solid rgba(233,184,115,.28);border-radius:14px
}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"],[data-testid="stMetricValue"] *{
 color:#f1e8dc!important;white-space:normal!important;overflow-wrap:anywhere
}
[data-testid="stMetricLabel"]{line-height:1.4}
[data-testid="stTextInput"] input{
 min-height:2.75rem;background:#251d16;color:#f1e8dc;border:1px solid rgba(233,184,115,.35)
}
[data-testid="stTextInput"] input::placeholder{color:#b8a995}
[data-testid="stButton"] button,[data-testid="stDownloadButton"] button,
[data-testid="stFileUploader"] button{
 min-height:2.65rem;padding:.55rem 1rem;background:#2f241b;color:#f1e8dc;
 border:1px solid rgba(233,184,115,.4);border-radius:999px;line-height:1.4;
 white-space:normal
}
[data-testid="stButton"] button:hover,[data-testid="stDownloadButton"] button:hover,
[data-testid="stFileUploader"] button:hover{border-color:#e9b873;color:#e9b873}
[data-testid="stDataFrame"]{border:1px solid rgba(233,184,115,.28);border-radius:12px}
.gx-report-table-wrap{width:100%;overflow-x:auto;margin:.4rem 0 1rem;
 border:1px solid rgba(233,184,115,.28);border-radius:12px}
.gx-report-table{width:100%;border-collapse:collapse;color:#f1e8dc;font-size:.92rem}
.gx-report-table th{padding:.65rem .8rem;background:#2f241b;color:#e9b873;
 text-align:left;white-space:nowrap;border-bottom:1px solid rgba(233,184,115,.28)}
.gx-report-table td{padding:.62rem .8rem;color:#f1e8dc;border-bottom:1px solid rgba(233,184,115,.18)}
.gx-report-table tbody tr:nth-child(even){background:rgba(233,184,115,.055)}
.gx-report-table tbody tr:last-child td{border-bottom:0}
@media(max-width:700px){
 [data-testid="stRadio"] [role="radiogroup"]{flex-wrap:wrap}
 [data-testid="stMetric"]{padding:.75rem}
 .gx-report-table{font-size:.82rem}
 .gx-report-table th,.gx-report-table td{padding:.5rem .6rem}
}
</style>
""",
    unsafe_allow_html=True,
)
ui.html(theme.page_head(
    "Laporan PDF atau Word",
    "Susun laporan gradasi, rancangan campuran, dan hasil Marshall dari data JSON.",
    "Dokumen laporan",
))

st.markdown(
    "Unggah data JSON dari Kalkulator, atau gunakan data ilustrasi untuk melihat "
    "contoh laporan. Perhitungan laporan dilakukan ulang dari data sumber."
)


def _number(value, default=None):
    if value is None or value == "" or isinstance(value, bool):
        return default
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def _format(value, digits=2):
    if value is None or not np.isfinite(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _sample_state():
    specification = [
        (25, 100, 100), (19, 100, 100), (12.5, 90, 100), (9.5, 77, 90),
        (4.75, 53, 69), (2.36, 33, 53), (1.18, 21, 40), (0.6, 14, 30),
        (0.3, 9, 22), (0.15, 6, 15), (0.075, 4, 9),
    ]
    fractions = [
        [100, 100, 100], [100, 100, 100], [95, 100, 100], [82, 95, 100],
        [60, 70, 80], [40, 50, 60], [25, 35, 45], [18, 25, 34],
        [12, 18, 25], [8, 12, 17], [5, 7, 9],
    ]
    rows = [
        {"d": str(d), "mn": str(mn), "mx": str(mx), "f": [str(v) for v in values] + [""]}
        for (d, mn, mx), values in zip(specification, fractions)
    ]
    marshall_rows = []
    for ka, samples in {
        5.0: [(1200, 1210, 700, 900, 2.6), (1201, 1211, 701, 920, 2.6), (1199, 1209, 699, 880, 2.5)],
        5.5: [(1202, 1205, 700, 980, 3.0), (1200, 1203, 698, 1000, 3.0), (1201, 1204, 699, 1020, 3.1)],
        6.0: [(1201, 1201, 700, 1030, 3.3), (1200, 1201, 700, 1050, 3.4), (1202, 1203, 701, 1070, 3.3)],
        6.5: [(1198, 1202, 700, 930, 3.7), (1199, 1203, 701, 950, 3.8), (1200, 1204, 702, 970, 3.7)],
    }.items():
        for dry, ssd, immersed, stability, flow in samples:
            marshall_rows.append({
                "ka": str(ka), "a": str(dry), "b": str(ssd), "c": str(immersed),
                "st": str(stability), "fl": str(flow),
            })
    return {
        "sp": "AC-WC",
        "n": 3,
        "rows": rows,
        "p": ["35", "35", "30"],
        "jm": {"kg": "2", "ka": "5.5", "k": "0.75", "bt": "1200", "tg": "mid"},
        "mz": {
            "sp": "AC-WC",
            "lim": {"vi1": "3", "vi2": "5", "vma": "15", "vfa": "65", "st": "800", "fl1": "2", "fl2": "4", "mq": "250"},
            "g": {"gsb": "2.65", "gse": "2.65", "gb": "1.03", "pg": "1"},
            "rows": marshall_rows,
        },
    }


def _validate_state(state):
    if not isinstance(state, dict) or not isinstance(state.get("rows"), list):
        raise ValueError("JSON harus berupa objek yang berisi daftar rows.")
    if any(not isinstance(row, dict) for row in state["rows"]):
        raise ValueError("Setiap baris ayakan harus berupa objek.")
    if not state["rows"]:
        raise ValueError("Data belum memiliki baris ayakan.")
    count = state.get("n")
    if not isinstance(count, int) or isinstance(count, bool) or count not in (2, 3, 4):
        raise ValueError("Jumlah fraksi harus 2, 3, atau 4.")
    if not isinstance(state.get("p"), list) or len(state["p"]) < count:
        raise ValueError("Proporsi fraksi tidak lengkap.")
    if any(_number(value) is None for value in state["p"][:count]):
        raise ValueError("Proporsi fraksi harus berupa angka.")
    if not any(_number(row.get("d")) is not None and _number(row.get("d")) > 0 for row in state["rows"]):
        raise ValueError("Tidak ada ukuran ayakan yang valid.")
    return state


def validate_data_warnings(state, grad):
    """Return non-blocking warnings for suspicious gradation and Marshall data."""
    # Keep this threshold synchronized with validateGradationOrder() in app.js.
    warnings = []
    rows = grad["rows"]
    for fraction_index in range(grad["n"]):
        for coarse, fine in zip(rows, rows[1:]):
            coarse_value = _number(coarse["f"][fraction_index])
            fine_value = _number(fine["f"][fraction_index])
            if (
                coarse_value is not None
                and fine_value is not None
                and fine_value > coarse_value + GRADATION_ORDER_TOL
            ):
                warnings.append(
                    f"Fraksi {chr(65 + fraction_index)}: % lolos di ayakan "
                    f"{fine['d']:g} mm ({fine_value:.2f}%) lebih besar dari "
                    f"ayakan yang lebih kasar {coarse['d']:g} mm "
                    f"({coarse_value:.2f}%)."
                )

    total_proportion = sum(grad["p"])
    if total_proportion > 0 and abs(total_proportion - 100) > 0.5:
        warnings.append(
            f"Total proporsi fraksi = {total_proportion:.2f}% "
            "(seharusnya 100%). Hasil tetap dihitung proporsional."
        )
    if any(proportion < 0 for proportion in grad["p"]):
        warnings.append("Ada proporsi fraksi bernilai negatif.")

    marshall = state.get("mz")
    marshall_rows = marshall.get("rows", []) if isinstance(marshall, dict) else []
    if isinstance(marshall_rows, list):
        for index, row in enumerate(marshall_rows):
            if not isinstance(row, dict):
                continue
            dry = _number(row.get("a"))
            ssd = _number(row.get("b"))
            flow = _number(row.get("fl"))
            if (
                dry is not None and ssd is not None
                and dry > 0 and ssd > 0 and ssd < dry - 0.01
            ):
                warnings.append(
                    f"Benda uji #{index + 1}: berat SSD ({ssd:.1f} g) lebih "
                    f"kecil dari berat kering ({dry:.1f} g)."
                )
            if flow is not None and flow <= 0:
                warnings.append(
                    f"Benda uji #{index + 1}: Flow = {flow:.2f} mm (harus > 0)."
                )
    return warnings


def compute_jmf(state, grad):
    config = state.get("jm")
    if not isinstance(config, dict):
        return None
    group = int(_number(config.get("kg"), 2))
    group = min(max(group, 1), 4)
    asphalt_percent = _number(config.get("ka"), KAS[group])
    total_weight = _number(config.get("bt"), 1200.0)
    constant = _number(config.get("k"), 0.75)
    if not 0 <= asphalt_percent < 100 or total_weight <= 0:
        raise ValueError("Pengaturan JMF harus memiliki kadar aspal 0–<100% dan berat total positif.")

    targets = []
    for row in grad["rows"]:
        if config.get("tg", "mid") == "blend":
            target = row["P"]
        elif row["mn"] is not None and row["mx"] is not None:
            target = (row["mn"] + row["mx"]) / 2
        else:
            target = row["P"]
        if target is not None:
            targets.append({"d": row["d"], "P": target})
    if not targets:
        return None

    previous = 100.0
    sieve_rows = []
    for row in targets:
        retained = previous - row["P"]
        sieve_rows.append({"d": row["d"], "P": row["P"], "t": retained})
        previous = row["P"]
    pan = previous
    coarse = sum(row["t"] for row in sieve_rows if row["d"] >= 4.75)
    fine = sum(row["t"] for row in sieve_rows if row["d"] < 4.75)
    binder_formula = 0.035 * coarse + 0.045 * fine + 0.18 * pan + constant
    aggregate_weight = total_weight * (1 - asphalt_percent / 100)
    asphalt_weight = total_weight * asphalt_percent / 100
    groups = []
    for current_group, default_percent in KAS.items():
        current_percent = asphalt_percent if current_group == group else default_percent
        current_aggregate = total_weight * (1 - current_percent / 100)
        groups.append({
            "group": current_group,
            "ka": current_percent,
            "asphalt": total_weight * current_percent / 100,
            "aggregate": current_aggregate,
        })
    return {
        "kg": group, "ka": asphalt_percent, "bt": total_weight, "k": constant,
        "tg": config.get("tg", "mid"), "T": sieve_rows, "pan": pan, "ca": coarse,
        "fa": fine, "pb": binder_formula, "ag": aggregate_weight,
        "aspal": asphalt_weight, "groups": groups,
    }


def _chart_buffer(figure, dpi=160, image_format="png"):
    output = BytesIO()
    save_options = {"format": image_format, "bbox_inches": "tight"}
    if image_format == "png":
        save_options["dpi"] = dpi
    figure.savefig(output, **save_options)
    plt.close(figure)
    output.seek(0)
    return output


def chart_gradation(gradation, dpi=160, image_format="png"):
    rows = [row for row in gradation["rows"] if row["P"] is not None]
    if not rows:
        return None
    diameters = [row["d"] for row in rows]
    figure, axis = plt.subplots(figsize=(10.2, 4.2))
    bounded = [row for row in rows if row["mn"] is not None and row["mx"] is not None]
    if len(bounded) > 1:
        x_values = [row["d"] for row in bounded]
        minimum = [row["mn"] for row in bounded]
        maximum = [row["mx"] for row in bounded]
        axis.fill_between(x_values, minimum, maximum, color="#0e6b78", alpha=0.15, label="Rentang spesifikasi")
        axis.plot(x_values, minimum, color="#0e6b78", linewidth=1.3, label="Batas min/maks")
        axis.plot(x_values, maximum, color="#0e6b78", linewidth=1.3)
    for index in range(gradation["n"]):
        axis.plot(diameters, [row["f"][index] for row in rows], linestyle="--", linewidth=1, label=f"Fraksi {chr(65 + index)}")
    axis.plot(diameters, [row["P"] for row in rows], color="#b3261e", marker="o", linewidth=2, label="Campuran")
    axis.set_xscale("log")
    axis.set_xlim(max(diameters), min(diameters))
    axis.set_ylim(0, 100)
    axis.set_xlabel("Ukuran ayakan (mm, skala log)")
    axis.set_ylabel("% lolos")
    axis.set_xticks(diameters, [f"{value:g}" for value in diameters])
    axis.grid(True, which="both", alpha=0.25)
    axis.legend(fontsize=8, ncol=3, loc="best")
    figure.tight_layout()
    return _chart_buffer(figure, dpi=dpi, image_format=image_format)


def chart_marshall(metric, label, unit, marshall, kao_info, dpi=160, image_format="png"):
    averages = [row for row in marshall["A"] if row[metric] is not None]
    if not averages:
        return None
    x_values = [row["ka"] for row in averages]
    y_values = [row[metric] for row in averages]
    figure, axis = plt.subplots(figsize=(4.8, 3.0))
    axis.scatter(x_values, y_values, color="#b3261e", s=24, zorder=3, label="Rata-rata")
    fit = kao_info["fits"].get(metric) if kao_info else None
    if fit is not None and len(x_values) >= 2:
        x_fit = np.linspace(min(x_values), max(x_values), 100)
        axis.plot(x_fit, fit(x_fit), color="#0e6b78", linewidth=1.5, label="Regresi")
    minimum, maximum = marshall["lims"].get(metric, (None, None))
    if minimum is not None:
        axis.axhline(minimum, color="#b3261e", linestyle="--", linewidth=1, label="Batas spesifikasi")
    if maximum is not None:
        axis.axhline(maximum, color="#b3261e", linestyle="--", linewidth=1)
    if kao_info and kao_info.get("kao") is not None:
        axis.axvline(kao_info["kao"], color="#c8400d", linestyle=":", linewidth=1.2, label="KAO")
    axis.set_title(f"{label} ({unit})")
    axis.set_xlabel("Kadar aspal (%)")
    axis.set_ylabel(unit)
    axis.grid(True, alpha=0.25)
    axis.legend(fontsize=7)
    figure.tight_layout()
    return _chart_buffer(figure, dpi=dpi, image_format=image_format)


def chart_marshall_panel(marshall, kao_info, dpi=160, image_format="png"):
    metrics = (
        ("vim", "VIM", "%"),
        ("vma", "VMA", "%"),
        ("vfa", "VFA", "%"),
        ("st", "Stabilitas", "kg"),
        ("fl", "Flow", "mm"),
        ("mq", "MQ", "kg/mm"),
    )
    figure, axes = plt.subplots(2, 3, figsize=(12, 7.5))
    for axis, (metric, label, unit) in zip(axes.flat, metrics):
        averages = [
            row for row in marshall["A"]
            if row[metric] is not None and np.isfinite(row[metric])
        ]
        if not averages:
            axis.set_title(f"{label} ({unit}) — data tidak tersedia")
            axis.set_axis_off()
            continue

        x_values = [row["ka"] for row in averages]
        y_values = [row[metric] for row in averages]
        axis.scatter(x_values, y_values, color="#b3261e", s=20, zorder=3, label="Rata-rata")
        fit = kao_info["fits"].get(metric) if kao_info else None
        if fit is not None and len(x_values) >= 2:
            fit_x = np.linspace(min(x_values), max(x_values), 100)
            axis.plot(fit_x, fit(fit_x), color="#0e6b78", linewidth=1.4, label="Regresi")
        minimum, maximum = marshall["lims"].get(metric, (None, None))
        if minimum is not None:
            axis.axhline(minimum, color="#b3261e", linestyle="--", linewidth=0.8)
        if maximum is not None:
            axis.axhline(maximum, color="#b3261e", linestyle="--", linewidth=0.8)
        if kao_info and kao_info.get("kao") is not None:
            axis.axvline(kao_info["kao"], color="#c8400d", linestyle=":", linewidth=1.1)
        axis.set_title(f"{label} ({unit})")
        axis.set_xlabel("Kadar aspal (%)")
        axis.grid(True, alpha=0.25)
        axis.legend(fontsize=7)

    kao = kao_info.get("kao") if kao_info else None
    title = "Parameter Marshall terhadap Kadar Aspal"
    if kao is not None:
        title += f" — KAO = {kao:.2f}%"
    figure.suptitle(title)
    figure.tight_layout()
    return _chart_buffer(figure, dpi=dpi, image_format=image_format)


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=20, leading=24, textColor=ACCENT, alignment=TA_LEFT, spaceAfter=5,
        ),
        "section": ParagraphStyle(
            "ReportSection", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12, leading=15, textColor=ACCENT, spaceBefore=11, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "ReportBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9, leading=13, spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "ReportSmall", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.5, leading=10, textColor=MUTED,
        ),
        "cell": ParagraphStyle(
            "ReportCell", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.2, leading=9, wordWrap="CJK",
        ),
        "head_cell": ParagraphStyle(
            "ReportHeadCell", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=7.2, leading=9, textColor=colors.white, wordWrap="CJK",
        ),
    }


def _pdf_table(rows, widths, styles, right_from=1):
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["head_cell"] if row_index == 0 else styles["cell"]
        converted.append([
            value if isinstance(value, Paragraph) else Paragraph(escape(str(value)), style)
            for value in row
        ])
    table = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    if right_from is not None:
        table_styles.append(("ALIGN", (right_from, 1), (-1, -1), "RIGHT"))
    table.setStyle(TableStyle(table_styles))
    return table


def _page_decor(canvas, document):
    canvas.saveState()
    page_width, page_height = landscape(A4)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, page_height - 13 * mm, page_width - 15 * mm, page_height - 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(15 * mm, page_height - 10 * mm, "Laporan Perancangan Campuran Aspal")
    canvas.drawRightString(page_width - 15 * mm, page_height - 10 * mm, f"Halaman {document.page}")
    canvas.line(15 * mm, 12 * mm, page_width - 15 * mm, 12 * mm)
    canvas.drawCentredString(page_width / 2, 7 * mm, "Dibuat otomatis dari data kalkulator gradasi agregat")
    canvas.restoreState()


def build_pdf(state, gradation, jmf, marshall, kao_info, metadata):
    output = BytesIO()
    page_width, _ = landscape(A4)
    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=19 * mm,
        bottomMargin=17 * mm,
        title="Laporan Perancangan Campuran Aspal",
        author=metadata.get("author") or "Aplikasi Gradasi Agregat",
    )
    styles = _styles()
    story = []
    story.append(Paragraph("Laporan Perancangan Campuran Aspal", styles["title"]))
    detail = [
        f"Spesifikasi: <b>{escape(str(state.get('sp', '—')))}</b>",
        f"Fraksi: <b>{gradation['n']}</b>",
        f"Tanggal: <b>{datetime.now().day} {MONTHS[datetime.now().month - 1]} {datetime.now().year}</b>",
    ]
    if metadata.get("project"):
        detail.append(f"Proyek: <b>{escape(metadata['project'])}</b>")
    if metadata.get("location"):
        detail.append(f"Lokasi: <b>{escape(metadata['location'])}</b>")
    if metadata.get("author"):
        detail.append(f"Disusun oleh: <b>{escape(metadata['author'])}</b>")
    story.append(Paragraph(" &nbsp; | &nbsp; ".join(detail), styles["small"]))
    story.append(Spacer(1, 8))

    failed = [row for row in gradation["rows"] if not row["ok"]]
    story.append(Paragraph("1. Ringkasan Eksekutif", styles["section"]))
    status_text = "MEMENUHI spesifikasi" if not failed else f"TIDAK MEMENUHI ({len(failed)} ayakan)"
    summary = f"Gradasi gabungan <b>{status_text}</b>. Proporsi campuran: "
    summary += ", ".join(
        f"Fraksi {chr(65 + index)} = {_format(value)}%"
        for index, value in enumerate(gradation["p"])
    ) + "."
    if jmf:
        summary += f" Pb hasil rumus = <b>{_format(jmf['pb'])}%</b> (pembulatan 0,5%: <b>{_format(round(jmf['pb'] * 2) / 2)}%</b>)."
    if kao_info and kao_info.get("kao") is not None:
        summary += f" Kadar aspal optimum (KAO) = <b>{_format(kao_info['kao'])}%</b>."
    story.append(Paragraph(summary, styles["body"]))

    story.append(Paragraph("2. Data Gradasi Input", styles["section"]))
    input_rows = [["Ayakan (mm)", "Min (%)", "Maks (%)"] + [f"Lolos {chr(65 + i)} (%)" for i in range(gradation["n"])]]
    for row in gradation["rows"]:
        input_rows.append([
            _format(row["d"], 3),
            _format(row["mn"]),
            _format(row["mx"]),
            *[_format(value) for value in row["f"]],
        ])
    input_widths = [30 * mm, 25 * mm, 25 * mm] + [30 * mm] * gradation["n"]
    story.append(_pdf_table(input_rows, input_widths, styles))

    story.append(Paragraph("3. Gradasi Gabungan dan Evaluasi", styles["section"]))
    blend_rows = [[
        "Ayakan (mm)", "Min (%)", "Maks (%)", "Gabungan (%)",
        "Tertahan (%)", "Kum. tertahan (%)", "Evaluasi",
    ]]
    previous = 100.0
    for row in gradation["rows"]:
        passing = row["P"]
        retained = previous - passing if passing is not None else None
        previous = passing if passing is not None else previous
        evaluation = "Memenuhi" if row["ok"] else "Data fraksi belum lengkap" if passing is None else (
            "Di bawah min" if row["mn"] is not None and passing < row["mn"] else "Di atas maks"
        )
        blend_rows.append([
            _format(row["d"], 3), _format(row["mn"]), _format(row["mx"]),
            _format(passing), _format(retained),
            _format(100 - passing if passing is not None else None), evaluation,
        ])
    blend_rows.append(["Pan", "—", "—", "—", _format(previous), "100,00", "—"])
    story.append(_pdf_table(
        blend_rows,
        [25 * mm, 23 * mm, 23 * mm, 29 * mm, 29 * mm, 37 * mm, 55 * mm],
        styles,
    ))
    gradation_chart = chart_gradation(gradation)
    if gradation_chart:
        story.append(Spacer(1, 5))
        story.append(Image(gradation_chart, width=page_width - 34 * mm, height=82 * mm))
        story.append(Paragraph("Gambar 1. Kurva gradasi tiap fraksi, campuran, dan rentang spesifikasi.", styles["small"]))

    if jmf:
        story.append(Paragraph("4. Rancangan Campuran (JMF)", styles["section"]))
        story.append(Paragraph(
            f"Kelompok {jmf['kg']}; kadar aspal <b>{_format(jmf['ka'])}%</b>; "
            f"berat total benda uji <b>{_format(jmf['bt'], 1)} g</b>; "
            f"berat aspal <b>{_format(jmf['aspal'], 1)} g</b>; "
            f"berat agregat <b>{_format(jmf['ag'], 1)} g</b>. "
            f"Komposisi target: CA {_format(jmf['ca'])}%, FA {_format(jmf['fa'])}%, "
            f"filler {_format(jmf['pan'])}%. Target: "
            f"{'campuran fraksi' if jmf['tg'] == 'blend' else 'nilai tengah spesifikasi'}.",
            styles["body"],
        ))
        jmf_rows = [[
            "Ayakan (mm)", "Target (% lolos)", "Tertahan (%)",
            *[f"Berat agregat K{group['group']} (g)" for group in jmf["groups"]],
        ]]
        for row in jmf["T"]:
            jmf_rows.append([
                _format(row["d"], 3), _format(row["P"]), _format(row["t"]),
                *[_format(row["t"] * group["aggregate"] / 100, 1) for group in jmf["groups"]],
            ])
        jmf_rows.append([
            "Pan", "0,00", _format(jmf["pan"]),
            *[_format(jmf["pan"] * group["aggregate"] / 100, 1) for group in jmf["groups"]],
        ])
        story.append(_pdf_table(jmf_rows, [28 * mm, 32 * mm, 30 * mm, 42 * mm, 42 * mm, 42 * mm, 42 * mm], styles))
        group_rows = [["Kelompok", "Kadar aspal (%)", "Berat aspal (g)", "Berat agregat (g)"]]
        for group in jmf["groups"]:
            group_rows.append([
                f"Kelompok {group['group']}", _format(group["ka"]),
                _format(group["asphalt"], 1), _format(group["aggregate"], 1),
            ])
        story.append(Spacer(1, 5))
        story.append(_pdf_table(group_rows, [42 * mm, 48 * mm, 52 * mm, 55 * mm], styles))

    if marshall:
        story.append(PageBreak())
        story.append(Paragraph("5. Analisis Uji Marshall", styles["section"]))
        limit_rows = [["Parameter", "Batas minimum", "Batas maksimum", "Satuan"]]
        labels = [
            ("vim", "VIM", "%"), ("vma", "VMA", "%"), ("vfa", "VFA", "%"),
            ("st", "Stabilitas", "kg"), ("fl", "Flow", "mm"), ("mq", "MQ", "kg/mm"),
        ]
        for metric, label, unit in labels:
            minimum, maximum = marshall["lims"][metric]
            if minimum is not None or maximum is not None:
                limit_rows.append([label, f">= {_format(minimum)}" if minimum is not None else "—",
                                   f"<= {_format(maximum)}" if maximum is not None else "—", unit])
        story.append(_pdf_table(limit_rows, [55 * mm, 55 * mm, 55 * mm, 35 * mm], styles, right_from=None))
        sample_rows = [["KA (%)", "Berat kering (g)", "Berat SSD (g)", "Berat dalam air (g)", "Stabilitas (baca)", "Flow (mm)"]]
        for sample in marshall["samples"]:
            sample_rows.append([
                _format(sample["ka"]), _format(sample["a"], 1), _format(sample["b"], 1),
                _format(sample["c"], 1), _format(sample["st"], 2), _format(sample["fl"]),
            ])
        story.append(Spacer(1, 7))
        story.append(Paragraph("Data benda uji", styles["body"]))
        story.append(_pdf_table(sample_rows, [34 * mm, 42 * mm, 42 * mm, 44 * mm, 45 * mm, 35 * mm], styles))
        result_rows = [[
            "KA (%)", "n", "Gmb", "VIM (%)", "VMA (%)", "VFA (%)",
            "Stabilitas (kg)", "Flow (mm)", "MQ (kg/mm)",
        ]]
        for row in marshall["A"]:
            result_rows.append([
                _format(row["ka"]), str(row["n"]), _format(row["gmb"], 3),
                _format(row["vim"]), _format(row["vma"]), _format(row["vfa"]),
                _format(row["st"]), _format(row["fl"]), _format(row["mq"]),
            ])
        story.append(Spacer(1, 7))
        story.append(Paragraph("Rata-rata hasil per kadar aspal", styles["body"]))
        story.append(_pdf_table(
            result_rows,
            [23 * mm, 12 * mm, 22 * mm, 25 * mm, 25 * mm, 25 * mm, 34 * mm, 23 * mm, 27 * mm],
            styles,
        ))
        if kao_info and kao_info.get("kao") is not None:
            first, last = kao_info["range"]
            story.append(Spacer(1, 5))
            story.append(Paragraph(
                f"<b>KAO = {_format(kao_info['kao'])}%</b>, titik tengah rentang "
                f"{_format(first)}–{_format(last)}% yang memenuhi batas terpasang.",
                styles["body"],
            ))
        if len(marshall["A"]) > 1:
            story.append(Paragraph("Grafik Parameter Marshall", styles["section"]))
            metric_charts = []
            for metric, label, unit in labels:
                chart = chart_marshall(metric, label, unit, marshall, kao_info)
                if chart:
                    metric_charts.append(Image(chart, width=80 * mm, height=50 * mm))
            for start in range(0, len(metric_charts), 3):
                row = metric_charts[start:start + 3]
                while len(row) < 3:
                    row.append("")
                chart_table = Table([row], colWidths=[86 * mm] * 3, hAlign="LEFT")
                chart_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]))
                story.append(chart_table)

    story.append(Paragraph("6. Kesimpulan", styles["section"]))
    conclusions = []
    if failed:
        conclusions.append(
            "Gradasi gabungan tidak memenuhi seluruh batas pada ayakan: "
            + ", ".join(f"{_format(row['d'], 3)} mm" for row in failed) + "."
        )
    else:
        conclusions.append("Gradasi gabungan memenuhi seluruh batas spesifikasi yang tersedia.")
    if jmf:
        conclusions.append(
            f"Pb hasil rumus adalah {_format(jmf['pb'])}% "
            f"(pembulatan 0,5%: {_format(round(jmf['pb'] * 2) / 2)}%)."
        )
    if kao_info and kao_info.get("kao") is not None:
        conclusions.append(f"KAO hasil interpolasi parameter Marshall adalah {_format(kao_info['kao'])}%.")
    elif state.get("mz"):
        conclusions.append("KAO belum dapat ditentukan dari data Marshall dan batas yang tersedia.")
    for sentence in conclusions:
        story.append(Paragraph(f"• {escape(sentence)}", styles["body"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Catatan: laporan dihitung ulang dari data JSON yang diunggah. "
        "Hasil bergantung pada ketepatan data laboratorium dan batas spesifikasi; "
        "verifikasi kembali sebelum digunakan sebagai dokumen teknis.",
        styles["small"],
    ))
    document.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
    output.seek(0)
    return output


def _docx_cell_shading(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _docx_table(document, rows):
    table = document.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    table.autofit = True
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row_index, values in enumerate(rows):
        cells = table.rows[0].cells if row_index == 0 else table.add_row().cells
        for cell, value in zip(cells, values):
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8)
                    if row_index == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        _docx_cell_shading(cell, "0E6B78")
        if row_index == 0:
            row_properties = table.rows[0]._tr.get_or_add_trPr()
            repeat = OxmlElement("w:tblHeader")
            repeat.set(qn("w:val"), "true")
            row_properties.append(repeat)
    document.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def _docx_heading(document, title, level=1):
    heading = document.add_heading(title, level=level)
    heading.paragraph_format.keep_with_next = True
    return heading


def _docx_add_chart(document, chart, caption=None, width=Cm(23)):
    if not chart:
        return
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(chart, width=width)
    if caption:
        caption_paragraph = document.add_paragraph(caption)
        caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in caption_paragraph.runs:
            run.italic = True
            run.font.size = Pt(8)


def _docx_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Halaman ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)


def build_docx(state, gradation, jmf, marshall, kao_info, metadata):
    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Cm(29.7)
    section.page_height = Cm(21)
    section.top_margin = Cm(1.7)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(1.7)
    section.right_margin = Cm(1.7)

    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(5)
    for style_name in ("Heading 1", "Heading 2"):
        style = document.styles[style_name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(14, 107, 120)

    header = section.header.paragraphs[0]
    header.text = "Laporan Perancangan Campuran Aspal"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(90, 103, 114)
    _docx_page_number(section.footer.paragraphs[0])

    title = document.add_heading("Laporan Perancangan Campuran Aspal", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.name = "Arial"
    title_run.font.color.rgb = RGBColor(14, 107, 120)

    details = [
        f"Spesifikasi: {state.get('sp', '—')}",
        f"Fraksi: {gradation['n']}",
        f"Tanggal: {datetime.now().day} {MONTHS[datetime.now().month - 1]} {datetime.now().year}",
    ]
    for key, label in (("project", "Proyek"), ("location", "Lokasi"), ("author", "Disusun oleh")):
        if metadata.get(key):
            details.append(f"{label}: {metadata[key]}")
    detail_paragraph = document.add_paragraph("  |  ".join(details))
    detail_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    failed = [row for row in gradation["rows"] if not row["ok"]]
    _docx_heading(document, "1. Ringkasan Eksekutif")
    status_text = "MEMENUHI spesifikasi" if not failed else f"TIDAK MEMENUHI ({len(failed)} ayakan)"
    summary = (
        f"Gradasi gabungan {status_text}. Proporsi campuran: "
        + ", ".join(
            f"Fraksi {chr(65 + index)} = {_format(value)}%"
            for index, value in enumerate(gradation["p"])
        )
        + "."
    )
    if jmf:
        summary += (
            f" Pb hasil rumus = {_format(jmf['pb'])}% "
            f"(pembulatan 0,5%: {_format(round(jmf['pb'] * 2) / 2)}%)."
        )
    if kao_info and kao_info.get("kao") is not None:
        summary += f" Kadar aspal optimum (KAO) = {_format(kao_info['kao'])}%."
    document.add_paragraph(summary)

    _docx_heading(document, "2. Data Gradasi Input")
    input_rows = [[
        "Ayakan (mm)", "Min (%)", "Maks (%)",
        *[f"Lolos {chr(65 + index)} (%)" for index in range(gradation["n"])],
    ]]
    for row in gradation["rows"]:
        input_rows.append([
            _format(row["d"], 3), _format(row["mn"]), _format(row["mx"]),
            *[_format(value) for value in row["f"]],
        ])
    _docx_table(document, input_rows)

    _docx_heading(document, "3. Gradasi Gabungan dan Evaluasi")
    blend_rows = [[
        "Ayakan (mm)", "Min (%)", "Maks (%)", "Gabungan (%)",
        "Tertahan (%)", "Kum. tertahan (%)", "Evaluasi",
    ]]
    previous = 100.0
    for row in gradation["rows"]:
        passing = row["P"]
        retained = previous - passing if passing is not None else None
        previous = passing if passing is not None else previous
        evaluation = "Memenuhi" if row["ok"] else "Data fraksi belum lengkap" if passing is None else (
            "Di bawah min" if row["mn"] is not None and passing < row["mn"] else "Di atas maks"
        )
        blend_rows.append([
            _format(row["d"], 3), _format(row["mn"]), _format(row["mx"]),
            _format(passing), _format(retained),
            _format(100 - passing if passing is not None else None), evaluation,
        ])
    blend_rows.append(["Pan", "—", "—", "—", _format(previous), "100,00", "—"])
    _docx_table(document, blend_rows)
    _docx_add_chart(
        document,
        chart_gradation(gradation),
        "Gambar 1. Kurva gradasi tiap fraksi, campuran, dan rentang spesifikasi.",
    )

    if jmf:
        _docx_heading(document, "4. Rancangan Campuran (JMF)")
        document.add_paragraph(
            f"Kelompok {jmf['kg']}; kadar aspal {_format(jmf['ka'])}%; "
            f"berat total benda uji {_format(jmf['bt'], 1)} g; "
            f"berat aspal {_format(jmf['aspal'], 1)} g; "
            f"berat agregat {_format(jmf['ag'], 1)} g. Komposisi target: "
            f"CA {_format(jmf['ca'])}%, FA {_format(jmf['fa'])}%, "
            f"filler {_format(jmf['pan'])}%. Target: "
            f"{'campuran fraksi' if jmf['tg'] == 'blend' else 'nilai tengah spesifikasi'}."
        )
        jmf_rows = [[
            "Ayakan (mm)", "Target (% lolos)", "Tertahan (%)",
            *[f"Berat agregat K{group['group']} (g)" for group in jmf["groups"]],
        ]]
        for row in jmf["T"]:
            jmf_rows.append([
                _format(row["d"], 3), _format(row["P"]), _format(row["t"]),
                *[_format(row["t"] * group["aggregate"] / 100, 1) for group in jmf["groups"]],
            ])
        jmf_rows.append([
            "Pan", "0,00", _format(jmf["pan"]),
            *[_format(jmf["pan"] * group["aggregate"] / 100, 1) for group in jmf["groups"]],
        ])
        _docx_table(document, jmf_rows)
        group_rows = [["Kelompok", "Kadar aspal (%)", "Berat aspal (g)", "Berat agregat (g)"]]
        for group in jmf["groups"]:
            group_rows.append([
                f"Kelompok {group['group']}", _format(group["ka"]),
                _format(group["asphalt"], 1), _format(group["aggregate"], 1),
            ])
        _docx_table(document, group_rows)

    if marshall:
        document.add_page_break()
        _docx_heading(document, "5. Analisis Uji Marshall")
        labels = [
            ("vim", "VIM", "%"), ("vma", "VMA", "%"), ("vfa", "VFA", "%"),
            ("st", "Stabilitas", "kg"), ("fl", "Flow", "mm"), ("mq", "MQ", "kg/mm"),
        ]
        limit_rows = [["Parameter", "Batas minimum", "Batas maksimum", "Satuan"]]
        for metric, label, unit in labels:
            minimum, maximum = marshall["lims"][metric]
            if minimum is not None or maximum is not None:
                limit_rows.append([
                    label, f">= {_format(minimum)}" if minimum is not None else "—",
                    f"<= {_format(maximum)}" if maximum is not None else "—", unit,
                ])
        _docx_table(document, limit_rows)

        sample_rows = [[
            "KA (%)", "Berat kering (g)", "Berat SSD (g)", "Berat dalam air (g)",
            "Stabilitas (baca)", "Flow (mm)",
        ]]
        for sample in marshall["samples"]:
            sample_rows.append([
                _format(sample["ka"]), _format(sample["a"], 1), _format(sample["b"], 1),
                _format(sample["c"], 1), _format(sample["st"], 2), _format(sample["fl"]),
            ])
        _docx_heading(document, "Data benda uji", level=2)
        _docx_table(document, sample_rows)

        result_rows = [[
            "KA (%)", "n", "Gmb", "VIM (%)", "VMA (%)", "VFA (%)",
            "Stabilitas (kg)", "Flow (mm)", "MQ (kg/mm)",
        ]]
        for row in marshall["A"]:
            result_rows.append([
                _format(row["ka"]), str(row["n"]), _format(row["gmb"], 3),
                _format(row["vim"]), _format(row["vma"]), _format(row["vfa"]),
                _format(row["st"]), _format(row["fl"]), _format(row["mq"]),
            ])
        _docx_heading(document, "Rata-rata hasil per kadar aspal", level=2)
        _docx_table(document, result_rows)
        if kao_info and kao_info.get("kao") is not None:
            first, last = kao_info["range"]
            document.add_paragraph(
                f"KAO = {_format(kao_info['kao'])}%, titik tengah rentang "
                f"{_format(first)}–{_format(last)}% yang memenuhi batas terpasang."
            )
        if len(marshall["A"]) > 1:
            _docx_heading(document, "Grafik Parameter Marshall", level=2)
            for metric, label, unit in labels:
                _docx_add_chart(
                    document,
                    chart_marshall(metric, label, unit, marshall, kao_info),
                    f"{label} ({unit})",
                    width=Cm(11),
                )

    _docx_heading(document, "6. Kesimpulan")
    conclusions = []
    if failed:
        conclusions.append(
            "Gradasi gabungan tidak memenuhi seluruh batas pada ayakan: "
            + ", ".join(f"{_format(row['d'], 3)} mm" for row in failed) + "."
        )
    else:
        conclusions.append("Gradasi gabungan memenuhi seluruh batas spesifikasi yang tersedia.")
    if jmf:
        conclusions.append(
            f"Pb hasil rumus adalah {_format(jmf['pb'])}% "
            f"(pembulatan 0,5%: {_format(round(jmf['pb'] * 2) / 2)}%)."
        )
    if kao_info and kao_info.get("kao") is not None:
        conclusions.append(f"KAO hasil evaluasi adalah {_format(kao_info['kao'])}%.")
    for sentence in conclusions:
        document.add_paragraph(sentence, style="List Bullet")
    note = document.add_paragraph(
        "Catatan: laporan dihitung ulang dari data JSON yang diunggah. "
        "Hasil bergantung pada ketepatan data laboratorium dan batas spesifikasi; "
        "verifikasi kembali sebelum digunakan sebagai dokumen teknis."
    )
    for run in note.runs:
        run.italic = True
        run.font.size = Pt(8)

    output = BytesIO()
    document.save(output)
    output.seek(0)
    return output


selected_state = None
source_name = ""
report_source = st.radio(
    "Sumber data laporan",
    ["Unggah file JSON", "Data contoh"],
    horizontal=True,
    label_visibility="collapsed",
)
if report_source == "Unggah file JSON":
    uploaded_file = st.file_uploader("Pilih file data dari Kalkulator", type=["json"], key="report_json")
    if uploaded_file is not None:
        try:
            selected_state = _validate_state(json.loads(uploaded_file.getvalue().decode("utf-8-sig")))
            source_name = uploaded_file.name
            st.success(f"File {uploaded_file.name} berhasil dibaca.")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            st.error(f"File tidak dapat diproses: {error}")
else:
    st.caption("Data contoh hanya ilustrasi, bukan data hasil pengujian laboratorium.")
    if st.button("Gunakan data contoh", key="use_pdf_sample"):
        st.session_state["pdf_sample_state"] = _sample_state()
    if st.session_state.get("pdf_sample_state") is not None:
        selected_state = st.session_state["pdf_sample_state"]
        source_name = "data-contoh"

if selected_state is not None:
    try:
        gradation = compute_gradation(selected_state)
        jmf = compute_jmf(selected_state, gradation)
        marshall = compute_marshall(selected_state)
        kao_info = find_kao(marshall)
        warnings = validate_data_warnings(selected_state, gradation)
        if warnings:
            with st.expander(
                f"⚠ {len(warnings)} peringatan pada data (klik untuk melihat)",
                expanded=False,
            ):
                for warning in warnings:
                    st.warning(warning)
        failed = [row for row in gradation["rows"] if not row["ok"]]
        st.divider()
        st.subheader("Pratinjau laporan")
        columns = st.columns(4)
        columns[0].metric("Spesifikasi", str(selected_state.get("sp", "—")))
        columns[1].metric("Ayakan", len(gradation["rows"]))
        columns[2].metric("Status gradasi", "Memenuhi" if not failed else f"{len(failed)} di luar batas")
        columns[3].metric(
            "KAO",
            f"{_format(kao_info['kao'])}%"
            if kao_info and kao_info.get("kao") is not None else "—",
        )
        with st.expander("Lihat tabel gradasi gabungan"):
            preview = pd.DataFrame([
                {
                    "Ayakan (mm)": _format(row["d"], 3),
                    "Min": _format(row["mn"]),
                    "Maks": _format(row["mx"]),
                    "Gabungan (%)": _format(row["P"]),
                    "Status": "Memenuhi" if row["ok"] else "Tidak memenuhi",
                }
                for row in gradation["rows"]
            ])
            headers = "".join(f"<th>{escape(str(column))}</th>" for column in preview.columns)
            body = "".join(
                "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
                for row in preview.itertuples(index=False, name=None)
            )
            ui.html(
                '<div class="gx-report-table-wrap"><table class="gx-report-table">'
                f"<thead><tr>{headers}</tr></thead><tbody>{body}</tbody>"
                "</table></div>"
            )

        st.subheader("Ekspor grafik terpisah")
        st.caption(
            "Unduh grafik untuk presentasi tanpa membuat laporan lengkap. "
            "PNG cocok untuk gambar raster; SVG adalah format vektor."
        )
        export_columns = st.columns([1, 2])
        with export_columns[0]:
            export_dpi = st.selectbox(
                "Resolusi PNG",
                [150, 300, 600],
                index=1,
                help="300 DPI cocok untuk laporan cetak; 600 DPI untuk kebutuhan resolusi tinggi.",
                key="chart_export_dpi",
            )
        export_format = st.radio(
            "Format grafik",
            ["PNG", "SVG"],
            horizontal=True,
            key="chart_export_format",
        )
        image_format = export_format.lower()
        mime_type = "image/png" if image_format == "png" else "image/svg+xml"
        image_suffix = f".{image_format}"
        chart_stem = "".join(
            char.lower() if char.isalnum() else "-"
            for char in source_name
        ).strip("-") or "gradasi"
        date_stamp = datetime.now().strftime("%Y%m%d")
        graph_columns = st.columns(2)
        with graph_columns[0]:
            gradation_image = chart_gradation(
                gradation, dpi=export_dpi, image_format=image_format
            )
            if gradation_image is None:
                st.warning("Data gradasi belum cukup untuk membuat grafik.")
            else:
                st.download_button(
                    "Unduh grafik gradasi",
                    data=gradation_image.getvalue(),
                    file_name=f"grafik-gradasi-{chart_stem}-{date_stamp}{image_suffix}",
                    mime=mime_type,
                    key="download_gradation_chart",
                )
        with graph_columns[1]:
            if marshall is None or not marshall["A"]:
                st.info("Data Marshall belum cukup untuk membuat grafik.")
            else:
                marshall_image = chart_marshall_panel(
                    marshall, kao_info, dpi=export_dpi, image_format=image_format
                )
                st.download_button(
                    "Unduh grafik Marshall",
                    data=marshall_image.getvalue(),
                    file_name=f"grafik-marshall-{chart_stem}-{date_stamp}{image_suffix}",
                    mime=mime_type,
                    key="download_marshall_chart",
                )

        project_column, author_column, location_column = st.columns(3)
        with project_column:
            project = st.text_input("Nama proyek (opsional)", key="pdf_project")
        with author_column:
            author = st.text_input("Disusun oleh (opsional)", key="pdf_author")
        with location_column:
            location = st.text_input("Lokasi (opsional)", key="pdf_location")
        metadata = {"project": project.strip(), "author": author.strip(), "location": location.strip()}
        report_format = st.radio(
            "Format laporan",
            ["PDF", "Word (.docx)"],
            horizontal=True,
            key="report_format",
        )
        if report_format == "PDF":
            report = build_pdf(selected_state, gradation, jmf, marshall, kao_info, metadata)
            extension = "pdf"
            mime_type = "application/pdf"
        else:
            report = build_docx(selected_state, gradation, jmf, marshall, kao_info, metadata)
            extension = "docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        file_stem = "".join(char.lower() if char.isalnum() else "-" for char in source_name).strip("-")
        filename = (
            f"laporan-{file_stem or 'gradasi'}-"
            f"{datetime.now().strftime('%Y%m%d-%H%M')}.{extension}"
        )
        st.download_button(
            f"Unduh laporan {report_format}",
            data=report.getvalue(),
            file_name=filename,
            mime=mime_type,
            type="primary",
            key="download_report",
        )
    except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError) as error:
        st.error(f"Data tidak bisa diproses untuk laporan: {error}")
