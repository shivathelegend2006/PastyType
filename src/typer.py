# Om Namo Venketesaya
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
saved_ide_mode = True  # Tracks the IDE Auto-Indent & Smart Bracket toggle state!
start_hotkey_id = None
stop_hotkey_id = None

typing = False
typing_thread = None

# Prevents programmatic ESC presses from accidentally triggering the Stop hotkey!
suppress_stop = False

def save_configuration(text, delay, start_key, stop_key, ide_mode=True):
    global saved_text
    global saved_delay
    global saved_start_key
    global saved_stop_key
    global saved_ide_mode

    saved_text = text
    saved_delay = max(float(delay),0.006)
    saved_start_key = start_key.lower()
    saved_stop_key = stop_key.lower()
    saved_ide_mode = ide_mode

    print(f"Configuration Saved (IDE Mode: {saved_ide_mode})")
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
        suppress=True
    )

    stop_hotkey_id = keyboard.add_hotkey(
        saved_stop_key,
        stop_typing,
        suppress=True
    )
    print("Hotkeys Saved")


def clear_auto_indent():
    """Used in RAW mode when editors insert unwanted auto-indents."""
    global suppress_stop

    suppress_stop = True
    pyautogui.press('esc')
    time.sleep(0.05)
    suppress_stop = False

    time.sleep(0.45)
    pyautogui.hotkey("shift", "home")
    pyautogui.hotkey('ctrl', 'backspace')


def type_line(line, delay, ide_mode=True):
    global typing
    if not typing:
        return

    # In IDE mode, we strip leading spaces so the editor handles indenting.
    # In RAW mode, we keep all leading spaces and type them manually.
    text_to_type = line.lstrip() if ide_mode else line

    # We check if the line contains ANY characters that trigger IDE auto-closing.
    # If not, or if IDE mode is OFF, we bypass the slow while-loop entirely!
    has_smart_chars = any(c in '()[]{}"\'' for c in text_to_type)

    if not ide_mode or not has_smart_chars:
        # FAST TRACK: Dump the whole line at once!
        pyautogui.write(text_to_type, interval=delay)
        return

   # Only runs for lines that actually contain brackets/quotes when IDE Mode is ON.
    in_double_quote = False
    in_single_quote = False

    i = 0
    while i < len(text_to_type):
        if not typing:
            return

        char = text_to_type[i]

        # 1. Hop over closing brackets that the IDE already auto-generated
        if char in [")", "]", "}"]:
            pyautogui.press("right")
            i += 1
            continue

        # 2. Double Quotes Flip-Flop
        elif char == '"':
            if not in_double_quote:
                pyautogui.write('"', interval=delay)
                in_double_quote = True
            else:
                pyautogui.press("right")  # Hop over the auto-generated closing quote
                in_double_quote = False
            i += 1
            continue

        # 3. Single Quotes Flip-Flop
        elif char == "'":
            if not in_single_quote:
                pyautogui.write("'", interval=delay)
                in_single_quote = True
            else:
                pyautogui.press("right")  # Hop over the auto-generated closing quote
                in_single_quote = False
            i += 1
            continue

        # 4. Normal character typing
        pyautogui.write(char, interval=delay)
        i += 1


def type_text(text, delay=0.01, ide_mode=True):
    global typing

    try:
        lines = text.splitlines()
        first_line = True
        
        for line in lines:
            if not typing:
                print("Typing stopped")
                return

            if not first_line:
                # Move to the next line
                pyautogui.press("enter")
                time.sleep(0.09)
                
                # Only try to wipe out auto-indents if we are in RAW mode!
                if not ide_mode:
                    clear_auto_indent()

            type_line(line, delay, ide_mode)
            first_line = False

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
        args=(saved_text, saved_delay, saved_ide_mode),
        daemon=True
    )

    typing_thread.start()


def stop_typing():
    global typing, suppress_stop

    # Ignore internal programmatic ESC presses (like inside clear_auto_indent)
    if suppress_stop:
        return

    typing = False
    print("Stopped Auto Typing")