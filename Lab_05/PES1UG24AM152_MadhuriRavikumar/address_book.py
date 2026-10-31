
"""A simple address book with contact management and backup features."""

import csv
import hashlib
import json
import re

contacts = {}


def add_contact(full_name, phone, email="", city="Unknown"):
    """Add a contact after validating the phone number."""
    if not re.fullmatch(r"[0-9]{10}", phone):
        print("Invalid phone number for", full_name)
        return False

    contacts[full_name] = {
        "phone": phone,
        "email": email,
        "city": city
    }
    return True


def contact_id(full_name):
    """Generate a unique identifier for a contact."""
    return hashlib.sha256(full_name.encode("utf-8")).hexdigest()[:6]


def search_contacts(text):
    """Search contacts by name or phone number."""
    found = []

    for name, info in contacts.items():
        if text.lower() in name.lower() or text in info["phone"]:
            found.append(name)

    return found


def update_city(full_name, city):
    """Update the city of an existing contact."""
    try:
        contacts[full_name]["city"] = city
        return True
    except KeyError:
        print("No contact named", full_name)
        return False


def contacts_by_city():
    """Group contacts according to their city."""
    grouped = {}

    for name, info in contacts.items():
        grouped.setdefault(info["city"], []).append(name)

    return grouped


def print_directory():
    """Print all contacts in alphabetical order."""
    names = sorted(contacts)

    for index, name in enumerate(names, start=1):
        print(index, name, contacts[name]["phone"])


def export_csv(file_name="contacts.csv"):
    """Export all contacts to a CSV file."""
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for name, info in contacts.items():
            writer.writerow([
                name,
                info["phone"],
                info["email"],
                info["city"]
            ])


def backup_book(file_name="contacts.bak"):
    """Save the address book to a JSON backup file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)


def restore_book(file_name="contacts.bak"):
    """Restore contacts from a JSON backup file."""
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    """Demonstrate the address book functionality."""
    add_contact(
        "Neha Sharma", "9876543210",
        "neha@example.com", "Bengaluru"
    )
    add_contact(
        "Rahul Verma", "9123456780",
        "rahul@example.com", "Mysuru"
    )
    add_contact("Test User", "12345")
    add_contact("Kavya Nair", "9988776655", city="Bengaluru")

    update_city("Rahul Verma", "Chennai")
    update_city("Nobody", "Delhi")

    print_directory()
    print("Search 'ra':", search_contacts("ra"))
    print("By city:", contacts_by_city())
    print("Id for Neha:", contact_id("Neha Sharma"))

    export_csv()
    backup_book()

    restored = restore_book()

    print(
        "Contacts restored:",
        len(restored),
        "| first:",
        sorted(restored)[0]
    )
    print(
        "Restored contacts match the in-memory address book:",
        restored == contacts
    )


if __name__ == "__main__":
    main()
