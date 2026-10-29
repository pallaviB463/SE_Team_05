"""TC-REC: Student profiles, grades and attendance (APAS-F-004 .. APAS-F-006)."""
from datetime import date, timedelta

import pytest

from conftest import TEST_DATA

tc = pytest.mark.tc
BV = TEST_DATA["boundary_values"]
NEW_STUDENT = {"id": "PES1UG24AM007", "name": "Neel Kapoor", "email": "neel.kapoor@apas.test",
               "program": "B.Tech CSE (AI & ML)", "current_semester": 1}


# --------------------------------------------------------------------------
# APAS-F-004 student academic profiles
# --------------------------------------------------------------------------
@tc("TC-REC-01.1", "APAS-F-004")
def test_create_and_view_profile(client, login, db, record):
    """Administrator creates a student profile and it is stored correctly
    Objective: Verify profile creation and retrieval.
    Preconditions: Logged in as admin; PES1UG24AM007 does not exist.
    Test data: id=PES1UG24AM007, name=Neel Kapoor, email=neel.kapoor@apas.test, semester=1.
    Steps:
    1. POST /api/students with the new profile.
    2. GET /api/students/PES1UG24AM007.
    3. Inspect the students table.
    Expected: HTTP 201; GET returns identical field values; one row stored in the database.
    """
    h = login("admin")
    resp = client.post("/api/students", headers=h, json=NEW_STUDENT)
    assert resp.status_code == 201
    got = client.get("/api/students/PES1UG24AM007", headers=h).get_json()
    assert {k: got[k] for k in NEW_STUDENT} == NEW_STUDENT
    row = db.execute("SELECT * FROM students WHERE id = 'PES1UG24AM007'").fetchone()
    assert row["email"] == NEW_STUDENT["email"]
    record(f"create HTTP 201; GET returned {{{', '.join(f'{k}={got[k]}' for k in NEW_STUDENT)}}}; DB row present")


@tc("TC-REC-01.2", "APAS-F-004")
def test_update_profile(client, login, db, record):
    """Administrator updates a student profile
    Objective: Verify that profile updates are saved and timestamps change.
    Preconditions: Student PES1UG24AM004 exists (semester 3).
    Test data: name="Ishita R. Rao", current_semester=4.
    Steps:
    1. PUT /api/students/PES1UG24AM004 with the changes.
    2. GET the profile again.
    Expected: HTTP 200; new values returned and persisted; updated_at changed; other fields unchanged.
    """
    h = login("admin")
    before = client.get("/api/students/PES1UG24AM004", headers=h).get_json()
    resp = client.put("/api/students/PES1UG24AM004", headers=h,
                      json={"name": "Ishita R. Rao", "current_semester": 4})
    after = client.get("/api/students/PES1UG24AM004", headers=h).get_json()
    assert resp.status_code == 200
    assert after["name"] == "Ishita R. Rao" and after["current_semester"] == 4
    assert after["email"] == before["email"] and after["updated_at"] != before["updated_at"]
    record(f"HTTP 200; name '{before['name']}' -> '{after['name']}', semester {before['current_semester']} -> "
           f"{after['current_semester']}; updated_at changed")


@tc("TC-REC-01.3", "APAS-F-004")
@pytest.mark.parametrize("field,value", [("id", v) for v in BV["student_id_invalid"]] +
                         [("current_semester", v) for v in BV["semester_invalid"]] +
                         [("email", "not-an-email"), ("name", ""), ("name", "x" * 101), ("unexpected", 1)])
def test_invalid_profile_rejected(client, login, db, record, field, value):
    """Invalid or incomplete profile data is rejected
    Objective: Verify validation of student profile fields (boundary and invalid values).
    Preconditions: Logged in as admin.
    Test data: Invalid IDs, semesters outside 1-8, malformed email, empty/over-long name, unknown field.
    Steps:
    1. POST /api/students with one invalid field.
    Expected: HTTP 400 naming the invalid field; no row is created.
    """
    h = login("admin")
    payload = dict(NEW_STUDENT, **{field: value})
    resp = client.post("/api/students", headers=h, json=payload)
    assert resp.status_code == 400
    assert db.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 6
    record(f"{field}={value!r} -> HTTP 400 {resp.get_json().get('fields')}")


