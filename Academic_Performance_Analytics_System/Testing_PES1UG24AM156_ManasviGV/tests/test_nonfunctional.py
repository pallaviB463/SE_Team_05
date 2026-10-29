"""Non-functional tests: TC-PERF-01, TC-REL-01, TC-AUD-01, TC-UX-01 (APAS-NF-001, -002, -004, -005)."""
import json
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from html.parser import HTMLParser
from pathlib import Path

import pytest
import requests

from apas import create_app
from apas.db import connect
from apas.seed import add_synthetic_students
from apas.security import iso, purge_audit_log, utcnow
from conftest import PASSWORDS, RESULTS_DIR, ROOT, https_client
from live import https_server

tc = pytest.mark.tc


# --------------------------------------------------------------------------
# TC-PERF-01 dashboard response time (APAS-NF-001)
# --------------------------------------------------------------------------
def percentile(values, pct):
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct / 100
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


@tc("TC-PERF-01.1", "APAS-NF-001", type="Performance",
    limitation="'Normal operating conditions' are not quantified in the SRS; load profile taken from team test data "
               "TD-12 (50 concurrent users), cohort of 306 students, single developer laptop. Repeat on the "
               "deployment infrastructure.")
@pytest.mark.live
def test_dashboard_response_time(db_path, tmp_path, record):
    """Dashboards load within 3 seconds for at least 95% of requests
    Objective: Measure dashboard response time under normal load.
    Preconditions: Seeded data plus 300 synthetic students (306 total, ~42 000 grade/attendance rows); APAS on a real HTTPS socket.
    Test data: 300 requests, 50 concurrent clients (TD-12), mix of admin/faculty overview dashboards, student dashboards and HTML dashboards.
    Steps:
    1. Add 300 synthetic students to the database.
    2. Start the HTTPS server and log in as admin, fac.rao and aarav.
    3. Send 300 dashboard requests from 50 worker threads; time each request end-to-end.
    4. Compute the 95th-percentile response time overall and per dashboard type.
    Expected: All requests HTTP 200; 95th percentile <= 3.0 s overall and for every dashboard type.
    """
    conn = connect(db_path)
    add_synthetic_students(conn, 300)
    conn.close()
    app = create_app({"DATABASE": str(db_path)})
    with https_server(app, tmp_path) as (base, cert, _port):
        tokens = {u: requests.post(f"{base}/api/auth/login", json={"username": u, "password": PASSWORDS[u]},
                                   verify=str(cert)).json()["token"] for u in ("admin", "fac.rao", "aarav")}
        scenarios = [
            ("admin API overview", "admin", "/api/dashboard"),
            ("faculty API overview", "fac.rao", "/api/dashboard"),
            ("student API dashboard", "aarav", "/api/dashboard"),
            ("faculty selected student", "fac.rao", "/api/dashboard?student_id=SYN00150"),
            ("admin HTML overview", "admin", "/dashboard"),
            ("faculty HTML student", "fac.rao", "/dashboard?student_id=PES1UG24AM003"),
        ]
        plan = [scenarios[i % len(scenarios)] for i in range(300)]

        def hit(item):
            name, user, path = item
            start = time.perf_counter()
            r = requests.get(base + path, headers={"Authorization": f"Bearer {tokens[user]}"}, verify=str(cert))
            return name, r.status_code, time.perf_counter() - start, len(r.content)

        wall = time.perf_counter()
        with ThreadPoolExecutor(max_workers=50) as pool:
            samples = list(pool.map(hit, plan))
        wall = time.perf_counter() - wall
    times = [s[2] for s in samples]
    per = {}
    for name, *_ in scenarios:
        t = [s[2] for s in samples if s[0] == name]
        per[name] = {"n": len(t), "p50_s": round(statistics.median(t), 3),
                     "p95_s": round(percentile(t, 95), 3), "max_s": round(max(t), 3)}
    result = {
        "requests": len(samples), "concurrency": 50, "students_in_db": 306,
        "status_codes": sorted({s[1] for s in samples}),
        "overall": {"p50_s": round(statistics.median(times), 3), "p95_s": round(percentile(times, 95), 3),
                    "max_s": round(max(times), 3), "mean_s": round(statistics.mean(times), 3),
                    "within_3s_pct": round(100 * sum(t <= 3.0 for t in times) / len(times), 2)},
        "throughput_rps": round(len(samples) / wall, 1),
        "per_dashboard": per,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "performance_results.json").write_text(json.dumps(result, indent=2))
    record(f"{len(samples)} requests @50 concurrent: p50 {result['overall']['p50_s']} s, p95 "
           f"{result['overall']['p95_s']} s, max {result['overall']['max_s']} s, "
           f"{result['overall']['within_3s_pct']}% within 3 s; slowest p95 = "
           f"{max(v['p95_s'] for v in per.values())} s")
    assert result["status_codes"] == [200]
    assert result["overall"]["p95_s"] <= 3.0
    assert all(v["p95_s"] <= 3.0 for v in per.values())


