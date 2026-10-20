"""Authentication Service and Audit Logging Service (SAD 3.4 items 5 and 14)."""
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import current_app, g, jsonify, redirect, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

# APAS-SR-004: approved password-hashing algorithm (PBKDF2-HMAC-SHA256,
# 600 000 iterations as recommended by OWASP), random 16-byte salt per user.
PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"
SENSITIVE_KEYS = ("password", "token", "secret")


def utcnow():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def hash_password(password):
    return generate_password_hash(password, method=PASSWORD_HASH_METHOD, salt_length=16)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def _token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


# --------------------------------------------------------------------------
# Audit logging (APAS-NF-004, APAS-SR-005)
# --------------------------------------------------------------------------
def _scrub(details):
    if isinstance(details, dict):
        return {k: ("***" if any(s in k.lower() for s in SENSITIVE_KEYS) else _scrub(v))
                for k, v in details.items()}
    return details


def audit(event_type, outcome="success", entity=None, details=None, user=None, username=None):
    user = user if user is not None else getattr(g, "user", None)
    db = get_db()
    db.execute(
        "INSERT INTO audit_log(ts, user_id, username, event_type, entity, outcome, details, ip) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            iso(utcnow()),
            user["id"] if user else None,
            user["username"] if user else username,
            event_type,
            entity,
            outcome,
            json.dumps(_scrub(details or {}), sort_keys=True),
            request.remote_addr if request else None,
        ),
    )
    db.commit()


def subtract_months(dt, months):
    month_index = dt.month - 1 - months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    # Clamp the day for shorter months (e.g. 31 March - 1 month -> 28/29 Feb).
    for day in (dt.day, 30, 29, 28):
        try:
            return dt.replace(year=year, month=month, day=day)
        except ValueError:
            continue
    raise ValueError("invalid date")


def purge_audit_log(conn, retention_months, now=None):
    """Delete audit entries older than the retention period.

    The SRS (APAS-NF-004) requires at least 12 months of retention, so any
    configured value below 12 is raised to 12.
    """
    months = max(int(retention_months), current_app.config["AUDIT_MIN_RETENTION_MONTHS"])
    cutoff = subtract_months(now or utcnow(), months)
    cur = conn.execute("DELETE FROM audit_log WHERE ts < ?", (iso(cutoff),))
    conn.commit()
    return cur.rowcount


# --------------------------------------------------------------------------
# Sessions (APAS-F-001, APAS-F-003)
# --------------------------------------------------------------------------
def authenticate(username, password):
    """Return (user_row, error_message)."""
    db = get_db()
    cfg = current_app.config
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    generic = "Invalid username or password"
    if user is None:
        # Run a hash anyway so response timing does not reveal valid usernames.
        verify_password(current_app.config["DUMMY_HASH"], password)
        audit("auth.login", "failure", details={"reason": "unknown user"}, user=False, username=username)
        return None, generic
    if not user["active"]:
        audit("auth.login", "failure", details={"reason": "inactive account"}, user=user)
        return None, generic
    if user["locked_until"] and datetime.fromisoformat(user["locked_until"]) > utcnow():
        audit("auth.login", "failure", details={"reason": "account locked"}, user=user)
        return None, "Account temporarily locked after repeated failed attempts. Try again later."
    if not verify_password(user["password_hash"], password):
        attempts = user["failed_attempts"] + 1
        locked_until = None
        if attempts >= cfg["MAX_FAILED_LOGINS"]:
            locked_until = iso(utcnow() + timedelta(minutes=cfg["LOCKOUT_MINUTES"]))
            attempts = 0
        db.execute("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
                   (attempts, locked_until, user["id"]))
        db.commit()
        audit("auth.login", "failure", details={"reason": "wrong password",
                                                 "locked": bool(locked_until)}, user=user)
        return None, generic
    db.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?", (user["id"],))
    db.commit()
    audit("auth.login", "success", user=user)
    return user, None


def create_session(user):
    token = secrets.token_urlsafe(32)
    now = iso(utcnow())
    db = get_db()
    db.execute("INSERT INTO sessions(token_hash, user_id, created_at, last_seen) VALUES (?, ?, ?, ?)",
               (_token_hash(token), user["id"], now, now))
    db.commit()
    return token


def end_session(token):
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))
    db.commit()


def request_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return request.cookies.get(current_app.config["SESSION_COOKIE"])


def current_user():
    token = request_token()
    if not token:
        return None
    db = get_db()
    row = db.execute(
        "SELECT s.token_hash, s.last_seen, u.* FROM sessions s JOIN users u ON u.id = s.user_id "
        "WHERE s.token_hash = ?", (_token_hash(token),)).fetchone()
    if row is None or not row["active"]:
        return None
    idle = timedelta(minutes=current_app.config["SESSION_IDLE_MINUTES"])
    since = utcnow() - datetime.fromisoformat(row["last_seen"])
    if since > idle:
        db.execute("DELETE FROM sessions WHERE token_hash = ?", (row["token_hash"],))
        db.commit()
        return None
    if since > timedelta(seconds=60):
        # Throttled so read-only requests do not contend for the database write lock (DEF-002).
        db.execute("UPDATE sessions SET last_seen = ? WHERE token_hash = ?", (iso(utcnow()), row["token_hash"]))
        db.commit()
    return row


def api_error(status, message):
    resp = jsonify({"error": message, "status": status})
    resp.status_code = status
    return resp


def login_required(*roles, html=False):
    """Authorization check enforced on the server (SAD 3.9.2)."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                if html:
                    return redirect(url_for("web.login_page"))
                return api_error(401, "Authentication required")
            g.user = user
            if roles and user["role"] not in roles:
                audit("access.denied", "failure", entity=request.path,
                      details={"method": request.method, "role": user["role"]})
                return api_error(403, "You do not have permission to perform this operation")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def can_view_student(user, student_id):
    if user["role"] in ("admin", "faculty"):
        return True
    return user["role"] == "student" and user["student_id"] == student_id


def faculty_teaches(user, subject_code):
    if user["role"] != "faculty":
        return False
    row = get_db().execute("SELECT 1 FROM faculty_subjects WHERE user_id = ? AND subject_code = ?",
                           (user["id"], subject_code)).fetchone()
    return row is not None
