"""TC-SEC: Security requirements (APAS-NF-003, APAS-SR-001 .. APAS-SR-005)."""
import json
import socket
import ssl
from datetime import datetime, timedelta, timezone

import pytest

from apas import create_app
from conftest import PASSWORDS, RESULTS_DIR, https_client
from live import https_server

tc = pytest.mark.tc

PROTECTED = [
    ("get", "/api/dashboard"), ("get", "/api/students"), ("post", "/api/students"),
    ("get", "/api/students/PES1UG24AM001"), ("put", "/api/students/PES1UG24AM001"),
    ("get", "/api/students/PES1UG24AM001/grades"), ("post", "/api/students/PES1UG24AM001/grades"),
    ("get", "/api/students/PES1UG24AM001/attendance"), ("post", "/api/students/PES1UG24AM001/attendance"),
    ("get", "/api/analytics/performance/PES1UG24AM001"), ("get", "/api/analytics/trends/PES1UG24AM001"),
    ("get", "/api/analytics/predictions/PES1UG24AM001"), ("get", "/api/analytics/at-risk"),
    ("get", "/api/analytics/flagged"), ("get", "/api/analytics/insights/PES1UG24AM001"),
    ("post", "/api/reports"), ("get", "/api/audit"), ("get", "/api/config/thresholds"),
    ("put", "/api/config/thresholds"), ("post", "/api/auth/logout"),
]


# --------------------------------------------------------------------------
# TC-SEC-01: valid credentials required (APAS-SR-001, APAS-NF-003)
# --------------------------------------------------------------------------
@tc("TC-SEC-01.1", ["APAS-SR-001", "APAS-NF-003"], type="Security")
def test_protected_endpoints_require_authentication(client, record):
    """Every protected endpoint rejects unauthenticated requests
    Objective: Verify that academic information cannot be accessed without valid credentials.
    Preconditions: No session.
    Test data: All 20 protected API operations (SAD 4.3.1) and the /dashboard page.
    Steps:
    1. Call each protected operation without a token.
    2. Open /dashboard without a session.
    Expected: Every API call returns HTTP 401 with no academic data; /dashboard redirects to /login.
    """
    codes = {}
    for method, path in PROTECTED:
        resp = getattr(client, method)(path, json={})
        codes[f"{method.upper()} {path}"] = resp.status_code
        assert resp.status_code == 401 and set(resp.get_json()) == {"error", "status"}
    page = client.get("/dashboard")
    assert page.status_code == 302 and page.headers["Location"].endswith("/login")
    record(f"{len(codes)} protected API operations -> all HTTP 401; /dashboard -> 302 /login")


@tc("TC-SEC-01.2", ["APAS-SR-001", "APAS-NF-003"], type="Security")
@pytest.mark.parametrize("header", ["Bearer invalidtoken", "Bearer ", "Basic YWRtaW46QWRtaW5AQVBBUzIwMjY=",
                                    "Bearer ' OR '1'='1", "TAMPER"])
def test_forged_tokens_rejected(client, login, record, header):
    """Forged, malformed or tampered tokens are rejected
    Objective: Verify that only server-issued session tokens grant access.
    Test data: Random token, empty bearer, HTTP Basic credentials, SQL injection string, a valid token with one character changed.
    Steps:
    1. GET /api/dashboard with the forged Authorization header.
    Expected: HTTP 401.
    """
    if header == "TAMPER":
        real = login("admin")["Authorization"]
        header = real[:-1] + ("A" if real[-1] != "A" else "B")
    resp = client.get("/api/dashboard", headers={"Authorization": header})
    assert resp.status_code == 401
    record(f"Authorization '{header[:24]}...' -> HTTP {resp.status_code}")


