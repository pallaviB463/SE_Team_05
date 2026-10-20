"""TC-VIS / TC-REP: Dashboards, graphical trends and reports (APAS-F-010 .. APAS-F-012)."""
import csv
import io
import re
from datetime import date
from html.parser import HTMLParser

import pytest

tc = pytest.mark.tc


class SvgCollector(HTMLParser):
    """Collect chart elements and KPI values from rendered dashboard HTML."""

    def __init__(self):
        super().__init__()
        self.charts, self.current, self.kpis, self._kpi = {}, None, {}, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg" and "chart" in a.get("class", ""):
            self.current = a["id"]
            self.charts[self.current] = []
        elif tag in ("rect", "circle") and self.current and "data-value" in a:
            self.charts[self.current].append(a)
        elif a.get("id", "").startswith("kpi-"):
            self._kpi = a["id"]

    def handle_endtag(self, tag):
        if tag == "svg":
            self.current = None

    def handle_data(self, data):
        if self._kpi and data.strip():
            self.kpis[self._kpi] = data.strip()
            self._kpi = None


def parse(html):
    p = SvgCollector()
    p.feed(html.decode() if isinstance(html, bytes) else html)
    return p


# --------------------------------------------------------------------------
# APAS-F-010 dashboard
# --------------------------------------------------------------------------
@tc("TC-VIS-01.1", "APAS-F-010")
def test_student_dashboard_shows_own_data(client, login, record):
    """Student dashboard shows the student's own grades, attendance and performance
    Objective: Verify dashboard accuracy for the logged-in student.
    Preconditions: aarav logged in.
    Test data: Expected CGPA 9.39, overall 86.91%, attendance 95.00%.
    Steps:
    1. GET /api/dashboard as aarav.
    2. GET /api/dashboard?student_id=PES1UG24AM003 as aarav (attempt to view another student).
    Expected: Dashboard shows PES1UG24AM001 with the expected values; the student_id parameter is ignored for students (still own data).
    """
    h = login("aarav")
    own = client.get("/api/dashboard", headers=h).get_json()
    other = client.get("/api/dashboard?student_id=PES1UG24AM003", headers=h).get_json()
    assert own["student"]["id"] == "PES1UG24AM001"
    assert own["performance"]["cgpa"] == 9.39 and own["performance"]["overall_percentage"] == 86.91
    assert own["attendance"]["overall_percentage"] == 95.0
    assert other["student"]["id"] == "PES1UG24AM001"
    record(f"student={own['student']['id']} CGPA={own['performance']['cgpa']} overall="
           f"{own['performance']['overall_percentage']}% attendance={own['attendance']['overall_percentage']}%; "
           f"?student_id=AM003 still returned {other['student']['id']}")


@tc("TC-VIS-01.2", "APAS-F-010")
def test_faculty_selected_student_dashboard(client, login, record):
    """Faculty dashboard for a selected student matches stored records
    Objective: Verify dashboard data for the selected student.
    Preconditions: fac.rao logged in.
    Test data: Diya (AM002): CGPA 7.82, overall 70.64%, attendance 60.00%, flagged.
    Steps:
    1. GET /api/dashboard?student_id=PES1UG24AM002.
    2. GET /dashboard?student_id=PES1UG24AM002 (HTML).
    Expected: API and HTML KPIs show CGPA 7.82, overall 70.64, attendance 60.0 and the "Needs attention" flags.
    """
    h = login("fac.rao")
    d = client.get("/api/dashboard?student_id=PES1UG24AM002", headers=h).get_json()["selected_student"]
    html = client.get("/dashboard?student_id=PES1UG24AM002", headers=h)
    kpis = parse(html.data).kpis
    assert d["performance"]["cgpa"] == 7.82 and d["attendance"]["overall_percentage"] == 60.0
    assert kpis == {"kpi-cgpa": "7.82", "kpi-overall": "70.64", "kpi-attendance": "60.0"}
    assert b"Needs attention" in html.data
    record(f"API CGPA={d['performance']['cgpa']}, attendance={d['attendance']['overall_percentage']}; HTML KPIs={kpis}")


