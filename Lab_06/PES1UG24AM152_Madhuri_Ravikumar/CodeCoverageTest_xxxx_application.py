"""
Code Coverage Test Suite
Tests all major functions in the traffic fine application.
"""
import pytest
from traffic_fine import speeding_fine, license_action, total_penalty


# ---------------- CODE COVERAGE TEST CASES ----------------

# Speeding fine tests
def test_no_speeding():
    assert speeding_fine(50, 60, "city") == 0


def test_school_zone_normal_speeding():
    assert speeding_fine(70, 60, "school") == 2000


def test_highway_zone_normal_speeding():
    assert speeding_fine(70, 60, "highway") == 1000


def test_city_zone_normal_speeding():
    assert speeding_fine(70, 60, "city") == 500


def test_speeding_above_20():
    assert speeding_fine(85, 60, "city") == 1000


def test_speeding_above_40():
    assert speeding_fine(105, 60, "city") == 1500


# License action tests
def test_clean_record():
    assert license_action(2, False, False) == "none"


def test_notice_action():
    assert license_action(5, False, False) == "notice"


def test_warning_action():
    assert license_action(9, False, False) == "warning"


def test_suspension_action_repeat_offender():
    assert license_action(9, False, True) == "suspend"


def test_suspension_action_commercial():
    assert license_action(12, False, False) == "suspend"


def test_revoke_commercial_license():
    assert license_action(12, True, False) == "revoke"


# Total penalty tests
def test_total_penalty_normal():
    assert total_penalty([100, 200, 300]) == 600


def test_total_penalty_empty():
    assert total_penalty([]) == 0


def test_total_penalty_cap():
    assert total_penalty([6000, 6000]) == 10000


def test_negative_fine():
    with pytest.raises(ValueError):
        total_penalty([100, -50])
