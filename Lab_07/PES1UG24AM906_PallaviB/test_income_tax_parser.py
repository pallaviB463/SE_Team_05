import pytest
from hypothesis import given, strategies as st
from income_tax_parser import clean_pan, parse_amount, parse_tax_slab

@given(st.text() | st.none())
def test_clean_pan_no_crash(s):
    try:
        clean_pan(s)
    except Exception as e:
        pytest.fail(f"clean_pan crashed on input {s!r} with {type(e).__name__}: {e}")

@given(st.text() | st.none())
def test_parse_amount_no_crash(s):
    try:
        parse_amount(s)
    except Exception as e:
        pytest.fail(f"parse_amount crashed on input {s!r} with {type(e).__name__}: {e}")

@given(st.text() | st.none())
def test_parse_tax_slab_no_crash(s):
    try:
        parse_tax_slab(s)
    except Exception as e:
        pytest.fail(f"parse_tax_slab crashed on input {s!r} with {type(e).__name__}: {e}")
