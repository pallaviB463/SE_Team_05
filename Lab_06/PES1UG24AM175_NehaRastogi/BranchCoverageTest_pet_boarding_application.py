import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


def test_within_included_days():
    assert boarding_fee("dog", 1, False) == 0


def test_admission_ok():
    assert admission_ok(4, 2, False) is True


def test_invalid_pet():
    with pytest.raises(ValueError):
        boarding_fee("bird", 5, False)


def test_negative_days():
    with pytest.raises(ValueError):
        boarding_fee("cat", -1, False)


def test_premium_cat():
    assert boarding_fee("cat", 5, True) == 20


def test_premium_dog():
    assert boarding_fee("dog", 5, True) == 60


def test_rabbit_extra_days():
    assert boarding_fee("rabbit", 6, True) == 40


def test_dog_extra_days():
    assert boarding_fee("dog", 5, False) == 90


def test_dog_long_stay():
    assert boarding_fee("dog", 15, False) == 585


def test_cat_long_stay():
    assert boarding_fee("cat", 15, False) == 360


def test_senior_admission():
    assert admission_ok(8, 3, True) is True


def test_senior_insufficient_vaccinations():
    assert admission_ok(8, 1, True) is False


def test_young_pet():
    assert admission_ok(0.5, 3, False) is False


def test_insufficient_vaccinations():
    assert admission_ok(3, 1, False) is False


def test_checkout_open():
    assert checkout_status(40, True, False) == "open"


def test_checkout_late():
    assert checkout_status(20, True, False) == "late"


def test_checkout_closed():
    assert checkout_status(5, True, False) == "closed"


def test_checkout_short_stay():
    assert checkout_status(20, False, False) == "open"


def test_checkout_weekend():
    assert checkout_status(40, False, True) == "open"
