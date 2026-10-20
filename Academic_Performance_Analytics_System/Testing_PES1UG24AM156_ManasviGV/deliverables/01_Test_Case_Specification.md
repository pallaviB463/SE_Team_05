# Test Case Specification

**Project:** Academic Performance Analytics System (APAS) v1.0  
**Prepared by:** Manasvi G V (PES1UG24AM156), Test Engineer, Team 05  
**Reference documents:** APAS SRS v1.0, APAS SAD v1.0, APAS STP v1.0  
**Final execution run:** 2026-10-20T12:24:34+05:30 to 2026-10-20T12:26:10+05:30  
**Generated:** 20-10-2026 12:26


Each test case below is implemented as an automated pytest script in `tests/`. Data-driven test cases run once per data variant (listed under *Variants*). Expected values for calculations were worked out by hand from `test_data/apas_test_data.json`.


## Authentication, Role-Based Access and Logout


### TC-AUTH-01.1: Valid credentials grant access for every role

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify that registered administrator, faculty and student users can log in with valid credentials. |
| Preconditions | Active accounts admin, fac.rao and aarav exist in the test data. |
| Test data | Valid username/password pairs from test_data/apas_test_data.json. |
| Steps | 1. POST /api/auth/login with the valid username and password.<br>2. Call GET /api/dashboard with the returned bearer token. |
| Expected result | Login returns HTTP 200 with a session token and the correct role; dashboard returns HTTP 200. |
| Variants | 3: admin-admin, fac.rao-faculty, aarav-student |
| Script | `tests/test_auth.py::test_valid_login_each_role` |

### TC-AUTH-01.2: Wrong password is rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify that an incorrect password is rejected. |
| Preconditions | Account fac.rao exists. |
| Test data | username=fac.rao, password=WrongPass@1 |
| Steps | 1. POST /api/auth/login with a wrong password. |
| Expected result | HTTP 401, generic error message, no token issued. |
| Script | `tests/test_auth.py::test_wrong_password_rejected` |

### TC-AUTH-01.3: Unknown username is rejected without revealing whether the account exists

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify that login with a non-registered username fails with the same message as a wrong password. |
| Preconditions | No account named ghost.user exists. |
| Test data | username=ghost.user, password=Whatever@123 |
| Steps | 1. POST /api/auth/login with the unknown username. |
| Expected result | HTTP 401 with the same generic message used for a wrong password. |
| Script | `tests/test_auth.py::test_unknown_user_same_message` |

### TC-AUTH-01.4: Missing or malformed credential fields are rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify input validation on the login request. |
| Preconditions | None. |
| Test data | Empty body, missing fields, blank strings, wrong JSON types. |
| Steps | 1. POST /api/auth/login with each malformed payload. |
| Expected result | HTTP 400 "Username and password are required"; no session created. |
| Variants | 6: payload0, payload1, payload2, payload3, payload4, payload5 |
| Script | `tests/test_auth.py::test_missing_credentials` |

### TC-AUTH-01.5: Deactivated account cannot log in

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify that a deactivated account is rejected even with the correct password. |
| Preconditions | Account inactive.user exists with active=false. |
| Test data | username=inactive.user with its correct password. |
| Steps | 1. POST /api/auth/login with the correct credentials of the inactive account. |
| Expected result | HTTP 401 with the generic error message. |
| Script | `tests/test_auth.py::test_inactive_account_rejected` |

### TC-AUTH-01.6: Account is temporarily locked after 5 consecutive failed attempts

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001, APAS-SR-001 |
| Type / Priority | Security / High |
| Objective | Verify brute-force protection on the login service. |
| Preconditions | Account diya exists and is unlocked. |
| Test data | 5 wrong passwords followed by the correct password. |
| Steps | 1. POST /api/auth/login five times with a wrong password.<br>2. POST /api/auth/login with the correct password. |
| Expected result | The 6th attempt (correct password) is rejected with HTTP 401 and a lockout message. |
| Script | `tests/test_auth.py::test_lockout_after_repeated_failures` |

### TC-AUTH-01.7: Web login form accepts valid and rejects invalid credentials

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001 |
| Type / Priority | Functional / High |
| Objective | Verify login through the browser interface. |
| Preconditions | Account aarav exists. |
| Test data | aarav / valid password; aarav / wrong password. |
| Steps | 1. POST the login form with wrong credentials.<br>2. POST the login form with valid credentials and follow the redirect. |
| Expected result | Wrong credentials re-display the form with an error (HTTP 401); valid credentials redirect to /dashboard and set an HttpOnly, Secure session cookie. |
| Script | `tests/test_auth.py::test_web_login_form` |

### TC-AUTH-01.8: SQL injection in the username field does not bypass authentication

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-001, APAS-SR-001 |
| Type / Priority | Security / High |
| Objective | Verify that injection strings are treated as data. |
| Preconditions | None. |
| Test data | Classic SQL injection payloads in the username field. |
| Steps | 1. POST /api/auth/login with the injection payload and any password.<br>2. Check that the users table is intact. |
| Expected result | HTTP 401; users table still contains all accounts. |
| Variants | 4: ' OR '1'='1, admin'--, admin" OR ""=", fac.rao; DROP TABLE users |
| Script | `tests/test_auth.py::test_sql_injection_login` |

### TC-AUTH-02.1: Each role receives a role-appropriate dashboard

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-002 |
| Type / Priority | Functional / High |
| Objective | Verify that the dashboard content depends on the authenticated role. |
| Preconditions | admin, fac.rao and aarav accounts exist. |
| Test data | - |
| Steps | 1. GET /api/dashboard as admin, faculty and student. |
| Expected result | Admin sees institution totals; faculty sees assigned subjects and student list; student sees only their own profile and results. |
| Script | `tests/test_auth.py::test_role_specific_dashboards` |

### TC-AUTH-02.2: Users can access only the functions permitted for their role

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-002 |
| Type / Priority | Functional / High |
| Objective | Verify the role/function permission matrix defined in SAD 3.9.2. |
| Preconditions | admin, fac.rao (assigned AM301) and aarav accounts exist. |
| Test data | One request per (role, function) pair; see parameter table. |
| Steps | 1. Authenticate as the role.<br>2. Call the function endpoint. |
| Expected result | Permitted pairs succeed (200/201); all others return HTTP 403. |
| Variants | 17: admin-post-/api/students-new-201, fac.rao-post-/api/students-new-403, aarav-post-/api/students-new-403, fac.rao-post-/api/students/PES1UG24AM006/grades-grade-201, admin-post-/api/students/PES1UG24AM006/grades-grade-403, aarav-post-/api/students/PES1UG24AM006/grades-grade-403, fac.rao-post-/api/students/PES1UG24AM006/attendance-att-201, aarav-post-/api/students/PES1UG24AM006/attendance-att-403, admin-get-/api/audit-None-200, fac.rao-get-/api/audit-None-403, aarav-get-/api/audit-None-403, admin-put-/api/config/thresholds-cfg-200, fac.rao-put-/api/config/thresholds-cfg-403, fac.rao-get-/api/analytics/at-risk-None-200, aarav-get-/api/analytics/at-risk-None-403, aarav-get-/api/analytics/flagged-None-403, aarav-get-/api/students-None-403 |
| Script | `tests/test_auth.py::test_function_permission_matrix` |

