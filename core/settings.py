"""
Persistent settings — stored at ~/.config/ytmusic_player/settings.json
"""
from __future__ import annotations
import json
from pathlib import Path

_DIR  = Path.home() / ".config" / "ytmusic_player"
_FILE = _DIR / "settings.json"

_DEFAULTS: dict = {
    "theme":           "dark",      # "dark" | "light" | "system"
    "glass_effect":    True,
    "accent":          "violet",    # "violet"|"blue"|"green"|"rose"|"orange"
    "audio_quality":   "best",      # "best" | "medium" | "low"
    "autonext":        True,
    "download_dir":    "",          # "" → XDG_MUSIC_DIR / ~/Music
    "download_format": "mp3",
}

_cache: dict | None = None


def load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        _cache = {**_DEFAULTS, **json.loads(_FILE.read_text())}
    except Exception:
        _cache = dict(_DEFAULTS)
    return _cache


def save(data: dict):
    global _cache
    _cache = data
    _DIR.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(data, indent=2))


def get(key: str):
    return load().get(key, _DEFAULTS.get(key))


def set(key: str, value):
    d = load()
    d[key] = value
    save(d)
