import QtQuick

Item {
    id: btn
    property var themeColors: null
    property string icon: ""
    property string text: ""
    property color iconColor: themeColors ? themeColors.onSurfaceVariant : "#C4C6D0"
    property int iconSize: 22

    signal clicked()

    implicitWidth: 40
    implicitHeight: 40
    width: implicitWidth
    height: implicitHeight

    readonly property bool hovered: mouseArea.containsMouse
    readonly property bool pressed: mouseArea.pressed

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        color: {
            if (!btn.enabled) return "transparent"
            if (btn.pressed) return btn.themeColors ? Qt.rgba(btn.themeColors.onSurface.r, btn.themeColors.onSurface.g, btn.themeColors.onSurface.b, 0.12) : "#20FFFFFF"
            if (btn.hovered) return btn.themeColors ? Qt.rgba(btn.themeColors.onSurface.r, btn.themeColors.onSurface.g, btn.themeColors.onSurface.b, 0.08) : "#15FFFFFF"
            return "transparent"
        }

        Behavior on color {
            ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
        }

        scale: btn.pressed ? 0.90 : 1.0
        Behavior on scale {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
    }

    Text {
        anchors.centerIn: parent
        text: btn.icon !== "" ? btn.icon : btn.text
        font.family: "Material Symbols Rounded"
        font.pixelSize: btn.iconSize
        color: btn.enabled ? btn.iconColor : (btn.themeColors ? btn.themeColors.disabledText : "#77737E")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        Behavior on color {
            ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: if (btn.enabled) btn.clicked()
    }
}
