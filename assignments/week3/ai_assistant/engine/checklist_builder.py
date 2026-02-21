def build_checklist(changes):
    checklist = []

    for change in changes:
        if change["category"] == "removed":
            checklist.append(f"Replace or remove usage of: {change['description']}")
        elif change["category"] == "deprecated":
            checklist.append(f"Migrate deprecated item: {change['description']}")

    return checklist
