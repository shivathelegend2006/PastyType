import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# =====================================================================
# TOKENS — light gray desk, white card, neon green accent. The paste
# box is the one place that keeps a "terminal" feel.
# =====================================================================
BG          = "#EAEAEA"   # everything around the card — the desk
CARD        = "#FFFFFF"   # the card itself — always white
BORDER      = "#D9D9D9"   # card edge, sits quietly against BG
INK         = "#17251C"
INK_SOFT    = "#5C7A63"
GREEN       = "#39FF14"   # neon accent — buttons, slider, start hotkey
GREEN_TEXT  = "#1FA82B"   # slightly deeper green for small text on white (legibility)
RED         = "#C6473F"
LISTEN_BG   = "#EAF7EC"

TERM_BG     = "#0B1E3D"   # navy — the terminal now reads as a console screen
TERM_TEXT   = GREEN       # neon green text on navy
TERM_BORDER = "#1B3A63"   # muted navy border

SLIDER_TRACK = "#2E3B32"  # dark green-gray track, independent of the terminal navy

FONT_TITLE = ("Arial", 32, "bold")
FONT_LABEL = ("Arial", 12, "bold")
FONT_MONO  = ("Arial", 14, "bold")

_MODIFIER_KEYS = {
    "Shift_L", "Shift_R", "Control_L", "Control_R",
    "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock", "Super_L", "Super_R",
    "Meta_L", "Meta_R",
}

_KEY_DISPLAY = {
    "Escape": "ESC", "space": "SPACE", "Return": "ENTER",
    "BackSpace": "BACKSPACE", "Tab": "TAB", "Delete": "DEL",
    "Up": "UP", "Down": "DOWN", "Left": "LEFT", "Right": "RIGHT",
    "Home": "HOME", "End": "END", "Prior": "PGUP", "Next": "PGDN",
}


def spaced(text: str) -> str:
    return " ".join(list(text.upper()))


def format_keysym(keysym: str) -> str:
    return _KEY_DISPLAY.get(keysym, keysym.upper())


