"""TC-ANA: Academic performance analysis (APAS-F-007 .. APAS-F-009).

Expected values are calculated by hand from test_data/apas_test_data.json, not
with the application's own functions. Example (Aarav, semester 1):
  AM101 45+47=92% -> S(10), AM102 40+42=82% -> A(9), AM103 38+40=78% -> B(8)
  SGPA = (4*10 + 4*9 + 3*8) / 11 = 100/11 = 9.09
"""
import pytest

from apas.analytics import grade_for

tc = pytest.mark.tc

# Hand-calculated expected results
EXPECTED = {
    "PES1UG24AM001": {"sgpa": [9.09, 9.36, 9.73], "sem_pct": [84.55, 86.82, 89.36], "cgpa": 9.39, "overall": 86.91},
    "PES1UG24AM002": {"sgpa": [7.73, 7.73, 8.0], "sem_pct": [69.91, 70.55, 71.45], "cgpa": 7.82, "overall": 70.64},
    "PES1UG24AM003": {"sgpa": [7.36, 6.0, 3.18], "sem_pct": [65.73, 55.18, 40.27], "cgpa": 5.52, "overall": 53.73},
    "PES1UG24AM004": {"sgpa": [6.09], "sem_pct": [53.09], "cgpa": 6.09, "overall": 53.09},
    "PES1UG24AM005": {"sgpa": [6.0], "sem_pct": [50.0], "cgpa": 6.0, "overall": 50.0},
}


@tc("TC-ANA-01.1", "APAS-F-007", type="Unit")
@pytest.mark.parametrize("pct,points,letter", [
    (100, 10, "S"), (90, 10, "S"), (89.99, 9, "A"), (80, 9, "A"), (79.99, 8, "B"), (70, 8, "B"),
    (60, 7, "C"), (59.99, 6, "D"), (50, 6, "D"), (40, 5, "E"), (39.99, 0, "F"), (0, 0, "F")])
def test_grade_scale_boundaries(record, pct, points, letter):
    """Grade-point scale is applied correctly at every boundary
    Objective: Verify the configured 10-point grading rule at boundary values.
    Preconditions: Scale S>=90, A>=80, B>=70, C>=60, D>=50, E>=40, F<40.
    Test data: Percentages on and just below each cut-off.
    Steps:
    1. Call the grade calculation for each percentage.
    Expected: Each percentage maps to the grade point and letter shown in the parameter table.
    """
    assert grade_for(pct) == (points, letter)
    record(f"{pct}% -> {grade_for(pct)}")


@tc("TC-ANA-01.2", "APAS-F-007")
@pytest.mark.parametrize("sid", list(EXPECTED))
def test_overall_performance(client, login, record, sid):
    """Overall performance (CGPA and overall %) matches the hand calculation
    Objective: Verify the automatic overall academic performance calculation.
    Preconditions: Seeded grade records for students AM001-AM005.
    Test data: See EXPECTED table (hand-calculated, credit-weighted).
    Steps:
    1. GET /api/analytics/performance/<student>.
    Expected: CGPA and overall percentage equal the hand-calculated values to 2 decimals.
    """
    data = client.get(f"/api/analytics/performance/{sid}", headers=login("fac.rao")).get_json()
    exp = EXPECTED[sid]
    assert data["cgpa"] == exp["cgpa"] and data["overall_percentage"] == exp["overall"]
    record(f"{sid}: CGPA {data['cgpa']} (exp {exp['cgpa']}), overall {data['overall_percentage']}% "
           f"(exp {exp['overall']}%)")


@tc("TC-ANA-01.3", "APAS-F-007")
def test_recalculation_after_grade_change(client, login, record):
    """Performance values are recalculated after a grade update
    Objective: Verify that calculations always reflect the stored grades.
    Preconditions: Ishita (AM004): AM301 60%, AM302 50%, AM303 48%; SGPA 6.09.
    Test data: AM302 ESA changed 25 -> 40 (AM302 becomes 65% -> C(7)).
    Steps:
    1. POST the updated AM302 ESA grade as fac.rao.
    2. GET the performance summary.
    Expected: SGPA = (4*7 + 4*7 + 3*5)/11 = 6.45; overall = (240+260+144)/11 = 58.55%.
    """
    h = login("fac.rao")
    client.post("/api/students/PES1UG24AM004/grades", headers=h,
                json={"subject_code": "AM302", "assessment": "ESA", "score": 40})
    data = client.get("/api/analytics/performance/PES1UG24AM004", headers=h).get_json()
    assert data["semesters"][0]["sgpa"] == 6.45 and data["overall_percentage"] == 58.55
    record(f"SGPA {data['semesters'][0]['sgpa']}, overall {data['overall_percentage']}%")