### TC-AUTH-03.1: Logout terminates the session token

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-003 |
| Type / Priority | Functional / High |
| Objective | Verify that a token cannot be reused after logout. |
| Preconditions | fac.rao is logged in. |
| Test data | - |
| Steps | 1. GET /api/dashboard with the token (expect 200).<br>2. POST /api/auth/logout.<br>3. GET /api/dashboard again with the same token. |
| Expected result | Step 3 returns HTTP 401 "Authentication required". |
| Script | `tests/test_auth.py::test_api_logout_invalidates_token` |

### TC-AUTH-03.2: Browser logout clears the session and protected pages require login again

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-003 |
| Type / Priority | Functional / High |
| Objective | Verify logout from the web interface. |
| Preconditions | aarav logged in through the login form. |
| Test data | - |
| Steps | 1. Open /dashboard (expect 200, Cache-Control: no-store).<br>2. Submit the Log out form.<br>3. Open /dashboard again. |
| Expected result | After logout the session cookie is cleared and /dashboard redirects to /login. |
| Script | `tests/test_auth.py::test_web_logout_blocks_protected_pages` |

### TC-AUTH-03.3: Idle sessions expire after 30 minutes

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-003 |
| Type / Priority | Functional / High |
| Objective | Verify automatic session termination after inactivity. |
| Preconditions | fac.rao is logged in. |
| Test data | Session last activity set to 31 minutes ago. |
| Steps | 1. Set sessions.last_seen to now - 31 minutes.<br>2. GET /api/dashboard with the token. |
| Expected result | HTTP 401; the expired session is removed. |
| Script | `tests/test_auth.py::test_idle_session_expires` |

### TC-AUTH-03.4: Logout without a session is rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-003 |
| Type / Priority | Functional / High |
| Objective | Verify that logout cannot be called anonymously. |
| Preconditions | - |
| Test data | - |
| Steps | 1. POST /api/auth/logout without a token. |
| Expected result | HTTP 401. |
| Script | `tests/test_auth.py::test_logout_requires_session` |

## Student Academic Record Management


### TC-REC-01.1: Administrator creates a student profile and it is stored correctly

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-004 |
| Type / Priority | Functional / High |
| Objective | Verify profile creation and retrieval. |
| Preconditions | Logged in as admin; PES1UG24AM007 does not exist. |
| Test data | id=PES1UG24AM007, name=Neel Kapoor, email=neel.kapoor@apas.test, semester=1. |
| Steps | 1. POST /api/students with the new profile.<br>2. GET /api/students/PES1UG24AM007.<br>3. Inspect the students table. |
| Expected result | HTTP 201; GET returns identical field values; one row stored in the database. |
| Script | `tests/test_records.py::test_create_and_view_profile` |

### TC-REC-01.2: Administrator updates a student profile

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-004 |
| Type / Priority | Functional / High |
| Objective | Verify that profile updates are saved and timestamps change. |
| Preconditions | Student PES1UG24AM004 exists (semester 3). |
| Test data | name="Ishita R. Rao", current_semester=4. |
| Steps | 1. PUT /api/students/PES1UG24AM004 with the changes.<br>2. GET the profile again. |
| Expected result | HTTP 200; new values returned and persisted; updated_at changed; other fields unchanged. |
| Script | `tests/test_records.py::test_update_profile` |

### TC-REC-01.3: Invalid or incomplete profile data is rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-004 |
| Type / Priority | Functional / High |
| Objective | Verify validation of student profile fields (boundary and invalid values). |
| Preconditions | Logged in as admin. |
| Test data | Invalid IDs, semesters outside 1-8, malformed email, empty/over-long name, unknown field. |
| Steps | 1. POST /api/students with one invalid field. |
| Expected result | HTTP 400 naming the invalid field; no row is created. |
| Variants | 15: id-, id-abc, id-PES 1UG, id-PES1UG24AM001-XYZ-TOO-LONG, id-pes1ug24am007, current_semester-0, current_semester-9, current_semester--1, current_semester-3, current_semester-2.5, current_semester-True, email-not-an-email, name-, name-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, unexpected-1 |
| Script | `tests/test_records.py::test_invalid_profile_rejected` |

### TC-REC-01.4: Duplicate IDs/emails and unknown students are handled

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-004 |
| Type / Priority | Functional / High |
| Objective | Verify conflict and not-found handling for profiles. |
| Preconditions | PES1UG24AM001 exists; PES1UG24AM999 does not. |
| Test data | - |
| Steps | 1. POST a profile reusing id PES1UG24AM001.<br>2. POST a profile reusing aarav's email.<br>3. GET and PUT PES1UG24AM999.<br>4. PUT PES1UG24AM001 with a different id. |
| Expected result | Steps 1-2 HTTP 409; step 3 HTTP 404; step 4 HTTP 400 (ID is immutable). |
| Script | `tests/test_records.py::test_duplicate_and_missing_profiles` |

### TC-REC-02.1: Faculty enters a valid grade and it is saved and displayed

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify grade entry by an authorised faculty member. |
| Preconditions | fac.rao is assigned AM301; PES1UG24AM006 has no grades. |
| Test data | AM301 ISA=42, ESA=45. |
| Steps | 1. POST /api/students/PES1UG24AM006/grades for ISA and ESA.<br>2. GET the grades and the performance summary. |
| Expected result | HTTP 201 for both; stored scores 42 and 45; AM301 percentage 87.00, grade A. |
| Script | `tests/test_records.py::test_enter_grade_and_display` |

### TC-REC-02.2: Faculty updates an existing grade

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify grade updates through POST (upsert) and PUT. |
| Preconditions | Ishita (PES1UG24AM004) has AM302 ESA=25. |
| Test data | ESA 25 -> 40 (POST), then 40 -> 38 (PUT). |
| Steps | 1. POST the AM302 ESA grade with score 40.<br>2. PUT /api/students/PES1UG24AM004/grades/<id> with score 38. |
| Expected result | Step 1 HTTP 200 (updated, not duplicated); step 2 HTTP 200; final score 38 with only one ESA row. |
| Script | `tests/test_records.py::test_update_grade` |

### TC-REC-02.3: Boundary grade values within 0-50 are accepted

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify boundary-value acceptance for assessment scores. |
| Preconditions | fac.rao assigned AM302. |
| Test data | 0, 0.5, 25, 49.5, 50 (max). |
| Steps | 1. POST an ISA grade with the boundary score. |
| Expected result | HTTP 201 and the stored score equals the input. |
| Variants | 5: 0, 0.5, 25, 49.5, 50 |
| Script | `tests/test_records.py::test_valid_boundary_scores` |

### TC-REC-02.4: Invalid grade values are rejected and nothing is stored

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify that out-of-range and non-numeric grades are rejected. |
| Preconditions | fac.rao assigned AM302. |
| Test data | -1, -0.01, 50.01, 51, 100, 1000 (1e3), "45", blank "", null, true, "abc" (TD-04). |
| Steps | 1. POST an ISA grade with the invalid score. |
| Expected result | HTTP 400 with a validation message; grade count unchanged. |
| Variants | 11: -1, -0.01, 50.01, 51, 100, 1000, 45, , None, True, abc |
| Script | `tests/test_records.py::test_invalid_scores_rejected` |

### TC-REC-02.5: Grades for unknown subjects or assessments are rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify referential validation of grade entries. |
| Preconditions | fac.rao logged in. |
| Test data | Unknown subject XX999, unknown assessment "Quiz", missing subject. |
| Steps | 1. POST the grade. |
| Expected result | HTTP 400. |
| Variants | 3: payload0-400, payload1-400, payload2-400 |
| Script | `tests/test_records.py::test_grade_reference_validation` |