@tc("TC-VIS-01.3", "APAS-F-010")
def test_overview_dashboard_counts(client, login, record):
    """Overview dashboard lists all students with correct flag and risk counts
    Objective: Verify the faculty/admin overview dashboard.
    Preconditions: 6 seeded students; 2 flagged (Diya, Kabir); 2 at risk (Diya, Kabir).
    Steps:
    1. GET /api/dashboard and /dashboard as admin.
    Expected: 6 students, flagged_count=2, at_risk_count=2; HTML KPI cards show 6 / 2 / 2.
    """
    h = login("admin")
    d = client.get("/api/dashboard", headers=h).get_json()
    kpis = parse(client.get("/dashboard", headers=h).data).kpis
    assert len(d["students"]) == 6 and d["flagged_count"] == 2 and d["at_risk_count"] == 2
    assert kpis == {"kpi-students": "6", "kpi-flagged": "2", "kpi-at-risk": "2"}
    record(f"API students={len(d['students'])}, flagged={d['flagged_count']}, at_risk={d['at_risk_count']}; HTML {kpis}")


@tc("TC-VIS-01.5", ["APAS-F-010", "APAS-NF-001"], type="Regression")
def test_overview_reflects_changes_immediately(client, login, record):
    """Overview dashboard reflects a grade change on the next request (regression for DEF-002 cache)
    Objective: Verify that cached dashboard results are invalidated when academic data changes.
    Preconditions: Rohan (AM005) not flagged; overview dashboard already loaded once.
    Test data: Rohan AM302 ESA 25 -> 10 (AM302 becomes 35%, grade F).
    Steps:
    1. GET /api/dashboard as fac.rao (warms the cache).
    2. POST the new grade.
    3. GET /api/dashboard again.
    Expected: Step 1 flagged_count 2; step 3 flagged_count 3 with Rohan flagged for "Failed AM302 (35.0%)".
    """
    h = login("fac.rao")
    before = client.get("/api/dashboard", headers=h).get_json()
    client.post("/api/students/PES1UG24AM005/grades", headers=h,
                json={"subject_code": "AM302", "assessment": "ESA", "score": 10})
    after = client.get("/api/dashboard", headers=h).get_json()
    rohan = next(s for s in after["students"] if s["id"] == "PES1UG24AM005")
    assert before["flagged_count"] == 2 and after["flagged_count"] == 3
    assert "Failed AM302 (35.0%)" in rohan["flag_reasons"]
    record(f"flagged_count {before['flagged_count']} -> {after['flagged_count']}; Rohan reasons {rohan['flag_reasons']}")


@tc("TC-VIS-01.4", "APAS-F-010")
def test_dashboard_unknown_student(client, login, record):
    """Dashboard for a non-existent student returns a clear not-found response
    Objective: Verify error handling on the dashboard.
    Steps:
    1. GET /api/dashboard?student_id=PES1UG24AM999 and the HTML equivalent as fac.rao.
    Expected: HTTP 404 with "Student not found" (no server error).
    """
    h = login("fac.rao")
    api = client.get("/api/dashboard?student_id=PES1UG24AM999", headers=h)
    page = client.get("/dashboard?student_id=PES1UG24AM999", headers=h)
    assert api.status_code == 404 and page.status_code == 404 and b"Student not found" in page.data
    record(f"API {api.status_code}, HTML {page.status_code} 'Student not found'")


# --------------------------------------------------------------------------
# APAS-F-011 graphical visualisation
# --------------------------------------------------------------------------
@tc("TC-VIS-02.1", "APAS-F-011")
def test_bar_chart_matches_data(client, login, record):
    """Bar charts represent the stored subject percentages accurately
    Objective: Verify that bar chart values and bar heights match the data.
    Preconditions: fac.rao logged in; Kabir semester-3 scores 42%, 35%, 45%; attendance 80% each.
    Steps:
    1. GET /api/analytics/trends/PES1UG24AM003.
    2. Render /dashboard?student_id=PES1UG24AM003 and read the SVG bars.
    Expected: One bar per subject; data-value equals the API percentage; bar height = value x 1.6 px (160 px plot area for 100%).
    """
    h = login("fac.rao")
    api = client.get("/api/analytics/trends/PES1UG24AM003", headers=h).get_json()
    charts = parse(client.get("/dashboard?student_id=PES1UG24AM003", headers=h).data).charts
    bars = charts["chart-subjects"]
    assert [(b["data-label"], float(b["data-value"])) for b in bars] == \
           [(s["subject_code"], s["percentage"]) for s in api["subject_scores"]]
    for b in bars:
        assert abs(float(b["height"]) - float(b["data-value"]) * 1.6) < 0.01
    att = [(b["data-label"], float(b["data-value"])) for b in charts["chart-attendance"]]
    assert att == [("AM301", 80.0), ("AM302", 80.0), ("AM303", 80.0)]
    record(f"subject bars={[(b['data-label'], b['data-value'], b['height']) for b in bars]}; attendance bars={att}")


