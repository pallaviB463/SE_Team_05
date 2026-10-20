# Defect Report

**Project:** Academic Performance Analytics System (APAS) v1.0  
**Prepared by:** Manasvi G V (PES1UG24AM156), Test Engineer, Team 05  
**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  
**Final execution run:** 2026-10-20T12:24:34+05:30 to 2026-10-20T12:26:10+05:30  
**Generated:** 20-10-2026 12:26


## Summary

| Category | Total | Critical | Major | Minor | Trivial | Open | Closed |
|---|---|---|---|---|---|---|---|
| Execution defects (software) | 2 | 1 | 1 | 0 | 0 | 0 | 2 |
| Review defects (SRS / STP) | 9 | 0 | 2 | 5 | 2 | 9 | 0 |

Severity: Critical = security breach or data loss; Major = requirement not met; Minor = workaround exists or ambiguity; Trivial = cosmetic. Priority P1 (fix immediately) to P4 (fix when convenient).


## Execution defects


### DEF-001: HTTPS enforcement bypassed by a client-supplied X-Forwarded-Proto header

| Field | Detail |
|---|---|
| Test case / Requirement | TC-SEC-03.3 / APAS-SR-003 |
| Module | Security / API Gateway (apas/__init__.py require_https) |
| Severity / Priority | Critical / P1 |
| Environment | APAS reference build, production configuration (ENFORCE_HTTPS=True), Flask test client over plain HTTP |
| Description | The HTTPS check treated any request carrying the header X-Forwarded-Proto: https as secure, even when no reverse proxy is deployed. A client on plain HTTP could therefore submit credentials and receive a session token over an unencrypted connection. |
| Steps to reproduce | 1. Start APAS with the production configuration (no reverse proxy).<br>2. Send POST http://<host>/api/auth/login with a valid username/password and the header X-Forwarded-Proto: https.<br>3. Send GET http://<host>/dashboard with the same header. |
| Expected result | POST rejected with HTTP 403 "HTTPS is required"; GET redirected to https:// with HTTP 301. |
| Actual result | POST returned HTTP 200 with a session token over plain HTTP; GET was served (HTTP 302 to /login) instead of being redirected to HTTPS. |
| Evidence | results/cycle1/execution_results.json (TC-SEC-03.3: 'spoofed GET -> HTTP 302; spoofed POST login -> HTTP 200') |
| Root cause | require_https() trusted request.headers['X-Forwarded-Proto'] unconditionally. |
| Resolution | The header is now honoured only when TRUST_PROXY=True, through werkzeug ProxyFix (x_proto=1). Otherwise only the real connection scheme (request.is_secure) is used. |
| Found / Fixed | Cycle 1 / Cycle 2 |
| Status history | New -> Assigned -> In Progress -> Fixed -> Retest -> Closed |
| Current status | Closed |
| Reported by / Assigned to | Manasvi G V (Test Engineer) / Madhuri Ravikumar (Developer) |
| Retest | TC-SEC-03.3 passed in cycle 2 (GET 301, POST 403). Regression: TC-SEC-03.1/03.2 and all suites passed. |

### DEF-002: Administrator overview dashboard exceeds the 3-second response target under concurrent load

