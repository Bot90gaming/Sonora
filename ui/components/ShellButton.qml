import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool primary: false
    required property var themeColors

    implicitHeight: 42
    leftPadding: 16
    rightPadding: 16

    contentItem: Text {
        text: control.text
        color: !control.enabled ? control.themeColors.disabledText
            : control.primary ? control.themeColors.accentText
            : control.themeColors.text
        font.pixelSize: 13
        font.weight: Font.Medium
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: 16
        color: !control.enabled ? control.themeColors.disabledSurface
            : control.primary ? control.themeColors.accent
            : control.down ? control.themeColors.raised
            : control.hovered ? control.themeColors.raised : control.themeColors.surface
        border.color: !control.enabled ? control.themeColors.disabledSurface
            : control.activeFocus ? control.themeColors.accent
            : control.primary ? control.themeColors.accent : control.themeColors.border
        Behavior on color { ColorAnimation { duration: 160 } }
        Behavior on border.color { ColorAnimation { duration: 160 } }
    }
}
