import QtQuick
import QtQuick.Controls

// Material 3 Expressive Thicker Slider with smooth state expansion
Slider {
    id: slider
    property var themeColors: null

    implicitHeight: 36
    hoverEnabled: true

    background: Item {
        x: slider.leftPadding
        y: slider.topPadding + (slider.availableHeight - height) / 2
        width: slider.availableWidth
        height: slider.hovered || slider.pressed ? 12 : 8

        Behavior on height {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
        Behavior on y {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }

        // Inactive background track
        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: slider.themeColors ? slider.themeColors.surfaceContainerHighest : "#37393E"
        }

        // Active highlighted track
        Rectangle {
            width: Math.max(0, Math.min(parent.width, slider.visualPosition * parent.width))
            height: parent.height
            radius: height / 2
            color: slider.themeColors ? slider.themeColors.primary : "#A8C7FA"

            Behavior on width {
                NumberAnimation {
                    duration: 120
                    easing.type: Easing.Linear
                }
            }
        }
    }

    handle: Item {
        x: slider.leftPadding + slider.visualPosition * slider.availableWidth - width / 2
        y: slider.topPadding + slider.availableHeight / 2 - height / 2
        width: slider.pressed ? 8 : 6
        height: slider.hovered || slider.pressed ? 26 : 18

        Behavior on x {
            enabled: !slider.pressed
            NumberAnimation {
                duration: 120
                easing.type: Easing.Linear
            }
        }

        Behavior on height {
            NumberAnimation { duration: 150; easing.type: Easing.OutBack }
        }
        Behavior on width {
            NumberAnimation { duration: 150; easing.type: Easing.OutBack }
        }

        // M3 Pill Thumb
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: slider.themeColors ? slider.themeColors.primary : "#A8C7FA"
            border.width: 1.5
            border.color: "#FFFFFF"
        }
    }

    HoverHandler {
        cursorShape: Qt.PointingHandCursor
    }
}
