def detect_question_type(user_query: str):
    q = user_query.lower()

    if "break" in q:
        return "breaking"
    if "deprecated" in q:
        return "deprecated"
    if "security" in q:
        return "security"
    if "checklist" in q:
        return "checklist"
    return "full"
