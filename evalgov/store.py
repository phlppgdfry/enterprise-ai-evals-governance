import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class Store:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, report TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, at TEXT NOT NULL, actor TEXT NOT NULL,
              action TEXT NOT NULL, subject TEXT NOT NULL);
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        try:
            with db:
                yield db
        finally:
            db.close()

    def save(self, report: dict, actor: str):
        with self.connection() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?)", (report["run_id"], report["created_at"], json.dumps(report)))
            db.execute("INSERT INTO audit(at,actor,action,subject) VALUES(?,?,?,?)",
                       (report["created_at"], actor, "evaluate", report["run_id"]))

    def get(self, run_id: str):
        with self.connection() as db:
            row = db.execute("SELECT report FROM runs WHERE id=?", (run_id,)).fetchone()
            return json.loads(row[0]) if row else None

    def list_runs(self):
        with self.connection() as db:
            rows = db.execute("SELECT id, created_at, report FROM runs ORDER BY created_at DESC LIMIT 100")
            return [{"id": row["id"], "created_at": row["created_at"],
                     "passed": json.loads(row["report"])["summary"]["passed"],
                     "target": json.loads(row["report"])["target"]} for row in rows]

    def audit(self):
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 100")]

    def record(self, actor: str, action: str, subject: str):
        with self.connection() as db:
            db.execute("INSERT INTO audit(at,actor,action,subject) VALUES(?,?,?,?)",
                       (datetime.now(timezone.utc).isoformat(), actor, action, subject))
