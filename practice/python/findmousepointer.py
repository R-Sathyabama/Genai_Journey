import pyautogui 
import time
x,y = pyautogui.position()
time.sleep(5)
print(f'x:{x},y:{y}')