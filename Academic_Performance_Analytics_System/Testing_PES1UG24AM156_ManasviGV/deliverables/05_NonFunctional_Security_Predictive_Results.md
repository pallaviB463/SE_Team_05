# Performance, Security, Reliability, Accessibility and Predictive Analytics Results

**Project:** Academic Performance Analytics System (APAS) v1.0  
**Prepared by:** Manasvi G V (PES1UG24AM156), Test Engineer, Team 05  
**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  
**Final execution run:** 2026-10-20T12:24:34+05:30 to 2026-10-20T12:26:10+05:30  
**Generated:** 20-10-2026 12:26


## 1. Performance (APAS-NF-001, TC-PERF-01)

Load profile: 306 students, 50 concurrent clients (team test data TD-12; the SRS does not define it, see DOC-003), HTTPS, 300 requests. Cycle 1 used 10 concurrent clients.

| Dashboard | Cycle 1 p95 (s) | Cycle 2 p95 (s) | Cycle 2 max (s) | Target |
|---|---|---|---|---|
| admin API overview | 4.189 | 0.489 | 0.523 | <= 3.0 |
| faculty API overview | 2.994 | 0.508 | 0.544 | <= 3.0 |
| student API dashboard | 1.648 | 0.349 | 0.355 | <= 3.0 |
| faculty selected student | 1.591 | 0.406 | 0.427 | <= 3.0 |
| admin HTML overview | 2.11 | 0.485 | 0.507 | <= 3.0 |
| faculty HTML student | 1.752 | 0.35 | 0.365 | <= 3.0 |
| **All dashboards** | 2.744 | 0.475 | 0.544 | <= 3.0 |

Cycle 2: 100.0% of requests completed within 3 s; throughput 162.6 req/s.

TC-PERF-01.2, mixed workload (270 dashboard requests + 30 grade writes): dashboard p50 0.653 s, p95 0.795 s, max 0.942 s; write p95 0.162 s.


## 2. Security (APAS-SR-001 to SR-005, APAS-NF-003)

| Check | Result |
|---|---|
| TC-SEC-01.1 Every protected endpoint rejects unauthenticated requests | Pass: 20 protected API operations -> all HTTP 401; /dashboard -> 302 /login |
| TC-SEC-01.2 Forged, malformed or tampered tokens are rejected | Pass: Authorization 'Bearer invalidtoken...' -> HTTP 401 / Authorization 'Bearer ...' -> HTTP 401 / ... plus 3 more data variants (all 5/5 passed) |
| TC-SEC-02.1 A student cannot access another student's academic records | Pass: GET /api/students/PES1UG24AM003 as aarav -> HTTP 403, no data leaked / GET /api/students/PES1UG24AM003/grades as aarav -> HTTP 403, no data leaked / ... plus 5 more data variants (all 7/7 passed) |
| TC-SEC-02.2 Faculty cannot change grades of subjects they are not assigned to | Pass: POST -> 403, PUT -> 403; stored score still 20.0 |
| TC-SEC-02.3 Students cannot escalate privileges through crafted requests | Pass: grade/profile/thresholds/audit -> [403, 403, 403, 403]; profile unchanged ('Aarav Sharma') |
| TC-SEC-03.1 Plain-HTTP requests are redirected (GET) or rejected (state-changing) | Pass: HTTP GET -> 301 https://localhost/dashboard; HTTP POST -> 403; HSTS='max-age=31536000; includeSubDomains'; cookie Secure |
| TC-SEC-03.2 Server negotiates TLS 1.2/1.3 and refuses TLS 1.0/1.1 | Pass (with limitation): TLSv1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); TLSv1.1: refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)); TLSv1.2: accepted (TLSv1.2, ECDHE-RSA-AES256-GCM-SHA384); TLSv1.3: accepted (TLSv1.3, TLS_AES_256_GCM_SHA384) |
| TC-SEC-03.3 A client-supplied X-Forwarded-Proto header cannot bypass HTTPS enforcement | Pass: spoofed GET -> HTTP 301; spoofed POST login -> HTTP 403 |
| TC-SEC-04.1 Passwords are stored as salted PBKDF2 hashes, never in plaintext | Pass: 9 accounts: pbkdf2:sha256:600000, salt length 16, 64-hex digest; no plaintext passwords found in DB file (143360 bytes scanned) |
| TC-SEC-04.2 Identical passwords produce different hashes; verification works | Pass: same password -> 2 different hashes; correct verifies True; case-changed password verifies False |
| TC-SEC-04.3 Password hashes are never exposed by the API | Pass: 4 responses scanned; no password data found |
| TC-SEC-05.1 Successful and failed login attempts are logged with user, event type and timestamp | Pass: entries=[('fac.rao', 'success', None), ('fac.rao', 'failure', 'wrong password'), ('ghost', 'failure', 'unknown user')]; timestamps ['2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00', '2026-10-20T06:56:07+00:00'] |
| TC-SEC-05.2 Academic record changes and denied access attempts are logged | Pass: grade.update by fac.rao {'assessment': 'ISA', 'new': 25, 'old': 20.0, 'subject_code': 'AM301'} at 2026-10-20T06:56:07+00:00; access.denied for aarav {"path": "/api/students/PES1UG24AM003/grades"} |
| TC-SEC-05.3 Passwords and session tokens are never written to the audit log | Pass: 2 audit entries scanned; no passwords or tokens present |
| TC-SEC-05.4 Malicious path parameters are handled safely | Pass: /api/students/..%2F..%2Fetc%2Fpasswd -> HTTP 404 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.' / /api/students/PES1'%20OR%20'1'='1 -> HTTP 404 'Student not found' / ... plus 1 more data variants (all 3/3 passed) |

