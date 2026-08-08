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

    conn.commit()
    conn.close()

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