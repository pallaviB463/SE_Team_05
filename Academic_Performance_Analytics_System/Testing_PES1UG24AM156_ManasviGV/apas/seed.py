"""Load synthetic test data into an APAS database.

Usage:  python -m apas.seed <database path> [--synthetic N]
"""
import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

from .analytics import ASSESSMENTS
from .db import connect, init_schema
from .security import hash_password

DATA_FILE = Path(__file__).resolve().parent.parent / "test_data" / "apas_test_data.json"
SESSION_START = date(2026, 8, 3)


def session_dates(count, start=SESSION_START):
    days, d = [], start
    while len(days) < count:
        if d.weekday() < 5:
            days.append(d.isoformat())
        d += timedelta(days=1)
    return days


def load_dataset(conn, data=None):
    data = data or json.loads(DATA_FILE.read_text())
    init_schema(conn)
    now = "2026-10-01T00:00:00+00:00"
    for s in data["subjects"]:
        conn.execute("INSERT INTO subjects(code, name, semester, credits) VALUES (?, ?, ?, ?)",
                     (s["code"], s["name"], s["semester"], s["credits"]))
    for st in data["students"]:
        conn.execute("INSERT INTO students(id, name, email, program, current_semester, created_at, updated_at) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (st["id"], st["name"], st["email"], st["program"], st["current_semester"], now, now))
    for u in data["users"]:
        cur = conn.execute(
            "INSERT INTO users(username, full_name, password_hash, role, student_id, active) VALUES (?, ?, ?, ?, ?, ?)",
            (u["username"], u["full_name"], hash_password(u["password"]), u["role"], u.get("student_id"),
             1 if u.get("active", True) else 0))
        for code in u.get("subjects", []):
            conn.execute("INSERT INTO faculty_subjects(user_id, subject_code) VALUES (?, ?)", (cur.lastrowid, code))
    for st in data["students"]:
        insert_records(conn, st["id"], st["grades"], st["attendance"], now)
    conn.commit()


def insert_records(conn, student_id, grades, attendance, now):
    for code, (isa, esa) in grades.items():
        for assessment, score in (("ISA", isa), ("ESA", esa)):
            conn.execute("INSERT INTO grades(student_id, subject_code, assessment, score, max_score, updated_at) "
                         "VALUES (?, ?, ?, ?, ?, ?)", (student_id, code, assessment, score, ASSESSMENTS[assessment], now))
    for code, (present, total) in attendance.items():
        for i, day in enumerate(session_dates(total)):
            conn.execute("INSERT INTO attendance(student_id, subject_code, date, status) VALUES (?, ?, ?, ?)",
                         (student_id, code, day, "present" if i < present else "absent"))


def add_synthetic_students(conn, count, seed=2026, sessions=40):
    """Large synthetic cohort for performance testing (APAS-NF-001) and model evaluation."""
    rng = random.Random(seed)
    subjects = [dict(r) for r in conn.execute("SELECT * FROM subjects ORDER BY semester, code")]
    now = "2026-10-01T00:00:00+00:00"
    cohort = []
    for n in range(1, count + 1):
        sid = f"SYN{n:05d}"
        conn.execute("INSERT INTO students(id, name, email, program, current_semester, created_at, updated_at) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (sid, f"Synthetic Student {n}", f"syn{n}@apas.test", "B.Tech CSE (AI & ML)", 3, now, now))
        ability = rng.uniform(0.35, 0.95)
        drift = rng.uniform(-0.08, 0.06)
        grades = {}
        for s in subjects:
            level = min(0.99, max(0.05, ability + drift * (s["semester"] - 1) + rng.gauss(0, 0.04)))
            grades[s["code"]] = [round(50 * min(1, max(0, level + rng.gauss(0, 0.03)))),
                                 round(50 * min(1, max(0, level + rng.gauss(0, 0.03))))]
        rate = rng.uniform(0.5, 1.0)
        attendance = {s["code"]: [sum(rng.random() < rate for _ in range(sessions)), sessions]
                      for s in subjects if s["semester"] == 3}
        insert_records(conn, sid, grades, attendance, now)
        cohort.append(sid)
    conn.commit()
    return cohort


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("--synthetic", type=int, default=0)
    args = parser.parse_args()
    if Path(args.database).exists():
        raise SystemExit(f"{args.database} already exists; choose a new path")
    conn = connect(args.database)
    load_dataset(conn)
    if args.synthetic:
        add_synthetic_students(conn, args.synthetic)
    conn.close()
    print(f"Seeded {args.database}")


if __name__ == "__main__":
    main()
