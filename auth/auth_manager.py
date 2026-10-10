"""
No-auth client — connects to YouTube Music anonymously.
Search and streaming work; personal library features are unavailable.
"""
from ytmusicapi import YTMusic


def get_ytmusic_client() -> YTMusic:
    """Return an unauthenticated YTMusic client (public access only)."""
    return YTMusic()
