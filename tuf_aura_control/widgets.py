"""Widgets custom: ColorWheel, GradientSlider, BreathingGlow."""

import tkinter as tk
import colorsys
import math

from .theme import BG_APP, FG_MUTED


def _hex_to_rgb(hexval):
    hexval = hexval.lstrip("#")
    return tuple(int(hexval[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(c))) for c in rgb])


def blend_hex(hex1, hex2, t):
    """t=0 -> hex1, t=1 -> hex2"""
    r1, g1, b1 = _hex_to_rgb(hex1)
    r2, g2, b2 = _hex_to_rgb(hex2)
    return _rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


class ColorWheel(tk.Canvas):

    def __init__(self, master, size=190, on_change=None, on_release=None):
        super().__init__(master, width=size, height=size, bg=BG_APP,
                          highlightthickness=0, cursor="crosshair")
        self.size = size
        self.cx = size / 2
        self.cy = size / 2
        self.radius = size / 2 - 4
        self.on_change = on_change
        self.on_release = on_release
        self._marker = None
        self._marker_ring = None
        self._img = None
        self._build_wheel()
        self.bind("<Button-1>", self._on_interact)
        self.bind("<B1-Motion>", self._on_interact)
        self.bind("<ButtonRelease-1>", self._on_up)

    def _build_wheel(self):
        size = self.size
        img = tk.PhotoImage(width=size, height=size)
        bg_hex = BG_APP
        r = self.radius
        rows = []
        for y in range(size):
            dy = y - self.cy
            row = []
            for x in range(size):
                dx = x - self.cx
                dist = math.hypot(dx, dy)
                if dist <= r:
                    angle = math.atan2(-dy, dx)
                    hue = (angle / (2 * math.pi)) % 1.0
                    sat = min(dist / r, 1.0)
                    rr, gg, bb = colorsys.hsv_to_rgb(hue, sat, 1.0)
                    row.append(f"#{int(rr*255):02x}{int(gg*255):02x}{int(bb*255):02x}")
                else:
                    row.append(bg_hex)
            rows.append(tuple(row))
        img.put(tuple(rows))
        self._img = img
        self.create_image(0, 0, anchor="nw", image=img)

    def _coords_to_hex(self, x, y):
        dx, dy = x - self.cx, y - self.cy
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            scale = self.radius / dist if dist else 0
            dx *= scale
            dy *= scale
            dist = self.radius
        angle = math.atan2(-dy, dx)
        hue = (angle / (2 * math.pi)) % 1.0
        sat = min(dist / self.radius, 1.0) if self.radius else 0
        rr, gg, bb = colorsys.hsv_to_rgb(hue, sat, 1.0)
        return _rgb_to_hex((rr * 255, gg * 255, bb * 255)), (self.cx + dx, self.cy + dy)

    def _on_interact(self, event):
        hexval, (mx, my) = self._coords_to_hex(event.x, event.y)
        self._draw_marker(mx, my)
        if self.on_change:
            self.on_change(hexval)

    def _on_up(self, event):
        hexval, _ = self._coords_to_hex(event.x, event.y)
        if self.on_release:
            self.on_release(hexval)

    def _draw_marker(self, x, y):
        if self._marker:
            self.delete(self._marker)
        if self._marker_ring:
            self.delete(self._marker_ring)
        self._marker_ring = self.create_oval(x - 9, y - 9, x + 9, y + 9,
                                              outline="#000000", width=1)
        self._marker = self.create_oval(x - 7, y - 7, x + 7, y + 7,
                                         outline="#ffffff", width=2)

    def set_selection_from_hex(self, hexval):
        r, g, b = [c / 255 for c in _hex_to_rgb(hexval)]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        angle = h * 2 * math.pi
        dist = s * self.radius
        x = self.cx + dist * math.cos(angle)
        y = self.cy - dist * math.sin(angle)
        self._draw_marker(x, y)


