# Test Execution Log

**Project:** Academic Performance Analytics System (APAS) v1.0  
**Prepared by:** Manasvi G V (PES1UG24AM156), Test Engineer, Team 05  
**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  
**Final execution run:** 2026-10-20T12:24:34+05:30 to 2026-10-20T12:26:10+05:30  
**Generated:** 20-10-2026 12:26


## Test environment

| Item | Value |
|---|---|
| Application under test | APAS reference build (apas/), production configuration (HTTPS enforced) |
| Python / Flask / pytest | 3.12.0 / 3.1.3 / 9.1.1 |
| Database | SQLite 3.42.0 |
| Platform | macOS-26.6.2-arm64-arm-64bit |
| Test data | test_data/apas_test_data.json (6 students, 9 subjects, 9 accounts) + 300 synthetic students for performance and prediction evaluation |

## Execution summary

| Cycle | Test cases | Pass | Fail | Blocked | Not executed | Executions (incl. data variants) |
|---|---|---|---|---|---|---|
| Cycle 1 (2026-10-20) | 85 | 81 | 4 | 0 | 0 | 190 (186 pass / 4 fail) |
| Cycle 2 - retest and regression (2026-10-20) | 88 | 88 | 0 | 0 | 0 | 196 (196 pass / 0 fail) |

5 passed test cases have a documented limitation (see the Limitation column of the test case specification and the RTM).

A dry run before cycle 1 was discarded because of a test-harness configuration error (TS-001 in the defect report). It is not counted as an execution cycle.


## Detailed log

