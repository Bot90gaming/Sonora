import QtQuick

// Modern Material 3 Indeterminate Circular Loading Indicator
Item {
    id: indicator
    property var themeColors: null
    property color color: themeColors ? themeColors.primary : "#A8C7FA"
    property color trackColor: themeColors
        ? Qt.rgba(themeColors.onSurface.r, themeColors.onSurface.g, themeColors.onSurface.b, 0.12)
        : Qt.rgba(1, 1, 1, 0.12)
    property real strokeWidth: Math.max(3.5, Math.min(width, height) * 0.13)
    property bool running: true

    implicitWidth: 32
    implicitHeight: 32

    property real angleOffset: 0
    property real sweepAngle: 60
    property real corePulse: 1.0

    NumberAnimation on angleOffset {
        running: indicator.running && indicator.visible
        loops: Animation.Infinite
        from: 0
        to: 360
        duration: 1300
    }

    SequentialAnimation on sweepAngle {
        running: indicator.running && indicator.visible
        loops: Animation.Infinite
        NumberAnimation {
            from: 35
            to: 285
            duration: 800
            easing.type: Easing.InOutQuad
        }
        NumberAnimation {
            from: 285
            to: 35
            duration: 800
            easing.type: Easing.InOutQuad
        }
    }

    SequentialAnimation on corePulse {
        running: indicator.running && indicator.visible && indicator.width >= 28
        loops: Animation.Infinite
        NumberAnimation {
            from: 0.7
            to: 1.2
            duration: 650
            easing.type: Easing.InOutSine
        }
        NumberAnimation {
            from: 1.2
            to: 0.7
            duration: 650
            easing.type: Easing.InOutSine
        }
    }

    onAngleOffsetChanged: cvs.requestPaint()
    onSweepAngleChanged: cvs.requestPaint()
    onCorePulseChanged: if (indicator.width >= 28) cvs.requestPaint()
    onColorChanged: cvs.requestPaint()
    onTrackColorChanged: cvs.requestPaint()

    Canvas {
        id: cvs
        anchors.fill: parent
        antialiasing: true

        onPaint: {
            let ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            let cx = width / 2
            let cy = height / 2
            let r = Math.max(2, (Math.min(width, height) - indicator.strokeWidth) / 2)
            if (r <= 2) return

            // 1. Inactive background guide track
            ctx.beginPath()
            ctx.arc(cx, cy, r, 0, Math.PI * 2)
            ctx.strokeStyle = indicator.trackColor
            ctx.lineWidth = indicator.strokeWidth
            ctx.stroke()

            // 2. Dynamic Expanding/Contracting Active Arc
            let start = (indicator.angleOffset - 90) * Math.PI / 180
            let end = start + (indicator.sweepAngle * Math.PI / 180)

            ctx.beginPath()
            ctx.arc(cx, cy, r, start, end)
            ctx.strokeStyle = indicator.color
            ctx.lineWidth = indicator.strokeWidth
            ctx.lineCap = "round"
            ctx.stroke()

            // 3. Concentric Center Dot for larger loaders
            if (indicator.width >= 32) {
                let dotR = Math.max(1.5, indicator.strokeWidth * 0.75 * indicator.corePulse)
                ctx.beginPath()
                ctx.arc(cx, cy, dotR, 0, Math.PI * 2)
                ctx.fillStyle = indicator.color
                ctx.fill()
            }
        }
    }
}
