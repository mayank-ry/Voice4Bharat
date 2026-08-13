import sqlite3
import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "NyaAI_Memory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        language_pref TEXT,
        facts TEXT,
        last_interaction TEXT)

        """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        sip_address TEXT NOT NULL,
        topic TEXT,
        scheduled_time TEXT NOT NULL,
        status TEXT DEFAULT 'scheduled',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS calls (
    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    channel TEXT,
    started_at TEXT,
    ended_at TEXT,
    outcome TEXT DEFAULT 'in_progress',
    reason TEXT)
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    reason TEXT,
    summary TEXT,
    urgency TEXT,
    language TEXT,
    follow_up TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT)
    """)
def schedule_call(user_id: str, sip_address: str, topic: str, scheduled_time: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scheduled_calls (user_id, sip_address, topic, scheduled_time) VALUES (?, ?, ?, ?)",
        (user_id, sip_address, topic, scheduled_time)
    )
    conn.commit()
    conn.close()

def get_due_calls():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM scheduled_calls WHERE status='pending' AND scheduled_time <= ?",
        (datetime.now(timezone.utc).isoformat(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_call_done(call_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE scheduled_calls SET status='done' WHERE id=?", (call_id,))
    conn.commit()
    conn.close()

    conn.commit()
    conn.close()

def create_escalation_record(user_id, reason, summary, urgency, language, follow_up):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "INSERT INTO escalations (user_id, reason, summary, urgency, language, follow_up, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, reason, summary, urgency, language, follow_up, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    escalation_id = cur.lastrowid
    conn.close()
    return escalation_id

def start_call(user_id: str, channel: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "INSERT INTO calls (user_id, channel, started_at, outcome) VALUES (?, ?, ?, 'in_progress')",
        (user_id, channel, now)
    )
    conn.commit()
    call_id = cur.lastrowid
    conn.close()
    return call_id

def end_call(call_id: int, outcome: str, reason: str):
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE calls SET ended_at = ?, outcome = ?, reason = ? WHERE call_id = ?",
        (now, outcome, reason, call_id)
    )
    conn.commit()
    conn.close()

def get_call_stats():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) c FROM calls WHERE outcome != 'in_progress'").fetchone()["c"]
    success = conn.execute("SELECT COUNT(*) c FROM calls WHERE outcome = 'success'").fetchone()["c"]
    failed = conn.execute("SELECT COUNT(*) c FROM calls WHERE outcome = 'failed'").fetchone()["c"]
    recent = conn.execute("SELECT call_id, channel, started_at, ended_at, outcome, reason FROM calls WHERE outcome != 'in_progress' ORDER BY started_at DESC LIMIT 10").fetchall()
    conn.close()
    return {"total": total, "success": success, "failed": failed, "recent": [dict(r) for r in recent]}

def get_user(user_id:str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT user_id ,name,language_pref,facts,last_interaction FROM users
        WHERE user_id=?""",
        (user_id,)
    ).fetchone()

    conn.close()
    if not row:
        return None

    return {
        "User_ID":row['user_id'],
        "Name":row['name'],
        "Language_Preferance":row['language_pref'],
        "facts":json.loads(row['facts'] or "{}"),
        "Last_Interaction":row['last_interaction']
    }

def save_user(
    user_id: str,
    name: str | None,
    language_pref: str | None,
    facts: dict
):
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    existing = conn.execute(
        """
        SELECT name, language_pref, facts
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if existing:
        old_facts = json.loads(existing["facts"] or "{}")

        # Merge old + new facts
        for key, value in facts.items():

            if key not in old_facts:
                old_facts[key] = value

            elif isinstance(old_facts[key], list):
                if isinstance(value, list):
                    for item in value:
                        if item not in old_facts[key]:
                            old_facts[key].append(item)
                else:
                    if value not in old_facts[key]:
                        old_facts[key].append(value)

            else:
                old_facts[key] = value

        final_name = name or existing["name"]
        final_language = language_pref or existing["language_pref"]

        conn.execute(
            """
            UPDATE users
            SET name = ?,
                language_pref = ?,
                facts = ?,
                last_interaction = ?
            WHERE user_id = ?
            """,
            (
                final_name,
                final_language,
                json.dumps(old_facts, ensure_ascii=False),
                now,
                user_id
            )
        )

    else:
        conn.execute(
            """
            INSERT INTO users (
                user_id,
                name,
                language_pref,
                facts,
                last_interaction
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                language_pref,
                json.dumps(facts, ensure_ascii=False),
                now
            )
        )
    conn.commit()
    conn.close()