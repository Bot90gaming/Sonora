"""
Theme CSS for GTK4 / Adwaita.
Injects a custom CssProvider at application startup.
Real blur-behind requires a compositor (GNOME Shell / KWin with blur plugin).
On any compositor with alpha support, the frosted-glass palette still looks great.
"""
from __future__ import annotations
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk

# ── Palette ───────────────────────────────────────────────────────────────────
# Base colours for the glass surfaces
_BG_DARK        = "rgba(10, 10, 18, 0.92)"
_GLASS_SURFACE  = "rgba(255, 255, 255, 0.06)"
_GLASS_SURFACE2 = "rgba(255, 255, 255, 0.10)"
_GLASS_BORDER   = "rgba(255, 255, 255, 0.14)"
_GLASS_BORDER2  = "rgba(255, 255, 255, 0.22)"
_ACCENT         = "#a78bfa"          # violet-400
_ACCENT_GLOW    = "rgba(167,139,250,0.35)"
_TEXT_DIM       = "rgba(255,255,255,0.45)"
_SHADOW         = "rgba(0, 0, 0, 0.55)"
_PROGRESS_TROUGH = "__PROGRESS_TROUGH__"
_ACCOUNT_POPOVER_BG = "__ACCOUNT_POPOVER_BG__"

CSS = f"""
/* ── Window / root ────────────────────────────────────────────────────────── */
window.background,
.background {{
    background-color: {_BG_DARK};
    color: #e2e2f0;
}}
window label,
window entry,
window textview text,
window dropdown,
window dropdown row,
window .title,
window .subtitle {{
    color: #e2e2f0;
}}
window label.dim-label {{
    color: {_TEXT_DIM};
}}

/* ── Header bar ────────────────────────────────────────────────────────────── */
headerbar {{
    background-color: rgba(20, 18, 36, 0.75);
    border-bottom: 1px solid {_GLASS_BORDER};
    box-shadow: 0 1px 12px {_SHADOW};
    padding: 4px 8px;
}}
headerbar .title {{
    font-weight: 600;
    letter-spacing: 0.5px;
}}

/* ── View switcher tabs ─────────────────────────────────────────────────────── */
viewswitcher button {{
    background-color: transparent;
    border-radius: 10px;
    padding: 4px 16px;
    transition: background-color 150ms ease;
}}
viewswitcher button:hover {{
    background-color: {_GLASS_SURFACE2};
}}
viewswitcher button:checked {{
    background-color: {_GLASS_SURFACE2};
    border: 1px solid {_GLASS_BORDER2};
    box-shadow: 0 0 12px {_ACCENT_GLOW};
    color: {_ACCENT};
}}

/* ── Sidebar (navigation-sidebar) ──────────────────────────────────────────── */
.navigation-sidebar {{
    background-color: rgba(15, 13, 28, 0.60);
    border-right: 1px solid {_GLASS_BORDER};
}}
.navigation-sidebar row {{
    border-radius: 10px;
    margin: 2px 6px;
    transition: background-color 120ms ease;
}}
.navigation-sidebar row:hover {{
    background-color: {_GLASS_SURFACE2};
}}
.navigation-sidebar row:selected {{
    background-color: rgba(167,139,250,0.18);
    border: 1px solid rgba(167,139,250,0.30);
    box-shadow: 0 0 10px {_ACCENT_GLOW};
    color: {_ACCENT};
}}

/* ── Track list ─────────────────────────────────────────────────────────────── */
.boxed-list {{
    background-color: transparent;
    border: none;
}}
.boxed-list row {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 12px;
    margin: 3px 12px;
    transition: background-color 120ms ease,
                border-color    120ms ease,
                box-shadow      120ms ease;
}}
.boxed-list row:hover {{
    background-color: {_GLASS_SURFACE2};
    border-color: {_GLASS_BORDER2};
    box-shadow: 0 2px 16px {_SHADOW};
}}
.boxed-list row:selected {{
    background-color: rgba(167,139,250,0.15);
    border-color: rgba(167,139,250,0.40);
    box-shadow: 0 0 14px {_ACCENT_GLOW};
}}

/* ── Cards (download page) ──────────────────────────────────────────────────── */
.card {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 14px;
    box-shadow: 0 4px 20px {_SHADOW};
}}

/* ── Player bar ─────────────────────────────────────────────────────────────── */
box.player-bar {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 20px;
    box-shadow: 0 8px 28px {_SHADOW};
    padding: 10px 14px;
}}
.player-art {{
    background-color: {_GLASS_SURFACE2};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 8px;
}}
.track-thumb {{
    background-color: {_GLASS_SURFACE2};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 8px;
}}
.player-controls {{
    margin-bottom: 1px;
}}
button.player-transport {{
    min-width: 34px;
    min-height: 34px;
    color: {_TEXT_DIM};
}}
button.player-play {{
    min-width: 42px;
    min-height: 42px;
    padding: 0;
}}
.player-seek scale {{
    min-width: 280px;
}}
.player-side-controls {{
    border-radius: 999px;
}}
.player-side-controls image {{
    color: {_TEXT_DIM};
}}

/* ── Buttons ─────────────────────────────────────────────────────────────────── */
button.suggested-action {{
    background-color: rgba(167,139,250,0.80);
    border: 1px solid rgba(167,139,250,0.60);
    border-radius: 999px;
    box-shadow: 0 0 14px {_ACCENT_GLOW};
    color: #0a0a12;
    font-weight: 600;
    transition: background-color 150ms ease, box-shadow 150ms ease;
}}
button.suggested-action:hover {{
    background-color: rgba(167,139,250,1.0);
    box-shadow: 0 0 22px {_ACCENT_GLOW};
}}
button.circular.flat {{
    background-color: transparent;
    border-radius: 999px;
    transition: background-color 120ms ease;
}}
button.circular.flat:hover {{
    background-color: {_GLASS_SURFACE2};
}}
button.accent {{
    color: {_ACCENT};
}}
switch:checked,
checkbutton check:checked,
radiobutton radio:checked {{
    background-color: {_ACCENT};
    border-color: {_ACCENT};
}}

/* ── Search entry ───────────────────────────────────────────────────────────── */
entry,
searchentry {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 12px;
    color: #e2e2f0;
    padding: 6px 12px;
    box-shadow: inset 0 1px 4px rgba(0,0,0,0.25);
    transition: border-color 150ms ease, box-shadow 150ms ease;
}}
entry:focus,
searchentry:focus {{
    border-color: rgba(167,139,250,0.60);
    box-shadow: inset 0 1px 4px rgba(0,0,0,0.25),
                0 0 0 3px rgba(167,139,250,0.20);
    outline: none;
}}

/* ── Custom choice dropdown ─────────────────────────────────────────────────── */
menubutton.choice-control > button {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 10px;
    color: #e2e2f0;
    padding: 4px 0;
}}
menubutton.choice-control > button:hover {{
    background-color: {_GLASS_SURFACE2};
    border-color: {_GLASS_BORDER2};
}}
popover.choice-popover {{
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
}}
popover.choice-popover > contents {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 14px;
    box-shadow: 0 8px 24px {_SHADOW};
    padding: 6px;
}}
.choice-options {{
    background-color: transparent;
}}
button.choice-option {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    box-shadow: none;
    color: #e2e2f0;
    padding: 8px 12px;
}}
button.choice-option:hover {{
    background-color: {_GLASS_SURFACE2};
}}
button.choice-option.selected {{
    background-color: rgba(167,139,250,0.18);
    color: {_ACCENT};
}}
.login-dialog notebook,
.login-dialog notebook > stack,
.login-dialog notebook > stack > box,
.login-dialog label,
.login-dialog textview,
.login-dialog textview text {{
    background-color: transparent;
}}
.login-dialog textview,
.login-dialog textview text {{
    color: #e2e2f0;
}}

/* ── Scale / slider ─────────────────────────────────────────────────────────── */
scale trough {{
    background-color: rgba(255,255,255,0.12);
    border-radius: 999px;
    min-height: 4px;
}}
scale trough highlight {{
    background-color: {_ACCENT};
    border-radius: 999px;
}}
scale slider {{
    background-color: #ffffff;
    border-radius: 999px;
    min-width:  14px;
    min-height: 14px;
    box-shadow: 0 0 6px {_ACCENT_GLOW};
}}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
scrollbar {{
    background-color: transparent;
}}
scrollbar slider {{
    background-color: rgba(255,255,255,0.18);
    border-radius: 999px;
    min-width: 5px;
}}
scrollbar slider:hover {{
    background-color: rgba(255,255,255,0.30);
}}

/* ── Progress bar ────────────────────────────────────────────────────────────── */
progressbar trough {{
    background-color: {_PROGRESS_TROUGH};
    border-radius: 999px;
    min-height: 5px;
}}
progressbar progress {{
    background-color: {_ACCENT};
    border-radius: 999px;
    box-shadow: 0 0 8px {_ACCENT_GLOW};
}}

/* ── Separator ───────────────────────────────────────────────────────────────── */
separator {{
    background-color: {_GLASS_BORDER};
    min-height: 1px;
}}

/* ── Labels ─────────────────────────────────────────────────────────────────── */
.dim-label {{
    color: {_TEXT_DIM};
}}
.heading {{
    font-weight: 600;
    letter-spacing: 0.3px;
}}
.caption {{
    font-size: 0.78em;
}}

/* ── Popover ─────────────────────────────────────────────────────────────────── */
popover > contents {{
    background-color: rgba(20, 18, 36, 0.92);
    border: 1px solid {_GLASS_BORDER2};
    border-radius: 14px;
    box-shadow: 0 8px 32px {_SHADOW};
}}

popover.account-popover {{
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
}}
popover.account-popover > contents {{
    background-color: {_ACCOUNT_POPOVER_BG};
    border: 1px solid {_GLASS_BORDER2};
    border-radius: 16px;
    box-shadow: 0 10px 30px {_SHADOW};
    padding: 2px;
}}
.account-menu-content {{
    background-color: transparent;
}}
.account-menu-status {{
    padding: 6px 8px;
}}
button.account-menu-action {{
    background-color: transparent;
    border: none;
    border-radius: 10px;
    box-shadow: none;
    color: #e2e2f0;
    padding: 8px 10px;
}}
button.account-menu-action:hover {{
    background-color: {_GLASS_SURFACE2};
}}

/* ── Status page ─────────────────────────────────────────────────────────────── */
statuspage {{
    color: {_TEXT_DIM};
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 18px;
    margin: 12px;
    padding: 16px;
}}
"""


