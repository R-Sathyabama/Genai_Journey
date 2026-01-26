# AI Using Playwright

## Objective
To understand browser automation using Playwright with Python by
automating real-world website interactions and collecting page metadata.

## What We Tried
- Open Netflix website
- Navigate to the Sign In page
- Fill phone/email field
- Trigger page navigation
- Collect browser and page metadata
- Store metadata into a text file

## How It Works
This script uses Playwright’s async API to control a Chromium browser.
Each step is executed sequentially with delays for visibility.
After navigation, browser and page-level metadata are extracted using
JavaScript execution and saved locally.

## How to Run

### Prerequisites
- Python 3.11+
- Playwright installed

### Steps
```bash
pip install playwright
playwright install
python playwright_bot.py
```

### Output

- Browser opens and navigates automatically
- Metadata saved as netflix_metadata.txt
- Demo execution recorded in <video controls src="https://github.com/R-Sathyabama/Genai_Journey/blob/main/assignments/week1/playwright/playwright.mp4" title="playwright.mp4"></video>