**TLS handshake results (TC-SEC-03.2):**

| Protocol | Outcome |
|---|---|
| TLSv1 | refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)) |
| TLSv1.1 | refused (SSLError: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:1000)) |
| TLSv1.2 | accepted (TLSv1.2, ECDHE-RSA-AES256-GCM-SHA384) |
| TLSv1.3 | accepted (TLSv1.3, TLS_AES_256_GCM_SHA384) |

Client library: OpenSSL 3.0.11 19 Sep 2023. TLS 1.0/1.1 were refused by the server (TLSV1_ALERT_PROTOCOL_VERSION alert received from the server).


## 3. Reliability (APAS-NF-002, TC-REL-01)

Soak test: 400/400 health probes succeeded (**100.00%** availability in a 2.8 s window) while 400 faulty requests were injected. Fault responses: [400, 401, 404, 405]; 5xx or dropped connections: 0.

Monthly availability can only be confirmed on a deployed instance; use `python tools/availability_monitor.py <url>` for 30 days and compare against the 99% target.


## 4. Audit logging (APAS-NF-004, TC-AUD-01)

- **TC-AUD-01.1** Every academic record modification is logged with user ID, timestamp and details: Pass. logged: ['attendance.create', 'attendance.update', 'config.update', 'grade.create', 'grade.update', 'student.create', 'student.update']; grade.update {'assessment': 'ISA', 'new': 35, 'old': 30.0, 'subject_code': 'AM101'}; student.update {'current_semester': {'new': 2, 'old': 1}}
- **TC-AUD-01.2** Audit records are retained for at least 12 months: Pass. retained with 12 months: ['11m29d', '30d']; with 6 (minimum 12 enforced): ['11m29d', '30d']; with 18: ['11m29d', '12m2d', '13m', '30d']
- **TC-AUD-01.3** Audit records cannot be modified: Pass. direct UPDATE -> 'audit_log is append-only'; API PUT/DELETE -> [405, 405]
- **TC-AUD-01.4** Audit entries can be retrieved and filtered by an administrator: Pass. 1 entry returned: grade.update by fac.rao at 2026-10-20T06:55:23+00:00


## 5. Accessibility (APAS-NF-005, TC-UX-01)

- **TC-UX-01.1** Pages provide labels, landmarks, skip link and a logical keyboard order: Pass. 4 pages checked, 0 problems: ['login', 'student dashboard', 'admin overview', 'admin student view']
- **TC-UX-01.2** Form errors are announced to assistive technology: Pass. Both error cases render role="alert" message linked by aria-describedby
- **TC-UX-01.3** Text and UI colours meet WCAG 2.1 AA contrast ratios: Pass. text/bg 16.46:1; text/surface 15.21:1; text-muted/bg 7.84:1; text-muted/surface 7.25:1; link/bg 7.36:1; link/surface 6.8:1; on-primary/primary 7.36:1; danger/bg 7.52:1; warning-text/warning-bg 7.51:1; border/bg 4.76:1; border/surface 4.4:1; focus/bg 5.49:1; focus/surface 5.08:1; chart-bar/surface 6.8:1; chart-line/surface 4.97:1
- **TC-UX-01.4** Keyboard focus is visible and layout reflows at narrow widths: Pass. :focus-visible outline 3px; skip link shown on focus; viewport meta present; tables in scroll wrapper

Automated checks do not replace a manual audit. Still to do: a screen-reader walkthrough (VoiceOver/NVDA), keyboard-only navigation of every page and 200% zoom, recorded in the manual checklist (docs/Manual_Accessibility_Checklist.md).


## 6. Predictive analytics evaluation (APAS-F-013 / F-014, TC-PRED-01.4)

- **Method:** Least-squares linear trend on semester SGPA (2 semesters of history), clipped to [0, 10]
- **Data:** Synthetic cohort generated by apas.seed.add_synthetic_students(seed=2026); 300 students; semesters 1-2 used as history, semester 3 held out.
- **Coverage:** 300/300 eligible students received a prediction.
- **Error:** MAE 0.858 SGPA, RMSE 1.39 SGPA, mean error (bias) 0.071.
- **Risk classification (SGPA < 6.0):** TP 79, FP 18, FN 23, TN 180; precision 0.814, recall 0.775, F1 0.794, accuracy 0.863.
- **Limitations:** synthetic data only; linear extrapolation from 2 data points; no accuracy target exists in the SRS (DOC-004), so these figures are informational. Re-evaluate on anonymised historical records before relying on predictions.

