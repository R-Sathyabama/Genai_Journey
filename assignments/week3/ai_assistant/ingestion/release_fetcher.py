import requests

def fetch_release_notes(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch release notes")
    return response.text
