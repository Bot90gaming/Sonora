# Sonora — YouTube Music for Linux

A native GTK4 + libadwaita YouTube Music desktop player for Linux.

![Sonora](assets/preview.png)

## Features

- 🔍 Search songs, albums, artists, playlists and videos
- 🎵 Stream audio via GStreamer + yt-dlp
- 📚 Browse your library — liked songs, playlists, albums
- ❤️ Like songs directly from the player bar
- ⬇️ Download tracks in mp3, m4a, opus, flac or wav
- 🎨 Glassmorphism UI with accent colour themes
- 🌙 Dark / Light / System colour scheme

## Requirements

- Python 3.10+
- GTK 4 + libadwaita (pre-installed on GNOME / Fedora)
- GStreamer plugins

**Fedora:**
```bash
sudo dnf install gstreamer1-plugins-base gstreamer1-plugins-good \
                 gstreamer1-plugins-bad-free gstreamer1-plugins-ugly \
                 python3-gobject
```

**Ubuntu / Debian:**
```bash
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                 gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
                 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

## Install

```bash
git clone https://github.com/Bot90gaming/sonora.git
cd sonora
chmod +x install.sh
./install.sh
```

## Uninstall

```bash
cd sonora
./uninstall.sh
```

## Sign in

Sonora uses your YouTube Music browser session headers to authenticate.

1. Open **music.youtube.com** in Chrome/Firefox and sign in
2. Open DevTools → Network tab → refresh the page
3. Find any request to `music.youtube.com`, right-click → **Copy as cURL**
4. Open Sonora → Settings → Sign in, paste the headers and save
5. If you find it too difficult check out my video tutorial at :
## License

MIT
