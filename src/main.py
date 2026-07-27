# Om Namo Venketesaya

from ui import App

import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
    

def is_admin():
    """Returns True if the program is running as Administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin():
    """Ask the user whether they want to restart as Administrator."""

    root = tk.Tk()
    root.withdraw()

    elevate = messagebox.askyesno(
        "Administrator Required",
        "PastyType requires Administrator privileges for keyboard "
        "simulation to work correctly.\n\n"
        "Would you like to restart PastyType as Administrator now?"
    )

    root.destroy()

    if elevate:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )

    # Close this non-admin instance whether they accepted or declined.
    sys.exit()


def main():

    if not is_admin():
        request_admin()

    app = App()
    app.run()


if __name__ == "__main__":
    main()