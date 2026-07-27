#Om Namo Venketesaya
import threading
import time
import pyautogui
import keyboard

pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0

saved_text = ""
saved_delay = 0.01
saved_start_key = "Q"
saved_stop_key = "esc"
start_hotkey_id = None
stop_hotkey_id = None

typing = False
typing_thread = None

# NEW: Prevents programmatic ESC presses from accidentally triggering the Stop hotkey!
suppress_stop = False

def save_configuration(text, delay, start_key, stop_key):

    global saved_text
    global saved_delay
    global saved_start_key
    global saved_stop_key

    saved_text = text
    saved_delay = delay
    saved_start_key = start_key.lower()
    saved_stop_key = stop_key.lower()

    print("Configuration Saved")
    register_hotkeys()


def register_hotkeys():

    global start_hotkey_id
    global stop_hotkey_id

    if start_hotkey_id is not None:
        keyboard.remove_hotkey(start_hotkey_id)

    if stop_hotkey_id is not None:
        keyboard.remove_hotkey(stop_hotkey_id)

    start_hotkey_id = keyboard.add_hotkey(
        saved_start_key,
        start_typing,
        suppress= True
    )

    stop_hotkey_id = keyboard.add_hotkey(
        saved_stop_key,
        stop_typing,
        suppress= True
    )
    print("Hotekyes Saved")


def clear_auto_indent():
    global suppress_stop

    pyautogui.press('esc')
    time.sleep(0.05)

    
    # Hit Enter to go to the next line

    time.sleep(0.45)

    pyautogui.hotkey("shift", "home")
    pyautogui.hotkey('ctrl', 'backspace')

def type_line(line, delay):
    global typing
    if not typing:
        return

    leadingSpaces = len(line) - len(line.lstrip())
    text = line.lstrip() # lstrip removes only left side

    # Type OUR exact spaces (this directly overwrites whatever auto-indent was highlighted by shift+home!)
    if leadingSpaces > 0:
        pyautogui.press('space', presses=leadingSpaces, interval=0.005)

    # Restored your exact bracket and string handling loop!
    i = 0
    while i < len(text):

        if not typing:
            return

        char = text[i]
        
        if char in ["(", "[", "{"]:
            pyautogui.write(
                char,
                interval=delay
            )
            time.sleep(0)
            pyautogui.press("right")
            pyautogui.press("backspace")
        else:
            pyautogui.press(
                char,
                interval=delay
            )
            time.sleep(0)

        i += 1


def type_text(text, delay = 0.01):
    global typing
    
    # WRAP IN TRY-FINALLY: Guarantees typing = False always resets so you can press Start again!
    try:
        lines = text.splitlines()
        firstLine = True
        for line in lines:
            if not typing:
                print("Typing stopped")
                return
            
            if not firstLine:
                clear_auto_indent()

            type_line(line, delay)

            firstLine = False

        print("Finished Typing!")
    finally:
        typing = False


def start_typing():
    global typing
    global typing_thread

    if typing:
        return
    
    typing = True

    typing_thread = threading.Thread(
        target=type_text,
        args=(saved_text, saved_delay),
        daemon=True
    )

    typing_thread.start()


def stop_typing():
    global typing, suppress_stop
    

        
    typing = False
    print("Stopped Auto Typing")