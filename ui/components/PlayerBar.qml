import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

Rectangle {
    id: playerBar
    required property var bridge
    required property var themeColors

    signal queueRequested

    objectName: "playerDock"
    height: 104
    color: themeColors.panel
    border.color: themeColors.border

    GridLayout {
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 24
        columns: 3
        columnSpacing: 12

        RowLayout {
            objectName: "playerInfo"
            Layout.column: 0
            Layout.preferredWidth: playerBar.width * 0.30
            Layout.minimumWidth: playerBar.width * 0.30
            Layout.maximumWidth: playerBar.width * 0.30
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            spacing: 12

            Rectangle {
                id: nowPlayingArtworkCard
                Layout.preferredWidth: 58
                Layout.preferredHeight: 58
                radius: 16
                color: playerBar.themeColors.raised
                clip: true
                layer.enabled: true
                layer.smooth: true

                Image {
                    id: nowPlayingArtwork
                    anchors.fill: parent
                    source: playerBar.bridge.nowPlaying.thumbnail || ""
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    cache: true
                    visible: false
                }

                Rectangle {
                    id: nowPlayingMask
                    anchors.fill: parent
                    radius: nowPlayingArtworkCard.radius
                    color: "white"
                    visible: false
                    layer.enabled: true
                }

                MultiEffect {
                    anchors.fill: parent
                    source: nowPlayingArtwork
                    maskEnabled: true
                    maskSource: nowPlayingMask
                    visible: nowPlayingArtwork.status === Image.Ready
                }

                Text {
                    anchors.centerIn: parent
                    visible: nowPlayingArtwork.status !== Image.Ready
                    text: "♫"
                    color: playerBar.themeColors.accent
                    font.pixelSize: 25
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                spacing: 2
                Label {
                    Layout.fillWidth: true
                    text: playerBar.bridge.nowPlaying.title || "Nothing playing"
                    color: playerBar.themeColors.text
                    elide: Text.ElideRight
                    font.pixelSize: 13
                    font.weight: Font.Medium
                }
                Label {
                    Layout.fillWidth: true
                    text: playerBar.bridge.nowPlaying.artist || "Choose a song to begin"
                    color: playerBar.themeColors.muted
                    elide: Text.ElideRight
                    font.pixelSize: 11
                }
            }
        }

        ColumnLayout {
            Layout.column: 1
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignCenter
            spacing: 2

            RowLayout {
                objectName: "transportControls"
                Layout.alignment: Qt.AlignHCenter
                spacing: 8
                ThemeToolButton {
                    themeColors: playerBar.themeColors
                    text: "‹"
                    font.pixelSize: 28
                    ToolTip.text: "Previous track"
                    ToolTip.visible: hovered
                    onClicked: playerBar.bridge.previousTrack()
                }
                Button {
                    implicitWidth: 50
                    implicitHeight: 50
                    enabled: !!playerBar.bridge.nowPlaying.title
                    text: playerBar.bridge.loading ? "…"
                        : playerBar.bridge.playing ? "Ⅱ" : "▶"
                    contentItem: Text {
                        text: parent.text
                        color: parent.enabled
                            ? playerBar.themeColors.accentText
                            : playerBar.themeColors.disabledText
                        font.pixelSize: 19
                        font.weight: Font.Bold
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 25
                        color: parent.enabled
                            ? playerBar.themeColors.accent
                            : playerBar.themeColors.disabledSurface
                        border.color: parent.activeFocus
                            ? playerBar.themeColors.text : "transparent"
                        border.width: parent.activeFocus ? 2 : 0
                        scale: parent.down ? 0.94 : 1
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        Behavior on color { ColorAnimation { duration: 180 } }
                    }
                    ToolTip.text: playerBar.bridge.playing ? "Pause" : "Play"
                    ToolTip.visible: hovered
                    onClicked: playerBar.bridge.togglePlayback()
                }
                ThemeToolButton {
                    themeColors: playerBar.themeColors
                    text: "›"
                    font.pixelSize: 28
                    ToolTip.text: "Next track"
                    ToolTip.visible: hovered
                    onClicked: playerBar.bridge.nextTrack()
                }
            }

            ThemeSlider {
                themeColors: playerBar.themeColors
                Layout.fillWidth: true
                Layout.preferredHeight: 22
                from: 0
                to: 1
                value: playerBar.bridge.durationMs > 0
                    ? playerBar.bridge.positionMs / playerBar.bridge.durationMs : 0
                onMoved: playerBar.bridge.seek(value)
            }
        }

        RowLayout {
            objectName: "playerActions"
            Layout.column: 2
            Layout.preferredWidth: playerBar.width * 0.30
            Layout.minimumWidth: playerBar.width * 0.30
            Layout.maximumWidth: playerBar.width * 0.30
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            spacing: 4

            ThemeToolButton {
                themeColors: playerBar.themeColors
                text: playerBar.bridge.liked ? "♥" : "♡"
                iconColor: playerBar.bridge.liked
                    ? playerBar.themeColors.accent : playerBar.themeColors.text
                font.pixelSize: 22
                ToolTip.text: "Like current track"
                ToolTip.visible: hovered
                onClicked: playerBar.bridge.likeSong(playerBar.bridge.nowPlaying)
            }
            ThemeToolButton {
                themeColors: playerBar.themeColors
                visible: playerBar.width >= 1000
                text: "◉"
                font.pixelSize: 18
                ToolTip.text: "Start a radio station"
                ToolTip.visible: hovered
                onClicked: playerBar.bridge.startStation(playerBar.bridge.nowPlaying)
            }
            ThemeToolButton {
                themeColors: playerBar.themeColors
                text: "≡"
                font.pixelSize: 22
                ToolTip.text: "Playback queue"
                ToolTip.visible: hovered
                onClicked: playerBar.queueRequested()
            }
            ThemeToolButton {
                themeColors: playerBar.themeColors
                visible: playerBar.width >= 1000
                text: playerBar.bridge.loopEnabled ? "↻" : "⟳"
                iconColor: playerBar.bridge.loopEnabled
                    ? playerBar.themeColors.accent : playerBar.themeColors.text
                font.pixelSize: 20
                ToolTip.text: "Repeat current track"
                ToolTip.visible: hovered
                onClicked: playerBar.bridge.toggleLoop()
            }
            ThemeSlider {
                themeColors: playerBar.themeColors
                Layout.preferredWidth: playerBar.width >= 1000 ? 100 : 68
                Layout.maximumWidth: playerBar.width * 0.36
                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                from: 0
                to: 1
                value: playerBar.bridge.volume
                ToolTip.text: "Volume"
                ToolTip.visible: hovered
                onMoved: playerBar.bridge.setVolume(value)
            }
        }
    }
}
