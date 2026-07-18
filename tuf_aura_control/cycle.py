"""Lanza y controla el proceso independiente de ciclo de color."""

import os
import signal
import subprocess
import sys

from .state import (write_pid, read_pid, clear_pid,
                     read_current_color, clear_current_color)


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _is_our_daemon(pid):
    """Verifica via /proc que el pid sea realmente nuestro daemon."""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            cmdline = f.read().decode(errors="ignore")
    except OSError:
        # No estamos en Linux o el proceso ya no existe: no podemos
        # verificar, así que no asumimos que es seguro tocarlo.
        return False
    return "cycle_daemon" in cmdline


class DetachedCycleController:
    def start(self, interval_seconds=0.8):
        self.stop()
        proc = subprocess.Popen(
            [sys.executable, "-m", "tuf_aura_control.cycle_daemon",
             "--interval", str(interval_seconds)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        write_pid(proc.pid)

    def stop(self):
        pid = read_pid()
        if pid and _pid_alive(pid) and _is_our_daemon(pid):
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        clear_pid()
        clear_current_color()

    @property
    def running(self):
        pid = read_pid()
        if pid is None:
            return False
        if _pid_alive(pid) and _is_our_daemon(pid):
            return True

        clear_pid()
        clear_current_color()
        return False

    def get_current_color(self):
        return read_current_color()
