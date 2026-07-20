#Om Namo Venketesaya
import time
import pyautogui

def clear_auto_indent():
    pyautogui.press('esc')
    pyautogui.press('enter')
    pyautogui.hotkey("shift"+"home")
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

    if text:
        pyautogui.write(
            text,
            interval=delay
        )

def type_text(text,delay = 0.01):
    line = text.split("\n")

    firstLine = True