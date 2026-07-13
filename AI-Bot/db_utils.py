"""
db_utils.py
-----------
Handles the local SQLite database that stores a history of every SQL query
the AI agent has generated and run against Athena. This is used to power the
password-protected "Query History" admin tab in the dashboard, so queries
never need to be shown to regular chat users but are still fully auditable.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query_history.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the query_history table if it doesn't exist yet."""
    conn = _get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT NOT NULL,
                user_question   TEXT NOT NULL,
                intent          TEXT,
                sql_query       TEXT,
                status          TEXT,
                error_message   TEXT,
                row_count       INTEGER
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def log_query(user_question, intent=None, sql_query=None, status="success",
              error_message=None, row_count=None):
    """Insert one row describing a chat turn / query execution."""
    conn = _get_conn()
    try:
        conn.execute(
            """
            INSERT INTO query_history
                (timestamp, user_question, intent, sql_query, status, error_message, row_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                user_question,
                intent,
                sql_query,
                status,
                error_message,
                row_count,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_history(limit=500):
    """Return the most recent query history rows as a list of dicts."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM query_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def clear_history():
    """Wipe the query history table. Used by the admin tab's Clear button."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM query_history")
        conn.commit()
    finally:
        conn.close()
