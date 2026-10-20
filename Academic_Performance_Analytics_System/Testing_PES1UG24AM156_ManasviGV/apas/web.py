"""Web portals (SAD 3.4 items 1-3): login page and role-based dashboards."""
from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, url_for

from .api import student_dashboard, student_overview
from .db import get_thresholds, get_db
from .security import authenticate, audit, create_session, current_user, end_session, login_required, request_token

bp = Blueprint("web", __name__)

CHART_W, CHART_H, PAD = 560, 240, 40


def bar_chart(items, label_key, value_key, max_value=100.0):
    """Bar chart geometry: bar height is proportional to the value (APAS-F-011)."""
    if not items:
        return None
    inner_w, inner_h = CHART_W - 2 * PAD, CHART_H - 2 * PAD
    slot = inner_w / len(items)
    bars = []
    for i, item in enumerate(items):
        value = item[value_key] or 0
        h = inner_h * value / max_value
        bars.append({"label": item[label_key], "value": value,
                     "x": round(PAD + i * slot + slot * 0.2, 2), "w": round(slot * 0.6, 2),
                     "y": round(PAD + inner_h - h, 2), "h": round(h, 2)})
    return {"w": CHART_W, "h": CHART_H, "pad": PAD, "base": PAD + inner_h, "bars": bars, "max": max_value}


def line_chart(points, label_key, value_key, max_value=10.0):
    if not points:
        return None
    inner_w, inner_h = CHART_W - 2 * PAD, CHART_H - 2 * PAD
    step = inner_w / max(len(points) - 1, 1)
    pts = []
    for i, p in enumerate(points):
        value = p[value_key] or 0
        pts.append({"label": p[label_key], "value": value, "x": round(PAD + i * step, 2),
                    "y": round(PAD + inner_h - inner_h * value / max_value, 2)})
    return {"w": CHART_W, "h": CHART_H, "pad": PAD, "base": PAD + inner_h, "points": pts,
            "path": " ".join(f"{p['x']},{p['y']}" for p in pts), "max": max_value}


@bp.after_request
def no_store(resp):
    # Pages with academic data must not be served from browser cache after logout.
    resp.headers["Cache-Control"] = "no-store"
    return resp


@bp.get("/")
def index():
    return redirect(url_for("web.dashboard_page"))


@bp.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            error = "Enter both your username and password."
        else:
            user, error = authenticate(username, password)
            if user:
                resp = redirect(url_for("web.dashboard_page"))
                resp.set_cookie(current_app.config["SESSION_COOKIE"], create_session(user), httponly=True,
                                samesite="Lax", secure=current_app.config["ENFORCE_HTTPS"])
                return resp
    status = 401 if error and request.method == "POST" else 200
    return render_template("login.html", error=error), status


@bp.post("/logout")
def logout_page():
    if current_user():
        token = request_token()
        g.user = current_user()
        end_session(token)
        audit("auth.logout")
    resp = redirect(url_for("web.login_page"))
    resp.delete_cookie(current_app.config["SESSION_COOKIE"])
    return resp


@bp.get("/dashboard")
@login_required(html=True)
def dashboard_page():
    user = g.user
    selected = request.args.get("student_id")
    if user["role"] == "student":
        selected = user["student_id"]
    ctx = {"user": user, "thresholds": get_thresholds(get_db())}
    if selected:
        if not get_db().execute("SELECT 1 FROM students WHERE id = ?", (selected,)).fetchone():
            return make_response(render_template("error.html", user=user, message="Student not found."), 404)
        d = student_dashboard(selected)
        ctx.update(d=d,
                   subject_chart=bar_chart(d["trends"]["subject_scores"], "subject_code", "percentage"),
                   attendance_chart=bar_chart(d["trends"]["attendance"], "subject_code", "percentage"),
                   sgpa_chart=line_chart(d["trends"]["semester_sgpa"], "semester", "sgpa"))
        return render_template("student_dashboard.html", **ctx)
    ctx["students"] = student_overview()
    return render_template("overview_dashboard.html", **ctx)
