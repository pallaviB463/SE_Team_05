# APAS Test Cases

Derived from SRS v1.0 / STP v1.0. Status values: Pass, Fail, Blocked, Not Executed.

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
- **Actual result:** 
- **Status:** Not Executed

## TC-AUTH-02 - Role-based access to functions
- **Requirement(s):** APAS-F-002
- **Module:** Authentication | **Priority:** High | **Type:** Functional
- **Preconditions:** Admin, faculty, student accounts logged in
- **Steps:** 1. As student, try faculty pages (grade entry) via menu and direct URL 2. As faculty, try admin user-management 3. As admin, access admin functions
- **Expected result:** Each role sees/accesses only permitted functions; others return 403/redirect
- **Actual result:** 
- **Status:** Not Executed

## TC-AUTH-03 - Secure logout and session termination
- **Requirement(s):** APAS-F-003
- **Module:** Authentication | **Priority:** High | **Type:** Functional
- **Preconditions:** User logged in
- **Steps:** 1. Click Logout 2. Press browser Back 3. Re-open a protected URL 4. Replay old session token (Postman)
- **Expected result:** Session terminated; protected pages require re-login; old token rejected (401)
- **Actual result:** 
- **Status:** Not Executed

## TC-REC-01 - Student profile management
- **Requirement(s):** APAS-F-004
- **Module:** Academic Records | **Priority:** High | **Type:** Functional
- **Preconditions:** Admin logged in
- **Steps:** 1. Create student profile 2. View it 3. Update fields 4. Submit invalid/missing mandatory data 5. Try as student/faculty
- **Expected result:** Profile created/updated and stored correctly; invalid data rejected; non-admin changes denied
- **Actual result:** 
- **Status:** Not Executed

## TC-REC-02 - Grade entry and update
- **Requirement(s):** APAS-F-005
- **Module:** Academic Records | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty logged in; student & assessment exist
- **Steps:** 1. Enter valid grade 2. Update it 3. Enter invalid values (negative, >max, text, blank) 4. Boundary values (0, max)
- **Expected result:** Valid grades saved and displayed; invalid rejected with message; boundaries accepted per rules
- **Actual result:** 
- **Status:** Not Executed

## TC-REC-03 - Attendance recording and % calculation
- **Requirement(s):** APAS-F-006
- **Module:** Attendance | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty logged in; classes defined
- **Steps:** 1. Record attendance for known data set (e.g. 18 present of 20) 2. View percentage 3. Test 0 classes, 100%, all absent
- **Expected result:** Percentage matches attendance/total x 100 (90%); edge cases handled without error (no divide-by-zero)
- **Actual result:** 
- **Status:** Not Executed

## TC-ANA-01 - Overall performance calculation
- **Requirement(s):** APAS-F-007
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Grades and assessment scores loaded
- **Steps:** 1. Load student with known scores 2. View overall performance 3. Compare with manual calculation using configured rules
- **Expected result:** System value equals expected value
- **Actual result:** 
- **Status:** Not Executed

## TC-ANA-02 - Subject-wise & semester-wise analysis
- **Requirement(s):** APAS-F-008
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Multi-semester, multi-subject data exists
- **Steps:** 1. Open analysis for student 2. Compare subject-wise and semester-wise figures with source data
- **Expected result:** Subject/semester comparisons are accurate and trends correct
- **Actual result:** 
- **Status:** Not Executed

## TC-ANA-03 - Low-performance / low-attendance identification
- **Requirement(s):** APAS-F-009
- **Module:** Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Thresholds configured; students above/below/at threshold
- **Steps:** 1. Run identification 2. Check flagged list vs. expected
- **Expected result:** Students below thresholds flagged; at/above not flagged; boundary student handled per rule
- **Actual result:** 
- **Status:** Not Executed

## TC-VIS-01 - Role-appropriate dashboard
- **Requirement(s):** APAS-F-010
- **Module:** Dashboard | **Priority:** High | **Type:** Functional
- **Preconditions:** All role accounts with data
- **Steps:** 1. Open dashboard as each role 2. Verify grades, attendance %, overall performance 3. Student views other student's data
- **Expected result:** Accurate data for selected/authorized student; unauthorized data not visible
- **Actual result:** 
- **Status:** Not Executed

## TC-VIS-02 - Graphical trends (bar/line)
- **Requirement(s):** APAS-F-011
- **Module:** Dashboard | **Priority:** Medium | **Type:** Functional
- **Preconditions:** Multi-semester data exists
- **Steps:** 1. Open trend charts 2. Compare plotted values with stored data 3. Check labels/legends
- **Expected result:** Bar and line charts accurately reflect stored/calculated data
- **Actual result:** 
- **Status:** Not Executed

## TC-REP-01 - Report generation and download
- **Requirement(s):** APAS-F-012
- **Module:** Reporting | **Priority:** High | **Type:** Functional
- **Preconditions:** Faculty/admin logged in
- **Steps:** 1. Select report type/filters/format 2. Generate 3. Download 4. Compare contents 5. Request as unauthorized user / invalid filters
- **Expected result:** Report generated and downloadable with accurate grades, attendance, summaries; invalid/unauthorized requests rejected
- **Actual result:** 
- **Status:** Not Executed

