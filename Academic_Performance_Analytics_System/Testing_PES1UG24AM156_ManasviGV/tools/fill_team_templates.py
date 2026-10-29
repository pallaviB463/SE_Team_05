"""Fill the QA Lead's testing templates (Neha Rastogi, branch neha-testing) with the executed results.

Reads the untouched templates in team_templates/ and the recorded results, and writes the
completed files into ../testing/ (the folder layout of the neha-testing branch). Each of the 24
team test cases (e.g. TC-AUTH-01) rolls up the automated sub-cases that start with its ID
(TC-AUTH-01.1, TC-AUTH-01.2, ...).

    python tools/fill_team_templates.py
"""
import csv
import io
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_reports import ROOT, aggregate, load, status_label  # noqa: E402

TEMPLATES = ROOT / "team_templates"
TARGET = ROOT.parent / "testing"
RESULTS = ROOT / "results"
TESTER = "Manasvi G V"
REPORTED = "2026-10-20"
AUTOMATION = "Testing_PES1UG24AM156_ManasviGV"
SCRIPT_ERRORS = {}
PRIORITY = {"P1": "High", "P2": "High", "P3": "Medium", "P4": "Low"}

# Where the reference build differs from what a team test case anticipated.
OBSERVATIONS = {
    "TC-AUTH-02": "No separate user-management screen exists in the reference build; admin-only functions "
                  "(student creation, thresholds, audit log) were used for the faculty-to-admin check.",
    "TC-REP-01": "Reports are per student in CSV or JSON. PDF output and class-level reports (TD-11) are not "
                 "implemented; requesting format 'pdf' is rejected with HTTP 400. Report formats are an open "
                 "issue in SAD 4.6.1.",
    "TC-PRED-01": "No trained ML model: prediction uses a linear SGPA trend (see predictive_analytics_evaluation_report.md).",
    "TC-UX-01": "Automated checks used Python (labels, landmarks, tab order, WCAG contrast formula) instead of "
                "axe/WAVE. The manual keyboard/screen-reader checklist is still open.",
}


def parent(tc_id):
    return tc_id.rsplit(".", 1)[0]


def rollup(cases):
    groups = {}
    for c in cases.values():
        groups.setdefault(parent(c["tc_id"]), []).append(c)
    out = {}
    for pid, subs in groups.items():
        fails = [s for s in subs if s["status"] == "Fail"]
        limited = [s for s in subs if s["limitation"]]
        status = "Fail" if fails else "Pass"
        out[pid] = {
            "subs": subs, "status": status, "limited": bool(limited) and not fails,
            "label": status + (" (with limitation)" if limited and not fails else ""),
            "executions": sum(len(s["variants"]) for s in subs),
            "passed": sum(s["passed"] for s in subs),
            "date": max(s["executed_at"] for s in subs)[:10],
            "limitations": list(dict.fromkeys(s["limitation"] for s in limited)),
            "failures": fails,
        }
    return out


def observation(group, defects_by_tc, verbose=True):
    subs = group["subs"]
    ids = f"{subs[0]['tc_id']}..{subs[-1]['tc_id'].rsplit('-', 1)[1]}" if len(subs) > 1 else subs[0]["tc_id"]
    text = f"{len(subs)} automated sub-case{'s' if len(subs) > 1 else ''} ({ids}); {group['passed']}/{group['executions']} executions passed."
    if group["failures"]:
        parts = []
        for f in group["failures"]:
            if f["tc_id"] in defects_by_tc:
                d = defects_by_tc[f["tc_id"]]
                parts.append(f"{f['tc_id']} - product defect {d['id']}: {d['actual']}")
            else:
                t = SCRIPT_ERRORS.get(f["tc_id"], {})
                parts.append(f"{f['tc_id']} - test script error {t.get('id', '')}: {t.get('description', '')}")
        text += " Failed: " + "; ".join(parts)
    elif verbose:
        text += " Key results: " + " | ".join(clip(s["actual"][0]) for s in subs[:3] if s["actual"])
    return text


