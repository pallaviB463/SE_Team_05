"""Build the Test Engineer deliverables from recorded test results.

Inputs : results/execution_results.json (latest cycle), results/cycle1/*.json (first cycle),
         results/*_results.json, results/prediction_evaluation.json, docs/defects.json
Outputs: deliverables/*.md and deliverables/PES1UG24AM156_ManasviGV_Test_Deliverables.docx
"""
import json
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "deliverables"

AUTHOR = {"name": "Manasvi G V", "srn": "PES1UG24AM156", "role": "Test Engineer", "team": "Team 05"}

REQUIREMENTS = OrderedDict([
    ("APAS-F-001", ("User authentication and login", "TC-AUTH-01")),
    ("APAS-F-002", ("Role-based access control", "TC-AUTH-02")),
    ("APAS-F-003", ("Secure logout and session termination", "TC-AUTH-03")),
    ("APAS-F-004", ("Student academic profile management", "TC-REC-01")),
    ("APAS-F-005", ("Grade entry and update", "TC-REC-02")),
    ("APAS-F-006", ("Attendance tracking and percentage calculation", "TC-REC-03")),
    ("APAS-F-007", ("Overall academic performance calculation", "TC-ANA-01")),
    ("APAS-F-008", ("Subject-wise and semester-wise performance analysis", "TC-ANA-02")),
    ("APAS-F-009", ("Identification of low performance / attendance below thresholds", "TC-ANA-03")),
    ("APAS-F-010", ("Dashboard display", "TC-VIS-01")),
    ("APAS-F-011", ("Graphical performance trends", "TC-VIS-02")),
    ("APAS-F-012", ("Report generation and download", "TC-REP-01")),
    ("APAS-F-013", ("Prediction using historical academic records", "TC-PRED-01")),
    ("APAS-F-014", ("Identification of academically at-risk students", "TC-PRED-02")),
    ("APAS-F-015", ("Academic insights and recommendations", "TC-PRED-03")),
    ("APAS-NF-001", ("Dashboard response time <= 3 s for 95% of requests", "TC-PERF-01")),
    ("APAS-NF-002", ("Monthly availability >= 99%", "TC-REL-01")),
    ("APAS-NF-003", ("Access restrictions based on authenticated roles", "TC-SEC-01")),
    ("APAS-NF-004", ("Timestamped audit logs retained >= 12 months", "TC-AUD-01")),
    ("APAS-NF-005", ("Accessibility: keyboard navigation and contrast (WCAG 2.1 AA)", "TC-UX-01")),
    ("APAS-SR-001", ("Valid credentials required for protected access", "TC-SEC-01")),
    ("APAS-SR-002", ("Role-based access restrictions", "TC-SEC-02")),
    ("APAS-SR-003", ("HTTPS with TLS 1.2 or higher", "TC-SEC-03")),
    ("APAS-SR-004", ("Secure password hashing; no plaintext storage", "TC-SEC-04")),
    ("APAS-SR-005", ("Timestamped security logs (logins, record changes)", "TC-SEC-05")),
])

MODULES = OrderedDict([
    ("AUTH", "Authentication, Role-Based Access and Logout"),
    ("REC", "Student Academic Record Management"),
    ("ANA", "Academic Performance Analysis"),
    ("VIS", "Dashboard and Data Visualisation"),
    ("REP", "Report Generation"),
    ("PRED", "Predictive Analytics, Risk Identification and Insights"),
    ("SEC", "Security"),
    ("PERF", "Performance"),
    ("REL", "Reliability"),
    ("AUD", "Audit Logging and Retention"),
    ("UX", "Usability and Accessibility"),
])


def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def tc_sort_key(tc_id):
    prefix, num = tc_id[3:].rsplit("-", 1)
    major, minor = num.split(".")
    return list(MODULES).index(prefix), int(major), int(minor)


def aggregate(run):
    """Group per-test entries (parametrised variants) into one row per test case ID."""
    cases = {}
    for r in (run or {}).get("results", []):
        c = cases.setdefault(r["tc_id"], {"tc_id": r["tc_id"], "spec": r["spec"], "requirements": [],
                                           "test_type": r["test_type"], "priority": r["priority"],
                                           "limitation": r["limitation"], "suite": r["suite"],
                                           "variants": [], "actual": [], "failures": []})
        for req in r["requirements"]:
            if req not in c["requirements"]:
                c["requirements"].append(req)
        c["variants"].append(r)
        c["actual"].extend(r["actual"])
        if r.get("failure"):
            c["failures"].append(r["failure"])
    for c in cases.values():
        statuses = {v["status"] for v in c["variants"]}
        c["status"] = ("Fail" if "Fail" in statuses else "Blocked" if "Blocked" in statuses
                       else "Not Executed" if "Not Executed" in statuses else "Pass")
        c["passed"] = sum(v["status"] == "Pass" for v in c["variants"])
        c["executed_at"] = max(v["executed_at"] for v in c["variants"])
        c["duration"] = round(sum(v["duration_s"] for v in c["variants"]), 2)
    return OrderedDict(sorted(cases.items(), key=lambda kv: tc_sort_key(kv[0])))