| Field | Detail |
|---|---|
| Test case / Requirement | TC-PERF-01.1 / APAS-NF-001 |
| Module | Reporting and Dashboard Service / Authentication Service (apas/api.py student_overview, apas/security.py current_user) |
| Severity / Priority | Major / P2 |
| Environment | APAS on HTTPS (werkzeug threaded server), SQLite, 306 students (~42 000 grade/attendance rows), 10 concurrent clients, MacBook (darwin) |
| Description | With 10 concurrent users, the 95th-percentile response time of the administrator overview dashboard (GET /api/dashboard as admin) was 4.19 s, with a maximum of 7.10 s. Overall p95 across all dashboards was 2.74 s, but one dashboard type broke the APAS-NF-001 target. |
| Steps to reproduce | 1. Seed the test data plus 300 synthetic students (apas.seed.add_synthetic_students).<br>2. Run APAS over HTTPS and log in as admin, fac.rao and aarav.<br>3. Send 300 dashboard requests (6 dashboard types, 50 each) from 10 concurrent threads.<br>4. Compute the 95th percentile per dashboard type. |
| Expected result | 95th percentile <= 3.0 s for every dashboard type. |
| Actual result | admin API overview p95 = 4.189 s (max 7.102 s); faculty API overview p95 = 2.994 s (close to the limit). |
| Evidence | results/cycle1/performance_results.json |
| Root cause | (1) Every overview request re-analysed all 306 students, even when nothing had changed. (2) Every authenticated request wrote sessions.last_seen, so concurrent read-only requests queued for SQLite's single write lock. |
| Resolution | Overview results are cached per database and invalidated through a data_version counter maintained by triggers on students/subjects/grades/attendance/config. The session last_seen timestamp is written at most once per 60 s. |
| Found / Fixed | Cycle 1 / Cycle 2 |
| Status history | New -> Assigned -> In Progress -> Fixed -> Retest -> Closed |
| Current status | Closed |
| Reported by / Assigned to | Manasvi G V (Test Engineer) / Madhuri Ravikumar (Developer) |
| Retest | Cycle 2 retest at the team load profile TD-12 (50 concurrent users, stricter than cycle 1): TC-PERF-01.1 overall p95 0.46 s (max 0.54 s); TC-PERF-01.2 with concurrent grade writes p95 0.90 s. New regression test TC-VIS-01.5 confirms the cache is invalidated immediately after a grade change. |

## Review defects (static testing of SRS v1.0 and STP v1.0)