@tc("TC-PERF-01.2", "APAS-NF-001", type="Performance",
    limitation="Same load assumptions as TC-PERF-01.1. Write rate (1 grade update per 10 requests) is an assumption "
               "representing faculty entering marks while others view dashboards.")
@pytest.mark.live
def test_dashboard_response_time_with_updates(db_path, tmp_path, record):
    """Dashboards stay within 3 seconds while faculty are updating grades
    Objective: Verify NF-001 when cached dashboard results are constantly invalidated by data changes.
    Preconditions: 306 students; APAS on a real HTTPS socket.
    Test data: 300 operations from 50 concurrent clients (TD-12); every 10th operation is a grade update by fac.rao (forces recomputation); the rest are admin/faculty overview dashboards.
    Steps:
    1. Add 300 synthetic students and start the server.
    2. Run the mixed workload and time each dashboard request.
    Expected: All requests succeed; dashboard 95th percentile <= 3.0 s.
    """
    conn = connect(db_path)
    add_synthetic_students(conn, 300)
    conn.close()
    app = create_app({"DATABASE": str(db_path)})
    with https_server(app, tmp_path) as (base, cert, _port):
        tokens = {u: requests.post(f"{base}/api/auth/login", json={"username": u, "password": PASSWORDS[u]},
                                   verify=str(cert)).json()["token"] for u in ("admin", "fac.rao")}

        def op(i):
            start = time.perf_counter()
            if i % 10 == 0:
                r = requests.post(f"{base}/api/students/SYN{i + 1:05d}/grades", verify=str(cert),
                                  headers={"Authorization": f"Bearer {tokens['fac.rao']}"},
                                  json={"subject_code": "AM301", "assessment": "ISA", "score": i % 50})
                kind = "write"
            else:
                user = "fac.rao" if i % 2 else "admin"
                r = requests.get(f"{base}/api/dashboard", verify=str(cert),
                                 headers={"Authorization": f"Bearer {tokens[user]}"})
                kind = "dashboard"
            return kind, r.status_code, time.perf_counter() - start

        with ThreadPoolExecutor(max_workers=50) as pool:
            samples = list(pool.map(op, range(300)))
    dash = [t for k, _, t in samples if k == "dashboard"]
    writes = [t for k, _, t in samples if k == "write"]
    result = {"operations": len(samples), "dashboard_requests": len(dash), "writes": len(writes),
              "status_codes": sorted({c for _, c, _ in samples}),
              "dashboard": {"p50_s": round(statistics.median(dash), 3), "p95_s": round(percentile(dash, 95), 3),
                            "max_s": round(max(dash), 3),
                            "within_3s_pct": round(100 * sum(t <= 3 for t in dash) / len(dash), 2)},
              "write_p95_s": round(percentile(writes, 95), 3)}
    path = RESULTS_DIR / "performance_results.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    data["mixed_read_write"] = result
    path.write_text(json.dumps(data, indent=2))
    record(f"{len(dash)} dashboard requests + {len(writes)} grade writes @50 concurrent: dashboard p50 "
           f"{result['dashboard']['p50_s']} s, p95 {result['dashboard']['p95_s']} s, max {result['dashboard']['max_s']} s")
    assert set(result["status_codes"]) <= {200, 201} and result["dashboard"]["p95_s"] <= 3.0


# --------------------------------------------------------------------------
# TC-REL-01 availability (APAS-NF-002)
# --------------------------------------------------------------------------
@tc("TC-REL-01.1", "APAS-NF-002", type="Reliability",
    limitation="Monthly availability (>= 99%) can only be confirmed by monitoring a deployed instance for a full "
               "calendar month (tools/availability_monitor.py). This run covers a short soak test with fault injection.")
