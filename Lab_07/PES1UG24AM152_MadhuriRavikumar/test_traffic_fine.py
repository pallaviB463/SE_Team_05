
import pytest
from hypothesis import given, strategies as st

from traffic_fine import parse_ticket_id, total_fines, speed_excess


# 1. Ticket ID fuzz testing
@given(st.text() | st.none())
def test_parse_ticket_id_no_crash(s):
    try:
        parse_ticket_id(s)
    except (ValueError, TypeError, AttributeError):
        pass


# 2. Valid ticket ID
def test_parse_ticket_id_valid():
    assert parse_ticket_id("TF-2024-0456") == ("TF", 2024, 456)


# 3. Total fines fuzz testing
@given(st.text() | st.none())
def test_total_fines_no_crash(s):
    try:
        total_fines(s)
    except (ValueError, TypeError, AttributeError):
        pass


# 4. Valid total fines
def test_total_fines_valid():
    assert total_fines("500,1200,300") == 2000


# 5. Speed excess fuzz testing
@given(st.text() | st.none())
def test_speed_excess_no_crash(s):
    try:
        speed_excess(s)
    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        pass


# 6. Valid speed excess
def test_speed_excess_valid():
    assert speed_excess("72/60") == 20


# 7. Fine maximum limit
def test_total_fines_limit():
    assert total_fines("5000,7000") == 10000


# 8. Zero speed limit
def test_speed_excess_zero():
    with pytest.raises(ValueError):
        speed_excess("72/0")


# 9. Invalid ticket ID
def test_parse_ticket_id_invalid():
    with pytest.raises((ValueError, TypeError)):
        parse_ticket_id("INVALID")


# 10. Negative fines
@given(st.integers(max_value=-1))
def test_negative_fines_should_be_rejected(amount):
    with pytest.raises(ValueError):
        total_fines(str(amount))


# 11. Zero speed limit validation
def test_zero_limit_should_be_rejected():
    with pytest.raises(ValueError):
        speed_excess("72/0")


# 12. Negative speed limit
@given(st.integers(max_value=-1))
def test_negative_speed_limit_should_be_rejected(limit):
    with pytest.raises(ValueError):
        speed_excess(f"72/{limit}")


# 13. Malformed ticket ID
@given(st.text().filter(lambda s: s.count("-") != 2))
def test_malformed_ticket_id_should_be_rejected(ticket_id):
    with pytest.raises(ValueError):
        parse_ticket_id(ticket_id)