# --------------------------------------------------------------------------
# TC-SEC-02: role-based access control (APAS-SR-002)
# --------------------------------------------------------------------------
@tc("TC-SEC-02.1", "APAS-SR-002", type="Security")
@pytest.mark.parametrize("method,path,body", [
    ("get", "/api/students/PES1UG24AM003", None),
    ("get", "/api/students/PES1UG24AM003/grades", None),
    ("get", "/api/students/PES1UG24AM003/attendance", None),
    ("get", "/api/analytics/performance/PES1UG24AM003", None),
    ("get", "/api/analytics/trends/PES1UG24AM003", None),
    ("get", "/api/analytics/insights/PES1UG24AM003", None),
    ("post", "/api/reports", {"student_id": "PES1UG24AM003"}),
])
def test_student_cannot_read_other_student(client, login, record, method, path, body):
    """A student cannot access another student's academic records
    Objective: Verify horizontal access control between students.
    Preconditions: aarav (PES1UG24AM001) logged in.
    Test data: Requests for Kabir (PES1UG24AM003).
    Steps:
    1. Call the endpoint for the other student.
    Expected: HTTP 403; the response contains none of Kabir's data.
    """
    resp = getattr(client, method)(path, headers=login("aarav"), json=body)
    assert resp.status_code == 403 and b"Kabir" not in resp.data and b"PES1UG24AM003" not in resp.data
    record(f"{method.upper()} {path} as aarav -> HTTP {resp.status_code}, no data leaked")


@tc("TC-SEC-02.2", "APAS-SR-002", type="Security")
def test_faculty_limited_to_assigned_subjects(client, login, db, record):
    """Faculty cannot change grades of subjects they are not assigned to
    Objective: Verify record-level authorisation for grade changes.
    Preconditions: fac.iyer assigned AM103/AM203/AM303 only. Kabir AM301 ISA = 20.
    Test data: fac.iyer sets Kabir AM301 ISA to 50 via POST and via PUT.
    Steps:
    1. POST the grade as fac.iyer.
    2. PUT /api/students/PES1UG24AM003/grades/<id> as fac.iyer.
    3. Read the grade from the database.
    Expected: Both requests HTTP 403; stored score still 20.
    """
    gid = db.execute("SELECT id FROM grades WHERE student_id='PES1UG24AM003' AND subject_code='AM301' "
                     "AND assessment='ISA'").fetchone()["id"]
    h = login("fac.iyer")
    post = client.post("/api/students/PES1UG24AM003/grades", headers=h,
                       json={"subject_code": "AM301", "assessment": "ISA", "score": 50})
    put = client.put(f"/api/students/PES1UG24AM003/grades/{gid}", headers=h, json={"score": 50})
    score = db.execute("SELECT score FROM grades WHERE id = ?", (gid,)).fetchone()["score"]
    assert post.status_code == 403 and put.status_code == 403 and score == 20
    record(f"POST -> {post.status_code}, PUT -> {put.status_code}; stored score still {score}")


@tc("TC-SEC-02.3", "APAS-SR-002", type="Security")
def test_privilege_escalation_attempts(client, login, db, record):
    """Students cannot escalate privileges through crafted requests
    Objective: Verify server-side enforcement independent of the UI.
    Preconditions: aarav logged in.
    Test data: Self-grade change, profile edit, threshold change, audit read.
    Steps:
    1. aarav POSTs a grade of 50 for himself.
    2. aarav PUTs his own profile.
    3. aarav PUTs thresholds and GETs /api/audit.
    Expected: All HTTP 403; database unchanged.
    """
    h = login("aarav")
    codes = [
        client.post("/api/students/PES1UG24AM001/grades", headers=h,
                    json={"subject_code": "AM302", "assessment": "ISA", "score": 50}).status_code,
        client.put("/api/students/PES1UG24AM001", headers=h, json={"name": "Hacker"}).status_code,
        client.put("/api/config/thresholds", headers=h, json={"min_attendance_pct": 0}).status_code,
        client.get("/api/audit", headers=h).status_code,
    ]
    name = db.execute("SELECT name FROM students WHERE id='PES1UG24AM001'").fetchone()["name"]
    assert codes == [403, 403, 403, 403] and name == "Aarav Sharma"
    record(f"grade/profile/thresholds/audit -> {codes}; profile unchanged ('{name}')")


