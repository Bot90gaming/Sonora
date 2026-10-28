import QtQuick

Item {
    id: stateLayer
    property var motion: null
    property int radius: 0
    property color stateColor: "#E2E2E9"
    property bool hovered: false
    property bool pressed: false
    property bool focused: false

    Rectangle {
        anchors.fill: parent
        radius: stateLayer.radius
        color: stateLayer.stateColor
        opacity: stateLayer.pressed ? 0.12 : (stateLayer.hovered ? 0.08 : (stateLayer.focused ? 0.10 : 0.0))

        Behavior on opacity {
            NumberAnimation {
                duration: stateLayer.motion ? stateLayer.motion.expressiveFastEffectsDuration : 150
                easing.type: Easing.BezierSpline
                easing.bezierCurve: stateLayer.motion ? stateLayer.motion.expressiveFastEffectsCurve : [0.2, 0.0, 0.0, 1.0, 1.0, 1.0]
            }
        }
    }
}
