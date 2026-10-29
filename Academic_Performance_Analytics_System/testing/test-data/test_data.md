# APAS Test Data

Only synthetic / anonymised data is used (STP §6.4). Threshold values are placeholders - align with configured rules.

| Data ID | Category | Description | Sample Values (synthetic) | Used By | Actual data used in execution |
|---|---|---|---|---|---|
| TD-01 | User accounts | One account per role + disabled/unknown user | admin01 / faculty01 / student01 (passwords per test env); invalid: student01 + wrong pwd; blank; unknown_user | TC-AUTH-01..03, TC-SEC-* | admin, fac.rao, fac.iyer, 5 students, inactive.user; unknown 'ghost.user' |
| TD-02 | Student profiles | Valid, incomplete and duplicate profiles | Valid: STU001 Asha R, CSE, Sem 3; Invalid: missing name, duplicate ID STU001 | TC-REC-01 | 6 profiles PES1UG24AM001-006; invalid IDs/semesters/email; duplicate PES1UG24AM001 |
| TD-03 | Grade entries (valid) | Within allowed range | 0, 1, 50, 75.5, 100 (max=100) | TC-REC-02 | Per assessment max 50 (ISA + ESA = 100): 0, 0.5, 25, 49.5, 50 |
| TD-04 | Grade entries (invalid/boundary) | Out of range, type errors | -1, 100.01, 101, 'abc', blank, 1e3; boundary 0 and 100 accepted | TC-REC-02 | -1, -0.01, 50.01, 51, 100, 1000, '45', '', null, true, 'abc' |
| TD-05 | Attendance | Known totals for % checks | 18/20=90%; 0/20=0%; 20/20=100%; 0 classes held (no divide-by-zero) | TC-REC-03 | 19/20=95%, 12/20=60%, 15/20=75%, 4/4 absent=0%, 4/4 present=100%; no records -> null |
| TD-06 | Performance calc set | Known scores with expected overall result | Subject A 80, B 70, C 90 (equal weight) -> expected 80.0 (adjust to configured rules) | TC-ANA-01 | Hand-calculated CGPA/overall % for 5 students (e.g. Aarav CGPA 9.39, 86.91%) |
| TD-07 | Multi-semester records | 3 semesters x 5 subjects per student | Sem1 avg 65, Sem2 avg 72, Sem3 avg 78 (improving trend) | TC-ANA-02, TC-VIS-02 | 3 semesters x 3 subjects: Aarav improving, Kabir declining |
| TD-08 | Threshold cases | Below / at / above thresholds (set per config, e.g. 40% score, 75% attendance) | STU101 score 39 att 80; STU102 score 40 att 74; STU103 score 40 att 75; STU104 score 85 att 95 | TC-ANA-03, TC-PRED-02 | Thresholds used: attendance < 75%, overall < 50%, any subject < 40% (fail). Rohan exactly 75%/50% |
| TD-09 | Historical dataset | Synthetic multi-year records for model train/test | Min. 200 students x 4 semesters; labelled outcome (pass/at-risk); 80/20 train-test split | TC-PRED-01..03 | 300 synthetic students x 3 semesters (seed 2026) |
| TD-10 | Insufficient history | Students with <2 semesters | STU301 Sem 1 only | TC-PRED-01 | Ishita and Rohan (1 semester), Meera (none) |
| TD-11 | Report requests | Types/filters/formats | Class report, semester filter, PDF/CSV; invalid filter: semester=99 | TC-REP-01 | Per-student CSV and JSON; invalid format 'pdf'; unknown student |
| TD-12 | Load profile | Normal load for JMeter | 50 concurrent users, 5-min ramp, 200+ dashboard requests | TC-PERF-01 | 50 concurrent users, 300 requests, 306 students (no ramp-up) |
| TD-13 | Audit data | Record changes with back-dated entries | Grade change by faculty01 at T; entries dated T-13 months, T-11 months (retention check) | TC-AUD-01, TC-SEC-05 | Back-dated entries at 30 days, 11m29d, 12m2d, 13 and 24 months |

Actual data file: `../Testing_PES1UG24AM156_ManasviGV/test_data/apas_test_data.json`. Usernames and IDs differ from the placeholders above. Each mapping is listed in the last column.
