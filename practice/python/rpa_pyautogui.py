import pyautogui
import time

#Mouse operation

pyautogui.click(100,100)
time.sleep(3)
pyautogui.rightClick(100,130)
time.sleep(4)
pyautogui.doubleClick(997,898)
time.sleep(2)
pyautogui.scroll(987)
time.sleep(2)
pyautogui.drag(100, 200, duration=1, button='left')
time.sleep(2)



#Keyboard operation
"""
time.sleep(3)
pyautogui.click(940,857)
pyautogui.write("sathiya")
pyautogui.press('enter')
time.sleep(3)
pyautogui.hotkey('shift', 'command', '4')

time.sleep(1)

# Drag to select area
pyautogui.moveTo(300, 300)
pyautogui.dragTo(800, 700, duration=1, button='left')
"""

#image operation
"""
time.sleep(3)
location = pyautogui.locateOnScreen('ss.png', confidence = 0.8)
print(location)
time.sleep(3)
#pyautogui.click(pyautogui.center(location))
print(pyautogui.size())
tt = pyautogui.screenshot()
tt.save("demo.png")
"""