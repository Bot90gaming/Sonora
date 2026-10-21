#!/usr/bin/env bash
APP_DIR="$HOME/.local/share/sonora"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"

rm -rf "$APP_DIR"
rm -f  "$BIN_DIR/sonora"
rm -f  "$DESKTOP_DIR/io.github.sonora.desktop"
for size in 48 128 256 512; do
    rm -f "$ICON_DIR/${size}x${size}/apps/io.github.sonora.png"
done
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true

echo "Sonora uninstalled."
