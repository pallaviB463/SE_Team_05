# APAS Test Cases

Derived from SRS v1.0 / STP v1.0. Status values: Pass, Fail, Blocked, Not Executed.

Executed by Manasvi G V (Test Engineer). Each test case was automated as several sub-cases; scripts, data and raw evidence are in `../Testing_PES1UG24AM156_ManasviGV/`. Detailed sub-case specifications: `../Testing_PES1UG24AM156_ManasviGV/deliverables/01_Test_Case_Specification.md`.

| Test Case ID | Requirement(s) | Title | Module | Priority | Type |
|---|---|---|---|---|---|
| TC-AUTH-01 | APAS-F-001 | Valid/invalid login | Authentication | High | Functional |
| TC-AUTH-02 | APAS-F-002 | Role-based access to functions | Authentication | High | Functional |
| TC-AUTH-03 | APAS-F-003 | Secure logout and session termination | Authentication | High | Functional |
| TC-REC-01 | APAS-F-004 | Student profile management | Academic Records | High | Functional |
| TC-REC-02 | APAS-F-005 | Grade entry and update | Academic Records | High | Functional |
| TC-REC-03 | APAS-F-006 | Attendance recording and % calculation | Attendance | High | Functional |
| TC-ANA-01 | APAS-F-007 | Overall performance calculation | Analytics | High | Functional |
| TC-ANA-02 | APAS-F-008 | Subject-wise & semester-wise analysis | Analytics | High | Functional |
| TC-ANA-03 | APAS-F-009 | Low-performance / low-attendance identification | Analytics | High | Functional |
| TC-VIS-01 | APAS-F-010 | Role-appropriate dashboard | Dashboard | High | Functional |
| TC-VIS-02 | APAS-F-011 | Graphical trends (bar/line) | Dashboard | Medium | Functional |
| TC-REP-01 | APAS-F-012 | Report generation and download | Reporting | High | Functional |
| TC-PRED-01 | APAS-F-013 | Performance prediction | Predictive Analytics | High | Functional |
| TC-PRED-02 | APAS-F-014 | At-risk student identification | Predictive Analytics | High | Functional |
| TC-PRED-03 | APAS-F-015 | Insights and recommendations | Predictive Analytics | Medium | Functional |
| TC-PERF-01 | APAS-NF-001 | Dashboard response time | Performance | High | Non-Functional |
| TC-REL-01 | APAS-NF-002 | Monthly availability | Reliability | High | Non-Functional |
| TC-SEC-01 | APAS-NF-003; APAS-SR-001 | Access restriction & authentication required | Security | High | Security |
| TC-SEC-02 | APAS-SR-002 | Role-based access control (security) | Security | High | Security |
| TC-SEC-03 | APAS-SR-003 | HTTPS / TLS 1.2+ | Security | High | Security |
| TC-SEC-04 | APAS-SR-004 | Password hashing | Security | High | Security |
| TC-SEC-05 | APAS-SR-005 | Security event audit logging | Security | High | Security |
| TC-AUD-01 | APAS-NF-004 | Audit log content and 12-month retention | Audit | High | Non-Functional |
| TC-UX-01 | APAS-NF-005 | Accessibility (WCAG 2.1 AA) | Usability | Medium | Non-Functional |


