"""SQLite storage for the Lab 5 user API (sqlite3 is built into Python)."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

FIELDS = ("name", "email", "phone", "address", "country")
DEFAULT_DATABASE = Path(__file__).with_name("database.db")
INITIAL_USERS = (
    {"name": "Joseph Ghanem", "email": "jhg06@mail.aub.edu", "phone": "01000001", "address": "Beirut", "country": "Lebanon"},
    {"name": "John Doe", "email": "john@example.com", "phone": "01000002", "address": "Innsbruck", "country": "Austria"},
    {"name": "Jane Doe", "email": "jane@example.com", "phone": "01000003", "address": "Paris", "country": "France"},
)


def initialize_database(database=None):
    """Create and seed a new users table; preserve existing data on restart."""
    with closing(connect_to_db(database)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone()
        if exists:
            return
        conn.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        conn.executemany(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            [tuple(user[field] for field in FIELDS) for user in INITIAL_USERS],
        )


def connect_to_db(database=None):
    conn = sqlite3.connect(database or os.environ.get("DATABASE_PATH", DEFAULT_DATABASE))
    conn.row_factory = sqlite3.Row
    return conn


def create_db_table(database=None):
    with closing(connect_to_db(database)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)


def insert_user(user, database=None):
    with closing(connect_to_db(database)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            tuple(user[field] for field in FIELDS),
        )
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (cur.lastrowid,)).fetchone())


def get_users(database=None):
    with closing(connect_to_db(database)) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM users ORDER BY user_id")]


def get_user_by_id(user_id, database=None):
    with closing(connect_to_db(database)) as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_user(user, database=None):
    with closing(connect_to_db(database)) as conn, conn:
        cur = conn.execute(
            "UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
            tuple(user[field] for field in FIELDS) + (user["user_id"],),
        )
        if cur.rowcount == 0:
            return None
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user["user_id"],)).fetchone())


def patch_user(user_id, changes, database=None):
    """Update only supplied fields; column names come from a fixed allowlist."""
    fields = [field for field in FIELDS if field in changes]
    if not fields:
        raise ValueError("At least one user field is required.")
    assignments = ", ".join(f"{field} = ?" for field in fields)
    with closing(connect_to_db(database)) as conn, conn:
        cur = conn.execute(
            f"UPDATE users SET {assignments} WHERE user_id = ?",
            tuple(changes[field] for field in fields) + (user_id,),
        )
        if cur.rowcount == 0:
            return None
        return dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())


def delete_user(user_id, database=None):
    with closing(connect_to_db(database)) as conn, conn:
        return conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,)).rowcount > 0


if __name__ == "__main__":
    create_db_table()
    print("User table is ready.")

