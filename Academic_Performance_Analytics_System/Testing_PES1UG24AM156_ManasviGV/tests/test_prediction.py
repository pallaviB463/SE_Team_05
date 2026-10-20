"""TC-PRED: Predictive analytics, risk identification and insights (APAS-F-013 .. APAS-F-015).

Prediction method under test: least-squares linear trend of the semester SGPA history,
extrapolated one semester ahead and clipped to [0, 10]. A prediction requires at least
two completed semesters.

Hand calculation (Kabir): SGPA 7.36, 6.00, 3.18 -> mean 5.5133, slope (3.18-7.36)/2 = -2.09
  predicted semester 4 = 5.5133 + 2 * (-2.09) = 1.33
"""
import json
import math

import pytest

from apas import analytics
from apas.db import DEFAULT_THRESHOLDS, connect
from apas.seed import add_synthetic_students, load_dataset
from conftest import RESULTS_DIR, TEST_DATA

tc = pytest.mark.tc


@tc("TC-PRED-01.1", "APAS-F-013")
@pytest.mark.parametrize("sid,predicted,trend,confidence", [
    ("PES1UG24AM001", 10.0, "improving", "medium"),   # 9.39 + 2*0.32 = 10.03 -> clipped to 10.0
    ("PES1UG24AM002", 8.09, "improving", "medium"),   # 7.82 + 2*0.135 = 8.09
    ("PES1UG24AM003", 1.33, "declining", "medium"),
])
def test_prediction_for_students_with_history(client, login, record, sid, predicted, trend, confidence):
    """Predictions are generated for students with sufficient history
    Objective: Verify predicted SGPA, trend and confidence against the hand calculation.
    Preconditions: Three completed semesters for AM001-AM003; fac.rao logged in.
    Test data: Expected values in the parameter table (Aarav's prediction is clipped at the 10.0 maximum).
    Steps:
    1. GET /api/analytics/predictions/<student>.
    Expected: status "ok", predicted semester 4, predicted SGPA/trend/confidence as expected.
    """
    data = client.get(f"/api/analytics/predictions/{sid}", headers=login("fac.rao")).get_json()
    assert data["status"] == "ok" and data["predicted_semester"] == 4
    assert data["predicted_sgpa"] == predicted and data["trend"] == trend and data["confidence"] == confidence
    record(f"{sid}: predicted SGPA {data['predicted_sgpa']} (exp {predicted}), trend {data['trend']}, "
           f"confidence {data['confidence']}")


@tc("TC-PRED-01.2", "APAS-F-013")
@pytest.mark.parametrize("sid", ["PES1UG24AM004", "PES1UG24AM005", "PES1UG24AM006"])
def test_prediction_insufficient_history(client, login, record, sid):
    """Students without sufficient history get an explicit 'insufficient data' result
    Objective: Verify that no prediction is fabricated when history is insufficient.
    Preconditions: AM004/AM005 have one semester; AM006 has none.
    Steps:
    1. GET /api/analytics/predictions/<student>.
    Expected: status "insufficient_data", predicted_sgpa null, explanatory message.
    """
    data = client.get(f"/api/analytics/predictions/{sid}", headers=login("admin")).get_json()
    assert data["status"] == "insufficient_data" and data["predicted_sgpa"] is None and data["message"]
    record(f"{sid}: status={data['status']}, message='{data['message']}'")


@tc("TC-PRED-01.3", "APAS-F-013")
def test_prediction_access(client, login, record):
    """Only faculty and administrators can retrieve predictions
    Objective: Verify role restrictions on predictions (SRS stakeholders: Faculty, Administrator).
    Steps:
    1. GET /api/analytics/predictions/PES1UG24AM001 as aarav (own record) and as fac.rao.
    Expected: Student -> 403; faculty -> 200.
    """
    stu = client.get("/api/analytics/predictions/PES1UG24AM001", headers=login("aarav"))
    fac = client.get("/api/analytics/predictions/PES1UG24AM001", headers=login("fac.rao"))
    assert stu.status_code == 403 and fac.status_code == 200
    record(f"student -> {stu.status_code}; faculty -> {fac.status_code}")


@tc("TC-PRED-01.4", "APAS-F-013", type="Predictive Evaluation",
    limitation="Evaluation uses a synthetic cohort; results describe the method's behaviour, not real-world accuracy. "
               "No accuracy threshold is asserted because the SRS does not define one (STP 15.1).")
