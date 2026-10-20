"""Shared fixtures and result recording for the APAS test suite.

Every test is tagged with @pytest.mark.tc(test_case_id, requirement_ids, ...). The hooks
at the bottom of this file write one record per test case (status, actual result,
duration, timestamp) to results/execution_results.json, which tools/generate_reports.py
turns into the test execution log, RTM status and report.
"""
import json
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path

from importlib import metadata

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from apas import create_app  # noqa: E402
from apas.db import connect  # noqa: E402
from apas.seed import DATA_FILE, load_dataset  # noqa: E402

RESULTS_DIR = ROOT / "results"
TEST_DATA = json.loads(DATA_FILE.read_text())
PASSWORDS = {u["username"]: u["password"] for u in TEST_DATA["users"]}


# --------------------------------------------------------------------------
# Application fixtures
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def template_db(tmp_path_factory):
    """Seed the synthetic dataset once; each test gets its own copy."""
    path = tmp_path_factory.mktemp("template") / "apas_template.db"
    conn = connect(path)
    load_dataset(conn, TEST_DATA)
    conn.close()
    return path


@pytest.fixture
def db_path(template_db, tmp_path):
    path = tmp_path / "apas.db"
    shutil.copy(template_db, path)
    return path


@pytest.fixture
def app(db_path):
    # Production configuration: HTTPS enforcement stays ON; the test client talks HTTPS.
    return create_app({"DATABASE": str(db_path)})


def https_client(app):
    """Test client whose requests are sent over https:// unless a base_url is given."""
    c = app.test_client()
    plain_open = c.open

    def open_https(*args, **kwargs):
        kwargs.setdefault("base_url", "https://localhost")
        return plain_open(*args, **kwargs)

    c.open = open_https
    return c


@pytest.fixture
def client(app):
    return https_client(app)


@pytest.fixture
def db(db_path):
    conn = connect(db_path)
    yield conn
    conn.close()


@pytest.fixture
def login(client):
    """login('fac.rao') -> Authorization headers for that user."""
    def _login(username, password=None):
        resp = client.post("/api/auth/login",
                           json={"username": username, "password": password or PASSWORDS[username]})
        assert resp.status_code == 200, resp.get_json()
        client.delete_cookie("apas_session")  # keep tests explicit: authenticate via header only
        return {"Authorization": f"Bearer {resp.get_json()['token']}"}
    return _login


@pytest.fixture
def record(request):
    """record('observed ...') stores the actual result for the execution log."""
    notes = []
    request.node.apas_actual = notes
    return notes.append


# --------------------------------------------------------------------------
# Result collection
# --------------------------------------------------------------------------
def pytest_configure(config):
    config._apas_results = []
    config._apas_started = datetime.now().astimezone()


def _parse_doc(doc):
    lines = [l.rstrip() for l in (doc or "").strip().splitlines()]
    spec = {"title": lines[0].strip() if lines else ""}
    key = None
    for line in lines[1:]:
        stripped = line.strip()
        head, sep, rest = stripped.partition(":")
        if sep and head in ("Objective", "Preconditions", "Test data", "Steps", "Expected"):
            key = head.lower().replace(" ", "_")
            spec[key] = rest.strip()
        elif key and stripped:
            spec[key] = (spec[key] + "\n" + stripped).strip()
    return spec


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    marker = item.get_closest_marker("tc")
    if marker is None:
        return
    if rep.when == "setup" and rep.passed:
        return
    if rep.when == "teardown" and rep.passed:
        return
    tc_id = marker.args[0]
    reqs = marker.args[1]
    entry = {
        "tc_id": tc_id,
        "requirements": [reqs] if isinstance(reqs, str) else list(reqs),
        "suite": item.module.__name__.replace("test_", ""),
        "function": item.name,
        "priority": marker.kwargs.get("priority", "High"),
        "test_type": marker.kwargs.get("type", "Functional"),
        "limitation": marker.kwargs.get("limitation"),
        "spec": _parse_doc(item.function.__doc__),
        "actual": list(getattr(item, "apas_actual", [])),
        "duration_s": round(rep.duration, 3),
        "executed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if rep.when == "call":
        entry["status"] = "Pass" if rep.passed else ("Not Executed" if rep.skipped else "Fail")
    elif rep.skipped:
        entry["status"] = "Blocked"
    else:
        entry["status"] = "Fail"
    if rep.failed:
        entry["failure"] = str(rep.longrepr.reprcrash.message if hasattr(rep.longrepr, "reprcrash")
                               else rep.longrepr)[:1500]
    if rep.skipped:
        entry["failure"] = str(rep.longrepr[2]) if isinstance(rep.longrepr, tuple) else str(rep.longrepr)
    results = item.config._apas_results
    results[:] = [r for r in results if r["function"] != item.name or r["suite"] != entry["suite"]]
    results.append(entry)


def pytest_sessionfinish(session, exitstatus):
    results = session.config._apas_results
    if not results:
        return
    RESULTS_DIR.mkdir(exist_ok=True)
    payload = {
        "started_at": session.config._apas_started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "environment": {
            "python": platform.python_version(),
            "flask": metadata.version("flask"),
            "pytest": pytest.__version__,
            "platform": platform.platform(),
            "database": "SQLite " + __import__("sqlite3").sqlite_version,
        },
        "results": sorted(results, key=lambda r: r["tc_id"]),
    }
    (RESULTS_DIR / "execution_results.json").write_text(json.dumps(payload, indent=2))
