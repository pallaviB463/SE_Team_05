
import math
import pytest

from hypothesis import given, settings, strategies as st
from pet_boarding import parse_booking, stay_average, payable_fee


# ---------------------------------
# FUZZ TEST 1: PARSE BOOKING
# ---------------------------------

@given(st.text() | st.none())
@settings(max_examples=500)
def test_parse_booking_no_crash(s):
    result = parse_booking(s)
    assert result is None or isinstance(result, tuple)


@given(
    pet=st.sampled_from(["dog", "cat", "rabbit"]),
    days=st.integers(min_value=0, max_value=1000)
)
def test_parse_booking_valid(pet, days):
    result = parse_booking(f"{pet}:{days}")
    assert result == (pet.title(), float(days))


@pytest.mark.parametrize("value", [
    "",
    "dog",
    "dog:abc",
    "dog:-5",
    "dog:",
    ":5",
    "dog:5:10",
    None,
    123,
    "dog:nan",
    "dog:inf",
])
def test_parse_booking_invalid(value):
    assert parse_booking(value) is None


# ---------------------------------
# FUZZ TEST 2: STAY AVERAGE
# ---------------------------------

@given(st.text() | st.none())
@settings(max_examples=500)
def test_stay_average_no_crash(s):
    result = stay_average(s)
    assert result is None or isinstance(result, int)


@given(
    st.lists(
        st.integers(min_value=0, max_value=1000),
        min_size=1,
        max_size=20
    )
)
def test_stay_average_valid(days):
    csv = ",".join(map(str, days))
    expected = sum(days) // len(days)
    assert stay_average(csv) == expected


@pytest.mark.parametrize("value", [
    "",
    "abc",
    "1,abc,3",
    "1,,3",
    "-1,2,3",
    None,
    123,
    "1.5,2.5",
])
def test_stay_average_invalid(value):
    assert stay_average(value) is None


# ---------------------------------
# FUZZ TEST 3: PAYABLE FEE
# ---------------------------------

@given(st.text() | st.none())
@settings(max_examples=500)
def test_payable_fee_no_crash(s):
    result = payable_fee(s)
    assert result is None or (
        isinstance(result, float) and math.isfinite(result)
    )


@given(
    fee=st.integers(min_value=0, max_value=100000),
    discount=st.integers(min_value=0, max_value=100000)
)
def test_payable_fee_valid(fee, discount):
    expected = max(fee * 1.18 - discount, 0)
    result = payable_fee(f"{fee}|{discount}")
    assert result == pytest.approx(expected)


@pytest.mark.parametrize("value", [
    "",
    "100",
    "abc|10",
    "100|abc",
    "100|",
    "|10",
    "100|10|5",
    "-100|10",
    "100|-10",
    "nan|10",
    "inf|10",
    None,
    123,
])
def test_payable_fee_invalid(value):
    assert payable_fee(value) is None