def test_prediction_backtest(tmp_path, record):
    """Back-test the prediction method on a synthetic cohort
    Objective: Evaluate prediction error and risk classification using hold-out data.
    Preconditions: 300 synthetic students with 3 semesters of grades (seed 2026).
    Test data: Semesters 1-2 used as history; actual semester-3 SGPA held out.
    Steps:
    1. Generate the synthetic cohort.
    2. Predict semester-3 SGPA from semesters 1-2 for each student.
    3. Compare with the actual semester-3 SGPA; classify "at risk" as SGPA < 6.0.
    Expected: A prediction is produced for 100% of eligible students, every prediction lies in [0, 10]; MAE, RMSE, precision and recall are recorded in results/prediction_evaluation.json.
    """
    conn = connect(tmp_path / "eval.db")
    load_dataset(conn, TEST_DATA)
    cohort = add_synthetic_students(conn, 300)
    subjects = {r["code"]: dict(r) for r in conn.execute("SELECT * FROM subjects")}
    errors, tp, fp, fn, tn, produced = [], 0, 0, 0, 0, 0
    for sid in cohort:
        rows = [dict(r) for r in conn.execute("SELECT * FROM grades WHERE student_id = ?", (sid,))]
        history = [r for r in rows if subjects[r["subject_code"]]["semester"] < 3]
        actual = analytics.performance_summary(subjects, rows)["semesters"][2]["sgpa"]
        perf = analytics.performance_summary(subjects, history)
        pred = analytics.predict(perf, {"overall_percentage": None}, DEFAULT_THRESHOLDS)
        if pred["status"] != "ok":
            continue
        produced += 1
        p = pred["predicted_sgpa"]
        assert 0 <= p <= 10
        errors.append(p - actual)
        predicted_risk, actual_risk = p < 6.0, actual < 6.0
        tp += predicted_risk and actual_risk
        fp += predicted_risk and not actual_risk
        fn += actual_risk and not predicted_risk
        tn += not predicted_risk and not actual_risk
    conn.close()
    assert produced == len(cohort)
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    result = {
        "cohort_size": len(cohort), "predictions_produced": produced,
        "mae_sgpa": round(mae, 3), "rmse_sgpa": round(rmse, 3),
        "mean_error_sgpa": round(sum(errors) / len(errors), 3),
        "risk_threshold_sgpa": 6.0,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall": round(tp / (tp + fn), 3) if tp + fn else None,
        "accuracy": round((tp + tn) / produced, 3),
        "f1": round(2 * tp / (2 * tp + fp + fn), 3) if tp else None,
        "method": "Least-squares linear trend on semester SGPA (2 semesters of history), clipped to [0, 10]",
        "data": "Synthetic cohort generated by apas.seed.add_synthetic_students(seed=2026)",
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "prediction_evaluation.json").write_text(json.dumps(result, indent=2))
    record(f"{produced}/{len(cohort)} predictions; MAE {result['mae_sgpa']}, RMSE {result['rmse_sgpa']}; "
           f"risk precision {result['precision']}, recall {result['recall']}, F1 {result['f1']}, accuracy {result['accuracy']}")


# --------------------------------------------------------------------------
# APAS-F-014 at-risk identification
# --------------------------------------------------------------------------
@tc("TC-PRED-02.1", "APAS-F-014")
def test_at_risk_list(client, login, record):
    """Students meeting the risk criteria appear in the academic risk list
    Objective: Verify at-risk classification with default risk criteria.
    Preconditions: Default criteria: high if predicted SGPA < 5 or attendance < 65%; medium if predicted SGPA < 6 or attendance < 75%.
    Test data: Kabir predicted 1.33 (high); Diya attendance 60% (high); Aarav, Ishita, Rohan (75% boundary), Meera low.
    Steps:
    1. GET /api/analytics/at-risk as fac.rao.
    Expected: Exactly Diya and Kabir, both "high", with their risk factors; Rohan at exactly 75% is not listed.
    """
    data = client.get("/api/analytics/at-risk", headers=login("fac.rao")).get_json()
    got = {s["id"]: (s["risk_level"], s["risk_factors"]) for s in data["students"]}
    assert set(got) == {"PES1UG24AM002", "PES1UG24AM003"}
    assert got["PES1UG24AM002"][0] == "high" and "Attendance 60.0% below 65%" in got["PES1UG24AM002"][1]
    assert got["PES1UG24AM003"][0] == "high" and "Predicted SGPA 1.33 below 5" in got["PES1UG24AM003"][1]
    record(f"at-risk={got}")


