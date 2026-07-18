"""Daemon del ciclo de color. Corre como proceso independiente de la GUI.

    python3 -m tuf_aura_control.cycle_daemon --interval 0.8
    pkill -f tuf_aura_control.cycle_daemon
"""

import argparse
import colorsys
import signal
import sys
import time

from .backend import AsusctlBackend
from .config import load_config
from .state import write_current_color, clear_current_color

_running = True


def _handle_stop(signum, frame):
    global _running
    _running = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=0.8)
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    config = load_config()
    backend = AsusctlBackend(config)

    hue = 0.0
    try:
        while _running:
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            hexval = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            backend.set_static_color(hexval)
            write_current_color(hexval)
            hue = (hue + 0.015) % 1.0
            time.sleep(max(0.05, args.interval))
    finally:
        clear_current_color()


if __name__ == "__main__":
    sys.exit(main())
