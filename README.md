# sonora
<div align="center">

# 🎵 YTMusic Player

**A sleek, cross-platform desktop music player powered by YouTube Music**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![ytmusicapi](https://img.shields.io/badge/ytmusicapi-1.6+-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-7c6af7?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=for-the-badge)

*Search, stream, and download music from YouTube Music — no account required.*

</div>

---

## ✨ Features

- 🔍 **Search** — Find songs, albums, artists, and playlists instantly
- ▶️ **Stream** — Play any track directly without downloading
- 📚 **Library** — Browse featured playlists and new releases
- ⬇️ **Download** — Save songs locally in MP3, FLAC, M4A, and more
- 🎚️ **Queue** — Build a playback queue on the fly
- 🎨 **Dark UI** — Clean, modern dark theme built with PyQt6
- ⚡ **No login needed** — Works anonymously out of the box

---



---

## 🛠️ Tech Stack

| Layer | Library |
|---|---|
| GUI | [PyQt6](https://pypi.org/project/PyQt6/) |
| Audio playback | [PyQt6-Qt6 Multimedia](https://doc.qt.io/qt-6/qtmultimedia-index.html) |
| YouTube Music API | [ytmusicapi](https://ytmusicapi.readthedocs.io/) |
| Audio streaming | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Thumbnails | [Pillow](https://pillow.readthedocs.io/) + [requests](https://requests.readthedocs.io/) |

---

## 🚀 Installation

### Prerequisites

Make sure you have **Python 3.10+** and **ffmpeg** installed.

<details>
<summary>📦 Install ffmpeg</summary>

**Linux (Debian/Ubuntu):**
```bash
sudo apt install ffmpeg
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

</details>

### Install the app

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ytmusic-player.git
cd ytmusic-player

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py
```

The app launches directly into the player — no login or setup required.

### 🔍 Search
Type any song, artist, or album in the Search tab and press **Enter** or click **Search**. Double-click a result to play it, or right-click for more options.

### 📚 Library
Browse **Featured Playlists** and **New Releases** in the Library tab. Click a playlist to load its tracks.

### ⬇️ Downloads
Right-click any song → **Download**, or switch to the Downloads tab. Choose your output folder and audio format (MP3, FLAC, M4A, Opus, WAV).

### ⌨️ Player controls

| Action | How |
|---|---|
| Play / Pause | Click ▶ / ⏸ button |
| Next / Previous | Click ⏭ / ⏮ button |
| Seek | Drag the progress bar |
| Volume | Drag the volume slider |
| Add to queue | Right-click → *Add to queue* |

---

## 📁 Project Structure

```
ytmusic_player/
├── main.py              # Entry point
├── requirements.txt
├── auth/
│   └── auth_manager.py  # YTMusic client (anonymous)
├── core/
│   ├── api.py           # ytmusicapi wrapper
│   ├── player.py        # QMediaPlayer audio backend
│   └── downloader.py    # yt-dlp multi-threaded downloader
└── ui/
    ├── main_window.py   # App shell & queue management
    ├── player_bar.py    # Bottom playback bar
    ├── search_tab.py    # Search UI
    ├── library_tab.py   # Library UI
    └── download_tab.py  # Downloads UI
```

---

## 🐛 Troubleshooting

**`No module named 'PyQt6.QtMultimedia'`**
```bash
pip install PyQt6 PyQt6-Qt6
```

**No audio plays / silent playback**
Make sure `ffmpeg` is installed and available in your PATH (see Prerequisites above).

**Slow search results**
This is normal — yt-dlp fetches stream URLs in real time. The status bar will show *"Loading…"* while it resolves.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your branch (`git checkout -b feature/cool-thing`)
3. Commit your changes (`git commit -m 'Add cool thing'`)
4. Push to the branch (`git push origin feature/cool-thing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Built with 💜 using Python & PyQt6</sub>
</div>
