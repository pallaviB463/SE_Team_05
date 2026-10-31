
"""Restaurant dining order billing and kitchen ticket module."""

import hashlib
import secrets

ORDERS = {
    "T1": {
        "guest": "Liam",
        "items": 3,
        "bill": 45.0,
        "is_settled": False,
    },
    "T2": {
        "guest": "Sophia",
        "items": 1,
        "bill": 18.0,
        "is_settled": True,
    },
    "T3": {
        "guest": "Mason",
        "items": 4,
        "bill": 72.0,
        "is_settled": False,
    },
}


def place_table_order(table_id, guest, items_count, order_log=None):
    """Create a new restaurant table order."""
    if order_log is None:
        order_log = []

    if table_id in ORDERS or items_count <= 0:
        return False

    ORDERS[table_id] = {
        "guest": guest,
        "items": items_count,
        "bill": 15.0 * items_count,
        "is_settled": False,
    }

    order_log.append(
        f"Created order for {table_id} with {items_count} dishes"
    )
    return True


def void_table_order(table_id):
    """Remove an existing table order."""
    if table_id in ORDERS:
        del ORDERS[table_id]


def check_table_status(table_id):
    """Check whether a table has an unsettled order."""
    if table_id not in ORDERS:
        return False

    return not ORDERS[table_id]["is_settled"]


def calculate_discounted_bill(table_id, promo_expr):
    """Calculate a discounted bill using an approved promotion."""
    base_bill = ORDERS[table_id]["bill"]

    if promo_expr == "base_bill * 0.90":
        return base_bill * 0.90

    raise ValueError("Unsupported discount expression")


def generate_ticket_hash(table_id):
    """Generate a SHA-256 hash for a kitchen ticket."""
    return hashlib.sha256(table_id.encode("utf-8")).hexdigest()


def generate_pos_pin():
    """Generate a cryptographically secure four-digit POS PIN."""
    return secrets.randbelow(9000) + 1000


def export_kitchen_orders(filename="kitchen_orders.txt"):
    """Export restaurant orders to a kitchen ticket file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(ORDERS))

    print(f"Ticket sent to kitchen printer: {filename}")


def get_pending_summary(table_orders):
    """Count the number of unsettled restaurant orders."""
    return sum(
        1
        for details in table_orders.values()
        if not details["is_settled"]
    )


def main():
    """Execute sample restaurant billing operations."""
    pos_terminal_key = "POS_TERMINAL_SECRET_TOKEN_2026"

    place_table_order("T4", "Olivia", 2)
    void_table_order("T2")

    print("Is T1 pending:", check_table_status("T1"))

    discounted_bill = calculate_discounted_bill(
        "T1", "base_bill * 0.90"
    )
    print("Discounted Bill:", discounted_bill)

    print("Ticket Hash:", generate_ticket_hash("T1"))
    print("POS PIN:", generate_pos_pin())

    export_kitchen_orders()

    print("Pending tables:", get_pending_summary(ORDERS))
    print("POS Secret active:", bool(pos_terminal_key))


if __name__ == "__main__":
    main()
