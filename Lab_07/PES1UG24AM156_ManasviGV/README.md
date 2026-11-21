# Lab 7 – Fuzz Testing: Coupon Validator

**Manasvi G V (PES1UG24AM156)**, Team 05. Assigned repo: `L6_L7_31_coupon_validator` (lab7).

## Functions tested

| Function | Purpose |
|---|---|
| `split_code()` | Splits a coupon code such as `save-20` into `('SAVE', 20)` |
| `most_expensive()` | Returns the highest price from a CSV such as `199,49.5,320` |
| `expiry_days()` | Converts a `YYYY-MM-DD` date into a day number counted from 2024-01-01 |

## Approach

- Fuzz tests with `st.text() | st.none()` (500 examples per function): no input may crash a function.
- Structured fuzzing with near-valid characters (`-`, `,`, digits, `nan`, `inf`, `²`) to reach deeper code paths.
- Property tests on valid input: `split_code` round-trips, `most_expensive` equals `max()`, and `expiry_days`
  increases by exactly 1 per day and matches the real calendar.
- The minimal failing inputs Hypothesis reported are kept as regression examples.

## Bugs found and fixed

| Function | Failing input | Problem | Fix |
|---|---|---|---|
| all three | `None` | `AttributeError` | Non-string input returns `None` |
| `split_code` | `''`, `save`, `save-20-30` | `ValueError` (unpack) | Strict `PREFIX-NUMBER` pattern |
| `split_code` | `save-abc`, `save-²` | `ValueError` from `int()` (`'²'` passes `isdigit()`) | ASCII digits only |
| `split_code` | `save-` + 5000 digits | `ValueError`: 4300-digit int limit | At most 9 digits |
| `split_code` | `-20`, `sa ve-20` | Wrong result `('', 20)` | Prefix must be letters/digits |
| `most_expensive` | `''`, `abc`, `199,,320` | `ValueError` from `float()` | Empty items skipped; invalid item returns `None` |
| `most_expensive` | `nan`, `inf`, `1e400`, `-5` | Wrong result (nan/inf/negative) | Reject non-finite and negative prices |
| `expiry_days` | `''`, `2024-01`, `2024/01/01` | `ValueError` | Strict `YYYY-MM-DD` pattern |
| `expiry_days` | `2024-02-30`, `2024-13-01` | Impossible dates accepted | Validated with `datetime.date` |
| `expiry_days` | 2024-01-31 vs 2024-02-01 | Both gave 31 (30-day months) | Real calendar day count |

## Results

| Run | Result |
|---|---|
| Buggy code | 41 failed, 2 passed |
| Fixed code | **43 passed** (repeated with 5 random seeds) |

Valid input gives the same results as the original code: `save-20` → `('SAVE', 20)`, `199,49.5,320` → `320.0`,
`2024-03-01` → `61`.

## Commands

```bash
pip install pytest hypothesis
python coupon_validator.py
python -m pytest -v test_coupon_validator.py
```

## Files

| File | Description |
|---|---|
| `coupon_validator.py` | Fixed application |
| `test_coupon_validator.py` | Completed Hypothesis tests |
| `PES1UG24AM156_ManasviGV_Lab7.pdf` | Report with screenshots |
| `ss1.png` – `ss4.png` | Screenshots for steps 2, 4, 5, 6 |
