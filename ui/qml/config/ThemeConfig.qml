import QtQuick

QtObject {
    required property var bridge

    readonly property bool dark: bridge.darkTheme
    readonly property color background: dark ? "#111116" : "#f7f3fa"
    readonly property color panel: dark ? "#1b1b22" : "#fffaff"
    readonly property color surface: dark ? "#24242b" : "#efebf3"
    readonly property color raised: dark ? "#303039" : "#e7e1eb"
    readonly property color border: dark ? "#383841" : "#d8d1dc"
    readonly property color text: dark ? "#f0edf5" : "#201d24"
    readonly property color muted: dark ? "#aaa6b2" : "#706a77"
    readonly property color accent: bridge.accentColor
    readonly property real accentLuminance:
        0.2126 * linearChannel(accent.r)
        + 0.7152 * linearChannel(accent.g)
        + 0.0722 * linearChannel(accent.b)
    readonly property color accentText:
        accentLuminance > 0.179 ? "#18151d" : "#ffffff"
    readonly property color disabledSurface: dark ? "#292930" : "#e8e4ec"
    readonly property color disabledText: dark ? "#77737e" : "#a19ba7"
    readonly property color cardShadow: dark ? "#b8000000" : "#550d0914"
    readonly property color tooltip: dark ? "#303039" : "#29252f"
    readonly property color tooltipText: "#fffaff"
    readonly property color scrim: dark ? "#99000000" : "#660d0914"
    readonly property color edgeFadeTransparent:
        Qt.rgba(background.r, background.g, background.b, 0)

    function linearChannel(value) {
        return value <= 0.04045
            ? value / 12.92
            : Math.pow((value + 0.055) / 1.055, 2.4)
    }
}
