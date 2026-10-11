"""
Glassmorphism CSS theme for GTK4 / Adwaita dark.
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

CSS = f"""
/* ── Window / root ────────────────────────────────────────────────────────── */
window.background,
.background {{
    background-color: {_BG_DARK};
    color: #e2e2f0;
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
.toolbar {{
    background-color: rgba(12, 10, 22, 0.88);
    border-top: 1px solid {_GLASS_BORDER};
    box-shadow: 0 -4px 24px {_SHADOW};
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

/* ── Drop-down ───────────────────────────────────────────────────────────────── */
dropdown > button {{
    background-color: {_GLASS_SURFACE};
    border: 1px solid {_GLASS_BORDER};
    border-radius: 10px;
}}
dropdown > button:hover {{
    background-color: {_GLASS_SURFACE2};
    border-color: {_GLASS_BORDER2};
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
    background-color: rgba(255,255,255,0.10);
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

/* ── Status page ─────────────────────────────────────────────────────────────── */
statuspage {{
    color: {_TEXT_DIM};
}}

/* ── Settings page ──────────────────────────────────────────────────────────── */
.settings-page preferencesgroup {{
    margin: 12px 20px;
}}
.settings-page preferencesgroup > row {{
    padding: 6px 12px;
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


def apply(app=None, theme: str = "dark",
          glass: bool = True, accent: str = "violet"):
    """
    (Re-)apply the theme. Safe to call multiple times — replaces the provider.
    theme  : "dark" | "light" | "system"
    glass  : True = glass surfaces, False = solid surfaces
    accent : one of _ACCENT_COLOURS keys
    """
    global _provider

    from gi.repository import Adw
    scheme = {
        "dark":   Adw.ColorScheme.FORCE_DARK,
        "light":  Adw.ColorScheme.FORCE_LIGHT,
        "system": Adw.ColorScheme.DEFAULT,
    }.get(theme, Adw.ColorScheme.FORCE_DARK)
    Adw.StyleManager.get_default().set_color_scheme(scheme)

    acc_hex, acc_glow = _ACCENT_COLOURS.get(accent, _ACCENT_COLOURS["violet"])
    alpha = "0.06" if glass else "0.95"
    surface_col = f"rgba(255,255,255,{alpha})" if glass else "rgba(30,28,48,0.95)"

    css = _build_css(acc_hex, acc_glow, surface_col, glass)

    display = Gdk.Display.get_default()
    if _provider:
        Gtk.StyleContext.remove_provider_for_display(display, _provider)

    _provider = Gtk.CssProvider()
    _provider.load_from_string(css)
    Gtk.StyleContext.add_provider_for_display(
        display, _provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def _build_css(acc: str, glow: str, surface: str, glass: bool) -> str:
    border_a = "0.14" if glass else "0.25"
    return CSS.replace(_ACCENT, acc).replace(_ACCENT_GLOW, glow) \
              .replace(_GLASS_SURFACE, surface) \
              .replace("rgba(255, 255, 255, 0.14)", f"rgba(255,255,255,{border_a})")
