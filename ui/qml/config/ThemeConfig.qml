import QtQuick

QtObject {
    id: theme

    property var bridge: null

    // ─── DYNAMIC MATERIAL YOU SEED & PALETTE ─────────────────────
    readonly property color rawSeed: bridge ? (bridge.dynamicColor || bridge.accentColor || "#3B82F6") : "#3B82F6"
    readonly property bool isDark: bridge ? bridge.darkTheme : true

    function blend(c1, c2, w) {
        let a = Qt.color(c1)
        let b = Qt.color(c2)
        return Qt.rgba(a.r * (1 - w) + b.r * w, a.g * (1 - w) + b.g * w, a.b * (1 - w) + b.b * w, 1)
    }

    function lighten(c, factor) {
        let col = Qt.color(c)
        return Qt.rgba(
            Math.min(1.0, col.r + (1 - col.r) * factor),
            Math.min(1.0, col.g + (1 - col.g) * factor),
            Math.min(1.0, col.b + (1 - col.b) * factor),
            1
        )
    }

    function darken(c, factor) {
        let col = Qt.color(c)
        return Qt.rgba(col.r * (1 - factor), col.g * (1 - factor), col.b * (1 - factor), 1)
    }

    function withAlpha(c, alpha) {
        let col = Qt.color(c)
        return Qt.rgba(col.r, col.g, col.b, alpha)
    }

    function contrastText(c) {
        if (!c) return isDark ? "#FFFFFF" : "#0A0D14"
        let col = Qt.color(c)
        let lum = 0.2126 * col.r + 0.7152 * col.g + 0.0722 * col.b
        return lum > 0.42 ? "#091024" : "#FFFFFF"
    }

    // ── Inner Container Palette (avoids QML on<Prop> signal handler collision) ──
    property QtObject _containers: QtObject {
        id: _cnt
        property color surface:            theme.isDark ? theme.blend("#16181E", theme.rawSeed, 0.07) : theme.blend("#FAF9FD", theme.rawSeed, 0.04)
        property color primary:            theme.isDark ? theme.lighten(theme.rawSeed, 0.22) : theme.darken(theme.rawSeed, 0.24)
        property color primaryContainer:   theme.isDark ? theme.darken(theme.rawSeed, 0.42) : theme.lighten(theme.rawSeed, 0.72)
        property color secondary:          theme.isDark ? theme.blend("#D8D0E6", theme.rawSeed, 0.15) : theme.blend("#4F495E", theme.rawSeed, 0.20)
        property color secondaryContainer: theme.isDark ? theme.blend("#3C4352", theme.rawSeed, 0.18) : theme.blend("#E2D6F5", theme.rawSeed, 0.25)
        property color tertiary:           theme.isDark ? "#F5C2D1" : "#6E4554"
        property color tertiaryContainer:  theme.isDark ? "#5D3744" : "#FFD8E4"
        property color error:              theme.isDark ? "#F8B4B4" : "#B3261E"
        property color errorContainer:     theme.isDark ? "#8C1D18" : "#F9DEDC"
    }

    property alias surface:            _cnt.surface
    property alias primary:            _cnt.primary
    property alias primaryContainer:   _cnt.primaryContainer
    property alias secondary:          _cnt.secondary
    property alias secondaryContainer: _cnt.secondaryContainer
    property alias tertiary:           _cnt.tertiary
    property alias tertiaryContainer:  _cnt.tertiaryContainer
    property alias error:              _cnt.error
    property alias errorContainer:     _cnt.errorContainer

    // ── Surface & Background Tokens ──────────────────────────────
    readonly property color md3Bg:                 isDark ? blend("#101217", rawSeed, 0.06) : blend("#FBF8FD", rawSeed, 0.04)
    readonly property color bgBase:                md3Bg
    readonly property color surfaceDim:            isDark ? blend("#0E1015", rawSeed, 0.05) : blend("#DDD7E0", rawSeed, 0.06)
    readonly property color surfaceBright:         isDark ? blend("#363941", rawSeed, 0.09) : "#FFFFFF"

    readonly property color surfaceContainerLowest:isDark ? blend("#0A0C10", rawSeed, 0.04) : "#FFFFFF"
    readonly property color surfaceContainerLow:   isDark ? blend("#191C22", rawSeed, 0.06) : blend("#F5EFF7", rawSeed, 0.05)
    readonly property color surfaceContainer:      isDark ? blend("#20232A", rawSeed, 0.08) : blend("#EFE7F4", rawSeed, 0.07)
    readonly property color surfaceContainerHigh:  isDark ? blend("#2A2D35", rawSeed, 0.09) : blend("#E9E1EF", rawSeed, 0.09)
    readonly property color surfaceContainerHighest:isDark ? blend("#353841", rawSeed, 0.11) : blend("#E3DBE9", rawSeed, 0.11)

    // High Contrast Typography Tokens (WCAG AAA compliant)
    readonly property color onSurface:             isDark ? "#F4F4FA" : "#111216"
    readonly property color onSurfaceVariant:      isDark ? "#D6D8E4" : "#373A42"
    readonly property color inverseSurface:        isDark ? "#F4F4FA" : "#111216"
    readonly property color inverseOnSurface:      isDark ? "#16181E" : "#F4EFF7"

    // ── Primary Roles ────────────────────────────────────────────
    readonly property color onPrimary:             contrastText(primary)
    readonly property color onPrimaryContainer:    isDark ? lighten(rawSeed, 0.75) : darken(rawSeed, 0.60)
    readonly property color inversePrimary:        isDark ? darken(rawSeed, 0.25) : lighten(rawSeed, 0.35)

    // ── Secondary Roles ──────────────────────────────────────────
    readonly property color onSecondary:           isDark ? "#282334" : "#FFFFFF"
    readonly property color onSecondaryContainer:  isDark ? blend("#E4ECFF", rawSeed, 0.20) : blend("#141021", rawSeed, 0.25)

    // ── Tertiary Roles ───────────────────────────────────────────
    readonly property color onTertiary:            isDark ? "#3F1E2A" : "#FFFFFF"
    readonly property color onTertiaryContainer:   isDark ? "#FFDCE6" : "#280A16"

    // ── Error Roles ──────────────────────────────────────────────
    readonly property color onError:               isDark ? "#560000" : "#FFFFFF"
    readonly property color onErrorContainer:      isDark ? "#F9DEDC" : "#410E0B"

    // ── Outlines, Scrim & Shadows ────────────────────────────────
    readonly property color outline:               isDark ? "#9DA0AA" : "#6B6772"
    readonly property color outlineVariant:        isDark ? blend("#30333C", rawSeed, 0.12) : blend("#C0BAC6", rawSeed, 0.12)
    readonly property color scrim:                 "#000000"
    readonly property color shadow:                isDark ? "#000000" : Qt.rgba(0, 0, 0, 0.25)
    readonly property color edgeFadeTransparent:   Qt.rgba(surface.r, surface.g, surface.b, 0)

    // ── States & Disabled ────────────────────────────────────────
    readonly property color disabledSurface:       isDark ? "#26262D" : "#E2E2E8"
    readonly property color disabledText:          isDark ? "#8C8996" : "#6E6B76"
    readonly property real stateHover:             0.08
    readonly property real statePressed:           0.12
    readonly property real stateFocus:             0.12
    readonly property real stateDragged:           0.16

    // ── Fonts ────────────────────────────────────────────────────
    readonly property string fontFamily:           "Roboto, Cantarell, Noto Sans, sans-serif"
    readonly property string iconFontFamily:       "Material Symbols Rounded"

    // ── Shape Scale (radii) ──────────────────────────────────────
    readonly property QtObject shape: QtObject {
        readonly property int none:       0
        readonly property int extraSmall: 4
        readonly property int small:      8
        readonly property int medium:     12
        readonly property int large:      16
        readonly property int extraLarge: 28
        readonly property int full:       1000
    }

    // ── Typography Scale ─────────────────────────────────────────
    readonly property QtObject type: QtObject {
        readonly property int displayLarge:   57
        readonly property int displayMedium:  45
        readonly property int displaySmall:   36
        readonly property int headlineLarge:  32
        readonly property int headlineMedium: 28
        readonly property int headlineSmall:  24
        readonly property int titleLarge:     22
        readonly property int titleMedium:    16
        readonly property int titleSmall:     14
        readonly property int bodyLarge:      16
        readonly property int bodyMedium:     14
        readonly property int bodySmall:      12
        readonly property int labelLarge:     14
        readonly property int labelMedium:    12
        readonly property int labelSmall:     11

        readonly property int weightBold:     Font.Bold
        readonly property int weightDemiBold: Font.DemiBold
        readonly property int weightMedium:   Font.Medium
        readonly property int weightRegular:  Font.Normal

        readonly property real trackingBodyMedium: 0.25
        readonly property real trackingBodySmall:  0.4
        readonly property real trackingLabelLarge: 0.1
        readonly property real trackingLabelMedium:0.5
        readonly property real trackingLabelSmall: 0.5
        readonly property real trackingTitleLarge: 0
    }

    // ── Motion Tokens & Curves ───────────────────────────────────
    readonly property QtObject motion: QtObject {
        readonly property int short1: 50
        readonly property int short2: 100
        readonly property int short3: 150
        readonly property int short4: 200
        readonly property int medium1: 250
        readonly property int medium2: 300
        readonly property int medium3: 350
        readonly property int medium4: 400
        readonly property int long1: 450
        readonly property int long2: 500
        readonly property int extraLong1: 700

        readonly property int expressiveFastSpatialDuration: 150
        readonly property list<real> expressiveFastSpatialCurve: [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]

        readonly property int expressiveFastEffectsDuration: 150
        readonly property list<real> expressiveFastEffectsCurve: [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]

        readonly property int expressiveDefaultSpatialDuration: 350
        readonly property list<real> expressiveDefaultSpatialCurve: [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]

        readonly property int expressiveSlowSpatialDuration: 550
        readonly property list<real> expressiveSlowSpatialCurve: [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]

        readonly property int expressiveDefaultEffectsDuration: 250
        readonly property list<real> expressiveDefaultEffectsCurve: [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]
    }
}
