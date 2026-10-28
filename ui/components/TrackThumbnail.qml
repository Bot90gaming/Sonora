import QtQuick
import QtQuick.Effects

// Rounded M3 list media with a soft tonal placeholder and fade-in artwork.
Item {
    id: thumbnail
    required property var themeColors
    property url source
    property bool playing: false
    property int radius: themeColors.shape.medium
    property int imageSize: 64

    implicitWidth: 72
    implicitHeight: 72

    Rectangle {
        id: placeholder
        width: thumbnail.imageSize
        height: thumbnail.imageSize
        anchors.centerIn: parent
        radius: thumbnail.radius
        color: thumbnail.themeColors.surfaceContainerHigh
    }

    Rectangle {
        id: shadowSource
        anchors.fill: placeholder
        radius: placeholder.radius
        color: thumbnail.themeColors.surfaceContainerHigh
    }

    MultiEffect {
        anchors.fill: shadowSource
        source: shadowSource
        autoPaddingEnabled: true
        shadowEnabled: true
        shadowColor: thumbnail.themeColors.shadow
        shadowBlur: 0.35
        shadowOpacity: 0.55
        shadowHorizontalOffset: 0
        shadowVerticalOffset: 2
        shadowScale: 1.02
        z: 0
    }

    Image {
        id: artwork
        anchors.fill: placeholder
        anchors.margins: 1
        source: thumbnail.source
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: true
        visible: false
    }

    Rectangle {
        id: artworkMask
        anchors.fill: artwork
        radius: Math.max(0, placeholder.radius - 1)
        color: "white"
        visible: false
        layer.enabled: true
    }

    MultiEffect {
        anchors.fill: artwork
        source: artwork
        maskEnabled: true
        maskSource: artworkMask
        visible: artwork.status === Image.Ready
        opacity: artwork.status === Image.Ready ? 1 : 0
        z: 1

        Behavior on opacity {
            NumberAnimation {
                duration: thumbnail.themeColors.motion.expressiveDefaultEffectsDuration
                easing.type: Easing.BezierSpline
                easing.bezierCurve: thumbnail.themeColors.motion.expressiveDefaultEffectsCurve
            }
        }
    }

    Rectangle {
        anchors.fill: placeholder
        radius: placeholder.radius
        color: "transparent"
        border.color: thumbnail.themeColors.outlineVariant
        border.width: 1
        z: 2
    }

    Text {
        anchors.centerIn: placeholder
        visible: artwork.status !== Image.Ready
        text: "music_note"
        color: thumbnail.themeColors.primary
        font.family: "Material Symbols Rounded"
        font.pixelSize: 24
        z: 2
    }

    Item {
        visible: thumbnail.playing
        width: 22
        height: 22
        anchors.right: placeholder.right
        anchors.bottom: placeholder.bottom
        anchors.rightMargin: 3
        anchors.bottomMargin: 3
        z: 3

        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: thumbnail.themeColors.primaryContainer
            border.color: thumbnail.themeColors.surfaceContainerLow
            border.width: 2
        }

        EqualizerBars {
            themeColors: thumbnail.themeColors
            anchors.centerIn: parent
            width: 11
            height: 11
            color: thumbnail.themeColors.onPrimaryContainer
        }
    }
}
