import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

ColumnLayout {
    id: playlistGrid
    required property var model
    required property var service
    required property var themeColors
    required property string emptyLabel
    objectName: "playlistGrid"
    spacing: 12

    RowLayout {
        Layout.fillWidth: true
        Label {
            Layout.fillWidth: true
            text: "Play List"
            color: playlistGrid.themeColors.text
            font.pixelSize: 20
            font.weight: Font.DemiBold
        }
        Label {
            visible: playlistGrid.model.length === 0
            text: playlistGrid.emptyLabel
            color: playlistGrid.themeColors.muted
            font.pixelSize: 12
        }
    }

    GridView {
        id: grid
        Layout.fillWidth: true
        Layout.fillHeight: true
        cellWidth: width / 2
        cellHeight: 150
        model: playlistGrid.model
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ThemeScrollBar {
            themeColors: playlistGrid.themeColors
            policy: ScrollBar.AsNeeded
        }
        delegate: Item {
            required property var modelData
            required property int index
            width: grid.cellWidth
            height: grid.cellHeight

            Item {
                anchors.fill: parent
                anchors.rightMargin: 10
                anchors.bottomMargin: 10

                Rectangle {
                    id: playlistShadowBase
                    anchors.fill: parent
                    radius: 17
                    color: playlistGrid.themeColors.raised
                    visible: false
                }

                MultiEffect {
                    anchors.fill: playlistShadowBase
                    source: playlistShadowBase
                    autoPaddingEnabled: true
                    shadowEnabled: true
                    shadowColor: playlistGrid.themeColors.cardShadow
                    shadowBlur: 0.7
                    shadowOpacity: 0.85
                    shadowHorizontalOffset: 0
                    shadowVerticalOffset: 2
                    shadowScale: 1.04
                    z: 0
                }

                Rectangle {
                    id: playlistCard
                    anchors.fill: parent
                    radius: 17
                    clip: true
                    color: playlistGrid.themeColors.raised
                    layer.enabled: true
                    layer.smooth: true
                    z: 1

                    Image {
                        id: playlistArtwork
                        anchors.fill: parent
                        source: modelData.thumbnail || ""
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        cache: true
                        visible: false
                    }

                    Rectangle {
                        id: playlistMask
                        anchors.fill: parent
                        radius: playlistCard.radius
                        color: "white"
                        visible: false
                        layer.enabled: true
                    }

                    MultiEffect {
                        anchors.fill: parent
                        source: playlistArtwork
                        maskEnabled: true
                        maskSource: playlistMask
                        visible: playlistArtwork.status === Image.Ready
                    }

                    Text {
                        anchors.centerIn: parent
                        visible: playlistArtwork.status !== Image.Ready
                        text: "♫"
                        color: playlistGrid.themeColors.accent
                        font.pixelSize: 36
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: playlistCard.radius
                        color: "#88000000"
                    }
                    Label {
                        anchors.centerIn: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        width: parent.width - 16
                        text: modelData.title || "Playlist"
                        color: "#ffffff"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        wrapMode: Text.Wrap
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: playlistGrid.service.openCollection(modelData)
                    }
                }
            }
        }
    }
}
