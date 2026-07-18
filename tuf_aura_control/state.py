"""Estado en disco para coordinar la GUI con el daemon de ciclo.
Usa boot_id para invalidar PIDs de sesiones anteriores.
"""

import os

STATE_DIR = os.path.join(
    os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")),
    "tuf-aura-control",
)
PID_FILE = os.path.join(STATE_DIR, "cycle.pid")
COLOR_FILE = os.path.join(STATE_DIR, "cycle_color")

_BOOT_ID_PATH = "/proc/sys/kernel/random/boot_id"


def _ensure_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def get_boot_id():
    try:
        with open(_BOOT_ID_PATH) as f:
            return f.read().strip()
    except OSError:
        return "unknown-boot"


def write_pid(pid):
    _ensure_dir()
    with open(PID_FILE, "w") as f:
        f.write(f"{get_boot_id()}:{pid}")


def read_pid():
    try:
        with open(PID_FILE) as f:
            content = f.read().strip()
        boot_id, pid_str = content.split(":", 1)
    except (FileNotFoundError, ValueError):
        return None

    if boot_id != get_boot_id():
        clear_pid()
        clear_current_color()
        return None

    try:
        return int(pid_str)
    except ValueError:
        return None


def clear_pid():
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


def write_current_color(hexval):
    _ensure_dir()
    try:
        with open(COLOR_FILE, "w") as f:
            f.write(hexval)
    except OSError:
        pass


def read_current_color():
    try:
        with open(COLOR_FILE) as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None


def clear_current_color():
    try:
        os.remove(COLOR_FILE)
    except FileNotFoundError:
        pass
