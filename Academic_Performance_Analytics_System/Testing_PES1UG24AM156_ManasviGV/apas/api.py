"""REST API (SAD 4.3.1 proposed endpoints) - API Gateway / Application Controller."""
import csv
import io
import math
import re
import threading
from datetime import date

from flask import Blueprint, Response, current_app, g, jsonify, request

from . import analytics
from .db import data_version, get_db, get_thresholds
from .security import (api_error, audit, authenticate, can_view_student, create_session, end_session,
                       faculty_teaches, iso, login_required, request_token, utcnow)

bp = Blueprint("api", __name__, url_prefix="/api")

STUDENT_ID_RE = re.compile(r"^[A-Z0-9]{6,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def student_or_404(student_id):
    row = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return dict(row) if row else None


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


# --------------------------------------------------------------------------
# Health (used by availability monitoring, APAS-NF-002)
# --------------------------------------------------------------------------
@bp.get("/health")
def health():
    get_db().execute("SELECT 1").fetchone()
    return jsonify({"status": "ok", "time": iso(utcnow())})


# --------------------------------------------------------------------------
# Authentication (APAS-F-001, APAS-F-003, APAS-SR-001)
# --------------------------------------------------------------------------
@bp.post("/auth/login")
def login():
    data = body()
    if not data or not isinstance(data.get("username"), str) or not isinstance(data.get("password"), str) \
            or not data["username"].strip() or not data["password"]:
        return api_error(400, "Username and password are required")
    user, error = authenticate(data["username"].strip(), data["password"])
    if user is None:
        return api_error(401, error)
    token = create_session(user)
    resp = jsonify({"token": token, "user": {"username": user["username"], "role": user["role"],
                                             "full_name": user["full_name"],
                                             "student_id": user["student_id"]}})
    resp.set_cookie(current_app.config["SESSION_COOKIE"], token, httponly=True, samesite="Lax",
                    secure=current_app.config["ENFORCE_HTTPS"])
    return resp


@bp.post("/auth/logout")
@login_required()
def logout():
    end_session(request_token())
    audit("auth.logout")
    resp = jsonify({"message": "Logged out"})
    resp.delete_cookie(current_app.config["SESSION_COOKIE"])
    return resp


# --------------------------------------------------------------------------
# Student profiles (APAS-F-004)
# --------------------------------------------------------------------------
def validate_profile(data, partial=False):
    errors = {}
    fields = {"id", "name", "email", "program", "current_semester"}
    if not partial:
        for f in fields:
            if data.get(f) in (None, ""):
                errors[f] = "is required"
    if "id" in data and data["id"] not in (None, "") and \
            (not isinstance(data["id"], str) or not STUDENT_ID_RE.match(data["id"])):
        errors["id"] = "must be 6-20 upper-case letters or digits"
    if "name" in data and data["name"] not in (None, "") and \
            (not isinstance(data["name"], str) or not data["name"].strip() or len(data["name"]) > 100):
        errors["name"] = "must be 1-100 characters"
    if "email" in data and data["email"] not in (None, "") and \
            (not isinstance(data["email"], str) or not EMAIL_RE.match(data["email"])):
        errors["email"] = "must be a valid email address"
    if "program" in data and data["program"] not in (None, "") and \
            (not isinstance(data["program"], str) or len(data["program"]) > 100):
        errors["program"] = "must be at most 100 characters"
    if "current_semester" in data and data["current_semester"] not in (None, ""):
        sem = data["current_semester"]
        if not isinstance(sem, int) or isinstance(sem, bool) or not 1 <= sem <= 8:
            errors["current_semester"] = "must be an integer between 1 and 8"
    unknown = set(data) - fields
    if unknown:
        errors["unknown_fields"] = sorted(unknown)
    return errors


@bp.get("/students")
@login_required("admin", "faculty")
def list_students():
    rows = get_db().execute("SELECT * FROM students ORDER BY id").fetchall()
    return jsonify({"students": [dict(r) for r in rows]})


@bp.post("/students")
@login_required("admin")
def create_student():
    data = body()
    if data is None:
        return api_error(400, "Request body must be a JSON object")
    errors = validate_profile(data)
    if errors:
        return jsonify({"error": "Validation failed", "fields": errors, "status": 400}), 400
    db = get_db()
    if student_or_404(data["id"]):
        return api_error(409, f"Student {data['id']} already exists")
    if db.execute("SELECT 1 FROM students WHERE email = ?", (data["email"],)).fetchone():
        return api_error(409, "Email address is already in use")
    now = iso(utcnow())
    db.execute("INSERT INTO students(id, name, email, program, current_semester, created_at, updated_at) "
               "VALUES (?, ?, ?, ?, ?, ?, ?)",
               (data["id"], data["name"].strip(), data["email"], data["program"],
                data["current_semester"], now, now))
    db.commit()
    audit("student.create", entity=data["id"], details={"new": data})
    return jsonify(student_or_404(data["id"])), 201


@bp.get("/students/<student_id>")
@login_required()
def get_student(student_id):
    if not can_view_student(g.user, student_id):
        audit("access.denied", "failure", entity=student_id, details={"path": request.path})
        return api_error(403, "You do not have permission to view this student")
    student = student_or_404(student_id)
    if not student:
        return api_error(404, "Student not found")
    return jsonify(student)


@bp.put("/students/<student_id>")
@login_required("admin")
def update_student(student_id):
    student = student_or_404(student_id)
    if not student:
        return api_error(404, "Student not found")
    data = body()
    if not data:
        return api_error(400, "Request body must be a non-empty JSON object")
    if "id" in data and data["id"] != student_id:
        return api_error(400, "Student ID cannot be changed")
    data.pop("id", None)
    errors = validate_profile(data, partial=True)
    if errors:
        return jsonify({"error": "Validation failed", "fields": errors, "status": 400}), 400
    db = get_db()
    if "email" in data and db.execute("SELECT 1 FROM students WHERE email = ? AND id != ?",
                                      (data["email"], student_id)).fetchone():
        return api_error(409, "Email address is already in use")
    changes = {k: {"old": student[k], "new": v} for k, v in data.items() if student[k] != v}
    for k in data:
        db.execute(f"UPDATE students SET {k} = ? WHERE id = ?", (data[k], student_id))
    db.execute("UPDATE students SET updated_at = ? WHERE id = ?", (iso(utcnow()), student_id))
    db.commit()
    audit("student.update", entity=student_id, details={"changes": changes})
    return jsonify(student_or_404(student_id))


# --------------------------------------------------------------------------
# Grades (APAS-F-005)
# --------------------------------------------------------------------------
def grade_rows(student_id):
    rows = get_db().execute(
        "SELECT g.id, g.subject_code, s.name AS subject_name, s.semester, g.assessment, g.score, "
        "g.max_score, g.updated_at FROM grades g JOIN subjects s ON s.code = g.subject_code "
        "WHERE g.student_id = ? ORDER BY s.semester, g.subject_code, g.assessment", (student_id,)).fetchall()
    return [dict(r) for r in rows]


@bp.get("/students/<student_id>/grades")
@login_required()
def get_grades(student_id):
    if not can_view_student(g.user, student_id):
        audit("access.denied", "failure", entity=student_id, details={"path": request.path})
        return api_error(403, "You do not have permission to view this student")
    if not student_or_404(student_id):
        return api_error(404, "Student not found")
    return jsonify({"student_id": student_id, "grades": grade_rows(student_id)})


def _validate_score(score, max_score):
    if not is_number(score):
        return "score must be a number"
    if score < 0 or score > max_score:
        return f"score must be between 0 and {max_score:g}"
    return None


@bp.post("/students/<student_id>/grades")
@login_required("faculty")
def enter_grade(student_id):
    data = body()
    if data is None:
        return api_error(400, "Request body must be a JSON object")
    if not student_or_404(student_id):
        return api_error(404, "Student not found")
    code, assessment, score = data.get("subject_code"), data.get("assessment"), data.get("score")
    db = get_db()
    if not isinstance(code, str) or not db.execute("SELECT 1 FROM subjects WHERE code = ?", (code,)).fetchone():
        return api_error(400, "subject_code must be an existing subject")
    if assessment not in analytics.ASSESSMENTS:
        return api_error(400, f"assessment must be one of {sorted(analytics.ASSESSMENTS)}")
    max_score = analytics.ASSESSMENTS[assessment]
    problem = _validate_score(score, max_score)
    if problem:
        return api_error(400, problem)
    if not faculty_teaches(g.user, code):
        audit("access.denied", "failure", entity=student_id,
              details={"action": "grade.enter", "subject_code": code})
        return api_error(403, "You are not assigned to this subject")
    existing = db.execute("SELECT * FROM grades WHERE student_id = ? AND subject_code = ? AND assessment = ?",
                          (student_id, code, assessment)).fetchone()
    now = iso(utcnow())
    if existing:
        db.execute("UPDATE grades SET score = ?, recorded_by = ?, updated_at = ? WHERE id = ?",
                   (score, g.user["id"], now, existing["id"]))
        db.commit()
        audit("grade.update", entity=student_id,
              details={"subject_code": code, "assessment": assessment, "old": existing["score"], "new": score})
        status = 200
    else:
        db.execute("INSERT INTO grades(student_id, subject_code, assessment, score, max_score, recorded_by, "
                   "updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (student_id, code, assessment, score, max_score, g.user["id"], now))
        db.commit()
        audit("grade.create", entity=student_id,
              details={"subject_code": code, "assessment": assessment, "new": score})
        status = 201
    row = db.execute("SELECT * FROM grades WHERE student_id = ? AND subject_code = ? AND assessment = ?",
                     (student_id, code, assessment)).fetchone()
    return jsonify(dict(row)), status


@bp.put("/students/<student_id>/grades/<int:grade_id>")
@login_required("faculty")
def update_grade(student_id, grade_id):
    db = get_db()
    existing = db.execute("SELECT * FROM grades WHERE id = ? AND student_id = ?", (grade_id, student_id)).fetchone()
    if not existing:
        return api_error(404, "Grade not found")
    data = body()
    if data is None:
        return api_error(400, "Request body must be a JSON object")
    problem = _validate_score(data.get("score"), existing["max_score"])
    if problem:
        return api_error(400, problem)
    if not faculty_teaches(g.user, existing["subject_code"]):
        audit("access.denied", "failure", entity=student_id,
              details={"action": "grade.update", "subject_code": existing["subject_code"]})
        return api_error(403, "You are not assigned to this subject")
    db.execute("UPDATE grades SET score = ?, recorded_by = ?, updated_at = ? WHERE id = ?",
               (data["score"], g.user["id"], iso(utcnow()), grade_id))
    db.commit()
    audit("grade.update", entity=student_id,
          details={"subject_code": existing["subject_code"], "assessment": existing["assessment"],
                   "old": existing["score"], "new": data["score"]})
    return jsonify(dict(db.execute("SELECT * FROM grades WHERE id = ?", (grade_id,)).fetchone()))


# --------------------------------------------------------------------------
# Attendance (APAS-F-006)
# --------------------------------------------------------------------------
@bp.get("/students/<student_id>/attendance")
@login_required()
def get_attendance(student_id):
    if not can_view_student(g.user, student_id):
        audit("access.denied", "failure", entity=student_id, details={"path": request.path})
        return api_error(403, "You do not have permission to view this student")
    if not student_or_404(student_id):
        return api_error(404, "Student not found")
    subjects, _, att = analytics.load_student_records(get_db(), student_id)
    records = get_db().execute("SELECT subject_code, date, status FROM attendance WHERE student_id = ? "
                               "ORDER BY subject_code, date", (student_id,)).fetchall()
    summary = analytics.attendance_summary(subjects, att)
    summary.update(student_id=student_id, records=[dict(r) for r in records])
    return jsonify(summary)


@bp.post("/students/<student_id>/attendance")
@login_required("faculty")
def record_attendance(student_id):
    data = body()
    if data is None:
        return api_error(400, "Request body must be a JSON object")
    if not student_or_404(student_id):
        return api_error(404, "Student not found")
    db = get_db()
    code, day, status = data.get("subject_code"), data.get("date"), data.get("status")
    if not isinstance(code, str) or not db.execute("SELECT 1 FROM subjects WHERE code = ?", (code,)).fetchone():
        return api_error(400, "subject_code must be an existing subject")
    if status not in ("present", "absent"):
        return api_error(400, "status must be 'present' or 'absent'")
    try:
        parsed = date.fromisoformat(day) if isinstance(day, str) and len(day) == 10 else None
    except ValueError:
        parsed = None
    if parsed is None:
        return api_error(400, "date must be a valid date in YYYY-MM-DD format")
    if parsed > date.today():
        return api_error(400, "Attendance cannot be recorded for a future date")
    if not faculty_teaches(g.user, code):
        audit("access.denied", "failure", entity=student_id,
              details={"action": "attendance.record", "subject_code": code})
        return api_error(403, "You are not assigned to this subject")
    existing = db.execute("SELECT * FROM attendance WHERE student_id = ? AND subject_code = ? AND date = ?",
                          (student_id, code, day)).fetchone()
    if existing:
        db.execute("UPDATE attendance SET status = ?, recorded_by = ? WHERE id = ?",
                   (status, g.user["id"], existing["id"]))
        event, http, details = "attendance.update", 200, {"old": existing["status"], "new": status}
    else:
        db.execute("INSERT INTO attendance(student_id, subject_code, date, status, recorded_by) "
                   "VALUES (?, ?, ?, ?, ?)", (student_id, code, day, status, g.user["id"]))
        event, http, details = "attendance.create", 201, {"new": status}
    db.commit()
    audit(event, entity=student_id, details={"subject_code": code, "date": day, **details})
    subjects, _, att = analytics.load_student_records(db, student_id)
    return jsonify(analytics.attendance_summary(subjects, att)), http


# --------------------------------------------------------------------------
# Analytics (APAS-F-007 .. APAS-F-015)
# --------------------------------------------------------------------------
def analysis_for(student_id):
    db = get_db()
    subjects, grades, att = analytics.load_student_records(db, student_id)
    return analytics.full_student_analysis(subjects, grades, att, get_thresholds(db))


def guard_student(student_id, roles=("admin", "faculty", "student")):
    if g.user["role"] not in roles or not can_view_student(g.user, student_id):
        audit("access.denied", "failure", entity=student_id, details={"path": request.path})
        return api_error(403, "You do not have permission to view this student")
    if not student_or_404(student_id):
        return api_error(404, "Student not found")
    return None


@bp.get("/analytics/performance/<student_id>")
@login_required()
def performance(student_id):
    denied = guard_student(student_id)
    if denied:
        return denied
    a = analysis_for(student_id)
    return jsonify({"student_id": student_id, **a["performance"],
                    "attendance": a["attendance"], "flags": a["flags"]})


@bp.get("/analytics/trends/<student_id>")
@login_required()
def trends(student_id):
    denied = guard_student(student_id)
    if denied:
        return denied
    return jsonify(trend_series(analysis_for(student_id)) | {"student_id": student_id})


def trend_series(a):
    perf = a["performance"]
    latest = max((s["semester"] for s in perf["subjects"]), default=None)
    return {
        "semester_sgpa": [{"semester": s["semester"], "sgpa": s["sgpa"]} for s in perf["semesters"]],
        "semester_percentage": [{"semester": s["semester"], "percentage": s["percentage"]}
                                for s in perf["semesters"]],
        "subject_scores": [{"subject_code": s["subject_code"], "subject_name": s["subject_name"],
                            "percentage": s["percentage"]}
                           for s in perf["subjects"] if s["semester"] == latest],
        "attendance": [{"subject_code": s["subject_code"], "percentage": s["percentage"]}
                       for s in a["attendance"]["subjects"]],
    }


@bp.get("/analytics/flagged")
@login_required("admin", "faculty")
def flagged():
    rows = student_overview()
    return jsonify({"thresholds": get_thresholds(get_db()),
                    "students": [r for r in rows if r["flagged"]]})


@bp.get("/analytics/predictions/<student_id>")
@login_required("admin", "faculty")
def prediction(student_id):
    denied = guard_student(student_id)
    if denied:
        return denied
    return jsonify({"student_id": student_id, **analysis_for(student_id)["prediction"]})


@bp.get("/analytics/at-risk")
@login_required("admin", "faculty")
def at_risk():
    rows = [r for r in student_overview() if r["at_risk"]]
    order = {"high": 0, "medium": 1}
    rows.sort(key=lambda r: (order[r["risk_level"]], r["id"]))
    return jsonify({"students": rows})


@bp.get("/analytics/insights/<student_id>")
@login_required()
def student_insights(student_id):
    denied = guard_student(student_id)
    if denied:
        return denied
    db = get_db()
    a = analysis_for(student_id)
    recs = analytics.insights(a["performance"], a["attendance"], a["prediction"], get_thresholds(db))
    return jsonify({"student_id": student_id, "recommendations": recs})


_overview_cache = {}
_overview_lock = threading.Lock()


def student_overview():
    """Summary row per student (APAS-NF-001).

    Results are cached per database and reused until the data version changes,
    so concurrent dashboard requests do not each re-analyse every student (DEF-002).
    """
    db = get_db()
    key = current_app.config["DATABASE"]
    with _overview_lock:
        version = data_version(db)
        cached = _overview_cache.get(key)
        if cached and cached[0] == version:
            return [dict(r) for r in cached[1]]
        rows = _compute_overview(db)
        _overview_cache[key] = (version, rows)
        return [dict(r) for r in rows]


def _compute_overview(db):
    thresholds = get_thresholds(db)
    subjects, grades, attendance = analytics.load_all_records(db)
    out = []
    for s in db.execute("SELECT id, name, current_semester FROM students ORDER BY id"):
        a = analytics.full_student_analysis(subjects, grades.get(s["id"], []),
                                            attendance.get(s["id"], []), thresholds)
        out.append({
            "id": s["id"], "name": s["name"], "current_semester": s["current_semester"],
            "cgpa": a["performance"]["cgpa"],
            "overall_percentage": a["performance"]["overall_percentage"],
            "attendance_percentage": a["attendance"]["overall_percentage"],
            "flagged": a["flags"]["flagged"], "flag_reasons": a["flags"]["reasons"],
            "predicted_sgpa": a["prediction"]["predicted_sgpa"],
            "risk_level": a["prediction"]["risk_level"], "at_risk": a["prediction"]["at_risk"],
            "risk_factors": a["prediction"]["risk_factors"],
        })
    return out


# --------------------------------------------------------------------------
# Thresholds configuration (APAS-F-009 "configured thresholds")
# --------------------------------------------------------------------------
@bp.get("/config/thresholds")
@login_required("admin", "faculty")
def get_config():
    return jsonify(get_thresholds(get_db()))


@bp.put("/config/thresholds")
@login_required("admin")
def put_config():
    data = body()
    if not data:
        return api_error(400, "Request body must be a non-empty JSON object")
    current = get_thresholds(get_db())
    limits = {"min_attendance_pct": 100, "min_performance_pct": 100, "risk_high_attendance_pct": 100,
              "risk_high_sgpa": 10, "risk_medium_sgpa": 10}
    for k, v in data.items():
        if k not in limits:
            return api_error(400, f"Unknown threshold '{k}'")
        if not is_number(v) or not 0 <= v <= limits[k]:
            return api_error(400, f"{k} must be a number between 0 and {limits[k]}")
    db = get_db()
    for k, v in data.items():
        db.execute("UPDATE config SET value = ? WHERE key = ?", (float(v), k))
    db.commit()
    audit("config.update", details={k: {"old": current[k], "new": v} for k, v in data.items()})
    return jsonify(get_thresholds(db))


# --------------------------------------------------------------------------
# Dashboard (APAS-F-010)
# --------------------------------------------------------------------------
def student_dashboard(student_id):
    student = student_or_404(student_id)
    a = analysis_for(student_id)
    return {"student": student, "performance": a["performance"], "attendance": a["attendance"],
            "flags": a["flags"], "trends": trend_series(a)}


@bp.get("/dashboard")
@login_required()
def dashboard():
    user = g.user
    if user["role"] == "student":
        return jsonify({"role": "student", **student_dashboard(user["student_id"])})
    selected = request.args.get("student_id")
    if selected:
        if not student_or_404(selected):
            return api_error(404, "Student not found")
        return jsonify({"role": user["role"], "selected_student": student_dashboard(selected)})
    rows = student_overview()
    payload = {"role": user["role"], "students": rows,
               "flagged_count": sum(r["flagged"] for r in rows),
               "at_risk_count": sum(r["at_risk"] for r in rows)}
    db = get_db()
    if user["role"] == "faculty":
        payload["subjects"] = [dict(r) for r in db.execute(
            "SELECT s.* FROM subjects s JOIN faculty_subjects f ON f.subject_code = s.code "
            "WHERE f.user_id = ? ORDER BY s.code", (user["id"],))]
    else:
        payload["totals"] = {
            "students": len(rows),
            "faculty": db.execute("SELECT COUNT(*) FROM users WHERE role = 'faculty'").fetchone()[0],
            "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        }
    return jsonify(payload)


# --------------------------------------------------------------------------
# Reports (APAS-F-012)
# --------------------------------------------------------------------------
def build_report_rows(student, a):
    perf, att = a["performance"], a["attendance"]
    rows = [["APAS Academic Performance Report"],
            ["Generated (UTC)", iso(utcnow())],
            ["Student ID", student["id"]], ["Name", student["name"]],
            ["Program", student["program"]], ["Current semester", student["current_semester"]],
            [],
            ["Semester", "Subject code", "Subject", "Credits", "ISA", "ESA", "Percentage", "Grade",
             "Grade point", "Status"]]
    for s in perf["subjects"]:
        rows.append([s["semester"], s["subject_code"], s["subject_name"], s["credits"],
                     s["scores"].get("ISA", ""), s["scores"].get("ESA", ""), s["percentage"],
                     s["grade"] or "", "" if s["grade_point"] is None else s["grade_point"], s["status"]])
    rows += [[], ["Semester", "SGPA", "Percentage"]]
    rows += [[s["semester"], s["sgpa"], s["percentage"]] for s in perf["semesters"]]
    rows += [[], ["CGPA", perf["cgpa"]], ["Overall percentage", perf["overall_percentage"]], [],
             ["Attendance subject", "Present", "Total", "Percentage"]]
    rows += [[s["subject_code"], s["present"], s["total"], s["percentage"]] for s in att["subjects"]]
    rows += [["Overall attendance", att["present"], att["total"], att["overall_percentage"]], [],
             ["Flags", "; ".join(a["flags"]["reasons"]) or "None"]]
    return rows


@bp.post("/reports")
@login_required()
def generate_report():
    data = body() or {}
    student_id = data.get("student_id") or (g.user["student_id"] if g.user["role"] == "student" else None)
    fmt = data.get("format", "csv")
    if not student_id:
        return api_error(400, "student_id is required")
    if fmt not in ("csv", "json"):
        return api_error(400, "format must be 'csv' or 'json'")
    denied = guard_student(student_id)
    if denied:
        return denied
    student = student_or_404(student_id)
    a = analysis_for(student_id)
    audit("report.generate", entity=student_id, details={"format": fmt})
    stamp = date.today().isoformat()
    if fmt == "json":
        resp = jsonify({"student": student, **a, "generated_at": iso(utcnow())})
    else:
        buf = io.StringIO()
        csv.writer(buf).writerows(build_report_rows(student, a))
        resp = Response(buf.getvalue(), mimetype="text/csv")
    resp.headers["Content-Disposition"] = f'attachment; filename="APAS_Report_{student_id}_{stamp}.{fmt}"'
    return resp


# --------------------------------------------------------------------------
# Audit log (APAS-NF-004, APAS-SR-005)
# --------------------------------------------------------------------------
@bp.get("/audit")
@login_required("admin")
def audit_log():
    query, params = "SELECT * FROM audit_log WHERE 1=1", []
    for field in ("event_type", "entity", "username", "outcome"):
        if request.args.get(field):
            query += f" AND {field} = ?"
            params.append(request.args[field])
    limit = min(int(request.args.get("limit", 500)), 5000) if request.args.get("limit", "500").isdigit() else 500
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    return jsonify({"entries": [dict(r) for r in get_db().execute(query, params)]})
