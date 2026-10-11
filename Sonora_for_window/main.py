"""
Entry point for YTMusic Player. 
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sonora")
    app.setOrganizationName("Sonora")
    app.setWindowIcon(QIcon("images/app.png"))

    # Phông chữ cơ bản
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
