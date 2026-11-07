import json
from datetime import datetime

import pandas as pd
import streamlit as st

st.title("Data Tersimpan")
st.caption(
    "Tinjau data gradasi, pengaturan JMF, dan data Marshall dari berkas JSON. "
    "Tampilan dan grafik mengikuti tema aplikasi."
)
st.markdown(
    """
Unggah berkas **Unduh JSON** dari halaman Kalkulator. Berkas dapat dimuat
kembali di Kalkulator untuk memulihkan data dan menghitung ulang hasilnya.
"""
)

uploaded_files = st.file_uploader(
    "Unggah satu atau beberapa file data (.json)",
    type=["json"],
    accept_multiple_files=True,
)


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


def _marshall_results(marshall):
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
        if ka is None or ka < 0 or dry is None or dry <= 0 or ssd is None or immersed is None or ssd <= immersed:
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
        })
    return results


def _show_marshall(marshall):
    st.markdown("#### Pengaturan dan batas Marshall")
    specification_names = {
        "AC-WC": "AC-WC",
        "AC-BC": "AC-BC",
        "AC-Base": "AC-Base",
        "Kustom": "Kustom",
    }
    spec = marshall.get("sp", "AC-WC")
    st.caption(f"Spesifikasi: **{specification_names.get(spec, spec)}**")

    gravity = marshall.get("g")
    if not isinstance(gravity, dict):
        gravity = {}
    gravity_labels = {
        "gsb": "BJ bulk agregat (Gsb)",
        "gse": "BJ efektif agregat (Gse)",
        "gb": "BJ aspal (Gb)",
        "pg": "Pengali stabilitas",
    }
    st.dataframe(
        pd.DataFrame([{"Parameter": label, "Nilai": gravity.get(field, "—")} for field, label in gravity_labels.items()]),
        width="stretch",
        hide_index=True,
    )

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
        st.dataframe(
            pd.DataFrame([
                {"Batas": label, "Nilai": limits.get(field, "—"), "Satuan": unit}
                for field, (label, unit) in limit_labels.items()
                if field in limits
            ]),
            width="stretch",
            hide_index=True,
        )

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
        st.dataframe(pd.DataFrame(raw_table), width="stretch", hide_index=True)
    else:
        st.info("Belum ada data benda uji Marshall pada berkas ini.")

    results = _marshall_results(marshall)
    if not results:
        st.info("Hasil Marshall belum dapat dihitung. Lengkapi data benda uji dan nilai Gsb, Gse, serta Gb.")
        return

    st.markdown("#### Hasil perhitungan Marshall")
    st.dataframe(pd.DataFrame(results), width="stretch", hide_index=True)
    average_columns = [
        "Gmb", "VIM (%)", "VMA (%)", "VFA (%)",
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
                    st.line_chart(
                        averages.set_index("KA (%)")[[field]],
                        x_label="Kadar aspal (%)",
                        y_label=label,
                        height=230,
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
    st.dataframe(pd.DataFrame(summary), width="stretch", hide_index=True)

    for index, name, data, raw in parsed:
        with st.expander(f"Detail: {name}"):
            cols = st.columns(3)
            cols[0].metric("Spesifikasi", str(data.get("sp", "—")))
            cols[1].metric("Fraksi", str(data.get("n", "—")))
            cols[2].metric("Ayakan", len(data["rows"]))

            if data["rows"]:
                st.markdown("### Data gradasi")
                gradation = _gradation_rows(data)
                st.dataframe(pd.DataFrame(gradation), width="stretch", hide_index=True)
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
                        st.line_chart(
                            chart_data,
                            x="Ayakan (mm)",
                            y=series,
                            x_label="Ayakan (dari terbesar ke terkecil)",
                            y_label="% lolos",
                            height=300,
                        )

            config = data.get("jm")
            if isinstance(config, dict):
                st.markdown("### Pengaturan rancangan campuran (JMF)")
                target_labels = {"mid": "Nilai tengah spesifikasi", "blend": "Campuran fraksi"}
                setting_rows = [
                    ("Kelompok", f"Kelompok {config.get('kg', '2')}"),
                    ("Kadar aspal (%)", config.get("ka", "—")),
                    ("Konstanta K", config.get("k", "—")),
                    ("Berat benda uji (g)", config.get("bt", "—")),
                    ("Target gradasi", target_labels.get(config.get("tg"), config.get("tg", "—"))),
                ]
                st.dataframe(
                    pd.DataFrame([{"Pengaturan": label, "Nilai": value} for label, value in setting_rows]),
                    width="stretch",
                    hide_index=True,
                )
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
                    st.dataframe(jmf_table, width="stretch", hide_index=True)
                    st.markdown("#### Berat tiap kelompok")
                    st.dataframe(pd.DataFrame(jmf["components"]), width="stretch", hide_index=True)
                else:
                    st.info("Rincian JMF belum dapat dihitung. Periksa target gradasi, ayakan, dan pengaturan JMF.")

            marshall = data.get("mz")
            if isinstance(marshall, dict):
                st.markdown("### Data Marshall")
                _show_marshall(marshall)

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
