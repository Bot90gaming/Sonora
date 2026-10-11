"""
Login dialog — browser-headers auth flow.
"""
from __future__ import annotations
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from auth.auth_manager import setup_from_headers


class LoginDialog(Adw.Window):
    """
    Modal window that walks the user through pasting browser headers.
    on_success() is called (on the main loop) after a valid save.
    """

    def __init__(self, parent: Gtk.Window, on_success: callable):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Sign in to YouTube Music")
        self.set_default_size(560, 520)
        self._on_success = on_success
        self._build()

    # ── Khởi tạo giao diện ───────────────────────────────────────────────────

    def _build(self):
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)

        # Hướng dẫn
        steps_lbl = Gtk.Label()
        steps_lbl.set_markup(
            "<b>How to get your browser headers:</b>\n"
            "1. Open <a href='https://music.youtube.com'>music.youtube.com</a> "
            "and sign in.\n"
            "2. Press <b>F12</b> → Network tab → reload the page.\n"
            "3. Click any <i>browse</i> or <i>next</i> request.\n"
            "4. Right-click the request → <i>Copy → Copy request headers</i>.\n"
            "5. Paste below and click <b>Save</b>."
        )
        steps_lbl.set_wrap(True)
        steps_lbl.set_xalign(0)
        steps_lbl.set_selectable(True)
        content.append(steps_lbl)

        # Vùng nhập văn bản
        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._text = Gtk.TextView()
        self._text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text.set_monospace(True)
        self._text.get_buffer().set_text("")
        sw.set_child(self._text)
        content.append(sw)

        # Nhãn trạng thái
        self._status = Gtk.Label(label="")
        self._status.set_xalign(0)
        self._status.add_css_class("caption")
        content.append(self._status)

        # Các nút
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_halign(Gtk.Align.END)

        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.add_css_class("flat")
        btn_cancel.connect("clicked", lambda *_: self.close())

        btn_save = Gtk.Button(label="Save")
        btn_save.add_css_class("suggested-action")
        btn_save.connect("clicked", self._on_save)

        btn_row.append(btn_cancel)
        btn_row.append(btn_save)
        content.append(btn_row)

        toolbar.set_content(content)
        self.set_content(toolbar)

    # ── Hàm xử lý sự kiện ────────────────────────────────────────────────────

    def _on_save(self, *_):
        buf = self._text.get_buffer()
        raw = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False).strip()
        if not raw:
            self._status.set_markup('<span foreground="red">Paste your headers first.</span>')
            return

        self._status.set_markup('<span foreground="gray">Saving…</span>')

        import threading
        def _do():
            try:
                setup_from_headers(raw)
                GLib.idle_add(self._done_ok)
            except Exception as exc:
                GLib.idle_add(self._done_err, str(exc))

        threading.Thread(target=_do, daemon=True).start()

    def _done_ok(self):
        self.close()
        self._on_success()

    def _done_err(self, msg: str):
        self._status.set_markup(f'<span foreground="red">Error: {GLib.markup_escape_text(msg)}</span>')
