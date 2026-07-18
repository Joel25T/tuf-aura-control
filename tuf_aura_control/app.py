import tkinter as tk
from tkinter import colorchooser, messagebox

from .theme import (BG_APP, BG_CARD, FG_TEXT, FG_MUTED, ACCENT, DANGER, SUCCESS,
                     FONT_FAMILY, BRIGHTNESS_LEVELS, BORDER)
from .ui import Sidebar, rounded_swatch, make_button, make_rounded_panel
from .widgets import ColorWheel, GradientSlider, BreathingGlow
from .cycle import DetachedCycleController
from .backend import AsusctlBackend
from .config import load_config

PAGES = [
    ("static", "Color Estático"),
    ("cycle", "Ciclo de Color"),
    ("settings", "Ajustes"),
]


class TUFAuraControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TUF Aura Control")
        self.root.geometry("820x580")
        self.root.configure(bg=BG_APP)
        self.root.minsize(820, 580)
        self.root.resizable(False, False)

        self.config = load_config()
        self.backend = AsusctlBackend(self.config)
        self.current_color = "#ff7a1a"
        self.keyboard_on = True
        self.cycle_controller = DetachedCycleController()
        self._cycle_current_hex = "#444444"

        self._build_layout()
        self._check_daemon()
        self.select_page("static")
        self._sync_cycle_state_on_startup()



    def _build_layout(self):
        self.sidebar = Sidebar(self.root, self.select_page, PAGES,
                                on_power_toggle=self.toggle_power)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.root, bg=BG_APP)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {
            "static": self._build_static_page(),
            "cycle": self._build_cycle_page(),
            "settings": self._build_settings_page(),
        }

        self.status_bar = tk.Label(self.root, text="Listo", font=(FONT_FAMILY, 9),
                                    fg=FG_MUTED, bg=BG_APP, anchor="w", padx=20)
        self.status_bar.pack(side="bottom", fill="x", pady=(0, 8))

    def select_page(self, key):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[key].pack(fill="both", expand=True, padx=28, pady=24)
        self.sidebar.set_active(key)



    def _build_static_page(self):
        page = tk.Frame(self.content, bg=BG_APP)

        tk.Label(page, text="Color Estático", font=(FONT_FAMILY, 20, "bold"),
                 fg=FG_TEXT, bg=BG_APP).pack(anchor="w")
        tk.Label(page, text="Toca la rueda para elegir un matiz — se aplica en vivo.",
                 font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_APP).pack(anchor="w", pady=(2, 18))

        row = tk.Frame(page, bg=BG_APP)
        row.pack(anchor="w", fill="x")


        wheel_canvas, wheel_inner = make_rounded_panel(row, width=250, height=260, radius=20)
        wheel_canvas.pack(side="left")

        self.color_wheel = ColorWheel(wheel_inner, size=190,
                                       on_change=self._on_wheel_change,
                                       on_release=self._on_wheel_release)
        self.color_wheel.pack(padx=14, pady=(14, 10))
        self.color_wheel.set_selection_from_hex(self.current_color)


        info_canvas, info_inner = make_rounded_panel(row, width=310, height=260, radius=20)
        info_canvas.pack(side="left", padx=(16, 0))

        tk.Label(info_inner, text="COLOR ACTIVO", font=(FONT_FAMILY, 8, "bold"),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(10, 8), padx=4)

        swatch_wrap = tk.Frame(info_inner, bg=BG_CARD)
        swatch_wrap.pack(anchor="w", padx=4)
        self.swatch = tk.Canvas(swatch_wrap, width=90, height=90, bg=BG_CARD, highlightthickness=0)
        self.swatch.pack()
        self.swatch_glow = BreathingGlow(self.swatch, 45, 45, 30, lambda: self.current_color)
        rounded_swatch(self.swatch, 90, 90, self.current_color)
        self.swatch_glow.start()

        self.hex_label = tk.Label(info_inner, text=self.current_color.upper(),
                                   font=(FONT_FAMILY, 15, "bold"), fg=FG_TEXT, bg=BG_CARD)
        self.hex_label.pack(anchor="w", pady=(10, 14), padx=4)

        make_button(info_inner, "Color Exacto (HEX)…", self.pick_color_dialog).pack(
            anchor="w", padx=4)

        self._build_brightness_section(page)

        return page

    def _build_brightness_section(self, parent):
        bcanvas, binner = make_rounded_panel(parent, width=576, height=110, radius=18)
        bcanvas.pack(pady=(18, 0))

        header = tk.Frame(binner, bg=BG_CARD)
        header.pack(fill="x", padx=6, pady=(10, 4))
        tk.Label(header, text="BRILLO DEL TECLADO", font=(FONT_FAMILY, 9, "bold"),
                 fg=FG_MUTED, bg=BG_CARD).pack(side="left")
        self.brightness_readout = tk.Label(header, text=BRIGHTNESS_LEVELS[2].upper(),
                                            font=(FONT_FAMILY, 9, "bold"), fg=ACCENT, bg=BG_CARD)
        self.brightness_readout.pack(side="right")

        self.brightness_slider = GradientSlider(
            binner, width=520, height=30, value=2 / 3,
            track_start="#2a2a2a", track_end=ACCENT, ticks=4,
            on_change=self._on_brightness_drag,
            on_release=self._on_brightness_release,
        )
        self.brightness_slider.pack(padx=6, pady=(6, 4))

        labels = tk.Frame(binner, bg=BG_CARD)
        labels.pack(fill="x", padx=6)
        for lvl in BRIGHTNESS_LEVELS:
            tk.Label(labels, text=lvl.upper(), font=(FONT_FAMILY, 7),
                     fg=FG_MUTED, bg=BG_CARD, width=12, anchor="w").pack(side="left")

    def _on_wheel_change(self, hexval):
        self.current_color = hexval
        rounded_swatch(self.swatch, 90, 90, hexval)
        self.hex_label.config(text=hexval.upper())

    def _on_wheel_release(self, hexval):
        self._apply_new_color(hexval)

    def _on_brightness_drag(self, value):
        idx = round(value * (len(BRIGHTNESS_LEVELS) - 1))
        self.brightness_readout.config(text=BRIGHTNESS_LEVELS[idx].upper())

    def _on_brightness_release(self, value):
        idx = round(value * (len(BRIGHTNESS_LEVELS) - 1))
        snapped = idx / (len(BRIGHTNESS_LEVELS) - 1)
        self.brightness_slider.set_value(snapped)
        level = BRIGHTNESS_LEVELS[idx]
        result = self.backend.set_brightness(level)
        color = FG_MUTED if result.ok else DANGER
        self.status_bar.config(text=result.message, fg=color)
        if not self.keyboard_on and level != "off":
            self._set_power_state(True, reapply_color=True, silent_status=True)



    def _build_cycle_page(self):
        page = tk.Frame(self.content, bg=BG_APP)

        tk.Label(page, text="Ciclo de Color", font=(FONT_FAMILY, 20, "bold"),
                 fg=FG_TEXT, bg=BG_APP).pack(anchor="w")
        tk.Label(page,
                 text="Emulado por software (reaplica 'static' con un color distinto\n"
                      "en cada intervalo) — no hay efecto nativo en placas monozona.",
                 font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_APP, justify="left").pack(
            anchor="w", pady=(2, 18))

        row = tk.Frame(page, bg=BG_APP)
        row.pack(anchor="w", fill="x")

        pcanvas, pinner = make_rounded_panel(row, width=576, height=150, radius=20)
        pcanvas.pack()

        inner_row = tk.Frame(pinner, bg=BG_CARD)
        inner_row.pack(padx=10, pady=14)

        self.cycle_swatch = tk.Canvas(inner_row, width=100, height=100, bg=BG_CARD,
                                       highlightthickness=0)
        self.cycle_swatch.pack(side="left")
        self.cycle_glow = BreathingGlow(self.cycle_swatch, 50, 50, 32,
                                         lambda: self._cycle_current_hex)
        rounded_swatch(self.cycle_swatch, 100, 100, "#444444")

        controls = tk.Frame(inner_row, bg=BG_CARD)
        controls.pack(side="left", padx=24)

        self.cycle_status_lbl = tk.Label(controls, text="● Detenido", font=(FONT_FAMILY, 12, "bold"),
                                          fg=FG_MUTED, bg=BG_CARD)
        self.cycle_status_lbl.pack(anchor="w", pady=(4, 14))

        self.cycle_btn = make_button(controls, "Iniciar Ciclo", self.toggle_cycle, primary=True)
        self.cycle_btn.pack(anchor="w")

        scanvas, sinner = make_rounded_panel(page, width=576, height=110, radius=18)
        scanvas.pack(pady=(18, 0))

        header = tk.Frame(sinner, bg=BG_CARD)
        header.pack(fill="x", padx=6, pady=(10, 4))
        tk.Label(header, text="VELOCIDAD", font=(FONT_FAMILY, 9, "bold"),
                 fg=FG_MUTED, bg=BG_CARD).pack(side="left")
        self.speed_readout = tk.Label(header, text="Media", font=(FONT_FAMILY, 9, "bold"),
                                       fg=ACCENT, bg=BG_CARD)
        self.speed_readout.pack(side="right")

        self.speed_slider = GradientSlider(
            sinner, width=520, height=30, value=0.6,
            track_start="#2a2a2a", track_end=ACCENT,
            on_change=self._on_speed_drag, on_release=self._on_speed_release,
        )
        self.speed_slider.pack(padx=6, pady=(6, 4))

        labels = tk.Frame(sinner, bg=BG_CARD)
        labels.pack(fill="x", padx=6)
        tk.Label(labels, text="LENTO", font=(FONT_FAMILY, 7), fg=FG_MUTED, bg=BG_CARD,
                  anchor="w").pack(side="left")
        tk.Label(labels, text="RÁPIDO", font=(FONT_FAMILY, 7), fg=FG_MUTED, bg=BG_CARD,
                  anchor="e").pack(side="right")

        self.cycle_speed_seconds = self._speed_value_to_seconds(0.6)

        return page

    @staticmethod
    def _speed_value_to_seconds(value):

        return 3.0 - value * (3.0 - 0.15)

    def _on_speed_drag(self, value):
        seconds = self._speed_value_to_seconds(value)
        label = "Rápida" if seconds < 0.6 else ("Lenta" if seconds > 2.0 else "Media")
        self.speed_readout.config(text=label)
        self.cycle_speed_seconds = seconds

    def _on_speed_release(self, value):
        self.cycle_speed_seconds = self._speed_value_to_seconds(value)
        if self.cycle_controller.running:
            self.cycle_controller.start(interval_seconds=self.cycle_speed_seconds)

    def _poll_cycle_state(self):
        if not self.cycle_controller.running:
            self.cycle_btn.config(text="Iniciar Ciclo")
            self.cycle_status_lbl.config(text="● Detenido", fg=FG_MUTED)
            self.cycle_glow.stop()
            return
        hexval = self.cycle_controller.get_current_color()
        if hexval:
            self._cycle_current_hex = hexval
            rounded_swatch(self.cycle_swatch, 100, 100, hexval)
        self.root.after(200, self._poll_cycle_state)

    def toggle_cycle(self):
        if not self.cycle_controller.running:
            if not self.keyboard_on:
                self._set_power_state(True, reapply_color=False, silent_status=True)
            self.cycle_controller.start(interval_seconds=self.cycle_speed_seconds)
            self.cycle_btn.config(text="Detener Ciclo")
            self.cycle_status_lbl.config(text="● Activo", fg=ACCENT)
            self.cycle_glow.start()
            self.status_bar.config(
                text="Ciclo activo — sigue corriendo aunque cierres la ventana", fg=FG_MUTED)
            self._poll_cycle_state()
        else:
            self.cycle_controller.stop()
            self.cycle_glow.stop()
            self.cycle_btn.config(text="Iniciar Ciclo")
            self.cycle_status_lbl.config(text="● Detenido", fg=FG_MUTED)
            self.status_bar.config(text="Ciclo de color detenido", fg=FG_MUTED)

    def _sync_cycle_state_on_startup(self):
        if self.cycle_controller.running:
            self.cycle_btn.config(text="Detener Ciclo")
            self.cycle_status_lbl.config(text="● Activo", fg=ACCENT)
            self.cycle_glow.start()
            self.status_bar.config(text="Ciclo de color ya estaba activo", fg=FG_MUTED)
            self._poll_cycle_state()



    def _build_settings_page(self):
        page = tk.Frame(self.content, bg=BG_APP)

        tk.Label(page, text="Ajustes", font=(FONT_FAMILY, 20, "bold"),
                 fg=FG_TEXT, bg=BG_APP).pack(anchor="w")
        tk.Label(page, text="Información de hardware y límites conocidos.",
                 font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_APP).pack(anchor="w", pady=(2, 18))

        canvas, inner = make_rounded_panel(page, width=576, height=440, radius=20)
        canvas.pack()

        tk.Label(inner, text=self.config.get("model_notes", ""),
                 font=(FONT_FAMILY, 9), fg=FG_TEXT, bg=BG_CARD, justify="left",
                 wraplength=520, anchor="w").pack(fill="x", padx=8, pady=(14, 16))

        tk.Label(inner, text="BUG CONOCIDO: BRILLO DE TECLADO", font=(FONT_FAMILY, 9, "bold"),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", padx=8)
        tk.Label(inner,
                 text="En algunos modelos ASUS, 'asusctl leds set <nivel>'\n"
                      "responde sin error pero el brillo físico no cambia — es\n"
                      "un problema reportado en el propio proyecto asusctl. Esta\n"
                      "app intenta un fallback silencioso vía sysfs, que requiere\n"
                      "permisos (regla udev) para funcionar sin sudo.",
                 font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_CARD, justify="left").pack(
            anchor="w", padx=8, pady=(6, 16))

        tk.Label(inner, text="CONFIGURACIÓN AVANZADA", font=(FONT_FAMILY, 9, "bold"),
                 fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", padx=8)
        tk.Label(inner, text="~/.config/tuf-aura-control/config.json",
                 font=(FONT_FAMILY, 9), fg=FG_TEXT, bg=BG_CARD).pack(anchor="w", padx=8, pady=(4, 0))
        tk.Label(inner,
                 text="Si tu modelo usa otros comandos de asusctl, edita ese\n"
                      "archivo en vez de tocar el código fuente.",
                 font=(FONT_FAMILY, 8), fg=FG_MUTED, bg=BG_CARD, justify="left").pack(
            anchor="w", padx=8, pady=(4, 0))

        return page



    def _check_daemon(self):
        found = self.backend.is_available()
        self.sidebar.set_daemon_status(found)
        if not found:
            self.status_bar.config(text="asusctl no está instalado o no está en PATH", fg=DANGER)

    def pick_color_dialog(self):
        result = colorchooser.askcolor(title="Elige un color", initialcolor=self.current_color)
        if not result or not result[1]:
            return
        hexval = result[1]
        rounded_swatch(self.swatch, 90, 90, hexval)
        self.hex_label.config(text=hexval.upper())
        self.color_wheel.set_selection_from_hex(hexval)
        self._apply_new_color(hexval)

    def _apply_new_color(self, hexval):
        self.current_color = hexval

        self.cycle_controller.stop()
        self.cycle_glow.stop()
        if hasattr(self, "cycle_btn"):
            self.cycle_btn.config(text="Iniciar Ciclo")
            self.cycle_status_lbl.config(text="● Detenido", fg=FG_MUTED)

        if not self.keyboard_on:
            self.keyboard_on = True
            self.sidebar.set_power_state(True)

        outcome = self.backend.set_static_color(hexval)
        color = FG_MUTED if outcome.ok else DANGER
        self.status_bar.config(text=outcome.message, fg=color)

    def toggle_power(self):
        self._set_power_state(not self.keyboard_on, reapply_color=True, silent_status=False)

    def _set_power_state(self, turn_on, reapply_color, silent_status):
        if turn_on:
            self.keyboard_on = True
            self.sidebar.set_power_state(True)
            if reapply_color:
                outcome = self.backend.set_static_color(self.current_color)
                if not silent_status:
                    color = FG_MUTED if outcome.ok else DANGER
                    self.status_bar.config(text=outcome.message, fg=color)
        else:
            self.cycle_controller.stop()
            if hasattr(self, "cycle_glow"):
                self.cycle_glow.stop()
            if hasattr(self, "cycle_btn"):
                self.cycle_btn.config(text="Iniciar Ciclo")
                self.cycle_status_lbl.config(text="● Detenido", fg=FG_MUTED)
            self.keyboard_on = False
            self.sidebar.set_power_state(False)
            outcome = self.backend.power_off()
            if not silent_status:
                color = FG_MUTED if outcome.ok else DANGER
                self.status_bar.config(text=outcome.message, fg=color)

    def on_closing(self):
        if self.cycle_controller.running:
            answer = messagebox.askyesnocancel(
                "Ciclo de color activo",
                "El ciclo de color sigue corriendo en segundo plano.\n\n"
                "Sí: lo detengo y el teclado se queda en el último color.\n"
                "No: lo dejo corriendo (podrás volver a abrir la app después\n"
                "para controlarlo, o detenerlo manualmente con:\n"
                "pkill -f tuf_aura_control.cycle_daemon)",
            )
            if answer is None:  # Cancelar: no cerrar la ventana
                return
            if answer:  # Sí: detenerlo antes de cerrar
                self.cycle_controller.stop()
        self.root.destroy()


def run():
    root = tk.Tk()
    app = TUFAuraControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