### TC-REC-02.6: Grade entry for a non-existent student or with a non-JSON body is rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-005 |
| Type / Priority | Functional / High |
| Objective | Verify error handling for invalid grade requests. |
| Preconditions | - |
| Test data | - |
| Steps | 1. POST a grade for PES1UG24AM999.<br>2. POST plain text instead of JSON. |
| Expected result | Step 1 HTTP 404; step 2 HTTP 400; no server error. |
| Script | `tests/test_records.py::test_grade_unknown_student_and_bad_body` |

### TC-REC-03.1: Attendance percentage matches recorded attendance

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-006 |
| Type / Priority | Functional / High |
| Objective | Verify the automatic attendance percentage calculation. |
| Preconditions | Seeded attendance: Aarav 19/20, Diya 12/20, Rohan 15/20 per subject (3 subjects). |
| Test data | - |
| Steps | 1. GET /api/students/<id>/attendance for each student. |
| Expected result | Aarav 95.00% (57/60), Diya 60.00% (36/60), Rohan 75.00% (45/60), per subject and overall. |
| Script | `tests/test_records.py::test_attendance_percentage_seeded` |

### TC-REC-03.2: Faculty records attendance; corrections update the percentage

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-006 |
| Type / Priority | Functional / High |
| Objective | Verify attendance recording, duplicate-date handling and recalculation. |
| Preconditions | Meera (PES1UG24AM006) has no attendance; fac.rao assigned AM301. |
| Test data | 2026-10-12 present, 10-13 present, 10-14 present, 10-15 absent; then 10-15 corrected to present. |
| Steps | 1. POST four attendance entries.<br>2. POST 2026-10-15 again with status present. |
| Expected result | After step 1 percentage 75.00% (3/4); step 2 returns HTTP 200 (update, not duplicate) and 100.00% (4/4). |
| Script | `tests/test_records.py::test_record_and_correct_attendance` |

### TC-REC-03.3: Invalid attendance entries are rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-006 |
| Type / Priority | Functional / High |
| Objective | Verify validation of attendance status, date and subject. |
| Preconditions | fac.rao assigned AM301. |
| Test data | Invalid statuses, malformed/impossible dates, a future date, unknown subject. |
| Steps | 1. POST the attendance entry with one invalid field. |
| Expected result | HTTP 400; attendance table unchanged. |
| Variants | 14: status-Present, status-P, status-, status-late, status-None, status-1, date-2026-13-01, date-2026-02-30, date-03-08-2026, date-2026/08/03, date-, date-yesterday, date-FUTURE, subject_code-XX999 |
| Script | `tests/test_records.py::test_invalid_attendance_rejected` |

### TC-REC-03.4: Faculty cannot record attendance for a subject they do not teach

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-006 |
| Type / Priority | Functional / High |
| Objective | Verify that only authorised faculty record attendance. |
| Preconditions | fac.iyer is assigned AM303 only. |
| Test data | AM301 attendance for PES1UG24AM006. |
| Steps | 1. POST attendance for AM301 as fac.iyer. |
| Expected result | HTTP 403; no row stored. |
| Script | `tests/test_records.py::test_attendance_unassigned_faculty` |

### TC-REC-03.5: All-absent and all-present attendance give 0% and 100%

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-006 |
| Type / Priority | Functional / High |
| Objective | Verify the edge cases of the percentage calculation (team test data TD-05). |
| Preconditions | Meera (PES1UG24AM006) has no attendance; fac.rao assigned AM302. |
| Test data | 4 sessions (2026-10-12 to 10-15), all with the same status. |
| Steps | 1. POST four attendance entries with the same status. |
| Expected result | 0.00% when all absent; 100.00% when all present; no calculation error. |
| Variants | 2: absent-0.0, present-100.0 |
| Script | `tests/test_records.py::test_attendance_all_absent_or_present` |

## Academic Performance Analysis


### TC-ANA-01.1: Grade-point scale is applied correctly at every boundary

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-007 |
| Type / Priority | Unit / High |
| Objective | Verify the configured 10-point grading rule at boundary values. |
| Preconditions | Scale S>=90, A>=80, B>=70, C>=60, D>=50, E>=40, F<40. |
| Test data | Percentages on and just below each cut-off. |
| Steps | 1. Call the grade calculation for each percentage. |
| Expected result | Each percentage maps to the grade point and letter shown in the parameter table. |
| Variants | 12: 100-10-S, 90-10-S, 89.99-9-A, 80-9-A, 79.99-8-B, 70-8-B, 60-7-C, 59.99-6-D, 50-6-D, 40-5-E, 39.99-0-F, 0-0-F |
| Script | `tests/test_analysis.py::test_grade_scale_boundaries` |

### TC-ANA-01.2: Overall performance (CGPA and overall %) matches the hand calculation

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-007 |
| Type / Priority | Functional / High |
| Objective | Verify the automatic overall academic performance calculation. |
| Preconditions | Seeded grade records for students AM001-AM005. |
| Test data | See EXPECTED table (hand-calculated, credit-weighted). |
| Steps | 1. GET /api/analytics/performance/<student>. |
| Expected result | CGPA and overall percentage equal the hand-calculated values to 2 decimals. |
| Variants | 5: PES1UG24AM001, PES1UG24AM002, PES1UG24AM003, PES1UG24AM004, PES1UG24AM005 |
| Script | `tests/test_analysis.py::test_overall_performance` |

### TC-ANA-01.3: Performance values are recalculated after a grade update

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-007 |
| Type / Priority | Functional / High |
| Objective | Verify that calculations always reflect the stored grades. |
| Preconditions | Ishita (AM004): AM301 60%, AM302 50%, AM303 48%; SGPA 6.09. |
| Test data | AM302 ESA changed 25 -> 40 (AM302 becomes 65% -> C(7)). |
| Steps | 1. POST the updated AM302 ESA grade as fac.rao.<br>2. GET the performance summary. |
| Expected result | SGPA = (4*7 + 4*7 + 3*5)/11 = 6.45; overall = (240+260+144)/11 = 58.55%. |
| Script | `tests/test_analysis.py::test_recalculation_after_grade_change` |

### TC-ANA-01.4: Incomplete subject records are reported but excluded from GPA

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-007 |
| Type / Priority | Functional / High |
| Objective | Verify that incomplete academic records are handled appropriately (SRS 2.5). |
| Preconditions | Meera (AM006) has no grades. |
| Test data | Only AM301 ISA = 40 entered (ESA missing). |
| Steps | 1. POST the ISA grade.<br>2. GET the performance summary. |
| Expected result | AM301 status "incomplete", no grade letter; CGPA and overall % are null; AM301 listed in incomplete_subjects. |
| Script | `tests/test_analysis.py::test_incomplete_records_handled` |

### TC-ANA-01.5: A student with no records produces empty results without errors

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-007 |
| Type / Priority | Functional / High |
| Objective | Verify behaviour when no academic data exists. |
| Preconditions | Meera (AM006) has no grades or attendance. |
| Test data | - |
| Steps | 1. GET /api/analytics/performance/PES1UG24AM006. |
| Expected result | HTTP 200 with empty subject/semester lists and null CGPA/attendance; student not flagged. |
| Script | `tests/test_analysis.py::test_no_records` |

