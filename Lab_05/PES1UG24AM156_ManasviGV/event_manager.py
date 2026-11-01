"""Event management system: create events, register guests and save them."""

import json
import re
import secrets
import shutil
# subprocess is only used with a fixed argument list and no shell
import subprocess  # nosec B404
from datetime import date

events = {}


def create_event(event_name, venue, capacity=50, guests=None):
    """Create an event and store it in the events dictionary."""
    if guests is None:
        guests = []
    events[event_name] = {"venue": venue, "capacity": capacity,
                          "guests": guests}
    return events[event_name]


def register_guest(event_name, guest):
    """Add a guest to an event if it exists and is not full."""
    event = events.get(event_name)
    if event is None:
        print("No such event:", event_name)
        return False
    if len(event["guests"]) >= event["capacity"]:
        print(event_name, "is full, cannot add", guest)
        return False
    event["guests"].append(guest)
    return True


def seats_left(event_name):
    """Return the number of free seats for an event."""
    event = events[event_name]
    return event["capacity"] - len(event["guests"])


def event_status(event_date):
    """Return "Upcoming" or "Completed" depending on the event date."""
    if event_date >= date.today():
        return "Upcoming"
    return "Completed"


def guest_report(event_name, sort_order="name"):
    """Return the guest names of an event as a comma-separated string.

    sort_order can be "name" (A to Z) or "reverse" (Z to A).
    """
    if sort_order not in ("name", "reverse"):
        raise ValueError("sort_order must be 'name' or 'reverse'")
    names = sorted(events[event_name]["guests"],
                   reverse=sort_order == "reverse")
    return ", ".join(names)


def save_events(file_name="events.json"):
    """Save all events to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)


def load_events(file_name="events.json"):
    """Load events from a JSON file and return them."""
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def print_badges(event_name):
    """Send the badge file of an event to the printer."""
    # Helper kept for the lab: not called by the demo
    if not re.fullmatch(r"[\w \-]+", event_name):
        raise ValueError("Invalid event name: " + event_name)
    lp_path = shutil.which("lp")
    if lp_path is None:
        raise FileNotFoundError("The lp command is not available")
    file_name = "badges_" + event_name.replace(" ", "_") + ".txt"
    # No shell is used and the event name is validated above
    subprocess.run([lp_path, file_name], check=True)  # nosec B603


def main():
    """Run a short demonstration of the event manager."""
    create_event("Tech Meetup", "Hall A", 3)
    create_event("Alumni Dinner", "Rooftop",2)
    register_guest("Tech Meetup", "Asha")
    register_guest("Tech Meetup", "Ravi")
    register_guest("Alumni Dinner", "Meena")
    register_guest("Workshop", "Kiran")
    left=seats_left("Tech Meetup")
    print("Seats left at Tech Meetup:", left)
    print("Seats left at Alumni Dinner:", seats_left("Alumni Dinner"))
    print("Tech Meetup guests:", guest_report("Tech Meetup", "name"))
    print("Tech Meetup is", event_status(date(2099, 1, 15)))
    print("Alumni Dinner is", event_status(date(2020, 5, 1)))
    winner = secrets.choice(events["Tech Meetup"]["guests"])
    print("Lucky draw winner:", winner)
    save_events()
    restored = load_events() # reload to confirm the save worked
    print("Events restored from file:", len(restored))
    print("Venues:", [e["venue"] for e in restored.values()])

if __name__ == "__main__":
    main()
