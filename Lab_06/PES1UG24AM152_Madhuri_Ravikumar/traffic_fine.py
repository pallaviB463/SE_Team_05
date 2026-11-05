def speeding_fine(speed, limit, zone):
    if speed <= limit:
        return 0
    excess = speed - limit
    if zone == "school":
        base = 2000
    elif zone == "highway":
        base = 1000
    else:
        base = 500
    if excess > 40:
        return base * 3
    elif excess > 20:
        return base * 2
    return base


def license_action(points, is_commercial, repeat_offender):
    if points >= 12:
        if is_commercial:
            return "revoke"
        return "suspend"
    if points >= 8:
        if repeat_offender:
            return "suspend"
        return "warning"
    if points >= 4:
        return "notice"
    return "none"


def total_penalty(fines):
    total = 0
    for fine in fines:
        if fine < 0:
            raise ValueError("negative fine")
        total += fine
    if total > 10000:
        total = 10000
    return total
