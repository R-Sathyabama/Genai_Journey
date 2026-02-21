def parse_release_notes(md_text: str, tool: str, version: str):
    categories = {
        "deprecated": [],
        "removed": [],
        "api": [],
        "behavior": [],
        "security": []
    }

    current_section = None

    for line in md_text.splitlines():
        lower = line.lower()

        if "deprecated" in lower:
            current_section = "deprecated"
            continue
        elif "removed" in lower:
            current_section = "removed"
            continue
        elif "api change" in lower or "api changes" in lower:
            current_section = "api"
            continue
        elif "behavior change" in lower:
            current_section = "behavior"
            continue
        elif "security" in lower:
            current_section = "security"
            continue

        if current_section and line.strip().startswith(("-", "*")):
            categories[current_section].append(line.strip())

    structured = []

    for cat, items in categories.items():
        for item in items:
            structured.append({
                "tool": tool,
                "version": version,
                "category": cat,
                "description": item
            })

    return structured