@tc("TC-REC-01.4", "APAS-F-004")
def test_duplicate_and_missing_profiles(client, login, record):
    """Duplicate IDs/emails and unknown students are handled
    Objective: Verify conflict and not-found handling for profiles.
    Preconditions: PES1UG24AM001 exists; PES1UG24AM999 does not.
    Steps:
    1. POST a profile reusing id PES1UG24AM001.
    2. POST a profile reusing aarav's email.
    3. GET and PUT PES1UG24AM999.
    4. PUT PES1UG24AM001 with a different id.
    Expected: Steps 1-2 HTTP 409; step 3 HTTP 404; step 4 HTTP 400 (ID is immutable).
    """
    h = login("admin")
    dup_id = client.post("/api/students", headers=h, json=dict(NEW_STUDENT, id="PES1UG24AM001"))
    dup_mail = client.post("/api/students", headers=h, json=dict(NEW_STUDENT, email="aarav.sharma@apas.test"))
    missing_get = client.get("/api/students/PES1UG24AM999", headers=h)
    missing_put = client.put("/api/students/PES1UG24AM999", headers=h, json={"name": "X"})
    change_id = client.put("/api/students/PES1UG24AM001", headers=h, json={"id": "PES1UG24AM777"})
    codes = [r.status_code for r in (dup_id, dup_mail, missing_get, missing_put, change_id)]
    assert codes == [409, 409, 404, 404, 400]
    record(f"duplicate id/email/missing GET/missing PUT/change id -> {codes}")


# --------------------------------------------------------------------------
# APAS-F-005 grades
# --------------------------------------------------------------------------
@tc("TC-REC-02.1", "APAS-F-005")
def test_enter_grade_and_display(client, login, record):
    """Faculty enters a valid grade and it is saved and displayed
    Objective: Verify grade entry by an authorised faculty member.
    Preconditions: fac.rao is assigned AM301; PES1UG24AM006 has no grades.
    Test data: AM301 ISA=42, ESA=45.
    Steps:
    1. POST /api/students/PES1UG24AM006/grades for ISA and ESA.
    2. GET the grades and the performance summary.
    Expected: HTTP 201 for both; stored scores 42 and 45; AM301 percentage 87.00, grade A.
    """
    h = login("fac.rao")
    r1 = client.post("/api/students/PES1UG24AM006/grades", headers=h,
                     json={"subject_code": "AM301", "assessment": "ISA", "score": 42})
    r2 = client.post("/api/students/PES1UG24AM006/grades", headers=h,
                     json={"subject_code": "AM301", "assessment": "ESA", "score": 45})
    grades = client.get("/api/students/PES1UG24AM006/grades", headers=h).get_json()["grades"]
    perf = client.get("/api/analytics/performance/PES1UG24AM006", headers=h).get_json()
    subj = perf["subjects"][0]
    assert (r1.status_code, r2.status_code) == (201, 201)
    assert {g["assessment"]: g["score"] for g in grades} == {"ISA": 42, "ESA": 45}
    assert subj["percentage"] == 87.0 and subj["grade"] == "A"
    record(f"POST ISA/ESA -> {r1.status_code}/{r2.status_code}; stored ISA=42, ESA=45; "
           f"AM301 = {subj['percentage']}% grade {subj['grade']}")


@tc("TC-REC-02.2", "APAS-F-005")
def test_update_grade(client, login, record):
    """Faculty updates an existing grade
    Objective: Verify grade updates through POST (upsert) and PUT.
    Preconditions: Ishita (PES1UG24AM004) has AM302 ESA=25.
    Test data: ESA 25 -> 40 (POST), then 40 -> 38 (PUT).
    Steps:
    1. POST the AM302 ESA grade with score 40.
    2. PUT /api/students/PES1UG24AM004/grades/<id> with score 38.
    Expected: Step 1 HTTP 200 (updated, not duplicated); step 2 HTTP 200; final score 38 with only one ESA row.
    """
    h = login("fac.rao")
    r1 = client.post("/api/students/PES1UG24AM004/grades", headers=h,
                     json={"subject_code": "AM302", "assessment": "ESA", "score": 40})
    gid = r1.get_json()["id"]
    r2 = client.put(f"/api/students/PES1UG24AM004/grades/{gid}", headers=h, json={"score": 38})
    rows = [g for g in client.get("/api/students/PES1UG24AM004/grades", headers=h).get_json()["grades"]
            if g["subject_code"] == "AM302" and g["assessment"] == "ESA"]
    assert r1.status_code == 200 and r2.status_code == 200 and len(rows) == 1 and rows[0]["score"] == 38
    record(f"upsert -> HTTP {r1.status_code}; PUT -> HTTP {r2.status_code}; final ESA={rows[0]['score']}, rows={len(rows)}")


@tc("TC-REC-02.3", "APAS-F-005")
@pytest.mark.parametrize("score", BV["grade_score_valid"])
def test_valid_boundary_scores(client, login, record, score):
    """Boundary grade values within 0-50 are accepted
    Objective: Verify boundary-value acceptance for assessment scores.
    Preconditions: fac.rao assigned AM302.
    Test data: 0, 0.5, 25, 49.5, 50 (max).
    Steps:
    1. POST an ISA grade with the boundary score.
    Expected: HTTP 201 and the stored score equals the input.
    """
    resp = client.post("/api/students/PES1UG24AM006/grades", headers=login("fac.rao"),
                       json={"subject_code": "AM302", "assessment": "ISA", "score": score})
    assert resp.status_code == 201 and resp.get_json()["score"] == score
    record(f"score={score} -> HTTP 201, stored {resp.get_json()['score']}")