class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("PastyType")
        self.root.geometry("950x700")
        self.root.minsize(780, 560)
        self.root.configure(fg_color=BG)
        self._set_neon_icon()

        self._syncing = False
        self._hotkey_values = {"start": "Q", "stop": "ESC"}
        self._hotkey_widgets = {}
        self._listening = {"start": False, "stop": False}

        self.build_ui()

    def _set_neon_icon(self):
        """Solid neon-green window icon — built with tk.PhotoImage directly,
        no image file or extra library (e.g. Pillow) required."""
        icon = tk.PhotoImage(width=32, height=32)
        icon.put(GREEN, to=(0, 0, 32, 32))
        self._icon_ref = icon  # keep a reference alive
        self.root.iconphoto(True, icon)

    # =================================================================
    def build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------
        # Masthead
        # -------------------------------------------------------
        head = ctk.CTkFrame(self.root, fg_color="transparent")
        head.grid(row=0, column=0, pady=(24, 4))

        ctk.CTkLabel(head, text="PastyType", font=FONT_TITLE, text_color=INK).pack()
        ctk.CTkLabel(
            head, text=spaced("clipboard -> keystrokes"),
            font=("Arial", 11, "bold"), text_color=GREEN_TEXT,
        ).pack(pady=(2, 0))

        # -------------------------------------------------------
        # Card, floating on the gray desk (root background)
        # -------------------------------------------------------
        self.main = ctk.CTkFrame(
            self.root, fg_color=CARD, corner_radius=12,
            border_width=1, border_color=BORDER,
        )
        self.main.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.main, text="Paste Your Text", anchor="w",
            font=FONT_LABEL, text_color=INK,
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 8))

        self.textbox = ctk.CTkTextbox(
            self.main, fg_color=TERM_BG, text_color=TERM_TEXT, font=("Consolas", 17),
            corner_radius=8, border_width=1, border_color=TERM_BORDER, wrap="word",
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=22)

        # -------------------------------------------------------
        # Controls
        # -------------------------------------------------------
        controls = ctk.CTkFrame(self.main, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=22, pady=20)
        controls.grid_columnconfigure(0, weight=0, minsize=170)
        controls.grid_columnconfigure(1, weight=1)
        controls.grid_columnconfigure(2, weight=0, minsize=90)

        # --- Typing delay ---------------------------------------------
        ctk.CTkLabel(
            controls, text="Typing Delay (ms)",
            font=FONT_LABEL, text_color=INK, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.delay_slider = ctk.CTkSlider(
            controls, from_=1, to=100, number_of_steps=99,
            progress_color=GREEN, button_color=GREEN, button_hover_color=GREEN_TEXT,
            fg_color=SLIDER_TRACK,
            command=self.on_slider_change,
        )
        self.delay_slider.set(10)
        self.delay_slider.grid(row=0, column=1, sticky="ew", padx=15)

        self.delay_entry = ctk.CTkEntry(
            controls, width=90, justify="center", font=FONT_MONO,
            fg_color="#F4FAF5", text_color=INK, border_color=GREEN, border_width=2,
        )
        self.delay_entry.insert(0, "10")
        self.delay_entry.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        self.delay_entry.bind("<KeyRelease>", self.on_entry_change)
        self.delay_entry.bind("<FocusOut>", self.on_entry_finalize)
        self.delay_entry.bind("<Return>", self.on_entry_finalize)

        # --- Hotkeys ---------------------------------------------------
        ctk.CTkLabel(
            controls, text="Hotkeys",
            font=FONT_LABEL, text_color=INK, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(28, 0))

        keys_row = ctk.CTkFrame(controls, fg_color="transparent")
        keys_row.grid(row=1, column=1, columnspan=2, sticky="w", pady=(28, 0))

        self._build_key(keys_row, "start", GREEN, side="left")
        self._build_key(keys_row, "stop", RED, side="left", padx=(18, 0))

        ctk.CTkLabel(
            controls, text="click a key box, then press the key to bind",
            font=("Arial", 10), text_color=INK_SOFT,
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # --- Start button ---------------------------------------------------
        self.start_button = ctk.CTkButton(
            controls, text="START TYPING",
            fg_color=GREEN, hover_color=GREEN_TEXT, text_color="black",
            height=50, corner_radius=10, font=("Arial", 16, "bold"),
            border_width=2, border_color=INK,
        )
        self.start_button.grid(row=3, column=0, columnspan=3, pady=(30, 4), sticky="ew")

    # =================================================================
    # Hotkey capture — pure Tkinter/CTk, no external library required.
    # =================================================================
    def _build_key(self, parent, name, border_color, side="left", padx=(0, 0)):
        block = ctk.CTkFrame(parent, fg_color="transparent")
        block.pack(side=side, padx=padx)

        ctk.CTkLabel(
            block, text=spaced(name), font=("Arial", 10, "bold"), text_color=INK_SOFT,
        ).pack(anchor="w", pady=(0, 4))

        text_color = GREEN_TEXT if border_color == GREEN else border_color
        entry = ctk.CTkEntry(
            block, width=90, height=42, justify="center",
            font=("Arial", 15, "bold"),
            fg_color="#F4FAF5", text_color=text_color,
            border_color=border_color, border_width=3, corner_radius=8,
        )
        entry.insert(0, self._hotkey_values[name])
        entry.pack()

        entry.bind("<Key>", lambda e, n=name: self._capture_key(e, n))
        entry.bind("<Button-1>", lambda e, n=name: self._start_listen(n))
        entry.bind("<FocusOut>", lambda e, n=name: self._cancel_listen(n))

        self._hotkey_widgets[name] = entry
        return entry

    def _start_listen(self, name):
        entry = self._hotkey_widgets[name]
        self._listening[name] = True
        entry.configure(fg_color=LISTEN_BG, border_color=INK, text_color=INK)
        entry.delete(0, "end")
        entry.insert(0, "...")
        entry.focus_set()

    def _cancel_listen(self, name):
        if not self._listening[name]:
            return
        self._listening[name] = False
        entry = self._hotkey_widgets[name]
        entry.delete(0, "end")
        entry.insert(0, self._hotkey_values[name])
        border = GREEN if name == "start" else RED
        text_color = GREEN_TEXT if name == "start" else RED
        entry.configure(fg_color="#F4FAF5", border_color=border, text_color=text_color)

    def _capture_key(self, event, name):
        if event.keysym in _MODIFIER_KEYS:
            return "break"

        display = format_keysym(event.keysym)
        self._hotkey_values[name] = display
        self._listening[name] = False

        entry = self._hotkey_widgets[name]
        entry.delete(0, "end")
        entry.insert(0, display)
        border = GREEN if name == "start" else RED
        text_color = GREEN_TEXT if name == "start" else RED
        entry.configure(fg_color="#F4FAF5", border_color=border, text_color=text_color)

        self.root.focus_set()
        return "break"

    # =================================================================
    # Sync logic: slider <-> entry
    # =================================================================
    def on_slider_change(self, value):
        if self._syncing:
            return
        self._syncing = True
        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, str(int(round(value))))
        self._syncing = False

    def on_entry_change(self, event=None):
        if self._syncing:
            return
        text = self.delay_entry.get().strip()
        if not text.isdigit():
            return
        value = max(1, min(100, int(text)))
        self._syncing = True
        self.delay_slider.set(value)
        self._syncing = False

    def on_entry_finalize(self, event=None):
        text = self.delay_entry.get().strip()
        value = int(self.delay_slider.get()) if not text.isdigit() else max(1, min(100, int(text)))
        self._syncing = True
        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, str(value))
        self.delay_slider.set(value)
        self._syncing = False

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()