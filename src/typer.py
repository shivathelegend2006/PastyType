#Om Namo Venketesaya
import time
import pyautogui

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