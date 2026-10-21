"""Feature-owned schema and SQL, independent of the web framework."""


class BreathingStorage:
    def __init__(self, database):
        self.database = database

    def initialize(self):
        with self.database.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS skill_sessions (
                id TEXT PRIMARY KEY, pattern TEXT NOT NULL, status TEXT NOT NULL,
                started_at TEXT NOT NULL, ended_at TEXT NOT NULL, local_date TEXT NOT NULL,
                sequence_seconds REAL NOT NULL, active_seconds REAL NOT NULL,
                pause_seconds REAL NOT NULL, instruction_seconds REAL NOT NULL)""")


    def sessions(self):
        with self.database.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM skill_sessions ORDER BY started_at DESC, id")]

    def put_session(self, session_id, values):
        with self.database.connect() as db:
            result = db.execute("""INSERT INTO skill_sessions
                (id, pattern, status, started_at, ended_at, local_date, sequence_seconds, active_seconds, pause_seconds, instruction_seconds)
                VALUES (:id, :pattern, :status, :started_at, :ended_at, :local_date, :sequence_seconds, :active_seconds, :pause_seconds, :instruction_seconds)
                ON CONFLICT(id) DO NOTHING""", {**values, "id": session_id})
            return dict(db.execute("SELECT * FROM skill_sessions WHERE id = ?", (session_id,)).fetchone()), result.rowcount > 0
