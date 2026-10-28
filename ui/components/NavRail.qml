import QtQuick
import QtQuick.Controls

// Material 3 Collapsible & Expanded Navigation Rail
Item {
    id: rail
    required property var themeColors
    property string currentPage: "home"
    property bool expanded: false

    signal navigate(string page)

    readonly property var destinations: [
        { name: "Home", page: "home", icon: "home" },
        { name: "Search", page: "search", icon: "search" },
        { name: "Library", page: "library", icon: "library_music" },
        { name: "Downloads", page: "downloads", icon: "download" }
    ]

    // ─── TOP TOGGLE HEADER ───────────────────────────────────────
    Item {
        id: railHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 52

        Rectangle {
            id: toggleBtn
            width: 44
            height: 44
            radius: 22
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: rail.expanded ? 8 : (rail.width - 44) / 2
            color: toggleMouse.pressed
                ? Qt.rgba(rail.themeColors.onSurface.r, rail.themeColors.onSurface.g, rail.themeColors.onSurface.b, 0.12)
                : (toggleMouse.containsMouse
                    ? Qt.rgba(rail.themeColors.onSurface.r, rail.themeColors.onSurface.g, rail.themeColors.onSurface.b, 0.08)
                    : "transparent")

            Behavior on anchors.leftMargin {
                NumberAnimation {
                    duration: rail.themeColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: rail.themeColors.motion.expressiveDefaultSpatialCurve
                }
            }
            Behavior on color {
                ColorAnimation { duration: 150 }
            }

            Text {
                anchors.centerIn: parent
                text: rail.expanded ? "menu_open" : "menu"
                color: rail.themeColors.onSurface
                font.family: "Material Symbols Rounded"
                font.pixelSize: 24
            }

            MouseArea {
                id: toggleMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: rail.expanded = !rail.expanded
            }

            ToolTip.text: rail.expanded ? "Collapse navigation" : "Expand navigation"
            ToolTip.visible: toggleMouse.containsMouse
        }

        Row {
            anchors.left: toggleBtn.right
            anchors.leftMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8
            opacity: rail.expanded ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation {
                    duration: rail.themeColors.motion.expressiveFastEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: rail.themeColors.motion.expressiveFastEffectsCurve
                }
            }

            Text {
                text: "Sonora"
                color: rail.themeColors.onSurface
                font.family: rail.themeColors.fontFamily
                font.pixelSize: rail.themeColors.type.titleMedium
                font.weight: rail.themeColors.type.weightDemiBold
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // ─── MAIN DESTINATIONS ───────────────────────────────────────
    Column {
        id: navColumn
        anchors.top: railHeader.bottom
        anchors.topMargin: 12
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: rail.expanded ? 6 : 10

        Repeater {
            model: rail.destinations

            delegate: RailEntry {
                required property var modelData
                required property int index
                label: modelData.name
                glyph: modelData.icon
                selected: rail.currentPage === modelData.page
                expanded: rail.expanded
                themeColors: rail.themeColors
                onActivated: rail.navigate(modelData.page)
            }
        }
    }

    // ─── BOTTOM SETTINGS & DIVIDER ───────────────────────────────
    Rectangle {
        id: divider
        anchors.bottom: settingsEntry.top
        anchors.bottomMargin: 12
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: rail.expanded ? 16 : 12
        anchors.rightMargin: rail.expanded ? 16 : 12
        height: 1
        color: rail.themeColors.outlineVariant
    }

    RailEntry {
        id: settingsEntry
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 12
        anchors.left: parent.left
        anchors.right: parent.right
        label: "Settings"
        glyph: "settings"
        selected: rail.currentPage === "settings"
        expanded: rail.expanded
        themeColors: rail.themeColors
        onActivated: rail.navigate("settings")
    }

    // ─── REUSABLE NAV ENTRY COMPONENT ────────────────────────────
    component RailEntry: Item {
        id: entry
        property string label: ""
        property string glyph: ""
        property bool selected: false
        property bool expanded: false
        property var themeColors: null

        signal activated

        height: entry.expanded ? 48 : 56
        width: parent ? parent.width : 76

        Behavior on height {
            NumberAnimation {
                duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                easing.type: Easing.BezierSpline
                easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
            }
        }

        // Active Indicator Capsule
        Rectangle {
            id: indicatorPill
            z: 0
            radius: height / 2
            color: entry.themeColors ? entry.themeColors.secondaryContainer : "#383E4C"
            opacity: entry.selected ? 1.0 : 0.0

            // Expanded: horizontal bar filling row
            // Collapsed: 56x32 pill around the icon
            x: entry.expanded ? 8 : (entry.width - 56) / 2
            y: entry.expanded ? 0 : 4
            width: entry.expanded ? entry.width - 16 : 56
            height: entry.expanded ? 48 : 32

            Behavior on x {
                NumberAnimation {
                    duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
                }
            }
            Behavior on width {
                NumberAnimation {
                    duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
                }
            }
            Behavior on height {
                NumberAnimation {
                    duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
                }
            }
            Behavior on opacity {
                NumberAnimation {
                    duration: entry.themeColors ? entry.themeColors.motion.expressiveFastEffectsDuration : 150
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveFastEffectsCurve : [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]
                }
            }
        }

        // Hover & Pressed State Layer
        Rectangle {
            z: 1
            anchors.fill: indicatorPill
            radius: indicatorPill.radius
            color: entry.themeColors ? entry.themeColors.onSurface : "#FFFFFF"
            opacity: mouse.pressed ? 0.12 : (mouse.containsMouse && !entry.selected ? 0.08 : 0.0)
            Behavior on opacity {
                NumberAnimation { duration: 150 }
            }
        }

        // Content: Collapsed (Icon top, Label bottom) vs Expanded (Icon left, Label right)
        Item {
            z: 2
            anchors.fill: parent

            // Icon
            Text {
                id: iconText
                text: entry.glyph
                font.family: "Material Symbols Rounded"
                font.pixelSize: 22
                color: entry.selected
                    ? (entry.themeColors ? entry.themeColors.onSecondaryContainer : "#DAE2F9")
                    : (entry.themeColors ? entry.themeColors.onSurfaceVariant : "#C4C6D0")
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter

                // Collapsed: centered inside the 32px pill (y: 4..36)
                // Expanded: left margin 24, vertically centered
                x: entry.expanded ? 24 : (parent.width - width) / 2
                y: entry.expanded ? (parent.height - height) / 2 : 8
                width: 24
                height: 24

                Behavior on x {
                    NumberAnimation {
                        duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
                    }
                }
                Behavior on y {
                    NumberAnimation {
                        duration: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialDuration : 350
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: entry.themeColors ? entry.themeColors.motion.expressiveDefaultSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
                    }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }
            }

            // Expanded Label (beside icon)
            Text {
                anchors.left: iconText.right
                anchors.leftMargin: 16
                anchors.right: parent.right
                anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                text: entry.label
                color: entry.selected
                    ? (entry.themeColors ? entry.themeColors.onSecondaryContainer : "#DAE2F9")
                    : (entry.themeColors ? entry.themeColors.onSurface : "#E2E2E9")
                font.family: entry.themeColors ? entry.themeColors.fontFamily : "sans-serif"
                font.pixelSize: entry.themeColors ? entry.themeColors.type.labelLarge : 14
                font.weight: entry.selected
                    ? (entry.themeColors ? entry.themeColors.type.weightDemiBold : Font.DemiBold)
                    : (entry.themeColors ? entry.themeColors.type.weightMedium : Font.Medium)
                elide: Text.ElideRight
                opacity: entry.expanded ? 1.0 : 0.0
                visible: opacity > 0.01

                Behavior on opacity {
                    NumberAnimation {
                        duration: entry.themeColors ? entry.themeColors.motion.expressiveFastEffectsDuration : 150
                    }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }
            }

            // Collapsed Label (below icon pill)
            Text {
                anchors.top: iconText.bottom
                anchors.topMargin: 6
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 4
                text: entry.label
                color: entry.selected
                    ? (entry.themeColors ? entry.themeColors.onSurface : "#E2E2E9")
                    : (entry.themeColors ? entry.themeColors.onSurfaceVariant : "#C4C6D0")
                font.family: entry.themeColors ? entry.themeColors.fontFamily : "sans-serif"
                font.pixelSize: entry.themeColors ? entry.themeColors.type.labelSmall : 11
                font.weight: entry.selected
                    ? (entry.themeColors ? entry.themeColors.type.weightDemiBold : Font.DemiBold)
                    : (entry.themeColors ? entry.themeColors.type.weightMedium : Font.Normal)
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                opacity: !entry.expanded ? 1.0 : 0.0
                visible: opacity > 0.01

                Behavior on opacity {
                    NumberAnimation {
                        duration: entry.themeColors ? entry.themeColors.motion.expressiveFastEffectsDuration : 150
                    }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }
            }
        }

        MouseArea {
            id: mouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: entry.activated()
        }

        ToolTip.text: entry.label
        ToolTip.visible: mouse.containsMouse && !entry.expanded
    }
}