@tc("TC-VIS-02.2", "APAS-F-011")
def test_line_graph_matches_sgpa_trend(client, login, record):
    """Line graph plots the semester SGPA trend correctly
    Objective: Verify the SGPA line graph against calculated SGPA values.
    Preconditions: Aarav SGPA 9.09, 9.36, 9.73.
    Steps:
    1. Render /dashboard?student_id=PES1UG24AM001 and read the line-graph points.
    Expected: Three points in semester order with data-value = SGPA; y = 200 - 16 x SGPA (higher SGPA plotted higher).
    """
    h = login("fac.rao")
    pts = parse(client.get("/dashboard?student_id=PES1UG24AM001", headers=h).data).charts["chart-sgpa"]
    values = [float(p["data-value"]) for p in pts]
    assert values == [9.09, 9.36, 9.73]
    for p in pts:
        assert abs(float(p["cy"]) - (200 - 16 * float(p["data-value"]))) < 0.01
    assert float(pts[0]["cy"]) > float(pts[1]["cy"]) > float(pts[2]["cy"])
    record(f"points={[(p['data-label'], p['data-value'], p['cy']) for p in pts]}")


@tc("TC-VIS-02.3", "APAS-F-011")
def test_charts_update_after_change(client, login, record):
    """Charts reflect newly recorded data
    Objective: Verify that visualisations are generated from current data.
    Preconditions: Kabir AM302 ISA=18, ESA=17 (35%).
    Test data: AM302 ESA updated to 32 -> 50%.
    Steps:
    1. POST the new grade as fac.rao.
    2. Render Kabir's dashboard.
    Expected: AM302 bar shows 50.0 with height 80 px.
    """
    h = login("fac.rao")
    client.post("/api/students/PES1UG24AM003/grades", headers=h,
                json={"subject_code": "AM302", "assessment": "ESA", "score": 32})
    bars = parse(client.get("/dashboard?student_id=PES1UG24AM003", headers=h).data).charts["chart-subjects"]
    am302 = next(b for b in bars if b["data-label"] == "AM302")
    assert float(am302["data-value"]) == 50.0 and float(am302["height"]) == 80.0
    record(f"AM302 bar value={am302['data-value']} height={am302['height']}")


@tc("TC-VIS-02.4", "APAS-F-011")
def test_chart_without_data(client, login, record):
    """Dashboards without data show a message instead of an empty chart
    Objective: Verify chart behaviour when there is no data.
    Preconditions: Meera (AM006) has no records.
    Steps:
    1. Render /dashboard?student_id=PES1UG24AM006.
    Expected: HTTP 200; no chart SVGs; "No data recorded yet" / "No completed semesters yet" messages.
    """
    page = client.get("/dashboard?student_id=PES1UG24AM006", headers=login("fac.rao"))
    assert page.status_code == 200 and parse(page.data).charts == {}
    assert b"No data recorded yet" in page.data and b"No completed semesters yet" in page.data
    record("HTTP 200; no SVG charts rendered; empty-state messages shown")


# --------------------------------------------------------------------------
# APAS-F-012 reports
# --------------------------------------------------------------------------
def report_rows(resp):
    return list(csv.reader(io.StringIO(resp.data.decode())))


