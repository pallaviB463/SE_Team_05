# APAS Test Data

Only synthetic / anonymised data is used (STP §6.4). Threshold values are placeholders - align with configured rules.

| Data ID | Category | Description | Sample Values (synthetic) | Used By |
|---|---|---|---|---|
| TD-01 | User accounts | One account per role + disabled/unknown user | admin01 / faculty01 / student01 (passwords per test env); invalid: student01 + wrong pwd; blank; unknown_user | TC-AUTH-01..03, TC-SEC-* |
| TD-02 | Student profiles | Valid, incomplete and duplicate profiles | Valid: STU001 Asha R, CSE, Sem 3; Invalid: missing name, duplicate ID STU001 | TC-REC-01 |
| TD-03 | Grade entries (valid) | Within allowed range | 0, 1, 50, 75.5, 100 (max=100) | TC-REC-02 |
| TD-04 | Grade entries (invalid/boundary) | Out of range, type errors | -1, 100.01, 101, 'abc', blank, 1e3; boundary 0 and 100 accepted | TC-REC-02 |
| TD-05 | Attendance | Known totals for % checks | 18/20=90%; 0/20=0%; 20/20=100%; 0 classes held (no divide-by-zero) | TC-REC-03 |
| TD-06 | Performance calc set | Known scores with expected overall result | Subject A 80, B 70, C 90 (equal weight) -> expected 80.0 (adjust to configured rules) | TC-ANA-01 |
| TD-07 | Multi-semester records | 3 semesters x 5 subjects per student | Sem1 avg 65, Sem2 avg 72, Sem3 avg 78 (improving trend) | TC-ANA-02, TC-VIS-02 |
| TD-08 | Threshold cases | Below / at / above thresholds (set per config, e.g. 40% score, 75% attendance) | STU101 score 39 att 80; STU102 score 40 att 74; STU103 score 40 att 75; STU104 score 85 att 95 | TC-ANA-03, TC-PRED-02 |
| TD-09 | Historical dataset | Synthetic multi-year records for model train/test | Min. 200 students x 4 semesters; labelled outcome (pass/at-risk); 80/20 train-test split | TC-PRED-01..03 |
| TD-10 | Insufficient history | Students with <2 semesters | STU301 Sem 1 only | TC-PRED-01 |
| TD-11 | Report requests | Types/filters/formats | Class report, semester filter, PDF/CSV; invalid filter: semester=99 | TC-REP-01 |
| TD-12 | Load profile | Normal load for JMeter | 50 concurrent users, 5-min ramp, 200+ dashboard requests | TC-PERF-01 |
| TD-13 | Audit data | Record changes with back-dated entries | Grade change by faculty01 at T; entries dated T-13 months, T-11 months (retention check) | TC-AUD-01, TC-SEC-05 |
