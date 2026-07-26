#Om Namo Venketesaya
import threading
import pyautogui
import keyboard

saved_text = ""
saved_delay = 0.01
saved_start_key = "Q"
saved_stop_key = "esc"
start_hotkey_id = None
stop_hotkey_id = None

typing = False
typing_thread = None

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
        start_typing
    )

    stop_hotkey_id = keyboard.add_hotkey(
        saved_stop_key,
        stop_typing
    )
    print("Hotekyes Saved")


def clear_auto_indent():
    pyautogui.press('esc')
    pyautogui.press('enter')
    pyautogui.hotkey("shift","home")
    pyautogui.press("backspace")


def type_line(line,delay):
    leadingSpaces = len(line) - len(line.lstrip())
    text = line.lstrip() #lstrip removes only left side

    if leadingSpaces > 0:
        pyautogui.press(
            "space",
            presses=leadingSpaces,
            interval=delay
        )
    i = 0
    while i < len(text):

        if not typing:
            return

        char = text[i]

        if char in [")", "]", "}", '"']:

            pyautogui.press("right")
            pyautogui.press("backspace")

        else:

            pyautogui.write(
                char,
                interval=delay
            )

        i += 1
        
def type_text(text,delay = 0.01):
    lines = text.splitlines()
    global typing
    firstLine = True
    for line in lines:
        if not typing:
            print("Typing stopped")
            typing = False
            return
        
        if not firstLine:
            clear_auto_indent()

        type_line(line, delay)

        firstLine = False

    print("Finished Typing!")
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
    global typing
    typing = False
    print("Stopped Auto Typing")