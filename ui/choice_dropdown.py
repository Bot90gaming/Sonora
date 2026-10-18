"""Theme-aware dropdown built from a menu button and a rounded popover."""
from __future__ import annotations

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class ChoiceDropDown(Gtk.MenuButton):
    def __init__(
        self,
        choices: list[str],
        selected: int = 0,
        on_changed=None,
        width: int = -1,
    ):
        super().__init__()
        if not choices:
            raise ValueError("ChoiceDropDown requires at least one choice")
        if not 0 <= selected < len(choices):
            raise ValueError("Selected choice index is out of range")

        self._choices = choices
        self._selected = selected
        self._on_changed = on_changed

        self.add_css_class("choice-control")
        self.set_tooltip_text("Choose an option")
        if width > 0:
            self.set_size_request(width, -1)

        control = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        control.set_margin_start(10)
        control.set_margin_end(10)
        selected_label = Gtk.Label(label=choices[selected], xalign=0)
        selected_label.set_ellipsize(3)
        selected_label.set_hexpand(True)
        control.append(selected_label)
        control.append(Gtk.Image.new_from_icon_name("pan-down-symbolic"))
        self.set_child(control)

        popover = Gtk.Popover()
        popover.set_has_arrow(False)
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.add_css_class("choice-popover")

        options = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        options.add_css_class("choice-options")
        self._option_buttons: list[Gtk.Button] = []
        for index, choice in enumerate(choices):
            button = Gtk.Button()
            button.set_halign(Gtk.Align.FILL)
            button.add_css_class("choice-option")
            label = Gtk.Label(label=choice, xalign=0)
            label.set_hexpand(True)
            button.set_child(label)
            button.connect("clicked", self._on_option_clicked, index)
            options.append(button)
            self._option_buttons.append(button)
        popover.set_child(options)
        self.set_popover(popover)
        self._update_selected_style()

    def get_selected(self) -> int:
        return self._selected

    def set_selected(self, selected: int) -> None:
        if not 0 <= selected < len(self._choices):
            raise ValueError("Selected choice index is out of range")
        self._select(selected, notify=False)

    def _on_option_clicked(self, _button, index: int) -> None:
        self._select(index, notify=True)
        self.popdown()

    def _select(self, index: int, notify: bool) -> None:
        changed = index != self._selected
        self._selected = index
        control = self.get_child()
        control.get_first_child().set_label(self._choices[index])
        self._update_selected_style()
        if changed and notify and self._on_changed:
            self._on_changed(index)

    def _update_selected_style(self) -> None:
        for index, button in enumerate(self._option_buttons):
            if index == self._selected:
                button.add_css_class("selected")
            else:
                button.remove_css_class("selected")
