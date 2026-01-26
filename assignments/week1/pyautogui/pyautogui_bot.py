import pyautogui
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

time.sleep(5)

# 1️⃣ Open new tab (macOS)
pyautogui.hotkey('command', 't')
time.sleep(1)

# 2️⃣ Focus address bar (macOS FIX)
pyautogui.hotkey('command', 'l')
time.sleep(0.5)

# 3️⃣ Open Google NEWS results directly
query = "hindu newspaper today"
url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"

pyautogui.typewrite(url, interval=0.03)
pyautogui.press('enter')
time.sleep(5)

# 4️⃣ Click first news result (keyboard-safe)
pyautogui.press('tab', presses=19, interval=0.3)
pyautogui.press('enter')
