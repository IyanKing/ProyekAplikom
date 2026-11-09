"""Load and validate versioned mixture specification presets."""

import json
import math
from pathlib import Path


SPECIFICATIONS_PATH = Path(__file__).resolve().with_name("specs.json")
MARSHALL_LIMIT_KEYS = ("vi1", "vi2", "vma", "vfa", "st", "fl1", "fl2", "mq")


def load_specifications(path=SPECIFICATIONS_PATH):
    """Load specification presets, rejecting malformed or incomplete entries."""
    try:
        with Path(path).open(encoding="utf-8") as source_file:
            data = json.load(source_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"File spesifikasi tidak dapat dibaca: {error}") from error

    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Format specs.json tidak didukung (schema_version harus 1).")
    versions = data.get("versions")
    default_version = data.get("default_version")
    if (
        not isinstance(versions, dict)
        or not versions
        or not isinstance(default_version, str)
        or default_version not in versions
    ):
        raise ValueError("specs.json harus memiliki default_version yang tersedia.")

    for version_id, version in versions.items():
        if not isinstance(version_id, str) or not version_id:
            raise ValueError("Setiap ID versi spesifikasi harus berupa teks.")
        if not isinstance(version, dict):
            raise ValueError(f"Versi {version_id} harus berupa objek.")
        if not all(
            isinstance(version.get(key), str) and version[key].strip()
            for key in ("name", "source")
        ):
            raise ValueError(f"Versi {version_id} harus memiliki name dan source.")

        gradation = version.get("gradation")
        if not isinstance(gradation, dict) or not gradation:
            raise ValueError(f"Versi {version_id} tidak memiliki batas gradasi.")
        for mix_type, rows in gradation.items():
            if not isinstance(mix_type, str) or not mix_type:
                raise ValueError(f"Versi {version_id} memiliki nama campuran kosong.")
            if not isinstance(rows, list) or not rows:
                raise ValueError(
                    f"Batas gradasi {mix_type} pada {version_id} harus berupa daftar."
                )
            previous_sieve = math.inf
            for row in rows:
                if not isinstance(row, list) or len(row) != 3:
                    raise ValueError(
                        f"Setiap batas {mix_type} pada {version_id} "
                        "harus [ayakan, minimum, maksimum]."
                    )
                sieve, minimum, maximum = row
                if (
                    not all(_is_finite_number(value) for value in row)
                    or sieve <= 0
                    or sieve >= previous_sieve
                    or not 0 <= minimum <= maximum <= 100
                ):
                    raise ValueError(
                        f"Nilai/urutan batas gradasi {mix_type} pada {version_id} tidak valid."
                    )
                previous_sieve = sieve

        marshall = version.get("marshall")
        if not isinstance(marshall, dict) or not marshall:
            raise ValueError(f"Versi {version_id} tidak memiliki batas Marshall.")
        for mix_type, limits in marshall.items():
            if mix_type not in gradation or not isinstance(limits, dict):
                raise ValueError(
                    f"Batas Marshall {mix_type} pada {version_id} tidak valid."
                )
            if set(limits) != set(MARSHALL_LIMIT_KEYS):
                raise ValueError(
                    f"Batas Marshall {mix_type} pada {version_id} "
                    f"harus memiliki kunci {', '.join(MARSHALL_LIMIT_KEYS)}."
                )
            if any(
                not _is_finite_number(limits[key])
                for key in MARSHALL_LIMIT_KEYS if key != "mq"
            ) or (
                limits["mq"] is not None
                and not _is_finite_number(limits["mq"])
            ):
                raise ValueError(
                    f"Batas Marshall {mix_type} pada {version_id} harus berupa "
                    "angka atau null."
                )
            if (
                limits["vi1"] > limits["vi2"]
                or limits["fl1"] > limits["fl2"]
                or any(
                    not 0 <= limits[key] <= 100
                    for key in ("vi1", "vi2", "vma", "vfa")
                )
                or any(limits[key] < 0 for key in ("st", "fl1", "fl2"))
                or (limits["mq"] is not None and limits["mq"] < 0)
            ):
                raise ValueError(
                    f"Nilai batas Marshall {mix_type} pada {version_id} tidak valid."
                )
    return data


def specification_version_name(specifications, version_id):
    """Return a display name while preserving unknown historical version IDs."""
    versions = specifications.get("versions", {})
    version = versions.get(version_id) if isinstance(version_id, str) else None
    return version["name"] if isinstance(version, dict) else (
        version_id if isinstance(version_id, str) else "versi tidak diketahui"
    )


def _is_finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
