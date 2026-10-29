"""TC-AUTH: Authentication, role-based access and logout (APAS-F-001 .. APAS-F-003)."""
from datetime import timedelta

import pytest

from apas.security import iso, utcnow

tc = pytest.mark.tc
GENERIC = "Invalid username or password"


@tc("TC-AUTH-01.1", "APAS-F-001")
@pytest.mark.parametrize("username,role", [("admin", "admin"), ("fac.rao", "faculty"), ("aarav", "student")])
def test_valid_login_each_role(client, record, username, role):
    """Valid credentials grant access for every role
    Objective: Verify that registered administrator, faculty and student users can log in with valid credentials.
    Preconditions: Active accounts admin, fac.rao and aarav exist in the test data.
    Test data: Valid username/password pairs from test_data/apas_test_data.json.
    Steps:
    1. POST /api/auth/login with the valid username and password.
    2. Call GET /api/dashboard with the returned bearer token.
    Expected: Login returns HTTP 200 with a session token and the correct role; dashboard returns HTTP 200.
    """
    from conftest import PASSWORDS
    resp = client.post("/api/auth/login", json={"username": username, "password": PASSWORDS[username]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["token"] and data["user"]["role"] == role
    dash = client.get("/api/dashboard", headers={"Authorization": f"Bearer {data['token']}"})
    assert dash.status_code == 200 and dash.get_json()["role"] == role
    record(f"{username}: login HTTP 200, role={data['user']['role']}, token issued "
           f"({len(data['token'])} chars); dashboard HTTP {dash.status_code}")


@tc("TC-AUTH-01.2", "APAS-F-001")
def test_wrong_password_rejected(client, record):
    """Wrong password is rejected
    Objective: Verify that an incorrect password is rejected.
    Preconditions: Account fac.rao exists.
    Test data: username=fac.rao, password=WrongPass@1
    Steps:
    1. POST /api/auth/login with a wrong password.
    Expected: HTTP 401, generic error message, no token issued.
    """
    resp = client.post("/api/auth/login", json={"username": "fac.rao", "password": "WrongPass@1"})
    data = resp.get_json()
    assert resp.status_code == 401 and data["error"] == GENERIC and "token" not in data
    record(f"HTTP {resp.status_code}, message='{data['error']}', no token")


@tc("TC-AUTH-01.3", "APAS-F-001")
def test_unknown_user_same_message(client, record):
    """Unknown username is rejected without revealing whether the account exists
    Objective: Verify that login with a non-registered username fails with the same message as a wrong password.
    Preconditions: No account named ghost.user exists.
    Test data: username=ghost.user, password=Whatever@123
    Steps:
    1. POST /api/auth/login with the unknown username.
    Expected: HTTP 401 with the same generic message used for a wrong password.
    """
    resp = client.post("/api/auth/login", json={"username": "ghost.user", "password": "Whatever@123"})
    assert resp.status_code == 401 and resp.get_json()["error"] == GENERIC
    record(f"HTTP 401, message identical to wrong-password case: '{resp.get_json()['error']}'")


@tc("TC-AUTH-01.4", "APAS-F-001")
@pytest.mark.parametrize("payload", [{}, {"username": "fac.rao"}, {"password": "x"},
                                     {"username": "", "password": ""}, {"username": "  ", "password": "x"},
                                     {"username": 123, "password": ["x"]}])
def test_missing_credentials(client, record, payload):
    """Missing or malformed credential fields are rejected
    Objective: Verify input validation on the login request.
    Preconditions: None.
    Test data: Empty body, missing fields, blank strings, wrong JSON types.
    Steps:
    1. POST /api/auth/login with each malformed payload.
    Expected: HTTP 400 "Username and password are required"; no session created.
    """
    resp = client.post("/api/auth/login", json=payload)
    assert resp.status_code == 400
    record(f"payload={payload} -> HTTP {resp.status_code} '{resp.get_json()['error']}'")


@tc("TC-AUTH-01.5", "APAS-F-001")
def test_inactive_account_rejected(client, record):
    """Deactivated account cannot log in
    Objective: Verify that a deactivated account is rejected even with the correct password.
    Preconditions: Account inactive.user exists with active=false.
    Test data: username=inactive.user with its correct password.
    Steps:
    1. POST /api/auth/login with the correct credentials of the inactive account.
    Expected: HTTP 401 with the generic error message.
    """
    from conftest import PASSWORDS
    resp = client.post("/api/auth/login", json={"username": "inactive.user",
                                                "password": PASSWORDS["inactive.user"]})
    assert resp.status_code == 401
    record(f"HTTP {resp.status_code} '{resp.get_json()['error']}'")


@tc("TC-AUTH-01.6", ["APAS-F-001", "APAS-SR-001"], type="Security")
def test_lockout_after_repeated_failures(client, record):
    """Account is temporarily locked after 5 consecutive failed attempts
    Objective: Verify brute-force protection on the login service.
    Preconditions: Account diya exists and is unlocked.
    Test data: 5 wrong passwords followed by the correct password.
    Steps:
    1. POST /api/auth/login five times with a wrong password.
    2. POST /api/auth/login with the correct password.
    Expected: The 6th attempt (correct password) is rejected with HTTP 401 and a lockout message.
    """
    from conftest import PASSWORDS
    for _ in range(5):
        assert client.post("/api/auth/login", json={"username": "diya", "password": "bad"}).status_code == 401
    resp = client.post("/api/auth/login", json={"username": "diya", "password": PASSWORDS["diya"]})
    assert resp.status_code == 401 and "locked" in resp.get_json()["error"].lower()
    record(f"After 5 failures, correct password -> HTTP 401 '{resp.get_json()['error']}'")


@tc("TC-AUTH-01.7", "APAS-F-001")
def test_web_login_form(client, record):
    """Web login form accepts valid and rejects invalid credentials
    Objective: Verify login through the browser interface.
    Preconditions: Account aarav exists.
    Test data: aarav / valid password; aarav / wrong password.
    Steps:
    1. POST the login form with wrong credentials.
    2. POST the login form with valid credentials and follow the redirect.
    Expected: Wrong credentials re-display the form with an error (HTTP 401); valid credentials redirect to /dashboard and set an HttpOnly, Secure session cookie.
    """
    from conftest import PASSWORDS
    bad = client.post("/login", data={"username": "aarav", "password": "nope"})
    assert bad.status_code == 401 and b'role="alert"' in bad.data and GENERIC.encode() in bad.data
    good = client.post("/login", data={"username": "aarav", "password": PASSWORDS["aarav"]})
    assert good.status_code == 302 and good.headers["Location"].endswith("/dashboard")
    cookie = good.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=Lax" in cookie
    page = client.get("/dashboard")
    assert page.status_code == 200 and b"Aarav Sharma" in page.data
    record(f"invalid -> HTTP 401 with alert; valid -> 302 to /dashboard, cookie flags: HttpOnly, Secure, "
           f"SameSite=Lax; dashboard HTTP {page.status_code}")


@tc("TC-AUTH-01.8", ["APAS-F-001", "APAS-SR-001"], type="Security")
@pytest.mark.parametrize("username", ["' OR '1'='1", "admin'--", "admin\" OR \"\"=\"", "fac.rao; DROP TABLE users"])
def test_sql_injection_login(client, db, record, username):
    """SQL injection in the username field does not bypass authentication
    Objective: Verify that injection strings are treated as data.
    Preconditions: None.
    Test data: Classic SQL injection payloads in the username field.
    Steps:
    1. POST /api/auth/login with the injection payload and any password.
    2. Check that the users table is intact.
    Expected: HTTP 401; users table still contains all accounts.
    """
    resp = client.post("/api/auth/login", json={"username": username, "password": "x' OR '1'='1"})
    assert resp.status_code == 401
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 9
    record(f"'{username}' -> HTTP {resp.status_code}; users table intact ({count} rows)")


# --------------------------------------------------------------------------
# APAS-F-002 role-based access to functions
# --------------------------------------------------------------------------
@tc("TC-AUTH-02.1", "APAS-F-002")
def test_role_specific_dashboards(client, login, record):
    """Each role receives a role-appropriate dashboard
    Objective: Verify that the dashboard content depends on the authenticated role.
    Preconditions: admin, fac.rao and aarav accounts exist.
    Steps:
    1. GET /api/dashboard as admin, faculty and student.
    Expected: Admin sees institution totals; faculty sees assigned subjects and student list; student sees only their own profile and results.
    """
    admin = client.get("/api/dashboard", headers=login("admin")).get_json()
    fac = client.get("/api/dashboard", headers=login("fac.rao")).get_json()
    stu = client.get("/api/dashboard", headers=login("aarav")).get_json()
    assert admin["totals"] == {"students": 6, "faculty": 3, "users": 9}
    assert [s["code"] for s in fac["subjects"]] == ["AM101", "AM102", "AM201", "AM202", "AM301", "AM302"]
    assert "students" not in stu and stu["student"]["id"] == "PES1UG24AM001"
    record(f"admin totals={admin['totals']}; faculty subjects={[s['code'] for s in fac['subjects']]}; "
           f"student sees only {stu['student']['id']}")


@tc("TC-AUTH-02.2", "APAS-F-002")
@pytest.mark.parametrize("user,method,path,body,expected", [
    ("admin", "post", "/api/students", "new", 201),
    ("fac.rao", "post", "/api/students", "new", 403),
    ("aarav", "post", "/api/students", "new", 403),
    ("fac.rao", "post", "/api/students/PES1UG24AM006/grades", "grade", 201),
    ("admin", "post", "/api/students/PES1UG24AM006/grades", "grade", 403),
    ("aarav", "post", "/api/students/PES1UG24AM006/grades", "grade", 403),
    ("fac.rao", "post", "/api/students/PES1UG24AM006/attendance", "att", 201),
    ("aarav", "post", "/api/students/PES1UG24AM006/attendance", "att", 403),
    ("admin", "get", "/api/audit", None, 200),
    ("fac.rao", "get", "/api/audit", None, 403),
    ("aarav", "get", "/api/audit", None, 403),
    ("admin", "put", "/api/config/thresholds", "cfg", 200),
    ("fac.rao", "put", "/api/config/thresholds", "cfg", 403),
    ("fac.rao", "get", "/api/analytics/at-risk", None, 200),
    ("aarav", "get", "/api/analytics/at-risk", None, 403),
    ("aarav", "get", "/api/analytics/flagged", None, 403),
    ("aarav", "get", "/api/students", None, 403),
])
def test_function_permission_matrix(client, login, record, user, method, path, body, expected):
    """Users can access only the functions permitted for their role
    Objective: Verify the role/function permission matrix defined in SAD 3.9.2.
    Preconditions: admin, fac.rao (assigned AM301) and aarav accounts exist.
    Test data: One request per (role, function) pair; see parameter table.
    Steps:
    1. Authenticate as the role.
    2. Call the function endpoint.
    Expected: Permitted pairs succeed (200/201); all others return HTTP 403.
    """
    payloads = {
        "new": {"id": "PES1UG24AM099", "name": "Test Student", "email": "t99@apas.test",
                "program": "B.Tech CSE (AI & ML)", "current_semester": 1},
        "grade": {"subject_code": "AM301", "assessment": "ISA", "score": 30},
        "att": {"subject_code": "AM301", "date": "2026-10-12", "status": "present"},
        "cfg": {"min_attendance_pct": 75},
    }
    resp = getattr(client, method)(path, headers=login(user), json=payloads.get(body))
    assert resp.status_code == expected
    record(f"{user} {method.upper()} {path} -> HTTP {resp.status_code} (expected {expected})")


# --------------------------------------------------------------------------
# APAS-F-003 logout and session termination
# --------------------------------------------------------------------------
@tc("TC-AUTH-03.1", "APAS-F-003")
def test_api_logout_invalidates_token(client, login, record):
    """Logout terminates the session token
    Objective: Verify that a token cannot be reused after logout.
    Preconditions: fac.rao is logged in.
    Steps:
    1. GET /api/dashboard with the token (expect 200).
    2. POST /api/auth/logout.
    3. GET /api/dashboard again with the same token.
    Expected: Step 3 returns HTTP 401 "Authentication required".
    """
    h = login("fac.rao")
    assert client.get("/api/dashboard", headers=h).status_code == 200
    out = client.post("/api/auth/logout", headers=h)
    again = client.get("/api/dashboard", headers=h)
    assert out.status_code == 200 and again.status_code == 401
    record(f"before logout 200; logout {out.status_code}; reuse of token -> HTTP {again.status_code}")


@tc("TC-AUTH-03.2", "APAS-F-003")
def test_web_logout_blocks_protected_pages(client, record):
    """Browser logout clears the session and protected pages require login again
    Objective: Verify logout from the web interface.
    Preconditions: aarav logged in through the login form.
    Steps:
    1. Open /dashboard (expect 200, Cache-Control: no-store).
    2. Submit the Log out form.
    3. Open /dashboard again.
    Expected: After logout the session cookie is cleared and /dashboard redirects to /login.
    """
    from conftest import PASSWORDS
    client.post("/login", data={"username": "aarav", "password": PASSWORDS["aarav"]})
    page = client.get("/dashboard")
    assert page.status_code == 200 and page.headers["Cache-Control"] == "no-store"
    out = client.post("/logout")
    assert out.status_code == 302 and out.headers["Location"].endswith("/login")
    after = client.get("/dashboard")
    assert after.status_code == 302 and after.headers["Location"].endswith("/login")
    record(f"dashboard 200 (no-store); logout -> 302 /login; dashboard afterwards -> 302 /login")


@tc("TC-AUTH-03.3", "APAS-F-003")
def test_idle_session_expires(client, db, login, record):
    """Idle sessions expire after 30 minutes
    Objective: Verify automatic session termination after inactivity.
    Preconditions: fac.rao is logged in.
    Test data: Session last activity set to 31 minutes ago.
    Steps:
    1. Set sessions.last_seen to now - 31 minutes.
    2. GET /api/dashboard with the token.
    Expected: HTTP 401; the expired session is removed.
    """
    h = login("fac.rao")
    db.execute("UPDATE sessions SET last_seen = ?", (iso(utcnow() - timedelta(minutes=31)),))
    db.commit()
    resp = client.get("/api/dashboard", headers=h)
    remaining = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    assert resp.status_code == 401 and remaining == 0
    record(f"after 31 min idle -> HTTP {resp.status_code}; sessions remaining={remaining}")


@tc("TC-AUTH-03.4", "APAS-F-003")
def test_logout_requires_session(client, record):
    """Logout without a session is rejected
    Objective: Verify that logout cannot be called anonymously.
    Steps:
    1. POST /api/auth/logout without a token.
    Expected: HTTP 401.
    """
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 401
    record(f"HTTP {resp.status_code}")
