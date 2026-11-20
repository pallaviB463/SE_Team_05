
def parse_ticket_id(ticket_id):
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be a string")

    parts = ticket_id.split('-')

    if len(parts) != 3 or any(part == "" for part in parts):
        raise ValueError("Invalid ticket ID format")

    prefix, year, serial = parts

    try:
        year = int(year)
        serial = int(serial)
    except ValueError:
        raise ValueError("Year and serial must be integers")

    return prefix.upper(), year, serial


def total_fines(amounts_csv):
    if not isinstance(amounts_csv, str):
        raise ValueError("Fine amounts must be a string")

    try:
        amounts = [int(a.strip()) for a in amounts_csv.split(',')]
    except ValueError:
        raise ValueError("Fine amounts must be integers")

    if any(amount < 0 for amount in amounts):
        raise ValueError("Fine amounts cannot be negative")

    total = sum(amounts)

    if total > 10000:
        total = 10000

    return total


def speed_excess(reading):
    if not isinstance(reading, str):
        raise ValueError("Speed reading must be a string")

    parts = reading.split('/')

    if len(parts) != 2:
        raise ValueError("Reading must have the format speed/limit")

    try:
        speed = int(parts[0].strip())
        limit = int(parts[1].strip())
    except ValueError:
        raise ValueError("Speed and limit must be integers")

    if limit <= 0:
        raise ValueError("Speed limit must be greater than zero")

    return (speed - limit) * 100 // limit


def main():
    print("==== Running parse_ticket_id ====")
    user_input = input("Enter a ticket ID (e.g. TF-2024-0456): ")
    result = parse_ticket_id(user_input)
    print("Ticket Prefix, Year and Serial:", result)

    print("\n==== Running total_fines ====")
    user_input = input("Enter fine amounts as CSV (e.g. 500,1200,300): ")
    result = total_fines(user_input)
    print("Total Fines:", result)

    print("\n==== Running speed_excess ====")
    user_input = input("Enter speed/limit (e.g. 72/60): ")
    result = speed_excess(user_input)
    print("Percent Over Limit:", result)


if __name__ == "__main__":
    main()