@pytest.mark.live
def test_availability_under_faults(db_path, tmp_path, record):
    """Service stays available while receiving malformed and hostile requests
    Objective: Estimate availability during a soak test with injected faulty requests.
    Preconditions: APAS on a real HTTPS socket.
    Test data: 400 health probes interleaved with malformed JSON, oversized bodies, unknown routes and invalid methods.
    Steps:
    1. Start the server.
    2. Send 400 /api/health probes; after every probe send one faulty request.
    3. Availability = successful probes / total probes.
    Expected: Availability >= 99% in the window; faulty requests receive 4xx responses (never 5xx, never a dropped connection).
    """
    app = create_app({"DATABASE": str(db_path)})
    faults = [
        ("post", "/api/auth/login", {"data": "{not json", "headers": {"Content-Type": "application/json"}}),
        ("post", "/api/auth/login", {"data": "x" * 200_000, "headers": {"Content-Type": "application/json"}}),
        ("get", "/api/does-not-exist", {}),
        ("delete", "/api/students/PES1UG24AM001", {}),
        ("post", "/api/reports", {"json": [1, 2, 3]}),
    ]
    ok = fault_5xx = 0
    fault_codes = set()
    with https_server(app, tmp_path) as (base, cert, _port):
        s = requests.Session()
        s.verify = str(cert)
        start = time.perf_counter()
        for i in range(400):
            try:
                ok += s.get(f"{base}/api/health", timeout=5).status_code == 200
            except requests.RequestException:
                pass
            method, path, kw = faults[i % len(faults)]
            try:
                code = getattr(s, method)(base + path, timeout=5, **kw).status_code
                fault_codes.add(code)
                fault_5xx += code >= 500
            except requests.RequestException:
                fault_5xx += 1
        elapsed = time.perf_counter() - start
    availability = 100 * ok / 400
    result = {"probes": 400, "successful": ok, "availability_pct": availability, "window_s": round(elapsed, 1),
              "fault_requests": 400, "fault_status_codes": sorted(fault_codes), "fault_5xx_or_dropped": fault_5xx}
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "reliability_results.json").write_text(json.dumps(result, indent=2))
    record(f"{ok}/400 probes OK = {availability:.2f}% over {elapsed:.1f} s; fault responses {sorted(fault_codes)}, "
           f"5xx/dropped = {fault_5xx}")
    assert availability >= 99.0 and fault_5xx == 0


@tc("TC-REL-01.2", "APAS-NF-002", type="Reliability")
def test_unexpected_error_contained(db_path, record):
    """An internal failure returns a generic error and the service keeps running
    Objective: Verify graceful handling of unexpected server-side errors (SAD 4.4.1).
    Preconditions: Logged in as fac.rao.
    Test data: The subjects table is dropped to simulate a database failure.
    Steps:
    1. Drop the subjects table.
    2. GET /api/analytics/performance/PES1UG24AM001.
    3. GET /api/health.
    Expected: Step 2 HTTP 500 with "An unexpected error occurred" and no SQL/stack-trace details; step 3 HTTP 200.
    """
    app = create_app({"DATABASE": str(db_path)})
    client = https_client(app)
    token = client.post("/api/auth/login", json={"username": "fac.rao", "password": PASSWORDS["fac.rao"]}).get_json()["token"]
    conn = connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DROP TABLE subjects")
    conn.commit()
    conn.close()
    resp = client.get("/api/analytics/performance/PES1UG24AM001", headers={"Authorization": f"Bearer {token}"})
    health = client.get("/api/health")
    assert resp.status_code == 500 and resp.get_json() == {"error": "An unexpected error occurred", "status": 500}
    assert b"sqlite" not in resp.data.lower() and b"Traceback" not in resp.data and health.status_code == 200
    record(f"failure -> HTTP 500 {resp.get_json()}; health afterwards HTTP {health.status_code}")


