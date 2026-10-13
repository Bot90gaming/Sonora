"""
Quick setup script — installs dependencies and checks VLC.
Run: python setup.py
"""
import subprocess
import sys
import platform


def run(cmd):
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr.strip()}")
        return False
    return True


def main():
    print("=" * 50)
    print("  YTMusic Player — Setup")
    print("=" * 50)

    # 1. Cài đặt các gói phụ thuộc của Python
    print("\n[1/3] Installing Python dependencies…")
    ok = run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if not ok:
        print("      Try: pip install -r requirements.txt manually.")

    os_name = platform.system()

    # 2. Kiểm tra mô-đun đa phương tiện của PyQt6
    print("\n[2/3] Checking PyQt6 multimedia…")
    try:
        from PyQt6.QtMultimedia import QMediaPlayer
        print("      ✓ PyQt6.QtMultimedia found.")
    except ImportError:
        print("      ✗ PyQt6.QtMultimedia not found.")
        print("        Try: pip install PyQt6 PyQt6-Qt6")

    # 3. Kiểm tra ffmpeg (cần thiết để tải xuống)
    print("\n[3/3] Checking ffmpeg (needed for downloads)…")
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode == 0:
        print("      ✓ ffmpeg found.")
    else:
        print("      ✗ ffmpeg not found.")
        if os_name == "Windows":
            print("        Download from: https://ffmpeg.org/download.html")
        elif os_name == "Darwin":
            print("        Install with: brew install ffmpeg")
        else:
            print("        Install with: sudo apt install ffmpeg")

    print("\n" + "=" * 50)
    print("  Setup complete! Run the app with:")
    print("    python main.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