# --------------------------------------------------------------------------
# TC-SEC-03: HTTPS with TLS 1.2+ (APAS-SR-003)
# --------------------------------------------------------------------------
@tc("TC-SEC-03.1", "APAS-SR-003", type="Security")
def test_insecure_http_redirected_or_rejected(app, record):
    """Plain-HTTP requests are redirected (GET) or rejected (state-changing)
    Objective: Verify that insecure connections are not served.
    Preconditions: Production configuration (ENFORCE_HTTPS = True).
    Steps:
    1. GET http://localhost/dashboard.
    2. POST http://localhost/api/auth/login.
    3. GET https://localhost/api/health.
    Expected: Step 1 HTTP 301 to https://; step 2 HTTP 403 "HTTPS is required"; step 3 includes Strict-Transport-Security max-age >= 1 year; login cookie has the Secure flag.
    """
    plain = app.test_client()
    redirect = plain.get("/dashboard")
    post = plain.post("/api/auth/login", json={"username": "admin", "password": PASSWORDS["admin"]})
    secure = https_client(app)
    health = secure.get("/api/health")
    login = secure.post("/api/auth/login", json={"username": "admin", "password": PASSWORDS["admin"]})
    hsts = health.headers.get("Strict-Transport-Security", "")
    assert redirect.status_code == 301 and redirect.headers["Location"].startswith("https://")
    assert post.status_code == 403 and post.get_json()["error"] == "HTTPS is required"
    assert "max-age=31536000" in hsts and "Secure" in login.headers["Set-Cookie"]
    record(f"HTTP GET -> 301 {redirect.headers['Location']}; HTTP POST -> 403; HSTS='{hsts}'; cookie Secure")


@tc("TC-SEC-03.3", "APAS-SR-003", type="Security")
def test_spoofed_forwarded_proto_not_trusted(app, record):
    """A client-supplied X-Forwarded-Proto header cannot bypass HTTPS enforcement
    Objective: Verify that plain-HTTP requests are not accepted just because the client claims HTTPS.
    Preconditions: Production configuration; no reverse proxy configured.
    Test data: Plain-HTTP requests carrying "X-Forwarded-Proto: https".
    Steps:
    1. GET http://localhost/dashboard with the spoofed header.
    2. POST http://localhost/api/auth/login with the spoofed header and valid credentials.
    Expected: Step 1 HTTP 301 to https://; step 2 HTTP 403 "HTTPS is required" (credentials never accepted over plain HTTP).
    """
    plain = app.test_client()
    spoof = {"X-Forwarded-Proto": "https"}
    get = plain.get("/dashboard", headers=spoof)
    post = plain.post("/api/auth/login", headers=spoof,
                      json={"username": "admin", "password": PASSWORDS["admin"]})
    record(f"spoofed GET -> HTTP {get.status_code}; spoofed POST login -> HTTP {post.status_code}")
    assert get.status_code == 301 and post.status_code == 403


@tc("TC-SEC-03.2", "APAS-SR-003", type="Security", priority="High",
    limitation="Executed against the local test server; the deployed environment's TLS configuration must be "
               "re-checked (e.g. SSL Labs / testssl.sh) once a hosting platform is chosen (SAD 4.6.1 open issue 3).")
@pytest.mark.live
@pytest.mark.filterwarnings("ignore:ssl.TLSVersion.TLSv1:DeprecationWarning")
def test_tls_protocol_versions(db_path, tmp_path, record):
    """Server negotiates TLS 1.2/1.3 and refuses TLS 1.0/1.1
    Objective: Verify the minimum TLS version on a real socket.
    Preconditions: APAS served over HTTPS with make_ssl_context (minimum TLS 1.2), self-signed certificate.
    Test data: Client handshakes pinned to TLS 1.0, 1.1, 1.2 and 1.3.
    Steps:
    1. Start the HTTPS server.
    2. Attempt a handshake with each protocol version.
    Expected: TLS 1.2 and 1.3 handshakes succeed; TLS 1.0 and 1.1 handshakes fail.
    """
    app = create_app({"DATABASE": str(db_path)})
    outcomes = {}
    with https_server(app, tmp_path) as (_base, cert, port):
        for name, version in [("TLSv1", ssl.TLSVersion.TLSv1), ("TLSv1.1", ssl.TLSVersion.TLSv1_1),
                              ("TLSv1.2", ssl.TLSVersion.TLSv1_2), ("TLSv1.3", ssl.TLSVersion.TLSv1_3)]:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_verify_locations(cert)
            if version < ssl.TLSVersion.TLSv1_2:
                ctx.set_ciphers("ALL:@SECLEVEL=0")
            try:
                ctx.minimum_version = ctx.maximum_version = version
                with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
                    with ctx.wrap_socket(sock, server_hostname="localhost") as tls:
                        outcomes[name] = f"accepted ({tls.version()}, {tls.cipher()[0]})"
            except (ssl.SSLError, ValueError, OSError) as exc:
                outcomes[name] = f"refused ({type(exc).__name__}: {str(exc)[:80]})"
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "tls_results.json").write_text(json.dumps({"openssl": ssl.OPENSSL_VERSION, **outcomes}, indent=2))
    assert outcomes["TLSv1.2"].startswith("accepted") and outcomes["TLSv1.3"].startswith("accepted")
    assert outcomes["TLSv1"].startswith("refused") and outcomes["TLSv1.1"].startswith("refused")
    record("; ".join(f"{k}: {v}" for k, v in outcomes.items()))


