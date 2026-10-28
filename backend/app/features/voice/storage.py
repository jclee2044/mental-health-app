"""Atomic typed pairs and approximate voice transcript batches; no provider I/O."""
from datetime import datetime, timezone


class ConversationConflict(ValueError):
    pass


class ChatStorage:
    def __init__(self, database):
        self.database = database

    def initialize(self):
        with self.database.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS chat_conversations (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
                conversation_id TEXT NOT NULL, turn_id TEXT NOT NULL,
                position INTEGER NOT NULL CHECK(position BETWEEN 0 AND 99),
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY(conversation_id, position, role), UNIQUE(turn_id, role),
                FOREIGN KEY(conversation_id) REFERENCES chat_conversations(id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS chat_voice_messages (
                conversation_id TEXT NOT NULL, turn_id TEXT NOT NULL,
                position INTEGER NOT NULL CHECK(position BETWEEN 0 AND 99),
                ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 0 AND 49),
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY(conversation_id, position, ordinal), UNIQUE(turn_id, ordinal),
                FOREIGN KEY(conversation_id) REFERENCES chat_conversations(id))""")

    def save_turn(self, conversation_id, turn_id, values):
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as db:
            # Serialize read/compare/write and deletion, including concurrent retries.
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM chat_voice_messages WHERE turn_id=? OR (conversation_id=? AND position=?)",
                          (turn_id, conversation_id, values["position"])).fetchone():
                raise ConversationConflict()
            existing = [dict(row) for row in db.execute(
                "SELECT * FROM chat_messages WHERE turn_id = ?", (turn_id,))]
            if existing:
                if len(existing) != 2 or any(
                    row["conversation_id"] != conversation_id or
                    row["position"] != values["position"] or
                    row["content"] != values[row["role"]] for row in existing
                ):
                    raise ConversationConflict()
                return False
            if db.execute("SELECT 1 FROM chat_messages WHERE conversation_id = ? AND position = ?",
                          (conversation_id, values["position"])).fetchone():
                raise ConversationConflict()
            db.execute("INSERT INTO chat_conversations VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at",
                       (conversation_id, now, now))
            db.executemany("INSERT INTO chat_messages VALUES (?, ?, ?, ?, ?, ?)", [
                (conversation_id, turn_id, values["position"], role, values[role], now)
                for role in ("user", "assistant")])
        return True

    def save_voice_turn(self, conversation_id, turn_id, values):
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM chat_messages WHERE turn_id=? OR (conversation_id=? AND position=?)",
                          (turn_id, conversation_id, values["position"])).fetchone():
                raise ConversationConflict()
            existing = [dict(row) for row in db.execute(
                "SELECT * FROM chat_voice_messages WHERE turn_id=? ORDER BY ordinal", (turn_id,))]
            if existing:
                if len(existing) != len(values["messages"]) or any(
                    row["conversation_id"] != conversation_id or row["position"] != values["position"] or
                    row["role"] != message["role"] or row["content"] != message["content"]
                    for row, message in zip(existing, values["messages"])
                ):
                    raise ConversationConflict()
                return False
            if db.execute("SELECT 1 FROM chat_voice_messages WHERE conversation_id=? AND position=?",
                          (conversation_id, values["position"])).fetchone():
                raise ConversationConflict()
            db.execute("INSERT INTO chat_conversations VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at",
                       (conversation_id, now, now))
            db.executemany("INSERT INTO chat_voice_messages VALUES (?, ?, ?, ?, ?, ?, ?)", [
                (conversation_id, turn_id, values["position"], i, message["role"], message["content"], now)
                for i, message in enumerate(values["messages"])])
        return True

    def conversations(self):
        with self.database.connect() as db:
            return [dict(row) for row in db.execute("""SELECT c.*, COUNT(m.role) AS message_count
                FROM chat_conversations c JOIN (
                    SELECT conversation_id, role FROM chat_messages UNION ALL
                    SELECT conversation_id, role FROM chat_voice_messages
                ) m ON c.id=m.conversation_id
                GROUP BY c.id ORDER BY c.updated_at DESC, c.id""")]

    def conversation(self, conversation_id):
        with self.database.connect() as db:
            # One read transaction keeps header and messages consistent with deletion.
            db.execute("BEGIN")
            header = db.execute("SELECT * FROM chat_conversations WHERE id=?", (conversation_id,)).fetchone()
            if header is None:
                return None
            messages = [dict(row) for row in db.execute("""SELECT turn_id, position, role, content, created_at, source FROM (
                SELECT turn_id, position, role, content, created_at, 'text' AS source,
                    CASE role WHEN 'user' THEN 0 ELSE 1 END AS ordinal FROM chat_messages WHERE conversation_id=?
                UNION ALL
                SELECT turn_id, position, role, content, created_at, 'voice' AS source, ordinal
                    FROM chat_voice_messages WHERE conversation_id=?
                ) ORDER BY position, ordinal""", (conversation_id, conversation_id))]
            return {**dict(header), "message_count": len(messages), "messages": messages}

    def delete(self, conversation_id):
        with self.database.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM chat_messages WHERE conversation_id=?", (conversation_id,))
            db.execute("DELETE FROM chat_voice_messages WHERE conversation_id=?", (conversation_id,))
            return db.execute("DELETE FROM chat_conversations WHERE id=?", (conversation_id,)).rowcount > 0
