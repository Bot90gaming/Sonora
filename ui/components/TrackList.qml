import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// M3 expressive list of tracks. Items are filled, 16dp rounded list items;
// the current track uses the primary container role.
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
    spacing: 6
    boundsBehavior: Flickable.StopAtBounds
    reuseItems: true

    ScrollBar.vertical: ThemeScrollBar {
        themeColors: trackList.themeColors
        policy: ScrollBar.AsNeeded
    }

    delegate: Item {
        id: trackDelegate
        required property var modelData
        required property int index

        readonly property bool current: !!modelData.videoId
            && !!trackList.service
            && !!trackList.service.nowPlaying
            && (trackList.service.nowPlaying.videoId || "") === modelData.videoId
        readonly property bool playing: current && !!trackList.service && trackList.service.playing

        width: trackList.width - 10
        height: 84

        opacity: 0
        Component.onCompleted: enterAnimation.start()

        ParallelAnimation {
            id: enterAnimation
            NumberAnimation {
                target: trackDelegate
                property: "opacity"
                from: 0
                to: 1
                duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                easing.type: Easing.BezierSpline
                easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
            }
        }

        Rectangle {
            id: surface
            anchors.fill: parent
            radius: trackList.themeColors.shape.large
            color: trackDelegate.current
                ? trackList.themeColors.primaryContainer
                : trackList.themeColors.surfaceContainerLow
            border.width: 1
            border.color: trackDelegate.current
                ? trackList.themeColors.primary
                : trackList.themeColors.outlineVariant
            z: 0

            Behavior on color {
                ColorAnimation {
                    duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
                }
            }
            Behavior on border.color {
                ColorAnimation {
                    duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
                }
            }
        }

        StateLayer {
            motion: trackList.themeColors.motion
            anchors.fill: surface
            radius: surface.radius
            stateColor: trackDelegate.current
                ? trackList.themeColors.onPrimaryContainer
                : trackList.themeColors.onSurface
            hovered: hover.hovered
            z: 1
        }

        HoverHandler {
            id: hover
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 12
            spacing: 12
            z: 2

            TrackThumbnail {
                Layout.preferredWidth: 68
                Layout.preferredHeight: 68
                themeColors: trackList.themeColors
                source: trackDelegate.modelData.thumbnail || ""
                playing: trackDelegate.playing
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    Layout.fillWidth: true
                    text: trackDelegate.modelData.title || "Unknown title"
                    color: trackDelegate.current
                        ? trackList.themeColors.onPrimaryContainer
                        : trackList.themeColors.onSurface
                    font.family: trackList.themeColors.fontFamily
                    font.pixelSize: trackList.themeColors.type.bodyMedium
                    font.weight: trackDelegate.current
                        ? trackList.themeColors.type.weightDemiBold
                        : trackList.themeColors.type.weightMedium
                    font.letterSpacing: trackList.themeColors.type.trackingBodyMedium
                    elide: Text.ElideRight
                    Behavior on color {
                        ColorAnimation {
                            duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
                        }
                    }
                }
                Label {
                    Layout.fillWidth: true
                    text: trackDelegate.modelData.artist || "Unknown artist"
                    color: trackDelegate.current
                        ? trackList.themeColors.onPrimaryContainer
                        : trackList.themeColors.onSurfaceVariant
                    opacity: 0.85
                    font.family: trackList.themeColors.fontFamily
                    font.pixelSize: trackList.themeColors.type.bodySmall
                    font.letterSpacing: trackList.themeColors.type.trackingBodySmall
                    elide: Text.ElideRight
                    Behavior on color {
                        ColorAnimation {
                            duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
                        }
                    }
                }
            }

            Label {
                text: trackList.formatDuration(trackDelegate.modelData.duration)
                color: trackDelegate.current
                    ? trackList.themeColors.onPrimaryContainer
                    : trackList.themeColors.onSurfaceVariant
                font.family: trackList.themeColors.fontFamily
                font.pixelSize: trackList.themeColors.type.labelMedium
                font.letterSpacing: trackList.themeColors.type.trackingLabelMedium
                Layout.rightMargin: 2
                Behavior on color {
                    ColorAnimation {
                        duration: trackList.themeColors.motion.expressiveDefaultEffectsDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: trackList.themeColors.motion.expressiveDefaultEffectsCurve
                    }
                }
            }

            ShellButton {
                themeColors: trackList.themeColors
                variant: trackDelegate.current ? "filled" : "tonal"
                iconName: trackDelegate.modelData.videoId
                    ? (trackDelegate.playing ? "pause" : "play_arrow")
                    : "folder_open"
                text: trackDelegate.modelData.videoId
                    ? (trackDelegate.playing ? "Pause" : trackDelegate.current ? "Resume" : "Play")
                    : "Open"
                onClicked: {
                    if (trackDelegate.current)
                        trackList.service.togglePlayback()
                    else if (trackDelegate.modelData.videoId)
                        trackList.service.playSong(trackDelegate.modelData)
                    else
                        trackList.service.openCollection(trackDelegate.modelData)
                }
            }

            ThemeToolButton {
                themeColors: trackList.themeColors
                iconColor: trackDelegate.current
                    ? trackList.themeColors.onPrimaryContainer
                    : trackList.themeColors.onSurfaceVariant
                icon: "playlist_add"
                iconSize: 22
                ToolTip.visible: hovered
                ToolTip.text: "Add to queue"
                onClicked: trackList.service.enqueue(trackDelegate.modelData)
            }

            ThemeToolButton {
                themeColors: trackList.themeColors
                iconColor: trackDelegate.current
                    ? trackList.themeColors.onPrimaryContainer
                    : trackList.themeColors.onSurfaceVariant
                icon: "download"
                iconSize: 20
                ToolTip.visible: hovered
                ToolTip.text: "Download"
                onClicked: trackList.service.downloadSong(trackDelegate.modelData)
            }
        }
    }
}
