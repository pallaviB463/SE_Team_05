# Lab 7 – Fuzz Testing

## Objective
Perform fuzz testing on a Python Pet Boarding application using Hypothesis and pytest to identify unexpected crashes and validate input handling.

## Functions Tested
1. `parse_booking()` – Parses pet type and boarding duration.
2. `stay_average()` – Calculates average boarding duration.
3. `payable_fee()` – Calculates the payable amount after applying an 18% increase and subtracting the discount.

## Testing Approach
- Used Hypothesis to generate randomized inputs.
- Tested valid, invalid, empty, and unexpected input types.
- Added input validation and exception handling to prevent crashes.
- Verified expected results using pytest assertions.

## Test Results
- **Total tests:** 38
- **Passed:** 38
- **Failed:** 0
- **Randomized no-crash test examples:** 1,500 configured across three Hypothesis tests.

## Execution Commands

```powershell
python -m pip install pytest hypothesis
python -m pytest -v test_pet_boarding.py
python -m pytest -v -s test_pet_boarding.py
python pet_boarding.py
```

## Evidence
- `Pytest_Results_SS.png` – Passing pytest results.
- `FuzzTesting_SS.png` – Hypothesis fuzz test execution.
- `ApplicationOutput_SS.png` – Successful application execution.

## Conclusion
The updated Pet Boarding application successfully passed all 38 tests, including randomized fuzz tests and validation of malformed inputs. No test failures were observed in the final execution.