def clip(text, limit=220):
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def main():
    final_run = load(RESULTS / "execution_results.json")
    cycle1_run = load(RESULTS / "cycle1" / "execution_results.json")
    if not final_run:
        raise SystemExit("Run the tests first (python tools/run_all.py)")
    final, cycle1 = rollup(aggregate(final_run)), rollup(aggregate(cycle1_run)) if cycle1_run else {}
    defects = load(ROOT / "docs" / "defects.json")
    defects_by_tc = {d["test_case"]: d for d in defects["execution_defects"]}
    SCRIPT_ERRORS.update({t["test_case"]: t for t in defects["test_script_corrections"]})
    defect_for_parent = {}
    for d in defects["execution_defects"]:
        defect_for_parent.setdefault(parent(d["test_case"]), []).append(d["id"])
    env = final_run["environment"]
    env_text = (f"APAS reference build on {env['platform'].split('-')[0]}, Python {env['python']}, "
                f"Flask {env['flask']}, {env['database']}, HTTPS (local)")
    perf, rel = load(RESULTS / "performance_results.json", {}), load(RESULTS / "reliability_results.json", {})
    tls, pred = load(RESULTS / "tls_results.json", {}), load(RESULTS / "prediction_evaluation.json", {})

    if TARGET.exists():
        for f in TEMPLATES.rglob("*"):
            if f.is_file():
                (TARGET / f.relative_to(TEMPLATES)).unlink(missing_ok=True)
    shutil.copytree(TEMPLATES, TARGET, dirs_exist_ok=True)

    # ---- test-cases/test_cases.md: fill Actual result and Status ----------
    text = (TEMPLATES / "test-cases" / "test_cases.md").read_text()

    def fill_case(match):
        block, pid = match.group(0), match.group(1)
        g = final.get(pid)
        if not g:
            return block
        actual = observation(g, defects_by_tc)
        if pid in OBSERVATIONS:
            actual += " Note: " + OBSERVATIONS[pid]
        if g["limitations"]:
            actual += " Limitation: " + " ".join(g["limitations"])
        c1 = cycle1.get(pid)
        if c1 and c1["status"] == "Fail":
            actual += (f" Cycle 1 result was Fail ({', '.join(defect_for_parent.get(pid, ['test script error']))}); "
                       "retested in cycle 2.")
        block = re.sub(r"- \*\*Actual result:\*\*.*", lambda _: f"- **Actual result:** {actual}", block)
        block = re.sub(r"- \*\*Status:\*\*.*", lambda _: f"- **Status:** {g['label']} (executed {g['date']}, "
                                                         f"tester {TESTER})", block)
        return block

    text = re.sub(r"## (TC-[A-Z]+-\d+) - .*?(?=\n## |\Z)", fill_case, text, flags=re.S)
    text = text.replace("Status values: Pass, Fail, Blocked, Not Executed.",
                        "Status values: Pass, Fail, Blocked, Not Executed.\n\n"
                        f"Executed by {TESTER} (Test Engineer). Each test case was automated as several sub-cases; "
                        f"scripts, data and raw evidence are in `../{AUTOMATION}/`. Detailed sub-case "
                        f"specifications: `../{AUTOMATION}/deliverables/01_Test_Case_Specification.md`.")
    write(TARGET / "test-cases" / "test_cases.md", text)

    # ---- test-execution/test_execution_log.csv ---------------------------
    template_rows = list(csv.reader((TEMPLATES / "test-execution" / "test_execution_log.csv").open()))
    header, order = template_rows[0], [r[1] for r in template_rows[1:]]
    rows, run = [], 1
    for label, groups in (("cycle 1", cycle1), ("cycle 2 (retest + regression)", final)):
        for pid in order:
            g = groups.get(pid)
            if not g:
                continue
            ids = defect_for_parent.get(pid, []) if g["status"] == "Fail" or label.startswith("cycle 2") and \
                cycle1.get(pid, {}).get("status") == "Fail" else []
            ids += [SCRIPT_ERRORS[f["tc_id"]]["id"] + " (test script)" for f in g["failures"]
                    if f["tc_id"] in SCRIPT_ERRORS]
            rows.append([run, pid, f"APAS v1.0 reference build - {label}", env_text, g["date"], TESTER,
                         g["label"], observation(g, defects_by_tc, verbose=False), "; ".join(ids)])
            run += 1
    write(TARGET / "test-execution" / "test_execution_log.csv", csv_text(header, rows))

    # ---- test-execution/defect_log.csv -----------------------------------
    header = next(csv.reader((TEMPLATES / "test-execution" / "defect_log.csv").open()))
    rows = []
    for d in defects["execution_defects"]:
        rows.append([d["id"], d["test_case"], "; ".join(d["requirements"]), d["title"], d["description"],
                     " ".join(f"{i}. {s}" for i, s in enumerate(d["steps"], 1)), d["expected"], d["actual"],
                     d["severity"], PRIORITY[d["priority"]], d["status"], d["assigned_to"].split(" (")[0],
                     f"{AUTOMATION}/{d['evidence'].split(' (')[0]}", TESTER, REPORTED])
    for d in defects["review_defects"]:
        rows.append([d["id"], "Document review", d["document"], d["title"], d["description"],
                     f"Review {d['document']}", d["recommendation"], d["impact"], d["severity"],
                     PRIORITY[d["priority"]], d["status"], d["assigned_to"].split(" (")[0].split(" /")[0],
                     f"{AUTOMATION}/deliverables/03_Defect_Report.md", TESTER, REPORTED])
    write(TARGET / "test-execution" / "defect_log.csv", csv_text(header, rows))

    # ---- traceability/RTM.md: add execution columns ----------------------
    out = []
    for line in (TEMPLATES / "traceability" / "RTM.md").read_text().splitlines():
        m = re.match(r"\| (APAS-[A-Z]+-\d+) \|.*\| (TC-[A-Z]+-\d+) \|$", line)
        if line.startswith("| Requirement ID"):
            line += " Executed sub-cases | Execution status | Defects |"
        elif line.startswith("|---"):
            line += "---|---|---|"
        elif m:
            req, pid = m.groups()
            subs = [c for c in aggregate(final_run).values() if req in c["requirements"]]
            ok = all(s["status"] == "Pass" for s in subs)
            lim = any(s["limitation"] for s in subs)
            status = ("Pass" if ok else "Fail") + (" (with limitation)" if ok and lim else "")
            defect_ids = sorted({d["id"] for d in defects["execution_defects"] if req in d["requirements"]})
            line += (f" {len(subs)} ({sum(s['status'] == 'Pass' for s in subs)} passed) | {status} | "
                     f"{', '.join(f'{d} (closed)' for d in defect_ids) or '-'} |")
        out.append(line)
    out.append(f"\nExecution status added by {TESTER} from the cycle 2 run ({final_run['started_at'][:10]}). "
               "Sub-case counts include supporting cases mapped to the requirement (e.g. TC-SEC-05.4 also covers "
               "APAS-NF-003). Review note DOC-005: APAS-NF-003 is also exercised by TC-SEC-02 (role checks).")
    write(TARGET / "traceability" / "RTM.md", "\n".join(out) + "\n")

    # ---- reports/performance_security_results.md -------------------------
    sec = {k: v for k, v in final.items() if k.startswith("TC-SEC")}
    o, m = perf.get("overall", {}), perf.get("mixed_read_write", {})
    measured = {
        "TC-PERF-01": ("Python load script (requests, 50 threads) instead of JMeter",
                       f"p95 {o.get('p95_s')} s overall (worst dashboard {max(v['p95_s'] for v in perf.get('per_dashboard', {}).values()) if perf.get('per_dashboard') else '-'} s); "
                       f"with concurrent grade writes p95 {m.get('dashboard', {}).get('p95_s')} s", final["TC-PERF-01"]["label"]),
        "TC-REL-01": ("Health-probe soak test with fault injection",
                      f"{rel.get('availability_pct', 0):.2f}% over {rel.get('window_s')} s (monthly figure not yet measurable)",
                      final["TC-REL-01"]["label"]),
        "TC-SEC-03": ("Python ssl handshakes + HTTP redirect test (testssl/SSL Labs on deployment still to do)",
                      f"TLS 1.0/1.1 refused, TLS 1.2/1.3 accepted; HTTP GET -> 301, HTTP POST -> 403; HSTS set",
                      final["TC-SEC-03"]["label"]),
        "TC-SEC-04": ("DB inspection (automated)", "PBKDF2-SHA256, 600 000 iterations, 16-char salt; no plaintext in DB, "
                                                   "API responses or logs", final["TC-SEC-04"]["label"]),
        "TC-SEC-05": ("Audit log review (automated)", "Login success/failure, record changes and denied access logged "
                                                      "with user, event type and UTC timestamp; no secrets logged",
                      final["TC-SEC-05"]["label"]),
        "TC-AUD-01": ("Audit log review (automated, back-dated entries)", "12-month minimum enforced (11m29d kept, "
                                                                          "older purged; config < 12 raised to 12); "
                                                                          "UPDATE blocked", final["TC-AUD-01"]["label"]),
        "TC-UX-01": ("Python HTML/contrast checks instead of axe/WAVE", "0 structural issues on 4 pages; all text "
                                                                       "pairs >= 4.5:1, UI pairs >= 3:1; manual "
                                                                       "checklist pending", final["TC-UX-01"]["label"]),
    }
    out = []
    for line in (TEMPLATES / "reports" / "performance_security_results.md").read_text().splitlines():
        m2 = re.match(r"\| (TC-[A-Z]+-\d+) \| (.*?) \| (.*?) \| (.*?) \|  \|  \|$", line)
        if m2 and m2.group(1) in measured:
            tool, value, verdict = measured[m2.group(1)]
            line = f"| {m2.group(1)} | {m2.group(2)} | {tool} | {m2.group(4)} | {value} | {verdict} |"
        out.append(line)
    out += ["", "Additional security results:", ""]
    out += [f"- **{k}**: {v['label']} ({v['passed']}/{v['executions']} executions)" for k, v in sec.items()]
    out += ["", f"Raw data: `../{AUTOMATION}/results/` (performance_results.json, tls_results.json, "
                "reliability_results.json). Cycle 1 measured admin dashboard p95 4.19 s at 10 users (DEF-002, fixed)."]
    write(TARGET / "reports" / "performance_security_results.md", "\n".join(out) + "\n")

    # ---- reports/predictive_analytics_evaluation_report.md ----------------
    if pred:
        cm = pred["confusion"]
        values = {
            "Model used": "Least-squares linear trend on semester SGPA, extrapolated one semester, clipped to 0-10 "
                          "(no trained ML model)",
            "Dataset (source, size, synthetic?)": f"Synthetic, {pred['cohort_size']} students x 3 semesters "
                                                  "(apas.seed, seed 2026)",
            "Train/test split": "Time-based hold-out: semesters 1-2 as history, semester 3 as the test target "
                                "(no model training, so no 80/20 split)",
            "Input features": "Semester SGPA history (attendance is used for the risk level, not the SGPA forecast)",
            "Evaluation method": "MAE/RMSE on predicted SGPA; at-risk = SGPA < 6.0: precision, recall, F1, "
                                 "accuracy, confusion matrix",
            "Accuracy": f"{pred['accuracy']} (at-risk classification); SGPA MAE {pred['mae_sgpa']}, RMSE {pred['rmse_sgpa']}",
            "Precision (at-risk)": str(pred["precision"]), "Recall (at-risk)": str(pred["recall"]),
            "F1": str(pred.get("f1", "-")),
            "Observed results": f"{pred['predictions_produced']}/{pred['cohort_size']} predictions produced; "
                                f"confusion TP {cm['tp']}, FP {cm['fp']}, FN {cm['fn']}, TN {cm['tn']}; "
                                f"bias {pred['mean_error_sgpa']}. Students with < 2 semesters get 'insufficient data'.",
        }
        out = []
        for line in (TEMPLATES / "reports" / "predictive_analytics_evaluation_report.md").read_text().splitlines():
            m3 = re.match(r"\| (.*?) \| (.*?) ?\|$", line)
            if m3 and m3.group(1) in values:
                line = f"| {m3.group(1)} | {values[m3.group(1)]} |"
            elif m3 and m3.group(1) == "Limitations":
                line = (f"| Limitations | {m3.group(2).strip()}; synthetic data only; 2-point linear extrapolation |")
            elif m3 and m3.group(1) == "Acceptance threshold":
                line = f"| Acceptance threshold | {m3.group(2).strip()} (raised as review defect DOC-004) |"
            out.append(line)
        write(TARGET / "reports" / "predictive_analytics_evaluation_report.md", "\n".join(out) + "\n")

    # ---- test-data/test_data.md: show what each data set became ----------
    actual_data = {
        "TD-01": "admin, fac.rao, fac.iyer, 5 students, inactive.user; unknown 'ghost.user'",
        "TD-02": "6 profiles PES1UG24AM001-006; invalid IDs/semesters/email; duplicate PES1UG24AM001",
        "TD-03": "Per assessment max 50 (ISA + ESA = 100): 0, 0.5, 25, 49.5, 50",
        "TD-04": "-1, -0.01, 50.01, 51, 100, 1000, '45', '', null, true, 'abc'",
        "TD-05": "19/20=95%, 12/20=60%, 15/20=75%, 4/4 absent=0%, 4/4 present=100%; no records -> null",
        "TD-06": "Hand-calculated CGPA/overall % for 5 students (e.g. Aarav CGPA 9.39, 86.91%)",
        "TD-07": "3 semesters x 3 subjects: Aarav improving, Kabir declining",
        "TD-08": "Thresholds used: attendance < 75%, overall < 50%, any subject < 40% (fail). Rohan exactly 75%/50%",
        "TD-09": "300 synthetic students x 3 semesters (seed 2026)",
        "TD-10": "Ishita and Rohan (1 semester), Meera (none)",
        "TD-11": "Per-student CSV and JSON; invalid format 'pdf'; unknown student",
        "TD-12": "50 concurrent users, 300 requests, 306 students (no ramp-up)",
        "TD-13": "Back-dated entries at 30 days, 11m29d, 12m2d, 13 and 24 months",
    }
    out = []
    for line in (TEMPLATES / "test-data" / "test_data.md").read_text().splitlines():
        if line.startswith("| Data ID"):
            line += " Actual data used in execution |"
        elif line.startswith("|---"):
            line += "---|"
        else:
            m4 = re.match(r"\| (TD-\d+) \|", line)
            if m4:
                line += f" {actual_data.get(m4.group(1), '-')} |"
        out.append(line)
    out.append(f"\nActual data file: `../{AUTOMATION}/test_data/apas_test_data.json`. Usernames and IDs differ from the "
               "placeholders above. Each mapping is listed in the last column.")
    write(TARGET / "test-data" / "test_data.md", "\n".join(out) + "\n")

    # ---- README.md --------------------------------------------------------
    readme = (TEMPLATES / "README.md").read_text().replace(
        "Results fields are blank until tests are executed.",
        f"Results were filled in by {TESTER} (Test Engineer) from the automated runs on "
        f"{final_run['started_at'][:10]}: {sum(g['status'] == 'Pass' for g in final.values())}/{len(final)} test "
        f"cases pass after retest; defects in test-execution/defect_log.csv. The test summary report "
        f"(reports/test_summary_report.md) is left for the QA Lead.\n\n"
        f"Automation, the APAS reference build and raw evidence: `../{AUTOMATION}/` "
        f"(run `python3 tools/run_all.py` there to re-execute and refill these files).")
    write(TARGET / "README.md", readme)

    print(f"Filled {TARGET.relative_to(ROOT.parent.parent)}: {len(final)} team test cases, "
          f"{len(defects['execution_defects']) + len(defects['review_defects'])} defects logged")


if __name__ == "__main__":
    main()