# --------------------------------------------------------------------------
# TC-AUD-01 audit logging and retention (APAS-NF-004)
# --------------------------------------------------------------------------
@tc("TC-AUD-01.1", "APAS-NF-004", type="Audit")
def test_record_modifications_logged(client, login, db, record):
    """Every academic record modification is logged with user ID, timestamp and details
    Objective: Verify audit coverage of profile, grade, attendance and configuration changes.
    Steps:
    1. admin creates and updates a student profile, and changes a threshold.
    2. fac.rao creates a grade, updates it, records and corrects attendance.
    3. GET /api/audit as admin.
    Expected: Entries student.create, student.update, config.update, grade.create, grade.update, attendance.create, attendance.update — each with user_id, username, ISO timestamp and old/new values.
    """
    a, f = login("admin"), login("fac.rao")
    client.post("/api/students", headers=a, json={"id": "PES1UG24AM010", "name": "Audit Test", "email": "audit@apas.test",
                                                   "program": "B.Tech", "current_semester": 1})
    client.put("/api/students/PES1UG24AM010", headers=a, json={"current_semester": 2})
    client.put("/api/config/thresholds", headers=a, json={"min_attendance_pct": 80})
    client.post("/api/students/PES1UG24AM010/grades", headers=f, json={"subject_code": "AM101", "assessment": "ISA", "score": 30})
    client.post("/api/students/PES1UG24AM010/grades", headers=f, json={"subject_code": "AM101", "assessment": "ISA", "score": 35})
    client.post("/api/students/PES1UG24AM010/attendance", headers=f, json={"subject_code": "AM101", "date": "2026-10-12", "status": "absent"})
    client.post("/api/students/PES1UG24AM010/attendance", headers=f, json={"subject_code": "AM101", "date": "2026-10-12", "status": "present"})
    entries = client.get("/api/audit", headers=a).get_json()["entries"]
    wanted = ["student.create", "student.update", "config.update", "grade.create", "grade.update",
              "attendance.create", "attendance.update"]
    found = {e["event_type"]: e for e in entries if e["event_type"] in wanted}
    assert set(found) == set(wanted)
    for e in found.values():
        assert e["user_id"] and e["username"] and re.match(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", e["ts"])
    g = json.loads(found["grade.update"]["details"])
    s = json.loads(found["student.update"]["details"])
    assert (g["old"], g["new"]) == (30, 35) and s["changes"]["current_semester"] == {"old": 1, "new": 2}
    record(f"logged: {sorted(found)}; grade.update {g}; student.update {s['changes']}")


@tc("TC-AUD-01.2", "APAS-NF-004", type="Audit")
def test_audit_retention_minimum_12_months(app, db, record):
    """Audit records are retained for at least 12 months
    Objective: Verify the retention policy and its 12-month minimum.
    Test data: Entries aged 30 days, 11 months 29 days, 12 months + 2 days, 13 months, 24 months.
    Steps:
    1. Insert the aged entries.
    2. Run the purge with retention 12 months; check what remains.
    3. Re-insert and run the purge with a mis-configured retention of 6 months.
    4. Run the purge with retention 18 months.
    Expected: Step 2 keeps the 30-day and 11m29d entries and removes the older three; step 3 behaves like 12 months (minimum enforced); step 4 keeps everything younger than 18 months (30d, 11m29d, 12m2d, 13m).
    """
    from apas.security import subtract_months
    now = utcnow()
    ages = {"30d": now - timedelta(days=30), "11m29d": subtract_months(now, 11) - timedelta(days=29),
            "12m2d": subtract_months(now, 12) - timedelta(days=2), "13m": subtract_months(now, 13),
            "24m": subtract_months(now, 24)}

    def reset():
        db.execute("DELETE FROM audit_log")
        for label, ts in ages.items():
            db.execute("INSERT INTO audit_log(ts, event_type, entity, outcome, details) VALUES (?, 'grade.update', ?, "
                       "'success', '{}')", (iso(ts), label))
        db.commit()

    def remaining():
        return sorted(r[0] for r in db.execute("SELECT entity FROM audit_log"))

    results = {}
    with app.app_context():
        for months in (12, 6, 18):
            reset()
            purge_audit_log(db, months, now=now)
            results[months] = remaining()
    assert results[12] == ["11m29d", "30d"]
    assert results[6] == ["11m29d", "30d"]
    assert results[18] == ["11m29d", "12m2d", "13m", "30d"]
    record(f"retained with 12 months: {results[12]}; with 6 (minimum 12 enforced): {results[6]}; "
           f"with 18: {results[18]}")


@tc("TC-AUD-01.3", "APAS-NF-004", type="Audit")
def test_audit_log_tamper_protection(client, login, db, record):
    """Audit records cannot be modified
    Objective: Verify that audit logs are protected against modification (SAD 3.9.6).
    Steps:
    1. Attempt an UPDATE on audit_log directly in the database.
    2. Attempt PUT and DELETE on /api/audit as admin.
    Expected: Database rejects the UPDATE ("audit_log is append-only"); API returns HTTP 405 for both.
    """
    client.post("/api/auth/login", json={"username": "admin", "password": PASSWORDS["admin"]})
    with pytest.raises(Exception) as exc:
        db.execute("UPDATE audit_log SET username = 'someone-else'")
    db.rollback()  # release the write lock held by the aborted statement
    h = login("admin")
    codes = [client.put("/api/audit", headers=h, json={}).status_code, client.delete("/api/audit", headers=h).status_code]
    assert "append-only" in str(exc.value) and codes == [405, 405]
    record(f"direct UPDATE -> '{exc.value}'; API PUT/DELETE -> {codes}")


@tc("TC-AUD-01.4", "APAS-NF-004", type="Audit")
def test_audit_log_retrieval(client, login, record):
    """Audit entries can be retrieved and filtered by an administrator
    Objective: Verify that logs can be retrieved for investigation.
    Steps:
    1. Generate a grade.update entry for PES1UG24AM003.
    2. GET /api/audit?event_type=grade.update&entity=PES1UG24AM003 as admin.
    Expected: Only matching entries are returned, newest first.
    """
    client.post("/api/students/PES1UG24AM003/grades", headers=login("fac.rao"),
                json={"subject_code": "AM301", "assessment": "ESA", "score": 30})
    entries = client.get("/api/audit?event_type=grade.update&entity=PES1UG24AM003",
                         headers=login("admin")).get_json()["entries"]
    assert len(entries) == 1 and entries[0]["username"] == "fac.rao"
    record(f"{len(entries)} entry returned: {entries[0]['event_type']} by {entries[0]['username']} at {entries[0]['ts']}")


# --------------------------------------------------------------------------
# TC-UX-01 accessibility (APAS-NF-005)
# --------------------------------------------------------------------------
class A11yParser(HTMLParser):
    FOCUSABLE = {"a", "button", "input", "select", "textarea"}

    def __init__(self):
        super().__init__()
        self.elements, self.labels, self.ids, self.html_lang = [], set(), set(), None
        self.focus_order, self.tables, self._table = [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.elements.append((tag, a))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "label" and "for" in a:
            self.labels.add(a["for"])
        if tag in self.FOCUSABLE and a.get("type") != "hidden":
            self.focus_order.append((tag, a.get("href") or a.get("id") or a.get("type")))
        if tag == "table":
            self._table = {"caption": False, "th": 0, "th_scoped": 0}
            self.tables.append(self._table)
        if tag == "caption" and self._table is not None:
            self._table["caption"] = True
        if tag == "th" and self._table is not None:
            self._table["th"] += 1
            self._table["th_scoped"] += "scope" in a


def audit_page(html):
    p = A11yParser()
    p.feed(html.decode())
    problems = []
    if p.html_lang != "en":
        problems.append("html lang missing")
    for tag, a in p.elements:
        if tag == "input" and a.get("type") != "hidden" and a.get("id") not in p.labels:
            problems.append(f"input without label: {a}")
        if "tabindex" in a and int(a["tabindex"]) > 0:
            problems.append(f"positive tabindex: {tag}")
        if tag == "svg" and (a.get("role") != "img" or a.get("aria-labelledby") not in p.ids):
            problems.append(f"svg without accessible name: {a.get('id')}")
        if tag == "img" and not a.get("alt"):
            problems.append("img without alt")
    for t in p.tables:
        if not t["caption"] or t["th"] != t["th_scoped"]:
            problems.append(f"table missing caption or th scope: {t}")
    if not p.focus_order or p.focus_order[0] != ("a", "#main") or "main" not in p.ids:
        problems.append("first focusable element is not the skip link to #main")
    return problems, p


@tc("TC-UX-01.1", "APAS-NF-005", type="Accessibility", priority="Medium")
def test_pages_structure_and_keyboard_access(client, login, record):
    """Pages provide labels, landmarks, skip link and a logical keyboard order
    Objective: Automated checks for WCAG 2.1 AA criteria 1.1.1, 1.3.1, 2.1.1, 2.4.1, 2.4.3, 3.1.1, 3.3.2, 4.1.2.
    Preconditions: Login page, student dashboard (charts), admin overview dashboard.
    Steps:
    1. Render each page.
    2. Check: html lang, labelled inputs, no positive tabindex, SVG charts with role="img" and an accessible name, tables with caption and scoped headers, skip link as first focusable element.
    Expected: No problems reported on any page.
    """
    from conftest import PASSWORDS as P
    pages = {"login": client.get("/login").data}
    client.post("/login", data={"username": "aarav", "password": P["aarav"]})
    pages["student dashboard"] = client.get("/dashboard").data
    client.post("/logout")
    client.post("/login", data={"username": "admin", "password": P["admin"]})
    pages["admin overview"] = client.get("/dashboard").data
    pages["admin student view"] = client.get("/dashboard?student_id=PES1UG24AM003").data
    report = {}
    for name, html in pages.items():
        problems, parser = audit_page(html)
        report[name] = problems
        assert problems == [], f"{name}: {problems}"
    record(f"{len(pages)} pages checked, 0 problems: {list(pages)}")


@tc("TC-UX-01.2", "APAS-NF-005", type="Accessibility", priority="Medium")
def test_error_messages_announced(client, record):
    """Form errors are announced to assistive technology
    Objective: Verify WCAG 3.3.1 (error identification) and 4.1.3 (status messages) on the login form.
    Steps:
    1. Submit the login form with empty fields and with wrong credentials.
    Expected: Error text is shown in an element with role="alert" and linked to the username field via aria-describedby.
    """
    for data in ({"username": "", "password": ""}, {"username": "aarav", "password": "wrong"}):
        html = client.post("/login", data=data).data.decode()
        assert 'role="alert"' in html and 'aria-describedby="login-error"' in html and 'id="login-error"' in html
    record('Both error cases render role="alert" message linked by aria-describedby')


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(hex_colour):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in hex_to_rgb(hex_colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@tc("TC-UX-01.3", "APAS-NF-005", type="Accessibility", priority="Medium")
def test_colour_contrast(record):
    """Text and UI colours meet WCAG 2.1 AA contrast ratios
    Objective: Verify WCAG 1.4.3 (text >= 4.5:1) and 1.4.11 (non-text UI and graphics >= 3:1).
    Test data: Colour tokens from apas/static/style.css.
    Steps:
    1. Read the CSS custom properties.
    2. Compute the contrast ratio of every foreground/background pair used by the UI.
    Expected: All text pairs >= 4.5:1; all non-text pairs (borders, focus ring, chart marks) >= 3:1.
    """
    css = (ROOT / "apas" / "static" / "style.css").read_text()
    tokens = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", css))
    text_pairs = [("text", "bg"), ("text", "surface"), ("text-muted", "bg"), ("text-muted", "surface"),
                  ("link", "bg"), ("link", "surface"), ("on-primary", "primary"), ("danger", "bg"),
                  ("warning-text", "warning-bg")]
    ui_pairs = [("border", "bg"), ("border", "surface"), ("focus", "bg"), ("focus", "surface"),
                ("chart-bar", "surface"), ("chart-line", "surface")]
    ratios = {f"{a}/{b}": round(contrast(tokens[a], tokens[b]), 2) for a, b in text_pairs + ui_pairs}
    failing = [k for k, v in ratios.items() if v < (4.5 if tuple(k.split("/")) in text_pairs else 3.0)]
    assert failing == [], f"below AA: {failing} {ratios}"
    record("; ".join(f"{k} {v}:1" for k, v in ratios.items()))


@tc("TC-UX-01.4", "APAS-NF-005", type="Accessibility", priority="Medium")
def test_focus_visible_and_reflow(record):
    """Keyboard focus is visible and layout reflows at narrow widths
    Objective: Verify WCAG 2.4.7 (focus visible) and 1.4.10 (reflow) support in the stylesheet.
    Steps:
    1. Inspect apas/static/style.css and base.html.
    Expected: A :focus-visible outline of at least 2px is defined; the skip link becomes visible on focus; viewport meta is present; tables are wrapped for horizontal scrolling instead of page overflow.
    """
    css = (ROOT / "apas" / "static" / "style.css").read_text()
    base = (ROOT / "apas" / "templates" / "base.html").read_text()
    outline = re.search(r":focus-visible\s*{[^}]*outline:\s*(\d+)px", css)
    assert outline and int(outline.group(1)) >= 2
    assert re.search(r"\.skip-link:focus\s*{[^}]*left:\s*8px", css)
    assert 'name="viewport"' in base and ".table-wrap" in css
    record(f":focus-visible outline {outline.group(1)}px; skip link shown on focus; viewport meta present; tables in scroll wrapper")
