import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

ColumnLayout {
    id: carousel
    required property var model
    required property var service
    required property var themeColors
    objectName: "featuredCarousel"
    Layout.minimumHeight: 286
    Layout.preferredHeight: 286
    Layout.maximumHeight: 286
    Layout.fillWidth: true
    Layout.fillHeight: false
    implicitHeight: 286
    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Label {
            Layout.fillWidth: true
            text: "Top Music"
            color: carousel.themeColors.text
            font.pixelSize: 21
            font.weight: Font.DemiBold
        }
        Label {
            visible: carousel.model.length === 0
            text: "Your recommendations will appear here"
            color: carousel.themeColors.muted
            font.pixelSize: 12
        }
        ThemeToolButton {
            themeColors: carousel.themeColors
            text: "‹"
            enabled: cards.currentIndex > 0
            onClicked: cards.decrementCurrentIndex()
        }
        ThemeToolButton {
            themeColors: carousel.themeColors
            text: "›"
            enabled: cards.currentIndex < cards.count - 1
            onClicked: cards.incrementCurrentIndex()
        }
    }

    Item {
        Layout.fillWidth: true
        Layout.fillHeight: true

        ListView {
            id: cards
            objectName: "featuredCards"
            anchors.fill: parent
            orientation: ListView.Horizontal
            model: carousel.model
            clip: true
            spacing: -74
            boundsBehavior: Flickable.StopAtBounds
            snapMode: ListView.SnapToItem
            highlightMoveDuration: 320
            flickDeceleration: 1800
            maximumFlickVelocity: 1200
            preferredHighlightBegin: width / 2 - 92
            preferredHighlightEnd: width / 2 + 92
            highlightRangeMode: ListView.StrictlyEnforceRange
            highlightFollowsCurrentItem: true
            currentIndex: count > 0 ? Math.floor(count / 2) : -1
            header: Item { width: Math.max(0, cards.width / 2 - 92) }
            footer: Item { width: Math.max(0, cards.width / 2 - 92) }

            delegate: Item {
                required property var modelData
                required property int index
                objectName: "featuredCard_%1".arg(index)
                width: 184
                height: cards.height
                z: index === cards.currentIndex ? 10 : 1

                Item {
                    id: cardWrapper
                    anchors.centerIn: parent
                    width: 184
                    height: 224
                    scale: index === cards.currentIndex ? 1 : 0.84
                    Behavior on scale {
                        NumberAnimation {
                            duration: 320
                            easing.type: Easing.OutCubic
                        }
                    }

                    Rectangle {
                        id: cardShadowBase
                        anchors.fill: parent
                        radius: 20
                        color: carousel.themeColors.raised
                        visible: false
                    }

                    MultiEffect {
                        anchors.fill: cardShadowBase
                        source: cardShadowBase
                        autoPaddingEnabled: true
                        shadowEnabled: true
                        shadowColor: carousel.themeColors.cardShadow
                        shadowBlur: index === cards.currentIndex ? 0.85 : 0.6
                        shadowOpacity: index === cards.currentIndex ? 1.0 : 0.75
                        shadowHorizontalOffset: 0
                        shadowVerticalOffset: index === cards.currentIndex ? 3 : 2
                        shadowScale: index === cards.currentIndex ? 1.06 : 1.03
                        z: 0
                    }

                    Rectangle {
                        id: artCard
                        objectName: "featuredArtwork"
                        anchors.fill: parent
                        radius: 20
                        clip: true
                        color: carousel.themeColors.raised
                        layer.enabled: true
                        layer.smooth: true
                        z: 1

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
                            radius: artCard.radius
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
                        }

                        Text {
                            anchors.centerIn: parent
                            visible: artwork.status !== Image.Ready
                            text: "♫"
                            color: carousel.themeColors.accent
                            font.pixelSize: 42
                        }

                        Rectangle {
                            anchors.fill: parent
                            radius: artCard.radius
                            color: "#99000000"
                            opacity: index === cards.currentIndex ? 0.62 : 0.08
                            Behavior on opacity {
                                NumberAnimation {
                                    duration: 260
                                    easing.type: Easing.OutCubic
                                }
                            }
                        }

                        Rectangle {
                            anchors.fill: parent
                            radius: artCard.radius
                            color: "transparent"
                            border.color: index === cards.currentIndex
                                ? carousel.themeColors.border : "transparent"
                            border.width: 1
                            z: 2
                        }

                        Column {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.margins: 14
                            spacing: 5
                            visible: index === cards.currentIndex
                            z: 3
                            Label {
                                width: parent.width
                                text: modelData.title || "Unknown title"
                                color: "#ffffff"
                                font.pixelSize: 17
                                font.weight: Font.DemiBold
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }
                            Label {
                                width: parent.width
                                text: modelData.artist || "YouTube Music"
                                color: "#eeeeee"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            z: 4
                            onClicked: {
                                if (index === cards.currentIndex)
                                    carousel.service.playSong(modelData)
                                else
                                    cards.currentIndex = index
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            anchors.left: cards.left
            anchors.top: cards.top
            anchors.bottom: cards.bottom
            width: 104
            z: 20
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0; color: carousel.themeColors.background }
                GradientStop { position: 1; color: carousel.themeColors.edgeFadeTransparent }
            }
        }

        Rectangle {
            anchors.right: cards.right
            anchors.top: cards.top
            anchors.bottom: cards.bottom
            width: 104
            z: 20
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0; color: carousel.themeColors.edgeFadeTransparent }
                GradientStop { position: 1; color: carousel.themeColors.background }
            }
        }
    }
}
