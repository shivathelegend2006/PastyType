import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# =====================================================================
# TOKENS — one dark charcoal family top to bottom.
# =====================================================================
BG           = "#0B0D10"   # root — the desk
CARD         = "#15181D"   # card surface, one step lighter than BG
CARD_BORDER  = "#262A31"   # quiet edge between card and desk

TERM_BG      = "#0F1114"   # recessed one level deeper than CARD
TERM_BORDER  = "#20242B"   # subtle inset border, same family as CARD_BORDER

INK          = "#ECEEF1"   # primary text — near-white, not pure white
INK_SOFT     = "#8B93A1"   # secondary/caption text — muted blue-gray

GREEN        = "#4ADE80"   # single accent — refined mint, not neon
GREEN_DEEP   = "#2FAE64"   # hover/pressed state
GREEN_DIM    = "#1D2A22"   # accent tint for subtle fills (delay entry bg, etc.)

RED          = "#F87171"   # stop/danger — muted red-orange
RED_DIM      = "#2A1E1E"   # danger tint for subtle fills

FONT_TITLE   = ("Arial", 34, "bold")
FONT_TAGLINE = ("Arial", 11, "bold")
FONT_LABEL   = ("Arial", 12, "bold")
FONT_CAPTION = ("Arial", 10)
FONT_MONO    = ("Consolas", 15, "bold")

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
        self.root.geometry("950x720")
        self.root.minsize(780, 580)
        self.root.configure(fg_color=BG)

        # Custom titlebar needs the native chrome gone.
        self.root.overrideredirect(True)
        self._set_neon_icon()

        self._syncing = False
        self._hotkey_values = {"start": "Q", "stop": "ESC"}
        self._hotkey_widgets = {}
        self._listening = {"start": False, "stop": False}

        self._drag_offset = (0, 0)

        self.build_titlebar()
        self.build_ui()

    def _set_neon_icon(self):
        icon = tk.PhotoImage(width=32, height=32)
        icon.put(GREEN, to=(0, 0, 32, 32))
        self._icon_ref = icon
        self.root.iconphoto(True, icon)

    # =================================================================
    # Custom titlebar — matches the app palette instead of the OS default
    # =================================================================
    def build_titlebar(self):
        bar = ctk.CTkFrame(self.root, fg_color=CARD, height=40, corner_radius=0)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=14)

        dot = ctk.CTkFrame(left, fg_color=GREEN, width=10, height=10, corner_radius=5)
        dot.pack(side="left", pady=15)
        dot.pack_propagate(False)

        ctk.CTkLabel(
            left, text="PastyType", font=("Arial", 12, "bold"), text_color=INK,
        ).pack(side="left", padx=(8, 0))

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=8)

        close_btn = ctk.CTkButton(
            right, text="✕", width=32, height=28, corner_radius=6,
            fg_color="transparent", hover_color=RED_DIM, text_color=INK_SOFT,
            font=("Arial", 12), command=self.root.destroy,
        )
        close_btn.pack(side="right", padx=(4, 0))

        min_btn = ctk.CTkButton(
            right, text="—", width=32, height=28, corner_radius=6,
            fg_color="transparent", hover_color=CARD_BORDER, text_color=INK_SOFT,
            font=("Arial", 12), command=self._minimize,
        )
        min_btn.pack(side="right")

        for widget in (bar, left):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)

    def _minimize(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def _start_drag(self, event):
        self._drag_offset = (event.x_root - self.root.winfo_x(),
                              event.y_root - self.root.winfo_y())

    def _do_drag(self, event):
        x = event.x_root - self._drag_offset[0]
        y = event.y_root - self._drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def _on_restore(self, event=None):
        if self.root.state() == "normal":
            self.root.overrideredirect(True)

    # =================================================================
    def build_ui(self):
        self.root.bind("<Map>", self._on_restore)

        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(side="top", fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------
        # Masthead + Instructions Button (3-Column Perfectly Centered Grid)
        # -------------------------------------------------------
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 4))
        
        # We give col 0 and col 2 identical weights AND identical minimum sizes
        top.grid_columnconfigure(0, weight=1, minsize=150)
        top.grid_columnconfigure(1, weight=0)
        top.grid_columnconfigure(2, weight=1, minsize=150)

        # Invisible dummy spacer on the left guarantees exact mathematical symmetry
        spacer = ctk.CTkFrame(top, fg_color="transparent", width=150, height=34)
        spacer.grid(row=0, column=0, sticky="w")

        head = ctk.CTkFrame(top, fg_color="transparent")
        head.grid(row=0, column=1)

        ctk.CTkLabel(head, text="PastyType", font=FONT_TITLE, text_color=INK).pack()
        ctk.CTkLabel(
            head, text=spaced("clipboard -> keystrokes"),
            font=FONT_TAGLINE, text_color=GREEN,
        ).pack(pady=(4, 0))

        # Matches Start button dimensions & font, styled as a secondary action
        self.instructions_btn = ctk.CTkButton(
            top,
            text="Instructions",
            fg_color=CARD,
            hover_color=CARD_BORDER,
            text_color=INK,
            border_width=1,
            border_color=CARD_BORDER,
            height=34,
            width=150,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=self.show_instructions
        )
        self.instructions_btn.grid(
            row=0,
            column=2,
            sticky="e"
        )

        # -------------------------------------------------------
        # Card Surface
        # -------------------------------------------------------
        self.main = ctk.CTkFrame(
            body, fg_color=CARD, corner_radius=14,
            border_width=1, border_color=CARD_BORDER,
        )
        self.main.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.main, text="Paste Your Text", anchor="w",
            font=FONT_LABEL, text_color=INK,
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 8))

        self.textbox = ctk.CTkTextbox(
            self.main, fg_color=TERM_BG, text_color=GREEN, font=("Consolas", 16),
            corner_radius=10, border_width=1, border_color=TERM_BORDER, wrap="word",
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=22)

        # -------------------------------------------------------
        # Controls
        # -------------------------------------------------------
        controls = ctk.CTkFrame(self.main, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=22, pady=16)
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
            progress_color=GREEN, button_color=GREEN, button_hover_color=GREEN_DEEP,
            fg_color=CARD_BORDER,
            command=self.on_slider_change,
        )
        self.delay_slider.set(10)
        self.delay_slider.grid(row=0, column=1, sticky="ew", padx=15)

        self.delay_entry = ctk.CTkEntry(
            controls, width=90, justify="center", font=FONT_MONO,
            fg_color=GREEN_DIM, text_color=GREEN, border_color=GREEN, border_width=1,
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
        ).grid(row=1, column=0, sticky="w", pady=(24, 0))

        keys_row = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )
        keys_row.grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="nsew",
            pady=(20, 8)
        )
        keys_row.grid_columnconfigure(0, weight=1)
        keys_row.grid_columnconfigure(1, weight=0)
        keys_row.grid_columnconfigure(2, weight=1)

        start = self._build_key(keys_row, "start", GREEN, GREEN_DIM)
        start.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(
            keys_row,
            text="click a key box,\nthen press key to bind",
            font=FONT_CAPTION,
            text_color=INK_SOFT,
            justify="center",
        ).grid(row=0, column=1, padx=10, pady=(12, 0))

        stop = self._build_key(keys_row, "stop", RED, RED_DIM)
        stop.grid(row=0, column=2, sticky="ew", padx=(12, 0))

        # --- Start action & Footer Note ------------------------------------
        action_row = ctk.CTkFrame(controls, fg_color="transparent")
        action_row.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(16, 8)
        )
        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=0)

        # Subtle, professional helpful hint filling the bottom left space
        ctk.CTkLabel(
            action_row,
            text="ⓘ Tip: Review instructions before starting your first run.",
            font=FONT_CAPTION,
            text_color=INK_SOFT,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(4, 0))

        self.start_button = ctk.CTkButton(
            action_row, text="Start Typing",
            fg_color=GREEN, hover_color=GREEN_DEEP, text_color="#0B0D10",
            height=34, width=150, corner_radius=8, font=("Arial", 13, "bold"),
            border_width=0,
        )
        self.start_button.grid(row=0, column=1, sticky="e")

    # =================================================================
    # Instructions Modal
    # =================================================================
    def show_instructions(self):
        window = ctk.CTkToplevel(self.root)
        window.title("Instructions")
        window.geometry("650x500")

        textbox = ctk.CTkTextbox(
            window,
            wrap="word"
        )
        textbox.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )
        textbox.insert(
            "1.0",
            """
Instructions go here.

Replace this text later.
"""
        )
        textbox.configure(state="disabled")

    # =================================================================
    # Hotkey capture
    # =================================================================
    def _build_key(self, parent, name, accent, tint):
        block = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(
            block, text=spaced(name), font=("Arial", 10, "bold"), text_color=INK_SOFT,
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            block, width=90, height=38, justify="center",
            font=("Arial", 15, "bold"),
            fg_color=tint, text_color=accent,
            border_color=accent, border_width=1, corner_radius=8,
        )
        entry.insert(0, self._hotkey_values[name])
        entry.pack(fill="x", expand=True, pady=(2, 6))

        entry.bind("<Key>", lambda e, n=name: self._capture_key(e, n))
        entry.bind("<Button-1>", lambda e, n=name: self._start_listen(n))
        entry.bind("<FocusOut>", lambda e, n=name: self._cancel_listen(n))

        self._hotkey_widgets[name] = entry
        return block

    def _accent_for(self, name):
        return (GREEN, GREEN_DIM) if name == "start" else (RED, RED_DIM)

    def _start_listen(self, name):
        entry = self._hotkey_widgets[name]
        self._listening[name] = True
        entry.configure(fg_color=CARD_BORDER, border_color=INK, text_color=INK)
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
        accent, tint = self._accent_for(name)
        entry.configure(fg_color=tint, border_color=accent, text_color=accent)

    def _capture_key(self, event, name):
        if event.keysym in _MODIFIER_KEYS:
            return "break"

        display = format_keysym(event.keysym)
        self._hotkey_values[name] = display
        self._listening[name] = False

        entry = self._hotkey_widgets[name]
        entry.delete(0, "end")
        entry.insert(0, display)
        accent, tint = self._accent_for(name)
        entry.configure(fg_color=tint, border_color=accent, text_color=accent)

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