import QtQuick
import QtQuick.Controls

ToolButton {
    id: control
    required property var themeColors
    property color iconColor: control.enabled
        ? control.themeColors.text : control.themeColors.disabledText

    hoverEnabled: true
    implicitWidth: 32
    implicitHeight: 32
    padding: 0
    spacing: 0

    contentItem: Text {
        text: control.text
        color: control.iconColor
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideNone
    }

    background: Rectangle {
        implicitWidth: 32
        implicitHeight: 32
        radius: 10
        color: !control.enabled ? "transparent"
            : control.down ? control.themeColors.raised
            : control.hovered ? control.themeColors.surface : "transparent"
        border.color: control.checked || control.activeFocus
            ? control.themeColors.accent : "transparent"
        Behavior on color { ColorAnimation { duration: 140 } }
    }
}