@tc("TC-ANA-01.4", "APAS-F-007")
def test_incomplete_records_handled(client, login, record):
    """Incomplete subject records are reported but excluded from GPA
    Objective: Verify that incomplete academic records are handled appropriately (SRS 2.5).
    Preconditions: Meera (AM006) has no grades.
    Test data: Only AM301 ISA = 40 entered (ESA missing).
    Steps:
    1. POST the ISA grade.
    2. GET the performance summary.
    Expected: AM301 status "incomplete", no grade letter; CGPA and overall % are null; AM301 listed in incomplete_subjects.
    """
    h = login("fac.rao")
    client.post("/api/students/PES1UG24AM006/grades", headers=h,
                json={"subject_code": "AM301", "assessment": "ISA", "score": 40})
    data = client.get("/api/analytics/performance/PES1UG24AM006", headers=h).get_json()
    subj = data["subjects"][0]
    assert subj["status"] == "incomplete" and subj["grade"] is None
    assert data["cgpa"] is None and data["overall_percentage"] is None
    assert data["incomplete_subjects"] == ["AM301"]
    record(f"AM301 status={subj['status']}, grade={subj['grade']}, CGPA={data['cgpa']}, "
           f"incomplete={data['incomplete_subjects']}")


@tc("TC-ANA-01.5", "APAS-F-007")
def test_no_records(client, login, record):
    """A student with no records produces empty results without errors
    Objective: Verify behaviour when no academic data exists.
    Preconditions: Meera (AM006) has no grades or attendance.
    Steps:
    1. GET /api/analytics/performance/PES1UG24AM006.
    Expected: HTTP 200 with empty subject/semester lists and null CGPA/attendance; student not flagged.
    """
    resp = client.get("/api/analytics/performance/PES1UG24AM006", headers=login("fac.rao"))
    data = resp.get_json()
    assert resp.status_code == 200 and data["subjects"] == [] and data["cgpa"] is None
    assert data["attendance"]["overall_percentage"] is None and data["flags"]["flagged"] is False
    record(f"HTTP 200; subjects=[], CGPA=None, attendance=None, flagged=False")


@tc("TC-ANA-02.1", "APAS-F-008")
@pytest.mark.parametrize("sid", ["PES1UG24AM001", "PES1UG24AM002", "PES1UG24AM003"])
def test_semester_wise_analysis(client, login, record, sid):
    """Semester-wise SGPA and percentage match the hand calculation
    Objective: Verify semester-wise performance comparison.
    Preconditions: Three semesters of grades for AM001-AM003.
    Test data: See EXPECTED table.
    Steps:
    1. GET /api/analytics/performance/<student>.
    Expected: semesters[] lists semesters 1, 2, 3 with the expected SGPA and percentage.
    """
    data = client.get(f"/api/analytics/performance/{sid}", headers=login("fac.rao")).get_json()
    sems = data["semesters"]
    assert [s["semester"] for s in sems] == [1, 2, 3]
    assert [s["sgpa"] for s in sems] == EXPECTED[sid]["sgpa"]
    assert [s["percentage"] for s in sems] == EXPECTED[sid]["sem_pct"]
    record(f"{sid}: SGPA {[s['sgpa'] for s in sems]}, % {[s['percentage'] for s in sems]}")


@tc("TC-ANA-02.2", "APAS-F-008")
def test_subject_wise_analysis(client, login, record):
    """Subject-wise results are accurate for every subject
    Objective: Verify subject-wise performance figures.
    Preconditions: Kabir (AM003) seeded with 9 subjects.
    Test data: Semester 3: AM301 20+22=42% (E,5), AM302 18+17=35% (F,0), AM303 22+23=45% (E,5).
    Steps:
    1. GET /api/analytics/performance/PES1UG24AM003.
    Expected: 9 subjects; semester-3 percentages, grades and grade points as listed.
    """
    data = client.get("/api/analytics/performance/PES1UG24AM003", headers=login("fac.rao")).get_json()
    sem3 = {s["subject_code"]: (s["percentage"], s["grade"], s["grade_point"])
            for s in data["subjects"] if s["semester"] == 3}
    assert len(data["subjects"]) == 9
    assert sem3 == {"AM301": (42.0, "E", 5), "AM302": (35.0, "F", 0), "AM303": (45.0, "E", 5)}
    record(f"9 subjects returned; semester 3: {sem3}")


