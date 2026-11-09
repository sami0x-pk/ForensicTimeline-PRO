import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "forensic_pro.db"


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            investigator TEXT,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            added_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(case_id)
        );

        CREATE TABLE IF NOT EXISTS custody (
            custody_id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            person TEXT NOT NULL,
            notes TEXT,
            action_time TEXT NOT NULL,
            FOREIGN KEY(evidence_id) REFERENCES evidence(evidence_id)
        );

        CREATE TABLE IF NOT EXISTS audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            action_time TEXT NOT NULL
        );
        """)


def audit(action, details=""):
    with connect() as db:
        db.execute(
            "INSERT INTO audit(action, details, action_time) VALUES(?,?,?)",
            (action, str(details), now())
        )


def create_case(title, investigator, description):
    case_id = "FT-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    with connect() as db:
        db.execute("""
            INSERT INTO cases(case_id,title,investigator,description,status,created_at)
            VALUES(?,?,?,?,?,?)
        """, (case_id, title, investigator, description, "Open", now()))
    audit("CASE CREATED", f"{case_id}: {title}")
    return case_id


def list_cases():
    with connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM cases ORDER BY created_at DESC"
        ).fetchall()]


def update_case_status(case_id, status):
    with connect() as db:
        db.execute(
            "UPDATE cases SET status=? WHERE case_id=?",
            (status, case_id)
        )
    audit("CASE STATUS UPDATED", f"{case_id}: {status}")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_evidence(case_id, path, person, notes="Evidence registered"):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    digest = sha256_file(path)
    size = path.stat().st_size

    with connect() as db:
        cur = db.execute("""
            INSERT INTO evidence(case_id,filename,file_path,sha256,size_bytes,added_at)
            VALUES(?,?,?,?,?,?)
        """, (case_id, path.name, str(path), digest, size, now()))
        evidence_id = cur.lastrowid

        db.execute("""
            INSERT INTO custody(evidence_id,action,person,notes,action_time)
            VALUES(?,?,?,?,?)
        """, (evidence_id, "REGISTERED", person, notes, now()))

    audit("EVIDENCE REGISTERED", f"Evidence {evidence_id}, case {case_id}")
    return evidence_id, digest


def list_evidence(case_id=None):
    with connect() as db:
        if case_id:
            rows = db.execute("""
                SELECT * FROM evidence WHERE case_id=?
                ORDER BY added_at DESC
            """, (case_id,)).fetchall()
        else:
            rows = db.execute("""
                SELECT * FROM evidence ORDER BY added_at DESC
            """).fetchall()
        return [dict(row) for row in rows]


def verify_evidence(evidence_id):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM evidence WHERE evidence_id=?",
            (evidence_id,)
        ).fetchone()

    if not row:
        raise ValueError("Evidence record not found.")

    path = Path(row["file_path"])
    if not path.is_file():
        return {
            "exists": False,
            "match": False,
            "stored_hash": row["sha256"],
            "current_hash": None
        }

    current = sha256_file(path)
    match = current == row["sha256"]

    audit(
        "EVIDENCE VERIFIED",
        f"Evidence {evidence_id}: {'MATCH' if match else 'MISMATCH'}"
    )

    return {
        "exists": True,
        "match": match,
        "stored_hash": row["sha256"],
        "current_hash": current
    }


def add_custody(evidence_id, action, person, notes=""):
    with connect() as db:
        exists = db.execute(
            "SELECT evidence_id FROM evidence WHERE evidence_id=?",
            (evidence_id,)
        ).fetchone()

        if not exists:
            raise ValueError("Evidence record not found.")

        db.execute("""
            INSERT INTO custody(evidence_id,action,person,notes,action_time)
            VALUES(?,?,?,?,?)
        """, (evidence_id, action, person, notes, now()))

    audit("CUSTODY ACTION", f"Evidence {evidence_id}: {action}")


def list_custody(evidence_id=None):
    with connect() as db:
        if evidence_id:
            rows = db.execute("""
                SELECT * FROM custody WHERE evidence_id=?
                ORDER BY action_time ASC
            """, (evidence_id,)).fetchall()
        else:
            rows = db.execute("""
                SELECT * FROM custody ORDER BY action_time DESC
            """).fetchall()
        return [dict(row) for row in rows]


def list_audit(limit=500):
    with connect() as db:
        rows = db.execute("""
            SELECT * FROM audit ORDER BY audit_id DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]


def report_snapshot():
    return {
        "generated_at": now(),
        "cases": list_cases(),
        "evidence": list_evidence(),
        "custody": list_custody(),
        "audit": list_audit()
    }


init_db()
