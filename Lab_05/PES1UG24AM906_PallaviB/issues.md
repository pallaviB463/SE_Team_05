# Lab 5 – Static Code Analysis
## Support Ticket Tracker

### Issues Identified and Fixes Applied

| Issue | Type | Original Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Mutable default argument | Bug | 10 | The default `audit_log=[]` list was shared between function calls. | Removed the mutable default and introduced a separate audit log. |
| Bare exception handling | Code Quality / Security | 24 | Bare `except` catches unexpected exceptions and hides errors. | Replaced it with `except KeyError`. |
| Unsafe eval() | Security | 92 | `eval()` can execute arbitrary Python expressions. | Removed the unsafe demonstration block. |
| Unused imports | Code Quality | 4, 5 | `sys` and `random` were imported but never used. | Removed unused imports. |
| Incorrect None comparison | Code Quality | 37 | Used `status != None`. | Changed to `status is not None`. |
| Improper file handling | Code Quality | 46, 53 | Files were opened and closed manually. | Used `with open()` context managers. |
| Missing file encoding | Code Quality | 46, 53 | File operations did not specify an encoding. | Added `encoding="utf-8"`. |
| Invalid function naming | Code Quality | 66 | `closeTicket()` did not follow snake_case naming convention. | Renamed it to `close_ticket()`. |
| Unused variable | Code Quality | 84 | The variable `count` was assigned but never used. | Removed the unused variable. |
| Long lines and trailing whitespace | Formatting | 10, 14, 63, 71, 79, 80, 84 | Several lines violated Flake8 formatting rules. | Split long lines and removed trailing whitespace. |
| Missing docstrings | Code Quality | Multiple | Functions and the module did not have documentation strings. | Added module and function docstrings. |
| Missing final newline | Formatting | End of file | The Python file did not end with a newline character. | Added a final newline. |

### Verification Results

The corrected program was analyzed again using Pylint, Bandit and Flake8.

- Pylint: 9.84/10
- Bandit: No issues identified.
- Flake8: No errors after fixing the final newline.

The original program was improved without changing its main purpose of managing support tickets.