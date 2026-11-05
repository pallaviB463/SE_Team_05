import pytest
from income_tax import taxable_income, tax_due, refund_status


# ---------- taxable_income ----------
def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000

def test_negative_income_raises():
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)

def test_old_regime_investments_capped():
    # investments 200000 capped to 150000 -> deduction 200000
    assert taxable_income(1000000, "old", 200000) == 800000

def test_unknown_regime_raises():
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "foo", 0)

def test_taxable_income_floors_at_zero():
    assert taxable_income(50000, "new", 0) == 0


# ---------- tax_due ----------
def test_below_exemption():
    assert tax_due(200000, 30) == 0

def test_negative_taxable_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-5, 30)

def test_super_senior_exemption():
    assert tax_due(600000, 85) == 5000          # (600000-500000)*5%

def test_senior_exemption():
    assert tax_due(400000, 65) == 5000          # (400000-300000)*5%

def test_first_slab_regular_age():
    assert tax_due(400000, 30) == 7500          # (400000-250000)*5%

def test_second_slab():
    assert tax_due(800000, 30) == 12500 + 300000 * 20 // 100   # 72500


# ---------- refund_status ----------
def test_refund_on_time():
    assert refund_status(10000, 5000, True) == "refund"

def test_refund_delayed():
    assert refund_status(10000, 5000, False) == "refund delayed"

def test_pay_balance_on_time():
    assert refund_status(5000, 10000, True) == "pay balance"

def test_pay_balance_with_penalty():
    assert refund_status(5000, 10000, False) == "pay balance with penalty"

def test_settled():
    assert refund_status(5000, 5000, True) == "settled"


# ================= Additional tests for BRANCH coverage =================
# taxable_income: old regime with investments <= 150000 (cap NOT applied) -> branch 7->9
def test_old_regime_investments_below_cap():
    assert taxable_income(1000000, "old", 100000) == 850000   # deduction 150000

def test_old_regime_investments_exactly_at_cap():
    assert taxable_income(1000000, "old", 150000) == 800000   # 150000 is not > cap

def test_taxable_income_exactly_zero():
    assert taxable_income(75000, "new", 0) == 0               # taxable == 0, not < 0

def test_zero_gross_is_valid():
    assert taxable_income(0, "new", 0) == 0                   # gross == 0 is not invalid

# tax_due: boundaries of every decision
def test_taxable_zero_is_valid():
    assert tax_due(0, 30) == 0

def test_age_boundary_60():
    assert tax_due(300000, 60) == 0                           # age 60 -> exempt 300000
    assert tax_due(59, 59) == 0                               # age 59 -> exempt 250000

def test_age_boundary_80():
    assert tax_due(500000, 80) == 0                           # age 80 -> exempt 500000
    assert tax_due(500000, 79) == 10000                       # age 79 -> exempt 300000

def test_exactly_at_exemption_limit():
    assert tax_due(250000, 30) == 0

def test_slab_exactly_250000():
    assert tax_due(500000, 30) == 12500                       # slab == 250000 -> first slab

def test_slab_just_above_250000():
    assert tax_due(500001, 30) == 12500                       # 12500 + 1*20//100 = 12500
    assert tax_due(500100, 30) == 12520                       # 12500 + 100*20//100
