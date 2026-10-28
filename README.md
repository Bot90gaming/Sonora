<div align="center">

# Sonora

**A native YouTube Music client for Linux, built with PySide6 and Qt Quick.**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![Qt](https://img.shields.io/badge/Qt-Quick-green.svg)]()

</div>

Sonora lets you search YouTube Music, browse your library, play and queue tracks,
and download audio from a Linux desktop app.

## Features

- Search songs, albums, and playlists
- Real-time synchronized lyrics with animated glowing highlight aura and continuous sub-pixel font swell (powered by LRCLIB and local cache)
- Play tracks through GStreamer and yt-dlp, with automatic retries
- Start a station from the playing song, queue five similar tracks, and
  pre-download them in the background
- View and edit the playback queue by reordering or removing upcoming tracks
- Browse liked songs, playlists, and albums after signing in
- Like or unlike the current track
- Download audio as MP3, M4A, Opus, FLAC, or WAV
- Choose a solid dark, light, or system colour scheme with Material-inspired
  surfaces and accent colours, in an animated Qt Quick interface

The UI is built with PySide6, QtPy, and QML. Qt Quick provides the animated
shell and component styling; it does not use browser Tailwind CSS.

## Installation

Sonora requires Linux, Python 3.10 or later, PySide6, QtPy, PyGObject,
GStreamer, and FFmpeg for audio playback and downloads.

### Install system dependencies

Select your Linux distribution below to install the necessary GStreamer plugins, Python GObject bindings, and FFmpeg:

**Ubuntu / Debian / Linux Mint / Pop!_OS**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-gi \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav ffmpeg
```

**Fedora / RHEL / AlmaLinux / Rocky Linux**

```bash
sudo dnf install python3 python3-pip python3-gobject \
  gstreamer1-plugins-base gstreamer1-plugins-good \
  gstreamer1-plugins-bad-free gstreamer1-plugins-ugly \
  gstreamer1-libav ffmpeg
```
*(Note: If you need MP3/AAC audio codec support on Fedora, ensure RPM Fusion is enabled for `gstreamer1-plugins-ugly` and `gstreamer1-libav`).*

**Arch Linux / Manjaro / EndeavourOS**

```bash
sudo pacman -Syu python python-pip python-gobject \
  gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly \
  gst-libav ffmpeg
```

**openSUSE (Tumbleweed / Leap)**

```bash
sudo zypper install python3 python3-pip python3-gobject \
  gstreamer-plugins-base gstreamer-plugins-good \
  gstreamer-plugins-bad gstreamer-plugins-ugly \
  gstreamer-plugins-libav ffmpeg
```

**Void Linux**

```bash
sudo xbps-install -S python3 python3-pip python3-gobject \
  gst-plugins-base1 gst-plugins-good1 gst-plugins-bad1 gst-plugins-ugly1 \
  gst-libav ffmpeg
```

**Gentoo Linux**

```bash
sudo emerge --ask dev-python/pygobject media-libs/gst-plugins-base \
  media-libs/gst-plugins-good media-libs/gst-plugins-bad \
  media-plugins/gst-plugins-ugly media-video/ffmpeg
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

PyGObject (`gi`) and GStreamer are system dependencies. Install the system
packages above first, then use a virtual environment that inherits those system
packages:

```bash
git clone https://github.com/Bot90gaming/Sonora.git
cd Sonora
python3 -m venv --system-site-packages venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

For detailed diagnostic logs:

```bash
python3 main.py --debug
```

## Troubleshooting

- **`gi` or GStreamer import error:** install the PyGObject and GStreamer
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
│   ├── qt_bridge.py
│   ├── components/
│   │   ├── EqualizerBars.qml
│   │   ├── FeaturedCarousel.qml
│   │   ├── FilterChip.qml
│   │   ├── FullPlayerWindow.qml
│   │   ├── LinearProgress.qml
│   │   ├── LoadingIndicator.qml
│   │   ├── MD3Icon.qml
│   │   ├── NavRail.qml
│   │   ├── PlaylistGrid.qml
│   │   ├── PlayerBar.qml
│   │   ├── ShellButton.qml
│   │   ├── Snackbar.qml
│   │   ├── StateLayer.qml
│   │   ├── ThemeScrollBar.qml
│   │   ├── ThemeSlider.qml
│   │   ├── ThemeToolButton.qml
│   │   ├── TrackList.qml
│   │   └── TrackThumbnail.qml
│   └── qml/
│       ├── Main.qml
│       ├── config/
│       │   └── ThemeConfig.qml
└── assets/
```

Reusable QML controls and layouts each have their own file in `ui/components/`;
shared color tokens for dark, light, and accent themes live in `ui/qml/config/`.
Motion uses shared Material 3 Expressive spatial and effects tokens, based on
the [official spring-to-curve conversions](https://m3.material.io/styles/motion/overview/specs).

## License

Sonora is distributed under the MIT License. See [LICENSE](LICENSE).

<div align="center">
Made with ❤️ for the Linux desktop
</div>