@tc("TC-ANA-02.3", "APAS-F-008")
def test_trend_direction(client, login, record):
    """Performance trends identify improving and declining students
    Objective: Verify that the semester comparison exposes the trend direction.
    Preconditions: Aarav improves every semester; Kabir declines every semester.
    Steps:
    1. GET /api/analytics/trends/<id> for Aarav and Kabir.
    Expected: Aarav SGPA strictly increasing; Kabir SGPA strictly decreasing.
    """
    h = login("fac.rao")
    a = [p["sgpa"] for p in client.get("/api/analytics/trends/PES1UG24AM001", headers=h).get_json()["semester_sgpa"]]
    k = [p["sgpa"] for p in client.get("/api/analytics/trends/PES1UG24AM003", headers=h).get_json()["semester_sgpa"]]
    assert a == sorted(a) and len(set(a)) == 3 and k == sorted(k, reverse=True) and len(set(k)) == 3
    record(f"Aarav {a} (increasing); Kabir {k} (decreasing)")


@tc("TC-ANA-03.1", "APAS-F-009")
def test_flagged_students_default_thresholds(client, login, record):
    """Students below default thresholds are flagged
    Objective: Verify identification of low performance / low attendance.
    Preconditions: Default thresholds: attendance 75%, performance 50%; a failed subject is also flagged.
    Test data: Diya attendance 60%; Kabir failed AM302; Rohan exactly 75% attendance and 50% performance (boundary).
    Steps:
    1. GET /api/analytics/flagged as fac.rao.
    Expected: Exactly Diya (attendance reasons for AM301-AM303) and Kabir (Failed AM302) are flagged; Rohan is NOT flagged (thresholds are "below").
    """
    data = client.get("/api/analytics/flagged", headers=login("fac.rao")).get_json()
    flagged = {s["id"]: s["flag_reasons"] for s in data["students"]}
    assert set(flagged) == {"PES1UG24AM002", "PES1UG24AM003"}
    assert len(flagged["PES1UG24AM002"]) == 3 and all("Attendance" in r for r in flagged["PES1UG24AM002"])
    assert flagged["PES1UG24AM003"] == ["Failed AM302 (35.0%)"]
    record(f"flagged={flagged}; Rohan (boundary 75%/50%) not flagged")


@tc("TC-ANA-03.2", "APAS-F-009")
def test_flagging_uses_configured_thresholds(client, login, record):
    """Flagging follows thresholds configured by the administrator
    Objective: Verify that changing the configured thresholds changes the flagged list.
    Preconditions: Default thresholds.
    Test data: min_attendance_pct 75 -> 55; min_performance_pct 50 -> 55.
    Steps:
    1. PUT /api/config/thresholds as admin.
    2. GET /api/analytics/flagged.
    Expected: Diya no longer flagged for attendance (60% >= 55%); Kabir (53.73%), Ishita (53.09%) and Rohan (50%) flagged for performance.
    """
    put = client.put("/api/config/thresholds", headers=login("admin"),
                     json={"min_attendance_pct": 55, "min_performance_pct": 55})
    data = client.get("/api/analytics/flagged", headers=login("fac.rao")).get_json()
    flagged = {s["id"]: s["flag_reasons"] for s in data["students"]}
    assert put.status_code == 200
    assert set(flagged) == {"PES1UG24AM003", "PES1UG24AM004", "PES1UG24AM005"}
    assert any("Overall performance 50.0%" in r for r in flagged["PES1UG24AM005"])
    record(f"thresholds updated (HTTP {put.status_code}); flagged={sorted(flagged)}")


@tc("TC-ANA-03.3", "APAS-F-009")
@pytest.mark.parametrize("payload", [{"min_attendance_pct": 101}, {"min_attendance_pct": -1},
                                     {"risk_high_sgpa": 11}, {"min_attendance_pct": "75"},
                                     {"unknown_key": 5}])
def test_invalid_threshold_config(client, login, record, payload):
    """Invalid threshold values are rejected
    Objective: Verify validation of threshold configuration.
    Preconditions: Logged in as admin.
    Test data: Out-of-range, non-numeric and unknown thresholds.
    Steps:
    1. PUT /api/config/thresholds with the invalid payload.
    Expected: HTTP 400; thresholds unchanged.
    """
    h = login("admin")
    resp = client.put("/api/config/thresholds", headers=h, json=payload)
    current = client.get("/api/config/thresholds", headers=h).get_json()
    assert resp.status_code == 400 and current["min_attendance_pct"] == 75.0
    record(f"{payload} -> HTTP 400 '{resp.get_json()['error']}'")
