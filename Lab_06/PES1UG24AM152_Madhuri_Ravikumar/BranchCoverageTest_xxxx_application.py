
import pytest
from traffic_fine import speeding_fine, license_action, total_penalty


# Speeding fine: speed limit branches
def test_speed_equal_to_limit():
    assert speeding_fine(60, 60, "city") == 0


def test_speed_below_limit():
    assert speeding_fine(50, 60, "city") == 0


def test_speed_above_limit():
    assert speeding_fine(70, 60, "city") == 500


# Speeding fine: zone branches
def test_school_zone():
    assert speeding_fine(70, 60, "school") == 2000


def test_highway_zone():
    assert speeding_fine(70, 60, "highway") == 1000


def test_other_zone():
    assert speeding_fine(70, 60, "city") == 500


# Speeding fine: excess speed branches
def test_excess_equal_to_40():
    assert speeding_fine(100, 60, "city") == 1000


def test_excess_above_40():
    assert speeding_fine(101, 60, "city") == 1500


def test_excess_equal_to_20():
    assert speeding_fine(80, 60, "city") == 500


def test_excess_between_20_and_40():
    assert speeding_fine(81, 60, "city") == 1000


def test_excess_below_20():
    assert speeding_fine(70, 60, "city") == 500


# License action: points >= 12
def test_points_12_commercial():
    assert license_action(12, True, False) == "revoke"


def test_points_12_non_commercial():
    assert license_action(12, False, False) == "suspend"


# License action: points >= 8
def test_points_8_repeat_offender():
    assert license_action(8, False, True) == "suspend"


def test_points_8_not_repeat_offender():
    assert license_action(8, False, False) == "warning"


# License action: points >= 4
def test_points_4():
    assert license_action(4, False, False) == "notice"


# License action: points below 4
def test_points_below_4():
    assert license_action(3, False, False) == "none"


# Total penalty branches
def test_empty_fines():
    assert total_penalty([]) == 0


def test_positive_fines():
    assert total_penalty([100, 200, 300]) == 600


def test_negative_fine_branch():
    with pytest.raises(ValueError):
        total_penalty([-100])


def test_total_equal_to_10000():
    assert total_penalty([5000, 5000]) == 10000


def test_total_above_10000():
    assert total_penalty([6000, 6000]) == 10000
