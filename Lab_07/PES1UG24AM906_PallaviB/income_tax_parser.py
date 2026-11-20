def clean_pan(pan):
    """
    Removes spaces from a PAN and upper-cases it.
    Safely handles None, non-string, or malformed inputs without crashing.
    """
    if pan is None:
        return ""
    if not isinstance(pan, str):
        pan = str(pan)
    return pan.strip().replace(' ', '').upper()


def parse_amount(text):
    """
    Converts an amount such as 'Rs 12,50,000' into an int.
    Safely handles None, non-string, non-numeric, or malformed inputs without crashing.
    """
    if text is None:
        return 0
    if not isinstance(text, str):
        text = str(text)
    cleaned = text.replace('Rs.', '').replace('Rs', '').replace('rs', '').replace('RS', '').replace(',', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        import re
        digits = re.sub(r'[^\d]', '', cleaned)
        if digits:
            try:
                return int(digits)
            except ValueError:
                return 0
        return 0


def parse_tax_slab(line):
    """
    Parses 'LOW-HIGH:RATE' into a (low, high, rate) tuple.
    Safely handles None, malformed, or invalid inputs without crashing.
    """
    if line is None or not isinstance(line, str):
        return (0, 0, 0)
    try:
        if ':' not in line:
            return (0, 0, 0)
        parts = line.split(':')
        if len(parts) != 2:
            return (0, 0, 0)
        limits, rate_str = parts[0].strip(), parts[1].strip()
        if '-' not in limits:
            return (0, 0, 0)
        limit_parts = limits.split('-')
        if len(limit_parts) != 2:
            return (0, 0, 0)
        low = int(limit_parts[0].strip())
        high = int(limit_parts[1].strip())
        rate = int(rate_str)
        return (low, high, rate)
    except (ValueError, TypeError, AttributeError):
        return (0, 0, 0)


def main():
    print("==== Running clean_pan ====")
    try:
        value = input("Enter a PAN (e.g. abcde 1234f): ")
    except (EOFError, KeyboardInterrupt):
        value = ""
    print("Cleaned PAN:", clean_pan(value))

    print("\n==== Running parse_amount ====")
    try:
        value = input("Enter an amount (e.g. Rs 12,50,000): ")
    except (EOFError, KeyboardInterrupt):
        value = ""
    print("Amount in rupees:", parse_amount(value))

    print("\n==== Running parse_tax_slab ====")
    try:
        value = input("Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): ")
    except (EOFError, KeyboardInterrupt):
        value = ""
    print("Tax slab (low, high, rate):", parse_tax_slab(value))


if __name__ == "__main__":
    main()