class GradientSlider(tk.Canvas):

    def __init__(self, master, width=300, height=32, value=0.5,
                 track_start="#333333", track_end="#ff7a1a",
                 on_change=None, on_release=None, ticks=None):
        super().__init__(master, width=width, height=height, bg=BG_APP,
                          highlightthickness=0, cursor="hand2")
        self.w = width
        self.h = height
        self.value = value
        self.on_change = on_change
        self.on_release = on_release
        self.knob_r = height / 2 - 3
        self._draw_track(track_start, track_end)
        if ticks:
            self._draw_ticks(ticks)
        self._glow_item = self.create_oval(0, 0, 0, 0, outline="")
        self._knob_item = self.create_oval(0, 0, 0, 0, fill="#ffffff", outline="")
        self._position_knob()

        self.bind("<Button-1>", self._on_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw_ticks(self, count):
        for i in range(count):
            frac = i / (count - 1) if count > 1 else 0
            x = self.knob_r + frac * (self.w - 2 * self.knob_r)
            self.create_line(x, self.h - 3, x, self.h, fill=FG_MUTED)

    def _draw_track(self, c1, c2):
        h = max(4, int(self.h * 0.35))
        img = tk.PhotoImage(width=self.w, height=h)
        row = []
        rgb1, rgb2 = _hex_to_rgb(c1), _hex_to_rgb(c2)
        for x in range(self.w):
            t = x / max(1, self.w - 1)
            rr = int(rgb1[0] + (rgb2[0] - rgb1[0]) * t)
            gg = int(rgb1[1] + (rgb2[1] - rgb1[1]) * t)
            bb = int(rgb1[2] + (rgb2[2] - rgb1[2]) * t)
            row.append(f"#{rr:02x}{gg:02x}{bb:02x}")
        img.put(tuple(tuple(row) for _ in range(h)))
        self._track_img = img
        y0 = (self.h - h) / 2
        self.create_image(0, y0, anchor="nw", image=img)

        self.create_oval(0, y0, h, y0 + h, fill=c1, outline=c1)
        self.create_oval(self.w - h, y0, self.w, y0 + h, fill=c2, outline=c2)

    def _knob_x(self):
        return self.knob_r + self.value * (self.w - 2 * self.knob_r)

    def _position_knob(self):
        x = self._knob_x()
        y = self.h / 2
        r = self.knob_r
        self.coords(self._glow_item, x - r - 4, y - r - 4, x + r + 4, y + r + 4)
        self.coords(self._knob_item, x - r, y - r, x + r, y + r)

    def _set_glow_color(self, hexval):
        self.itemconfig(self._glow_item, fill=hexval, outline=hexval)

    def _on_drag(self, event):
        x = max(self.knob_r, min(self.w - self.knob_r, event.x))
        self.value = (x - self.knob_r) / max(1, (self.w - 2 * self.knob_r))
        self._position_knob()
        if self.on_change:
            self.on_change(self.value)

    def _on_release(self, event):
        if self.on_release:
            self.on_release(self.value)

    def set_value(self, v, glow_color=None):
        self.value = max(0.0, min(1.0, v))
        self._position_knob()
        if glow_color:
            self._set_glow_color(glow_color)


class BreathingGlow:

    def __init__(self, canvas, cx, cy, base_radius, get_color_fn):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.base_r = base_radius
        self.get_color_fn = get_color_fn
        self.phase = 0.0
        self.running = False
        self._ring = canvas.create_oval(0, 0, 0, 0, outline="", width=2)
        self.canvas.tag_lower(self._ring)

    def start(self):
        if self.running:
            return
        self.running = True
        self._tick()

    def stop(self):
        self.running = False
        try:
            self.canvas.itemconfig(self._ring, outline="")
        except tk.TclError:
            pass

    def _tick(self):
        if not self.running:
            return
        self.phase += 0.10
        pulse = (math.sin(self.phase) + 1) / 2  # 0..1
        r = self.base_r + 8 + pulse * 12
        color = blend_hex(self.get_color_fn(), BG_APP, 0.55 + 0.30 * pulse)
        try:
            self.canvas.coords(self._ring, self.cx - r, self.cy - r, self.cx + r, self.cy + r)
            self.canvas.itemconfig(self._ring, outline=color, width=2)
            self.canvas.tag_lower(self._ring)
        except tk.TclError:
            return
        self.canvas.after(45, self._tick)
