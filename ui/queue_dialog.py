from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class QueueDialog(Adw.Window):
    def __init__(self, parent, queue, current_index, on_move, on_remove,
                 on_clear):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Playback queue")
        self.set_default_size(440, 520)
        self._queue = queue
        self._current_index = current_index
        self._on_move = on_move
        self._on_remove = on_remove
        self._on_clear = on_clear

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        content.set_margin_start(18)
        content.set_margin_end(18)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        title = Gtk.Label(label="Playback queue")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)
        header.append(title)

        self._clear_button = Gtk.Button(label="Clear upcoming")
        self._clear_button.add_css_class("flat")
        self._clear_button.connect("clicked", self._clear_upcoming)
        header.append(self._clear_button)
        content.append(header)

        self._list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._empty_label = Gtk.Label(label="Nothing is queued")
        self._empty_label.add_css_class("dim-label")
        self._empty_label.set_margin_top(24)
        self._empty_label.set_margin_bottom(24)
        content.append(self._empty_label)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        scroller.set_child(self._list)
        content.append(scroller)
        self.set_content(content)
        self.refresh(queue, current_index)

    def refresh(self, queue, current_index):
        self._queue = queue
        self._current_index = current_index
        child = self._list.get_first_child()
        while child:
            following = child.get_next_sibling()
            self._list.remove(child)
            child = following

        self._empty_label.set_visible(not queue)
        self._clear_button.set_sensitive(current_index + 1 < len(queue))
        for index, song in enumerate(queue):
            self._list.append(self._make_row(index, song))

    def _make_row(self, index, song):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add_css_class("queue-row")

        number = Gtk.Label(label=str(index + 1))
        number.add_css_class("dim-label")
        number.set_width_chars(2)
        row.append(number)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)
        title = Gtk.Label(label=song.get("title") or "Unknown title")
        title.set_halign(Gtk.Align.START)
        title.set_ellipsize(3)
        artist = Gtk.Label(label=song.get("artist") or "")
        artist.set_halign(Gtk.Align.START)
        artist.set_ellipsize(3)
        artist.add_css_class("caption")
        artist.add_css_class("dim-label")
        info.append(title)
        info.append(artist)
        row.append(info)

        if index == self._current_index:
            status = Gtk.Label(label="Playing")
            status.add_css_class("accent")
            row.append(status)
        elif index > self._current_index:
            for icon, tooltip, offset in (
                ("go-up-symbolic", "Move up", -1),
                ("go-down-symbolic", "Move down", 1),
            ):
                button = Gtk.Button()
                button.set_icon_name(icon)
                button.set_tooltip_text(tooltip)
                button.add_css_class("flat")
                button.connect("clicked", self._move, index, offset)
                button.set_sensitive(
                    self._current_index < index + offset < len(self._queue))
                row.append(button)

            remove = Gtk.Button()
            remove.set_icon_name("user-trash-symbolic")
            remove.set_tooltip_text("Remove from queue")
            remove.add_css_class("flat")
            remove.connect("clicked", self._remove, index)
            row.append(remove)
        else:
            status = Gtk.Label(label="Played")
            status.add_css_class("caption")
            status.add_css_class("dim-label")
            row.append(status)
        return row

    def _move(self, _button, index, offset):
        self._on_move(index, offset)

    def _remove(self, _button, index):
        self._on_remove(index)

    def _clear_upcoming(self, *_):
        self._on_clear()
