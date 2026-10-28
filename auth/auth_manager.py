"""
Authentication via Google OAuth or browser request headers.
"""
from __future__ import annotations
from collections.abc import Callable
import json
import os
from pathlib import Path
import time
import webbrowser
from threading import Event

from ytmusicapi import OAuthCredentials, YTMusic
import ytmusicapi as _ytm

_TOKEN_DIR  = Path.home() / ".config" / "ytmusic_player"
_TOKEN_FILE = _TOKEN_DIR / "oauth.json"
_GOOGLE_TOKEN_FILE = _TOKEN_DIR / "google_oauth.json"
_GOOGLE_CREDENTIALS_FILE = _TOKEN_DIR / "google_oauth_credentials.json"
_PACKAGED_GOOGLE_CREDENTIALS_FILE = Path(__file__).with_name(
    "google_oauth_client.json")
_GOOGLE_CLIENT_ID_ENV = "SONORA_GOOGLE_CLIENT_ID"
_GOOGLE_CLIENT_SECRET_ENV = "SONORA_GOOGLE_CLIENT_SECRET"


def _google_oauth_credentials() -> dict[str, str]:
    if _GOOGLE_CREDENTIALS_FILE.exists():
        credentials = json.loads(_GOOGLE_CREDENTIALS_FILE.read_text())
    else:
        packaged_file = os.environ.get(
            "SONORA_GOOGLE_OAUTH_CONFIG",
            str(_PACKAGED_GOOGLE_CREDENTIALS_FILE),
        )
        if Path(packaged_file).is_file():
            credentials = json.loads(Path(packaged_file).read_text())
        else:
            credentials = {
                "client_id": os.environ.get(_GOOGLE_CLIENT_ID_ENV, ""),
                "client_secret": os.environ.get(_GOOGLE_CLIENT_SECRET_ENV, ""),
            }

    client_id = credentials.get("client_id", "")
    client_secret = credentials.get("client_secret", "")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Google sign-in is not configured by this Sonora installation. "
            "Use Request headers or contact the app distributor."
        )
    return {"client_id": client_id, "client_secret": client_secret}


def is_google_oauth_configured() -> bool:
    try:
        _google_oauth_credentials()
    except (OSError, ValueError, RuntimeError):
        return False
    return True


def sanitize_headers_dict(headers: dict[str, str]) -> dict[str, str]:
    """Sanitize parsed headers to ensure no corrupted or hop-by-hop headers are passed to YouTube."""
    disallowed_headers = {
        "host", "content-length", "accept-encoding", "content-encoding",
        "connection", "te", "keep-alive", "proxy-connection",
        "upgrade", "alt-used", "priority"
    }
    sanitized = {}
    for k, v in headers.items():
        k_clean = str(k).strip()
        k_lower = k_clean.lower()
        # Header names must be valid RFC tokens: no spaces, slashes, colons, question marks
        if not k_clean or any(c in k_clean for c in " \t/:?&=#;"):
            continue
        if k_lower.startswith(":") or k_lower in disallowed_headers:
            continue
        if k_lower.startswith("sec-"):
            continue
        sanitized[k_clean] = str(v).strip() if isinstance(v, str) else v
    return sanitized


def sanitize_oauth_file(path: Path) -> bool:
    """Read a stored headers json, remove corrupt/invalid keys, and rewrite if modified."""
    try:
        if not path.is_file():
            return False
        raw_text = path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
        if not isinstance(data, dict):
            return False
        cleaned = sanitize_headers_dict(data)
        if cleaned != data:
            path.write_text(json.dumps(cleaned, indent=4, ensure_ascii=True), encoding="utf-8")
            return True
    except Exception:
        pass
    return False


def is_authenticated() -> bool:
    return any(
        path.exists() and path.stat().st_size > 10
        for path in (_TOKEN_FILE, _GOOGLE_TOKEN_FILE)
    )


def get_ytmusic_client() -> YTMusic:
    if _GOOGLE_TOKEN_FILE.exists():
        credentials_data = _google_oauth_credentials()
        credentials = OAuthCredentials(
            client_id=credentials_data["client_id"],
            client_secret=credentials_data["client_secret"],
        )
        return YTMusic(str(_GOOGLE_TOKEN_FILE), oauth_credentials=credentials)

    if is_authenticated():
        try:
            sanitize_oauth_file(_TOKEN_FILE)
            return YTMusic(str(_TOKEN_FILE))
        except Exception:
            pass
    return YTMusic()


def setup_from_headers(headers_raw: str) -> str:
    _TOKEN_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(_TOKEN_DIR, 0o700)
    cleaned_lines = []
    for line in headers_raw.splitlines():
        trimmed = line.strip()
        if (trimmed.startswith(("GET ", "POST ", "PUT ", "DELETE ", "OPTIONS ", "HEAD ", "HTTP/"))
                or trimmed.startswith(":")
                or not trimmed):
            continue
        cleaned_lines.append(line)
    cleaned_raw = "\n".join(cleaned_lines)
    _ytm.setup(filepath=str(_TOKEN_FILE), headers_raw=cleaned_raw)
    sanitize_oauth_file(_TOKEN_FILE)
    os.chmod(_TOKEN_FILE, 0o600)
    _GOOGLE_TOKEN_FILE.unlink(missing_ok=True)
    _GOOGLE_CREDENTIALS_FILE.unlink(missing_ok=True)
    return str(_TOKEN_FILE)


def setup_google_oauth(
    on_device_code: Callable[[str], None],
    cancelled: Event,
) -> None:
    client_data = _google_oauth_credentials()
    credentials = OAuthCredentials(
        client_data["client_id"], client_data["client_secret"])
    code = credentials.get_code()
    verification_url = f"{code['verification_url']}?user_code={code['user_code']}"
    on_device_code(verification_url)
    webbrowser.open(verification_url)

    deadline = time.monotonic() + code["expires_in"]
    interval = code["interval"]
    while time.monotonic() < deadline:
        if cancelled.wait(interval):
            return

        response = credentials.token_from_code(code["device_code"])
        error = response.get("error")
        if not error:
            token = {
                "scope": response["scope"],
                "token_type": response["token_type"],
                "access_token": response["access_token"],
                "refresh_token": response["refresh_token"],
                "expires_at": int(time.time()) + response["expires_in"],
                "expires_in": response.get(
                    "refresh_token_expires_in", response["expires_in"]),
            }
            _TOKEN_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.chmod(_TOKEN_DIR, 0o700)
            _write_private_json(_GOOGLE_TOKEN_FILE, token)
            _write_private_json(_GOOGLE_CREDENTIALS_FILE, client_data)
            _TOKEN_FILE.unlink(missing_ok=True)
            return

        if error == "authorization_pending":
            continue
        if error == "slow_down":
            interval += 5
            continue
        if error == "access_denied":
            raise RuntimeError("Google sign-in was denied.")
        if error == "expired_token":
            raise RuntimeError("The Google sign-in code expired. Please try again.")
        raise RuntimeError(response.get("error_description", error))

    raise RuntimeError("The Google sign-in code expired. Please try again.")


def _write_private_json(path: Path, data: dict) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as token_file:
        os.fchmod(token_file.fileno(), 0o600)
        json.dump(data, token_file, indent=2)


def logout():
    _TOKEN_FILE.unlink(missing_ok=True)
    _GOOGLE_TOKEN_FILE.unlink(missing_ok=True)
    _GOOGLE_CREDENTIALS_FILE.unlink(missing_ok=True)
