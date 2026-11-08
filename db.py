"""SQLite persistence for uploaded mixture designs."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parent / "data" / "history.db"


@contextmanager
def _connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                spec TEXT,
                num_fractions INTEGER,
                num_sieves INTEGER NOT NULL,
                payload TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            )
            """
        )


def _serialize_payload(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise ValueError("Data harus berupa objek JSON dengan daftar rows.")
    if any(not isinstance(row, dict) for row in payload["rows"]):
        raise ValueError("Setiap baris ayakan harus berupa objek.")
    try:
        return json.dumps(payload, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("Data JSON berisi nilai yang tidak dapat disimpan.") from error


def save_design(name, payload, notes=""):
    name = name.strip() if isinstance(name, str) else ""
    notes = notes.strip() if isinstance(notes, str) else ""
    if not name:
        raise ValueError("Nama desain wajib diisi.")
    if len(name) > 100:
        raise ValueError("Nama desain maksimal 100 karakter.")
    if len(notes) > 2000:
        raise ValueError("Catatan maksimal 2.000 karakter.")

    init_db()
    serialized = _serialize_payload(payload)
    fractions = payload.get("n")
    if isinstance(fractions, bool) or not isinstance(fractions, int):
        fractions = None

    with _connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO designs
                (name, created_at, spec, num_fractions, num_sieves, payload, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                str(payload.get("sp", "")) or None,
                fractions,
                len(payload["rows"]),
                serialized,
                notes,
            ),
        )
        return cursor.lastrowid


def list_designs():
    init_db()
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, created_at, spec, num_fractions, num_sieves, notes
            FROM designs
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_design(design_id):
    init_db()
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM designs WHERE id = ?", (design_id,)
        ).fetchone()
    if row is None:
        return None

    design = dict(row)
    try:
        design["payload"] = json.loads(design["payload"])
    except json.JSONDecodeError as error:
        raise ValueError(f"Data desain #{design_id} rusak di database.") from error
    return design


def delete_design(design_id):
    init_db()
    with _connection() as connection:
        cursor = connection.execute(
            "DELETE FROM designs WHERE id = ?", (design_id,)
        )
    return cursor.rowcount > 0
