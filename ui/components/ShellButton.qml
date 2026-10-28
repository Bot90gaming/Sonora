import QtQuick
import QtQuick.Controls

Button {
    id: control
    property var themeColors: null
    property bool primary: false
    property string variant: "filled" // filled, tonal, text, outlined
    property string iconName: ""
    property string leadingIcon: ""

    implicitHeight: 40
    leftPadding: iconName !== "" ? 12 : 16
    rightPadding: 16
    hoverEnabled: true

    contentItem: Row {
        spacing: 8
        anchors.centerIn: parent

        Text {
            visible: control.iconName !== "" || control.leadingIcon !== ""
            text: control.iconName !== "" ? control.iconName : control.leadingIcon
            font.family: "Material Symbols Rounded"
            font.pixelSize: 18
            color: control.textColor
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: control.text
            font.family: control.themeColors ? control.themeColors.fontFamily : "sans-serif"
            font.pixelSize: control.themeColors ? control.themeColors.type.labelLarge : 14
            font.weight: control.themeColors ? control.themeColors.type.weightMedium : Font.Medium
            color: control.textColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    readonly property color textColor: {
        if (!control.enabled) return control.themeColors ? control.themeColors.disabledText : "#77737E"
        if (control.variant === "text" || control.variant === "outlined") {
            return control.themeColors ? control.themeColors.primary : "#A8C7FA"
        }
        if (control.variant === "tonal") {
            return control.themeColors ? control.themeColors.onSecondaryContainer : "#DAE2F9"
        }
        // filled
        return control.themeColors ? control.themeColors.onPrimary : "#062E6F"
    }

    background: Rectangle {
        radius: control.height / 2
        color: {
            if (!control.enabled) {
                return control.variant === "text" || control.variant === "outlined"
                    ? "transparent" : (control.themeColors ? control.themeColors.disabledSurface : "#292930")
            }
            if (control.variant === "text") {
                if (control.down) return control.themeColors ? Qt.rgba(control.themeColors.onSurface.r, control.themeColors.onSurface.g, control.themeColors.onSurface.b, 0.12) : "#20FFFFFF"
                if (control.hovered) return control.themeColors ? Qt.rgba(control.themeColors.onSurface.r, control.themeColors.onSurface.g, control.themeColors.onSurface.b, 0.08) : "#15FFFFFF"
                return "transparent"
            }
            if (control.variant === "outlined") {
                if (control.down) return control.themeColors ? Qt.rgba(control.themeColors.onSurface.r, control.themeColors.onSurface.g, control.themeColors.onSurface.b, 0.12) : "#20FFFFFF"
                if (control.hovered) return control.themeColors ? Qt.rgba(control.themeColors.onSurface.r, control.themeColors.onSurface.g, control.themeColors.onSurface.b, 0.08) : "#15FFFFFF"
                return "transparent"
            }
            if (control.variant === "tonal") {
                if (control.down) return control.themeColors ? Qt.darker(control.themeColors.secondaryContainer, 1.1) : "#353D4D"
                if (control.hovered) return control.themeColors ? Qt.lighter(control.themeColors.secondaryContainer, 1.1) : "#454F63"
                return control.themeColors ? control.themeColors.secondaryContainer : "#3E4759"
            }
            // filled
            if (control.down) return control.themeColors ? Qt.darker(control.themeColors.primary, 1.1) : "#95B5EC"
            if (control.hovered) return control.themeColors ? Qt.lighter(control.themeColors.primary, 1.08) : "#BBD4FC"
            return control.themeColors ? control.themeColors.primary : "#A8C7FA"
        }
        border.color: control.variant === "outlined" ? (control.themeColors ? control.themeColors.outline : "#938F99") : "transparent"
        border.width: control.variant === "outlined" ? 1 : 0

        Behavior on color {
            ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
        }

        scale: control.down ? 0.96 : 1.0
        Behavior on scale {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
    }

    HoverHandler {
        cursorShape: Qt.PointingHandCursor
    }
}
