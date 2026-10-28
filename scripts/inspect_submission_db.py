"""Read-only SQLite evidence. Default omits message contents; use fictional data."""
import argparse
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def inspect(path, include_messages=False):
    # mode=ro cannot create a missing database. No initialization or migration here.
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        result = {"database": str(path.resolve()), "tables": sorted(tables)}
        if "skill_sessions" in tables:
            result["breathing_sessions"] = [dict(row) for row in db.execute("""SELECT id, status, started_at, ended_at,
                active_seconds, sequence_seconds, pause_seconds, instruction_seconds
                FROM skill_sessions ORDER BY started_at DESC""")]
        if "chat_messages" in tables:
            result["conversations"] = [dict(row) for row in db.execute("""SELECT c.id, c.created_at,
                c.updated_at, COUNT(m.role) AS message_count FROM chat_conversations c
                JOIN chat_messages m ON m.conversation_id=c.id GROUP BY c.id ORDER BY c.updated_at DESC""")]
            if include_messages:
                result["messages"] = [dict(row) for row in db.execute("""SELECT conversation_id, turn_id,
                    position, role, content, created_at FROM chat_messages
                    ORDER BY conversation_id, position, CASE role WHEN 'user' THEN 0 ELSE 1 END""")]
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Inspect the isolated mocked-rehearsal database")
    parser.add_argument("--messages", action="store_true", help="Include message contents; fictional data only")
    args = parser.parse_args()
    path = ROOT / "backend" / "data" / ("submission-demo.sqlite3" if args.demo else "still.sqlite3")
    try:
        print(json.dumps(inspect(path, args.messages), indent=2, ensure_ascii=False))
    except sqlite3.Error:
        parser.exit(1, "Database unavailable. Start the appropriate server first; inspection does not create it.\n")
