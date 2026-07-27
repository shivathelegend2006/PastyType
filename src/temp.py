import ctypes
import random
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
import typer

ctk.set_default_color_theme("green")



THEMES = {
    "light": {
        "BG":            "#F3EFE6",   # warm bone / parchment paper
        "BG_GRAIN_LO":   "#EAE5DC",   # grain speckle, slightly darker
        "BG_GRAIN_HI":   "#FAF7F0",   # grain speckle, lighter cream
        "CARD":          "#FAFAF5",   # clean warm ivory deck
        "CARD_BORDER":   "#DCD7CC",   # crisp stone hairline edge
        "TERM_BG":       "#EBE6DC",   # recessed paper deck for textbox
        "TERM_BORDER":   "#D4CEBF",   # inset bezel frame
        "INK":           "#1A1917",   # deep espresso ink
        "TERM_INK":      "#1A1917",   # espresso ink for light mode textbox
        "INK_SOFT":      "#54504A",   # WCAG-compliant dark stone for crisp readability
        "ACCENT":        "#D2691E",   # warm cinnamon / amber
        "ACCENT_DEEP":   "#B85514",   # hover / pressed state
        "ACCENT_DIM":    "#FDF2E3",   # accent tint for pill fills
        "ACCENT_SHADOW": "#A67843",   # bezel shadow beneath keycaps
        "ACCENT_BRIGHT": "#B85514",   # rich cinnamon for borders/text
        "ACCENT_KEY_BG": "#FFF9F0",   # creamy beige keycap background
        "STOP":          "#C2412D",   # tactile terracotta red
        "STOP_DIM":      "#FBEBE8",   # danger tint for fills
        "STOP_SHADOW":   "#993322",   # bezel shadow for stop keycap
        "STOP_BRIGHT":   "#A83020",   # rich terracotta text/border
        "STOP_KEY_BG":   "#FFF0EE",   # creamy light stop background
        "TIP_TEXT":      "#7D786E",   # crisp readable tip text
        "SWITCH_BTN":    "#FFFFFF",   # IDE switch button thumb color
        "TOGGLE_ICON":   "☾",         # Show moon icon when in light mode (to click into dark)
    },
    "dark": {
        "BG":            "#141312",   # deep warm espresso
        "BG_GRAIN_LO":   "#100F0D",   # grain speckle, darker
        "BG_GRAIN_HI":   "#1B1917",   # grain speckle, lighter
        "CARD":          "#1C1A18",   # raised warm asphalt
        "CARD_BORDER":   "#2E2A26",   # hairline edge, warm stone
        "TERM_BG":       "#100F0E",   # recessed terminal
        "TERM_BORDER":   "#242019",   # inset border
        "INK":           "#F2EFE9",   # crisp cream text
        "TERM_INK":      "#FFE066",   # vibrant readable yellow for dark mode textbox
        "INK_SOFT":      "#9C968E",   # muted warm stone
        "ACCENT":        "#E5A93B",   # refined amber/gold
        "ACCENT_DEEP":   "#C68F2E",   # hover / pressed state
        "ACCENT_DIM":    "#3A2E1A",   # accent tint for subtle fills
        "ACCENT_SHADOW": "#8A6A22",   # bezel shadow beneath keycaps
        "ACCENT_BRIGHT": "#FFCF70",   # brighter amber for borders/text
        "ACCENT_KEY_BG": "#4A3B22",   # rich dark keycap background
        "STOP":          "#C9705F",   # muted rust
        "STOP_DIM":      "#2E211D",   # danger tint for subtle fills
        "STOP_SHADOW":   "#7C4436",   # bezel shadow for stop keycap
        "STOP_BRIGHT":   "#FFA595",   # brighter rust text/border
        "STOP_KEY_BG":   "#4A2B25",   # rich dark stop background
        "TIP_TEXT":      "#BDB6AC",   # disclaimer/tip text
        "SWITCH_BTN":    "#F2EFE9",   # IDE switch button thumb color
        "TOGGLE_ICON":   "☀",         # Show sun icon when in dark mode (to click into light)
    }
}

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


