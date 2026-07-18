import tkinter as tk
from .theme import (BG_SIDEBAR, BG_CARD, BG_CARD_HOVER, FG_TEXT, FG_MUTED,
                     ACCENT, DANGER, FONT_FAMILY, SUCCESS, BORDER)
from .widgets import blend_hex


class Sidebar(tk.Frame):
    def __init__(self, master, on_select, pages, on_power_toggle=None):
        super().__init__(master, bg=BG_SIDEBAR, width=170)
        self.pack_propagate(False)
        self.on_select = on_select
        self.buttons = {}
        self._active_key = None

        tk.Label(self, text="TUF", font=(FONT_FAMILY, 20, "bold"),
                 fg=ACCENT, bg=BG_SIDEBAR).pack(pady=(28, 2))
        tk.Label(self, text="AURA CONTROL", font=(FONT_FAMILY, 8, "bold"),
                 fg=FG_MUTED, bg=BG_SIDEBAR).pack(pady=(0, 18))


        switch_wrap = tk.Frame(self, bg=BG_SIDEBAR)
        switch_wrap.pack(pady=(0, 22))
        tk.Label(switch_wrap, text="TECLADO", font=(FONT_FAMILY, 8, "bold"),
                 fg=FG_MUTED, bg=BG_SIDEBAR).pack()
        self.power_switch = PowerSwitch(switch_wrap, command=on_power_toggle)
        self.power_switch.pack(pady=(6, 4))
        self.power_label = tk.Label(switch_wrap, text="Encendido", font=(FONT_FAMILY, 9, "bold"),
                                     fg=SUCCESS, bg=BG_SIDEBAR)
        self.power_label.pack()

        tk.Frame(self, bg=BG_SIDEBAR, height=1).pack(fill="x", padx=20, pady=(0, 8))

        for key, text in pages:
            b = tk.Label(self, text=text, font=(FONT_FAMILY, 11),
                         fg=FG_TEXT, bg=BG_SIDEBAR, anchor="w", padx=22, pady=12,
                         cursor="hand2")
            b.pack(fill="x")
            b.bind("<Button-1>", lambda e, k=key: self.on_select(k))
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BG_CARD_HOVER))
            b.bind("<Leave>", lambda e, k=key, w=b: w.config(
                bg=BG_CARD if self._active_key == k else BG_SIDEBAR))
            self.buttons[key] = b

        tk.Frame(self, bg=BG_SIDEBAR).pack(fill="both", expand=True)

        self.status_dot = tk.Label(self, text="\u25cf", font=(FONT_FAMILY, 10),
                                    fg=FG_MUTED, bg=BG_SIDEBAR)
        self.status_dot.pack(side="left", padx=(22, 4), pady=16)
        self.status_text = tk.Label(self, text="Comprobando…", font=(FONT_FAMILY, 8),
                                     fg=FG_MUTED, bg=BG_SIDEBAR)
        self.status_text.pack(side="left", pady=16)

    def set_active(self, key):
        self._active_key = key
        for k, b in self.buttons.items():
            b.config(bg=BG_CARD if k == key else BG_SIDEBAR,
                      fg=ACCENT if k == key else FG_TEXT)

    def set_daemon_status(self, ok):
        if ok:
            self.status_dot.config(fg=SUCCESS)
            self.status_text.config(text="asusctl listo")
        else:
            self.status_dot.config(fg=DANGER)
            self.status_text.config(text="asusctl no encontrado")

    def set_power_state(self, is_on):
        self.power_switch.set_state(is_on)
        self.power_label.config(text="Encendido" if is_on else "Apagado",
                                 fg=SUCCESS if is_on else FG_MUTED)


