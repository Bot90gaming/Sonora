import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

// Docked player surface styled with Material Design 3 Dark Dynamic Tonal principles.
// Features ambient elevation, squircle morphing play button, and Material Symbols Rounded icons.
Rectangle {
    id: playerBar
    required property var bridge
    required property var themeColors

    signal queueRequested
    signal expandRequested

    objectName: "playerDock"
    height: 104
    color: themeColors.surfaceContainer

    readonly property bool isPlaying: bridge ? bridge.playing : false
    readonly property bool isLoading: bridge ? bridge.loading : false
    readonly property bool isLiked: bridge ? bridge.liked : false
    readonly property bool isLoopEnabled: bridge ? bridge.loopEnabled : false
    readonly property string currentTitle: (bridge && bridge.nowPlaying && bridge.nowPlaying.title) ? bridge.nowPlaying.title : ""
    readonly property string currentArtist: (bridge && bridge.nowPlaying && bridge.nowPlaying.artist) ? bridge.nowPlaying.artist : ""
    readonly property string currentThumbnail: (bridge && bridge.nowPlaying && bridge.nowPlaying.thumbnail) ? bridge.nowPlaying.thumbnail : ""
    readonly property int posMs: bridge ? bridge.positionMs : 0
    readonly property int durMs: bridge ? bridge.durationMs : 0
    readonly property real currentVol: bridge ? bridge.volume : 0.8

    function formatTime(ms) {
        if (!ms || ms <= 0) return "0:00"
        let totalSec = Math.floor(ms / 1000)
        let mins = Math.floor(totalSec / 60)
        let secs = totalSec % 60
        return mins + ":" + (secs < 10 ? "0" : "") + secs
    }

    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: playerBar.themeColors.outlineVariant
    }

    GridLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        columns: 3
        columnSpacing: 16

        // ─── 1. NOW PLAYING TRACK INFO ───────────────────────────
        RowLayout {
            objectName: "playerInfo"
            Layout.column: 0
            Layout.preferredWidth: playerBar.width * 0.28
            Layout.minimumWidth: playerBar.width * 0.28
            Layout.maximumWidth: playerBar.width * 0.32
            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
            spacing: 14

            Rectangle {
                id: nowPlayingArtworkCard
                Layout.preferredWidth: 56
                Layout.preferredHeight: 56
                radius: playerBar.isPlaying ? 16 : 24
                color: playerBar.themeColors.surfaceContainerHigh
                clip: true

                Behavior on radius {
                    NumberAnimation {
                        duration: 400
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: playerBar.themeColors.motion.expressiveDefaultSpatialCurve
                    }
                }

                Image {
                    id: nowPlayingArtwork
                    anchors.fill: parent
                    source: playerBar.currentThumbnail
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    cache: true
                    visible: status === Image.Ready
                }

                Text {
                    anchors.centerIn: parent
                    visible: nowPlayingArtwork.status !== Image.Ready
                    text: "music_note"
                    color: playerBar.themeColors.primary
                    font.family: "Material Symbols Rounded"
                    font.pixelSize: 28
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onClicked: playerBar.expandRequested()
                    ToolTip.text: "Expand player"
                    ToolTip.visible: containsMouse
                }
            }

            ColumnLayout {
                id: playerMeta
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                spacing: 3

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    EqualizerBars {
                        themeColors: playerBar.themeColors
                        Layout.alignment: Qt.AlignVCenter
                        width: 14
                        height: 14
                        visible: playerBar.isPlaying && !!playerBar.currentTitle
                        color: playerBar.themeColors.primary
                    }

                    Label {
                        Layout.fillWidth: true
                        text: playerBar.currentTitle !== "" ? playerBar.currentTitle : "Nothing playing"
                        color: playerBar.themeColors.onSurface
                        elide: Text.ElideRight
                        font.family: playerBar.themeColors.fontFamily
                        font.pixelSize: playerBar.themeColors.type.bodyMedium
                        font.weight: playerBar.themeColors.type.weightMedium
                        font.letterSpacing: playerBar.themeColors.type.trackingBodyMedium
                    }
                }
                Label {
                    Layout.fillWidth: true
                    text: playerBar.currentArtist !== "" ? playerBar.currentArtist : "Choose a song to begin"
                    color: playerBar.themeColors.onSurfaceVariant
                    elide: Text.ElideRight
                    font.family: playerBar.themeColors.fontFamily
                    font.pixelSize: playerBar.themeColors.type.bodySmall
                    font.letterSpacing: playerBar.themeColors.type.trackingBodySmall
                }

                SequentialAnimation {
                    id: metaSwap

                    NumberAnimation {
                        target: playerMeta
                        property: "opacity"
                        to: 0
                        duration: playerBar.themeColors.motion.expressiveFastEffectsDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: playerBar.themeColors.motion.expressiveFastEffectsCurve
                    }
                    NumberAnimation {
                        target: playerMeta
                        property: "opacity"
                        to: 1
                        duration: playerBar.themeColors.motion.expressiveDefaultEffectsDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: playerBar.themeColors.motion.expressiveDefaultEffectsCurve
                    }
                }

                Connections {
                    target: playerBar.bridge
                    ignoreUnknownSignals: true
                    function onNowPlayingChanged() {
                        metaSwap.restart()
                    }
                }
            }
        }

        // ─── 2. PLAYBACK CONTROLS & SEEK BAR ─────────────────────
        ColumnLayout {
            Layout.column: 1
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignCenter
            spacing: 2

            RowLayout {
                objectName: "transportControls"
                Layout.alignment: Qt.AlignHCenter
                spacing: 12

                ThemeToolButton {
                    themeColors: playerBar.themeColors
                    icon: "skip_previous"
                    iconSize: 26
                    ToolTip.text: "Previous track"
                    ToolTip.visible: hovered
                    onClicked: if (playerBar.bridge) playerBar.bridge.previousTrack()
                }

                // MD3 Morphing Squircle Play/Pause button
                Button {
                    id: playButton
                    implicitWidth: 54
                    implicitHeight: 54
                    scale: playButton.down ? 0.92 : (playButton.hovered ? 1.05 : 1.0)
                    enabled: !!playerBar.currentTitle || (playerBar.bridge && playerBar.bridge.homeItems && playerBar.bridge.homeItems.length > 0)
                    hoverEnabled: true

                    Behavior on scale {
                        NumberAnimation {
                            duration: playerBar.themeColors.motion.expressiveFastSpatialDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playerBar.themeColors.motion.expressiveFastSpatialCurve
                        }
                    }

                    background: Rectangle {
                        radius: playButton.down ? 16 : (playerBar.isPlaying ? 18 : 27)
                        color: !playButton.enabled
                            ? playerBar.themeColors.disabledSurface
                            : playerBar.themeColors.primary
                        border.width: playButton.activeFocus ? 2 : 0
                        border.color: playerBar.themeColors.onPrimary

                        Behavior on radius {
                            NumberAnimation {
                                duration: 350
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: playerBar.themeColors.motion.expressiveDefaultSpatialCurve
                            }
                        }
                        Behavior on color {
                            ColorAnimation {
                                duration: playerBar.themeColors.motion.expressiveFastEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: playerBar.themeColors.motion.expressiveFastEffectsCurve
                            }
                        }

                        StateLayer {
                            motion: playerBar.themeColors.motion
                            radius: parent.radius
                            stateColor: playerBar.themeColors.onPrimary
                            hovered: playButton.hovered
                            pressed: playButton.down
                            visible: playButton.enabled
                        }
                    }

                    contentItem: Item {
                        LoadingIndicator {
                            themeColors: playerBar.themeColors
                            anchors.centerIn: parent
                            width: 24
                            height: 24
                            visible: playerBar.isLoading
                            color: playerBar.themeColors.onPrimary
                            running: playerBar.isLoading
                        }
                        Text {
                            anchors.centerIn: parent
                            visible: !playerBar.isLoading
                            text: playerBar.isPlaying ? "pause" : "play_arrow"
                            color: playButton.enabled
                                ? playerBar.themeColors.onPrimary
                                : playerBar.themeColors.disabledText
                            font.family: "Material Symbols Rounded"
                            font.pixelSize: 28
                        }
                    }

                    ToolTip.text: playerBar.isPlaying ? "Pause" : "Play"
                    ToolTip.visible: hovered
                    onClicked: {
                        if (playerBar.bridge) {
                            if (!playerBar.currentTitle && playerBar.bridge.homeItems && playerBar.bridge.homeItems.length > 0) {
                                playerBar.bridge.playSong(playerBar.bridge.homeItems[0])
                            } else {
                                playerBar.bridge.togglePlayback()
                            }
                        }
                    }

                    HoverHandler {
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                ThemeToolButton {
                    themeColors: playerBar.themeColors
                    icon: "skip_next"
                    iconSize: 26
                    ToolTip.text: "Next track"
                    ToolTip.visible: hovered
                    onClicked: if (playerBar.bridge) playerBar.bridge.nextTrack()
                }
            }

            // Seek slider with time display
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: playerBar.formatTime(playerBar.posMs)
                    color: playerBar.themeColors.onSurfaceVariant
                    font.family: playerBar.themeColors.fontFamily
                    font.pixelSize: 11
                    Layout.preferredWidth: 32
                    horizontalAlignment: Text.AlignRight
                }

                ThemeSlider {
                    themeColors: playerBar.themeColors
                    Layout.fillWidth: true
                    Layout.preferredHeight: 26
                    from: 0
                    to: 1
                    value: playerBar.durMs > 0 ? (playerBar.posMs / playerBar.durMs) : 0
                    onMoved: if (playerBar.bridge) playerBar.bridge.seek(value)
                }

                Text {
                    text: playerBar.formatTime(playerBar.durMs)
                    color: playerBar.themeColors.onSurfaceVariant
                    font.family: playerBar.themeColors.fontFamily
                    font.pixelSize: 11
                    Layout.preferredWidth: 32
                    horizontalAlignment: Text.AlignLeft
                }
            }
        }

        // ─── 3. ACTION CONTROLS & VOLUME ─────────────────────────
        RowLayout {
            objectName: "playerActions"
            Layout.column: 2
            Layout.preferredWidth: playerBar.width * 0.30
            Layout.minimumWidth: playerBar.width * 0.28
            Layout.maximumWidth: playerBar.width * 0.32
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            spacing: 2

            ThemeToolButton {
                id: likeButton
                themeColors: playerBar.themeColors
                icon: playerBar.isLiked ? "favorite" : "favorite_border"
                iconColor: playerBar.isLiked
                    ? playerBar.themeColors.error : playerBar.themeColors.onSurfaceVariant
                iconSize: 22
                ToolTip.text: playerBar.isLiked ? "Unlike track" : "Like track"
                ToolTip.visible: hovered
                onClicked: {
                    if (playerBar.bridge) {
                        playerBar.bridge.likeSong(playerBar.bridge.nowPlaying)
                        likePulse.restart()
                    }
                }
            }

            SequentialAnimation {
                id: likePulse
                NumberAnimation {
                    target: likeButton
                    property: "scale"
                    to: 1.25
                    duration: playerBar.themeColors.motion.expressiveFastSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: playerBar.themeColors.motion.expressiveFastSpatialCurve
                }
                NumberAnimation {
                    target: likeButton
                    property: "scale"
                    to: 1
                    duration: playerBar.themeColors.motion.expressiveFastSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: playerBar.themeColors.motion.expressiveFastSpatialCurve
                }
            }

            ThemeToolButton {
                themeColors: playerBar.themeColors
                visible: playerBar.width >= 1000
                icon: "radio"
                iconSize: 20
                ToolTip.text: "Start a radio station"
                ToolTip.visible: hovered
                onClicked: if (playerBar.bridge) playerBar.bridge.startStation(playerBar.bridge.nowPlaying)
            }

            Item {
                implicitWidth: queueBtn.implicitWidth
                implicitHeight: queueBtn.implicitHeight

                ThemeToolButton {
                    id: queueBtn
                    themeColors: playerBar.themeColors
                    icon: "queue_music"
                    iconSize: 22
                    ToolTip.text: "Playback queue"
                    ToolTip.visible: hovered
                    onClicked: playerBar.queueRequested()
                }

                Rectangle {
                    visible: playerBar.bridge && playerBar.bridge.queueItems && playerBar.bridge.queueItems.length > 0
                    anchors.top: parent.top
                    anchors.topMargin: 2
                    anchors.right: parent.right
                    anchors.rightMargin: 2
                    width: Math.max(16, badgeText.implicitWidth + 8)
                    height: 16
                    radius: 8
                    color: playerBar.themeColors.primary

                    Text {
                        id: badgeText
                        anchors.centerIn: parent
                        text: (playerBar.bridge && playerBar.bridge.queueItems) ? playerBar.bridge.queueItems.length : ""
                        color: playerBar.themeColors.onPrimary
                        font.family: playerBar.themeColors.fontFamily
                        font.pixelSize: 10
                        font.weight: Font.Bold
                    }
                }
            }

            ThemeToolButton {
                themeColors: playerBar.themeColors
                visible: playerBar.width >= 1000
                icon: playerBar.isLoopEnabled ? "repeat_one" : "repeat"
                iconColor: playerBar.isLoopEnabled
                    ? playerBar.themeColors.primary : playerBar.themeColors.onSurfaceVariant
                iconSize: 22
                ToolTip.text: playerBar.isLoopEnabled ? "Repeat: On" : "Repeat: Off"
                ToolTip.visible: hovered
                onClicked: if (playerBar.bridge) playerBar.bridge.toggleLoop()
            }

            // Volume Section
            RowLayout {
                spacing: 0
                ThemeToolButton {
                    themeColors: playerBar.themeColors
                    icon: playerBar.currentVol > 0.5 ? "volume_up" : (playerBar.currentVol > 0 ? "volume_down" : "volume_off")
                    iconSize: 20
                    ToolTip.text: "Mute / Unmute"
                    ToolTip.visible: hovered
                    onClicked: {
                        if (playerBar.bridge) {
                            if (playerBar.currentVol > 0) {
                                playerBar.bridge.setVolume(0)
                            } else {
                                playerBar.bridge.setVolume(0.8)
                            }
                        }
                    }
                }

                ThemeSlider {
                    themeColors: playerBar.themeColors
                    Layout.preferredWidth: playerBar.width >= 1000 ? 90 : 64
                    Layout.maximumWidth: 100
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    from: 0
                    to: 1
                    value: playerBar.currentVol
                    ToolTip.text: "Volume: " + Math.round(playerBar.currentVol * 100) + "%"
                    ToolTip.visible: hovered
                    onMoved: if (playerBar.bridge) playerBar.bridge.setVolume(value)
                }
            }

            ThemeToolButton {
                themeColors: playerBar.themeColors
                icon: "open_in_full"
                iconSize: 20
                ToolTip.text: "Expand player"
                ToolTip.visible: hovered
                onClicked: playerBar.expandRequested()
            }
        }
    }
}