@tc("TC-PRED-02.2", "APAS-F-014")
def test_risk_criteria_configurable(client, login, record):
    """Changing the predefined risk criteria changes the classification
    Objective: Verify that risk levels follow the configured criteria.
    Test data: risk_high_attendance_pct 65 -> 55 (Diya 60% now medium); risk_medium_sgpa 6 -> 8.5 (Diya predicted 8.09 -> medium).
    Steps:
    1. PUT /api/config/thresholds as admin.
    2. GET /api/analytics/at-risk.
    Expected: Diya listed as "medium"; Kabir still "high".
    """
    client.put("/api/config/thresholds", headers=login("admin"),
               json={"risk_high_attendance_pct": 55, "risk_medium_sgpa": 8.5})
    data = client.get("/api/analytics/at-risk", headers=login("fac.rao")).get_json()
    got = {s["id"]: s["risk_level"] for s in data["students"]}
    assert got == {"PES1UG24AM003": "high", "PES1UG24AM002": "medium"}
    assert [s["id"] for s in data["students"]] == ["PES1UG24AM003", "PES1UG24AM002"]
    record(f"risk list (ordered high->medium) = {[(s['id'], s['risk_level']) for s in data['students']]}")


# --------------------------------------------------------------------------
# APAS-F-015 insights and recommendations
# --------------------------------------------------------------------------
@tc("TC-PRED-03.1", "APAS-F-015", priority="Medium")
def test_insights_for_weak_student(client, login, record):
    """Recommendations address the identified weaknesses and risk factors
    Objective: Verify that insights are relevant to the student's weaknesses.
    Preconditions: Kabir: AM301 42%, AM302 35% (failed), AM303 45%, declining SGPA, predicted 1.33.
    Steps:
    1. GET /api/analytics/insights/PES1UG24AM003 as fac.rao.
    Expected: critical recommendation for AM302; academic recommendations for AM301 and AM303; one trend and one risk recommendation; no attendance recommendation (80%).
    """
    recs = client.get("/api/analytics/insights/PES1UG24AM003", headers=login("fac.rao")).get_json()["recommendations"]
    cats = sorted((r["category"], r["subject_code"] or "") for r in recs)
    assert cats == [("academic", "AM301"), ("academic", "AM303"), ("critical", "AM302"), ("risk", ""), ("trend", "")]
    record(f"{len(recs)} recommendations: {cats}")


@tc("TC-PRED-03.2", "APAS-F-015", priority="Medium")
@pytest.mark.parametrize("sid,expected", [
    ("PES1UG24AM002", [("attendance", "AM301"), ("attendance", "AM302"), ("attendance", "AM303")]),
    ("PES1UG24AM001", [("positive", "")]),
])
def test_insights_attendance_and_positive(client, login, record, sid, expected):
    """Attendance recommendations for low attendance; positive message when on track
    Objective: Verify insight rules for attendance and for students without weaknesses.
    Steps:
    1. GET /api/analytics/insights for Diya and Aarav.
    Expected: Diya -> one attendance recommendation per subject; Aarav -> a single "on track" message.
    """
    recs = client.get(f"/api/analytics/insights/{sid}", headers=login("fac.rao")).get_json()["recommendations"]
    assert sorted((r["category"], r["subject_code"] or "") for r in recs) == expected
    record(f"{sid}: {[r['message'] for r in recs]}")


@tc("TC-PRED-03.3", "APAS-F-015", priority="Medium")
def test_student_sees_own_insights_only(client, login, record):
    """Students can see their own insights but not another student's
    Steps:
    1. GET /api/analytics/insights/PES1UG24AM003 as kabir and as aarav.
    Expected: kabir -> 200; aarav -> 403.
    """
    own = client.get("/api/analytics/insights/PES1UG24AM003", headers=login("kabir"))
    other = client.get("/api/analytics/insights/PES1UG24AM003", headers=login("aarav"))
    assert own.status_code == 200 and other.status_code == 403
    record(f"own -> {own.status_code}; other student -> {other.status_code}")