@tc("TC-REC-02.4", "APAS-F-005")
@pytest.mark.parametrize("score", BV["grade_score_invalid"])
def test_invalid_scores_rejected(client, login, db, record, score):
    """Invalid grade values are rejected and nothing is stored
    Objective: Verify that out-of-range and non-numeric grades are rejected.
    Preconditions: fac.rao assigned AM302.
    Test data: -1, -0.01, 50.01, 51, 100, 1000 (1e3), "45", blank "", null, true, "abc" (TD-04).
    Steps:
    1. POST an ISA grade with the invalid score.
    Expected: HTTP 400 with a validation message; grade count unchanged.
    """
    before = db.execute("SELECT COUNT(*) FROM grades").fetchone()[0]
    resp = client.post("/api/students/PES1UG24AM006/grades", headers=login("fac.rao"),
                       json={"subject_code": "AM302", "assessment": "ISA", "score": score})
    after = db.execute("SELECT COUNT(*) FROM grades").fetchone()[0]
    assert resp.status_code == 400 and before == after
    record(f"score={score!r} -> HTTP 400 '{resp.get_json()['error']}'; grade rows unchanged")


@tc("TC-REC-02.5", "APAS-F-005")
@pytest.mark.parametrize("payload,expected", [
    ({"subject_code": "XX999", "assessment": "ISA", "score": 10}, 400),
    ({"subject_code": "AM301", "assessment": "Quiz", "score": 10}, 400),
    ({"assessment": "ISA", "score": 10}, 400),
])
def test_grade_reference_validation(client, login, record, payload, expected):
    """Grades for unknown subjects or assessments are rejected
    Objective: Verify referential validation of grade entries.
    Preconditions: fac.rao logged in.
    Test data: Unknown subject XX999, unknown assessment "Quiz", missing subject.
    Steps:
    1. POST the grade.
    Expected: HTTP 400.
    """
    resp = client.post("/api/students/PES1UG24AM006/grades", headers=login("fac.rao"), json=payload)
    assert resp.status_code == expected
    record(f"{payload} -> HTTP {resp.status_code} '{resp.get_json()['error']}'")


@tc("TC-REC-02.6", "APAS-F-005")
def test_grade_unknown_student_and_bad_body(client, login, record):
    """Grade entry for a non-existent student or with a non-JSON body is rejected
    Objective: Verify error handling for invalid grade requests.
    Steps:
    1. POST a grade for PES1UG24AM999.
    2. POST plain text instead of JSON.
    Expected: Step 1 HTTP 404; step 2 HTTP 400; no server error.
    """
    h = login("fac.rao")
    missing = client.post("/api/students/PES1UG24AM999/grades", headers=h,
                          json={"subject_code": "AM301", "assessment": "ISA", "score": 10})
    text = client.post("/api/students/PES1UG24AM006/grades", headers=h, data="score=10",
                       content_type="text/plain")
    assert missing.status_code == 404 and text.status_code == 400
    record(f"unknown student -> {missing.status_code}; non-JSON body -> {text.status_code}")


# --------------------------------------------------------------------------
# APAS-F-006 attendance
# --------------------------------------------------------------------------
@tc("TC-REC-03.1", "APAS-F-006")
def test_attendance_percentage_seeded(client, login, record):
    """Attendance percentage matches recorded attendance
    Objective: Verify the automatic attendance percentage calculation.
    Preconditions: Seeded attendance: Aarav 19/20, Diya 12/20, Rohan 15/20 per subject (3 subjects).
    Steps:
    1. GET /api/students/<id>/attendance for each student.
    Expected: Aarav 95.00% (57/60), Diya 60.00% (36/60), Rohan 75.00% (45/60), per subject and overall.
    """
    h = login("fac.rao")
    observed = {}
    for sid, pct, present in [("PES1UG24AM001", 95.0, 57), ("PES1UG24AM002", 60.0, 36),
                              ("PES1UG24AM005", 75.0, 45)]:
        data = client.get(f"/api/students/{sid}/attendance", headers=h).get_json()
        assert data["overall_percentage"] == pct and data["present"] == present and data["total"] == 60
        assert all(s["percentage"] == pct for s in data["subjects"])
        observed[sid] = f"{data['present']}/{data['total']} = {data['overall_percentage']}%"
    record(f"{observed}")