| TC ID | Title | Requirement(s) | Cycle 1 | Cycle 2 (final) | Actual result (final cycle) | Executed |
|---|---|---|---|---|---|---|
| TC-AUTH-01.1 | Valid credentials grant access for every role | APAS-F-001 | Pass | **Pass** (3/3) | admin: login HTTP 200, role=admin, token issued (43 chars); dashboard HTTP 200<br>fac.rao: login HTTP 200, role=faculty, token issued (43 chars); dashboard HTTP 200<br>aarav: login HTTP 200, role=student, token issued (43 chars); dashboard HTTP 200 | 2026-10-20 12:24 |
| TC-AUTH-01.2 | Wrong password is rejected | APAS-F-001 | Pass | **Pass** (1/1) | HTTP 401, message='Invalid username or password', no token | 2026-10-20 12:24 |
| TC-AUTH-01.3 | Unknown username is rejected without revealing whether the account exists | APAS-F-001 | Pass | **Pass** (1/1) | HTTP 401, message identical to wrong-password case: 'Invalid username or password' | 2026-10-20 12:24 |
| TC-AUTH-01.4 | Missing or malformed credential fields are rejected | APAS-F-001 | Pass | **Pass** (6/6) | payload={} -> HTTP 400 'Username and password are required'<br>payload={'username': 'fac.rao'} -> HTTP 400 'Username and password are required'<br>payload={'password': 'x'} -> HTTP 400 'Username and password are required'<br>... plus 3 more data variants (all 6/6 passed) | 2026-10-20 12:24 |
| TC-AUTH-01.5 | Deactivated account cannot log in | APAS-F-001 | Pass | **Pass** (1/1) | HTTP 401 'Invalid username or password' | 2026-10-20 12:24 |
| TC-AUTH-01.6 | Account is temporarily locked after 5 consecutive failed attempts | APAS-F-001, APAS-SR-001 | Pass | **Pass** (1/1) | After 5 failures, correct password -> HTTP 401 'Account temporarily locked after repeated failed attempts. Try again later.' | 2026-10-20 12:24 |
| TC-AUTH-01.7 | Web login form accepts valid and rejects invalid credentials | APAS-F-001 | Pass | **Pass** (1/1) | invalid -> HTTP 401 with alert; valid -> 302 to /dashboard, cookie flags: HttpOnly, Secure, SameSite=Lax; dashboard HTTP 200 | 2026-10-20 12:24 |
| TC-AUTH-01.8 | SQL injection in the username field does not bypass authentication | APAS-F-001, APAS-SR-001 | Pass | **Pass** (4/4) | '' OR '1'='1' -> HTTP 401; users table intact (9 rows)<br>'admin'--' -> HTTP 401; users table intact (9 rows)<br>'admin" OR ""="' -> HTTP 401; users table intact (9 rows)<br>... plus 1 more data variants (all 4/4 passed) | 2026-10-20 12:24 |
| TC-AUTH-02.1 | Each role receives a role-appropriate dashboard | APAS-F-002 | Pass | **Pass** (1/1) | admin totals={'faculty': 3, 'students': 6, 'users': 9}; faculty subjects=['AM101', 'AM102', 'AM201', 'AM202', 'AM301', 'AM302']; student sees only PES1UG24AM001 | 2026-10-20 12:24 |
| TC-AUTH-02.2 | Users can access only the functions permitted for their role | APAS-F-002 | Pass | **Pass** (17/17) | admin POST /api/students -> HTTP 201 (expected 201)<br>fac.rao POST /api/students -> HTTP 403 (expected 403)<br>aarav POST /api/students -> HTTP 403 (expected 403)<br>... plus 14 more data variants (all 17/17 passed) | 2026-10-20 12:25 |
| TC-AUTH-03.1 | Logout terminates the session token | APAS-F-003 | Pass | **Pass** (1/1) | before logout 200; logout 200; reuse of token -> HTTP 401 | 2026-10-20 12:25 |
| TC-AUTH-03.2 | Browser logout clears the session and protected pages require login again | APAS-F-003 | Pass | **Pass** (1/1) | dashboard 200 (no-store); logout -> 302 /login; dashboard afterwards -> 302 /login | 2026-10-20 12:25 |
| TC-AUTH-03.3 | Idle sessions expire after 30 minutes | APAS-F-003 | Pass | **Pass** (1/1) | after 31 min idle -> HTTP 401; sessions remaining=0 | 2026-10-20 12:25 |
| TC-AUTH-03.4 | Logout without a session is rejected | APAS-F-003 | Pass | **Pass** (1/1) | HTTP 401 | 2026-10-20 12:25 |
| TC-REC-01.1 | Administrator creates a student profile and it is stored correctly | APAS-F-004 | Pass | **Pass** (1/1) | create HTTP 201; GET returned {id=PES1UG24AM007, name=Neel Kapoor, email=neel.kapoor@apas.test, program=B.Tech CSE (AI & ML), current_semester=1}; DB row present | 2026-10-20 12:25 |
| TC-REC-01.2 | Administrator updates a student profile | APAS-F-004 | Pass | **Pass** (1/1) | HTTP 200; name 'Ishita Rao' -> 'Ishita R. Rao', semester 3 -> 4; updated_at changed | 2026-10-20 12:25 |
| TC-REC-01.3 | Invalid or incomplete profile data is rejected | APAS-F-004 | Pass | **Pass** (15/15) | id='' -> HTTP 400 {'id': 'is required'}<br>id='abc' -> HTTP 400 {'id': 'must be 6-20 upper-case letters or digits'}<br>id='PES 1UG' -> HTTP 400 {'id': 'must be 6-20 upper-case letters or digits'}<br>... plus 12 more data variants (all 15/15 passed) | 2026-10-20 12:25 |
| TC-REC-01.4 | Duplicate IDs/emails and unknown students are handled | APAS-F-004 | Pass | **Pass** (1/1) | duplicate id/email/missing GET/missing PUT/change id -> [409, 409, 404, 404, 400] | 2026-10-20 12:25 |
| TC-REC-02.1 | Faculty enters a valid grade and it is saved and displayed | APAS-F-005 | Pass | **Pass** (1/1) | POST ISA/ESA -> 201/201; stored ISA=42, ESA=45; AM301 = 87.0% grade A | 2026-10-20 12:25 |
| TC-REC-02.2 | Faculty updates an existing grade | APAS-F-005 | Pass | **Pass** (1/1) | upsert -> HTTP 200; PUT -> HTTP 200; final ESA=38.0, rows=1 | 2026-10-20 12:25 |
| TC-REC-02.3 | Boundary grade values within 0-50 are accepted | APAS-F-005 | Pass | **Pass** (5/5) | score=0 -> HTTP 201, stored 0.0<br>score=0.5 -> HTTP 201, stored 0.5<br>score=25 -> HTTP 201, stored 25.0<br>... plus 2 more data variants (all 5/5 passed) | 2026-10-20 12:25 |
| TC-REC-02.4 | Invalid grade values are rejected and nothing is stored | APAS-F-005 | Pass | **Pass** (11/11) | score=-1 -> HTTP 400 'score must be between 0 and 50'; grade rows unchanged<br>score=-0.01 -> HTTP 400 'score must be between 0 and 50'; grade rows unchanged<br>score=50.01 -> HTTP 400 'score must be between 0 and 50'; grade rows unchanged<br>... plus 8 more data variants (all 11/11 passed) | 2026-10-20 12:25 |
| TC-REC-02.5 | Grades for unknown subjects or assessments are rejected | APAS-F-005 | Pass | **Pass** (3/3) | {'subject_code': 'XX999', 'assessment': 'ISA', 'score': 10} -> HTTP 400 'subject_code must be an existing subject'<br>{'subject_code': 'AM301', 'assessment': 'Quiz', 'score': 10} -> HTTP 400 'assessment must be one of ['ESA', 'ISA']'<br>{'assessment': 'ISA', 'score': 10} -> HTTP 400 'subject_code must be an existing subject' | 2026-10-20 12:25 |
| TC-REC-02.6 | Grade entry for a non-existent student or with a non-JSON body is rejected | APAS-F-005 | Pass | **Pass** (1/1) | unknown student -> 404; non-JSON body -> 400 | 2026-10-20 12:25 |
| TC-REC-03.1 | Attendance percentage matches recorded attendance | APAS-F-006 | Pass | **Pass** (1/1) | {'PES1UG24AM001': '57/60 = 95.0%', 'PES1UG24AM002': '36/60 = 60.0%', 'PES1UG24AM005': '45/60 = 75.0%'} | 2026-10-20 12:25 |
| TC-REC-03.2 | Faculty records attendance; corrections update the percentage | APAS-F-006 | Pass | **Pass** (1/1) | after 4 entries: 3/4 = 75.0%; correction HTTP 200 -> 4/4 = 100.0% | 2026-10-20 12:25 |
| TC-REC-03.3 | Invalid attendance entries are rejected | APAS-F-006 | Pass | **Pass** (14/14) | status='Present' -> HTTP 400 'status must be 'present' or 'absent''<br>status='P' -> HTTP 400 'status must be 'present' or 'absent''<br>status='' -> HTTP 400 'status must be 'present' or 'absent''<br>... plus 11 more data variants (all 14/14 passed) | 2026-10-20 12:25 |
| TC-REC-03.4 | Faculty cannot record attendance for a subject they do not teach | APAS-F-006 | Pass | **Pass** (1/1) | HTTP 403; rows stored=0 | 2026-10-20 12:25 |
| TC-REC-03.5 | All-absent and all-present attendance give 0% and 100% | APAS-F-006 | Added in cycle 2 | **Pass** (2/2) | 4 x absent -> 0/4 = 0.0%<br>4 x present -> 4/4 = 100.0% | 2026-10-20 12:25 |
| TC-ANA-01.1 | Grade-point scale is applied correctly at every boundary | APAS-F-007 | Pass | **Pass** (12/12) | 100% -> (10, 'S')<br>90% -> (10, 'S')<br>89.99% -> (9, 'A')<br>... plus 9 more data variants (all 12/12 passed) | 2026-10-20 12:24 |
| TC-ANA-01.2 | Overall performance (CGPA and overall %) matches the hand calculation | APAS-F-007 | Pass | **Pass** (5/5) | PES1UG24AM001: CGPA 9.39 (exp 9.39), overall 86.91% (exp 86.91%)<br>PES1UG24AM002: CGPA 7.82 (exp 7.82), overall 70.64% (exp 70.64%)<br>PES1UG24AM003: CGPA 5.52 (exp 5.52), overall 53.73% (exp 53.73%)<br>... plus 2 more data variants (all 5/5 passed) | 2026-10-20 12:24 |
| TC-ANA-01.3 | Performance values are recalculated after a grade update | APAS-F-007 | Pass | **Pass** (1/1) | SGPA 6.45, overall 58.55% | 2026-10-20 12:24 |
| TC-ANA-01.4 | Incomplete subject records are reported but excluded from GPA | APAS-F-007 | Pass | **Pass** (1/1) | AM301 status=incomplete, grade=None, CGPA=None, incomplete=['AM301'] | 2026-10-20 12:24 |
| TC-ANA-01.5 | A student with no records produces empty results without errors | APAS-F-007 | Pass | **Pass** (1/1) | HTTP 200; subjects=[], CGPA=None, attendance=None, flagged=False | 2026-10-20 12:24 |
| TC-ANA-02.1 | Semester-wise SGPA and percentage match the hand calculation | APAS-F-008 | Pass | **Pass** (3/3) | PES1UG24AM001: SGPA [9.09, 9.36, 9.73], % [84.55, 86.82, 89.36]<br>PES1UG24AM002: SGPA [7.73, 7.73, 8.0], % [69.91, 70.55, 71.45]<br>PES1UG24AM003: SGPA [7.36, 6.0, 3.18], % [65.73, 55.18, 40.27] | 2026-10-20 12:24 |
| TC-ANA-02.2 | Subject-wise results are accurate for every subject | APAS-F-008 | Pass | **Pass** (1/1) | 9 subjects returned; semester 3: {'AM301': (42.0, 'E', 5), 'AM302': (35.0, 'F', 0), 'AM303': (45.0, 'E', 5)} | 2026-10-20 12:24 |
| TC-ANA-02.3 | Performance trends identify improving and declining students | APAS-F-008 | Pass | **Pass** (1/1) | Aarav [9.09, 9.36, 9.73] (increasing); Kabir [7.36, 6.0, 3.18] (decreasing) | 2026-10-20 12:24 |
| TC-ANA-03.1 | Students below default thresholds are flagged | APAS-F-009 | Pass | **Pass** (1/1) | flagged={'PES1UG24AM002': ['Attendance in AM301 is 60.0% (below 75%)', 'Attendance in AM302 is 60.0% (below 75%)', 'Attendance in AM303 is 60.0% (below 75%)'], 'PES1UG24AM003': ['Failed AM302 (35.0%)']}; Rohan (boundary 75%/50%) not flagged | 2026-10-20 12:24 |
| TC-ANA-03.2 | Flagging follows thresholds configured by the administrator | APAS-F-009 | Pass | **Pass** (1/1) | thresholds updated (HTTP 200); flagged=['PES1UG24AM003', 'PES1UG24AM004', 'PES1UG24AM005'] | 2026-10-20 12:24 |
| TC-ANA-03.3 | Invalid threshold values are rejected | APAS-F-009 | Pass | **Pass** (5/5) | {'min_attendance_pct': 101} -> HTTP 400 'min_attendance_pct must be a number between 0 and 100'<br>{'min_attendance_pct': -1} -> HTTP 400 'min_attendance_pct must be a number between 0 and 100'<br>{'risk_high_sgpa': 11} -> HTTP 400 'risk_high_sgpa must be a number between 0 and 10'<br>... plus 2 more data variants (all 5/5 passed) | 2026-10-20 12:24 |
| TC-VIS-01.1 | Student dashboard shows the student's own grades, attendance and performance | APAS-F-010 | Pass | **Pass** (1/1) | student=PES1UG24AM001 CGPA=9.39 overall=86.91% attendance=95.0%; ?student_id=AM003 still returned PES1UG24AM001 | 2026-10-20 12:25 |
| TC-VIS-01.2 | Faculty dashboard for a selected student matches stored records | APAS-F-010 | Pass | **Pass** (1/1) | API CGPA=7.82, attendance=60.0; HTML KPIs={'kpi-cgpa': '7.82', 'kpi-overall': '70.64', 'kpi-attendance': '60.0'} | 2026-10-20 12:25 |
| TC-VIS-01.3 | Overview dashboard lists all students with correct flag and risk counts | APAS-F-010 | Pass | **Pass** (1/1) | API students=6, flagged=2, at_risk=2; HTML {'kpi-students': '6', 'kpi-flagged': '2', 'kpi-at-risk': '2'} | 2026-10-20 12:25 |
| TC-VIS-01.4 | Dashboard for a non-existent student returns a clear not-found response | APAS-F-010 | Pass | **Pass** (1/1) | API 404, HTML 404 'Student not found' | 2026-10-20 12:25 |
| TC-VIS-01.5 | Overview dashboard reflects a grade change on the next request (regression for DEF-002 cache) | APAS-F-010, APAS-NF-001 | Added in cycle 2 | **Pass** (1/1) | flagged_count 2 -> 3; Rohan reasons ['Overall performance 44.55% (below 50%)', 'Failed AM302 (35.0%)'] | 2026-10-20 12:25 |
| TC-VIS-02.1 | Bar charts represent the stored subject percentages accurately | APAS-F-011 | Pass | **Pass** (1/1) | subject bars=[('AM301', '42.0', '67.2'), ('AM302', '35.0', '56.0'), ('AM303', '45.0', '72.0')]; attendance bars=[('AM301', 80.0), ('AM302', 80.0), ('AM303', 80.0)] | 2026-10-20 12:25 |
| TC-VIS-02.2 | Line graph plots the semester SGPA trend correctly | APAS-F-011 | Pass | **Pass** (1/1) | points=[('1', '9.09', '54.56'), ('2', '9.36', '50.24'), ('3', '9.73', '44.32')] | 2026-10-20 12:25 |
| TC-VIS-02.3 | Charts reflect newly recorded data | APAS-F-011 | Pass | **Pass** (1/1) | AM302 bar value=50.0 height=80.0 | 2026-10-20 12:25 |
| TC-VIS-02.4 | Dashboards without data show a message instead of an empty chart | APAS-F-011 | Pass | **Pass** (1/1) | HTTP 200; no SVG charts rendered; empty-state messages shown | 2026-10-20 12:25 |
| TC-REP-01.1 | Faculty generates and downloads an accurate CSV report | APAS-F-012 | Pass | **Pass** (1/1) | HTTP 200 text/csv; attachment; filename="APAS_Report_PES1UG24AM001_2026-10-20.csv"; 9 subject rows; CGPA 9.39; overall 86.91; attendance ['57', '60', '95.0'] | 2026-10-20 12:25 |
| TC-REP-01.2 | Reports include threshold flags and are available as JSON | APAS-F-012 | Pass | **Pass** (1/1) | CSV flags='Failed AM302 (35.0%)'; JSON CGPA=5.52 | 2026-10-20 12:25 |
| TC-REP-01.3 | Report requests are validated and restricted to permitted students | APAS-F-012 | Pass | **Pass** (1/1) | own/other/missing/bad format -> [200, 403, 404, 400] | 2026-10-20 12:25 |
| TC-PRED-01.1 | Predictions are generated for students with sufficient history | APAS-F-013 | Pass | **Pass** (3/3) | PES1UG24AM001: predicted SGPA 10.0 (exp 10.0), trend improving, confidence medium<br>PES1UG24AM002: predicted SGPA 8.09 (exp 8.09), trend improving, confidence medium<br>PES1UG24AM003: predicted SGPA 1.33 (exp 1.33), trend declining, confidence medium | 2026-10-20 12:25 |
| TC-PRED-01.2 | Students without sufficient history get an explicit 'insufficient data' result | APAS-F-013 | Pass | **Pass** (3/3) | PES1UG24AM004: status=insufficient_data, message='At least 2 completed semesters are required for a prediction.'<br>PES1UG24AM005: status=insufficient_data, message='At least 2 completed semesters are required for a prediction.'<br>PES1UG24AM006: status=insufficient_data, message='At least 2 completed semesters are required for a prediction.' | 2026-10-20 12:25 |
| TC-PRED-01.3 | Only faculty and administrators can retrieve predictions | APAS-F-013 | Pass | **Pass** (1/1) | student -> 403; faculty -> 200 | 2026-10-20 12:25 |
| TC-PRED-01.4 | Back-test the prediction method on a synthetic cohort | APAS-F-013 | Pass (with limitation) | **Pass (with limitation)** (1/1) | 300/300 predictions; MAE 0.858, RMSE 1.39; risk precision 0.814, recall 0.775, F1 0.794, accuracy 0.863 | 2026-10-20 12:25 |
| TC-PRED-02.1 | Students meeting the risk criteria appear in the academic risk list | APAS-F-014 | Pass | **Pass** (1/1) | at-risk={'PES1UG24AM002': ('high', ['Attendance 60.0% below 65%']), 'PES1UG24AM003': ('high', ['Predicted SGPA 1.33 below 5', 'SGPA trend is declining'])} | 2026-10-20 12:25 |
| TC-PRED-02.2 | Changing the predefined risk criteria changes the classification | APAS-F-014 | Pass | **Pass** (1/1) | risk list (ordered high->medium) = [('PES1UG24AM003', 'high'), ('PES1UG24AM002', 'medium')] | 2026-10-20 12:25 |
| TC-PRED-03.1 | Recommendations address the identified weaknesses and risk factors | APAS-F-015 | Pass | **Pass** (1/1) | 5 recommendations: [('academic', 'AM301'), ('academic', 'AM303'), ('critical', 'AM302'), ('risk', ''), ('trend', '')] | 2026-10-20 12:25 |
| TC-PRED-03.2 | Attendance recommendations for low attendance; positive message when on track | APAS-F-015 | Pass | **Pass** (2/2) | PES1UG24AM002: ['Attendance in Design and Analysis of Algorithms is 60.0%, below the required 75%. Attend classes regularly.', 'Attendance in Database Management Systems is 60.0%, below the required 75%. Attend classes regularly.', 'Attendance in Software Engineering is 60.0%, below the required 75%. Attend classes regularly.']<br>PES1UG24AM001: ['Performance is on track. Maintain consistent study and attendance.'] | 2026-10-20 12:25 |
| TC-PRED-03.3 | Students can see their own insights but not another student's | APAS-F-015 | Pass | **Pass** (1/1) | own -> 200; other student -> 403 | 2026-10-20 12:25 |
| TC-SEC-01.1 | Every protected endpoint rejects unauthenticated requests | APAS-SR-001, APAS-NF-003 | Pass | **Pass** (1/1) | 20 protected API operations -> all HTTP 401; /dashboard -> 302 /login | 2026-10-20 12:25 |
| TC-SEC-01.2 | Forged, malformed or tampered tokens are rejected | APAS-SR-001, APAS-NF-003 | Pass | **Pass** (5/5) | Authorization 'Bearer invalidtoken...' -> HTTP 401<br>Authorization 'Bearer ...' -> HTTP 401<br>Authorization 'Basic YWRtaW46QWRtaW5AQV...' -> HTTP 401<br>... plus 2 more data variants (all 5/5 passed) | 2026-10-20 12:26 |
| TC-SEC-02.1 | A student cannot access another student's academic records | APAS-SR-002 | Pass | **Pass** (7/7) | GET /api/students/PES1UG24AM003 as aarav -> HTTP 403, no data leaked<br>GET /api/students/PES1UG24AM003/grades as aarav -> HTTP 403, no data leaked<br>GET /api/students/PES1UG24AM003/attendance as aarav -> HTTP 403, no data leaked<br>... plus 4 more data variants (all 7/7 passed) | 2026-10-20 12:26 |
| TC-SEC-02.2 | Faculty cannot change grades of subjects they are not assigned to | APAS-SR-002 | Pass | **Pass** (1/1) | POST -> 403, PUT -> 403; stored score still 20.0 | 2026-10-20 12:26 |
| TC-SEC-02.3 | Students cannot escalate privileges through crafted requests | APAS-SR-002 | Pass | **Pass** (1/1) | grade/profile/thresholds/audit -> [403, 403, 403, 403]; profile unchanged ('Aarav Sharma') | 2026-10-20 12:26 |
| TC-SEC-03.1 | Plain-HTTP requests are redirected (GET) or rejected (state-changing) | APAS-SR-003 | Pass | **Pass** (1/1) | HTTP GET -> 301 https://localhost/dashboard; HTTP POST -> 403; HSTS='max-age=31536000; includeSubDomains'; cookie Secure | 2026-10-20 12:26 |
| TC-SEC-03.2 | Server negotiates TLS 1.2/1.3 and refuses TLS 1.0/1.1 | APAS-SR-003 | Pass (with limitation) | **Pass (with limitation)** (1/1) | TLSv1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); TLSv1.1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); TLSv1.2: accepted (TLSv1.2, ECDHE-RSA-AES256-GCM-SHA384); TLSv1.3: accepted (TLSv1.3, TLS_AES_256_GCM_SHA384) | 2026-10-20 12:26 |
| TC-SEC-03.3 | A client-supplied X-Forwarded-Proto header cannot bypass HTTPS enforcement | APAS-SR-003 | Fail | **Pass** (1/1) | spoofed GET -> HTTP 301; spoofed POST login -> HTTP 403 | 2026-10-20 12:26 |
| TC-SEC-04.1 | Passwords are stored as salted PBKDF2 hashes, never in plaintext | APAS-SR-004 | Pass | **Pass** (1/1) | 9 accounts: pbkdf2:sha256:600000, salt length 16, 64-hex digest; no plaintext passwords found in DB file (143360 bytes scanned) | 2026-10-20 12:26 |
| TC-SEC-04.2 | Identical passwords produce different hashes; verification works | APAS-SR-004 | Pass | **Pass** (1/1) | same password -> 2 different hashes; correct verifies True; case-changed password verifies False | 2026-10-20 12:26 |
| TC-SEC-04.3 | Password hashes are never exposed by the API | APAS-SR-004 | Pass | **Pass** (1/1) | 4 responses scanned; no password data found | 2026-10-20 12:26 |
| TC-SEC-05.1 | Successful and failed login attempts are logged with user, event type and timestamp | APAS-SR-005 | Pass | **Pass** (1/1) | entries=[('fac.rao', 'success', None), ('fac.rao', 'failure', 'wrong password'), ('ghost', 'failure', 'unknown user')]; timestamps ['2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00'] | 2026-10-20 12:26 |
| TC-SEC-05.2 | Academic record changes and denied access attempts are logged | APAS-SR-005 | Pass | **Pass** (1/1) | grade.update by fac.rao {'assessment': 'ISA', 'new': 25, 'old': 20.0, 'subject_code': 'AM301'} at 2026-10-20T06:56:07+00:00; access.denied for aarav {"path": "/api/students/PES1UG24AM003/grades"} | 2026-10-20 12:26 |
| TC-SEC-05.3 | Passwords and session tokens are never written to the audit log | APAS-SR-005 | Pass | **Pass** (1/1) | 2 audit entries scanned; no passwords or tokens present | 2026-10-20 12:26 |
| TC-SEC-05.4 | Malicious path parameters are handled safely | APAS-SR-005, APAS-NF-003 | Pass | **Pass** (3/3) | /api/students/..%2F..%2Fetc%2Fpasswd -> HTTP 404 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'<br>/api/students/PES1'%20OR%20'1'='1 -> HTTP 404 'Student not found'<br>/api/analytics/performance/%3Cscript%3E -> HTTP 404 'Student not found' | 2026-10-20 12:26 |
| TC-PERF-01.1 | Dashboards load within 3 seconds for at least 95% of requests | APAS-NF-001 | Fail | **Pass (with limitation)** (1/1) | 300 requests @50 concurrent: p50 0.292 s, p95 0.475 s, max 0.544 s, 100.0% within 3 s; slowest p95 = 0.508 s | 2026-10-20 12:25 |
| TC-PERF-01.2 | Dashboards stay within 3 seconds while faculty are updating grades | APAS-NF-001 | Added in cycle 2 | **Pass (with limitation)** (1/1) | 270 dashboard requests + 30 grade writes @50 concurrent: dashboard p50 0.653 s, p95 0.795 s, max 0.942 s | 2026-10-20 12:25 |
| TC-REL-01.1 | Service stays available while receiving malformed and hostile requests | APAS-NF-002 | Pass (with limitation) | **Pass (with limitation)** (1/1) | 400/400 probes OK = 100.00% over 2.8 s; fault responses [400, 401, 404, 405], 5xx/dropped = 0 | 2026-10-20 12:25 |
| TC-REL-01.2 | An internal failure returns a generic error and the service keeps running | APAS-NF-002 | Pass | **Pass** (1/1) | failure -> HTTP 500 {'error': 'An unexpected error occurred', 'status': 500}; health afterwards HTTP 200 | 2026-10-20 12:25 |
| TC-AUD-01.1 | Every academic record modification is logged with user ID, timestamp and details | APAS-NF-004 | Pass | **Pass** (1/1) | logged: ['attendance.create', 'attendance.update', 'config.update', 'grade.create', 'grade.update', 'student.create', 'student.update']; grade.update {'assessment': 'ISA', 'new': 35, 'old': 30.0, 'subject_code': 'AM101'}; student.update {'current_semester': {'new': 2, 'old': 1}} | 2026-10-20 12:25 |
| TC-AUD-01.2 | Audit records are retained for at least 12 months | APAS-NF-004 | Fail | **Pass** (1/1) | retained with 12 months: ['11m29d', '30d']; with 6 (minimum 12 enforced): ['11m29d', '30d']; with 18: ['11m29d', '12m2d', '13m', '30d'] | 2026-10-20 12:25 |
| TC-AUD-01.3 | Audit records cannot be modified | APAS-NF-004 | Fail | **Pass** (1/1) | direct UPDATE -> 'audit_log is append-only'; API PUT/DELETE -> [405, 405] | 2026-10-20 12:25 |
| TC-AUD-01.4 | Audit entries can be retrieved and filtered by an administrator | APAS-NF-004 | Pass | **Pass** (1/1) | 1 entry returned: grade.update by fac.rao at 2026-10-20T06:55:23+00:00 | 2026-10-20 12:25 |
| TC-UX-01.1 | Pages provide labels, landmarks, skip link and a logical keyboard order | APAS-NF-005 | Pass | **Pass** (1/1) | 4 pages checked, 0 problems: ['login', 'student dashboard', 'admin overview', 'admin student view'] | 2026-10-20 12:25 |
| TC-UX-01.2 | Form errors are announced to assistive technology | APAS-NF-005 | Pass | **Pass** (1/1) | Both error cases render role="alert" message linked by aria-describedby | 2026-10-20 12:25 |
| TC-UX-01.3 | Text and UI colours meet WCAG 2.1 AA contrast ratios | APAS-NF-005 | Pass | **Pass** (1/1) | text/bg 16.46:1; text/surface 15.21:1; text-muted/bg 7.84:1; text-muted/surface 7.25:1; link/bg 7.36:1; link/surface 6.8:1; on-primary/primary 7.36:1; danger/bg 7.52:1; warning-text/warning-bg 7.51:1; border/bg 4.76:1; border/surface 4.4:1; focus/bg 5.49:1; focus/surface 5.08:1; chart-bar/surface 6.8:1; chart-line/surface 4.97:1 | 2026-10-20 12:25 |
| TC-UX-01.4 | Keyboard focus is visible and layout reflows at narrow widths | APAS-NF-005 | Pass | **Pass** (1/1) | :focus-visible outline 3px; skip link shown on focus; viewport meta present; tables in scroll wrapper | 2026-10-20 12:25 |

## Cycle 1 failures

| TC ID | Failure observed | Disposition |
|---|---|---|
| TC-SEC-03.3 | spoofed GET -> HTTP 302; spoofed POST login -> HTTP 200 | Product defect DEF-001 |
| TC-PERF-01.1 | admin API overview p95 = 4.189 s (max 7.102 s); faculty API overview p95 = 2.994 s (close to the limit). | Product defect DEF-002 |
| TC-AUD-01.2 | AssertionError: assert ['11m29d', '1... '13m', '30d'] == ['11m29d', '13m', '30d']<br>  <br>  At index 1 diff: '12m2d' != '13m'<br>  Left contains one more item: '30d'<br>  Use -v to get more diff | Test script error TS-002 |
| TC-AUD-01.3 | AssertionError: {'error': 'An unexpected error occurred', 'status': 500}<br>assert 500 == 200<br> +  where 500 = <WrapperTestResponse streamed [500 INTERNAL SERVER ERROR]>.status_code | Test script error TS-003 |
