"""Backend de asusctl con fallback sysfs para brillo."""

import subprocess
import shutil
import os


class CommandResult:
    def __init__(self, ok, message):
        self.ok = ok
        self.message = message


class AsusctlBackend:
    def __init__(self, config):
        self.config = config

    def is_available(self):
        return shutil.which("asusctl") is not None

    def _run(self, args, ok_msg, err_prefix):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=5)
        except FileNotFoundError:
            return CommandResult(False, "asusctl no encontrado en el sistema")
        except subprocess.TimeoutExpired:
            return CommandResult(False, f"{err_prefix}: tiempo de espera agotado")
        except Exception as e:
            return CommandResult(False, f"{err_prefix}: {e}")

        if result.returncode == 0:
            return CommandResult(True, ok_msg)
        detail = result.stderr.strip() or "sin detalles"
        return CommandResult(False, f"{err_prefix}: {detail}")

    def set_static_color(self, hex_color):
        hexval = hex_color.replace("#", "").upper()
        cmd = [c.replace("{color}", hexval) for c in self.config["commands"]["static_color"]]
        return self._run(cmd, f"Color estático aplicado: #{hexval}", "No se pudo aplicar el color")

    def set_brightness(self, level):
        """level: uno de 'off', 'low', 'med', 'high'."""
        cmd = [c.replace("{level}", level) for c in self.config["commands"]["keyboard_brightness"]]
        result = self._run(cmd, f"Brillo: {level}", "No se pudo cambiar el brillo")

        # Fallback sysfs por si asusctl responde OK pero no cambia nada
        if result.ok:
            self._try_sysfs_fallback(level)
        return result

    def _try_sysfs_fallback(self, level):
        path = self.config.get("brightness_sysfs_fallback")
        if not path or not os.path.exists(path):
            return
        level_map = {"off": 0, "low": 1, "med": 2, "high": 3}
        value = level_map.get(level)
        if value is None:
            return
        try:
            with open(path, "w") as f:
                f.write(str(value))
        except (PermissionError, OSError):
            pass

    def power_off(self):
        cmd = list(self.config["commands"]["power_off"])
        return self._run(cmd, "Teclado apagado", "No se pudo apagar el teclado")
