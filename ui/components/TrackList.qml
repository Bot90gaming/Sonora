import QtQuick
import QtQuick.Controls
import QtQuick.Effects
import QtQuick.Layouts

ListView {
    id: trackList
    required property var themeColors
    required property var service

    function formatDuration(seconds) {
        const duration = Math.max(0, Number(seconds) || 0)
        return Math.floor(duration / 60) + ":"
            + String(Math.floor(duration % 60)).padStart(2, "0")
    }

    clip: true
    spacing: 8
    boundsBehavior: Flickable.StopAtBounds

    ScrollBar.vertical: ThemeScrollBar {
        themeColors: trackList.themeColors
        policy: ScrollBar.AsNeeded
    }

    delegate: Item {
        id: trackDelegate
        required property var modelData
        width: trackList.width - 10
        height: 88

        Rectangle {
            id: shadowSource
            anchors.fill: parent
            radius: 22
            color: trackList.themeColors.surface
        }
        MultiEffect {
            anchors.fill: shadowSource
            source: shadowSource
            shadowEnabled: true
            shadowColor: trackList.themeColors.cardShadow
            shadowBlur: 0.55
            shadowOpacity: 0.9
            shadowVerticalOffset: 4
            z: 0
        }

        Rectangle {
            id: trackRow
            anchors.fill: parent
            radius: 22
            color: rowMouse.containsMouse
                ? trackList.themeColors.raised : trackList.themeColors.surface
            border.color: trackList.themeColors.border
            Behavior on color { ColorAnimation { duration: 150 } }
            z: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 12
                spacing: 12

                TrackThumbnail {
                    Layout.preferredWidth: 72
                    Layout.preferredHeight: 72
                    themeColors: trackList.themeColors
                    source: trackDelegate.modelData.thumbnail || ""
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Label {
                        Layout.fillWidth: true
                        text: trackDelegate.modelData.title || "Unknown title"
                        color: trackList.themeColors.text
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        elide: Text.ElideRight
                    }
                    Label {
                        Layout.fillWidth: true
                        text: trackDelegate.modelData.artist || "Unknown artist"
                        color: trackList.themeColors.muted
                        font.pixelSize: 12
                        elide: Text.ElideRight
                    }
                }

                Label {
                    text: trackList.formatDuration(trackDelegate.modelData.duration)
                    color: trackList.themeColors.muted
                    font.pixelSize: 11
                    Layout.rightMargin: 4
                }

                ShellButton {
                    text: "Play"
                    primary: true
                    themeColors: trackList.themeColors
                    onClicked: {
                        if (trackDelegate.modelData.videoId)
                            trackList.service.playSong(trackDelegate.modelData)
                        else
                            trackList.service.openCollection(trackDelegate.modelData)
                    }
                }

                ThemeToolButton {
                    themeColors: trackList.themeColors
                    text: "+"
                    font.pixelSize: 18
                    ToolTip.visible: hovered
                    ToolTip.text: "Add to queue"
                    onClicked: trackList.service.enqueue(trackDelegate.modelData)
                }

                ThemeToolButton {
                    themeColors: trackList.themeColors
                    text: "↓"
                    font.pixelSize: 18
                    ToolTip.visible: hovered
                    ToolTip.text: "Download"
                    onClicked: trackList.service.downloadSong(trackDelegate.modelData)
                }
            }

            MouseArea {
                id: rowMouse
                anchors.fill: parent
                hoverEnabled: true
                z: -1
            }
        }
    }
}
