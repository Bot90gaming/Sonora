import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

// Symmetrical 5-Card 3D Stacked Coverflow Deck
// Designed according to asset/song 1.png specification
ColumnLayout {
    id: carousel
    objectName: "featuredCarousel"
    required property var model
    required property var service
    property var themeColors: null

    readonly property var colors: themeColors || ({
        isDark: true,
        fontFamily: "sans-serif",
        onSurface: "#F4F4FA",
        onSurfaceVariant: "#C4C8D4",
        surfaceContainerHigh: "#282F3B",
        surfaceContainerLow: "#1C212A",
        surfaceContainer: "#222731",
        surface: "#121418",
        primary: "#A0CAFD",
        onPrimary: "#003258",
        outline: "#444B57",
        outlineVariant: "#2E3540",
        shadow: "#000000",
        type: {
            titleLarge: 22,
            titleMedium: 16,
            bodySmall: 12,
            weightMedium: Font.Medium,
            weightDemiBold: Font.DemiBold,
            trackingTitleLarge: 0
        },
        shape: {
            extraLarge: 36
        },
        motion: {
            expressiveDefaultSpatialDuration: 350,
            expressiveFastSpatialDuration: 200,
            expressiveDefaultEffectsDuration: 250,
            expressiveFastEffectsDuration: 180,
            expressiveDefaultSpatialCurve: [0.2, 0.0, 0, 1.0],
            expressiveFastSpatialCurve: [0.2, 0.0, 0, 1.0],
            expressiveDefaultEffectsCurve: [0.2, 0.0, 0, 1.0],
            expressiveFastEffectsCurve: [0.2, 0.0, 0, 1.0]
        }
    })

    readonly property int count: model ? (model.length !== undefined ? model.length : (model.count !== undefined ? model.count : 0)) : 0
    property int currentIndex: 0

    onCountChanged: {
        if (count > 0 && (currentIndex < 0 || currentIndex >= count))
            currentIndex = Math.floor(count / 2)
    }

    function decrement() {
        if (count <= 1) return
        currentIndex = (currentIndex - 1 + count) % count
    }

    function increment() {
        if (count <= 1) return
        currentIndex = (currentIndex + 1) % count
    }

    Layout.minimumHeight: 310
    Layout.preferredHeight: 330
    Layout.maximumHeight: 350
    Layout.fillWidth: true
    Layout.fillHeight: false
    implicitHeight: 330
    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Label {
            Layout.fillWidth: true
            text: "Top Music"
            color: carousel.colors.onSurface
            font.family: carousel.colors.fontFamily
            font.pixelSize: carousel.colors.type.titleLarge
            font.weight: carousel.colors.type.weightMedium
            font.letterSpacing: carousel.colors.type.trackingTitleLarge
        }
        Label {
            visible: carousel.count === 0
            text: "Your recommendations will appear here"
            color: carousel.colors.onSurfaceVariant
            font.family: carousel.colors.fontFamily
            font.pixelSize: carousel.colors.type.bodySmall
        }
    }

    Item {
        id: deckArea
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredHeight: 280
        Layout.minimumHeight: 260
        implicitHeight: 280

        readonly property real cardW: Math.min(260, Math.max(220, deckArea.width * 0.28))
        readonly property real cardH: Math.min(280, Math.max(200, deckArea.height - 12))
        readonly property real centerX: (deckArea.width - cardW) / 2
        readonly property real centerY: (deckArea.height - cardH) / 2

        // Background click/drag area to swipe through cards
        MouseArea {
            anchors.fill: parent
            z: 0
            property real startX: 0
            onPressed: (mouse) => startX = mouse.x
            onReleased: (mouse) => {
                let dx = mouse.x - startX
                if (Math.abs(dx) > 40) {
                    if (dx < 0) carousel.increment()
                    else carousel.decrement()
                }
            }
        }

        // Empty state when no items loaded
        Rectangle {
            anchors.centerIn: parent
            width: deckArea.cardW
            height: deckArea.cardH
            radius: 36
            visible: carousel.count === 0
            color: carousel.colors.isDark ? carousel.colors.surfaceContainerLow : "#DDE3EA"
            border.color: carousel.colors.outlineVariant
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 12
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "library_music"
                    color: carousel.colors.onSurfaceVariant
                    font.family: "Material Symbols Rounded"
                    font.pixelSize: 44
                }
                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "No songs available"
                    color: carousel.colors.onSurfaceVariant
                    font.family: carousel.colors.fontFamily
                    font.pixelSize: carousel.colors.type.bodySmall
                }
            }
        }

        // 5-Card Stacked Coverflow Deck
        Repeater {
            id: cardsRepeater
            model: carousel.model

            delegate: Item {
                id: card
                required property var modelData
                required property int index

                readonly property int offset: {
                    if (carousel.count === 0) return 0
                    let diff = index - carousel.currentIndex
                    let n = carousel.count
                    if (n >= 3) {
                        if (diff > n / 2) diff -= n
                        else if (diff < -n / 2) diff += n
                    }
                    return diff
                }

                width: deckArea.cardW
                height: deckArea.cardH

                x: offset === 0 ? deckArea.centerX :
                   offset === -1 ? deckArea.centerX - 135 :
                   offset === 1 ? deckArea.centerX + 135 :
                   offset === -2 ? deckArea.centerX - 245 :
                   offset === 2 ? deckArea.centerX + 245 :
                   (offset < -2 ? deckArea.centerX - 360 : deckArea.centerX + 360)

                y: deckArea.centerY

                scale: offset === 0 ? 1.0 :
                       Math.abs(offset) === 1 ? 0.85 :
                       Math.abs(offset) === 2 ? 0.72 : 0.58

                z: offset === 0 ? 10 :
                   Math.abs(offset) === 1 ? 5 :
                   Math.abs(offset) === 2 ? 2 : 0

                opacity: Math.abs(offset) <= 2 ? (offset === 0 ? 1.0 : (Math.abs(offset) === 1 ? 0.85 : 0.68)) : 0.0
                visible: opacity > 0.01

                Behavior on x {
                    NumberAnimation {
                        duration: carousel.colors.motion.expressiveDefaultSpatialDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: carousel.colors.motion.expressiveDefaultSpatialCurve
                    }
                }
                Behavior on scale {
                    NumberAnimation {
                        duration: carousel.colors.motion.expressiveDefaultSpatialDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: carousel.colors.motion.expressiveDefaultSpatialCurve
                    }
                }
                Behavior on opacity {
                    NumberAnimation {
                        duration: carousel.colors.motion.expressiveDefaultEffectsDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: carousel.colors.motion.expressiveDefaultEffectsCurve
                    }
                }

                // Ambient drop shadow under cards
                Rectangle {
                    id: cardShadow
                    anchors.fill: parent
                    radius: 36
                    color: "#000000"
                    opacity: offset === 0 ? (carousel.colors.isDark ? 0.45 : 0.16) : (carousel.colors.isDark ? 0.20 : 0.07)
                    scale: offset === 0 ? 1.03 : 1.01
                    y: offset === 0 ? 8 : 4
                    z: 0

                    Behavior on opacity {
                        NumberAnimation { duration: carousel.colors.motion.expressiveDefaultEffectsDuration }
                    }
                    Behavior on scale {
                        NumberAnimation { duration: carousel.colors.motion.expressiveDefaultSpatialDuration }
                    }
                }

                // Card surface container
                Rectangle {
                    id: cardSurface
                    anchors.fill: parent
                    radius: 36
                    color: offset === 0 ?
                               (carousel.colors.isDark ? carousel.colors.surfaceContainerHigh : "#C8D1D9") :
                               (carousel.colors.isDark ? carousel.colors.surfaceContainerLow : "#DDE3EA")
                    border.color: offset === 0 ? carousel.colors.outline : carousel.colors.outlineVariant
                    border.width: 1
                    clip: true
                    z: 1

                    // Artwork image when available
                    Image {
                        id: artwork
                        anchors.fill: parent
                        source: modelData.thumbnail || ""
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        cache: true
                        visible: false
                    }

                    Rectangle {
                        id: artworkMask
                        anchors.fill: parent
                        radius: 36
                        color: "white"
                        visible: false
                        layer.enabled: true
                    }

                    MultiEffect {
                        anchors.fill: parent
                        source: artwork
                        maskEnabled: true
                        maskSource: artworkMask
                        visible: artwork.status === Image.Ready
                        opacity: artwork.status === Image.Ready ? 1 : 0

                        Behavior on opacity {
                            NumberAnimation {
                                duration: carousel.colors.motion.expressiveDefaultEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: carousel.colors.motion.expressiveDefaultEffectsCurve
                            }
                        }
                    }

                    // Fallback / No-Artwork View (matches asset/song 1.png design)
                    Column {
                        anchors.centerIn: parent
                        spacing: 8
                        width: parent.width - 40
                        visible: artwork.status !== Image.Ready

                        Text {
                            text: modelData.title || ("song " + (index + 1))
                            font.family: carousel.colors.fontFamily
                            font.pixelSize: offset === 0 ? 18 : 15
                            font.weight: Font.DemiBold
                            color: carousel.colors.onSurface
                            horizontalAlignment: Text.AlignHCenter
                            width: parent.width
                            elide: Text.ElideRight
                        }

                        Text {
                            text: modelData.artist || "YouTube Music"
                            font.family: carousel.colors.fontFamily
                            font.pixelSize: 13
                            color: carousel.colors.onSurfaceVariant
                            horizontalAlignment: Text.AlignHCenter
                            width: parent.width
                            elide: Text.ElideRight
                        }
                    }

                    // Tonal scrim for high-contrast text overlay when artwork is shown
                    Rectangle {
                        anchors.fill: parent
                        radius: 36
                        visible: artwork.status === Image.Ready
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#00000000" }
                            GradientStop { position: 0.50; color: "#40000000" }
                            GradientStop { position: 1.0; color: "#e6000000" }
                        }
                        opacity: offset === 0 ? 1.0 : 0.65

                        Behavior on opacity {
                            NumberAnimation { duration: carousel.colors.motion.expressiveDefaultEffectsDuration }
                        }
                    }

                    // Text overlay when artwork is active
                    Column {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.leftMargin: 20
                        anchors.rightMargin: offset === 0 ? 64 : 20
                        anchors.bottomMargin: 18
                        spacing: 4
                        visible: artwork.status === Image.Ready
                        opacity: offset === 0 ? 1.0 : 0.85

                        Behavior on opacity {
                            NumberAnimation { duration: carousel.colors.motion.expressiveDefaultEffectsDuration }
                        }

                        Label {
                            width: parent.width
                            text: modelData.title || ""
                            color: "#ffffff"
                            font.family: carousel.colors.fontFamily
                            font.pixelSize: offset === 0 ? 16 : 14
                            font.weight: Font.DemiBold
                            elide: Text.ElideRight
                        }
                        Label {
                            width: parent.width
                            text: modelData.artist || "YouTube Music"
                            color: "#d0d4dc"
                            font.family: carousel.colors.fontFamily
                            font.pixelSize: offset === 0 ? 12 : 11
                            elide: Text.ElideRight
                        }
                    }

                    // Play button affordance on center card
                    Rectangle {
                        id: playBtn
                        visible: offset === 0 && artwork.status === Image.Ready
                        width: 44
                        height: 44
                        radius: 22
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 14
                        color: carousel.colors.primary
                        scale: playBtnMouse.pressed ? 0.90 : (playBtnMouse.containsMouse ? 1.08 : 1.0)
                        z: 4

                        Behavior on scale {
                            NumberAnimation { duration: 150; easing.type: Easing.OutBack }
                        }

                        Text {
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: 1
                            text: "play_arrow"
                            font.family: "Material Symbols Rounded"
                            font.pixelSize: 24
                            color: carousel.colors.onPrimary
                        }

                        MouseArea {
                            id: playBtnMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: carousel.service.playSong(modelData)
                        }
                    }

                    // Card gesture & click mouse area
                    MouseArea {
                        anchors.fill: parent
                        z: 2
                        cursorShape: Qt.PointingHandCursor
                        property real startX: 0
                        property real startY: 0
                        onPressed: (mouse) => {
                            startX = mouse.x
                            startY = mouse.y
                        }
                        onReleased: (mouse) => {
                            let dx = mouse.x - startX
                            let dy = mouse.y - startY
                            if (Math.abs(dx) > 35) {
                                if (dx < 0) carousel.increment()
                                else carousel.decrement()
                            } else if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
                                if (card.offset === 0) {
                                    carousel.service.playSong(modelData)
                                } else {
                                    carousel.currentIndex = index
                                }
                            }
                        }
                    }
                }
            }
        }

        // Left Flank Circular Navigation Button
        Rectangle {
            id: leftBtn
            width: 58
            height: 58
            radius: 29
            z: 25
            visible: carousel.count > 1
            color: carousel.colors.isDark ? Qt.rgba(0.20, 0.24, 0.32, 0.88) : Qt.rgba(0.92, 0.94, 0.97, 0.92)
            border.color: carousel.colors.isDark ? Qt.rgba(1, 1, 1, 0.25) : Qt.rgba(0, 0, 0, 0.16)
            border.width: 1.2
            scale: leftBtnMouse.pressed ? 0.92 : (leftBtnMouse.containsMouse ? 1.08 : 1.0)

            x: deckArea.centerX - width / 2
            anchors.verticalCenter: deckArea.verticalCenter

            Behavior on scale {
                NumberAnimation { duration: 150; easing.type: Easing.OutBack }
            }

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "#000000"
                opacity: carousel.colors.isDark ? 0.40 : 0.14
                scale: 1.02
                y: 3
                z: -1
            }

            Text {
                anchors.centerIn: parent
                anchors.horizontalCenterOffset: -1
                text: "\u25C0"
                font.pixelSize: 22
                color: carousel.colors.onSurface
            }

            MouseArea {
                id: leftBtnMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: carousel.decrement()
            }
        }

        // Right Flank Circular Navigation Button
        Rectangle {
            id: rightBtn
            width: 58
            height: 58
            radius: 29
            z: 25
            visible: carousel.count > 1
            color: carousel.colors.isDark ? Qt.rgba(0.20, 0.24, 0.32, 0.88) : Qt.rgba(0.92, 0.94, 0.97, 0.92)
            border.color: carousel.colors.isDark ? Qt.rgba(1, 1, 1, 0.25) : Qt.rgba(0, 0, 0, 0.16)
            border.width: 1.2
            scale: rightBtnMouse.pressed ? 0.92 : (rightBtnMouse.containsMouse ? 1.08 : 1.0)

            x: deckArea.centerX + deckArea.cardW - width / 2
            anchors.verticalCenter: deckArea.verticalCenter

            Behavior on scale {
                NumberAnimation { duration: 150; easing.type: Easing.OutBack }
            }

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "#000000"
                opacity: carousel.colors.isDark ? 0.40 : 0.14
                scale: 1.02
                y: 3
                z: -1
            }

            Text {
                anchors.centerIn: parent
                anchors.horizontalCenterOffset: 1
                text: "\u25B6"
                font.pixelSize: 22
                color: carousel.colors.onSurface
            }

            MouseArea {
                id: rightBtnMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: carousel.increment()
            }
        }

        // Mouse Wheel Handler for scrolling deck
        WheelHandler {
            target: deckArea
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            property real accumulator: 0
            onWheel: (event) => {
                let delta = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x
                accumulator += delta
                if (accumulator <= -100) {
                    accumulator = 0
                    carousel.increment()
                } else if (accumulator >= 100) {
                    accumulator = 0
                    carousel.decrement()
                }
            }
        }
    }

    HoverHandler {
        id: carouselHover
    }

    // Ambient auto-advance (advances every 9 seconds when not hovered)
    Timer {
        interval: 9000
        repeat: true
        running: !carouselHover.hovered && carousel.count > 1
        onTriggered: carousel.increment()
    }
}
