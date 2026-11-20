
# Fuzz Testing – Lab 7

## 1. Introduction

Fuzz testing is a software testing technique in which a program is provided with a large variety of inputs, including unexpected, invalid, random, and malformed values, to identify errors and weaknesses.

The main purpose of fuzz testing is to examine how an application behaves when it receives inputs that may not follow the expected format.

In this lab, fuzz testing was performed on a Traffic Fine Application using Python's Hypothesis library and the Pytest framework.

## 2. Application Under Test

The application consists of three functions:

| Function | Purpose |
|---|---|
| `parse_ticket_id()` | Parses a ticket ID into prefix, year, and serial number |
| `total_fines()` | Calculates the total fine amount from comma-separated values |
| `speed_excess()` | Calculates the percentage of speed exceeding the speed limit |

Each function accepts user input and performs operations on that input. Therefore, invalid or unexpected values may cause errors if proper validation is not implemented.

## 3. Tools Used

### Pytest

Pytest is a Python testing framework used to execute test cases and verify whether the application behaves as expected.

### Hypothesis

Hypothesis is a property-based testing library for Python. Instead of relying only on manually written test inputs, it automatically generates multiple inputs and checks whether the defined properties hold.

The `@given` decorator is used to supply generated inputs to test functions.

The following strategies were used:

- `st.text()` – Generates different strings.
- `st.none()` – Generates None values.
- `st.integers()` – Generates integer values.
- `st.text().filter()` – Generates strings satisfying a specified condition.

## 4. Fuzz Testing Methodology

The following steps were followed:

### Step 1: Identify Input Functions

The three functions in `traffic_fine.py` were selected as fuzz testing targets because they process user-provided inputs.

### Step 2: Generate Different Inputs

Hypothesis was used to generate different input values, including arbitrary strings and None values.

This helped test whether the functions could handle unexpected inputs without producing unintended runtime errors.

### Step 3: Test Valid Inputs

Valid input values were supplied to verify that the functions produced the expected results.

Examples:

| Function | Input | Expected Output |
|---|---|---|
| `parse_ticket_id()` | `TF-2024-0456` | `('TF', 2024, 456)` |
| `total_fines()` | `500,1200,300` | `2000` |
| `speed_excess()` | `72/60` | `20` |

### Step 4: Test Invalid and Boundary Inputs

Additional tests were written to check malformed ticket IDs, negative fine amounts, zero speed limits, and negative speed limits.

### Step 5: Fix Validation Issues

The initial tests exposed several input-validation problems:

1. Negative fine amounts were accepted.
2. A zero speed limit caused a division-by-zero error.
3. Negative speed limits were accepted.

Input-validation checks were added to the application to handle these cases appropriately.

### Step 6: Execute the Final Test Suite

The tests were executed using:

```bash
pytest -v
```

The final execution completed with all 13 tests passing.

## 5. Test Cases

The following test cases were implemented in `test_traffic_fine.py`.

| No. | Test Case | Purpose |
|---|---|---|
| 1 | Ticket ID fuzz testing | Tests generated strings and None values |
| 2 | Valid ticket ID | Checks correct ticket parsing |
| 3 | Total fines fuzz testing | Tests generated fine input values |
| 4 | Valid total fines | Checks correct fine calculation |
| 5 | Speed excess fuzz testing | Tests generated speed readings |
| 6 | Valid speed excess | Checks correct percentage calculation |
| 7 | Fine maximum limit | Checks that total fines are capped at 10,000 |
| 8 | Zero speed limit | Checks rejection of a zero speed limit |
| 9 | Invalid ticket ID | Checks rejection of an invalid ticket format |
| 10 | Negative fines | Checks rejection of negative fine amounts |
| 11 | Zero limit validation | Checks rejection of a zero speed limit |
| 12 | Negative speed limit | Checks rejection of negative speed limits |
| 13 | Malformed ticket ID | Checks rejection of ticket IDs with an incorrect number of separators |

## 6. Issues Identified and Fixes

| Issue Identified | Corrective Action |
|---|---|
| Negative fine values were accepted | Added validation to reject negative amounts |
| Zero speed limit caused division by zero | Added validation requiring the speed limit to be greater than zero |
| Negative speed limits were accepted | Added validation to reject non-positive speed limits |
| Malformed ticket IDs were not properly validated | Added checks for the required ticket ID structure |
| Non-integer numeric fields could cause conversion errors | Added exception handling for integer conversion |

The validation changes ensure that invalid inputs raise `ValueError` instead of allowing unintended calculations or errors.

## 7. Final Test Results

The final test suite was executed using:

```bash
pytest -v
```

**Observed result:**

```text
13 passed in 1.14s
```

| Metric | Result |
|---|---:|
| Total test cases | 13 |
| Passed | 13 |
| Failed | 0 |
| Execution time | 1.14 seconds |

All implemented tests passed successfully.

## 8. Application Execution

The application was also executed independently using valid sample inputs.

**Input:**

```text
TF-2024-0456
500,1200,300
72/60
```

**Output:**

```text
Ticket Prefix, Year and Serial: ('TF', 2024, 456)
Total Fines: 2000
Percent Over Limit: 20
```

The output confirms that the three functions produce the expected results for the selected valid inputs.

## 9. Screenshots

The following screenshots provide evidence of the implementation and testing:

1. Application output – demonstrates successful execution of the application.
2. Pytest results – demonstrates the final test execution with 13 passing tests.
3. Fuzz testing workflow – illustrates how generated inputs are passed to the application and verified through automated tests.

## 10. Conclusion

Fuzz testing was performed on the Traffic Fine Application using Hypothesis and Pytest.

The testing process examined valid inputs, arbitrary generated strings, None values, malformed ticket IDs, and boundary conditions involving fine amounts and speed limits.

The initial tests helped identify input-validation issues. These issues were addressed by adding appropriate validation and exception handling to the application.

After the changes, all 13 tests passed successfully.

The lab demonstrates how property-based testing can be used to explore a wider range of inputs than manually written test cases alone and improve the robustness of an application.

