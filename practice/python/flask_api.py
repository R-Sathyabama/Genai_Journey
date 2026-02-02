from flask import Flask, jsonify
import pyautogui
import time
import threading



#basic of Flask 

'''
app = Flask(__name__)
@app.route('/')
def flash():
    return "hello sathya you are doing good keep up the progress"
if __name__ == '__main__':
    app.run(debug=True)

'''

#already used puautogui code testing with flash api

app = Flask(__name__)

def run_automation():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5

    time.sleep(10)  # time to switch to browser

    # Open new tab (macOS)
    pyautogui.hotkey('command', 't')
    time.sleep(1)

    # Focus address bar
    pyautogui.hotkey('command', 'l')
    time.sleep(0.5)

    # Google News search
    query = "hindu newspaper today"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"

    pyautogui.typewrite(url, interval=0.03)
    pyautogui.press('enter')
    time.sleep(5)

    # Open first news result
    pyautogui.press('tab', presses=19, interval=0.3)
    pyautogui.press('enter')


@app.route("/run", methods=["GET"])
def trigger_automation():
    thread = threading.Thread(target=run_automation)
    thread.start()

    return jsonify({
        "status": "started",
        "message": "PyAutoGUI automation running"
    })


if __name__ == "__main__":
    app.run(debug=True)