| ID | Title | Document | Sev. | Pri. | Description | Impact on testing | Recommendation | Status / Owner |
|---|---|---|---|---|---|---|---|---|
| DOC-001 | Risk and performance thresholds are not specified | SRS v1.0, APAS-F-009 and APAS-F-014 | Major | P2 | F-009 refers to 'configured thresholds' and F-014 to 'predefined risk criteria' without numeric values, so expected results cannot be derived from the SRS. | Testers had to assume values: attendance < 75%, overall performance < 50%, failed subject < 40%; high risk = predicted SGPA < 5.0 or attendance < 65%; medium risk = predicted SGPA < 6.0 or attendance < 75%. | Add default threshold values and state whether comparisons are strict (<) or inclusive (<=). Boundary tests TC-ANA-03.1 / TC-PRED-02.1 assume strict '<'. | New / Neha Rastogi (QA Lead) / requirement owners |
| DOC-002 | Assignment submission tracking has no functional requirement or test case | SRS v1.0 sections 1.2 and 2.2 vs section 4 / RTM | Major | P2 | Scope (1.2) and Major Product Functions (2.2) include 'Assignment submission and marks tracking', but no requirement from APAS-F-001 to F-015 and no RTM row covers it. | This function is untraceable and untested. The current build models only ISA/ESA assessments. | Either add a functional requirement (e.g. APAS-F-016) with acceptance criteria and a test case, or remove the function from the scope. | New / Pallavi B (Project Lead) |
| DOC-003 | 'Normal operating conditions' for the response-time target are not quantified | SRS v1.0 APAS-NF-001, STP 5.2 | Minor | P3 | The 3-second target has no defined concurrent-user count, data volume or network conditions. | Cycle 1 assumed 10 concurrent users. Cycle 2 uses the team test-data profile TD-12 (50 concurrent users, 306 students), which is still not an SRS-approved figure. | Define the load profile (e.g. N concurrent users, M students, request mix) in the SRS or STP. | New / Neha Rastogi (QA Lead) |
| DOC-004 | No acceptance criterion for prediction quality | SRS v1.0 APAS-F-013, section 6; STP 15.1 | Minor | P3 | F-013 requires predictions to be 'generated and displayed' but sets no accuracy or error bound. The STP correctly forbids inventing one. | TC-PRED-01.4 can only report MAE/RMSE/precision/recall, not pass or fail on accuracy. | Agree a target (e.g. MAE <= 0.5 SGPA on historical data) or record that prediction quality is informational only. | New / Pallavi B (Project Lead) |
| DOC-005 | RTM maps two different requirements to the same test case TC-SEC-01 | SRS v1.0 section 8 RTM; STP 13.2 | Minor | P3 | APAS-NF-003 (access restricted by role and permission) and APAS-SR-001 (valid credentials required) both map only to TC-SEC-01. NF-003 is about authorisation, which TC-SEC-02 covers. | Role-based restriction under NF-003 is not traceable to the RBAC test case. | Map APAS-NF-003 to TC-SEC-01 and TC-SEC-02 (as done in the execution RTM). | New / Neha Rastogi (QA Lead) |
| DOC-006 | SRS allows plain HTTP, which contradicts APAS-SR-003 | SRS v1.0 section 3.4 vs APAS-SR-003 | Minor | P3 | Section 3.4 says communication 'shall use HTTP or HTTPS', while SR-003 requires HTTPS with TLS 1.2+ and requires insecure connections to be rejected or redirected. | Ambiguous whether HTTP is acceptable anywhere. | State that HTTP is permitted only in local development environments without real student data. | New / Requirement owners |
| DOC-007 | Session timeout and account-lockout policy are not specified | SRS v1.0 APAS-F-003, APAS-SR-001 | Minor | P3 | The SRS requires secure sessions but does not define an idle timeout or a brute-force lockout policy. | The test build assumes a 30-minute idle timeout and a 15-minute lockout after 5 failed logins (TC-AUTH-03.3, TC-AUTH-01.6). | Add explicit values to the SRS security requirements. | New / Requirement owners |
| DOC-008 | Table text appears cut off in the SRS | SRS v1.0 section 4.1 (APAS-F-003) and 4.4 (APAS-F-012) | Trivial | P4 | Text extracted from the 'Comments / Dependencies' column ends mid-word: 'Requires session mana' (F-003) and 'reporting servic' (F-012). This suggests the table cells overflow the page. | Readability only. | Check visually and widen or rewrap the table columns. | New / Document owner |
| DOC-009 | Inconsistent document metadata | SRS v1.0 revision history; STP v1.0 section 15.3 | Trivial | P4 | The SRS revision history lists '1.0, 18-08-2025, Instructor, SRS with diagrams embedded' (template leftover), while the document is dated 12-10-2026 by Team 05. The STP approval table says 'To be assigned' although section 9 names the QA Lead (Neha Rastogi) and Project Lead (Pallavi B). | Traceability of approvals. | Remove the template row and fill in the approval table with the assigned names. | New / Neha Rastogi (QA Lead) |

## Test script corrections (not product defects)

| ID | Test case | Problem | Correction |
|---|---|---|---|
| TS-001 | All suites (dry run) | First dry run: 169 of 189 tests returned HTTP 301 because the test client did not send requests over https:// (werkzeug ignores environ_base['wsgi.url_scheme']). The application behaved correctly by redirecting plain HTTP. | Added the https_client() fixture, which defaults base_url to https://localhost. The dry run is not counted as an execution cycle. |
| TS-002 | TC-AUD-01.2 | The expected result for an 18-month retention period omitted the 12-months-2-days entry, which is correctly retained because it is younger than 18 months. | Expected result corrected to keep 30d, 11m29d, 12m2d and 13m. |
| TS-003 | TC-AUD-01.3 | After the expected 'append-only' error, the test's own database connection kept an open transaction. The application's next write timed out on the lock and returned HTTP 500. | The test now rolls back after the rejected UPDATE. |
