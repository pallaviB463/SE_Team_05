# APAS Testing: Manasvi G V (PES1UG24AM156), Test Engineer

Work for the **Test Engineer** role in the APAS Software Test Plan (section 9):

> Design and execute test cases, verify functional and non-functional requirements, record test results, and report defects.

The repository contained only the SRS, SAD and STP, with no implementation to test. So this folder also has
a **reference build of APAS** (`apas/`), written from the SAD: a layered architecture with the proposed API endpoints from SAD 4.3.1.
That build is the system under test.

## Deliverables (`deliverables/`)

| File | STP deliverable |
|---|---|
| `PES1UG24AM156_ManasviGV_Test_Deliverables.docx` | All of the below in one Word document for submission |
| `01_Test_Case_Specification.md` | 2. Test Cases (ID, requirement, objective, preconditions, data, steps, expected) |
| `02_Test_Execution_Log.md` | 5. Test Execution Logs (cycle 1 and cycle 2, actual results, pass/fail, dates) |
| `03_Defect_Report.md` | 6. Defect Reports (execution defects, SRS/STP review defects, test script corrections) |
| `04_RTM_Execution_Status.md` | 7. RTM updated with execution status |
| `05_NonFunctional_Security_Predictive_Results.md` | 8. Performance and Security Results; 9. Predictive Analytics Evaluation |

Supporting items: `tests/` (3. Test Scripts), `test_data/` (4. Test Data), `results/` (raw JSON evidence for each
cycle), `docs/defects.json` (defect log source), `docs/Manual_Accessibility_Checklist.md` (manual WCAG checks still to do).

## Working with the QA Lead's templates (branch `neha-testing`)

Neha's `testing/` folder from the `neha-testing` branch has been copied into `../testing/` (no branch switch, nothing
committed). `tools/fill_team_templates.py` fills her templates from the results: test case actual results and
status, the execution log (both cycles), the defect log, RTM execution columns, performance/security results, the
predictive evaluation and a test-data mapping. Her 24 test cases roll up the automated sub-cases (TC-AUTH-01 =
TC-AUTH-01.1 ... 01.8). Unedited copies of her templates are kept in `team_templates/`. Her test summary report
is left for her to write.

The tests follow her test data plan where it fixes a value: 50 concurrent users (TD-12), grade 1000 and blank
(TD-04), 0% and 100% attendance (TD-05).

## Results at a glance

- 88 test cases (196 executions including data-driven variants) cover all 25 SRS requirements.
- Cycle 1: 4 failures. Two were product defects (DEF-001 Critical: HTTPS bypass through a spoofed header; DEF-002 Major: admin dashboard
  p95 of 4.19 s). The other two were test script errors.
- Cycle 2 (retest and full regression, at 50 concurrent users): 88/88 pass. Both defects are fixed and closed.
- Nine review defects were raised against the SRS/STP (e.g. undefined thresholds, untraceable assignment tracking).
- Limitations are documented: monthly availability, TLS on the real deployment, assumed load profile, and synthetic prediction data.

## How to run

Requires Python 3.10+ with `flask`, `pytest`, `requests`, `cryptography` and `python-docx`.

```bash
python3 tools/run_all.py
```

That runs every test, rebuilds `deliverables/` and refills `../testing/`. To run only one suite:

```bash
python3 -m pytest tests/test_security.py -v
```

To try the application in a browser (accounts and passwords are in `test_data/apas_test_data.json`):

```bash
python3 run_app.py
```

Then open http://127.0.0.1:5000. Use `--https` for a self-signed HTTPS instance.

## Test suite map

| Script | Test cases | Requirements |
|---|---|---|
| `tests/test_auth.py` | TC-AUTH-01 to 03 | APAS-F-001 to F-003 |
| `tests/test_records.py` | TC-REC-01 to 03 | APAS-F-004 to F-006 |
| `tests/test_analysis.py` | TC-ANA-01 to 03 | APAS-F-007 to F-009 |
| `tests/test_dashboard_reports.py` | TC-VIS-01/02, TC-REP-01 | APAS-F-010 to F-012 |
| `tests/test_prediction.py` | TC-PRED-01 to 03 | APAS-F-013 to F-015 |
| `tests/test_security.py` | TC-SEC-01 to 05 | APAS-SR-001 to SR-005, NF-003 |
| `tests/test_nonfunctional.py` | TC-PERF-01, TC-REL-01, TC-AUD-01, TC-UX-01 | APAS-NF-001, 002, 004, 005 |
