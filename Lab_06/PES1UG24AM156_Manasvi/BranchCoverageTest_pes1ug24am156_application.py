import pytest
from coupon_validator import coupon_discount, best_discount, is_expired


# ---------- coupon_discount: every if takes both True and False ----------

def test_empty_cart_raises():
    with pytest.raises(ValueError):
        coupon_discount("WELCOME10", 0, True, "mon")


def test_negative_cart_raises():
    with pytest.raises(ValueError):
        coupon_discount("FLAT100", -50, True, "mon")


def test_welcome_coupon_new_user():
    assert coupon_discount("WELCOME10", 200, True, "mon") == 20


def test_welcome_coupon_existing_user():
    assert coupon_discount("WELCOME10", 200, False, "mon") == 0


def test_weekend_saturday_big_cart():
    assert coupon_discount("WEEKEND20", 600, False, "sat") == 120


def test_weekend_sunday_exactly_500():
    assert coupon_discount("WEEKEND20", 500, False, "sun") == 100


def test_weekend_small_cart_flat_50():
    assert coupon_discount("WEEKEND20", 499, False, "sat") == 50


def test_weekend_coupon_on_weekday():
    assert coupon_discount("WEEKEND20", 600, False, "fri") == 0


def test_flat100_above_300():
    assert coupon_discount("FLAT100", 301, False, "mon") == 100


def test_flat100_exactly_300():
    assert coupon_discount("FLAT100", 300, False, "mon") == 0


def test_unknown_code():
    assert coupon_discount("BOGUS", 200, True, "mon") == 0


# ---------- best_discount: loop entered/skipped, value > best both ways, cap both ways ----------

def test_best_discount_no_codes():
    assert best_discount([], 200, True, "mon") == 0


def test_best_discount_picks_highest_not_last():
    # FLAT100 (100) beats WELCOME10 (40) that comes after it -> "value > best" False path
    assert best_discount(["FLAT100", "WELCOME10"], 400, True, "mon") == 100


def test_best_discount_all_zero():
    assert best_discount(["BOGUS", "WELCOME10"], 200, False, "mon") == 0


def test_best_discount_capped_at_40_percent():
    assert best_discount(["WEEKEND20"], 100, False, "sat") == 40


def test_best_discount_under_cap():
    assert best_discount(["WEEKEND20"], 1000, False, "sun") == 200


# ---------- is_expired ----------

def test_zero_validity_expired():
    assert is_expired(10, 5, 0) is True


def test_negative_validity_expired():
    assert is_expired(10, 5, -3) is True


def test_past_validity_expired():
    assert is_expired(20, 5, 10) is True


def test_last_valid_day_not_expired():
    assert is_expired(15, 5, 10) is False
