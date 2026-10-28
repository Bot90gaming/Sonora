import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// M3 filter chip, also used as a segmented control segment.
Button {
    id: control
    required property var themeColors
    property bool selected: false
    checkable: false

    implicitHeight: 32
    implicitWidth: chipRow.implicitWidth + 24
    leftPadding: 12
    rightPadding: 16
    hoverEnabled: true

    contentItem: RowLayout {
        id: chipRow
        spacing: 6
        Text {
            visible: control.selected
            text: "check"
            color: control.themeColors.onSecondaryContainer
            font.family: "Material Symbols Rounded"
            font.pixelSize: 16
            verticalAlignment: Text.AlignVCenter
        }
        Text {
            text: control.text
            color: control.selected
                ? control.themeColors.onSecondaryContainer
                : control.themeColors.onSurfaceVariant
            font.family: control.themeColors.fontFamily
            font.pixelSize: control.themeColors.type.labelLarge
            font.weight: control.themeColors.type.weightMedium
            font.letterSpacing: control.themeColors.type.trackingLabelLarge
            verticalAlignment: Text.AlignVCenter
            Behavior on color {
                ColorAnimation {
                    duration: control.themeColors.motion.expressiveFastEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: control.themeColors.motion.expressiveFastEffectsCurve
                }
            }
        }
    }

    background: Rectangle {
        radius: control.themeColors.shape.small
        color: control.selected
            ? control.themeColors.secondaryContainer : "transparent"
        border.width: control.activeFocus ? 2 : control.selected ? 0 : 1
        border.color: control.activeFocus
            ? control.themeColors.primary : control.themeColors.outline

        Behavior on color {
            ColorAnimation {
                duration: control.themeColors.motion.expressiveFastEffectsDuration
                easing.type: Easing.BezierSpline
                easing.bezierCurve: control.themeColors.motion.expressiveFastEffectsCurve
            }
        }

        StateLayer {
            motion: control.themeColors.motion
            radius: parent.radius
            stateColor: control.selected
                ? control.themeColors.onSecondaryContainer
                : control.themeColors.onSurfaceVariant
            hovered: control.hovered
            pressed: control.down
            focused: control.activeFocus
        }
    }

    HoverHandler {
        cursorShape: Qt.PointingHandCursor
    }
}
