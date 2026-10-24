import QtQuick
import QtQuick.Controls

Slider {
    id: control
    required property var themeColors

    background: Rectangle {
        x: control.leftPadding
        y: control.topPadding + control.availableHeight / 2 - height / 2
        width: control.availableWidth
        height: 4
        radius: 2
        color: control.themeColors.border
        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            radius: parent.radius
            color: control.enabled ? control.themeColors.accent
                : control.themeColors.disabledText
        }
    }

    handle: Rectangle {
        x: control.leftPadding
            + control.visualPosition * (control.availableWidth - width)
        y: control.topPadding + control.availableHeight / 2 - height / 2
        implicitWidth: 14
        implicitHeight: 14
        radius: 7
        color: control.enabled ? control.themeColors.accent
            : control.themeColors.disabledText
        border.color: control.themeColors.panel
        border.width: 2
        scale: control.pressed ? 1.12 : 1
        Behavior on scale { NumberAnimation { duration: 110 } }
        Behavior on color { ColorAnimation { duration: 160 } }
    }
}
