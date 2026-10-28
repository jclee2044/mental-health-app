"""Feature-owned schema and SQL, independent of the web framework."""
from datetime import datetime, timezone


class EmotionStorage:
    def __init__(self, database):
        self.database = database

    def initialize(self):
        with self.database.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS emotion_entries (
                id TEXT PRIMARY KEY, feeling INTEGER NOT NULL, color TEXT NOT NULL,
                color_meaning TEXT NOT NULL, pleasantness INTEGER NOT NULL, energy INTEGER NOT NULL,
                note TEXT NOT NULL, recorded_at TEXT NOT NULL, local_date TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")

    @staticmethod
    def project(row):
        record = dict(row)
        # Zero is an internal absence marker, never a reported emotion.
        if record["feeling"] == 0:
            record["feeling"] = None
        return record

    def entries(self):
        with self.database.connect() as db:
            return [self.project(row) for row in db.execute("SELECT * FROM emotion_entries ORDER BY recorded_at DESC, id")]

    def entry(self, entry_id):
        with self.database.connect() as db:
            row = db.execute("SELECT * FROM emotion_entries WHERE id = ?", (entry_id,)).fetchone()
            return self.project(row) if row else None

    def put_entry(self, entry_id, values):
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as db:
            existing = db.execute("SELECT * FROM emotion_entries WHERE id = ?", (entry_id,)).fetchone()
            record = {**values, "id": entry_id, "created_at": now, "updated_at": now}
            if existing:
                for key in ("created_at", "recorded_at", "local_date"):
                    record[key] = existing[key]
            db.execute("""INSERT INTO emotion_entries
                (id, feeling, color, color_meaning, pleasantness, energy, note, recorded_at, local_date, created_at, updated_at)
                VALUES (:id, :feeling, :color, :color_meaning, :pleasantness, :energy, :note, :recorded_at, :local_date, :created_at, :updated_at)
                ON CONFLICT(id) DO UPDATE SET feeling=excluded.feeling, color=excluded.color,
                color_meaning=excluded.color_meaning, pleasantness=excluded.pleasantness, energy=excluded.energy,
                note=excluded.note, updated_at=excluded.updated_at""", {**record, "feeling": record["feeling"] if record["feeling"] is not None else 0})
        return record, existing is None

    def delete_entry(self, entry_id):
        with self.database.connect() as db:
            return db.execute("DELETE FROM emotion_entries WHERE id = ?", (entry_id,)).rowcount > 0
