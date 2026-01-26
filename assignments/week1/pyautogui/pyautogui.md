# AI Using PyAutoGUI

## Objective
To automate browser interaction using keyboard-based automation with PyAutoGUI.

## What We Tried
- Open a new browser tab
- Focus the address bar
- Search Google News for a keyword
- Open the first news result using keyboard navigation

## How It Works
PyAutoGUI simulates human keyboard interactions. This script uses
hotkeys, typing automation, and timed delays to control the browser
without DOM-level access.

## How to Run

### Prerequisites
- Python 3.11+
- Active browser window (Chrome/Safari)
- Screen focus on browser

### Steps
```bash
pip install pyautogui
python pyautogui_bot.py
```

⚠️ Ensure the browser window is active before execution.

###  Output
- Google News search opens
- First news article is clicked
- Demo recorded in [pyautogui.mp4](https://github.com/R-Sathyabama/Genai_Journey/blob/main/assignments/week1/pyautogui/pyautogui.mp4)