# --------------------------------------------------------------------------
# TC-SEC-04: password hashing (APAS-SR-004)
# --------------------------------------------------------------------------
@tc("TC-SEC-04.1", "APAS-SR-004", type="Security")
def test_passwords_hashed_not_plaintext(db, db_path, record):
    """Passwords are stored as salted PBKDF2 hashes, never in plaintext
    Objective: Verify password storage in the users table and the raw database file.
    Preconditions: 9 seeded accounts.
    Steps:
    1. Read users.password_hash for every account.
    2. Search the raw database file bytes for each plaintext password.
    Expected: Every hash uses pbkdf2:sha256 with >= 600000 iterations and a salt; no hash equals or contains the plaintext; no plaintext password occurs anywhere in the database file.
    """
    rows = db.execute("SELECT username, password_hash FROM users").fetchall()
    raw = db_path.read_bytes()
    for r in rows:
        method, salt, digest = r["password_hash"].split("$")
        algo, hash_name, iterations = method.split(":")
        assert algo == "pbkdf2" and hash_name == "sha256" and int(iterations) >= 600000
        assert len(salt) >= 16 and len(digest) == 64
        assert PASSWORDS[r["username"]] not in r["password_hash"]
        assert PASSWORDS[r["username"]].encode() not in raw
    record(f"{len(rows)} accounts: pbkdf2:sha256:{iterations}, salt length {len(salt)}, 64-hex digest; "
           f"no plaintext passwords found in DB file ({len(raw)} bytes scanned)")


@tc("TC-SEC-04.2", "APAS-SR-004", type="Security")
def test_hash_salting_and_verification(app, record):
    """Identical passwords produce different hashes; verification works
    Objective: Verify per-user salting and correct password verification.
    Steps:
    1. Hash the same password twice.
    2. Verify the correct and an incorrect password against the hash.
    Expected: The two hashes differ; correct password verifies True; incorrect verifies False.
    """
    from apas.security import hash_password, verify_password
    h1, h2 = hash_password("Same@Password1"), hash_password("Same@Password1")
    assert h1 != h2
    assert verify_password(h1, "Same@Password1") and not verify_password(h1, "same@password1")
    record("same password -> 2 different hashes; correct verifies True; case-changed password verifies False")


@tc("TC-SEC-04.3", "APAS-SR-004", type="Security")
def test_password_never_returned(client, login, record):
    """Password hashes are never exposed by the API
    Objective: Verify that no API response contains password data.
    Steps:
    1. Log in and call dashboard, student and audit endpoints as admin.
    Expected: No response body contains "password_hash", "pbkdf2" or a plaintext password.
    """
    h = login("admin")
    bodies = [client.post("/api/auth/login", json={"username": "admin", "password": PASSWORDS["admin"]}).data,
              client.get("/api/dashboard", headers=h).data, client.get("/api/students", headers=h).data,
              client.get("/api/audit", headers=h).data]
    for b in bodies:
        assert b"password_hash" not in b and b"pbkdf2" not in b and PASSWORDS["admin"].encode() not in b
    record(f"{len(bodies)} responses scanned; no password data found")


# --------------------------------------------------------------------------
# TC-SEC-05: security event logging (APAS-SR-005)
# --------------------------------------------------------------------------
def audit_entries(db, **where):
    sql = "SELECT * FROM audit_log" + (" WHERE " + " AND ".join(f"{k} = ?" for k in where) if where else "")
    return [dict(r) for r in db.execute(sql + " ORDER BY id", tuple(where.values()))]