## TC-AUTH-01 - Valid/invalid login
- **Requirement(s):** APAS-F-001
- **Module:** Authentication | **Priority:** High | **Type:** Functional
- **Preconditions:** User accounts exist for all 3 roles
- **Steps:** 1. Open login page 2. Enter valid admin/faculty/student credentials 3. Repeat with wrong password, unknown username, blank fields
- **Expected result:** Valid credentials grant access to role dashboard; invalid/blank credentials rejected with generic error
- **Actual result:** 8 automated sub-cases (TC-AUTH-01.1..01.8); 18/18 executions passed. Key results: admin: login HTTP 200, role=admin, token issued (43 chars); dashboard HTTP 200 | HTTP 401, message='Invalid username or password', no token | HTTP 401, message identical to wrong-password case: 'Invalid username or password'
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-AUTH-02 - Role-based access to functions
- **Requirement(s):** APAS-F-002
- **Module:** Authentication | **Priority:** High | **Type:** Functional
- **Preconditions:** Admin, faculty, student accounts logged in
- **Steps:** 1. As student, try faculty pages (grade entry) via menu and direct URL 2. As faculty, try admin user-management 3. As admin, access admin functions
- **Expected result:** Each role sees/accesses only permitted functions; others return 403/redirect
- **Actual result:** 2 automated sub-cases (TC-AUTH-02.1..02.2); 18/18 executions passed. Key results: admin totals={'faculty': 3, 'students': 6, 'users': 9}; faculty subjects=['AM101', 'AM102', 'AM201', 'AM202', 'AM301', 'AM302']; student sees only PES1UG24AM001 | admin POST /api/students -> HTTP 201 (expected 201) Note: No separate user-management screen exists in the reference build; admin-only functions (student creation, thresholds, audit log) were used for the faculty-to-admin check.
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-AUTH-03 - Secure logout and session termination
- **Requirement(s):** APAS-F-003
- **Module:** Authentication | **Priority:** High | **Type:** Functional
- **Preconditions:** User logged in
- **Steps:** 1. Click Logout 2. Press browser Back 3. Re-open a protected URL 4. Replay old session token (Postman)
- **Expected result:** Session terminated; protected pages require re-login; old token rejected (401)
- **Actual result:** 4 automated sub-cases (TC-AUTH-03.1..03.4); 4/4 executions passed. Key results: before logout 200; logout 200; reuse of token -> HTTP 401 | dashboard 200 (no-store); logout -> 302 /login; dashboard afterwards -> 302 /login | after 31 min idle -> HTTP 401; sessions remaining=0
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-REC-01 - Student profile management
- **Requirement(s):** APAS-F-004
- **Module:** Academic Records | **Priority:** High | **Type:** Functional
- **Preconditions:** Admin logged in
- **Steps:** 1. Create student profile 2. View it 3. Update fields 4. Submit invalid/missing mandatory data 5. Try as student/faculty
- **Expected result:** Profile created/updated and stored correctly; invalid data rejected; non-admin changes denied
- **Actual result:** 4 automated sub-cases (TC-REC-01.1..01.4); 18/18 executions passed. Key results: create HTTP 201; GET returned {id=PES1UG24AM007, name=Neel Kapoor, email=neel.kapoor@apas.test, program=B.Tech CSE (AI & ML), current_semester=1}; DB row present | HTTP 200; name 'Ishita Rao' -> 'Ishita R. Rao', semester 3 -> 4; updated_at changed | id='' -> HTTP 400 {'id': 'is required'}
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-REC-02 - Grade entry and update
- **Requirement(s):** APAS-F-005
- **Module:** Academic Records | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty logged in; student & assessment exist
- **Steps:** 1. Enter valid grade 2. Update it 3. Enter invalid values (negative, >max, text, blank) 4. Boundary values (0, max)
- **Expected result:** Valid grades saved and displayed; invalid rejected with message; boundaries accepted per rules
- **Actual result:** 6 automated sub-cases (TC-REC-02.1..02.6); 22/22 executions passed. Key results: POST ISA/ESA -> 201/201; stored ISA=42, ESA=45; AM301 = 87.0% grade A | upsert -> HTTP 200; PUT -> HTTP 200; final ESA=38.0, rows=1 | score=0 -> HTTP 201, stored 0.0
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-REC-03 - Attendance recording and % calculation
- **Requirement(s):** APAS-F-006
- **Module:** Attendance | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty logged in; classes defined
- **Steps:** 1. Record attendance for known data set (e.g. 18 present of 20) 2. View percentage 3. Test 0 classes, 100%, all absent
- **Expected result:** Percentage matches attendance/total x 100 (90%); edge cases handled without error (no divide-by-zero)
- **Actual result:** 5 automated sub-cases (TC-REC-03.1..03.5); 19/19 executions passed. Key results: {'PES1UG24AM001': '57/60 = 95.0%', 'PES1UG24AM002': '36/60 = 60.0%', 'PES1UG24AM005': '45/60 = 75.0%'} | after 4 entries: 3/4 = 75.0%; correction HTTP 200 -> 4/4 = 100.0% | status='Present' -> HTTP 400 'status must be 'present' or 'absent''
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-ANA-01 - Overall performance calculation
- **Requirement(s):** APAS-F-007
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Grades and assessment scores loaded
- **Steps:** 1. Load student with known scores 2. View overall performance 3. Compare with manual calculation using configured rules
- **Expected result:** System value equals expected value
- **Actual result:** 5 automated sub-cases (TC-ANA-01.1..01.5); 20/20 executions passed. Key results: 100% -> (10, 'S') | PES1UG24AM001: CGPA 9.39 (exp 9.39), overall 86.91% (exp 86.91%) | SGPA 6.45, overall 58.55%
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-ANA-02 - Subject-wise & semester-wise analysis
- **Requirement(s):** APAS-F-008
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Multi-semester, multi-subject data exists
- **Steps:** 1. Open analysis for student 2. Compare subject-wise and semester-wise figures with source data
- **Expected result:** Subject/semester comparisons are accurate and trends correct
- **Actual result:** 3 automated sub-cases (TC-ANA-02.1..02.3); 5/5 executions passed. Key results: PES1UG24AM001: SGPA [9.09, 9.36, 9.73], % [84.55, 86.82, 89.36] | 9 subjects returned; semester 3: {'AM301': (42.0, 'E', 5), 'AM302': (35.0, 'F', 0), 'AM303': (45.0, 'E', 5)} | Aarav [9.09, 9.36, 9.73] (increasing); Kabir [7.36, 6.0, 3.18] (decreasing)
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-ANA-03 - Low-performance / low-attendance identification
- **Requirement(s):** APAS-F-009
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Thresholds configured; students above/below/at threshold
- **Steps:** 1. Run identification 2. Check flagged list vs. expected
- **Expected result:** Students below thresholds flagged; at/above not flagged; boundary student handled per rule
- **Actual result:** 3 automated sub-cases (TC-ANA-03.1..03.3); 7/7 executions passed. Key results: flagged={'PES1UG24AM002': ['Attendance in AM301 is 60.0% (below 75%)', 'Attendance in AM302 is 60.0% (below 75%)', 'Attendance in AM303 is 60.0% (below 75%)'], 'PES1UG24AM003': ['Failed AM302 (35.0%)']}; Rohan (bounda... | thresholds updated (HTTP 200); flagged=['PES1UG24AM003', 'PES1UG24AM004', 'PES1UG24AM005'] | {'min_attendance_pct': 101} -> HTTP 400 'min_attendance_pct must be a number between 0 and 100'
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-VIS-01 - Role-appropriate dashboard
- **Requirement(s):** APAS-F-010
- **Module:** Dashboard | **Priority:** High | **Type:** Functional
- **Preconditions:** All role accounts with data
- **Steps:** 1. Open dashboard as each role 2. Verify grades, attendance %, overall performance 3. Student views other student's data
- **Expected result:** Accurate data for selected/authorized student; unauthorized data not visible
- **Actual result:** 5 automated sub-cases (TC-VIS-01.1..01.5); 5/5 executions passed. Key results: student=PES1UG24AM001 CGPA=9.39 overall=86.91% attendance=95.0%; ?student_id=AM003 still returned PES1UG24AM001 | API CGPA=7.82, attendance=60.0; HTML KPIs={'kpi-cgpa': '7.82', 'kpi-overall': '70.64', 'kpi-attendance': '60.0'} | API students=6, flagged=2, at_risk=2; HTML {'kpi-students': '6', 'kpi-flagged': '2', 'kpi-at-risk': '2'}
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-VIS-02 - Graphical trends (bar/line)
- **Requirement(s):** APAS-F-011
- **Module:** Dashboard | **Priority:** Medium | **Type:** Functional
- **Preconditions:** Multi-semester data exists
- **Steps:** 1. Open trend charts 2. Compare plotted values with stored data 3. Check labels/legends
- **Expected result:** Bar and line charts accurately reflect stored/calculated data
- **Actual result:** 4 automated sub-cases (TC-VIS-02.1..02.4); 4/4 executions passed. Key results: subject bars=[('AM301', '42.0', '67.2'), ('AM302', '35.0', '56.0'), ('AM303', '45.0', '72.0')]; attendance bars=[('AM301', 80.0), ('AM302', 80.0), ('AM303', 80.0)] | points=[('1', '9.09', '54.56'), ('2', '9.36', '50.24'), ('3', '9.73', '44.32')] | AM302 bar value=50.0 height=80.0
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-REP-01 - Report generation and download
- **Requirement(s):** APAS-F-012
- **Module:** Reporting | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty/admin logged in
- **Steps:** 1. Select report type/filters/format 2. Generate 3. Download 4. Compare contents 5. Request as unauthorized user / invalid filters
- **Expected result:** Report generated and downloadable with accurate grades, attendance, summaries; invalid/unauthorized requests rejected
- **Actual result:** 3 automated sub-cases (TC-REP-01.1..01.3); 3/3 executions passed. Key results: HTTP 200 text/csv; attachment; filename="APAS_Report_PES1UG24AM001_2026-10-20.csv"; 9 subject rows; CGPA 9.39; overall 86.91; attendance ['57', '60', '95.0'] | CSV flags='Failed AM302 (35.0%)'; JSON CGPA=5.52 | own/other/missing/bad format -> [200, 403, 404, 400] Note: Reports are per student in CSV or JSON. PDF output and class-level reports (TD-11) are not implemented; requesting format 'pdf' is rejected with HTTP 400. Report formats are an open issue in SAD 4.6.1.
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-PRED-01 - Performance prediction
- **Requirement(s):** APAS-F-013
- **Module:** Predictive Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Trained model; students with sufficient history + students with insufficient history
- **Steps:** 1. Request predictions 2. Check eligible and ineligible students
- **Expected result:** Predictions generated and displayed for eligible students; clear message for insufficient data
- **Actual result:** 4 automated sub-cases (TC-PRED-01.1..01.4); 8/8 executions passed. Key results: PES1UG24AM001: predicted SGPA 10.0 (exp 10.0), trend improving, confidence medium | PES1UG24AM004: status=insufficient_data, message='At least 2 completed semesters are required for a prediction.' | student -> 403; faculty -> 200 Note: No trained ML model: prediction uses a linear SGPA trend (see predictive_analytics_evaluation_report.md). Limitation: Evaluation uses a synthetic cohort; results describe the method's behaviour, not real-world accuracy. No accuracy threshold is asserted because the SRS does not define one (STP 15.1).
- **Status:** Pass (with limitation) (executed 2026-10-20, tester Manasvi G V)

## TC-PRED-02 - At-risk student identification
- **Requirement(s):** APAS-F-014
- **Module:** Predictive Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Risk thresholds configured
- **Steps:** 1. Run risk classification 2. Verify risk list against expected classification on labelled test data
- **Expected result:** Students meeting risk criteria correctly classified and listed
- **Actual result:** 2 automated sub-cases (TC-PRED-02.1..02.2); 2/2 executions passed. Key results: at-risk={'PES1UG24AM002': ('high', ['Attendance 60.0% below 65%']), 'PES1UG24AM003': ('high', ['Predicted SGPA 1.33 below 5', 'SGPA trend is declining'])} | risk list (ordered high->medium) = [('PES1UG24AM003', 'high'), ('PES1UG24AM002', 'medium')]
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-PRED-03 - Insights and recommendations
- **Requirement(s):** APAS-F-015
- **Module:** Predictive Analytics | **Priority:** Medium | **Type:** Functional
- **Preconditions:** Students with known weaknesses/risk factors
- **Steps:** 1. Open insights for weak-subject, low-attendance and healthy students
- **Expected result:** Recommendations relevant to the identified weakness/risk factor
- **Actual result:** 3 automated sub-cases (TC-PRED-03.1..03.3); 4/4 executions passed. Key results: 5 recommendations: [('academic', 'AM301'), ('academic', 'AM303'), ('critical', 'AM302'), ('risk', ''), ('trend', '')] | PES1UG24AM002: ['Attendance in Design and Analysis of Algorithms is 60.0%, below the required 75%. Attend classes regularly.', 'Attendance in Database Management Systems is 60.0%, below the required 75%. Attend classe... | own -> 200; other student -> 403
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-PERF-01 - Dashboard response time
- **Requirement(s):** APAS-NF-001
- **Module:** Performance | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Normal-load dataset; JMeter configured
- **Steps:** 1. Simulate normal concurrent load 2. Request dashboard repeatedly (e.g. 200+ requests) 3. Compute 95th percentile
- **Expected result:** 95th percentile response time <= 3 seconds
- **Actual result:** 2 automated sub-cases (TC-PERF-01.1..01.2); 2/2 executions passed. Key results: 300 requests @50 concurrent: p50 0.292 s, p95 0.475 s, max 0.544 s, 100.0% within 3 s; slowest p95 = 0.508 s | 270 dashboard requests + 30 grade writes @50 concurrent: dashboard p50 0.653 s, p95 0.795 s, max 0.942 s Limitation: 'Normal operating conditions' are not quantified in the SRS; load profile taken from team test data TD-12 (50 concurrent users), cohort of 306 students, single developer laptop. Repeat on the deployment infrastructure. Same load assumptions as TC-PERF-01.1. Write rate (1 grade update per 10 requests) is an assumption representing faculty entering marks while others view dashboards. Cycle 1 result was Fail (DEF-002); retested in cycle 2.
- **Status:** Pass (with limitation) (executed 2026-10-20, tester Manasvi G V)

## TC-REL-01 - Monthly availability
- **Requirement(s):** APAS-NF-002
- **Module:** Reliability | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Uptime monitoring in place
- **Steps:** 1. Collect monthly uptime log excl. scheduled maintenance 2. Compute availability
- **Expected result:** Availability >= 99%
- **Actual result:** 2 automated sub-cases (TC-REL-01.1..01.2); 2/2 executions passed. Key results: 400/400 probes OK = 100.00% over 2.8 s; fault responses [400, 401, 404, 405], 5xx/dropped = 0 | failure -> HTTP 500 {'error': 'An unexpected error occurred', 'status': 500}; health afterwards HTTP 200 Limitation: Monthly availability (>= 99%) can only be confirmed by monitoring a deployed instance for a full calendar month (tools/availability_monitor.py). This run covers a short soak test with fault injection.
- **Status:** Pass (with limitation) (executed 2026-10-20, tester Manasvi G V)

## TC-SEC-01 - Access restriction & authentication required
- **Requirement(s):** APAS-NF-003; APAS-SR-001
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Test accounts; unauthenticated client
- **Steps:** 1. Access protected URLs/API without login 2. Login with invalid credentials 3. Access another user's records by changing studentId
- **Expected result:** Unauthenticated/unauthorized attempts rejected (401/403); valid login allows access
- **Actual result:** 2 automated sub-cases (TC-SEC-01.1..01.2); 6/6 executions passed. Key results: 20 protected API operations -> all HTTP 401; /dashboard -> 302 /login | Authorization 'Bearer invalidtoken...' -> HTTP 401
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-SEC-02 - Role-based access control (security)
- **Requirement(s):** APAS-SR-002
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Admin/faculty/student sessions
- **Steps:** 1. Call every API endpoint with each role 2. Attempt UI-hidden functions directly via URL/API
- **Expected result:** Only role-permitted operations succeed; checks enforced server-side
- **Actual result:** 3 automated sub-cases (TC-SEC-02.1..02.3); 9/9 executions passed. Key results: GET /api/students/PES1UG24AM003 as aarav -> HTTP 403, no data leaked | POST -> 403, PUT -> 403; stored score still 20.0 | grade/profile/thresholds/audit -> [403, 403, 403, 403]; profile unchanged ('Aarav Sharma')
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-SEC-03 - HTTPS / TLS 1.2+
- **Requirement(s):** APAS-SR-003
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Deployed test environment
- **Steps:** 1. Open via http:// 2. Run TLS scan (e.g. SSL Labs/nmap/testssl) 3. Attempt TLS 1.0/1.1
- **Expected result:** HTTP redirected/rejected; only TLS 1.2 or higher accepted
- **Actual result:** 3 automated sub-cases (TC-SEC-03.1..03.3); 3/3 executions passed. Key results: HTTP GET -> 301 https://localhost/dashboard; HTTP POST -> 403; HSTS='max-age=31536000; includeSubDomains'; cookie Secure | TLSv1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); TLSv1.1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); T... | spoofed GET -> HTTP 301; spoofed POST login -> HTTP 403 Limitation: Executed against the local test server; the deployed environment's TLS configuration must be re-checked (e.g. SSL Labs / testssl.sh) once a hosting platform is chosen (SAD 4.6.1 open issue 3). Cycle 1 result was Fail (DEF-001); retested in cycle 2.
- **Status:** Pass (with limitation) (executed 2026-10-20, tester Manasvi G V)

## TC-SEC-04 - Password hashing
- **Requirement(s):** APAS-SR-004
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** DB read access in test env
- **Steps:** 1. Create user 2. Inspect stored password field 3. Verify login still works 4. Check logs
- **Expected result:** No plaintext passwords in DB/logs; hash from approved algorithm (e.g. bcrypt/Argon2/PBKDF2); login works
- **Actual result:** 3 automated sub-cases (TC-SEC-04.1..04.3); 3/3 executions passed. Key results: 9 accounts: pbkdf2:sha256:600000, salt length 16, 64-hex digest; no plaintext passwords found in DB file (143360 bytes scanned) | same password -> 2 different hashes; correct verifies True; case-changed password verifies False | 4 responses scanned; no password data found
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-SEC-05 - Security event audit logging
- **Requirement(s):** APAS-SR-005
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Audit log access
- **Steps:** 1. Perform successful & failed logins 2. Modify a grade/attendance 3. Inspect audit log
- **Expected result:** Entries record user ID, event type, timestamp; no passwords logged
- **Actual result:** 4 automated sub-cases (TC-SEC-05.1..05.4); 6/6 executions passed. Key results: entries=[('fac.rao', 'success', None), ('fac.rao', 'failure', 'wrong password'), ('ghost', 'failure', 'unknown user')]; timestamps ['2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00'] | grade.update by fac.rao {'assessment': 'ISA', 'new': 25, 'old': 20.0, 'subject_code': 'AM301'} at 2026-10-20T06:56:07+00:00; access.denied for aarav {"path": "/api/students/PES1UG24AM003/grades"} | 2 audit entries scanned; no passwords or tokens present
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-AUD-01 - Audit log content and 12-month retention
- **Requirement(s):** APAS-NF-004
- **Module:** Audit | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Audit log with entries; retention config
- **Steps:** 1. Modify academic records 2. Verify entries (user ID, timestamp, details) 3. Verify retention setting/ability to retrieve records >= 12 months old (simulated dates)
- **Expected result:** Changes logged with timestamp; logs retrievable for >= 12 months; logs not editable by users
- **Actual result:** 4 automated sub-cases (TC-AUD-01.1..01.4); 4/4 executions passed. Key results: logged: ['attendance.create', 'attendance.update', 'config.update', 'grade.create', 'grade.update', 'student.create', 'student.update']; grade.update {'assessment': 'ISA', 'new': 35, 'old': 30.0, 'subject_code': 'AM10... | retained with 12 months: ['11m29d', '30d']; with 6 (minimum 12 enforced): ['11m29d', '30d']; with 18: ['11m29d', '12m2d', '13m', '30d'] | direct UPDATE -> 'audit_log is append-only'; API PUT/DELETE -> [405, 405] Cycle 1 result was Fail (test script error); retested in cycle 2.
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)

## TC-UX-01 - Accessibility (WCAG 2.1 AA)
- **Requirement(s):** APAS-NF-005
- **Module:** Usability | **Priority:** Medium | **Type:** Non-Functional
- **Preconditions:** Accessibility tools (axe/WAVE/Lighthouse, contrast checker)
- **Steps:** 1. Navigate all key pages using keyboard only 2. Check focus visibility 3. Run contrast checks 4. Run automated audit
- **Expected result:** All functions keyboard-operable; text contrast meets AA (4.5:1 normal text); audit shows no AA failures
- **Actual result:** 4 automated sub-cases (TC-UX-01.1..01.4); 4/4 executions passed. Key results: 4 pages checked, 0 problems: ['login', 'student dashboard', 'admin overview', 'admin student view'] | Both error cases render role="alert" message linked by aria-describedby | text/bg 16.46:1; text/surface 15.21:1; text-muted/bg 7.84:1; text-muted/surface 7.25:1; link/bg 7.36:1; link/surface 6.8:1; on-primary/primary 7.36:1; danger/bg 7.52:1; warning-text/warning-bg 7.51:1; border/bg 4.76:1... Note: Automated checks used Python (labels, landmarks, tab order, WCAG contrast formula) instead of axe/WAVE. The manual keyboard/screen-reader checklist is still open.
- **Status:** Pass (executed 2026-10-20, tester Manasvi G V)
