# Lab 7 – Fuzz Testing: Traffic Fine Application

## 1. Overview

This lab focuses on performing fuzz testing on a Python-based Traffic Fine Application using **Hypothesis** and **Pytest**.

The objective is to evaluate how the application handles valid, invalid, unexpected, and boundary-value inputs. Property-based testing is used to automatically generate different inputs and identify potential input-validation issues.

The application consists of three main functions:

1. `parse_ticket_id()` – Parses a ticket ID into its prefix, year, and serial number.
2. `total_fines()` – Calculates the total fine amount from comma-separated values, subject to a maximum limit of 10,000.
3. `speed_excess()` – Calculates the percentage by which a vehicle's speed exceeds the speed limit.

## 2. Objectives

- Understand the concept of fuzz testing.
- Generate different inputs automatically using Hypothesis.
- Test application behaviour with unexpected and malformed inputs.
- Identify input-validation issues and runtime errors.
- Improve application robustness through input validation.
- Verify the implementation using automated tests.

## 3. Technologies Used

- Python 3.11
- Pytest – Testing framework.
- Hypothesis – Property-based testing library.

## 4. Project Structure

```text
PES1UG24AM152_MadhuriRavikumar/
│
├── traffic_fine.py
├── test_traffic_fine.py
├── README.md
├── Fuzz_Testing_Baseline_Results.md
└── Screenshots.pdf
```

## 5. Application Implementation

### 5.1 Ticket ID Parsing

The `parse_ticket_id()` function accepts a ticket ID in the format:

`TF-2024-0456`

It separates the prefix, year, and serial number, converts the numeric fields into integers, and converts the prefix to uppercase.

Input validation is included to reject malformed ticket IDs and non-integer year or serial values.

### 5.2 Total Fine Calculation

The `total_fines()` function accepts comma-separated fine amounts.

Example:

`500,1200,300`

The function converts the values into integers and calculates their sum. If the total exceeds 10,000, the result is capped at 10,000.

Negative values and invalid fine amounts are rejected.

### 5.3 Speed Excess Calculation

The `speed_excess()` function accepts a speed reading in the format:

`72/60`

It calculates the percentage by which the recorded speed exceeds the speed limit.

Formula:

```python
(speed - limit) * 100 // limit
```

Invalid readings and zero or negative speed limits are rejected.

## 6. Installation

Install the required dependencies:

```bash
pip install pytest hypothesis
```

## 7. Running the Application

Execute:

```bash
python traffic_fine.py
```

Example inputs:

```text
Ticket ID: TF-2024-0456
Fine amounts: 500,1200,300
Speed/limit: 72/60
```

Expected results:

```text
Ticket Prefix, Year and Serial: ('TF', 2024, 456)
Total Fines: 2000
Percent Over Limit: 20
```

## 8. Running the Tests

Execute the following command:

```bash
pytest -v
```

The test suite uses Pytest and Hypothesis to check application behaviour across generated and manually specified inputs.

## 9. Test Results

The final test execution completed successfully:

- Total tests: 13
- Passed: 13
- Failed: 0
- Execution time: 1.14 seconds

The initial testing phase identified input-validation issues involving negative fine amounts, zero speed limits, and negative speed limits.

These issues were addressed by adding validation checks to the application.

## 10. Screenshots and Documentation

The following evidence is included in `Screenshots.pdf`:

- Successful execution of the Traffic Fine Application.
- Initial fuzz testing results showing failures.
- Final fuzz testing results showing all 13 tests passing.
- Application implementation and execution evidence.

Detailed methodology, test cases, identified issues, corrective actions, and final results are documented in:

`Fuzz_Testing_Baseline_Results.md`

## 11. Conclusion

Fuzz testing was performed on the Traffic Fine Application using Hypothesis and Pytest.

The testing process examined valid inputs, arbitrary generated strings, None values, malformed ticket IDs, and boundary conditions involving fine amounts and speed limits.

The initial tests helped identify input-validation issues. These issues were addressed by adding appropriate validation and exception handling to the application.

After the changes, all 13 tests passed successfully.

The lab demonstrates how property-based testing can explore a wider range of inputs than manually written test cases alone and improve application robustness.
