#Om Namo Venketesaya
import time
import pyautogui
import keyboard

saved_text = ""
saved_delay = 0.01
saved_start_key = "Q"
saved_stop_key = "esc"

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
    keyboard.clear_all_hotkeys()
    keyboard.add_hotkey(saved_start_key,start_typing)
    keyboard.add_hotkey(saved_stop_key,stop_typing)

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
        char = text[i]
        if char in [")", "]", "}",'"']:
            pyautogui.press('right')
            pyautogui.press('backspace')


        else:
            pyautogui.write(
                text,
                interval=delay
            )
        i += 1

def type_text(text,delay = 0.01):
    lines = text.splitlines()

    firstLine = True
    for line in lines:

        if not firstLine:
            clear_auto_indent()

        type_line(line, delay)

        firstLine = False

    print("Finished Typing!")

def start_typing():
    type_text(saved_text,saved_delay)

def stop_typing():
    print("Stopped Auto Typing")