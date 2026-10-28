import QtQuick

// Thicker Material 3 Equalizer Bars showing active track playback
Item {
    id: equalizer
    property var themeColors: null
    property color color: themeColors ? themeColors.primary : "#A8C7FA"
    property bool running: true
    property real barWidth: Math.max(3.5, width / 4.2)

    implicitWidth: 20
    implicitHeight: 20

    Row {
        anchors.centerIn: parent
        spacing: Math.max(1.5, equalizer.width * 0.08)

        Repeater {
            model: [
                { delay: 0, low: 0.25, high: 1.0 },
                { delay: 120, low: 0.45, high: 0.82 },
                { delay: 60, low: 0.20, high: 0.68 }
            ]

            delegate: Rectangle {
                required property var modelData
                width: equalizer.barWidth
                height: equalizer.height * (equalizer.running ? 0.35 : 0.45)
                radius: width / 2
                color: equalizer.color
                anchors.verticalCenter: parent.verticalCenter

                SequentialAnimation on height {
                    running: equalizer.running && equalizer.visible
                    loops: Animation.Infinite
                    PauseAnimation { duration: modelData.delay }
                    NumberAnimation {
                        from: equalizer.height * modelData.low
                        to: equalizer.height * modelData.high
                        duration: equalizer.themeColors ? equalizer.themeColors.motion.expressiveFastSpatialDuration : 150
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: equalizer.themeColors ? equalizer.themeColors.motion.expressiveFastSpatialCurve : [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]
                    }
                    NumberAnimation {
                        from: equalizer.height * modelData.high
                        to: equalizer.height * modelData.low
                        duration: equalizer.themeColors ? equalizer.themeColors.motion.expressiveFastSpatialDuration : 150
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: equalizer.themeColors ? equalizer.themeColors.motion.expressiveFastSpatialCurve : [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]
                    }
                }
            }
        }
    }
}
