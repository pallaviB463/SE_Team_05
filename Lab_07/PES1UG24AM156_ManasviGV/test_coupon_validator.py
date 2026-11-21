import math
import string
from datetime import date, timedelta

import pytest
from hypothesis import given, settings, strategies as st

from coupon_validator import split_code, most_expensive, expiry_days

# --------------------------------------------------------------------------
# Fuzz tests (lab starter): random text or None must never crash a function.
# --------------------------------------------------------------------------
ANY_INPUT = st.text() | st.none()


@settings(max_examples=500)
@given(ANY_INPUT)
def test_split_code_no_crash(s):
    try:
        split_code(s)
    except Exception as e:
        pytest.fail(f"split_code crashed on {s!r} with {type(e).__name__}: {e}")


@settings(max_examples=500)
@given(ANY_INPUT)
def test_most_expensive_no_crash(s):
    try:
        most_expensive(s)
    except Exception as e:
        pytest.fail(f"most_expensive crashed on {s!r} with {type(e).__name__}: {e}")


@settings(max_examples=500)
@given(ANY_INPUT)
def test_expiry_days_no_crash(s):
    try:
        expiry_days(s)
    except Exception as e:
        pytest.fail(f"expiry_days crashed on {s!r} with {type(e).__name__}: {e}")


# --------------------------------------------------------------------------
# Structured fuzzing: inputs that look almost valid (delimiters, digits,
# signs, special float words) reach deeper code paths than plain random text.
# --------------------------------------------------------------------------
NEAR_CODE = st.text(alphabet="saveSAVE-0123456789 ²٣_", max_size=12)
NEAR_CSV = st.text(alphabet="0123456789.,-+eEinfatyNIA _", max_size=20)
NEAR_DATE = st.text(alphabet="0123456789-/ ", max_size=12)


@given(NEAR_CODE)
def test_split_code_near_valid_no_crash(s):
    split_code(s)


@given(NEAR_CSV)
def test_most_expensive_near_valid_no_crash(s):
    most_expensive(s)


@given(NEAR_DATE)
def test_expiry_days_near_valid_no_crash(s):
    expiry_days(s)


# --------------------------------------------------------------------------
# Property tests on valid input: the answers must also be correct.
# --------------------------------------------------------------------------
PREFIX = st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=10)


@given(PREFIX, st.integers(min_value=0, max_value=10**6), st.sampled_from(["", " ", "\t"]))
def test_split_code_round_trip(prefix, value, pad):
    assert split_code(f"{pad}{prefix.lower()}-{value}{pad}") == (prefix.upper(), value)


PRICE = st.floats(min_value=0, max_value=1e9, allow_nan=False, allow_infinity=False)


@given(st.lists(PRICE, min_size=1, max_size=20))
def test_most_expensive_returns_max(prices):
    csv_text = ",".join(repr(p) for p in prices)
    assert most_expensive(csv_text) == max(prices)


@given(st.dates(min_value=date(2024, 1, 1), max_value=date(2099, 12, 30)))
def test_expiry_days_next_day_is_one_more(d):
    tomorrow = d + timedelta(days=1)
    assert expiry_days(tomorrow.isoformat()) - expiry_days(d.isoformat()) == 1


@given(st.dates(min_value=date(2024, 1, 1), max_value=date(2099, 12, 31)))
def test_expiry_days_matches_calendar(d):
    assert expiry_days(d.isoformat()) == (d - date(2024, 1, 1)).days + 1


# --------------------------------------------------------------------------
# Known edge cases (minimal failing inputs Hypothesis reported on the buggy
# version) - invalid input is rejected with None instead of a crash.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("code", [None, "", "   ", "save", "save-", "-20", "save-20-30",
                                  "save-abc", "save-²", "save--5", "sa ve-20",
                                  pytest.param("save-" + "9" * 5000, id="save-<5000 digits>")])
def test_split_code_rejects_invalid(code):
    assert split_code(code) is None


@pytest.mark.parametrize("csv_text", [None, "", ",", "abc", "199,abc", "nan", "inf", "1e400",
                                      "-5,10", "NaN,3"])
def test_most_expensive_rejects_invalid(csv_text):
    assert most_expensive(csv_text) is None


@pytest.mark.parametrize("date_text", [None, "", "2024", "2024-01", "2024-13-01", "2024-02-30",
                                       "2023-02-29", "2024-1-1-1", "abcd-ef-gh", "2024/01/01"])
def test_expiry_days_rejects_invalid(date_text):
    assert expiry_days(date_text) is None


def test_examples_from_prompts():
    assert split_code("save-20") == ("SAVE", 20)
    assert most_expensive("199,49.5,320") == 320.0
    assert most_expensive(" 199 , ,49.5,320 ") == 320.0
    assert expiry_days("2024-01-01") == 1
    assert expiry_days("2024-03-01") == 61
    assert math.isfinite(most_expensive("1e308"))