### TC-ANA-02.1: Semester-wise SGPA and percentage match the hand calculation

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-008 |
| Type / Priority | Functional / High |
| Objective | Verify semester-wise performance comparison. |
| Preconditions | Three semesters of grades for AM001-AM003. |
| Test data | See EXPECTED table. |
| Steps | 1. GET /api/analytics/performance/<student>. |
| Expected result | semesters[] lists semesters 1, 2, 3 with the expected SGPA and percentage. |
| Variants | 3: PES1UG24AM001, PES1UG24AM002, PES1UG24AM003 |
| Script | `tests/test_analysis.py::test_semester_wise_analysis` |

### TC-ANA-02.2: Subject-wise results are accurate for every subject

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-008 |
| Type / Priority | Functional / High |
| Objective | Verify subject-wise performance figures. |
| Preconditions | Kabir (AM003) seeded with 9 subjects. |
| Test data | Semester 3: AM301 20+22=42% (E,5), AM302 18+17=35% (F,0), AM303 22+23=45% (E,5). |
| Steps | 1. GET /api/analytics/performance/PES1UG24AM003. |
| Expected result | 9 subjects; semester-3 percentages, grades and grade points as listed. |
| Script | `tests/test_analysis.py::test_subject_wise_analysis` |

### TC-ANA-02.3: Performance trends identify improving and declining students

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-008 |
| Type / Priority | Functional / High |
| Objective | Verify that the semester comparison exposes the trend direction. |
| Preconditions | Aarav improves every semester; Kabir declines every semester. |
| Test data | - |
| Steps | 1. GET /api/analytics/trends/<id> for Aarav and Kabir. |
| Expected result | Aarav SGPA strictly increasing; Kabir SGPA strictly decreasing. |
| Script | `tests/test_analysis.py::test_trend_direction` |

### TC-ANA-03.1: Students below default thresholds are flagged

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-009 |
| Type / Priority | Functional / High |
| Objective | Verify identification of low performance / low attendance. |
| Preconditions | Default thresholds: attendance 75%, performance 50%; a failed subject is also flagged. |
| Test data | Diya attendance 60%; Kabir failed AM302; Rohan exactly 75% attendance and 50% performance (boundary). |
| Steps | 1. GET /api/analytics/flagged as fac.rao. |
| Expected result | Exactly Diya (attendance reasons for AM301-AM303) and Kabir (Failed AM302) are flagged; Rohan is NOT flagged (thresholds are "below"). |
| Script | `tests/test_analysis.py::test_flagged_students_default_thresholds` |

### TC-ANA-03.2: Flagging follows thresholds configured by the administrator

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-009 |
| Type / Priority | Functional / High |
| Objective | Verify that changing the configured thresholds changes the flagged list. |
| Preconditions | Default thresholds. |
| Test data | min_attendance_pct 75 -> 55; min_performance_pct 50 -> 55. |
| Steps | 1. PUT /api/config/thresholds as admin.<br>2. GET /api/analytics/flagged. |
| Expected result | Diya no longer flagged for attendance (60% >= 55%); Kabir (53.73%), Ishita (53.09%) and Rohan (50%) flagged for performance. |
| Script | `tests/test_analysis.py::test_flagging_uses_configured_thresholds` |

### TC-ANA-03.3: Invalid threshold values are rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-009 |
| Type / Priority | Functional / High |
| Objective | Verify validation of threshold configuration. |
| Preconditions | Logged in as admin. |
| Test data | Out-of-range, non-numeric and unknown thresholds. |
| Steps | 1. PUT /api/config/thresholds with the invalid payload. |
| Expected result | HTTP 400; thresholds unchanged. |
| Variants | 5: payload0, payload1, payload2, payload3, payload4 |
| Script | `tests/test_analysis.py::test_invalid_threshold_config` |

## Dashboard and Data Visualisation


### TC-VIS-01.1: Student dashboard shows the student's own grades, attendance and performance

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-010 |
| Type / Priority | Functional / High |
| Objective | Verify dashboard accuracy for the logged-in student. |
| Preconditions | aarav logged in. |
| Test data | Expected CGPA 9.39, overall 86.91%, attendance 95.00%. |
| Steps | 1. GET /api/dashboard as aarav.<br>2. GET /api/dashboard?student_id=PES1UG24AM003 as aarav (attempt to view another student). |
| Expected result | Dashboard shows PES1UG24AM001 with the expected values; the student_id parameter is ignored for students (still own data). |
| Script | `tests/test_dashboard_reports.py::test_student_dashboard_shows_own_data` |

### TC-VIS-01.2: Faculty dashboard for a selected student matches stored records

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-010 |
| Type / Priority | Functional / High |
| Objective | Verify dashboard data for the selected student. |
| Preconditions | fac.rao logged in. |
| Test data | Diya (AM002): CGPA 7.82, overall 70.64%, attendance 60.00%, flagged. |
| Steps | 1. GET /api/dashboard?student_id=PES1UG24AM002.<br>2. GET /dashboard?student_id=PES1UG24AM002 (HTML). |
| Expected result | API and HTML KPIs show CGPA 7.82, overall 70.64, attendance 60.0 and the "Needs attention" flags. |
| Script | `tests/test_dashboard_reports.py::test_faculty_selected_student_dashboard` |

### TC-VIS-01.3: Overview dashboard lists all students with correct flag and risk counts

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-010 |
| Type / Priority | Functional / High |
| Objective | Verify the faculty/admin overview dashboard. |
| Preconditions | 6 seeded students; 2 flagged (Diya, Kabir); 2 at risk (Diya, Kabir). |
| Test data | - |
| Steps | 1. GET /api/dashboard and /dashboard as admin. |
| Expected result | 6 students, flagged_count=2, at_risk_count=2; HTML KPI cards show 6 / 2 / 2. |
| Script | `tests/test_dashboard_reports.py::test_overview_dashboard_counts` |

### TC-VIS-01.4: Dashboard for a non-existent student returns a clear not-found response

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-010 |
| Type / Priority | Functional / High |
| Objective | Verify error handling on the dashboard. |
| Preconditions | - |
| Test data | - |
| Steps | 1. GET /api/dashboard?student_id=PES1UG24AM999 and the HTML equivalent as fac.rao. |
| Expected result | HTTP 404 with "Student not found" (no server error). |
| Script | `tests/test_dashboard_reports.py::test_dashboard_unknown_student` |

### TC-VIS-01.5: Overview dashboard reflects a grade change on the next request (regression for DEF-002 cache)

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-010, APAS-NF-001 |
| Type / Priority | Regression / High |
| Objective | Verify that cached dashboard results are invalidated when academic data changes. |
| Preconditions | Rohan (AM005) not flagged; overview dashboard already loaded once. |
| Test data | Rohan AM302 ESA 25 -> 10 (AM302 becomes 35%, grade F). |
| Steps | 1. GET /api/dashboard as fac.rao (warms the cache).<br>2. POST the new grade.<br>3. GET /api/dashboard again. |
| Expected result | Step 1 flagged_count 2; step 3 flagged_count 3 with Rohan flagged for "Failed AM302 (35.0%)". |
| Script | `tests/test_dashboard_reports.py::test_overview_reflects_changes_immediately` |

