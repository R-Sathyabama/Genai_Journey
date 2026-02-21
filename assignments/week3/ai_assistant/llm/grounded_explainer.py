from openai import OpenAI

client = OpenAI()

def generate_report(changes, question_type):
    if not changes:
        return "No relevant changes found in release notes."

    structured_text = "\n".join(
        f"[{c['version']}] ({c['category']}) {c['description']}"
        for c in changes
    )

    prompt = f"""
You are a DevOps Upgrade Intelligence Assistant.

Use ONLY the structured changes below.
Do NOT invent or generalize.
If something is not in structured data, ignore it.

Structured Changes:
{structured_text}

Question Type: {question_type}

Generate a precise upgrade report.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content