class PowerSwitch(tk.Canvas):

    WIDTH = 64
    HEIGHT = 30
    ANIM_STEPS = 8
    ANIM_DELAY_MS = 12

    def __init__(self, master, command=None):
        super().__init__(master, width=self.WIDTH, height=self.HEIGHT,
                          bg=BG_SIDEBAR, highlightthickness=0, cursor="hand2")
        self.command = command
        self.is_on = True
        self._knob_frac = 1.0  # 0 = izquierda (off), 1 = derecha (on)
        self._anim_job = None
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)
        self._draw(self._knob_frac)

    def set_state(self, is_on):
        self.is_on = is_on
        target = 1.0 if is_on else 0.0
        self._animate_to(target)

    def _animate_to(self, target):
        if self._anim_job:
            self.after_cancel(self._anim_job)
        start = self._knob_frac
        steps = self.ANIM_STEPS

        def step(i=0):
            t = i / steps
            self._knob_frac = start + (target - start) * t
            self._draw(self._knob_frac)
            if i < steps:
                self._anim_job = self.after(self.ANIM_DELAY_MS, lambda: step(i + 1))
            else:
                self._knob_frac = target
                self._draw(self._knob_frac)
                self._anim_job = None

        step()

    def _draw(self, frac):
        self.delete("all")
        w, h, r = self.WIDTH, self.HEIGHT, self.HEIGHT // 2
        track_color = blend_hex(BORDER, SUCCESS, frac) if frac not in (0, 1) else (
            SUCCESS if frac == 1 else BORDER)

        self.create_oval(0, 0, h, h, fill=track_color, outline=track_color)
        self.create_oval(w - h, 0, w, h, fill=track_color, outline=track_color)
        self.create_rectangle(r, 0, w - r, h, fill=track_color, outline=track_color)

        knob_d = h - 6
        knob_x = 3 + frac * (w - h)
        self.create_oval(knob_x, 3, knob_x + knob_d, 3 + knob_d,
                          fill="#ffffff", outline="#ffffff")


def rounded_swatch(canvas, w, h, color):
    canvas.delete("all")
    r = 14
    canvas.create_oval(0, 0, r * 2, r * 2, fill=color, outline=color)
    canvas.create_oval(w - r * 2, 0, w, r * 2, fill=color, outline=color)
    canvas.create_oval(0, h - r * 2, r * 2, h, fill=color, outline=color)
    canvas.create_oval(w - r * 2, h - r * 2, w, h, fill=color, outline=color)
    canvas.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
    canvas.create_rectangle(0, r, w, h - r, fill=color, outline=color)


def make_button(master, text, command, primary=False, danger=False):
    bg = ACCENT if primary else (DANGER if danger else BG_CARD)
    fg = "#1a1a1a" if primary else "#ffffff"
    hover_bg = "#ff9142" if primary else ("#c73b36" if danger else BG_CARD_HOVER)

    btn = tk.Label(master, text=text, font=(FONT_FAMILY, 10, "bold"),
                    bg=bg, fg=fg, padx=22, pady=10, cursor="hand2")
    btn.bind("<Button-1>", lambda e: command())
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def make_rounded_panel(parent, width, height, bg=BG_CARD, border=BORDER, radius=18, app_bg=None):
    from .theme import BG_APP
    outer_bg = app_bg if app_bg is not None else BG_APP

    canvas = tk.Canvas(parent, width=width, height=height, bg=outer_bg, highlightthickness=0)
    d = radius * 2
    canvas.create_oval(0, 0, d, d, fill=bg, outline=border)
    canvas.create_oval(width - d, 0, width, d, fill=bg, outline=border)
    canvas.create_oval(0, height - d, d, height, fill=bg, outline=border)
    canvas.create_oval(width - d, height - d, width, height, fill=bg, outline=border)
    canvas.create_rectangle(radius, 0, width - radius, height, fill=bg, outline=bg)
    canvas.create_rectangle(0, radius, width, height - radius, fill=bg, outline=bg)
    # bordes superior e inferior
    canvas.create_line(radius, 1, width - radius, 1, fill=border)
    canvas.create_line(radius, height - 1, width - radius, height - 1, fill=border)

    inner = tk.Frame(canvas, bg=bg)
    canvas.create_window(radius, radius // 2 + 4, anchor="nw",
                          window=inner, width=width - radius * 2)

    return canvas, inner
