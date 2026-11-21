import math
import re
from datetime import date

# Bugs found by fuzzing (Hypothesis) and how they are handled:
#   * None / non-string input crashed every function (AttributeError).
#   * Missing, empty or extra '-' / ',' parts crashed the unpacking (ValueError).
#   * Non-ASCII digits such as '²' pass str.isdigit() but crash int().
#   * Very long numbers (> 4300 digits) crash int() (Python's DoS protection).
#   * 'nan', 'inf', '1e400' and negative prices were accepted as prices.
#   * expiry_days accepted impossible dates (2024-02-30, 2024-13-01) and treated
#     every month as 30 days, so 31 Jan and 1 Feb gave the same day count.
# Invalid input now returns None instead of crashing.

CODE_PATTERN = re.compile(r"([A-Z0-9]+)-([0-9]{1,9})")
DATE_PATTERN = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
EPOCH = date(2024, 1, 1)


def split_code(code):
    """Split a coupon code like 'save-20' into ('SAVE', 20); None if invalid."""
    if not isinstance(code, str):
        return None
    match = CODE_PATTERN.fullmatch(code.strip().upper())
    if match is None:
        return None
    prefix, value = match.groups()
    return prefix, int(value)


def most_expensive(prices_csv):
    """Highest price in a CSV like '199,49.5,320'; empty items are skipped; None if invalid."""
    if not isinstance(prices_csv, str):
        return None
    prices = []
    for part in prices_csv.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            price = float(part)
        except ValueError:
            return None
        if not math.isfinite(price) or price < 0:
            return None
        prices.append(price)
    if not prices:
        return None
    return max(prices)


def expiry_days(date_text):
    """Day number of a YYYY-MM-DD date counted from 2024-01-01 (= day 1); None if invalid."""
    if not isinstance(date_text, str):
        return None
    match = DATE_PATTERN.fullmatch(date_text.strip())
    if match is None:
        return None
    try:
        expiry = date(*(int(p) for p in match.groups()))
    except ValueError:
        return None
    return (expiry - EPOCH).days + 1


def ask(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""


def show(label, result, hint):
    print(label, result if result is not None else f"Invalid input - {hint}")


def main():
    print("==== Running split_code ====")
    user_input = ask("Enter a coupon code (e.g. save-20): ")
    show("Prefix and Value:", split_code(user_input), "use PREFIX-NUMBER, e.g. save-20")

    print("\n==== Running most_expensive ====")
    user_input = ask("Enter item prices as CSV (e.g. 199,49.5,320): ")
    show("Most Expensive Item:", most_expensive(user_input), "use non-negative numbers separated by commas")

    print("\n==== Running expiry_days ====")
    user_input = ask("Enter an expiry date as YYYY-MM-DD: ")
    show("Days Since 2024:", expiry_days(user_input), "use a real date as YYYY-MM-DD")


if __name__ == "__main__":
    main()
