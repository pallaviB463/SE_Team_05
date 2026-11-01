import os
import pickle
import random
from datetime import date

events = {}


def createEvent(eventName, venue, capacity=50, guests=[]):
    events[eventName] = {"venue": venue, "capacity": capacity,
                         "guests": guests}
    return events[eventName]


def registerGuest(eventName, guest):
    event = events.get(eventName)
    if event is None:
        print("No such event:", eventName)
        return False
    if len(event["guests"]) >= event["capacity"]:
        print(eventName, "is full, cannot add", guest)
        return False
    event["guests"].append(guest)
    return True


def seatsLeft(eventName):
    event = events[eventName]
    return event["capacity"] - len(event["guests"])


def eventStatus(eventDate):
    if eventDate >= date.today():
        return "Upcoming"
    else:
        return "Completed"


def guestReport(eventName, sortOrder):
    names = sorted(events[eventName]["guests"])
    return ", ".join(names)


def saveEvents(fileName="events.pkl"):
    with open(fileName, "wb") as f:
        pickle.dump(events, f)


def loadEvents(fileName="events.pkl"):
    with open(fileName, "rb") as f:
        return pickle.load(f)


def printBadges(eventName):
    # Helper kept for the lab: not called by the demo
    os.system("lp badges_" + eventName + ".txt")


def main():
    createEvent("Tech Meetup", "Hall A", 3)
    createEvent("Alumni Dinner", "Rooftop",2)
    registerGuest("Tech Meetup", "Asha")
    registerGuest("Tech Meetup", "Ravi")
    registerGuest("Alumni Dinner", "Meena")
    registerGuest("Workshop", "Kiran")
    left=seatsLeft("Tech Meetup")
    print("Seats left at Tech Meetup:", left)
    print("Seats left at Alumni Dinner:", seatsLeft("Alumni Dinner"))
    print("Tech Meetup guests:", guestReport("Tech Meetup", "name"))
    print("Tech Meetup is", eventStatus(date(2099, 1, 15)))
    print("Alumni Dinner is", eventStatus(date(2020, 5, 1)))
    winner = random.choice(events["Tech Meetup"]["guests"])
    print("Lucky draw winner:", winner)
    saveEvents()
    restored = loadEvents() # reload to confirm the save worked
    print("Events restored from file:", len(restored))
    print("Venues:", [e["venue"] for e in restored.values()])

main()
