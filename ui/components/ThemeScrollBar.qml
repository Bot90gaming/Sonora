import QtQuick
import QtQuick.Controls

ScrollBar {
    id: control
    required property var themeColors

    width: 8
    contentItem: Rectangle {
        implicitWidth: 6
        radius: 3
        color: control.pressed ? control.themeColors.accent
            : control.hovered ? control.themeColors.muted
            : control.themeColors.border
        opacity: control.active ? 1 : 0.45
        Behavior on color { ColorAnimation { duration: 140 } }
        Behavior on opacity { NumberAnimation { duration: 140 } }
    }
}
