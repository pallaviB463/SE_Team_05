
# Lab 7 – Fuzz Testing: Traffic Fine Application

## Overview

This lab focuses on fuzz testing a Python application that handles traffic fine information. The objective is to test how the application behaves when it receives different types of inputs, including valid, invalid, unexpected, and boundary-value inputs.

The application contains three main functions:

1. `parse_ticket_id()` – Parses a traffic ticket ID into its prefix, year, and serial number.
2. `total_fines()` – Calculates the total fine amount from comma-separated values, with a maximum limit of 10,000.
3. `speed_excess()` – Calculates the percentage by which a vehicle's speed exceeds the speed limit.

## Objectives

- Understand the concept of fuzz testing.
- Generate different input values automatically.
- Test application behaviour with unexpected and malformed inputs.
- Identify input-validation issues and runtime errors.
- Improve the robustness of the application.
- Verify the implementation using automated tests.

## Technologies Used

- Python 3.11
- Pytest – Testing framework.
- Hypothesis – Property-based testing library.

## Project Structure

```text
lab7/
│
├── traffic_fine.py
├── test_traffic_fine.py
├── README.md
├── FUZZ_TESTING.md
│
├── ApplicationOutput.png
├── Pytest_Results.png
└── FuzzTesting.png
```

## Implementation

### 1. Ticket ID Parsing

The `parse_ticket_id()` function accepts a ticket ID in the format:

`TF-2024-0456`

It separates the prefix, year, and serial number, converts the numeric fields into integers, and converts the prefix to uppercase.

Input validation is included to reject malformed ticket IDs and non-integer year or serial values.

### 2. Total Fine Calculation

The `total_fines()` function accepts comma-separated fine amounts.

Example:

`500,1200,300`

The function converts the values into integers and calculates their sum. If the total exceeds 10,000, the result is capped at 10,000.

Negative values and invalid fine amounts are rejected.

### 3. Speed Excess Calculation

The `speed_excess()` function accepts a speed reading in the format:

`72/60`

It calculates the percentage by which the recorded speed exceeds the speed limit.

The formula used is:

```python
(speed - limit) * 100 // limit
```

Invalid readings and zero or negative speed limits are rejected.

## Installation

Install the required dependencies:

```bash
pip install pytest hypothesis
```

## Running the Application

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

## Running the Tests

Execute the following command:

```bash
pytest -v
```

The test suite uses Pytest and Hypothesis to check the application's behaviour across generated and manually specified inputs.

## Test Results

The final test execution completed successfully:

- Total tests: 13
- Passed: 13
- Failed: 0
- Execution time: 1.14 seconds

## Screenshots

The following screenshots document the application execution and testing process:

| Screenshot | Description |
|---|---|
| `ApplicationOutput.png` | Successful execution of the traffic fine application |
| `Pytest_Results.png` | Summary of the successful test execution |
| `FuzzTesting.png` | Workflow of the fuzz testing process |

## Conclusion

Fuzz testing was performed on the traffic fine application using Hypothesis and Pytest. Different input values were tested to examine the behaviour of the three functions.

During testing, input-validation issues involving negative fine amounts, zero and negative speed limits, and malformed ticket IDs were identified and addressed.

After implementing the validation checks, all 13 tests passed successfully. This demonstrates that the tested functions handle the selected valid, invalid, and boundary-value inputs as expected.
