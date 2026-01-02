from __future__ import annotations
import sqlite3
from datetime import date
from .utils import iso

DB_NAME = "productivity_calendar.db"

class Repo:
    def __init__(self, db_name: str = DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS day_entries (
                date_iso TEXT PRIMARY KEY,
                color_state INTEGER NOT NULL,
                percent INTEGER NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        self.conn.commit()
        self._ensure_default("theme", "light")
        self._ensure_default("month_goal", "80")
        self._ensure_default("week_goal", "80")

    def _ensure_default(self, key: str, value: str) -> None:
        if self.get_setting(key) is None:
            self.set_setting(key, value)

    def upsert_day(self, d: date, color_state: int, percent: int) -> None:
        self.conn.execute("""
            INSERT INTO day_entries(date_iso, color_state, percent)
            VALUES(?, ?, ?)
            ON CONFLICT(date_iso) DO UPDATE SET
                color_state=excluded.color_state,
                percent=excluded.percent
        """, (iso(d), int(color_state), int(percent)))
        self.conn.commit()

    def get_day(self, d: date) -> tuple[int, int]:
        cur = self.conn.execute("SELECT color_state, percent FROM day_entries WHERE date_iso=?", (iso(d),))
        row = cur.fetchone()
        return (0, -1) if row is None else (int(row[0]), int(row[1]))

    def get_range(self, start: date, end: date):
        cur = self.conn.execute("""
            SELECT date_iso, color_state, percent
            FROM day_entries
            WHERE date_iso BETWEEN ? AND ?
        """, (iso(start), iso(end)))
        return cur.fetchall()

    def get_setting(self, key: str):
        cur = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute("""
            INSERT INTO settings(key, value) VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, str(value)))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
