def calculate_risk(changes):
    score = 0

    for change in changes:
        if change["category"] == "removed":
            score += 5
        elif change["category"] == "api":
            score += 4
        elif change["category"] == "behavior":
            score += 3
        elif change["category"] == "deprecated":
            score += 2
        elif change["category"] == "security":
            score += 3

    if score >= 15:
        return "CRITICAL"
    elif score >= 8:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"
