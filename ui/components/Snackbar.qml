import QtQuick

// M3 snackbar. Enters with a short fade/slide and exits with an accelerated
// fade; the surface is the inverse surface role so it separates from the app.
Rectangle {
    id: snackbar
    required property var themeColors
    property string message: ""
    property bool shown: false
    property real maxWidth: 460

    implicitWidth: Math.min(maxWidth, snackText.implicitWidth + 32)
    implicitHeight: snackText.implicitHeight + 28
    width: implicitWidth
    height: implicitHeight
    radius: themeColors.shape.small
    color: themeColors.inverseSurface
    opacity: shown ? 1 : 0

    transform: Translate {
        y: snackbar.shown ? 0 : 12
        Behavior on y {
            NumberAnimation {
                duration: snackbar.themeColors.motion.expressiveFastSpatialDuration
                easing.type: Easing.BezierSpline
                easing.bezierCurve: snackbar.themeColors.motion.expressiveFastSpatialCurve
            }
        }
    }

    Behavior on opacity {
        NumberAnimation {
            duration: snackbar.shown
                ? snackbar.themeColors.motion.expressiveDefaultEffectsDuration
                : snackbar.themeColors.motion.expressiveFastEffectsDuration
            easing.type: Easing.BezierSpline
            easing.bezierCurve: snackbar.shown
                ? snackbar.themeColors.motion.expressiveDefaultEffectsCurve
                : snackbar.themeColors.motion.expressiveFastEffectsCurve
        }
    }

    Text {
        id: snackText
        anchors.centerIn: parent
        width: Math.min(implicitWidth, snackbar.maxWidth - 32)
        text: snackbar.message
        color: snackbar.themeColors.inverseOnSurface
        font.family: snackbar.themeColors.fontFamily
        font.pixelSize: snackbar.themeColors.type.bodyMedium
        font.letterSpacing: snackbar.themeColors.type.trackingBodyMedium
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
    }
}