### TC-VIS-02.1: Bar charts represent the stored subject percentages accurately

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-011 |
| Type / Priority | Functional / High |
| Objective | Verify that bar chart values and bar heights match the data. |
| Preconditions | fac.rao logged in; Kabir semester-3 scores 42%, 35%, 45%; attendance 80% each. |
| Test data | - |
| Steps | 1. GET /api/analytics/trends/PES1UG24AM003.<br>2. Render /dashboard?student_id=PES1UG24AM003 and read the SVG bars. |
| Expected result | One bar per subject; data-value equals the API percentage; bar height = value x 1.6 px (160 px plot area for 100%). |
| Script | `tests/test_dashboard_reports.py::test_bar_chart_matches_data` |

### TC-VIS-02.2: Line graph plots the semester SGPA trend correctly

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-011 |
| Type / Priority | Functional / High |
| Objective | Verify the SGPA line graph against calculated SGPA values. |
| Preconditions | Aarav SGPA 9.09, 9.36, 9.73. |
| Test data | - |
| Steps | 1. Render /dashboard?student_id=PES1UG24AM001 and read the line-graph points. |
| Expected result | Three points in semester order with data-value = SGPA; y = 200 - 16 x SGPA (higher SGPA plotted higher). |
| Script | `tests/test_dashboard_reports.py::test_line_graph_matches_sgpa_trend` |

### TC-VIS-02.3: Charts reflect newly recorded data

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-011 |
| Type / Priority | Functional / High |
| Objective | Verify that visualisations are generated from current data. |
| Preconditions | Kabir AM302 ISA=18, ESA=17 (35%). |
| Test data | AM302 ESA updated to 32 -> 50%. |
| Steps | 1. POST the new grade as fac.rao.<br>2. Render Kabir's dashboard. |
| Expected result | AM302 bar shows 50.0 with height 80 px. |
| Script | `tests/test_dashboard_reports.py::test_charts_update_after_change` |

### TC-VIS-02.4: Dashboards without data show a message instead of an empty chart

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-011 |
| Type / Priority | Functional / High |
| Objective | Verify chart behaviour when there is no data. |
| Preconditions | Meera (AM006) has no records. |
| Test data | - |
| Steps | 1. Render /dashboard?student_id=PES1UG24AM006. |
| Expected result | HTTP 200; no chart SVGs; "No data recorded yet" / "No completed semesters yet" messages. |
| Script | `tests/test_dashboard_reports.py::test_chart_without_data` |

## Report Generation


### TC-REP-01.1: Faculty generates and downloads an accurate CSV report

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-012 |
| Type / Priority | Functional / High |
| Objective | Verify report generation, content accuracy and download headers. |
| Preconditions | fac.rao logged in; Aarav records seeded. |
| Test data | student_id=PES1UG24AM001, format=csv. |
| Steps | 1. POST /api/reports.<br>2. Parse the CSV. |
| Expected result | HTTP 200, text/csv, Content-Disposition attachment named APAS_Report_PES1UG24AM001_<date>.csv; 9 subject rows; CGPA 9.39; overall 86.91; attendance 57/60 = 95.0. |
| Script | `tests/test_dashboard_reports.py::test_generate_csv_report` |

### TC-REP-01.2: Reports include threshold flags and are available as JSON

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-012 |
| Type / Priority | Functional / High |
| Objective | Verify report summaries for a flagged student and JSON format. |
| Preconditions | admin logged in; Kabir failed AM302. |
| Test data | - |
| Steps | 1. POST /api/reports for Kabir in CSV and JSON formats. |
| Expected result | CSV "Flags" row contains "Failed AM302 (35.0%)"; JSON report contains the same CGPA 5.52 and a .json attachment name. |
| Script | `tests/test_dashboard_reports.py::test_report_contains_flags_and_json` |

### TC-REP-01.3: Report requests are validated and restricted to permitted students

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-012 |
| Type / Priority | Functional / High |
| Objective | Verify report authorisation and input validation. |
| Preconditions | aarav (student), fac.rao logged in. |
| Test data | - |
| Steps | 1. aarav requests own report (no student_id).<br>2. aarav requests Kabir's report.<br>3. fac.rao requests a report for PES1UG24AM999.<br>4. fac.rao requests format "pdf". |
| Expected result | 1 -> 200 (own report); 2 -> 403; 3 -> 404; 4 -> 400. |
| Script | `tests/test_dashboard_reports.py::test_report_access_and_validation` |

## Predictive Analytics, Risk Identification and Insights


