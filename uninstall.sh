#!/usr/bin/env bash
APP_DIR="$HOME/.local/share/sonora"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

rm -rf "$APP_DIR"
rm -f  "$BIN_DIR/sonora"
rm -f  "$DESKTOP_DIR/io.github.sonora.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "Sonora uninstalled."
