import QtQuick
import QtQuick.Effects

Item {
    id: thumbnail
    required property var themeColors
    property url source

    implicitWidth: 72
    implicitHeight: 72

    Rectangle {
        id: shadowSource
        width: 64
        height: 64
        anchors.centerIn: parent
        radius: 16
        color: thumbnail.themeColors.raised
    }

    MultiEffect {
        anchors.fill: parent
        source: shadowSource
        autoPaddingEnabled: true
        shadowEnabled: true
        shadowColor: thumbnail.themeColors.cardShadow
        shadowBlur: 0.75
        shadowOpacity: 0.95
        shadowHorizontalOffset: 0
        shadowVerticalOffset: 1
        shadowScale: 1.05
    }

    Rectangle {
        id: thumbnailPlaceholder
        anchors.fill: shadowSource
        radius: shadowSource.radius
        color: thumbnail.themeColors.raised
    }

    Image {
        id: artwork
        anchors.fill: thumbnailPlaceholder
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
        radius: Math.max(0, thumbnailPlaceholder.radius - 1)
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
    }

    Rectangle {
        anchors.fill: thumbnailPlaceholder
        radius: thumbnailPlaceholder.radius
        color: "transparent"
        border.color: thumbnail.themeColors.border
        border.width: 1
    }

    Text {
        anchors.centerIn: thumbnailPlaceholder
        visible: artwork.status !== Image.Ready
        text: "♫"
        color: thumbnail.themeColors.accent
        font.pixelSize: 22
    }
}