### TC-PRED-01.1: Predictions are generated for students with sufficient history

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-013 |
| Type / Priority | Functional / High |
| Objective | Verify predicted SGPA, trend and confidence against the hand calculation. |
| Preconditions | Three completed semesters for AM001-AM003; fac.rao logged in. |
| Test data | Expected values in the parameter table (Aarav's prediction is clipped at the 10.0 maximum). |
| Steps | 1. GET /api/analytics/predictions/<student>. |
| Expected result | status "ok", predicted semester 4, predicted SGPA/trend/confidence as expected. |
| Variants | 3: PES1UG24AM001-10.0-improving-medium, PES1UG24AM002-8.09-improving-medium, PES1UG24AM003-1.33-declining-medium |
| Script | `tests/test_prediction.py::test_prediction_for_students_with_history` |

### TC-PRED-01.2: Students without sufficient history get an explicit 'insufficient data' result

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-013 |
| Type / Priority | Functional / High |
| Objective | Verify that no prediction is fabricated when history is insufficient. |
| Preconditions | AM004/AM005 have one semester; AM006 has none. |
| Test data | - |
| Steps | 1. GET /api/analytics/predictions/<student>. |
| Expected result | status "insufficient_data", predicted_sgpa null, explanatory message. |
| Variants | 3: PES1UG24AM004, PES1UG24AM005, PES1UG24AM006 |
| Script | `tests/test_prediction.py::test_prediction_insufficient_history` |

### TC-PRED-01.3: Only faculty and administrators can retrieve predictions

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-013 |
| Type / Priority | Functional / High |
| Objective | Verify role restrictions on predictions (SRS stakeholders: Faculty, Administrator). |
| Preconditions | - |
| Test data | - |
| Steps | 1. GET /api/analytics/predictions/PES1UG24AM001 as aarav (own record) and as fac.rao. |
| Expected result | Student -> 403; faculty -> 200. |
| Script | `tests/test_prediction.py::test_prediction_access` |

### TC-PRED-01.4: Back-test the prediction method on a synthetic cohort

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-013 |
| Type / Priority | Predictive Evaluation / High |
| Objective | Evaluate prediction error and risk classification using hold-out data. |
| Preconditions | 300 synthetic students with 3 semesters of grades (seed 2026). |
| Test data | Semesters 1-2 used as history; actual semester-3 SGPA held out. |
| Steps | 1. Generate the synthetic cohort.<br>2. Predict semester-3 SGPA from semesters 1-2 for each student.<br>3. Compare with the actual semester-3 SGPA; classify "at risk" as SGPA < 6.0. |
| Expected result | A prediction is produced for 100% of eligible students, every prediction lies in [0, 10]; MAE, RMSE, precision and recall are recorded in results/prediction_evaluation.json. |
| Limitation | Evaluation uses a synthetic cohort; results describe the method's behaviour, not real-world accuracy. No accuracy threshold is asserted because the SRS does not define one (STP 15.1). |
| Script | `tests/test_prediction.py::test_prediction_backtest` |

### TC-PRED-02.1: Students meeting the risk criteria appear in the academic risk list

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-014 |
| Type / Priority | Functional / High |
| Objective | Verify at-risk classification with default risk criteria. |
| Preconditions | Default criteria: high if predicted SGPA < 5 or attendance < 65%; medium if predicted SGPA < 6 or attendance < 75%. |
| Test data | Kabir predicted 1.33 (high); Diya attendance 60% (high); Aarav, Ishita, Rohan (75% boundary), Meera low. |
| Steps | 1. GET /api/analytics/at-risk as fac.rao. |
| Expected result | Exactly Diya and Kabir, both "high", with their risk factors; Rohan at exactly 75% is not listed. |
| Script | `tests/test_prediction.py::test_at_risk_list` |

### TC-PRED-02.2: Changing the predefined risk criteria changes the classification

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-014 |
| Type / Priority | Functional / High |
| Objective | Verify that risk levels follow the configured criteria. |
| Preconditions | - |
| Test data | risk_high_attendance_pct 65 -> 55 (Diya 60% now medium); risk_medium_sgpa 6 -> 8.5 (Diya predicted 8.09 -> medium). |
| Steps | 1. PUT /api/config/thresholds as admin.<br>2. GET /api/analytics/at-risk. |
| Expected result | Diya listed as "medium"; Kabir still "high". |
| Script | `tests/test_prediction.py::test_risk_criteria_configurable` |

### TC-PRED-03.1: Recommendations address the identified weaknesses and risk factors

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-015 |
| Type / Priority | Functional / Medium |
| Objective | Verify that insights are relevant to the student's weaknesses. |
| Preconditions | Kabir: AM301 42%, AM302 35% (failed), AM303 45%, declining SGPA, predicted 1.33. |
| Test data | - |
| Steps | 1. GET /api/analytics/insights/PES1UG24AM003 as fac.rao. |
| Expected result | critical recommendation for AM302; academic recommendations for AM301 and AM303; one trend and one risk recommendation; no attendance recommendation (80%). |
| Script | `tests/test_prediction.py::test_insights_for_weak_student` |

### TC-PRED-03.2: Attendance recommendations for low attendance; positive message when on track

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-015 |
| Type / Priority | Functional / Medium |
| Objective | Verify insight rules for attendance and for students without weaknesses. |
| Preconditions | - |
| Test data | - |
| Steps | 1. GET /api/analytics/insights for Diya and Aarav. |
| Expected result | Diya -> one attendance recommendation per subject; Aarav -> a single "on track" message. |
| Variants | 2: PES1UG24AM002-expected0, PES1UG24AM001-expected1 |
| Script | `tests/test_prediction.py::test_insights_attendance_and_positive` |

### TC-PRED-03.3: Students can see their own insights but not another student's

| Field | Detail |
|---|---|
| Requirement(s) | APAS-F-015 |
| Type / Priority | Functional / Medium |
| Objective |  |
| Preconditions | - |
| Test data | - |
| Steps | 1. GET /api/analytics/insights/PES1UG24AM003 as kabir and as aarav. |
| Expected result | kabir -> 200; aarav -> 403. |
| Script | `tests/test_prediction.py::test_student_sees_own_insights_only` |

## Security


### TC-SEC-01.1: Every protected endpoint rejects unauthenticated requests

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-001, APAS-NF-003 |
| Type / Priority | Security / High |
| Objective | Verify that academic information cannot be accessed without valid credentials. |
| Preconditions | No session. |
| Test data | All 20 protected API operations (SAD 4.3.1) and the /dashboard page. |
| Steps | 1. Call each protected operation without a token.<br>2. Open /dashboard without a session. |
| Expected result | Every API call returns HTTP 401 with no academic data; /dashboard redirects to /login. |
| Script | `tests/test_security.py::test_protected_endpoints_require_authentication` |

### TC-SEC-01.2: Forged, malformed or tampered tokens are rejected

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-001, APAS-NF-003 |
| Type / Priority | Security / High |
| Objective | Verify that only server-issued session tokens grant access. |
| Preconditions | - |
| Test data | Random token, empty bearer, HTTP Basic credentials, SQL injection string, a valid token with one character changed. |
| Steps | 1. GET /api/dashboard with the forged Authorization header. |
| Expected result | HTTP 401. |
| Variants | 5: Bearer invalidtoken, Bearer , Basic YWRtaW46QWRtaW5AQVBBUzIwMjY=, Bearer ' OR '1'='1, TAMPER |
| Script | `tests/test_security.py::test_forged_tokens_rejected` |

### TC-SEC-02.1: A student cannot access another student's academic records

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-002 |
| Type / Priority | Security / High |
| Objective | Verify horizontal access control between students. |
| Preconditions | aarav (PES1UG24AM001) logged in. |
| Test data | Requests for Kabir (PES1UG24AM003). |
| Steps | 1. Call the endpoint for the other student. |
| Expected result | HTTP 403; the response contains none of Kabir's data. |
| Variants | 7: get-/api/students/PES1UG24AM003-None, get-/api/students/PES1UG24AM003/grades-None, get-/api/students/PES1UG24AM003/attendance-None, get-/api/analytics/performance/PES1UG24AM003-None, get-/api/analytics/trends/PES1UG24AM003-None, get-/api/analytics/insights/PES1UG24AM003-None, post-/api/reports-body6 |
| Script | `tests/test_security.py::test_student_cannot_read_other_student` |

### TC-SEC-02.2: Faculty cannot change grades of subjects they are not assigned to

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-002 |
| Type / Priority | Security / High |
| Objective | Verify record-level authorisation for grade changes. |
| Preconditions | fac.iyer assigned AM103/AM203/AM303 only. Kabir AM301 ISA = 20. |
| Test data | fac.iyer sets Kabir AM301 ISA to 50 via POST and via PUT. |
| Steps | 1. POST the grade as fac.iyer.<br>2. PUT /api/students/PES1UG24AM003/grades/<id> as fac.iyer.<br>3. Read the grade from the database. |
| Expected result | Both requests HTTP 403; stored score still 20. |
| Script | `tests/test_security.py::test_faculty_limited_to_assigned_subjects` |

### TC-SEC-02.3: Students cannot escalate privileges through crafted requests

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-002 |
| Type / Priority | Security / High |
| Objective | Verify server-side enforcement independent of the UI. |
| Preconditions | aarav logged in. |
| Test data | Self-grade change, profile edit, threshold change, audit read. |
| Steps | 1. aarav POSTs a grade of 50 for himself.<br>2. aarav PUTs his own profile.<br>3. aarav PUTs thresholds and GETs /api/audit. |
| Expected result | All HTTP 403; database unchanged. |
| Script | `tests/test_security.py::test_privilege_escalation_attempts` |

### TC-SEC-03.1: Plain-HTTP requests are redirected (GET) or rejected (state-changing)

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-003 |
| Type / Priority | Security / High |
| Objective | Verify that insecure connections are not served. |
| Preconditions | Production configuration (ENFORCE_HTTPS = True). |
| Test data | - |
| Steps | 1. GET http://localhost/dashboard.<br>2. POST http://localhost/api/auth/login.<br>3. GET https://localhost/api/health. |
| Expected result | Step 1 HTTP 301 to https://; step 2 HTTP 403 "HTTPS is required"; step 3 includes Strict-Transport-Security max-age >= 1 year; login cookie has the Secure flag. |
| Script | `tests/test_security.py::test_insecure_http_redirected_or_rejected` |

### TC-SEC-03.2: Server negotiates TLS 1.2/1.3 and refuses TLS 1.0/1.1

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-003 |
| Type / Priority | Security / High |
| Objective | Verify the minimum TLS version on a real socket. |
| Preconditions | APAS served over HTTPS with make_ssl_context (minimum TLS 1.2), self-signed certificate. |
| Test data | Client handshakes pinned to TLS 1.0, 1.1, 1.2 and 1.3. |
| Steps | 1. Start the HTTPS server.<br>2. Attempt a handshake with each protocol version. |
| Expected result | TLS 1.2 and 1.3 handshakes succeed; TLS 1.0 and 1.1 handshakes fail. |
| Limitation | Executed against the local test server; the deployed environment's TLS configuration must be re-checked (e.g. SSL Labs / testssl.sh) once a hosting platform is chosen (SAD 4.6.1 open issue 3). |
| Script | `tests/test_security.py::test_tls_protocol_versions` |

### TC-SEC-03.3: A client-supplied X-Forwarded-Proto header cannot bypass HTTPS enforcement

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-003 |
| Type / Priority | Security / High |
| Objective | Verify that plain-HTTP requests are not accepted just because the client claims HTTPS. |
| Preconditions | Production configuration; no reverse proxy configured. |
| Test data | Plain-HTTP requests carrying "X-Forwarded-Proto: https". |
| Steps | 1. GET http://localhost/dashboard with the spoofed header.<br>2. POST http://localhost/api/auth/login with the spoofed header and valid credentials. |
| Expected result | Step 1 HTTP 301 to https://; step 2 HTTP 403 "HTTPS is required" (credentials never accepted over plain HTTP). |
| Script | `tests/test_security.py::test_spoofed_forwarded_proto_not_trusted` |

### TC-SEC-04.1: Passwords are stored as salted PBKDF2 hashes, never in plaintext

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-004 |
| Type / Priority | Security / High |
| Objective | Verify password storage in the users table and the raw database file. |
| Preconditions | 9 seeded accounts. |
| Test data | - |
| Steps | 1. Read users.password_hash for every account.<br>2. Search the raw database file bytes for each plaintext password. |
| Expected result | Every hash uses pbkdf2:sha256 with >= 600000 iterations and a salt; no hash equals or contains the plaintext; no plaintext password occurs anywhere in the database file. |
| Script | `tests/test_security.py::test_passwords_hashed_not_plaintext` |

### TC-SEC-04.2: Identical passwords produce different hashes; verification works

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-004 |
| Type / Priority | Security / High |
| Objective | Verify per-user salting and correct password verification. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Hash the same password twice.<br>2. Verify the correct and an incorrect password against the hash. |
| Expected result | The two hashes differ; correct password verifies True; incorrect verifies False. |
| Script | `tests/test_security.py::test_hash_salting_and_verification` |

### TC-SEC-04.3: Password hashes are never exposed by the API

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-004 |
| Type / Priority | Security / High |
| Objective | Verify that no API response contains password data. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Log in and call dashboard, student and audit endpoints as admin. |
| Expected result | No response body contains "password_hash", "pbkdf2" or a plaintext password. |
| Script | `tests/test_security.py::test_password_never_returned` |

### TC-SEC-05.1: Successful and failed login attempts are logged with user, event type and timestamp

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-005 |
| Type / Priority | Security / High |
| Objective | Verify security logging of authentication events. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Log in successfully as fac.rao.<br>2. Fail a login for fac.rao (wrong password) and for unknown user "ghost".<br>3. Read the audit log. |
| Expected result | Three auth.login entries: success (fac.rao, user id), failure (fac.rao, "wrong password"), failure (ghost, "unknown user"); each with an ISO-8601 UTC timestamp within 60 s of now. |
| Script | `tests/test_security.py::test_login_attempts_logged` |

### TC-SEC-05.2: Academic record changes and denied access attempts are logged

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-005 |
| Type / Priority | Security / High |
| Objective | Verify security logging of record modifications and authorisation failures. |
| Preconditions | - |
| Test data | - |
| Steps | 1. fac.rao updates Kabir AM301 ISA 20 -> 25.<br>2. aarav tries to read Kabir's grades.<br>3. Read the audit log. |
| Expected result | grade.update entry with user fac.rao, entity PES1UG24AM003, old 20, new 25; access.denied entry for aarav with the requested path. |
| Script | `tests/test_security.py::test_modifications_and_denials_logged` |

### TC-SEC-05.3: Passwords and session tokens are never written to the audit log

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-005 |
| Type / Priority | Security / High |
| Objective | Verify SAD 4.4.2 (sensitive authentication information must not be logged). |
| Preconditions | - |
| Test data | - |
| Steps | 1. Perform successful and failed logins.<br>2. Search all audit_log columns for passwords and the issued token. |
| Expected result | No password or token text appears in the audit log. |
| Script | `tests/test_security.py::test_no_secrets_in_logs` |

### TC-SEC-05.4: Malicious path parameters are handled safely

| Field | Detail |
|---|---|
| Requirement(s) | APAS-SR-005, APAS-NF-003 |
| Type / Priority | Security / High |
| Objective | Verify input validation does not cause errors or data exposure (STP 5.6 Input Validation). |
| Preconditions | - |
| Test data | Path traversal, SQL injection and script injection in the student ID. |
| Steps | 1. GET the URL as fac.rao. |
| Expected result | HTTP 404 "Student not found" (no HTTP 500, no stack trace). |
| Variants | 3: /api/students/..%2F..%2Fetc%2Fpasswd, /api/students/PES1'%20OR%20'1'='1, /api/analytics/performance/%3Cscript%3E |
| Script | `tests/test_security.py::test_malicious_input_handled_safely` |

## Performance


### TC-PERF-01.1: Dashboards load within 3 seconds for at least 95% of requests

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-001 |
| Type / Priority | Performance / High |
| Objective | Measure dashboard response time under normal load. |
| Preconditions | Seeded data plus 300 synthetic students (306 total, ~42 000 grade/attendance rows); APAS on a real HTTPS socket. |
| Test data | 300 requests, 50 concurrent clients (TD-12), mix of admin/faculty overview dashboards, student dashboards and HTML dashboards. |
| Steps | 1. Add 300 synthetic students to the database.<br>2. Start the HTTPS server and log in as admin, fac.rao and aarav.<br>3. Send 300 dashboard requests from 50 worker threads; time each request end-to-end.<br>4. Compute the 95th-percentile response time overall and per dashboard type. |
| Expected result | All requests HTTP 200; 95th percentile <= 3.0 s overall and for every dashboard type. |
| Limitation | 'Normal operating conditions' are not quantified in the SRS; load profile taken from team test data TD-12 (50 concurrent users), cohort of 306 students, single developer laptop. Repeat on the deployment infrastructure. |
| Script | `tests/test_nonfunctional.py::test_dashboard_response_time` |

### TC-PERF-01.2: Dashboards stay within 3 seconds while faculty are updating grades

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-001 |
| Type / Priority | Performance / High |
| Objective | Verify NF-001 when cached dashboard results are constantly invalidated by data changes. |
| Preconditions | 306 students; APAS on a real HTTPS socket. |
| Test data | 300 operations from 50 concurrent clients (TD-12); every 10th operation is a grade update by fac.rao (forces recomputation); the rest are admin/faculty overview dashboards. |
| Steps | 1. Add 300 synthetic students and start the server.<br>2. Run the mixed workload and time each dashboard request. |
| Expected result | All requests succeed; dashboard 95th percentile <= 3.0 s. |
| Limitation | Same load assumptions as TC-PERF-01.1. Write rate (1 grade update per 10 requests) is an assumption representing faculty entering marks while others view dashboards. |
| Script | `tests/test_nonfunctional.py::test_dashboard_response_time_with_updates` |

## Reliability


### TC-REL-01.1: Service stays available while receiving malformed and hostile requests

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-002 |
| Type / Priority | Reliability / High |
| Objective | Estimate availability during a soak test with injected faulty requests. |
| Preconditions | APAS on a real HTTPS socket. |
| Test data | 400 health probes interleaved with malformed JSON, oversized bodies, unknown routes and invalid methods. |
| Steps | 1. Start the server.<br>2. Send 400 /api/health probes; after every probe send one faulty request.<br>3. Availability = successful probes / total probes. |
| Expected result | Availability >= 99% in the window; faulty requests receive 4xx responses (never 5xx, never a dropped connection). |
| Limitation | Monthly availability (>= 99%) can only be confirmed by monitoring a deployed instance for a full calendar month (tools/availability_monitor.py). This run covers a short soak test with fault injection. |
| Script | `tests/test_nonfunctional.py::test_availability_under_faults` |

### TC-REL-01.2: An internal failure returns a generic error and the service keeps running

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-002 |
| Type / Priority | Reliability / High |
| Objective | Verify graceful handling of unexpected server-side errors (SAD 4.4.1). |
| Preconditions | Logged in as fac.rao. |
| Test data | The subjects table is dropped to simulate a database failure. |
| Steps | 1. Drop the subjects table.<br>2. GET /api/analytics/performance/PES1UG24AM001.<br>3. GET /api/health. |
| Expected result | Step 2 HTTP 500 with "An unexpected error occurred" and no SQL/stack-trace details; step 3 HTTP 200. |
| Script | `tests/test_nonfunctional.py::test_unexpected_error_contained` |

## Audit Logging and Retention


### TC-AUD-01.1: Every academic record modification is logged with user ID, timestamp and details

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-004 |
| Type / Priority | Audit / High |
| Objective | Verify audit coverage of profile, grade, attendance and configuration changes. |
| Preconditions | - |
| Test data | - |
| Steps | 1. admin creates and updates a student profile, and changes a threshold.<br>2. fac.rao creates a grade, updates it, records and corrects attendance.<br>3. GET /api/audit as admin. |
| Expected result | Entries student.create, student.update, config.update, grade.create, grade.update, attendance.create, attendance.update — each with user_id, username, ISO timestamp and old/new values. |
| Script | `tests/test_nonfunctional.py::test_record_modifications_logged` |

### TC-AUD-01.2: Audit records are retained for at least 12 months

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-004 |
| Type / Priority | Audit / High |
| Objective | Verify the retention policy and its 12-month minimum. |
| Preconditions | - |
| Test data | Entries aged 30 days, 11 months 29 days, 12 months + 2 days, 13 months, 24 months. |
| Steps | 1. Insert the aged entries.<br>2. Run the purge with retention 12 months; check what remains.<br>3. Re-insert and run the purge with a mis-configured retention of 6 months.<br>4. Run the purge with retention 18 months. |
| Expected result | Step 2 keeps the 30-day and 11m29d entries and removes the older three; step 3 behaves like 12 months (minimum enforced); step 4 keeps everything younger than 18 months (30d, 11m29d, 12m2d, 13m). |
| Script | `tests/test_nonfunctional.py::test_audit_retention_minimum_12_months` |

### TC-AUD-01.3: Audit records cannot be modified

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-004 |
| Type / Priority | Audit / High |
| Objective | Verify that audit logs are protected against modification (SAD 3.9.6). |
| Preconditions | - |
| Test data | - |
| Steps | 1. Attempt an UPDATE on audit_log directly in the database.<br>2. Attempt PUT and DELETE on /api/audit as admin. |
| Expected result | Database rejects the UPDATE ("audit_log is append-only"); API returns HTTP 405 for both. |
| Script | `tests/test_nonfunctional.py::test_audit_log_tamper_protection` |

### TC-AUD-01.4: Audit entries can be retrieved and filtered by an administrator

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-004 |
| Type / Priority | Audit / High |
| Objective | Verify that logs can be retrieved for investigation. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Generate a grade.update entry for PES1UG24AM003.<br>2. GET /api/audit?event_type=grade.update&entity=PES1UG24AM003 as admin. |
| Expected result | Only matching entries are returned, newest first. |
| Script | `tests/test_nonfunctional.py::test_audit_log_retrieval` |

## Usability and Accessibility


### TC-UX-01.1: Pages provide labels, landmarks, skip link and a logical keyboard order

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-005 |
| Type / Priority | Accessibility / Medium |
| Objective | Automated checks for WCAG 2.1 AA criteria 1.1.1, 1.3.1, 2.1.1, 2.4.1, 2.4.3, 3.1.1, 3.3.2, 4.1.2. |
| Preconditions | Login page, student dashboard (charts), admin overview dashboard. |
| Test data | - |
| Steps | 1. Render each page.<br>2. Check: html lang, labelled inputs, no positive tabindex, SVG charts with role="img" and an accessible name, tables with caption and scoped headers, skip link as first focusable element. |
| Expected result | No problems reported on any page. |
| Script | `tests/test_nonfunctional.py::test_pages_structure_and_keyboard_access` |

### TC-UX-01.2: Form errors are announced to assistive technology

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-005 |
| Type / Priority | Accessibility / Medium |
| Objective | Verify WCAG 3.3.1 (error identification) and 4.1.3 (status messages) on the login form. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Submit the login form with empty fields and with wrong credentials. |
| Expected result | Error text is shown in an element with role="alert" and linked to the username field via aria-describedby. |
| Script | `tests/test_nonfunctional.py::test_error_messages_announced` |

### TC-UX-01.3: Text and UI colours meet WCAG 2.1 AA contrast ratios

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-005 |
| Type / Priority | Accessibility / Medium |
| Objective | Verify WCAG 1.4.3 (text >= 4.5:1) and 1.4.11 (non-text UI and graphics >= 3:1). |
| Preconditions | - |
| Test data | Colour tokens from apas/static/style.css. |
| Steps | 1. Read the CSS custom properties.<br>2. Compute the contrast ratio of every foreground/background pair used by the UI. |
| Expected result | All text pairs >= 4.5:1; all non-text pairs (borders, focus ring, chart marks) >= 3:1. |
| Script | `tests/test_nonfunctional.py::test_colour_contrast` |

### TC-UX-01.4: Keyboard focus is visible and layout reflows at narrow widths

| Field | Detail |
|---|---|
| Requirement(s) | APAS-NF-005 |
| Type / Priority | Accessibility / Medium |
| Objective | Verify WCAG 2.4.7 (focus visible) and 1.4.10 (reflow) support in the stylesheet. |
| Preconditions | - |
| Test data | - |
| Steps | 1. Inspect apas/static/style.css and base.html. |
| Expected result | A :focus-visible outline of at least 2px is defined; the skip link becomes visible on focus; viewport meta is present; tables are wrapped for horizontal scrolling instead of page overflow. |
| Script | `tests/test_nonfunctional.py::test_focus_visible_and_reflow` |
