<div align="center">

<img src="assets/preview.png" alt="Sonora" width="700"/>

# Sonora

**A native YouTube Music client for Linux — built with GTK 4 and libadwaita**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![GTK](https://img.shields.io/badge/GTK-4.0-green.svg)]()

</div>

---

## ✨ Features

| | |
|---|---|
| 🔍 **Search** | Songs, albums, artists, playlists and videos |
| 🎵 **Stream** | High-quality audio via GStreamer + yt-dlp with auto-retry |
| 📚 **Library** | Browse liked songs, playlists and albums |
| ❤️ **Like** | Heart songs directly from the player bar |
| ⬇️ **Download** | Save tracks as mp3, m4a, opus, flac or wav |
| 🎨 **Themes** | Glassmorphism UI with 5 accent colours |
| 🌙 **Colour schemes** | Dark, Light or follow the system |
| 🐣 **Easter egg** | Try searching for something… |

---

## 📦 Installation

### Dependencies

**Fedora / RHEL:**
```bash
sudo dnf install gstreamer1-plugins-base gstreamer1-plugins-good \
                 gstreamer1-plugins-bad-free gstreamer1-plugins-ugly \
                 python3-gobject python3-pip
```

**Ubuntu / Debian:**
```bash
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                 gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
                 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 \
                 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4 libadwaita gst-plugins-base \
               gst-plugins-good gst-plugins-bad gst-plugins-ugly python-pip
```

### Install Sonora

```bash
git clone https://github.com/Bot90gaming/sonora.git
cd sonora
chmod +x install.sh
./install.sh
```

After installing, launch from your app menu or run:
```bash
sonora
```

### Uninstall

```bash
cd sonora
./uninstall.sh
```

---

## 🔐 Signing In

Sonora authenticates using your YouTube Music browser session headers — no OAuth app registration needed.

1. Open **[music.youtube.com](https://music.youtube.com)** in Chrome or Firefox and sign in
2. Open DevTools (`F12`) → **Network** tab → refresh the page
3. Find any request to `music.youtube.com`, right-click it → **Copy → Copy as cURL**
4. In Sonora, go to **Settings → Account → Sign in**
5. Paste the copied headers and click **Save**

> **Note:** Headers expire after some time. If the library stops loading, sign out and sign in again.

---

## 🖥️ Screenshots

> _Add screenshots here once the app is running_

---

## 🛠️ Running from Source

```bash
git clone https://github.com/Bot90gaming/sonora.git
cd sonora
pip install --user -r requirements.txt
python3 main.py
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Reporting bugs

Open an [issue](https://github.com/YOUR_USERNAME/sonora/issues) and include:
- Your distro and version
- Steps to reproduce
- Any error output from the terminal (`sonora` prints errors there)

### Suggesting features

Open an issue with the `enhancement` label. Describe what you want and why it would be useful.

### Submitting code

1. **Fork** the repository
2. **Create a branch** for your change:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Make your changes** — keep commits focused and descriptive
4. **Test** that the app still runs and nothing is broken
5. **Open a pull request** against `main` with a clear description of what changed and why

### Project structure

```
sonora/
├── main.py               # Entry point
├── core/
│   ├── api.py            # ytmusicapi wrapper
│   ├── player.py         # GStreamer playback
│   ├── downloader.py     # yt-dlp download manager
│   └── settings.py       # JSON settings persistence
├── auth/
│   └── auth_manager.py   # Browser-headers authentication
├── ui/
│   ├── main_window.py    # Root window and queue logic
│   ├── player_bar.py     # Bottom transport bar
│   ├── search_page.py    # Search view
│   ├── library_page.py   # Library sidebar + track panel
│   ├── download_page.py  # Download manager view
│   ├── settings_page.py  # Preferences
│   ├── login_dialog.py   # Sign-in modal
│   ├── glass_theme.py    # Glassmorphism CSS engine
│   ├── easter_egg.py     # 🐣
│   └── widgets.py        # Shared helpers
└── assets/
```

### Code style

- Python 3.10+, standard library imports first then third-party
- GTK4 patterns: `GLib.idle_add` for UI updates from threads, `Gtk.GestureDrag` for drag events
- Keep UI construction in `_build()` methods, callbacks in separate methods

---

## 📄 License

MIT © 2024 YOUR_NAME

---

<div align="center">
Made with ❤️ for the Linux desktop
</div>