@tc("TC-REP-01.1", "APAS-F-012")
def test_generate_csv_report(client, login, record):
    """Faculty generates and downloads an accurate CSV report
    Objective: Verify report generation, content accuracy and download headers.
    Preconditions: fac.rao logged in; Aarav records seeded.
    Test data: student_id=PES1UG24AM001, format=csv.
    Steps:
    1. POST /api/reports.
    2. Parse the CSV.
    Expected: HTTP 200, text/csv, Content-Disposition attachment named APAS_Report_PES1UG24AM001_<date>.csv; 9 subject rows; CGPA 9.39; overall 86.91; attendance 57/60 = 95.0.
    """
    resp = client.post("/api/reports", headers=login("fac.rao"),
                       json={"student_id": "PES1UG24AM001", "format": "csv"})
    rows = report_rows(resp)
    disp = resp.headers["Content-Disposition"]
    lookup = {r[0]: r[1:] for r in rows if r}
    subject_rows = [r for r in rows if len(r) == 10 and r[0].isdigit()]
    assert resp.status_code == 200 and resp.mimetype == "text/csv"
    assert disp == f'attachment; filename="APAS_Report_PES1UG24AM001_{date.today().isoformat()}.csv"'
    assert len(subject_rows) == 9
    assert lookup["CGPA"] == ["9.39"] and lookup["Overall percentage"] == ["86.91"]
    assert lookup["Overall attendance"] == ["57", "60", "95.0"]
    assert lookup["Student ID"] == ["PES1UG24AM001"] and lookup["Flags"] == ["None"]
    record(f"HTTP 200 {resp.mimetype}; {disp}; {len(subject_rows)} subject rows; CGPA {lookup['CGPA'][0]}; "
           f"overall {lookup['Overall percentage'][0]}; attendance {lookup['Overall attendance']}")


@tc("TC-REP-01.2", "APAS-F-012")
def test_report_contains_flags_and_json(client, login, record):
    """Reports include threshold flags and are available as JSON
    Objective: Verify report summaries for a flagged student and JSON format.
    Preconditions: admin logged in; Kabir failed AM302.
    Steps:
    1. POST /api/reports for Kabir in CSV and JSON formats.
    Expected: CSV "Flags" row contains "Failed AM302 (35.0%)"; JSON report contains the same CGPA 5.52 and a .json attachment name.
    """
    h = login("admin")
    csv_resp = client.post("/api/reports", headers=h, json={"student_id": "PES1UG24AM003"})
    json_resp = client.post("/api/reports", headers=h, json={"student_id": "PES1UG24AM003", "format": "json"})
    flags = {r[0]: r[1:] for r in report_rows(csv_resp) if r}["Flags"][0]
    assert "Failed AM302 (35.0%)" in flags
    assert json_resp.get_json()["performance"]["cgpa"] == 5.52
    assert json_resp.headers["Content-Disposition"].endswith('.json"')
    record(f"CSV flags='{flags}'; JSON CGPA={json_resp.get_json()['performance']['cgpa']}")


@tc("TC-REP-01.3", "APAS-F-012")
def test_report_access_and_validation(client, login, record):
    """Report requests are validated and restricted to permitted students
    Objective: Verify report authorisation and input validation.
    Preconditions: aarav (student), fac.rao logged in.
    Steps:
    1. aarav requests own report (no student_id).
    2. aarav requests Kabir's report.
    3. fac.rao requests a report for PES1UG24AM999.
    4. fac.rao requests format "pdf".
    Expected: 1 -> 200 (own report); 2 -> 403; 3 -> 404; 4 -> 400.
    """
    s = login("aarav")
    f = login("fac.rao")
    own = client.post("/api/reports", headers=s, json={})
    other = client.post("/api/reports", headers=s, json={"student_id": "PES1UG24AM003"})
    missing = client.post("/api/reports", headers=f, json={"student_id": "PES1UG24AM999"})
    bad_fmt = client.post("/api/reports", headers=f, json={"student_id": "PES1UG24AM001", "format": "pdf"})
    codes = [own.status_code, other.status_code, missing.status_code, bad_fmt.status_code]
    assert codes == [200, 403, 404, 400]
    assert "PES1UG24AM001" in own.headers["Content-Disposition"]
    record(f"own/other/missing/bad format -> {codes}")