def format_keysym(keysym: str) -> str:
    return _KEY_DISPLAY.get(keysym, keysym.upper())


def _first_available_font(candidates, fallback):
    """Pick the first installed font family from candidates, else fallback."""
    try:
        installed = {f.lower() for f in tkfont.families()}
    except Exception:
        return fallback
    for name in candidates:
        if name.lower() in installed:
            return name
    return fallback


class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("1080x750")
        self.root.minsize(900, 600)

        # Default start mode
        self.current_mode = "light"
        self.T = THEMES[self.current_mode]
        ctk.set_appearance_mode(self.current_mode)
        self.root.configure(fg_color=self.T["BG"])

        # Custom titlebar needs the native chrome gone.
        self.root.overrideredirect(True)

        self._resolve_fonts()
        self._set_accent_icon()

        self._syncing = False
        self._hotkey_values = {"start": "Q", "stop": "ESC"}
        self._hotkey_widgets = {}
        self._listening = {"start": False, "stop": False}

        self._drag_offset = (0, 0)
        self._is_minimized = False

        self._add_grain_texture()
        self.build_titlebar()
        self.build_ui()

        self._set_taskbar_presence()

    def _resolve_fonts(self):
        mono = _first_available_font(
            ["JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas"],
            "Consolas",
        )
        sans = _first_available_font(
            ["Poppins", "Century Gothic", "Segoe UI Semibold", "Segoe UI"],
            "Arial",
        )

        self.FONT_TITLE      = (sans, 34, "bold")
        self.FONT_TAGLINE    = (mono, 13, "bold")
        self.FONT_LABEL      = (mono, 13, "bold")
        self.FONT_CAPTION    = (mono, 11)
        self.FONT_MONO       = (mono, 15, "bold")
        self.FONT_SMALL_MONO = (mono, 12, "bold")
        self.FONT_KEYCAP     = (mono, 18, "bold")
        self.FONT_TIP        = (mono, 13)
        self.FONT_BTN        = (sans, 14, "bold")
        self.FONT_TITLEBAR   = (sans, 12, "bold")

    def _add_grain_texture(self):
        if hasattr(self, "_grain_canvas") and self._grain_canvas:
            self._grain_canvas.destroy()

        canvas = tk.Canvas(
            self.root, bg=self.T["BG"], highlightthickness=0, bd=0,
        )
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        rng = random.Random(7)
        w, h = 1080, 750
        for _ in range(650):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            shade = self.T["BG_GRAIN_HI"] if rng.random() > 0.5 else self.T["BG_GRAIN_LO"]
            size = 1 if rng.random() > 0.15 else 2
            canvas.create_rectangle(
                x, y, x + size, y + size, fill=shade, outline="",
            )
        self._grain_canvas = canvas

    def _set_taskbar_presence(self):
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080
            style = style | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)

            self.root.withdraw()
            self.root.after(10, self.root.deiconify)
        except Exception as e:
            print(f"Taskbar presence fix failed: {e}")

    def save_configuration(self):
        text = self.textbox.get("1.0", "end-1c")
        delay = float(self.delay_slider.get()) / 1000
        start = self._hotkey_values["start"]
        stop = self._hotkey_values["stop"]
        ide_mode = self.ide_mode_switch.get() == 1

        typer.save_configuration(
            text, delay, start, stop, ide_mode
        )

    def _set_accent_icon(self):
        icon = tk.PhotoImage(width=32, height=32)
        icon.put(self.T["ACCENT"], to=(0, 0, 32, 32))
        self._icon_ref = icon
        self.root.iconphoto(True, icon)

    # =================================================================
    # THEME TOGGLE LOGIC — Flawless instant hot-swapping!
    # =================================================================
    def toggle_theme(self):
        # Swap the mode string
        self.current_mode = "dark" if self.current_mode == "light" else "light"
        self.T = THEMES[self.current_mode]
        
        # Apply global CustomTkinter appearance mode
        ctk.set_appearance_mode(self.current_mode)
        self.root.configure(fg_color=self.T["BG"])
        
        # Re-render background grain and icon for the new theme
        self._add_grain_texture()
        self._set_accent_icon()

        # Re-build UI widgets with the updated color palette tokens
        for child in self.root.winfo_children():
            if child != self._grain_canvas:
                child.destroy()
                
        self.build_titlebar()
        self.build_ui()

    def build_titlebar(self):
        bar = ctk.CTkFrame(self.root, fg_color=self.T["CARD"], height=40, corner_radius=0)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)

        hairline = ctk.CTkFrame(self.root, fg_color=self.T["CARD_BORDER"], height=1, corner_radius=0)
        hairline.pack(side="top", fill="x")

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=14)

        dot = ctk.CTkFrame(left, fg_color=self.T["ACCENT"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", pady=15)
        dot.pack_propagate(False)

        ctk.CTkLabel(
            left, text="PastyType", font=self.FONT_TITLEBAR, text_color=self.T["INK"],
        ).pack(side="left", padx=(8, 0))

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=8)

        close_btn = ctk.CTkButton(
            right, text="✕", width=32, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.T["STOP_DIM"], text_color=self.T["INK_SOFT"],
            font=self.FONT_TITLEBAR, command=self.root.destroy,
        )
        close_btn.pack(side="right", padx=(4, 0))

        min_btn = ctk.CTkButton(
            right, text="—", width=32, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.T["CARD_BORDER"], text_color=self.T["INK_SOFT"],
            font=self.FONT_TITLEBAR, command=self._minimize,
        )
        min_btn.pack(side="right", padx=(0, 4))

        # --- THEME TOGGLE PILL BUTTON (Integrated smoothly into Titlebar) ---
        self.theme_btn = ctk.CTkButton(
            right, text=f"{self.T['TOGGLE_ICON']} Theme", width=74, height=26, corner_radius=13,
            fg_color=self.T["ACCENT_DIM"], hover_color=self.T["CARD_BORDER"],
            text_color=self.T["ACCENT"], font=(self.FONT_TITLEBAR[0], 11, "bold"),
            border_width=1, border_color=self.T["ACCENT"],
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right", padx=(0, 8))

        for widget in (bar, left):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)

    def _minimize(self):
        self._is_minimized = True
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
        if self._is_minimized and self.root.state() == "normal":
            self._is_minimized = False
            self.root.overrideredirect(True)
            self._set_taskbar_presence()

    # =================================================================
    def build_ui(self):
        self.root.bind("<Map>", self._on_restore)

        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(side="top", fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=36, pady=(24, 6))

        top.grid_columnconfigure(0, weight=1, minsize=150)
        top.grid_columnconfigure(1, weight=0)
        top.grid_columnconfigure(2, weight=1, minsize=150)

        spacer = ctk.CTkFrame(top, fg_color="transparent", width=150, height=34)
        spacer.grid(row=0, column=0, sticky="w")

        head = ctk.CTkFrame(top, fg_color="transparent")
        head.grid(row=0, column=1)

        ctk.CTkLabel(head, text="PastyType", font=self.FONT_TITLE, text_color=self.T["INK"]).pack()
        ctk.CTkLabel(
            head, text="Clipboard → Keystrokes",
            font=self.FONT_TAGLINE, text_color=self.T["ACCENT"],
        ).pack(pady=(6, 0))

        self.instructions_btn = ctk.CTkButton(
            top,
            text="Instructions",
            fg_color=self.T["CARD"],
            hover_color=self.T["CARD_BORDER"],
            text_color=self.T["INK"],
            border_width=1,
            border_color=self.T["CARD_BORDER"],
            height=34,
            width=150,
            corner_radius=8,
            font=self.FONT_BTN,
            command=self.show_instructions
        )
        self.instructions_btn.grid(
            row=0,
            column=2,
            sticky="e"
        )

        self.main = ctk.CTkFrame(
            body, fg_color=self.T["CARD"], corner_radius=14,
            border_width=1, border_color=self.T["CARD_BORDER"],
        )
        self.main.grid(row=1, column=0, sticky="nsew", padx=36, pady=14)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.main, text="Paste Your Text", anchor="w",
            font=self.FONT_LABEL, text_color=self.T["INK"],
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(24, 8))

        term_bezel = ctk.CTkFrame(
            self.main, fg_color=self.T["TERM_BORDER"], corner_radius=10,
        )
        term_bezel.grid(row=1, column=0, sticky="nsew", padx=28)
        term_bezel.grid_columnconfigure(0, weight=1)
        term_bezel.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            term_bezel, fg_color=self.T["TERM_BG"], text_color=self.T["TERM_INK"],
            font=(self.FONT_MONO[0], 16),
            corner_radius=8, border_width=0, wrap="word",
        )
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        controls = ctk.CTkFrame(self.main, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=28, pady=20)
        controls.grid_columnconfigure(0, weight=0, minsize=170)
        controls.grid_columnconfigure(1, weight=1)
        controls.grid_columnconfigure(2, weight=0, minsize=90)

        # --- Typing delay ---------------------------------------------
        ctk.CTkLabel(
            controls, text="Typing Delay",
            font=self.FONT_LABEL, text_color=self.T["INK"], anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.delay_slider = ctk.CTkSlider(
            controls, from_=0, to=100, number_of_steps=100,
            height=14, corner_radius=7,
            progress_color=self.T["ACCENT"], button_color=self.T["ACCENT"],
            button_hover_color=self.T["ACCENT_DEEP"], button_corner_radius=8,
            button_length=16, border_width=0,
            fg_color=self.T["TERM_BORDER"],
            command=self.on_slider_change,
        )
        self.delay_slider.set(10)
        self.delay_slider.grid(row=0, column=1, sticky="ew", padx=18)

        self.delay_entry = ctk.CTkEntry(
            controls, width=90, height=32, justify="center",
            font=self.FONT_SMALL_MONO,
            fg_color=self.T["ACCENT_DIM"], text_color=self.T["ACCENT"],
            border_color=self.T["ACCENT"], border_width=1, corner_radius=16,
        )
        self.delay_entry.insert(0, "10 ms")
        self.delay_entry.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        self.delay_entry.bind("<KeyRelease>", self.on_entry_change)
        self.delay_entry.bind("<FocusOut>", self.on_entry_finalize)
        self.delay_entry.bind("<Return>", self.on_entry_finalize)

        # --- IDE Mode Toggle -------------------------------------------
        ctk.CTkLabel(
            controls, text="IDE Auto-Indent",
            font=self.FONT_LABEL, text_color=self.T["INK"], anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(22, 0))

        toggle_frame = ctk.CTkFrame(controls, fg_color="transparent")
        toggle_frame.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(18, 0), pady=(22, 0))
        self.ide_mode_switch = ctk.CTkSwitch(
            toggle_frame,
            text="",
            progress_color=self.T["ACCENT"],
            button_color=self.T["SWITCH_BTN"],
            button_hover_color=self.T["ACCENT_DIM"],
            fg_color=self.T["TERM_BORDER"],
            border_color=self.T["CARD_BORDER"],
            width=46,
            switch_height=20,
            switch_width=46,
            corner_radius=10,
        )
        self.ide_mode_switch.select()
        self.ide_mode_switch.pack(side="left")

        ctk.CTkLabel(
            toggle_frame,
            text="Turn ON for smart editors (auto-indents & closes brackets). Turn OFF for raw textboxes.",
            font=self.FONT_CAPTION,
            text_color=self.T["INK_SOFT"],
            anchor="w"
        ).pack(side="left", padx=(12, 0))

        # --- Hotkeys ---------------------------------------------------
        ctk.CTkLabel(
            controls, text="Hotkeys",
            font=self.FONT_LABEL, text_color=self.T["INK"], anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(22, 0))

        keys_row = ctk.CTkFrame(controls, fg_color="transparent")
        keys_row.grid(row=1, column=1, columnspan=2, sticky="nsew", pady=(18, 4))
        keys_row.grid_columnconfigure(0, weight=1)
        keys_row.grid_columnconfigure(1, weight=0)
        keys_row.grid_columnconfigure(2, weight=1)

        start = self._build_key(keys_row, "start", self.T["ACCENT_BRIGHT"], self.T["ACCENT_KEY_BG"], self.T["ACCENT_SHADOW"])
        start.grid(row=0, column=0, sticky="ew", padx=(0, 16))

        ctk.CTkLabel(
            keys_row,
            text="Click a key box,\nthen press key to bind",
            font=self.FONT_CAPTION,
            text_color=self.T["INK_SOFT"],
            justify="center",
        ).grid(row=0, column=1, padx=12, sticky="s", pady=(0, 14))

        stop = self._build_key(keys_row, "stop", self.T["STOP_BRIGHT"], self.T["STOP_KEY_BG"], self.T["STOP_SHADOW"])
        stop.grid(row=0, column=2, sticky="ew", padx=(16, 0))

        # --- Start action & Footer Note ------------------------------------
        action_row = ctk.CTkFrame(controls, fg_color="transparent")
        action_row.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(18, 4))
        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            action_row,
            text="ⓘ Tip: Review instructions before starting your first run.",
            font=self.FONT_TIP,
            text_color=self.T["TIP_TEXT"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(4, 0))

        self.start_button = ctk.CTkButton(
            action_row,
            text="Save",
            fg_color=self.T["ACCENT"],
            hover_color=self.T["ACCENT_DEEP"],
            text_color="#FFFFFF" if self.current_mode == "light" else "#1C1706",
            height=36,
            width=150,
            corner_radius=8,
            font=self.FONT_BTN,
            command=self.save_configuration
        )
        self.start_button.grid(row=0, column=1, sticky="e")

    def show_instructions(self):
        window = ctk.CTkToplevel(self.root)
        window.title("PastyType — Instructions")
        window.geometry("740x620")
        window.minsize(600, 500)
        
        # Dedicated custom dark theme: dark graphite background with cream text
        dark_bg = "#1E1E1E"
        cream_text = "#F0EAD6"
        border_color = "#333333"
        
        window.configure(fg_color=dark_bg)

        # Container frame for nice padding and border
        frame = ctk.CTkFrame(window, fg_color="#141414", corner_radius=12, border_width=1, border_color=border_color)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        textbox = ctk.CTkTextbox(
            frame,
            wrap="word",
            fg_color="transparent",
            text_color=cream_text,
            font=(self.FONT_MONO[0], 14),
            border_width=0,
        )
        textbox.pack(fill="both", expand=True, padx=24, pady=24)

        instructions_text = """AUTO-TYPER SETUP & INSTRUCTIONS
====================================================================
Auto-Typer is a blind GUI keyboard automation tool. Because it types directly into your active window without reading the underlying editor code, understanding how to configure your typing mode and environment is critical for preventing misaligned text.


1. CHOOSE YOUR TYPING MODE
--------------------------------------------------------------------
Your editor's built-in behavior dictates which mode you must use. Using the wrong mode will cause double-indentation, duplicated brackets, or flat unformatted code.

• Smart IDE Mode (Toggle ON):
  Use for VS Code, LeetCode, HackerRank, PyCharm, or WebStorm. Smart editors automatically indent new lines and auto-close brackets and quotes. In this mode, Auto-Typer strips leading whitespace so it doesn't fight your editor's auto-indentation, using a predictive flip-flop algorithm to hop over auto-generated closing brackets.

• Raw Mode (Toggle OFF):
  Use for Notepad, basic web text boxes, terminal prompts, or simple plain-text editors that do not format text for you. Auto-Typer physically types every space, quote, and bracket from scratch, automatically converting hidden tab characters (\\t) into 4 physical spaces.


2. HOTKEYS & CONFIGURATION
--------------------------------------------------------------------
You can customize your control keys directly in the interface:

• Start Hotkey: Triggers the typing sequence in whatever window currently holds your cursor focus.
• Stop Hotkey (Kill Switch): Immediately aborts the typing loop.
• Typing Delay: Controls speed between keystrokes (e.g., 10ms for fast typing, 50ms for a slower human cadence).

To bind a new key: Click the key box, press your desired key or combination, and click Save.


3. THE GOLDEN RULES FOR 99% RELIABILITY
--------------------------------------------------------------------
• Hands Off While Running:
  Do not touch your mouse or keyboard after pressing Start. A stray click or keypress will break cursor synchronization and ruin indentation.

• Wait for Browser IDEs:
  When automating a coding test in a web browser, click into the code editor and wait a full second before pressing Start to allow web rendering latency to settle.

• Use a Safe Delay Floor:
  Keeping a minimum delay of 10ms to 20ms gives web-based editors enough time to process character rendering without dropping keys.


4. KNOWN LIMITATIONS & WARNINGS
--------------------------------------------------------------------
Because Auto-Typer operates at the OS hardware level, expect a ~90% to 95% out-of-the-box success rate across random environments. If the script fails, check for these common triggers:

• Aggressive AI Popups:
  Inline AI suggestions (Copilot/IntelliSense) can intercept the Enter key. Temporarily disable aggressive ghost-text in your target editor.

• OS CPU Spikes:
  Heavy background system CPU loads can stretch sleep timers, causing arrow-key jumps to process out of order.

• Niche Editor Quirks:
  If Smart IDE Mode misbehaves on a proprietary web editor, switch to Raw Mode, turn off auto-closing brackets in the website's settings, and let Auto-Typer brute-force the formatting.

⚠️ IF THE LAYOUT BREAKS: Hit your Stop Hotkey immediately, clear the editor, check your mode toggle, and try again."""

        textbox.insert("1.0", instructions_text)
        textbox.configure(state="disabled")

    def _build_key(self, parent, name, accent_bright, key_bg, shadow):
        block = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(
            block, text=name.capitalize(), font=self.FONT_LABEL, text_color=self.T["INK_SOFT"],
        ).pack(anchor="w", pady=(0, 6))

        bezel = ctk.CTkFrame(block, fg_color=shadow, corner_radius=10)
        bezel.pack(fill="x", expand=True, pady=(0, 6))

        entry = ctk.CTkEntry(
            bezel, width=110, height=44, justify="center",
            font=self.FONT_KEYCAP,
            fg_color=key_bg, text_color=accent_bright,
            border_color=accent_bright, border_width=2, corner_radius=8,
        )
        entry.insert(0, self._hotkey_values[name])
        entry.pack(fill="x", expand=True, padx=1, pady=(1, 3))

        entry.bind("<Key>", lambda e, n=name: self._capture_key(e, n))
        entry.bind("<Button-1>", lambda e, n=name: self._start_listen(n))
        entry.bind("<FocusOut>", lambda e, n=name: self._cancel_listen(n))

        self._hotkey_widgets[name] = entry
        return block

    def _accent_for(self, name):
        return (self.T["ACCENT_BRIGHT"], self.T["ACCENT_KEY_BG"]) if name == "start" else (self.T["STOP_BRIGHT"], self.T["STOP_KEY_BG"])

    def _start_listen(self, name):
        entry = self._hotkey_widgets[name]
        self._listening[name] = True
        entry.configure(fg_color=self.T["CARD_BORDER"], border_color=self.T["INK"], text_color=self.T["INK"])
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

    def on_slider_change(self, value):
        if self._syncing:
            return
        self._syncing = True
        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, f"{int(round(value))} ms")
        self._syncing = False

    def on_entry_change(self, event=None):
        if self._syncing:
            return
        text = self.delay_entry.get().strip().replace("ms", "").strip()
        if not text.isdigit():
            return
        value = max(0, min(100, int(text)))
        self._syncing = True
        self.delay_slider.set(value)
        self._syncing = False

    def on_entry_finalize(self, event=None):
        text = self.delay_entry.get().strip().replace("ms", "").strip()
        value = int(self.delay_slider.get()) if not text.isdigit() else max(0, min(100, int(text)))
        self._syncing = True
        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, f"{value} ms")
        self.delay_slider.set(value)
        self._syncing = False

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()