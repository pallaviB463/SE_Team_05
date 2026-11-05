import pytest
from traffic_fine import speeding_fine, license_action, total_penalty

#Example test cases:
def test_no_speeding():
    assert speeding_fine(50, 60, "city") == 0

def test_clean_record():
    assert license_action(2, False, False) == "none"

#Write the rest of the test cases so that the code is 90- 100% covered.
