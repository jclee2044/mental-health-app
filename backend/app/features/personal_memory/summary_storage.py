"""Versioned summary claims. No model I/O runs inside a database transaction."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from .summary_domain import summary_input


def initialize_summaries(db):
    db.execute("""CREATE TABLE IF NOT EXISTS personal_memory_summaries (
        conversation_id TEXT PRIMARY KEY, revision INTEGER NOT NULL DEFAULT 0,
        state TEXT NOT NULL DEFAULT 'stale', summary TEXT,
        input_shortened INTEGER NOT NULL DEFAULT 0, updated_at TEXT,
        expires_at TEXT, source_date TEXT, job_token TEXT, job_revision INTEGER,
        job_epoch INTEGER)""")
    # A crashed process cannot claim that its interrupted paid task completed.
    db.execute("UPDATE personal_memory_summaries SET state='failed',job_token=NULL WHERE state='pending'")


def install_summary_triggers(db):
    for table in ("chat_messages", "chat_voice_messages"):
        for action in ("INSERT", "UPDATE"):
            db.execute(f"""CREATE TRIGGER IF NOT EXISTS personal_memory_summary_{table}_{action.lower()}
                AFTER {action} ON {table} BEGIN
                INSERT INTO personal_memory_summaries(conversation_id,revision) VALUES (NEW.conversation_id,1)
                ON CONFLICT(conversation_id) DO UPDATE SET revision=revision+1,state='stale',
                    summary=NULL,job_token=NULL,expires_at=NULL;
                END""")
    db.execute("""CREATE TRIGGER IF NOT EXISTS personal_memory_summary_delete_chat
        AFTER DELETE ON chat_conversations BEGIN
        DELETE FROM personal_memory_summaries WHERE conversation_id=OLD.id;
        END""")


class SummaryStorage:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def permitted(db, conversation_id):
        preferences = db.execute("SELECT conversations,summary_epoch FROM personal_memory_preferences WHERE id=1").fetchone()
        if not preferences or not preferences["conversations"]:
            return "off", None
        if db.execute("SELECT 1 FROM personal_memory_exclusions WHERE kind='conversation' AND source_id=?", (conversation_id,)).fetchone():
            return "excluded", None
        if not db.execute("SELECT 1 FROM chat_conversations WHERE id=?", (conversation_id,)).fetchone():
            return "missing", None
        return None, preferences["summary_epoch"]

    def status(self, conversation_id):
        with self.database.connect() as db:
            reason, _ = self.permitted(db, conversation_id)
            if reason:
                return {"status": reason}
            row = db.execute("SELECT state,expires_at,input_shortened FROM personal_memory_summaries WHERE conversation_id=?", (conversation_id,)).fetchone()
            state = row["state"] if row else "stale"
            if row and row["expires_at"] and row["expires_at"] < datetime.now(timezone.utc).isoformat():
                state = "stale"
            return {"status": state, "input_shortened": bool(row and row["input_shortened"])}

    def claim(self, conversation_id, retry=False):
        now = datetime.now(timezone.utc)
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            reason, epoch = self.permitted(db, conversation_id)
            if reason:
                return {"status": reason}
            db.execute("INSERT OR IGNORE INTO personal_memory_summaries(conversation_id) VALUES (?)", (conversation_id,))
            row = db.execute("SELECT * FROM personal_memory_summaries WHERE conversation_id=?", (conversation_id,)).fetchone()
            valid = row["expires_at"] and row["expires_at"] >= now.isoformat()
            if row["state"] in {"ready", "empty"} and valid:
                return {"status": row["state"], "cached": True}
            if row["state"] == "pending":
                return {"status": "pending"}
            if row["state"] == "failed" and not retry:
                return {"status": "failed"}
            rows = [dict(item) for item in db.execute("""SELECT content,created_at,source FROM (
                SELECT content,created_at,position,0 AS ordinal,'text' AS source FROM chat_messages WHERE conversation_id=? AND role='user'
                UNION ALL SELECT content,created_at,position,ordinal,'voice' AS source FROM chat_voice_messages WHERE conversation_id=? AND role='user'
                ) WHERE created_at BETWEEN ? AND ? ORDER BY position,ordinal""",
                                                   (conversation_id, conversation_id, (now - timedelta(days=7)).isoformat(), now.isoformat()))]
            if not rows:
                return {"status": "empty"}
            data, shortened = summary_input(rows)
            token = str(uuid4())
            expires_at = (min(datetime.fromisoformat(item["created_at"]) for item in rows) + timedelta(days=7)).isoformat()
            db.execute("""UPDATE personal_memory_summaries SET state='pending',summary=NULL,job_token=?,
                job_revision=revision,job_epoch=?,input_shortened=?,expires_at=?,source_date=? WHERE conversation_id=?""",
                       (token, epoch, int(shortened), expires_at, max(item["created_at"] for item in rows)[:10], conversation_id))
            return {"status": "claimed", "token": token, "input": data}

    def finish(self, conversation_id, token, summary=None, failed=False):
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            reason, epoch = self.permitted(db, conversation_id)
            row = db.execute("SELECT * FROM personal_memory_summaries WHERE conversation_id=?", (conversation_id,)).fetchone()
            if not row or row["job_token"] != token:
                return {"status": "discarded"}
            if reason or epoch != row["job_epoch"] or row["revision"] != row["job_revision"] or row["expires_at"] < now:
                db.execute("UPDATE personal_memory_summaries SET state='stale',summary=NULL,job_token=NULL WHERE conversation_id=? AND job_token=?", (conversation_id, token))
                return {"status": "discarded"}
            state = "failed" if failed else "ready" if summary else "empty"
            db.execute("UPDATE personal_memory_summaries SET state=?,summary=?,updated_at=?,job_token=NULL WHERE conversation_id=? AND job_token=?",
                       (state, summary if state == "ready" else None, now, conversation_id, token))
            return {"status": state, "cached": False, "input_shortened": bool(row["input_shortened"])}
