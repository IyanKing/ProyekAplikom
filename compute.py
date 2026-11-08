"""Shared calculations for aggregate gradation and Marshall mix design."""

import numpy as np


def _number(value, default=None):
    if value is None or value == "" or isinstance(value, bool):
        return default
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def compute_gradation(state):
    count = state["n"]
    proportions = [_number(value, 0.0) for value in state["p"][:count]]
    total = sum(proportions)
    if total <= 0:
        raise ValueError("Total proporsi fraksi harus lebih besar dari 0%.")
    weights = [value / total for value in proportions]
    rows = []
    for row in state["rows"]:
        sieve = _number(row.get("d"))
        if sieve is None or sieve <= 0:
            continue
        passing_values = row.get("f")
        if not isinstance(passing_values, list):
            passing_values = []
        fractions = [
            _number(passing_values[index]) if index < len(passing_values) else None
            for index in range(count)
        ]
        minimum = _number(row.get("mn"))
        maximum = _number(row.get("mx"))
        passing = (
            sum(value * weight for value, weight in zip(fractions, weights))
            if all(value is not None for value in fractions)
            else None
        )
        meets = passing is not None and (
            (minimum is None or passing >= minimum - 1e-9)
            and (maximum is None or passing <= maximum + 1e-9)
        )
        rows.append({
            "d": sieve,
            "mn": minimum,
            "mx": maximum,
            "f": fractions,
            "P": passing,
            "ok": meets,
        })
    rows.sort(key=lambda row: row["d"], reverse=True)
    if not rows:
        raise ValueError("Tidak ada ukuran ayakan positif yang dapat dihitung.")
    return {"n": count, "p": proportions, "w": weights, "rows": rows}


def compute_marshall(state):
    marshall = state.get("mz")
    if not isinstance(marshall, dict):
        return None
    gravity = marshall.get("g")
    gravity = gravity if isinstance(gravity, dict) else {}
    bulk = _number(gravity.get("gsb"))
    effective = _number(gravity.get("gse"))
    asphalt = _number(gravity.get("gb"))
    multiplier = _number(gravity.get("pg"), 1.0) or 1.0
    if not (bulk and effective and asphalt and bulk > 0 and effective > 0 and asphalt > 0):
        return None

    raw_samples = marshall.get("rows")
    if not isinstance(raw_samples, list):
        return None
    samples = []
    for row in raw_samples:
        if not isinstance(row, dict):
            continue
        ka = _number(row.get("ka"))
        dry = _number(row.get("a"))
        ssd = _number(row.get("b"))
        immersed = _number(row.get("c"))
        stability = _number(row.get("st"))
        flow = _number(row.get("fl"))
        if (
            ka is None or not 0 <= ka < 100
            or dry is None or dry <= 0
            or ssd is None or immersed is None or ssd <= immersed
        ):
            continue
        denominator = (100 - ka) / effective + ka / asphalt
        if denominator <= 0:
            continue
        gmb = dry / (ssd - immersed)
        gmm = 100 / denominator
        vim = 100 * (gmm - gmb) / gmm
        vma = 100 - gmb * (100 - ka) / bulk
        vfa = 100 * (vma - vim) / vma if vma else None
        stability_result = stability * multiplier if stability is not None else None
        samples.append({
            "ka": ka,
            "a": dry,
            "b": ssd,
            "c": immersed,
            "gmb": gmb,
            "gmm": gmm,
            "vim": vim,
            "vma": vma,
            "vfa": vfa,
            "st": stability_result,
            "fl": flow,
            "mq": (
                stability_result / flow
                if stability_result is not None and flow is not None and flow != 0
                else None
            ),
        })
    if not samples:
        return None

    grouped = {}
    for sample in samples:
        grouped.setdefault(round(sample["ka"], 3), []).append(sample)
    averages = []
    metrics = ("gmb", "vim", "vma", "vfa", "st", "fl", "mq")
    for ka, group in sorted(grouped.items()):
        average = {"ka": ka, "n": len(group)}
        for metric in metrics:
            values = [sample[metric] for sample in group if sample[metric] is not None]
            average[metric] = sum(values) / len(values) if values else None
        averages.append(average)

    limits_data = marshall.get("lim")
    limits_data = limits_data if isinstance(limits_data, dict) else {}
    limits = {
        "vim": (_number(limits_data.get("vi1")), _number(limits_data.get("vi2"))),
        "vma": (_number(limits_data.get("vma")), None),
        "vfa": (_number(limits_data.get("vfa")), None),
        "st": (_number(limits_data.get("st")), None),
        "fl": (_number(limits_data.get("fl1")), _number(limits_data.get("fl2"))),
        "mq": (_number(limits_data.get("mq")), None),
    }
    return {
        "samples": samples,
        "A": averages,
        "lims": limits,
        "spec": marshall.get("sp", "AC-WC"),
    }


def find_kao(marshall):
    if marshall is None or len(marshall["A"]) < 2:
        return None
    averages = marshall["A"]
    x_values = np.array([row["ka"] for row in averages], dtype=float)
    if len(np.unique(x_values)) < 2:
        return None
    fits = {}
    for key, (minimum, maximum) in marshall["lims"].items():
        y_values = np.array(
            [row[key] if row[key] is not None else np.nan for row in averages],
            dtype=float,
        )
        valid = np.isfinite(y_values)
        if valid.sum() < 2:
            continue
        degree = min(2, int(valid.sum()) - 1)
        try:
            fits[key] = np.poly1d(np.polyfit(x_values[valid], y_values[valid], degree))
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue

    grid = np.linspace(x_values.min(), x_values.max(), 1000)
    valid_grid = np.ones(len(grid), dtype=bool)
    for key, (minimum, maximum) in marshall["lims"].items():
        fit = fits.get(key)
        if fit is None or (minimum is None and maximum is None):
            continue
        values = fit(grid)
        if minimum is not None:
            valid_grid &= values >= minimum - 1e-9
        if maximum is not None:
            valid_grid &= values <= maximum + 1e-9

    intervals = []
    start = None
    for index, valid in enumerate(valid_grid):
        if valid and start is None:
            start = index
        if not valid and start is not None:
            intervals.append((start, index - 1))
            start = None
    if start is not None:
        intervals.append((start, len(grid) - 1))
    if not intervals:
        return {"kao": None, "fits": fits, "range": None}
    first, last = max(intervals, key=lambda interval: interval[1] - interval[0])
    return {
        "kao": float((grid[first] + grid[last]) / 2),
        "fits": fits,
        "range": (float(grid[first]), float(grid[last])),
    }