_ACCENT_COLOURS = {
    "violet": ("#a78bfa", "rgba(167,139,250,0.35)"),
    "blue":   ("#60a5fa", "rgba( 96,165,250,0.35)"),
    "green":  ("#34d399", "rgba( 52,211,153,0.35)"),
    "rose":   ("#fb7185", "rgba(251,113,133,0.35)"),
    "orange": ("#fb923c", "rgba(251,146, 60,0.35)"),
}

_provider: Gtk.CssProvider | None = None
_style_manager = None
_theme_options: dict | None = None


def apply(app=None, theme: str = "dark",
          glass: bool = True, accent: str = "violet"):
    """
    (Re-)apply the theme. Safe to call multiple times — replaces the provider.
    theme  : "dark" | "light" | "system"
    glass  : True = glass surfaces, False = solid surfaces
    accent : one of _ACCENT_COLOURS keys
    """
    global _provider, _style_manager, _theme_options

    from gi.repository import Adw
    _theme_options = {
        "app": app,
        "theme": theme,
        "glass": glass,
        "accent": accent,
    }
    _style_manager = Adw.StyleManager.get_default()
    if not getattr(apply, "_system_scheme_connected", False):
        _style_manager.connect("notify::dark", _on_system_scheme_changed)
        apply._system_scheme_connected = True

    scheme = {
        "dark":   Adw.ColorScheme.FORCE_DARK,
        "light":  Adw.ColorScheme.FORCE_LIGHT,
        "system": Adw.ColorScheme.DEFAULT,
    }.get(theme, Adw.ColorScheme.FORCE_DARK)
    _style_manager.set_color_scheme(scheme)
    is_dark = theme == "dark" or (theme == "system" and _style_manager.get_dark())

    acc_hex, acc_glow = _ACCENT_COLOURS.get(accent, _ACCENT_COLOURS["violet"])
    surface_col = (
        "rgba(255,255,255,0.06)" if is_dark else "rgba(35,25,55,0.035)"
    ) if glass else (
        "rgba(30,28,48,0.95)" if is_dark else "rgba(255,255,255,0.96)"
    )
    surface2_col = (
        "rgba(255,255,255,0.10)" if is_dark else "rgba(35,25,55,0.07)"
    ) if glass else (
        "rgba(30,28,48,1.0)" if is_dark else "rgba(255,255,255,1.0)"
    )

    css = _build_css(acc_hex, acc_glow, surface_col, surface2_col, glass, is_dark)

    display = Gdk.Display.get_default()
    if _provider:
        Gtk.StyleContext.remove_provider_for_display(display, _provider)

    _provider = Gtk.CssProvider()
    _provider.load_from_string(css)
    Gtk.StyleContext.add_provider_for_display(
        display, _provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def _on_system_scheme_changed(*_):
    if _theme_options and _theme_options["theme"] == "system":
        apply(**_theme_options)


def _rgba(hex_colour: str, alpha: float) -> str:
    red = int(hex_colour[1:3], 16)
    green = int(hex_colour[3:5], 16)
    blue = int(hex_colour[5:7], 16)
    return f"rgba({red},{green},{blue},{alpha})"


def _build_css(acc: str, glow: str, surface: str, surface2: str,
               glass: bool, is_dark: bool) -> str:
    border = (
        "rgba(255,255,255,0.14)" if glass else "rgba(255,255,255,0.25)"
    ) if is_dark else (
        "rgba(40,32,60,0.16)" if glass else "rgba(40,32,60,0.25)"
    )
    border2 = (
        "rgba(255,255,255,0.22)" if glass else "rgba(255,255,255,0.35)"
    ) if is_dark else (
        "rgba(40,32,60,0.26)" if glass else "rgba(40,32,60,0.35)"
    )
    text = "#e2e2f0" if is_dark else "#242033"
    dim_text = "rgba(255,255,255,0.45)" if is_dark else "rgba(36,32,51,0.62)"
    shadow = "rgba(0,0,0,0.55)" if is_dark else "rgba(35,25,55,0.16)"
    root_bg = "rgba(10,10,18,0.92)" if is_dark else "rgba(247,246,251,0.98)"
    header_bg = "rgba(20,18,36,0.75)" if is_dark else "rgba(255,255,255,0.88)"
    sidebar_bg = "rgba(15,13,28,0.60)" if is_dark else "rgba(238,235,246,0.90)"
    toolbar_bg = "rgba(12,10,22,0.88)" if is_dark else "rgba(255,255,255,0.92)"
    popover_bg = "rgba(20,18,36,0.92)" if is_dark else "rgba(255,255,255,0.98)"
    account_popover_bg = (
        "rgba(20,18,36,0.72)" if is_dark else "rgba(255,255,255,0.76)"
    ) if glass else (
        "rgba(30,28,48,0.98)" if is_dark else "rgba(255,255,255,0.98)"
    )
    scale_trough = "rgba(255,255,255,0.12)" if is_dark else "rgba(35,25,55,0.14)"
    scale_slider = "#ffffff" if is_dark else "#615b70"
    scrollbar = "rgba(255,255,255,0.18)" if is_dark else "rgba(35,25,55,0.20)"
    scrollbar_hover = "rgba(255,255,255,0.30)" if is_dark else "rgba(35,25,55,0.32)"
    progress_trough = "rgba(255,255,255,0.10)" if is_dark else "rgba(35,25,55,0.10)"
    nav_selection = _rgba(acc, 0.18)
    nav_selection_border = _rgba(acc, 0.30)
    row_selection = _rgba(acc, 0.15)
    row_selection_border = _rgba(acc, 0.40)
    button_bg = _rgba(acc, 0.80)
    button_border = _rgba(acc, 0.60)
    focus_ring = _rgba(acc, 0.20)

    css = CSS
    replacements = {
        _BG_DARK: root_bg,
        "#e2e2f0": text,
        "rgba(20, 18, 36, 0.75)": header_bg,
        "rgba(15, 13, 28, 0.60)": sidebar_bg,
        "rgba(12, 10, 22, 0.88)": toolbar_bg,
        "rgba(20, 18, 36, 0.92)": popover_bg,
        _ACCOUNT_POPOVER_BG: account_popover_bg,
        _GLASS_SURFACE: surface,
        _GLASS_SURFACE2: surface2,
        _PROGRESS_TROUGH: progress_trough,
        _GLASS_BORDER: border,
        _GLASS_BORDER2: border2,
        _TEXT_DIM: dim_text,
        _SHADOW: shadow,
        _ACCENT: acc,
        _ACCENT_GLOW: glow,
        "rgba(167,139,250,0.18)": nav_selection,
        "rgba(167,139,250,0.30)": nav_selection_border,
        "rgba(167,139,250,0.15)": row_selection,
        "rgba(167,139,250,0.40)": row_selection_border,
        "rgba(167,139,250,0.80)": button_bg,
        "rgba(167,139,250,0.60)": button_border,
        "rgba(167,139,250,1.0)": acc,
        "rgba(167,139,250,0.20)": focus_ring,
        "rgba(255,255,255,0.12)": scale_trough,
        "#ffffff": scale_slider,
        "rgba(255,255,255,0.18)": scrollbar,
        "rgba(255,255,255,0.30)": scrollbar_hover,
        "rgba(255,255,255,0.14)": border,
    }
    for old, new in replacements.items():
        css = css.replace(old, new)
    return css