## TC-PRED-01 - Performance prediction
- **Requirement(s):** APAS-F-013
- **Module:** Predictive Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Trained model; students with sufficient history + students with insufficient history
- **Steps:** 1. Request predictions 2. Check eligible and ineligible students
- **Expected result:** Predictions generated and displayed for eligible students; clear message for insufficient data
- **Actual result:** 
- **Status:** Not Executed

## TC-PRED-02 - At-risk student identification
- **Requirement(s):** APAS-F-014
- **Module:** Predictive Analytics | **Priority:** High | **Type:** Functional
- **Preconditions:** Risk thresholds configured
- **Steps:** 1. Run risk classification 2. Verify risk list against expected classification on labelled test data
- **Expected result:** Students meeting risk criteria correctly classified and listed
- **Actual result:** 
- **Status:** Not Executed

## TC-PRED-03 - Insights and recommendations
- **Requirement(s):** APAS-F-015
- **Module:** Predictive Analytics | **Priority:** Medium | **Type:** Functional
- **Preconditions:** Students with known weaknesses/risk factors
- **Steps:** 1. Open insights for weak-subject, low-attendance and healthy students
- **Expected result:** Recommendations relevant to the identified weakness/risk factor
- **Actual result:** 
- **Status:** Not Executed

## TC-PERF-01 - Dashboard response time
- **Requirement(s):** APAS-NF-001
- **Module:** Performance | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Normal-load dataset; JMeter configured
- **Steps:** 1. Simulate normal concurrent load 2. Request dashboard repeatedly (e.g. 200+ requests) 3. Compute 95th percentile
- **Expected result:** 95th percentile response time <= 3 seconds
- **Actual result:** 
- **Status:** Not Executed

## TC-REL-01 - Monthly availability
- **Requirement(s):** APAS-NF-002
- **Module:** Reliability | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Uptime monitoring in place
- **Steps:** 1. Collect monthly uptime log excl. scheduled maintenance 2. Compute availability
- **Expected result:** Availability >= 99%
- **Actual result:** 
- **Status:** Not Executed

## TC-SEC-01 - Access restriction & authentication required
- **Requirement(s):** APAS-NF-003; APAS-SR-001
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Test accounts; unauthenticated client
- **Steps:** 1. Access protected URLs/API without login 2. Login with invalid credentials 3. Access another user's records by changing studentId
- **Expected result:** Unauthenticated/unauthorized attempts rejected (401/403); valid login allows access
- **Actual result:** 
- **Status:** Not Executed

## TC-SEC-02 - Role-based access control (security)
- **Requirement(s):** APAS-SR-002
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Admin/faculty/student sessions
- **Steps:** 1. Call every API endpoint with each role 2. Attempt UI-hidden functions directly via URL/API
- **Expected result:** Only role-permitted operations succeed; checks enforced server-side
- **Actual result:** 
- **Status:** Not Executed

## TC-SEC-03 - HTTPS / TLS 1.2+
- **Requirement(s):** APAS-SR-003
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Deployed test environment
- **Steps:** 1. Open via http:// 2. Run TLS scan (e.g. SSL Labs/nmap/testssl) 3. Attempt TLS 1.0/1.1
- **Expected result:** HTTP redirected/rejected; only TLS 1.2 or higher accepted
- **Actual result:** 
- **Status:** Not Executed

## TC-SEC-04 - Password hashing
- **Requirement(s):** APAS-SR-004
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** DB read access in test env
- **Steps:** 1. Create user 2. Inspect stored password field 3. Verify login still works 4. Check logs
- **Expected result:** No plaintext passwords in DB/logs; hash from approved algorithm (e.g. bcrypt/Argon2/PBKDF2); login works
- **Actual result:** 
- **Status:** Not Executed

## TC-SEC-05 - Security event audit logging
- **Requirement(s):** APAS-SR-005
- **Module:** Security | **Priority:** High | **Type:** Security
- **Preconditions:** Audit log access
- **Steps:** 1. Perform successful & failed logins 2. Modify a grade/attendance 3. Inspect audit log
- **Expected result:** Entries record user ID, event type, timestamp; no passwords logged
- **Actual result:** 
- **Status:** Not Executed

## TC-AUD-01 - Audit log content and 12-month retention
- **Requirement(s):** APAS-NF-004
- **Module:** Audit | **Priority:** High | **Type:** Non-Functional
- **Preconditions:** Audit log with entries; retention config
- **Steps:** 1. Modify academic records 2. Verify entries (user ID, timestamp, details) 3. Verify retention setting/ability to retrieve records >= 12 months old (simulated dates)
- **Expected result:** Changes logged with timestamp; logs retrievable for >= 12 months; logs not editable by users
- **Actual result:** 
- **Status:** Not Executed

## TC-UX-01 - Accessibility (WCAG 2.1 AA)
- **Requirement(s):** APAS-NF-005
- **Module:** Usability | **Priority:** Medium | **Type:** Non-Functional
- **Preconditions:** Accessibility tools (axe/WAVE/Lighthouse, contrast checker)
- **Steps:** 1. Navigate all key pages using keyboard only 2. Check focus visibility 3. Run contrast checks 4. Run automated audit
- **Expected result:** All functions keyboard-operable; text contrast meets AA (4.5:1 normal text); audit shows no AA failures
- **Actual result:** 
- **Status:** Not Executed
