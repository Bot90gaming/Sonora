<div align="center">

<img src="assets/preview.png" alt="Sonora" width="700"/>

# Sonora

**A native YouTube Music client for Linux, built with GTK 4 and libadwaita.**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![GTK](https://img.shields.io/badge/GTK-4.0-green.svg)]()

</div>

Sonora lets you search YouTube Music, browse your library, play and queue tracks,
and download audio from a Linux desktop app.

## Features

- Search songs, albums, artists, playlists, and videos
- Play tracks through GStreamer and yt-dlp, with automatic retries
- Start a station from the playing song, queue five similar tracks, and
  pre-download them in the background
- View and edit the playback queue by reordering or removing upcoming tracks
- Browse liked songs, playlists, and albums after signing in
- Like or unlike the current track
- Download audio as MP3, M4A, Opus, FLAC, or WAV
- Choose dark, light, or system colour scheme, with glass effects and accent colours

## Installation

Sonora requires Linux, Python 3.10 or later, GTK 4, libadwaita, GStreamer, and
FFmpeg for audio downloads.

### Install system dependencies

**Ubuntu / Debian**

```bash
sudo apt install python3 python3-pip python3-gi python3-gi-cairo \
  gir1.2-gtk-4.0 gir1.2-adw-1 \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-libav ffmpeg
```

**Fedora / RHEL**

```bash
sudo dnf install python3 python3-pip python3-gobject gtk4 libadwaita \
  gstreamer1-plugins-base gstreamer1-plugins-good \
  gstreamer1-plugins-bad-free gstreamer1-plugins-ugly \
  gstreamer1-libav ffmpeg
```

**Arch Linux**

```bash
sudo pacman -S python python-pip python-gobject gtk4 libadwaita \
  gst-plugins-base gst-plugins-good gst-plugins-bad gst-libav ffmpeg
```

### Install Sonora

```bash
git clone https://github.com/Bot90gaming/Sonora.git
cd Sonora
chmod +x install.sh
./install.sh
```

The installer places the app under `~/.local/share/sonora` and creates a
launcher named `sonora` in `~/.local/bin`. If that command is not found, add
`~/.local/bin` to your `PATH`, or launch Sonora from your desktop application
menu. It also installs the app icons into your local `hicolor` icon theme and
registers a desktop entry so the icon appears in application menus and docks.
If Sonora is already installed without its icon, run `./install.sh` again to
install the desktop entry and icons.

To uninstall, run `./uninstall.sh` from the cloned repository.

## Sign in with YouTube Music

**Google sign-in is unavailable in this build.** Use the **Request headers**
tab in Sonora's sign-in window. This uses your existing signed-in browser
session; Sonora does not ask for your Google password.

### Copy request headers from Chrome or Chromium

These steps apply to Google Chrome and Chromium-based browsers such as Brave,
Microsoft Edge, and Vivaldi. The menu wording can vary slightly by browser.

1. Open `https://music.youtube.com` in the browser where you are already signed
   in to the Google account whose music library you want to use. Complete any
   sign-in prompt before continuing.
2. Open Developer Tools:
   - **Windows / Linux:** press `F12` or `Ctrl+Shift+I`.
   - **macOS:** press `Cmd+Option+I`.
   - Alternatively, open the browser menu and choose **More tools → Developer
     tools**.
3. Select the **Network** tab in Developer Tools. If it is not visible, use the
   `»` overflow menu.
4. Keep Developer Tools open and reload YouTube Music (`Ctrl+R` on Windows or
   Linux, `Cmd+R` on macOS). The Network tab should begin listing requests.
5. In the Network filter box, enter `browse`. Select a request whose name or
   URL contains `browse` and whose domain is `music.youtube.com`. If there are
   no matching requests, clear the filter and reload the page again.
6. Copy the request headers using either method:
   - **Right-click the matching request** in the request list and choose
     **Copy → Copy Request Headers** (sometimes labelled **Copy request
     headers**).
   - Or select the request, find **Request Headers** in the **Headers** panel,
     and use the copy icon beside that section if your browser provides one.
7. In Sonora, open **Settings → Account → Sign in**, select **Request headers**,
   paste the copied text into the box, and click **Save headers**. Wait for the
   sign-in window to close, then open **Library**.

Use **Copy Request Headers**, not **Copy response headers**. If your browser
offers **Copy as fetch** instead, Sonora's sign-in dialog also accepts that
format.

### Header privacy and expiry

Request headers include private session data, especially the `cookie` header.
Treat the copied text like a password: paste it only into Sonora, and never
post it in an issue, chat, screenshot, or support request. Sonora saves the
headers locally in `~/.config/ytmusic_player/oauth.json` and restricts access
to that file on your device. Choose **Sign out** in Settings to remove the
saved credentials.

Browser session headers can expire. If your library stops loading or YouTube
Music rejects requests, sign in again and save a fresh set of request headers.

## Run from source

PyGObject (`gi`) and GTK are system dependencies, so a regular isolated virtual
environment may not be able to import them. Install the system dependencies
above first, then install the Python packages and launch the app:

```bash
git clone https://github.com/Bot90gaming/Sonora.git
cd Sonora
python3 -m pip install --user -r requirements.txt
python3 main.py
```

For detailed diagnostic logs:

```bash
python3 main.py --debug
```

If you use a virtual environment, make it inherit the system packages so it can
access PyGObject:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

## Troubleshooting

- **`gi` or GTK import error:** install the GTK, libadwaita, and PyGObject
  system packages for your Linux distribution.
- **Playback or download fails:** check your network connection and install
  GStreamer plugins and FFmpeg. For more detail, start with `--debug` and check
  the terminal output.
- **Library does not load:** confirm that you signed in with fresh YouTube
  Music request headers. If needed, sign out and repeat the header steps.
- **The `sonora` command is not found:** add `~/.local/bin` to your `PATH` or
  start Sonora from your application menu.

## Contributing

Bug reports and contributions are welcome. When reporting a bug, include your
Linux distribution, steps to reproduce it, and relevant terminal output. Do
not include request headers, cookies, or other account credentials.

1. Fork the repository and create a feature branch.
2. Make a focused change and test it.
3. Open a pull request against `main` with a description of the change.

## Project layout

```text
sonora/
├── main.py
├── auth/
│   └── auth_manager.py
├── core/
│   ├── api.py
│   ├── downloader.py
│   ├── player.py
│   └── settings.py
├── ui/
│   ├── choice_dropdown.py
│   ├── download_page.py
│   ├── easter_egg.py
│   ├── glass_theme.py
│   ├── library_page.py
│   ├── login_dialog.py
│   ├── main_window.py
│   ├── player_bar.py
│   ├── search_page.py
│   ├── settings_page.py
│   └── widgets.py
└── assets/
```

## License

Sonora is distributed under the MIT License. See [LICENSE](LICENSE).

<div align="center">
Made with ❤️ for the Linux desktop
</div>
