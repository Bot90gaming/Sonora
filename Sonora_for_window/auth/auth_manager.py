"""
Auth manager — supports both anonymous and OAuth-authenticated access.

OAuth token is stored at ~/.config/ytmusic_player/oauth.json.
If the file exists and is valid the app starts authenticated; otherwise
it falls back to anonymous mode.  Call setup_oauth() to (re-)authenticate.
"""
from __future__ import annotations
import os
from pathlib import Path
from ytmusicapi import YTMusic
import ytmusicapi as _ytm

_TOKEN_DIR  = Path.home() / ".config" / "ytmusic_player"
_TOKEN_FILE = _TOKEN_DIR / "oauth.json"


def token_path() -> Path:
    return _TOKEN_FILE


def is_authenticated() -> bool:
    return _TOKEN_FILE.exists() and _TOKEN_FILE.stat().st_size > 10


def get_ytmusic_client() -> YTMusic:
    """Return an authenticated client if a token exists, else anonymous."""
    if is_authenticated():
        try:
            return YTMusic(str(_TOKEN_FILE))
        except Exception:
            pass
    return YTMusic()


def setup_from_headers(headers_raw: str) -> str:
    """
    Authenticate using raw browser request headers pasted by the user.
    ytmusicapi parses the Cookie / Authorization headers and saves a token.
    Returns the token file path on success, raises on failure.
    """
    _TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    _ytm.setup(filepath=str(_TOKEN_FILE), headers_raw=headers_raw)
    return str(_TOKEN_FILE)


def logout():
    """Remove the stored OAuth token."""
    try:
        _TOKEN_FILE.unlink(missing_ok=True)
    except Exception:
        pass