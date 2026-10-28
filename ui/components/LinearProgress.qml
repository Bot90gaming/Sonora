import QtQuick

// Material 3 Thicker Linear Progress Indicator
Item {
    id: progress
    property var themeColors: null
    property real value: -1
    property color color: themeColors ? themeColors.primary : "#A8C7FA"
    property color trackColor: "transparent"
    property int thickness: 6

    implicitHeight: thickness
    height: thickness
    clip: true

    // Background Track
    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: progress.trackColor !== "transparent"
            ? progress.trackColor
            : (progress.themeColors ? Qt.rgba(progress.themeColors.onSurface.r, progress.themeColors.onSurface.g, progress.themeColors.onSurface.b, 0.15) : "#20FFFFFF")
    }

    // Determinate Track
    Item {
        anchors.fill: parent
        visible: progress.value >= 0

        Rectangle {
            id: active
            height: parent.height
            radius: height / 2
            color: progress.color
            width: Math.max(progress.height,
                progress.width * Math.min(1, Math.max(0, progress.value)))
            Behavior on width {
                NumberAnimation {
                    duration: 120
                    easing.type: Easing.Linear
                }
            }
        }
    }

    // Indeterminate Track: traveling fluid pill segment
    Rectangle {
        id: indeterminate
        visible: progress.value < 0
        width: Math.max(48, progress.width * 0.35)
        height: parent.height
        radius: height / 2
        color: progress.color

        NumberAnimation on x {
            running: progress.value < 0 && progress.visible
            from: -indeterminate.width
            to: progress.width
            duration: 1200
            loops: Animation.Infinite
            easing.type: Easing.BezierSpline
            easing.bezierCurve: progress.themeColors ? progress.themeColors.motion.expressiveSlowSpatialCurve : [0.05, 0.7, 0.1, 1.0, 1.0, 1.0]
        }
    }
}
