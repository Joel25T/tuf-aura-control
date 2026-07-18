"""Configuración de comandos de asusctl, con override por usuario."""

import json
import os

DEFAULT_CONFIG = {
    "model_notes": "ASUS TUF Gaming A16 (FA607NUG) - RGB monozona",

    "commands": {
        "static_color": ["asusctl", "aura", "effect", "static", "--colour", "{color}"],
        "keyboard_brightness": ["asusctl", "leds", "set", "{level}"],
        "power_off": ["asusctl", "aura", "effect", "static", "--colour", "000000"],
    },
    "brightness_sysfs_fallback": "/sys/class/leds/asus::kbd_backlight/brightness",
}

CONFIG_DIR = os.path.expanduser("~/.config/tuf-aura-control")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    """Carga la config default y la mezcla con el override del usuario si existe."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            return _deep_merge(DEFAULT_CONFIG, user_cfg)
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def write_example_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    return CONFIG_PATH
