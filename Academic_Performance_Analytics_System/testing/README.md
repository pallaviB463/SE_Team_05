# APAS - Testing (QA)

Owner: Neha Rastogi (QA Lead / Test Coordinator). Team 05, Academic Performance Analytics System v1.0.

| Folder | Contents |
|---|---|
| test-plan/ | Software Test Plan (PDF) |
| test-cases/ | 24 test cases (TC-AUTH, REC, ANA, VIS, REP, PRED, PERF, REL, SEC, AUD, UX) |
| test-data/ | Synthetic test data sets |
| test-execution/ | Execution log, defect log (CSV), defect report template |
| traceability/ | Requirements Traceability Matrix |
| reports/ | Test summary, predictive analytics evaluation, performance & security results |

Results were filled in by Manasvi G V (Test Engineer) from the automated runs on 2026-10-20: 24/24 test cases pass after retest; defects in test-execution/defect_log.csv. The test summary report (reports/test_summary_report.md) is left for the QA Lead.

Automation, the APAS reference build and raw evidence: `../Testing_PES1UG24AM156_ManasviGV/` (run `python3 tools/run_all.py` there to re-execute and refill these files).