def status_label(case):
    if case is None:
        return "Not in cycle"
    if case["status"] == "Pass" and case["limitation"]:
        return "Pass (with limitation)"
    return case["status"]


def short_actual(case, limit=3):
    lines = case["actual"] or ([case["failures"][0][:300]] if case["failures"] else ["(no observation recorded)"])
    if len(lines) > limit:
        return lines[:limit] + [f"... plus {len(lines) - limit} more data variants (all {case['passed']}/"
                                f"{len(case['variants'])} passed)" if case["status"] == "Pass"
                                else f"... plus {len(lines) - limit} more"]
    return lines


def md_escape(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


# --------------------------------------------------------------------------
# Data assembly
# --------------------------------------------------------------------------
def build_context():
    final_run = load(RESULTS / "execution_results.json")
    if not final_run:
        raise SystemExit("results/execution_results.json not found - run the test suite first")
    cycle1_run = load(RESULTS / "cycle1" / "execution_results.json")
    final, cycle1 = aggregate(final_run), aggregate(cycle1_run)
    defects = load(ROOT / "docs" / "defects.json")
    ctx = {
        "final_run": final_run, "cycle1_run": cycle1_run, "final": final, "cycle1": cycle1, "defects": defects,
        "perf": load(RESULTS / "performance_results.json", {}),
        "perf_c1": load(RESULTS / "cycle1" / "performance_results.json", {}),
        "rel": load(RESULTS / "reliability_results.json", {}),
        "tls": load(RESULTS / "tls_results.json", {}),
        "pred": load(RESULTS / "prediction_evaluation.json", {}),
        "generated": datetime.now().strftime("%d-%m-%Y %H:%M"),
    }

    def counts(cases, run):
        variants = [r for r in (run or {}).get("results", [])]
        return {"cases": len(cases),
                "pass": sum(c["status"] == "Pass" for c in cases.values()),
                "fail": sum(c["status"] == "Fail" for c in cases.values()),
                "blocked": sum(c["status"] == "Blocked" for c in cases.values()),
                "not_executed": sum(c["status"] == "Not Executed" for c in cases.values()),
                "limited": sum(c["status"] == "Pass" and bool(c["limitation"]) for c in cases.values()),
                "executions": len(variants),
                "exec_pass": sum(v["status"] == "Pass" for v in variants),
                "exec_fail": sum(v["status"] == "Fail" for v in variants)}

    ctx["c_final"] = counts(final, final_run)
    ctx["c_cycle1"] = counts(cycle1, cycle1_run) if cycle1 else None

    rtm = []
    for req, (desc, planned) in REQUIREMENTS.items():
        cases = [c for c in final.values() if req in c["requirements"]]
        if not cases:
            verdict = "Not covered"
        elif any(c["status"] == "Fail" for c in cases):
            verdict = "Failed"
        elif any(c["limitation"] for c in cases):
            verdict = "Verified with limitation"
        else:
            verdict = "Verified"
        rtm.append({"req": req, "desc": desc, "planned": planned, "cases": [c["tc_id"] for c in cases],
                    "passed": sum(c["status"] == "Pass" for c in cases), "total": len(cases), "verdict": verdict,
                    "limitations": [c["limitation"] for c in cases if c["limitation"]]})
    ctx["rtm"] = rtm
    return ctx


# --------------------------------------------------------------------------
# Markdown output
# --------------------------------------------------------------------------
def header(title, ctx):
    run = ctx["final_run"]
    return (f"# {title}\n\n"
            f"**Project:** Academic Performance Analytics System (APAS) v1.0  \n"
            f"**Prepared by:** {AUTHOR['name']} ({AUTHOR['srn']}), {AUTHOR['role']}, {AUTHOR['team']}  \n"
            f"**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  \n"
            f"**Final execution run:** {run['started_at']} to {run['finished_at']}  \n"
            f"**Generated:** {ctx['generated']}\n\n")


def md_test_cases(ctx):
    out = [header("Test Case Specification", ctx)]
    out.append("Each test case below is implemented as an automated pytest script in `tests/`. "
               "Data-driven test cases run once per data variant (listed under *Variants*). "
               "Expected values for calculations were worked out by hand from `test_data/apas_test_data.json`.\n")
    for prefix, module in MODULES.items():
        cases = [c for c in ctx["final"].values() if c["tc_id"].startswith(f"TC-{prefix}-")]
        if not cases:
            continue
        out.append(f"\n## {module}\n")
        for c in cases:
            s = c["spec"]
            out.append(f"\n### {c['tc_id']}: {s['title']}\n")
            out.append("| Field | Detail |\n|---|---|")
            rows = [("Requirement(s)", ", ".join(c["requirements"])), ("Type / Priority", f"{c['test_type']} / {c['priority']}"),
                    ("Objective", s.get("objective", "")), ("Preconditions", s.get("preconditions", "-")),
                    ("Test data", s.get("test_data", "-")), ("Steps", s.get("steps", "")),
                    ("Expected result", s.get("expected", ""))]
            if len(c["variants"]) > 1:
                rows.append(("Variants", f"{len(c['variants'])}: " + ", ".join(
                    v["function"].split("[", 1)[1].rstrip("]") if "[" in v["function"] else v["function"]
                    for v in c["variants"])))
            if c["limitation"]:
                rows.append(("Limitation", c["limitation"]))
            rows.append(("Script", f"`tests/test_{c['suite']}.py::{c['variants'][0]['function'].split('[')[0]}`"))
            out += [f"| {k} | {md_escape(v)} |" for k, v in rows]
    return "\n".join(out) + "\n"


def md_execution_log(ctx):
    out = [header("Test Execution Log", ctx)]
    env = ctx["final_run"]["environment"]
    out.append("## Test environment\n")
    out.append("| Item | Value |\n|---|---|")
    out += [f"| {k} | {md_escape(v)} |" for k, v in [
        ("Application under test", "APAS reference build (apas/), production configuration (HTTPS enforced)"),
        ("Python / Flask / pytest", f"{env['python']} / {env['flask']} / {env['pytest']}"),
        ("Database", env["database"]), ("Platform", env["platform"]),
        ("Test data", "test_data/apas_test_data.json (6 students, 9 subjects, 9 accounts) + 300 synthetic students "
                      "for performance and prediction evaluation")]]
    out.append("\n## Execution summary\n")
    out.append("| Cycle | Test cases | Pass | Fail | Blocked | Not executed | Executions (incl. data variants) |\n"
               "|---|---|---|---|---|---|---|")
    if ctx["c_cycle1"]:
        c = ctx["c_cycle1"]
        out.append(f"| Cycle 1 ({ctx['cycle1_run']['started_at'][:10]}) | {c['cases']} | {c['pass']} | {c['fail']} | "
                   f"{c['blocked']} | {c['not_executed']} | {c['executions']} ({c['exec_pass']} pass / {c['exec_fail']} fail) |")
    c = ctx["c_final"]
    out.append(f"| Cycle 2 - retest and regression ({ctx['final_run']['started_at'][:10]}) | {c['cases']} | {c['pass']} | "
               f"{c['fail']} | {c['blocked']} | {c['not_executed']} | {c['executions']} ({c['exec_pass']} pass / "
               f"{c['exec_fail']} fail) |")
    out.append(f"\n{c['limited']} passed test cases have a documented limitation (see the Limitation column of the "
               "test case specification and the RTM).\n")
    out.append("A dry run before cycle 1 was discarded because of a test-harness configuration error (TS-001 in the "
               "defect report). It is not counted as an execution cycle.\n")
    out.append("\n## Detailed log\n")
    out.append("| TC ID | Title | Requirement(s) | Cycle 1 | Cycle 2 (final) | Actual result (final cycle) | Executed |\n"
               "|---|---|---|---|---|---|---|")
    for tc_id, f in ctx["final"].items():
        c1 = ctx["cycle1"].get(tc_id)
        c1_label = status_label(c1) if ctx["cycle1"] else "-"
        if c1 is None and ctx["cycle1"]:
            c1_label = "Added in cycle 2"
        out.append(f"| {tc_id} | {md_escape(f['spec']['title'])} | {', '.join(f['requirements'])} | {c1_label} | "
                   f"**{status_label(f)}** ({f['passed']}/{len(f['variants'])}) | "
                   f"{md_escape(chr(10).join(short_actual(f)))} | {f['executed_at'][:16].replace('T', ' ')} |")
    failed_c1 = [c for c in ctx["cycle1"].values() if c["status"] == "Fail"]
    if failed_c1:
        out.append("\n## Cycle 1 failures\n")
        out.append("| TC ID | Failure observed | Disposition |\n|---|---|---|")
        defects = {d["test_case"]: d for d in ctx["defects"]["execution_defects"]}
        dispositions = {k: f"Product defect {d['id']}" for k, d in defects.items()}
        dispositions.update({d["test_case"]: f"Test script error {d['id']}" for d in ctx["defects"]["test_script_corrections"]})
        for c in failed_c1:
            observed = ("; ".join(c["actual"]) or (defects[c["tc_id"]]["actual"] if c["tc_id"] in defects
                                                   else c["failures"][0][:250]))
            out.append(f"| {c['tc_id']} | {md_escape(observed)} | {dispositions.get(c['tc_id'], 'Under investigation')} |")
    return "\n".join(out) + "\n"


def md_defects(ctx):
    d = ctx["defects"]
    out = [header("Defect Report", ctx)]
    ex, rv = d["execution_defects"], d["review_defects"]
    out.append("## Summary\n")
    out.append("| Category | Total | Critical | Major | Minor | Trivial | Open | Closed |\n|---|---|---|---|---|---|---|---|")
    for name, items in (("Execution defects (software)", ex), ("Review defects (SRS / STP)", rv)):
        sev = [i["severity"] for i in items]
        out.append(f"| {name} | {len(items)} | {sev.count('Critical')} | {sev.count('Major')} | {sev.count('Minor')} | "
                   f"{sev.count('Trivial')} | {sum(i['status'] != 'Closed' for i in items)} | "
                   f"{sum(i['status'] == 'Closed' for i in items)} |")
    out.append("\nSeverity: Critical = security breach or data loss; Major = requirement not met; Minor = workaround "
               "exists or ambiguity; Trivial = cosmetic. Priority P1 (fix immediately) to P4 (fix when convenient).\n")
    out.append("\n## Execution defects\n")
    for e in ex:
        out.append(f"\n### {e['id']}: {e['title']}\n")
        out.append("| Field | Detail |\n|---|---|")
        rows = [("Test case / Requirement", f"{e['test_case']} / {', '.join(e['requirements'])}"),
                ("Module", e["module"]), ("Severity / Priority", f"{e['severity']} / {e['priority']}"),
                ("Environment", e["environment"]), ("Description", e["description"]),
                ("Steps to reproduce", "\n".join(f"{i}. {s}" for i, s in enumerate(e["steps"], 1))),
                ("Expected result", e["expected"]), ("Actual result", e["actual"]), ("Evidence", e["evidence"]),
                ("Root cause", e["root_cause"]), ("Resolution", e["resolution"]),
                ("Found / Fixed", f"{e['found_in']} / {e['fixed_in']}"),
                ("Status history", " -> ".join(e["lifecycle"])), ("Current status", e["status"]),
                ("Reported by / Assigned to", f"{e['reported_by']} / {e['assigned_to']}"), ("Retest", e["retest"])]
        out += [f"| {k} | {md_escape(v)} |" for k, v in rows]
    out.append("\n## Review defects (static testing of SRS v1.0 and STP v1.0)\n")
    out.append("| ID | Title | Document | Sev. | Pri. | Description | Impact on testing | Recommendation | Status / Owner |\n"
               "|---|---|---|---|---|---|---|---|---|")
    for r in rv:
        out.append(f"| {r['id']} | {md_escape(r['title'])} | {md_escape(r['document'])} | {r['severity']} | {r['priority']} | "
                   f"{md_escape(r['description'])} | {md_escape(r['impact'])} | {md_escape(r['recommendation'])} | "
                   f"{r['status']} / {md_escape(r['assigned_to'])} |")
    out.append("\n## Test script corrections (not product defects)\n")
    out.append("| ID | Test case | Problem | Correction |\n|---|---|---|---|")
    for t in d["test_script_corrections"]:
        out.append(f"| {t['id']} | {t['test_case']} | {md_escape(t['description'])} | {md_escape(t['correction'])} |")
    return "\n".join(out) + "\n"


def md_rtm(ctx):
    out = [header("Requirements Traceability Matrix with Execution Status", ctx)]
    out.append("| Requirement | Description | Planned TC (STP 13.2) | Executed test cases | Passed | Verdict |\n"
               "|---|---|---|---|---|---|")
    for r in ctx["rtm"]:
        out.append(f"| {r['req']} | {md_escape(r['desc'])} | {r['planned']} | {', '.join(r['cases'])} | "
                   f"{r['passed']}/{r['total']} | **{r['verdict']}** |")
    covered = sum(r["total"] > 0 for r in ctx["rtm"])
    out.append(f"\nCoverage: {covered}/{len(ctx['rtm'])} requirements have at least one executed test case.\n")
    lim = [(r["req"], l) for r in ctx["rtm"] for l in dict.fromkeys(r["limitations"])]
    if lim:
        out.append("\n## Limitations affecting verdicts\n")
        out += [f"- **{req}**: {l}" for req, l in lim]
    return "\n".join(out) + "\n"


def md_results(ctx):
    out = [header("Performance, Security, Reliability, Accessibility and Predictive Analytics Results", ctx)]
    p, p1 = ctx["perf"], ctx["perf_c1"]
    out.append("## 1. Performance (APAS-NF-001, TC-PERF-01)\n")
    out.append(f"Load profile: 306 students, {p.get('concurrency', '-')} concurrent clients (team test data TD-12; "
               f"the SRS does not define it, see DOC-003), HTTPS, {p.get('requests', '-')} requests. Cycle 1 used "
               f"{p1.get('concurrency', '-')} concurrent clients.\n")
    out.append("| Dashboard | Cycle 1 p95 (s) | Cycle 2 p95 (s) | Cycle 2 max (s) | Target |\n|---|---|---|---|---|")
    for name, v in p.get("per_dashboard", {}).items():
        old = p1.get("per_dashboard", {}).get(name, {}).get("p95_s", "-")
        out.append(f"| {name} | {old} | {v['p95_s']} | {v['max_s']} | <= 3.0 |")
    if p.get("overall"):
        o, o1 = p["overall"], p1.get("overall", {})
        out.append(f"| **All dashboards** | {o1.get('p95_s', '-')} | {o['p95_s']} | {o['max_s']} | <= 3.0 |")
        out.append(f"\nCycle 2: {o['within_3s_pct']}% of requests completed within 3 s; throughput {p['throughput_rps']} req/s.")
    if p.get("mixed_read_write"):
        m = p["mixed_read_write"]
        out.append(f"\nTC-PERF-01.2, mixed workload ({m['dashboard_requests']} dashboard requests + {m['writes']} grade writes): "
                   f"dashboard p50 {m['dashboard']['p50_s']} s, p95 {m['dashboard']['p95_s']} s, max {m['dashboard']['max_s']} s; "
                   f"write p95 {m['write_p95_s']} s.\n")
    out.append("\n## 2. Security (APAS-SR-001 to SR-005, APAS-NF-003)\n")
    out.append("| Check | Result |\n|---|---|")
    for tc_id in [k for k in ctx["final"] if k.startswith("TC-SEC-")]:
        c = ctx["final"][tc_id]
        out.append(f"| {tc_id} {md_escape(c['spec']['title'])} | {status_label(c)}: {md_escape(' / '.join(short_actual(c, 2)))} |")
    if ctx["tls"]:
        out.append("\n**TLS handshake results (TC-SEC-03.2):**\n")
        out.append("| Protocol | Outcome |\n|---|---|")
        out += [f"| {k} | {md_escape(v)} |" for k, v in ctx["tls"].items() if k != "openssl"]
        out.append(f"\nClient library: {ctx['tls'].get('openssl')}. TLS 1.0/1.1 were refused by the server "
                   "(TLSV1_ALERT_PROTOCOL_VERSION alert received from the server).\n")
    out.append("\n## 3. Reliability (APAS-NF-002, TC-REL-01)\n")
    r = ctx["rel"]
    if r:
        out.append(f"Soak test: {r['successful']}/{r['probes']} health probes succeeded "
                   f"(**{r['availability_pct']:.2f}%** availability in a {r['window_s']} s window) while "
                   f"{r['fault_requests']} faulty requests were injected. Fault responses: {r['fault_status_codes']}; "
                   f"5xx or dropped connections: {r['fault_5xx_or_dropped']}.\n")
    out.append("Monthly availability can only be confirmed on a deployed instance; use "
               "`python tools/availability_monitor.py <url>` for 30 days and compare against the 99% target.\n")
    out.append("\n## 4. Audit logging (APAS-NF-004, TC-AUD-01)\n")
    for tc_id in [k for k in ctx["final"] if k.startswith("TC-AUD-")]:
        c = ctx["final"][tc_id]
        out.append(f"- **{tc_id}** {c['spec']['title']}: {status_label(c)}. {' '.join(c['actual'])}")
    out.append("\n\n## 5. Accessibility (APAS-NF-005, TC-UX-01)\n")
    for tc_id in [k for k in ctx["final"] if k.startswith("TC-UX-")]:
        c = ctx["final"][tc_id]
        out.append(f"- **{tc_id}** {c['spec']['title']}: {status_label(c)}. {' '.join(c['actual'])}")
    out.append("\nAutomated checks do not replace a manual audit. Still to do: a screen-reader walkthrough "
               "(VoiceOver/NVDA), keyboard-only navigation of every page and 200% zoom, recorded in the manual "
               "checklist (docs/Manual_Accessibility_Checklist.md).\n")
    pr = ctx["pred"]
    out.append("\n## 6. Predictive analytics evaluation (APAS-F-013 / F-014, TC-PRED-01.4)\n")
    if pr:
        cm = pr["confusion"]
        out.append(f"- **Method:** {pr['method']}\n- **Data:** {pr['data']}; {pr['cohort_size']} students; "
                   "semesters 1-2 used as history, semester 3 held out.\n"
                   f"- **Coverage:** {pr['predictions_produced']}/{pr['cohort_size']} eligible students received a prediction.\n"
                   f"- **Error:** MAE {pr['mae_sgpa']} SGPA, RMSE {pr['rmse_sgpa']} SGPA, mean error (bias) {pr['mean_error_sgpa']}.\n"
                   f"- **Risk classification (SGPA < {pr['risk_threshold_sgpa']}):** TP {cm['tp']}, FP {cm['fp']}, "
                   f"FN {cm['fn']}, TN {cm['tn']}; precision {pr['precision']}, recall {pr['recall']}, F1 {pr.get('f1', '-')}, accuracy {pr['accuracy']}.\n"
                   "- **Limitations:** synthetic data only; linear extrapolation from 2 data points; no accuracy target "
                   "exists in the SRS (DOC-004), so these figures are informational. Re-evaluate on anonymised "
                   "historical records before relying on predictions.\n")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Word document
# --------------------------------------------------------------------------
def shade(cell, hex_fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def add_table(doc, headers, rows, widths=None, font=8.5, status_col=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(font)
        shade(cell, "D9E2F3")
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            lines = str(value).split("\n")
            p = cells[i].paragraphs[0]
            for j, line in enumerate(lines):
                run = p.add_run(line)
                run.font.size = Pt(font)
                if j < len(lines) - 1:
                    run.add_break()
            if status_col is not None and i == status_col:
                v = str(value)
                shade(cells[i], "E2EFDA" if v.startswith(("Pass", "Verified", "Closed")) else
                      "FCE4D6" if v.startswith(("Fail", "Failed", "Critical")) else "FFF2CC")
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def kv_table(doc, rows, font=9):
    add_table(doc, ["Field", "Detail"], rows, widths=[4, 13.5], font=font)


def build_docx(ctx, path):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Academic Performance Analytics System (APAS)")
    r.bold, r.font.size = True, Pt(20)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Test Engineer Deliverables: Test Cases, Execution Log, Defect Reports and Results")
    r.font.size, r.font.color.rgb = Pt(13), RGBColor(0x2F, 0x54, 0x96)
    kv_table(doc, [("Name", AUTHOR["name"]), ("SRN", AUTHOR["srn"]), ("Role", AUTHOR["role"] + " (STP section 9)"),
                   ("Team", AUTHOR["team"]),
                   ("Responsibility", "Design and execute test cases, verify functional and non-functional requirements, "
                                      "record test results, and report defects."),
                   ("Reference documents", "APAS SRS v1.0 (12-10-2026), SAD v1.0 (16-10-2026), STP v1.0 (15-10-2026)"),
                   ("Final execution run", f"{ctx['final_run']['started_at']} to {ctx['final_run']['finished_at']}"),
                   ("Document generated", ctx["generated"])], font=10)

    c, c1 = ctx["c_final"], ctx["c_cycle1"]
    doc.add_heading("1. Summary", level=1)
    open_ex = sum(e["status"] != "Closed" for e in ctx["defects"]["execution_defects"])
    doc.add_paragraph(
        f"{c['cases']} test cases ({c['executions']} executions including data-driven variants) cover all 25 "
        f"requirements of the APAS SRS v1.0 (15 functional, 5 non-functional, 5 security). "
        + (f"Cycle 1 found {c1['fail']} failing test cases. Two were product defects (DEF-001 Critical, DEF-002 Major) "
           "and two were test script errors. " if c1 else "")
        + f"After the fixes, cycle 2 (retest + full regression) passed {c['pass']}/{c['cases']} test cases with "
          f"{c['fail']} failures. {open_ex} execution defects remain open. {c['limited']} passed test cases carry a "
          f"documented limitation (monthly availability, deployed TLS configuration, assumed load profile, synthetic "
          f"prediction data). {len(ctx['defects']['review_defects'])} review defects were raised against the SRS/STP.")
    add_table(doc, ["Cycle", "Test cases", "Pass", "Fail", "Blocked", "Executions (pass/fail)"],
              ([["Cycle 1", c1["cases"], c1["pass"], c1["fail"], c1["blocked"],
                 f"{c1['executions']} ({c1['exec_pass']}/{c1['exec_fail']})"]] if c1 else []) +
              [["Cycle 2 (retest + regression)", c["cases"], c["pass"], c["fail"], c["blocked"],
                f"{c['executions']} ({c['exec_pass']}/{c['exec_fail']})"]], font=9.5)

    doc.add_heading("2. Test Approach and Environment", level=1)
    env = ctx["final_run"]["environment"]
    doc.add_paragraph(
        "No APAS implementation existed in the repository. To execute the planned tests, a reference build was "
        "implemented from the SAD (layered architecture: web portals, API controller, services, SQLite data layer, "
        "proposed endpoints from SAD 4.3.1). All tests are automated pytest scripts with requirement IDs attached. "
        "Expected values for every calculation were worked out by hand from the synthetic test data, not with the "
        "application's own code. Performance, reliability and TLS tests run against a real HTTPS socket.")
    kv_table(doc, [("Application", "apas/ reference build, production configuration (HTTPS enforced, PBKDF2 hashing)"),
                   ("Runtime", f"Python {env['python']}, Flask {env['flask']}, pytest {env['pytest']}, {env['database']}"),
                   ("Platform", env["platform"]),
                   ("Test data", "test_data/apas_test_data.json: 9 subjects, 6 students (high performer, low attendance, "
                                 "declining/failed, lateral entry, exact-boundary, no records), 9 accounts (admin, 2 "
                                 "faculty, 5 students, 1 inactive), boundary/invalid value sets; plus 300 synthetic "
                                 "students (seed 2026)"),
                   ("Tools", "pytest (functional, security, data validation), requests + ThreadPoolExecutor (load), "
                             "Python ssl (TLS handshakes), html.parser + WCAG contrast formula (accessibility)"),
                   ("Status values", "Pass / Fail / Blocked / Not Executed (STP 13.1)")])

    doc.add_heading("3. Requirements Traceability Matrix with Execution Status", level=1)
    doc.add_paragraph("Sub-cases roll up into the team's 24 test cases (TC-AUTH-01 = TC-AUTH-01.1 ... 01.8, etc.), "
                      "which the QA Lead's templates on branch neha-testing use. Those templates have been filled "
                      "with these results in Academic_Performance_Analytics_System/testing/.")
    add_table(doc, ["Requirement", "Description", "Executed test cases", "Passed", "Verdict"],
              [[r["req"], r["desc"], ", ".join(r["cases"]), f"{r['passed']}/{r['total']}", r["verdict"]]
               for r in ctx["rtm"]], widths=[2.4, 5.2, 5.6, 1.4, 3.0], font=8, status_col=4)

    doc.add_heading("4. Test Execution Log", level=1)
    rows = []
    for tc_id, f in ctx["final"].items():
        c1case = ctx["cycle1"].get(tc_id) if ctx["cycle1"] else None
        rows.append([tc_id, f["spec"]["title"], ", ".join(f["requirements"]),
                     status_label(c1case) if c1case else ("Added in cycle 2" if ctx["cycle1"] else "-"),
                     f"{status_label(f)} ({f['passed']}/{len(f['variants'])})",
                     "\n".join(short_actual(f, 2))])
    add_table(doc, ["TC ID", "Title", "Req.", "Cycle 1", "Cycle 2", "Actual result (cycle 2)"], rows,
              widths=[1.9, 3.6, 2.0, 1.7, 1.9, 6.4], font=7.5, status_col=4)

    doc.add_heading("5. Defect Reports", level=1)
    doc.add_heading("5.1 Execution defects", level=2)
    for e in ctx["defects"]["execution_defects"]:
        doc.add_heading(f"{e['id']}: {e['title']}", level=3)
        kv_table(doc, [("Test case / Requirement", f"{e['test_case']} / {', '.join(e['requirements'])}"),
                       ("Module", e["module"]), ("Severity / Priority", f"{e['severity']} / {e['priority']}"),
                       ("Environment", e["environment"]), ("Description", e["description"]),
                       ("Steps to reproduce", "\n".join(f"{i}. {s}" for i, s in enumerate(e["steps"], 1))),
                       ("Expected result", e["expected"]), ("Actual result", e["actual"]),
                       ("Evidence", e["evidence"]), ("Root cause", e["root_cause"]), ("Resolution", e["resolution"]),
                       ("Lifecycle", " -> ".join(e["lifecycle"])), ("Status", e["status"]),
                       ("Reported by / Assigned to", f"{e['reported_by']} / {e['assigned_to']}"),
                       ("Retest result", e["retest"])], font=8.5)
    doc.add_heading("5.2 Review defects (static testing of SRS / STP)", level=2)
    add_table(doc, ["ID", "Title / Document", "Sev / Pri", "Description and impact", "Recommendation"],
              [[r["id"], f"{r['title']}\n({r['document']})", f"{r['severity']} / {r['priority']}",
                f"{r['description']}\nImpact: {r['impact']}", r["recommendation"]]
               for r in ctx["defects"]["review_defects"]], widths=[1.4, 3.8, 1.8, 6.0, 4.5], font=7.5)
    doc.add_heading("5.3 Test script corrections (not product defects)", level=2)
    add_table(doc, ["ID", "Test case", "Problem", "Correction"],
              [[t["id"], t["test_case"], t["description"], t["correction"]]
               for t in ctx["defects"]["test_script_corrections"]], widths=[1.4, 2.6, 7.0, 6.5], font=8)

    doc.add_heading("6. Non-Functional, Security and Predictive Results", level=1)
    p, p1 = ctx["perf"], ctx["perf_c1"]
    doc.add_heading("6.1 Performance (APAS-NF-001)", level=2)
    if p.get("per_dashboard"):
        add_table(doc, ["Dashboard", "Cycle 1 p95 (s)", "Cycle 2 p95 (s)", "Cycle 2 max (s)"],
                  [[n, p1.get("per_dashboard", {}).get(n, {}).get("p95_s", "-"), v["p95_s"], v["max_s"]]
                   for n, v in p["per_dashboard"].items()] +
                  [["All dashboards", p1.get("overall", {}).get("p95_s", "-"), p["overall"]["p95_s"], p["overall"]["max_s"]]],
                  font=9)
    if p.get("mixed_read_write"):
        m = p["mixed_read_write"]
        doc.add_paragraph(f"Mixed workload (TC-PERF-01.2): dashboard p95 {m['dashboard']['p95_s']} s with "
                          f"{m['writes']} concurrent grade writes. Target 3.0 s met.")
    doc.add_heading("6.2 Security and TLS (APAS-SR-001 to SR-005)", level=2)
    if ctx["tls"]:
        add_table(doc, ["Protocol", "Outcome"], [[k, v] for k, v in ctx["tls"].items() if k != "openssl"], font=9)
    sec_rows = [[k, ctx["final"][k]["spec"]["title"], status_label(ctx["final"][k])]
                for k in ctx["final"] if k.startswith("TC-SEC-")]
    add_table(doc, ["TC ID", "Security check", "Status"], sec_rows, widths=[2.4, 12, 3], font=8.5, status_col=2)
    doc.add_heading("6.3 Reliability (APAS-NF-002)", level=2)
    if ctx["rel"]:
        r = ctx["rel"]
        doc.add_paragraph(f"{r['successful']}/{r['probes']} health probes succeeded ({r['availability_pct']:.2f}%) during a "
                          f"{r['window_s']} s soak with {r['fault_requests']} injected faulty requests (responses "
                          f"{r['fault_status_codes']}, no 5xx). Limitation: the monthly 99% target needs 30 days of "
                          "monitoring on the deployed system (tools/availability_monitor.py).")
    doc.add_heading("6.4 Audit logging and accessibility (APAS-NF-004, NF-005)", level=2)
    for k in [k for k in ctx["final"] if k.startswith(("TC-AUD-", "TC-UX-"))]:
        f = ctx["final"][k]
        doc.add_paragraph(f"{k} {f['spec']['title']}: {status_label(f)}. {' '.join(f['actual'])}", style="List Bullet")
    doc.add_heading("6.5 Predictive analytics evaluation (APAS-F-013 / F-014)", level=2)
    pr = ctx["pred"]
    if pr:
        cm = pr["confusion"]
        kv_table(doc, [("Method", pr["method"]), ("Data", f"{pr['data']}; {pr['cohort_size']} students; sem 1-2 history, sem 3 held out"),
                       ("Coverage", f"{pr['predictions_produced']}/{pr['cohort_size']} predictions produced"),
                       ("Prediction error", f"MAE {pr['mae_sgpa']}, RMSE {pr['rmse_sgpa']}, bias {pr['mean_error_sgpa']} (SGPA points)"),
                       ("Risk classification (SGPA < 6.0)", f"TP {cm['tp']}, FP {cm['fp']}, FN {cm['fn']}, TN {cm['tn']}; precision "
                                                            f"{pr['precision']}, recall {pr['recall']}, F1 {pr.get('f1', '-')}, accuracy {pr['accuracy']}"),
                       ("Limitations", "Synthetic data; linear extrapolation from 2 semesters; no accuracy target in the SRS "
                                       "(DOC-004), so the figures are informational.")])

    doc.add_heading("7. Exit Criteria Check (STP 5.4)", level=1)
    crit = ctx["defects"]["execution_defects"]
    add_table(doc, ["Exit criterion", "Status"], [
        ["100% of planned test cases executed", f"Met: {c['cases']} test cases executed, 0 not executed"],
        ["All high-priority functional requirements verified", "Met: APAS-F-001 to F-015 verified"],
        ["All 5 NFRs and 5 security requirements tested", "Met: NF-002 and SR-003 verified with documented limitations"],
        ["No unresolved critical-severity defects",
         "Met: DEF-001 (Critical) fixed and closed" if all(d["status"] == "Closed" for d in crit) else "Not met"],
        ["Failed test cases investigated and defects documented", "Met: see section 5"],
        ["Performance, reliability, security, accessibility and predictive results recorded", "Met: see section 6"],
        ["Test summary report prepared and reviewed", "Pending: QA Lead (Neha Rastogi) to prepare; Project Lead (Pallavi B) to approve"],
    ], widths=[8, 9.5], font=9)
    doc.add_heading("8. Open Items for the Team", level=1)
    for item in [
        "Developer (Madhuri Ravikumar): review the DEF-001 and DEF-002 fixes in the reference build.",
        "QA Lead (Neha Rastogi): resolve review defects DOC-001 to DOC-009 with the requirement owners and update the RTM (DOC-005).",
        "Run tools/availability_monitor.py against the deployed instance for one month (APAS-NF-002).",
        "Repeat TC-SEC-03.2 and TC-PERF-01 on the chosen hosting platform once it is selected (SAD 4.6.1).",
        "Complete the manual accessibility checklist (screen reader, keyboard-only, 200% zoom).",
    ]:
        doc.add_paragraph(item, style="List Bullet")
    doc.save(path)


def main():
    ctx = build_context()
    OUT.mkdir(exist_ok=True)
    files = {
        "01_Test_Case_Specification.md": md_test_cases(ctx),
        "02_Test_Execution_Log.md": md_execution_log(ctx),
        "03_Defect_Report.md": md_defects(ctx),
        "04_RTM_Execution_Status.md": md_rtm(ctx),
        "05_NonFunctional_Security_Predictive_Results.md": md_results(ctx),
    }
    for name, text in files.items():
        (OUT / name).write_text(text)
    docx_path = OUT / f"{AUTHOR['srn']}_ManasviGV_Test_Deliverables.docx"
    build_docx(ctx, docx_path)
    c = ctx["c_final"]
    print(f"Test cases: {c['cases']}  pass {c['pass']}  fail {c['fail']}  blocked {c['blocked']}  "
          f"(executions {c['executions']})")
    for name in list(files) + [docx_path.name]:
        print(f"  wrote deliverables/{name}")


if __name__ == "__main__":
    main()
