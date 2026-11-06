import pytest
from coupon_validator import coupon_discount, best_discount, is_expired


# ---------- coupon_discount ----------

def test_welcome_coupon_new_user():
    assert coupon_discount("WELCOME10", 200, True, "mon") == 20


def test_welcome_coupon_existing_user():
    assert coupon_discount("WELCOME10", 200, False, "mon") == 0


def test_empty_cart_raises():
    with pytest.raises(ValueError):
        coupon_discount("WELCOME10", 0, True, "mon")


def test_weekend_big_cart():
    assert coupon_discount("WEEKEND20", 600, False, "sat") == 120


def test_weekend_small_cart():
    assert coupon_discount("WEEKEND20", 200, False, "sun") == 50


def test_weekend_coupon_on_weekday():
    assert coupon_discount("WEEKEND20", 600, False, "tue") == 0


def test_flat100_above_300():
    assert coupon_discount("FLAT100", 400, False, "mon") == 100


def test_flat100_below_300():
    assert coupon_discount("FLAT100", 200, False, "mon") == 0


def test_unknown_code():
    assert coupon_discount("BOGUS", 200, True, "mon") == 0


# ---------- best_discount ----------

def test_best_discount_picks_highest():
    assert best_discount(["WELCOME10", "FLAT100"], 400, True, "mon") == 100


def test_best_discount_capped_at_40_percent():
    # WEEKEND20 gives 50 on a 100 cart, but the cap is 40
    assert best_discount(["WEEKEND20"], 100, False, "sat") == 40


# ---------- is_expired ----------

def test_zero_validity_expired():
    assert is_expired(10, 5, 0) is True


def test_not_expired():
    assert is_expired(10, 5, 10) is False
