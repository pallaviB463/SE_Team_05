"""Performance Analytics Service and Predictive Analytics Service (SAD 3.4 items 8 and 10).

Calculation rules (the "configured calculation rules" of APAS-F-007):
  * Every subject has two assessments: ISA (max 50) and ESA (max 50).
  * Subject percentage = sum(scores) / sum(max scores) * 100.
  * A subject is complete only when every required assessment is recorded;
    incomplete subjects are reported but excluded from SGPA / CGPA.
  * 10-point grade scale: >=90 S(10), >=80 A(9), >=70 B(8), >=60 C(7),
    >=50 D(6), >=40 E(5), otherwise F(0).
  * SGPA = credit-weighted mean of grade points in a semester.
  * CGPA = credit-weighted mean of grade points across all semesters.
  * Overall percentage = credit-weighted mean of subject percentages.
All reported values are rounded half-up to 2 decimal places.
"""
from decimal import ROUND_HALF_UP, Decimal

ASSESSMENTS = {"ISA": 50.0, "ESA": 50.0}
GRADE_SCALE = [(90, 10, "S"), (80, 9, "A"), (70, 8, "B"), (60, 7, "C"), (50, 6, "D"), (40, 5, "E")]


def r2(value):
    if value is None:
        return None
    return float(Decimal(repr(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def grade_for(percentage):
    for cutoff, points, letter in GRADE_SCALE:
        if percentage >= cutoff:
            return points, letter
    return 0, "F"


def _weighted(pairs):
    total_credits = sum(c for c, _ in pairs)
    if not total_credits:
        return None
    return sum(c * v for c, v in pairs) / total_credits


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def load_student_records(db, student_id):
    subjects = {r["code"]: dict(r) for r in db.execute("SELECT * FROM subjects")}
    grades = db.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,)).fetchall()
    attendance = db.execute(
        "SELECT subject_code, status FROM attendance WHERE student_id = ?", (student_id,)).fetchall()
    return subjects, [dict(g) for g in grades], [dict(a) for a in attendance]


def load_all_records(db):
    """Bulk loader used by dashboards to avoid one query per student (APAS-NF-001)."""
    subjects = {r["code"]: dict(r) for r in db.execute("SELECT * FROM subjects")}
    grades, attendance = {}, {}
    for g in db.execute("SELECT student_id, subject_code, assessment, score, max_score FROM grades"):
        grades.setdefault(g["student_id"], []).append(dict(g))
    for a in db.execute("SELECT student_id, subject_code, status FROM attendance"):
        attendance.setdefault(a["student_id"], []).append(dict(a))
    return subjects, grades, attendance


# --------------------------------------------------------------------------
# APAS-F-006: attendance percentage
# --------------------------------------------------------------------------
def attendance_summary(subjects, attendance_rows):
    per_subject = {}
    for row in attendance_rows:
        s = per_subject.setdefault(row["subject_code"], {"present": 0, "total": 0})
        s["total"] += 1
        if row["status"] == "present":
            s["present"] += 1
    result = []
    for code in sorted(per_subject):
        s = per_subject[code]
        result.append({
            "subject_code": code,
            "subject_name": subjects.get(code, {}).get("name", code),
            "present": s["present"],
            "total": s["total"],
            "percentage": r2(s["present"] / s["total"] * 100),
        })
    present = sum(s["present"] for s in per_subject.values())
    total = sum(s["total"] for s in per_subject.values())
    return {
        "subjects": result,
        "present": present,
        "total": total,
        "overall_percentage": r2(present / total * 100) if total else None,
    }


# --------------------------------------------------------------------------
# APAS-F-007 / APAS-F-008: performance
# --------------------------------------------------------------------------
def subject_results(subjects, grade_rows):
    by_subject = {}
    for g in grade_rows:
        by_subject.setdefault(g["subject_code"], {})[g["assessment"]] = g
    results = []
    for code, assessments in by_subject.items():
        subj = subjects[code]
        scored = sum(a["score"] for a in assessments.values())
        maximum = sum(a["max_score"] for a in assessments.values())
        complete = set(ASSESSMENTS) <= set(assessments)
        pct = r2(scored / maximum * 100) if maximum else None
        points, letter = grade_for(pct) if complete else (None, None)
        results.append({
            "subject_code": code,
            "subject_name": subj["name"],
            "semester": subj["semester"],
            "credits": subj["credits"],
            "scores": {k: assessments[k]["score"] for k in sorted(assessments)},
            "percentage": pct,
            "grade_point": points,
            "grade": letter,
            "status": "complete" if complete else "incomplete",
        })
    results.sort(key=lambda r: (r["semester"], r["subject_code"]))
    return results


def performance_summary(subjects, grade_rows):
    results = subject_results(subjects, grade_rows)
    complete = [r for r in results if r["status"] == "complete"]
    semesters = []
    for sem in sorted({r["semester"] for r in complete}):
        rows = [r for r in complete if r["semester"] == sem]
        semesters.append({
            "semester": sem,
            "sgpa": r2(_weighted([(r["credits"], r["grade_point"]) for r in rows])),
            "percentage": r2(_weighted([(r["credits"], r["percentage"]) for r in rows])),
            "credits": sum(r["credits"] for r in rows),
            "subjects": [r["subject_code"] for r in rows],
        })
    return {
        "subjects": results,
        "semesters": semesters,
        "cgpa": r2(_weighted([(r["credits"], r["grade_point"]) for r in complete])),
        "overall_percentage": r2(_weighted([(r["credits"], r["percentage"]) for r in complete])),
        "incomplete_subjects": [r["subject_code"] for r in results if r["status"] == "incomplete"],
    }


# --------------------------------------------------------------------------
# APAS-F-009: threshold flags
# --------------------------------------------------------------------------
def threshold_flags(performance, attendance, thresholds):
    reasons = []
    min_att = thresholds["min_attendance_pct"]
    min_perf = thresholds["min_performance_pct"]
    for s in attendance["subjects"]:
        if s["percentage"] < min_att:
            reasons.append(f"Attendance in {s['subject_code']} is {s['percentage']}% "
                           f"(below {min_att:g}%)")
    if performance["overall_percentage"] is not None and performance["overall_percentage"] < min_perf:
        reasons.append(f"Overall performance {performance['overall_percentage']}% "
                       f"(below {min_perf:g}%)")
    for s in performance["subjects"]:
        if s["status"] == "complete" and s["grade"] == "F":
            reasons.append(f"Failed {s['subject_code']} ({s['percentage']}%)")
    return {"flagged": bool(reasons), "reasons": reasons}


# --------------------------------------------------------------------------
# APAS-F-013 / APAS-F-014: prediction and risk
# --------------------------------------------------------------------------
def predict(performance, attendance, thresholds, min_semesters=2):
    """Linear least-squares trend on SGPA history, extrapolated one semester."""
    history = [(s["semester"], s["sgpa"]) for s in performance["semesters"]]
    att = attendance["overall_percentage"]
    result = {"history": [{"semester": s, "sgpa": v} for s, v in history],
              "attendance_pct": att}
    if len(history) < min_semesters:
        result.update(status="insufficient_data", predicted_sgpa=None, trend=None, confidence=None,
                      message=f"At least {min_semesters} completed semesters are required for a prediction.")
    else:
        xs = [s for s, _ in history]
        ys = [v for _, v in history]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        predicted = my + slope * (max(xs) + 1 - mx)
        predicted = min(10.0, max(0.0, predicted))
        trend = "improving" if slope > 0.1 else "declining" if slope < -0.1 else "stable"
        result.update(status="ok", predicted_semester=max(xs) + 1, predicted_sgpa=r2(predicted),
                      slope=r2(slope), trend=trend,
                      confidence="medium" if len(history) >= 3 else "low")
    result.update(risk_assessment(result, thresholds))
    return result


def risk_assessment(prediction, thresholds):
    factors = []
    level = "low"
    pred = prediction.get("predicted_sgpa")
    att = prediction.get("attendance_pct")

    def raise_to(new):
        nonlocal level
        order = ["low", "medium", "high"]
        if order.index(new) > order.index(level):
            level = new

    if pred is not None:
        if pred < thresholds["risk_high_sgpa"]:
            raise_to("high")
            factors.append(f"Predicted SGPA {pred} below {thresholds['risk_high_sgpa']:g}")
        elif pred < thresholds["risk_medium_sgpa"]:
            raise_to("medium")
            factors.append(f"Predicted SGPA {pred} below {thresholds['risk_medium_sgpa']:g}")
    if att is not None:
        if att < thresholds["risk_high_attendance_pct"]:
            raise_to("high")
            factors.append(f"Attendance {att}% below {thresholds['risk_high_attendance_pct']:g}%")
        elif att < thresholds["min_attendance_pct"]:
            raise_to("medium")
            factors.append(f"Attendance {att}% below {thresholds['min_attendance_pct']:g}%")
    if prediction.get("trend") == "declining":
        factors.append("SGPA trend is declining")
    return {"risk_level": level, "at_risk": level in ("medium", "high"), "risk_factors": factors}


# --------------------------------------------------------------------------
# APAS-F-015: insights and recommendations (rule based)
# --------------------------------------------------------------------------
def insights(performance, attendance, prediction, thresholds):
    recs = []
    latest = max((s["semester"] for s in performance["subjects"]), default=None)
    for s in performance["subjects"]:
        if s["semester"] != latest or s["status"] != "complete":
            continue
        if s["percentage"] < 40:
            recs.append({"category": "critical", "subject_code": s["subject_code"],
                         "message": f"Failed {s['subject_name']} ({s['percentage']}%). "
                                    "Arrange remedial classes and plan for the supplementary exam."})
        elif s["percentage"] < 60:
            recs.append({"category": "academic", "subject_code": s["subject_code"],
                         "message": f"Weak performance in {s['subject_name']} ({s['percentage']}%). "
                                    "Schedule extra practice and attend faculty office hours."})
    for s in attendance["subjects"]:
        if s["percentage"] < thresholds["min_attendance_pct"]:
            recs.append({"category": "attendance", "subject_code": s["subject_code"],
                         "message": f"Attendance in {s['subject_name']} is {s['percentage']}%, below "
                                    f"the required {thresholds['min_attendance_pct']:g}%. "
                                    "Attend classes regularly."})
    hist = prediction.get("history", [])
    if prediction.get("trend") == "declining" and len(hist) >= 2:
        recs.append({"category": "trend", "subject_code": None,
                     "message": f"SGPA declined from {hist[0]['sgpa']} to {hist[-1]['sgpa']}. "
                                "Meet your faculty advisor to review study plans."})
    pred = prediction.get("predicted_sgpa")
    if pred is not None and pred < thresholds["risk_medium_sgpa"]:
        recs.append({"category": "risk", "subject_code": None,
                     "message": f"Predicted SGPA {pred} is below {thresholds['risk_medium_sgpa']:g}. "
                                "Academic counselling is recommended."})
    if not recs:
        recs.append({"category": "positive", "subject_code": None,
                     "message": "Performance is on track. Maintain consistent study and attendance."})
    return recs


def full_student_analysis(subjects, grade_rows, attendance_rows, thresholds):
    perf = performance_summary(subjects, grade_rows)
    att = attendance_summary(subjects, attendance_rows)
    pred = predict(perf, att, thresholds)
    return {
        "performance": perf,
        "attendance": att,
        "flags": threshold_flags(perf, att, thresholds),
        "prediction": pred,
    }