@tc("TC-REC-03.2", "APAS-F-006")
def test_record_and_correct_attendance(client, login, record):
    """Faculty records attendance; corrections update the percentage
    Objective: Verify attendance recording, duplicate-date handling and recalculation.
    Preconditions: Meera (PES1UG24AM006) has no attendance; fac.rao assigned AM301.
    Test data: 2026-10-12 present, 10-13 present, 10-14 present, 10-15 absent; then 10-15 corrected to present.
    Steps:
    1. POST four attendance entries.
    2. POST 2026-10-15 again with status present.
    Expected: After step 1 percentage 75.00% (3/4); step 2 returns HTTP 200 (update, not duplicate) and 100.00% (4/4).
    """
    h = login("fac.rao")
    url = "/api/students/PES1UG24AM006/attendance"
    for day, status in [("2026-10-12", "present"), ("2026-10-13", "present"),
                        ("2026-10-14", "present"), ("2026-10-15", "absent")]:
        resp = client.post(url, headers=h, json={"subject_code": "AM301", "date": day, "status": status})
        assert resp.status_code == 201
    first = resp.get_json()
    fix = client.post(url, headers=h, json={"subject_code": "AM301", "date": "2026-10-15", "status": "present"})
    second = fix.get_json()
    assert first["overall_percentage"] == 75.0 and first["total"] == 4
    assert fix.status_code == 200 and second["overall_percentage"] == 100.0 and second["total"] == 4
    record(f"after 4 entries: {first['present']}/{first['total']} = {first['overall_percentage']}%; "
           f"correction HTTP {fix.status_code} -> {second['present']}/{second['total']} = {second['overall_percentage']}%")


@tc("TC-REC-03.3", "APAS-F-006")
@pytest.mark.parametrize("field,value", [("status", v) for v in BV["attendance_status_invalid"]] +
                         [("date", v) for v in BV["attendance_date_invalid"]] +
                         [("date", "FUTURE"), ("subject_code", "XX999")])
def test_invalid_attendance_rejected(client, login, db, record, field, value):
    """Invalid attendance entries are rejected
    Objective: Verify validation of attendance status, date and subject.
    Preconditions: fac.rao assigned AM301.
    Test data: Invalid statuses, malformed/impossible dates, a future date, unknown subject.
    Steps:
    1. POST the attendance entry with one invalid field.
    Expected: HTTP 400; attendance table unchanged.
    """
    if value == "FUTURE":
        value = (date.today() + timedelta(days=1)).isoformat()
    payload = dict({"subject_code": "AM301", "date": "2026-10-12", "status": "present"}, **{field: value})
    before = db.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
    resp = client.post("/api/students/PES1UG24AM006/attendance", headers=login("fac.rao"), json=payload)
    after = db.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
    assert resp.status_code == 400 and before == after
    record(f"{field}={value!r} -> HTTP 400 '{resp.get_json()['error']}'")


@tc("TC-REC-03.4", "APAS-F-006")
def test_attendance_unassigned_faculty(client, login, db, record):
    """Faculty cannot record attendance for a subject they do not teach
    Objective: Verify that only authorised faculty record attendance.
    Preconditions: fac.iyer is assigned AM303 only.
    Test data: AM301 attendance for PES1UG24AM006.
    Steps:
    1. POST attendance for AM301 as fac.iyer.
    Expected: HTTP 403; no row stored.
    """
    resp = client.post("/api/students/PES1UG24AM006/attendance", headers=login("fac.iyer"),
                       json={"subject_code": "AM301", "date": "2026-10-12", "status": "present"})
    rows = db.execute("SELECT COUNT(*) FROM attendance WHERE student_id = 'PES1UG24AM006'").fetchone()[0]
    assert resp.status_code == 403 and rows == 0
    record(f"HTTP {resp.status_code}; rows stored={rows}")


@tc("TC-REC-03.5", "APAS-F-006")
@pytest.mark.parametrize("status,expected", [("absent", 0.0), ("present", 100.0)])
def test_attendance_all_absent_or_present(client, login, record, status, expected):
    """All-absent and all-present attendance give 0% and 100%
    Objective: Verify the edge cases of the percentage calculation (team test data TD-05).
    Preconditions: Meera (PES1UG24AM006) has no attendance; fac.rao assigned AM302.
    Test data: 4 sessions (2026-10-12 to 10-15), all with the same status.
    Steps:
    1. POST four attendance entries with the same status.
    Expected: 0.00% when all absent; 100.00% when all present; no calculation error.
    """
    h = login("fac.rao")
    for day in ("2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15"):
        resp = client.post("/api/students/PES1UG24AM006/attendance", headers=h,
                           json={"subject_code": "AM302", "date": day, "status": status})
    data = resp.get_json()
    record(f"4 x {status} -> {data['present']}/{data['total']} = {data['overall_percentage']}%")
    assert resp.status_code == 201 and data["overall_percentage"] == expected
