"""
Auth manager — browser-headers method, no framework dependency.
Token stored at ~/.config/ytmusic_player/oauth.json.
"""
from __future__ import annotations
from pathlib import Path
from ytmusicapi import YTMusic
import ytmusicapi as _ytm

_TOKEN_DIR  = Path.home() / ".config" / "ytmusic_player"
_TOKEN_FILE = _TOKEN_DIR / "oauth.json"


def is_authenticated() -> bool:
    return _TOKEN_FILE.exists() and _TOKEN_FILE.stat().st_size > 10


def get_ytmusic_client() -> YTMusic:
    if is_authenticated():
        try:
            return YTMusic(str(_TOKEN_FILE))
        except Exception:
            pass
    return YTMusic()


def setup_from_headers(headers_raw: str) -> str:
    _TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    _ytm.setup(filepath=str(_TOKEN_FILE), headers_raw=headers_raw)
    return str(_TOKEN_FILE)


def logout():
    try:
        _TOKEN_FILE.unlink(missing_ok=True)
    except Exception:
        pass
