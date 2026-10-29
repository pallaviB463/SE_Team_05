"""Data layer for APAS (SAD 3.5 - Data Layer / Repository).

SQLite is used as the relational store for the test build. The schema mirrors
the data stores listed in SAD 3.6: users and roles, student academic records,
attendance, configuration thresholds and audit logs.
"""
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    email            TEXT NOT NULL UNIQUE,
    program          TEXT NOT NULL,
    current_semester INTEGER NOT NULL CHECK (current_semester BETWEEN 1 AND 8),
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('admin', 'faculty', 'student')),
    student_id      TEXT REFERENCES students(id),
    active          INTEGER NOT NULL DEFAULT 1,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT
);

CREATE TABLE IF NOT EXISTS subjects (
    code     TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    semester INTEGER NOT NULL,
    credits  INTEGER NOT NULL CHECK (credits > 0)
);

CREATE TABLE IF NOT EXISTS faculty_subjects (
    user_id      INTEGER NOT NULL REFERENCES users(id),
    subject_code TEXT NOT NULL REFERENCES subjects(code),
    PRIMARY KEY (user_id, subject_code)
);

CREATE TABLE IF NOT EXISTS grades (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   TEXT NOT NULL REFERENCES students(id),
    subject_code TEXT NOT NULL REFERENCES subjects(code),
    assessment   TEXT NOT NULL,
    score        REAL NOT NULL,
    max_score    REAL NOT NULL,
    recorded_by  INTEGER REFERENCES users(id),
    updated_at   TEXT NOT NULL,
    UNIQUE (student_id, subject_code, assessment)
);

CREATE TABLE IF NOT EXISTS attendance (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   TEXT NOT NULL REFERENCES students(id),
    subject_code TEXT NOT NULL REFERENCES subjects(code),
    date         TEXT NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('present', 'absent')),
    recorded_by  INTEGER REFERENCES users(id),
    UNIQUE (student_id, subject_code, date)
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    last_seen  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT NOT NULL,
    user_id    INTEGER,
    username   TEXT,
    event_type TEXT NOT NULL,
    entity     TEXT,
    outcome    TEXT NOT NULL,
    details    TEXT,
    ip         TEXT
);

-- Audit records are append-only (SAD 3.9.6: protected against modification).
CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only');
END;

-- Incremented by triggers on every change to data used by analytics; lets the
-- dashboard reuse cached results until the data changes (DEF-002).
CREATE TABLE IF NOT EXISTS data_version (
    id      INTEGER PRIMARY KEY CHECK (id = 1),
    version INTEGER NOT NULL
);
INSERT OR IGNORE INTO data_version(id, version) VALUES (1, 0);

CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts);
"""

DEFAULT_THRESHOLDS = {
    "min_attendance_pct": 75.0,     # APAS-F-009 attendance threshold
    "min_performance_pct": 50.0,    # APAS-F-009 performance threshold
    "risk_high_sgpa": 5.0,          # APAS-F-014 predicted SGPA below this -> high risk
    "risk_medium_sgpa": 6.0,        # APAS-F-014 predicted SGPA below this -> medium risk
    "risk_high_attendance_pct": 65.0,
}


def connect(path):
    conn = sqlite3.connect(path, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


VERSIONED_TABLES = ("students", "subjects", "grades", "attendance", "config")


def init_schema(conn):
    conn.executescript(SCHEMA)
    for table in VERSIONED_TABLES:
        for op in ("INSERT", "UPDATE", "DELETE"):
            conn.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_{op.lower()}_version AFTER {op} ON {table} "
                         "BEGIN UPDATE data_version SET version = version + 1 WHERE id = 1; END")
    for key, value in DEFAULT_THRESHOLDS.items():
        conn.execute("INSERT OR IGNORE INTO config(key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def get_thresholds(conn):
    rows = conn.execute("SELECT key, value FROM config").fetchall()
    values = dict(DEFAULT_THRESHOLDS)
    values.update({r["key"]: r["value"] for r in rows})
    return values


def data_version(conn):
    return conn.execute("SELECT version FROM data_version WHERE id = 1").fetchone()[0]
