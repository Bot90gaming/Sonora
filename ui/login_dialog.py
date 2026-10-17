"""
Login dialog — Google OAuth and browser-headers authentication.
"""
from __future__ import annotations
import logging
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from auth.auth_manager import (
    is_google_oauth_configured,
    setup_from_headers,
    setup_google_oauth,
)

logger = logging.getLogger(__name__)


class LoginDialog(Adw.Window):
    """
    Modal window for Google OAuth or browser-header sign-in.
    on_success() is called (on the main loop) after a valid save.
    """

    def __init__(self, parent: Gtk.Window, on_success: callable):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Sign in to YouTube Music")
        self.set_default_size(580, 580)
        self.add_css_class("login-dialog")
        self._on_success = on_success
        self._oauth_cancel = threading.Event()
        self._build()
        self.connect("close-request", self._on_close_request)

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(24)
        content.set_margin_end(24)

        # Intro label
        intro = Gtk.Label()
        intro.set_markup(
            "<b>Choose a sign-in method.</b>\n"
            "<span size='small'>Google OAuth is recommended; request headers remain available "
            "as a manual option.</span>"
        )
        intro.set_wrap(True)
        intro.set_xalign(0)
        content.append(intro)

        # Authentication methods
        notebook = Gtk.Notebook()
        notebook.set_show_border(False)
        notebook.set_vexpand(True)

        # ── Google OAuth tab ─────────────────────────────────────────────────
        oauth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        oauth_box.set_margin_top(12)
        oauth_box.set_margin_bottom(8)
        oauth_box.set_margin_start(4)
        oauth_box.set_margin_end(4)

        oauth_instructions = Gtk.Label()
        oauth_instructions.set_markup(
            "<b>Sign in with Google</b>\n"
            "Continue in your browser to authorize Sonora. Your Google password is "
            "never shared with this app."
        )
        oauth_instructions.set_wrap(True)
        oauth_instructions.set_xalign(0)
        oauth_box.append(oauth_instructions)

        self._google_btn = Gtk.Button(label="Continue with Google")
        self._google_btn.add_css_class("suggested-action")
        self._google_btn.set_halign(Gtk.Align.START)
        self._google_btn.connect("clicked", self._on_google_login)
        oauth_configured = is_google_oauth_configured()
        self._google_btn.set_sensitive(oauth_configured)
        oauth_box.append(self._google_btn)

        if not oauth_configured:
            oauth_box.append(Gtk.Label(
                label="Google sign-in is not enabled by this installation. "
                      "Use Request headers instead.",
                xalign=0,
                wrap=True,
            ))

        self._device_link = Gtk.LinkButton.new_with_label(
            "https://www.google.com/device",
            "Open Google sign-in if the browser did not open",
        )
        self._device_link.set_halign(Gtk.Align.START)
        self._device_link.set_visible(False)
        oauth_box.append(self._device_link)

        self._oauth_status = Gtk.Label(label="")
        self._oauth_status.set_xalign(0)
        self._oauth_status.add_css_class("caption")
        self._oauth_status.set_wrap(True)
        oauth_box.append(self._oauth_status)
        notebook.append_page(oauth_box, Gtk.Label(label="Google sign-in"))

        # ── Firefox tab ──────────────────────────────────────────────────────
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(4)
        header_box.set_margin_start(4)
        header_box.set_margin_end(4)
        browser_tabs = Gtk.Notebook()
        browser_tabs.set_show_border(False)

        ff_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ff_box.set_margin_top(12)
        ff_box.set_margin_bottom(4)
        ff_lbl = Gtk.Label()
        ff_lbl.set_markup(
            "1. Open <a href='https://music.youtube.com'>music.youtube.com</a> and sign in.\n"
            "2. Press <b>F12</b> → <b>Network</b> tab → reload the page (<b>F5</b>).\n"
            "3. Type <tt>browse</tt> in the filter box and click any result.\n"
            "4. Right-click the request → <b>Copy → Copy Request Headers</b>.\n"
            "5. Paste below and click <b>Save</b>."
        )
        ff_lbl.set_wrap(True)
        ff_lbl.set_xalign(0)
        ff_box.append(ff_lbl)
        browser_tabs.append_page(ff_box, Gtk.Label(label="Firefox"))

        # ── Chrome / Chromium tab ────────────────────────────────────────────
        cr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        cr_box.set_margin_top(12)
        cr_box.set_margin_bottom(4)
        cr_lbl = Gtk.Label()
        cr_lbl.set_markup(
            "1. Open <a href='https://music.youtube.com'>music.youtube.com</a> and sign in.\n"
            "2. Press <b>F12</b> → <b>Network</b> tab → reload the page (<b>F5</b>).\n"
            "3. Type <tt>browse</tt> in the filter box and click any result.\n"
            "4. In the right panel scroll to <b>Request Headers</b>.\n"
            "5. Click the <b>copy icon</b> at the top-right of that section.\n"
            "   <i>Or right-click the request → Copy → Copy request headers.</i>\n"
            "6. Paste below and click <b>Save</b>.\n\n"
            "<span size='small'>Tip: if you see <b>Copy as fetch</b> only, "
            "paste that — it works too.</span>"
        )
        cr_lbl.set_wrap(True)
        cr_lbl.set_xalign(0)
        cr_box.append(cr_lbl)
        browser_tabs.append_page(cr_box, Gtk.Label(label="Chrome / Chromium"))

        header_box.append(browser_tabs)

        # Paste area label
        paste_lbl = Gtk.Label(label="Paste your request headers here:")
        paste_lbl.set_xalign(0)
        paste_lbl.add_css_class("caption")
        header_box.append(paste_lbl)

        # Text area
        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.set_min_content_height(120)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add_css_class("card")

        self._text = Gtk.TextView()
        self._text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text.set_monospace(True)
        self._text.set_margin_top(8)
        self._text.set_margin_bottom(8)
        self._text.set_margin_start(8)
        self._text.set_margin_end(8)
        self._text.get_buffer().set_text("")
        sw.set_child(self._text)
        header_box.append(sw)

        # Privacy notice
        privacy = Gtk.Label()
        privacy.set_markup(
            "<span size='small'>🔒 Headers are saved only to "
            "<tt>~/.config/ytmusic_player/oauth.json</tt> on your device.</span>"
        )
        privacy.set_wrap(True)
        privacy.set_xalign(0)
        header_box.append(privacy)

        self._status = Gtk.Label(label="")
        self._status.set_xalign(0)
        self._status.add_css_class("caption")
        header_box.append(self._status)

        save_headers = Gtk.Button(label="Save headers")
        save_headers.add_css_class("suggested-action")
        save_headers.set_halign(Gtk.Align.END)
        save_headers.connect("clicked", self._on_save)
        header_box.append(save_headers)

        notebook.append_page(header_box, Gtk.Label(label="Request headers"))
        content.append(notebook)

        # Buttons
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_halign(Gtk.Align.END)

        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.add_css_class("flat")
        btn_cancel.connect("clicked", lambda *_: self.close())

        btn_row.append(btn_cancel)
        content.append(btn_row)

        toolbar.set_content(content)
        self.set_content(toolbar)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_google_login(self, *_):
        self._oauth_cancel.clear()
        self._google_btn.set_sensitive(False)
        self._device_link.set_visible(False)
        self._oauth_status.set_text("Connecting to Google…")
        threading.Thread(
            target=self._run_google_login,
            daemon=True,
        ).start()

    def _run_google_login(self):
        try:
            setup_google_oauth(
                self._on_device_code,
                self._oauth_cancel,
            )
        except Exception as exc:
            logger.exception("Google OAuth sign-in failed")
            if not self._oauth_cancel.is_set():
                GLib.idle_add(self._show_google_error, str(exc))
        else:
            if not self._oauth_cancel.is_set():
                logger.info("Google OAuth sign-in completed")
                GLib.idle_add(self._done_ok)

    def _on_device_code(self, url: str):
        GLib.idle_add(self._show_device_link, url)

    def _show_device_link(self, url: str):
        self._device_link.set_uri(url)
        self._device_link.set_visible(True)
        self._oauth_status.set_text(
            "Complete Google sign-in in your browser. Waiting for approval…")

    def _show_google_error(self, message: str):
        self._google_btn.set_sensitive(True)
        self._oauth_status.set_markup(
            f'<span foreground="red">{GLib.markup_escape_text(message)}</span>')

    def _on_close_request(self, *_):
        self._oauth_cancel.set()
        return False

    def _on_save(self, *_):
        buf = self._text.get_buffer()
        raw = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False).strip()
        if not raw:
            self._status.set_markup('<span foreground="red">Paste your headers first.</span>')
            return

        self._status.set_text("Saving…")

        def _do():
            try:
                setup_from_headers(raw)
                logger.info("YouTube Music session headers saved")
                GLib.idle_add(self._done_ok)
            except Exception as exc:
                logger.exception("Could not save YouTube Music session headers")
                GLib.idle_add(self._done_err, str(exc))

        threading.Thread(target=_do, daemon=True).start()

    def _done_ok(self):
        self.close()
        self._on_success()

    def _done_err(self, msg: str):
        self._status.set_markup(
            f'<span foreground="red">Error: {GLib.markup_escape_text(msg)}</span>\n'
            '<span size="small">Make sure you pasted the full headers block '
            '(including lines like "accept:" and "cookie:").</span>'
        )
