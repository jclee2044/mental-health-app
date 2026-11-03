"""Personal-memory SQL only; no embeddings, model calls, audio or book corpus."""
from datetime import datetime, timedelta, timezone
import time
from .domain import bundle, clipped
from .summary_storage import initialize_summaries, install_summary_triggers

DEFAULTS = {"emotions": False, "conversations": False, "facts": False}


class MemoryConflict(ValueError):
    pass


class MemoryStorage:
    def __init__(self, database):
        self.database = database

    def initialize(self):
        with self.database.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS personal_memory_preferences (
                id INTEGER PRIMARY KEY CHECK(id=1), emotions INTEGER NOT NULL,
                conversations INTEGER NOT NULL, facts INTEGER NOT NULL)""")
            if 'summary_epoch' not in {row['name'] for row in db.execute('PRAGMA table_info(personal_memory_preferences)')}:
                db.execute('ALTER TABLE personal_memory_preferences ADD COLUMN summary_epoch INTEGER NOT NULL DEFAULT 0')
            db.execute("INSERT OR IGNORE INTO personal_memory_preferences(id,emotions,conversations,facts) VALUES (1,0,0,0)")
            db.execute("""CREATE TABLE IF NOT EXISTS personal_memory_facts (
                id TEXT PRIMARY KEY, text TEXT NOT NULL, conversation_id TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS personal_memory_exclusions (
                kind TEXT NOT NULL CHECK(kind IN ('emotion','conversation')),
                source_id TEXT NOT NULL, PRIMARY KEY(kind,source_id))""")
            initialize_summaries(db)

    def finalize_initialize(self):
        # Installed after all feature schemas exist. Deletion is atomic with its
        # source, without importing memory logic into emotion/chat storage.
        with self.database.connect() as db:
            install_summary_triggers(db)
            db.execute("""CREATE TRIGGER IF NOT EXISTS personal_memory_delete_chat
                AFTER DELETE ON chat_conversations BEGIN
                DELETE FROM personal_memory_facts WHERE conversation_id=OLD.id;
                END""")

    @staticmethod
    def _preferences(db):
        row = db.execute("SELECT emotions,conversations,facts FROM personal_memory_preferences WHERE id=1").fetchone()
        return {key: bool(row[key]) for key in DEFAULTS} if row else dict(DEFAULTS)

    def preferences(self):
        with self.database.connect() as db:
            return self._preferences(db)

    def set_preferences(self, values):
        with self.database.connect() as db:
            db.execute("UPDATE personal_memory_preferences SET summary_epoch=summary_epoch + CASE WHEN conversations!=? THEN 1 ELSE 0 END, emotions=?,conversations=?,facts=? WHERE id=1",
                       (int(values['conversations']), *tuple(int(values[key]) for key in DEFAULTS)))
        return values

    def facts(self):
        with self.database.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM personal_memory_facts ORDER BY updated_at DESC,id")]

    def put_fact(self, fact_id, text, conversation_id=None):
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if conversation_id and (not db.execute("SELECT 1 FROM chat_conversations WHERE id=?", (conversation_id,)).fetchone()
                                    or db.execute("SELECT 1 FROM personal_memory_exclusions WHERE kind='conversation' AND source_id=?", (conversation_id,)).fetchone()):
                raise MemoryConflict("The source chat is missing or excluded from memory.")
            if not db.execute("SELECT 1 FROM personal_memory_facts WHERE id=?", (fact_id,)).fetchone() and db.execute("SELECT COUNT(*) FROM personal_memory_facts").fetchone()[0] >= 40:
                raise MemoryConflict("Keep at most 40 facts; forget one before adding another.")
            db.execute("""INSERT INTO personal_memory_facts VALUES (?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET text=excluded.text,
                conversation_id=excluded.conversation_id,updated_at=excluded.updated_at""",
                       (fact_id, text, conversation_id, now, now))
            return dict(db.execute("SELECT * FROM personal_memory_facts WHERE id=?", (fact_id,)).fetchone())

    def delete_fact(self, fact_id):
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT conversation_id FROM personal_memory_facts WHERE id=?", (fact_id,)).fetchone()
            if row is None:
                return False
            if row["conversation_id"]:
                db.execute("INSERT OR IGNORE INTO personal_memory_exclusions VALUES ('conversation',?)", (row["conversation_id"],))
                db.execute("DELETE FROM personal_memory_facts WHERE conversation_id=?", (row["conversation_id"],))
                db.execute("DELETE FROM personal_memory_summaries WHERE conversation_id=?", (row["conversation_id"],))
            else:
                db.execute("DELETE FROM personal_memory_facts WHERE id=?", (fact_id,))
            return True

    def exclusions(self):
        with self.database.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM personal_memory_exclusions ORDER BY kind,source_id")]

    def exclude(self, kind, source_id):
        with self.database.connect() as db:
            db.execute("INSERT OR IGNORE INTO personal_memory_exclusions VALUES (?,?)", (kind, source_id))
            if kind == "conversation":
                db.execute("DELETE FROM personal_memory_facts WHERE conversation_id=?", (source_id,))
                db.execute("DELETE FROM personal_memory_summaries WHERE conversation_id=?", (source_id,))

    def restore(self, kind, source_id):
        with self.database.connect() as db:
            db.execute("DELETE FROM personal_memory_exclusions WHERE kind=? AND source_id=?", (kind, source_id))

    def select(self, as_of, conversation_id=None, query=""):
        # No persistent derived text index: deletion/edits take effect on every
        # snapshot. One literal user excerpt represents each recent conversation.
        started = time.monotonic()
        with self.database.connect() as db:
            db.execute("PRAGMA busy_timeout=50")
            db.execute("PRAGMA temp_store=MEMORY")
            db.set_progress_handler(lambda: int(time.monotonic() - started > .12), 500)
            db.execute("BEGIN")
            preferences = self._preferences(db)
            sources = []
            if preferences["emotions"]:
                rows = db.execute("""SELECT * FROM (SELECT id,local_date,energy,pleasantness,note,color_meaning,recorded_at,
                    ROW_NUMBER() OVER (PARTITION BY local_date ORDER BY recorded_at DESC,id) AS daily_order FROM emotion_entries
                    WHERE local_date BETWEEN ? AND ? AND NOT EXISTS (
                        SELECT 1 FROM personal_memory_exclusions x WHERE x.kind='emotion' AND x.source_id=emotion_entries.id)
                    ) WHERE daily_order=1 ORDER BY local_date DESC LIMIT 7""",
                                  ((as_of - timedelta(days=6)).isoformat(), as_of.isoformat()))
                seen = set()
                for row in rows:
                    if row["local_date"] in seen:
                        continue
                    seen.add(row["local_date"])
                    sources.append({"kind": "emotion", "id": row["id"], "date": row["local_date"],
                                    "energy": row["energy"], "pleasantness": row["pleasantness"],
                                    "note": clipped(row["note"], 160), "personal_color_meaning": clipped(row["color_meaning"], 80)})
            if preferences["facts"]:
                for row in db.execute("""SELECT * FROM personal_memory_facts
                    WHERE conversation_id IS NULL OR (conversation_id != ? AND EXISTS (
                        SELECT 1 FROM chat_conversations c WHERE c.id=conversation_id))
                    ORDER BY updated_at DESC,id LIMIT 6""", (conversation_id or "",)):
                    sources.append({"kind": "fact", "id": row["id"], "date": row["updated_at"][:10],
                                    "text": row["text"], "conversation_id": row["conversation_id"], "origin": "user_confirmed"})
            if preferences["conversations"]:
                now = datetime.now(timezone.utc)
                rows = db.execute("""SELECT c.*,s.state AS summary_state,s.summary AS cached_summary,
                    s.input_shortened,s.source_date,s.expires_at FROM (SELECT * FROM (SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY conversation_id ORDER BY content_bytes DESC,created_at DESC,position DESC,ordinal DESC,turn_id
                    ) AS chosen FROM (
                    SELECT conversation_id,turn_id,position,0 AS ordinal,substr(content,1,700) AS text,
                        length(CAST(content AS BLOB)) AS content_bytes,created_at,'text' AS source
                    FROM chat_messages WHERE role='user' AND created_at BETWEEN ? AND ?
                    UNION ALL
                    SELECT conversation_id,turn_id,position,ordinal,substr(content,1,700) AS text,
                        length(CAST(content AS BLOB)) AS content_bytes,created_at,'voice' AS source
                    FROM chat_voice_messages WHERE role='user' AND created_at BETWEEN ? AND ?) m
                    WHERE conversation_id != ? AND NOT EXISTS (SELECT 1 FROM personal_memory_exclusions x
                        WHERE x.kind='conversation' AND x.source_id=m.conversation_id))
                    WHERE chosen=1) c LEFT JOIN personal_memory_summaries s ON c.conversation_id=s.conversation_id
                    ORDER BY c.created_at DESC,c.conversation_id""",
                                  ((now - timedelta(days=7)).isoformat(), now.isoformat(),
                                   (now - timedelta(days=7)).isoformat(), now.isoformat(), conversation_id or ""))
                skipped = 0
                for row in rows:
                    valid_cache = row['expires_at'] and row['expires_at'] >= now.isoformat()
                    if valid_cache and row['summary_state'] == 'empty':
                        skipped += 1
                        continue
                    if valid_cache and row['summary_state'] == 'ready' and row['cached_summary']:
                        sources.append({'kind': 'conversation', 'id': row['conversation_id'],
                                        'date': row['source_date'], 'text': row['cached_summary'],
                                        'source': 'model_summary', 'role': 'summary',
                                        'input_shortened': bool(row['input_shortened']), 'excerpt_truncated': False})
                        continue
                    text = clipped(row["text"], 700)
                    sources.append({"kind": "conversation", "id": row["conversation_id"], "turn_id": row["turn_id"],
                                    "ordinal": row["ordinal"], "date": row["created_at"][:10],
                                    "text": text, "source": row["source"], "role": "user",
                                    "excerpt_truncated": row["content_bytes"] > len(text.encode("utf-8"))})
            return preferences, bundle(sources, as_of.isoformat(), skipped_non_substantive=skipped if preferences['conversations'] else 0)
