"""
Settings page — polished Adw.PreferencesPage.
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from core import settings as cfg
from auth.auth_manager import logout
from ui.choice_dropdown import ChoiceDropDown

_THEMES      = ["Dark", "Light", "System"]
_THEME_KEYS  = ["dark", "light", "system"]
_ACCENT_KEYS = ["violet", "blue", "green", "rose", "orange"]
_ACCENT_HEX  = {
    "violet": "#a78bfa", "blue": "#60a5fa", "green": "#34d399",
    "rose":   "#fb7185", "orange": "#fb923c",
}
_FORMATS     = ["mp3", "m4a", "opus", "flac", "wav"]
_QUALITY     = ["Best — highest bitrate", "Medium — ~128 kbps", "Low — ~64 kbps"]
_QUALITY_KEYS = ["best", "medium", "low"]


class SettingsPage(Adw.PreferencesPage):
    def __init__(self,
                 on_theme_change: callable | None = None,
                 on_logout:       callable | None = None,
                 on_login:        callable | None = None):
        super().__init__()
        self.set_title("Settings")
        self.set_icon_name("preferences-system-symbolic")
        self._on_theme_change = on_theme_change
        self._on_logout       = on_logout
        self._on_login        = on_login
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self._settings_group = Adw.PreferencesGroup()
        self.add(self._settings_group)
        self._build_appearance()
        self._build_account()
        self._build_playback()
        self._build_downloads()
        self._build_about()

    # ── Appearance ────────────────────────────────────────────────────────────

    def _build_appearance(self):
        group = self._settings_group

        # Theme
        theme_row = self._choice_row(
            "Colour scheme",
            "Choose between dark, light or follow the system",
            "weather-clear-night-symbolic",
            _THEMES,
            _idx(_THEME_KEYS, cfg.get("theme"), 0),
            self._on_theme_selected,
            width=118,
        )
        group.add(theme_row)

        # Glass
        glass_row = Adw.SwitchRow()
        glass_row.set_title("Glass surfaces")
        glass_row.set_subtitle(
            "Translucent frosted panels — looks best with a blur compositor")
        glass_row.set_icon_name("window-maximize-symbolic")
        glass_row.set_active(cfg.get("glass_effect"))
        glass_row.connect("notify::active", self._on_glass_row)
        group.add(glass_row)

        # Accent colour — row with colour swatches
        accent_row = Adw.ActionRow()
        accent_row.set_title("Accent colour")
        accent_row.set_subtitle("Highlights, buttons and selection indicators")
        accent_row.set_icon_name("applications-graphics-symbolic")

        swatch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        swatch_box.set_valign(Gtk.Align.CENTER)
        swatch_box.set_margin_end(4)

        self._swatch_btns: dict[str, Gtk.ToggleButton] = {}
        saved_accent = cfg.get("accent")

        for key in _ACCENT_KEYS:
            tb = Gtk.ToggleButton()
            tb.set_size_request(26, 26)
            tb.set_tooltip_text(key.capitalize())
            tb.add_css_class("circular")
            # Inline CSS for the swatch colour
            _apply_swatch_css(tb, _ACCENT_HEX[key])
            tb.set_active(key == saved_accent)
            tb.connect("toggled", self._on_swatch_toggled, key)
            self._swatch_btns[key] = tb
            swatch_box.append(tb)

        accent_row.add_suffix(swatch_box)
        group.add(accent_row)

    # ── Account ───────────────────────────────────────────────────────────────

    def _build_account(self):
        group = self._settings_group

        # Sign in row
        signin_row = Adw.ActionRow()
        signin_row.set_title("Sign in")
        signin_row.set_subtitle("Paste browser headers from music.youtube.com")
        signin_row.set_icon_name("dialog-password-symbolic")
        signin_row.set_activatable(True)
        signin_row.add_suffix(
            Gtk.Image.new_from_icon_name("go-next-symbolic"))
        signin_row.connect("activated",
                           lambda *_: self._on_login and self._on_login())
        group.add(signin_row)

        # Sign out row
        signout_row = Adw.ActionRow()
        signout_row.set_title("Sign out")
        signout_row.set_subtitle("Remove saved credentials from this device")
        signout_row.set_icon_name("system-log-out-symbolic")

        signout_btn = Gtk.Button(label="Sign out")
        signout_btn.add_css_class("destructive-action")
        signout_btn.add_css_class("pill")
        signout_btn.set_valign(Gtk.Align.CENTER)
        signout_btn.connect("clicked", self._do_signout)
        signout_row.add_suffix(signout_btn)
        group.add(signout_row)

    def _do_signout(self, *_):
        logout()
        if self._on_logout:
            self._on_logout()

    # ── Playback ──────────────────────────────────────────────────────────────

    def _build_playback(self):
        group = self._settings_group

        q_row = self._choice_row(
            "Stream quality",
            "Higher quality uses more bandwidth",
            "audio-headphones-symbolic",
            _QUALITY,
            _idx(_QUALITY_KEYS, cfg.get("audio_quality"), 0),
            lambda index: cfg.set("audio_quality", _QUALITY_KEYS[index]),
            width=260,
        )
        group.add(q_row)

        autonext_row = Adw.SwitchRow()
        autonext_row.set_title("Auto-play next track")
        autonext_row.set_subtitle("Continue playing the queue when a song ends")
        autonext_row.set_icon_name("media-skip-forward-symbolic")
        autonext_row.set_active(cfg.get("autonext"))
        autonext_row.connect("notify::active",
                             lambda r, *_: cfg.set("autonext", r.get_active()))
        group.add(autonext_row)

    # ── Downloads ─────────────────────────────────────────────────────────────

    def _build_downloads(self):
        group = self._settings_group

        saved_dir = cfg.get("download_dir") or str(
            Path(os.environ.get("XDG_MUSIC_DIR") or Path.home() / "Music"))

        folder_row = Adw.ActionRow()
        folder_row.set_title("Save folder")
        folder_row.set_subtitle(_short_path(saved_dir))
        folder_row.set_icon_name("folder-symbolic")
        self._folder_row = folder_row

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        btn_box.set_valign(Gtk.Align.CENTER)

        open_btn = Gtk.Button()
        open_btn.set_icon_name("folder-open-symbolic")
        open_btn.add_css_class("flat")
        open_btn.add_css_class("circular")
        open_btn.set_valign(Gtk.Align.CENTER)
        open_btn.set_tooltip_text("Open in Files")
        open_btn.connect("clicked",
                         lambda *_: subprocess.Popen(
                             ["xdg-open", cfg.get("download_dir") or saved_dir]))
        btn_box.append(open_btn)

        pick_btn = Gtk.Button(label="Change…")
        pick_btn.add_css_class("pill")
        pick_btn.set_valign(Gtk.Align.CENTER)
        pick_btn.connect("clicked", self._pick_folder)
        btn_box.append(pick_btn)

        folder_row.add_suffix(btn_box)
        group.add(folder_row)

        fmt_row = self._choice_row(
            "Audio format",
            "Format used when converting downloaded audio",
            "audio-x-generic-symbolic",
            _FORMATS,
            _idx(_FORMATS, cfg.get("download_format"), 0),
            lambda index: cfg.set("download_format", _FORMATS[index]),
            width=96,
        )
        group.add(fmt_row)

    def _choice_row(self, title, subtitle, icon, choices, selected,
                    on_changed, width=-1):
        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)
        row.set_icon_name(icon)
        row.add_suffix(ChoiceDropDown(
            choices, selected=selected, on_changed=on_changed, width=width))
        return row

    def _pick_folder(self, *_):
        d = Gtk.FileDialog()
        d.set_title("Choose download folder")
        d.select_folder(self.get_root(), None, self._folder_chosen, None)

    def _folder_chosen(self, dialog, result, _):
        try:
            f = dialog.select_folder_finish(result)
            path = f.get_path()
            cfg.set("download_dir", path)
            self._folder_row.set_subtitle(_short_path(path))
        except Exception:
            pass

    # ── About ─────────────────────────────────────────────────────────────────

    def _build_about(self):
        group = self._settings_group

        name_row = Adw.ActionRow()
        name_row.set_title("Sonora")
        name_row.set_subtitle("YouTube Music desktop player for Linux")
        icon = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
        icon.set_pixel_size(36)
        icon.set_valign(Gtk.Align.CENTER)
        name_row.add_prefix(icon)
        group.add(name_row)

        for title, value in [
            ("Version",   "1.0.0"),
            ("Toolkit",   "GTK 4 + libadwaita"),
            ("Streaming", "GStreamer · yt-dlp"),
            ("Auth",      "ytmusicapi (browser headers)"),
        ]:
            row = Adw.ActionRow()
            row.set_title(title)
            lbl = Gtk.Label(label=value)
            lbl.add_css_class("dim-label")
            lbl.add_css_class("caption")
            lbl.set_valign(Gtk.Align.CENTER)
            row.add_suffix(lbl)
            group.add(row)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_theme_selected(self, index: int):
        cfg.set("theme", _THEME_KEYS[index])
        if self._on_theme_change:
            self._on_theme_change()

    def _on_glass_row(self, row, _):
        cfg.set("glass_effect", row.get_active())
        if self._on_theme_change:
            self._on_theme_change()

    def _on_swatch_toggled(self, btn: Gtk.ToggleButton, key: str):
        if not btn.get_active():
            return
        # Untoggle all others
        for k, b in self._swatch_btns.items():
            if k != key:
                b.handler_block_by_func(self._on_swatch_toggled)
                b.set_active(False)
                b.handler_unblock_by_func(self._on_swatch_toggled)
        cfg.set("accent", key)
        if self._on_theme_change:
            self._on_theme_change()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _apply_swatch_css(widget: Gtk.Widget, hex_colour: str):
    provider = Gtk.CssProvider()
    provider.load_from_string(f"""
        button {{
            background-color: {hex_colour};
            min-width:  26px;
            min-height: 26px;
            padding: 0;
            border: 2px solid transparent;
        }}
        button:checked {{
            border-color: white;
            box-shadow: 0 0 0 1px {hex_colour};
        }}
    """)
    widget.get_style_context().add_provider(
        provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def _idx(lst: list, val, fallback: int) -> int:
    try:
        return lst.index(val)
    except ValueError:
        return fallback


def _short_path(p: str) -> str:
    home = str(Path.home())
    return p.replace(home, "~") if p.startswith(home) else p
