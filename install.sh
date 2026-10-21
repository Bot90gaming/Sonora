#!/usr/bin/env bash
set -e

APP_DIR="$HOME/.local/share/sonora"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"

echo "Installing Sonora..."

# 1. Python dependencies
pip install --quiet ytmusicapi yt-dlp requests --break-system-packages

# 2. Copy app files
mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"

# 3. Create launcher
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/sonora" <<LAUNCHER
#!/usr/bin/env bash
exec python3 "$APP_DIR/main.py" "\$@"
LAUNCHER
chmod +x "$BIN_DIR/sonora"

# 4. Install desktop entry
mkdir -p "$DESKTOP_DIR"
sed "s|Exec=.*|Exec=python3 $APP_DIR/main.py|" \
    io.github.sonora.desktop \
    > "$DESKTOP_DIR/io.github.sonora.desktop"

# 5. Install app icons in the standard per-user icon theme
for size in 48 128 256 512; do
    size_dir="$ICON_DIR/${size}x${size}/apps"
    mkdir -p "$size_dir"
    cp "assets/icons/sonora_${size}.png" \
        "$size_dir/io.github.sonora.png"
done

update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true

echo ""
echo "✓ Sonora installed!"
echo ""
echo "Launch with:  sonora"
echo "Or find 'Sonora' in your app launcher."
echo ""
echo "If 'sonora' command is not found, add this to your ~/.bashrc:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