@tc("TC-SEC-05.1", "APAS-SR-005", type="Security")
def test_login_attempts_logged(client, db, record):
    """Successful and failed login attempts are logged with user, event type and timestamp
    Objective: Verify security logging of authentication events.
    Steps:
    1. Log in successfully as fac.rao.
    2. Fail a login for fac.rao (wrong password) and for unknown user "ghost".
    3. Read the audit log.
    Expected: Three auth.login entries: success (fac.rao, user id), failure (fac.rao, "wrong password"), failure (ghost, "unknown user"); each with an ISO-8601 UTC timestamp within 60 s of now.
    """
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    client.post("/api/auth/login", json={"username": "fac.rao", "password": PASSWORDS["fac.rao"]})
    client.post("/api/auth/login", json={"username": "fac.rao", "password": "wrong"})
    client.post("/api/auth/login", json={"username": "ghost", "password": "wrong"})
    logs = audit_entries(db, event_type="auth.login")
    summary = [(e["username"], e["outcome"], json.loads(e["details"]).get("reason")) for e in logs]
    assert summary == [("fac.rao", "success", None), ("fac.rao", "failure", "wrong password"),
                       ("ghost", "failure", "unknown user")]
    assert logs[0]["user_id"] is not None and logs[2]["user_id"] is None
    for e in logs:
        ts = datetime.fromisoformat(e["ts"])
        assert ts.tzinfo is not None and before <= ts <= datetime.now(timezone.utc) + timedelta(seconds=60)
    record(f"entries={summary}; timestamps {[e['ts'] for e in logs]}")


@tc("TC-SEC-05.2", "APAS-SR-005", type="Security")
def test_modifications_and_denials_logged(client, login, db, record):
    """Academic record changes and denied access attempts are logged
    Objective: Verify security logging of record modifications and authorisation failures.
    Steps:
    1. fac.rao updates Kabir AM301 ISA 20 -> 25.
    2. aarav tries to read Kabir's grades.
    3. Read the audit log.
    Expected: grade.update entry with user fac.rao, entity PES1UG24AM003, old 20, new 25; access.denied entry for aarav with the requested path.
    """
    client.post("/api/students/PES1UG24AM003/grades", headers=login("fac.rao"),
                json={"subject_code": "AM301", "assessment": "ISA", "score": 25})
    client.get("/api/students/PES1UG24AM003/grades", headers=login("aarav"))
    upd = audit_entries(db, event_type="grade.update")[-1]
    denied = audit_entries(db, event_type="access.denied")[-1]
    d = json.loads(upd["details"])
    assert upd["username"] == "fac.rao" and upd["entity"] == "PES1UG24AM003" and (d["old"], d["new"]) == (20, 25)
    assert denied["username"] == "aarav" and denied["outcome"] == "failure" and "PES1UG24AM003" in denied["details"]
    record(f"grade.update by {upd['username']} {d} at {upd['ts']}; access.denied for {denied['username']} {denied['details']}")


@tc("TC-SEC-05.3", "APAS-SR-005", type="Security")
def test_no_secrets_in_logs(client, db, record):
    """Passwords and session tokens are never written to the audit log
    Objective: Verify SAD 4.4.2 (sensitive authentication information must not be logged).
    Steps:
    1. Perform successful and failed logins.
    2. Search all audit_log columns for passwords and the issued token.
    Expected: No password or token text appears in the audit log.
    """
    token = client.post("/api/auth/login", json={"username": "admin", "password": PASSWORDS["admin"]}).get_json()["token"]
    client.post("/api/auth/login", json={"username": "admin", "password": "Typo@Password"})
    dump = json.dumps(audit_entries(db))
    for secret in (PASSWORDS["admin"], "Typo@Password", token):
        assert secret not in dump
    record(f"{len(audit_entries(db))} audit entries scanned; no passwords or tokens present")


@tc("TC-SEC-05.4", ["APAS-SR-005", "APAS-NF-003"], type="Security")
@pytest.mark.parametrize("path", ["/api/students/..%2F..%2Fetc%2Fpasswd", "/api/students/PES1'%20OR%20'1'='1",
                                  "/api/analytics/performance/%3Cscript%3E"])
def test_malicious_input_handled_safely(client, login, record, path):
    """Malicious path parameters are handled safely
    Objective: Verify input validation does not cause errors or data exposure (STP 5.6 Input Validation).
    Test data: Path traversal, SQL injection and script injection in the student ID.
    Steps:
    1. GET the URL as fac.rao.
    Expected: HTTP 404 "Student not found" (no HTTP 500, no stack trace).
    """
    resp = client.get(path, headers=login("fac.rao"))
    assert resp.status_code == 404 and b"Traceback" not in resp.data
    record(f"{path} -> HTTP {resp.status_code} '{resp.get_json()['error']}'")
