"""
YTMusic Player — GTK4 + libadwaita entry point (Linux).
"""
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Adw, Gst, GLib

# Khởi tạo GStreamer trước mọi thành phần khác.
Gst.init(None)


def main():
    app = Adw.Application(application_id="io.github.ytmusic_player")

    # Buộc dùng giao diện tối để phù hợp với tông màu tím.
    app.connect("activate", _on_activate)

    sys.exit(app.run(sys.argv))


def _on_activate(app: Adw.Application):
    # Dùng thiết lập của hệ thống; gọi set_color_scheme để buộc dùng giao diện tối nếu cần.
    Adw.StyleManager.get_default().set_color_scheme(
        Adw.ColorScheme.PREFER_DARK
    )
    from ui.main_window import MainWindow
    win = MainWindow(application=app)
    win.present()


if __name__ == "__main__":
    main()
