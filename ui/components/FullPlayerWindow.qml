import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

// Fullscreen Now Playing Window with blurred album art background,
// round framed thumbnail with orbital wavy progress ring, and auto-scrolling synced lyrics.
Item {
    id: playerWindow
    objectName: "fullPlayer"

    required property var bridge
    required property var themeColors

    property bool isExpanded: false
    signal queueRequested

    visible: parent ? (y < parent.height) : true
    anchors.left: parent ? parent.left : undefined
    anchors.right: parent ? parent.right : undefined
    height: parent ? parent.height : 600
    y: parent ? (isExpanded ? 0 : parent.height) : 0
    layer.enabled: parent ? (y > 0 && y < parent.height) : false
    layer.smooth: true

    Behavior on y {
        NumberAnimation {
            duration: playerWindow.themeColors.motion.expressiveSlowSpatialDuration
            easing.type: Easing.BezierSpline
            easing.bezierCurve: playerWindow.themeColors.motion.expressiveDefaultSpatialCurve
        }
    }

    Shortcut {
        sequence: "Escape"
        enabled: playerWindow.isExpanded
        onActivated: playerWindow.isExpanded = false
    }

    readonly property bool isPlaying: bridge ? bridge.playing : false
    readonly property bool isLoading: bridge ? bridge.loading : false
    readonly property bool isLiked: bridge ? bridge.liked : false
    readonly property bool isLoopEnabled: bridge ? bridge.loopEnabled : false
    readonly property string currentTitle: (bridge && bridge.nowPlaying && bridge.nowPlaying.title) ? bridge.nowPlaying.title : ""
    readonly property string currentArtist: (bridge && bridge.nowPlaying && bridge.nowPlaying.artist) ? bridge.nowPlaying.artist : ""
    readonly property string currentAlbum: (bridge && bridge.nowPlaying && bridge.nowPlaying.album) ? bridge.nowPlaying.album : ""
    readonly property string currentThumbnail: (bridge && bridge.nowPlaying && bridge.nowPlaying.thumbnail) ? bridge.nowPlaying.thumbnail : ""
    readonly property int posMs: bridge ? bridge.positionMs : 0
    readonly property int durMs: bridge ? bridge.durationMs : 0
    readonly property real currentVol: bridge ? bridge.volume : 0.8
    readonly property real progressVal: durMs > 0 ? Math.max(0.0, Math.min(1.0, posMs / durMs)) : 0.0

    function formatTime(ms) {
        if (!ms || ms <= 0) return "0:00"
        let totalSec = Math.floor(ms / 1000)
        let mins = Math.floor(totalSec / 60)
        let secs = totalSec % 60
        return mins + ":" + (secs < 10 ? "0" : "") + secs
    }

    // ─── 1. FULL BLEED AMBIENT BLUR BACKGROUND ───────────────────
    Rectangle {
        anchors.fill: parent
        color: playerWindow.themeColors.surfaceContainerLowest
    }

    Image {
        id: bgArtwork
        anchors.fill: parent
        source: playerWindow.currentThumbnail
        fillMode: Image.PreserveAspectCrop
        visible: false
        asynchronous: true
        cache: true
    }

    FastBlur {
        id: bgBlur
        anchors.fill: bgArtwork
        source: bgArtwork
        radius: 96
        cached: true
        opacity: playerWindow.isPlaying ? 0.32 : 0.20
        visible: playerWindow.currentThumbnail !== ""

        Behavior on opacity {
            NumberAnimation { duration: 600 }
        }

        SequentialAnimation on opacity {
            running: playerWindow.isExpanded && playerWindow.isPlaying && playerWindow.currentThumbnail !== ""
            loops: Animation.Infinite
            NumberAnimation { to: 0.38; duration: 3600; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.24; duration: 3600; easing.type: Easing.InOutSine }
        }
    }

    // Gradient scrim for maximum contrast and elegance
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(playerWindow.themeColors.surfaceContainerLowest.r, playerWindow.themeColors.surfaceContainerLowest.g, playerWindow.themeColors.surfaceContainerLowest.b, 0.75) }
            GradientStop { position: 0.5; color: Qt.rgba(playerWindow.themeColors.surfaceContainerLowest.r, playerWindow.themeColors.surfaceContainerLowest.g, playerWindow.themeColors.surfaceContainerLowest.b, 0.88) }
            GradientStop { position: 1.0; color: Qt.rgba(playerWindow.themeColors.surfaceContainerLowest.r, playerWindow.themeColors.surfaceContainerLowest.g, playerWindow.themeColors.surfaceContainerLowest.b, 0.96) }
        }
    }

    // ─── 2. TOP HEADER BAR ───────────────────────────────────────
    RowLayout {
        id: topBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 18
        height: 52
        z: 10

        // Minimize Button
        ThemeToolButton {
            themeColors: playerWindow.themeColors
            icon: "keyboard_arrow_down"
            iconSize: 28
            ToolTip.text: "Minimize player (Esc)"
            ToolTip.visible: hovered
            onClicked: playerWindow.isExpanded = false
        }

        // Center Context Label
        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            spacing: 2

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "PLAYING FROM"
                color: playerWindow.themeColors.onSurfaceVariant
                font.family: playerWindow.themeColors.fontFamily
                font.pixelSize: 10
                font.weight: Font.Bold
                font.letterSpacing: 1.2
            }
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: playerWindow.currentAlbum !== "" ? playerWindow.currentAlbum : "YouTube Music"
                color: playerWindow.themeColors.onSurface
                font.family: playerWindow.themeColors.fontFamily
                font.pixelSize: 13
                font.weight: Font.Medium
                elide: Text.ElideRight
            }
        }

        // Quick Top Actions
        ThemeToolButton {
            themeColors: playerWindow.themeColors
            icon: playerWindow.isLoopEnabled ? "repeat_one" : "repeat"
            iconColor: playerWindow.isLoopEnabled
                ? playerWindow.themeColors.primary : playerWindow.themeColors.onSurfaceVariant
            iconSize: 22
            ToolTip.text: playerWindow.isLoopEnabled ? "Repeat: On" : "Repeat: Off"
            ToolTip.visible: hovered
            onClicked: if (playerWindow.bridge) playerWindow.bridge.toggleLoop()
        }

        ThemeToolButton {
            themeColors: playerWindow.themeColors
            icon: "radio"
            iconSize: 22
            ToolTip.text: "Start Radio"
            ToolTip.visible: hovered
            onClicked: if (playerWindow.bridge) playerWindow.bridge.startStation(playerWindow.bridge.nowPlaying)
        }

        Item {
            implicitWidth: 40
            implicitHeight: 40

            ThemeToolButton {
                id: topQueueBtn
                themeColors: playerWindow.themeColors
                icon: "queue_music"
                iconSize: 22
                ToolTip.text: "Queue"
                ToolTip.visible: hovered
                onClicked: playerWindow.queueRequested()
            }

            Rectangle {
                visible: playerWindow.bridge && playerWindow.bridge.queueItems && playerWindow.bridge.queueItems.length > 0
                anchors.top: parent.top
                anchors.topMargin: 2
                anchors.right: parent.right
                anchors.rightMargin: 2
                width: Math.max(16, queueCountText.implicitWidth + 8)
                height: 16
                radius: 8
                color: playerWindow.themeColors.primary

                Text {
                    id: queueCountText
                    anchors.centerIn: parent
                    text: (playerWindow.bridge && playerWindow.bridge.queueItems) ? playerWindow.bridge.queueItems.length : ""
                    color: playerWindow.themeColors.onPrimary
                    font.family: playerWindow.themeColors.fontFamily
                    font.pixelSize: 10
                    font.weight: Font.Bold
                }
            }
        }
    }

    // ─── 3. MAIN SPLIT CONTENT: PROGRESS/ARTWORK (LEFT) & LYRICS (RIGHT) ─────
    RowLayout {
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 36
        anchors.rightMargin: 36
        anchors.bottomMargin: 24
        spacing: 36

        // ════════════════ LEFT COLUMN: ROUND ARTWORK, WAVY RING & CONTROLS ════════════════
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.48
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            spacing: 16

            Item { Layout.fillHeight: true }

            // ── Circular Frame Thumbnail ──
            Item {
                id: artworkContainer
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: Math.min(300, Math.max(200, playerWindow.height * 0.36))
                Layout.preferredHeight: Layout.preferredWidth
                implicitWidth: Layout.preferredWidth
                implicitHeight: Layout.preferredWidth

                // Soft Ambient Drop Shadow
                Rectangle {
                    anchors.fill: roundFrame
                    radius: roundFrame.radius
                    color: "#000000"
                    opacity: 0.32
                    scale: 1.02
                    y: 6
                    z: 0
                }

                // Round Frame Thumbnail
                Rectangle {
                    id: roundFrame
                    anchors.fill: parent
                    radius: width / 2
                    color: playerWindow.themeColors.surfaceContainerHigh
                    clip: true
                    z: 1

                    Image {
                        id: roundThumbnail
                        anchors.fill: parent
                        source: playerWindow.currentThumbnail
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        cache: true
                        visible: false
                    }

                    Rectangle {
                        id: roundMask
                        anchors.fill: parent
                        radius: parent.radius
                        color: "white"
                        visible: false
                        layer.enabled: true
                    }

                    OpacityMask {
                        anchors.fill: roundThumbnail
                        source: roundThumbnail
                        maskSource: roundMask
                        visible: roundThumbnail.status === Image.Ready
                    }

                    // Placeholder note when artwork is loading/missing
                    Text {
                        anchors.centerIn: parent
                        visible: roundThumbnail.status !== Image.Ready
                        text: "music_note"
                        color: playerWindow.themeColors.primary
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 48
                    }

                    // Subtle inner vinyl groove border
                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: "transparent"
                        border.color: Qt.rgba(1, 1, 1, 0.12)
                        border.width: 2
                    }
                }
            }

            // ── Linear Progress Bar at the Bottom of Song Thumbnail ──
            ColumnLayout {
                id: progressContainer
                objectName: "progressContainer"
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: Math.min(320, playerWindow.width * 0.42)
                implicitWidth: Layout.preferredWidth
                spacing: 4

                Item {
                    id: linearTrackArea
                    objectName: "linearTrackArea"
                    Layout.fillWidth: true
                    Layout.preferredWidth: progressContainer.implicitWidth
                    implicitWidth: progressContainer.implicitWidth
                    implicitHeight: 28

                    property bool isHovered: progressHover.hovered || progressDrag.pressed
                    property bool isDragging: progressDrag.pressed
                    property real dragFraction: 0.0

                    // Inactive Guide Track Bar
                    Rectangle {
                        id: bgTrack
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        height: linearTrackArea.isHovered ? 10 : 6
                        radius: height / 2
                        color: Qt.rgba(playerWindow.themeColors.onSurface.r, playerWindow.themeColors.onSurface.g, playerWindow.themeColors.onSurface.b, 0.16)

                        Behavior on height {
                            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                        }
                    }

                    // Active Highlighted Progress Track
                    Rectangle {
                        id: activeTrack
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        height: bgTrack.height
                        radius: height / 2
                        color: playerWindow.themeColors.primary
                        width: {
                            let frac = linearTrackArea.isDragging
                                ? linearTrackArea.dragFraction
                                : playerWindow.progressVal
                            return Math.max(0, Math.min(linearTrackArea.width, frac * linearTrackArea.width))
                        }

                        Behavior on width {
                            enabled: !linearTrackArea.isDragging
                            NumberAnimation {
                                duration: 120
                                easing.type: Easing.Linear
                            }
                        }
                    }

                    // M3 High-Contrast Pill Thumb Knob
                    Rectangle {
                        id: thumbKnob
                        width: linearTrackArea.isDragging ? 8 : (linearTrackArea.isHovered ? 7 : 5)
                        height: linearTrackArea.isHovered ? 22 : 16
                        radius: width / 2
                        x: Math.max(0, Math.min(linearTrackArea.width - width, activeTrack.width - width / 2))
                        anchors.verticalCenter: parent.verticalCenter
                        color: playerWindow.themeColors.primary
                        border.color: "#FFFFFF"
                        border.width: 1.5
                        visible: linearTrackArea.isHovered || linearTrackArea.isDragging

                        Behavior on height {
                            NumberAnimation { duration: 150; easing.type: Easing.OutBack }
                        }
                        Behavior on width {
                            NumberAnimation { duration: 150; easing.type: Easing.OutBack }
                        }
                    }

                    HoverHandler {
                        id: progressHover
                        cursorShape: Qt.PointingHandCursor
                    }

                    MouseArea {
                        id: progressDrag
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor

                        function seekFromMouse(mouse) {
                            let frac = Math.max(0.0, Math.min(1.0, mouse.x / linearTrackArea.width))
                            linearTrackArea.dragFraction = frac
                            if (playerWindow.bridge) {
                                playerWindow.bridge.seek(frac)
                            }
                        }

                        onPressed: (mouse) => seekFromMouse(mouse)
                        onPositionChanged: (mouse) => {
                            if (pressed) {
                                let frac = Math.max(0.0, Math.min(1.0, mouse.x / linearTrackArea.width))
                                linearTrackArea.dragFraction = frac
                            }
                        }
                        onReleased: (mouse) => seekFromMouse(mouse)
                    }
                }

                // Time Elapsed on Left, Total Duration on Right
                RowLayout {
                    Layout.fillWidth: true

                    Label {
                        text: linearTrackArea.isDragging
                            ? playerWindow.formatTime(linearTrackArea.dragFraction * playerWindow.durMs)
                            : playerWindow.formatTime(playerWindow.posMs)
                        color: playerWindow.themeColors.onSurfaceVariant
                        font.family: playerWindow.themeColors.fontFamily
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }

                    Item { Layout.fillWidth: true }

                    Label {
                        text: playerWindow.formatTime(playerWindow.durMs)
                        color: playerWindow.themeColors.onSurfaceVariant
                        font.family: playerWindow.themeColors.fontFamily
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }
                }
            }

            // ── Track Metadata ──
            ColumnLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                spacing: 4

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 8

                    EqualizerBars {
                        themeColors: playerWindow.themeColors
                        width: 16
                        height: 16
                        color: playerWindow.themeColors.primary
                        visible: playerWindow.isPlaying && !!playerWindow.currentTitle
                    }

                    Label {
                        text: playerWindow.currentTitle !== "" ? playerWindow.currentTitle : "Nothing playing"
                        color: playerWindow.themeColors.onSurface
                        font.family: playerWindow.themeColors.fontFamily
                        font.pixelSize: playerWindow.themeColors.type.headlineSmall
                        font.weight: Font.Bold
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        Layout.maximumWidth: playerWindow.width * 0.44
                    }
                }

                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: playerWindow.currentArtist !== "" ? playerWindow.currentArtist : "Select a song"
                    color: playerWindow.themeColors.onSurfaceVariant
                    font.family: playerWindow.themeColors.fontFamily
                    font.pixelSize: playerWindow.themeColors.type.bodyMedium
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                }
            }

            // ── Playback Controls ──
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 20

                ThemeToolButton {
                    id: fullLikeBtn
                    themeColors: playerWindow.themeColors
                    icon: playerWindow.isLiked ? "favorite" : "favorite_border"
                    iconColor: playerWindow.isLiked
                        ? playerWindow.themeColors.error : playerWindow.themeColors.onSurfaceVariant
                    iconSize: 26
                    ToolTip.text: playerWindow.isLiked ? "Unlike track" : "Like track"
                    ToolTip.visible: hovered
                    onClicked: {
                        if (playerWindow.bridge) {
                            playerWindow.bridge.likeSong(playerWindow.bridge.nowPlaying)
                            fullLikeAnim.restart()
                        }
                    }

                    SequentialAnimation {
                        id: fullLikeAnim
                        NumberAnimation { target: fullLikeBtn; property: "scale"; to: 1.35; duration: 150 }
                        NumberAnimation { target: fullLikeBtn; property: "scale"; to: 1.0; duration: 150 }
                    }
                }

                ThemeToolButton {
                    themeColors: playerWindow.themeColors
                    icon: "skip_previous"
                    iconSize: 34
                    ToolTip.text: "Previous"
                    ToolTip.visible: hovered
                    onClicked: if (playerWindow.bridge) playerWindow.bridge.previousTrack()
                }

                // Play / Pause Squircle Morph Button
                Button {
                    id: fullPlayBtn
                    implicitWidth: 64
                    implicitHeight: 64
                    scale: fullPlayBtn.down ? 0.92 : (fullPlayBtn.hovered ? 1.05 : 1.0)
                    enabled: !!playerWindow.currentTitle || (playerWindow.bridge && playerWindow.bridge.homeItems && playerWindow.bridge.homeItems.length > 0)
                    hoverEnabled: true

                    Behavior on scale {
                        NumberAnimation {
                            duration: playerWindow.themeColors.motion.expressiveFastSpatialDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playerWindow.themeColors.motion.expressiveFastSpatialCurve
                        }
                    }

                    background: Rectangle {
                        radius: fullPlayBtn.down ? 18 : (playerWindow.isPlaying ? 20 : 32)
                        color: !fullPlayBtn.enabled
                            ? playerWindow.themeColors.disabledSurface
                            : playerWindow.themeColors.primary
                        border.width: fullPlayBtn.activeFocus ? 2 : 0
                        border.color: playerWindow.themeColors.onPrimary

                        Behavior on radius {
                            NumberAnimation {
                                duration: 350
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: playerWindow.themeColors.motion.expressiveDefaultSpatialCurve
                            }
                        }
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }

                        StateLayer {
                            motion: playerWindow.themeColors.motion
                            radius: parent.radius
                            stateColor: playerWindow.themeColors.onPrimary
                            hovered: fullPlayBtn.hovered
                            pressed: fullPlayBtn.down
                            visible: fullPlayBtn.enabled
                        }
                    }

                    contentItem: Item {
                        LoadingIndicator {
                            themeColors: playerWindow.themeColors
                            anchors.centerIn: parent
                            width: 28
                            height: 28
                            visible: playerWindow.isLoading
                            color: playerWindow.themeColors.onPrimary
                            running: playerWindow.isLoading
                        }
                        Text {
                            anchors.centerIn: parent
                            visible: !playerWindow.isLoading
                            text: playerWindow.isPlaying ? "pause" : "play_arrow"
                            color: fullPlayBtn.enabled
                                ? playerWindow.themeColors.onPrimary
                                : playerWindow.themeColors.disabledText
                            font.family: "Material Symbols Rounded"
                            font.pixelSize: 34
                        }
                    }

                    ToolTip.text: playerWindow.isPlaying ? "Pause" : "Play"
                    ToolTip.visible: hovered
                    onClicked: {
                        if (playerWindow.bridge) {
                            if (!playerWindow.currentTitle && playerWindow.bridge.homeItems && playerWindow.bridge.homeItems.length > 0) {
                                playerWindow.bridge.playSong(playerWindow.bridge.homeItems[0])
                            } else {
                                playerWindow.bridge.togglePlayback()
                            }
                        }
                    }

                    HoverHandler {
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                ThemeToolButton {
                    themeColors: playerWindow.themeColors
                    icon: "skip_next"
                    iconSize: 34
                    ToolTip.text: "Next"
                    ToolTip.visible: hovered
                    onClicked: if (playerWindow.bridge) playerWindow.bridge.nextTrack()
                }

                // Volume Quick Slider
                RowLayout {
                    spacing: 0
                    ThemeToolButton {
                        themeColors: playerWindow.themeColors
                        icon: playerWindow.currentVol > 0.5 ? "volume_up" : (playerWindow.currentVol > 0 ? "volume_down" : "volume_off")
                        iconSize: 22
                        ToolTip.text: "Mute / Unmute"
                        ToolTip.visible: hovered
                        onClicked: {
                            if (playerWindow.bridge) {
                                if (playerWindow.currentVol > 0) {
                                    playerWindow.bridge.setVolume(0)
                                } else {
                                    playerWindow.bridge.setVolume(0.8)
                                }
                            }
                        }
                    }
                    ThemeSlider {
                        themeColors: playerWindow.themeColors
                        Layout.preferredWidth: 80
                        from: 0
                        to: 1
                        value: playerWindow.currentVol
                        ToolTip.text: "Volume: " + Math.round(playerWindow.currentVol * 100) + "%"
                        ToolTip.visible: hovered
                        onMoved: if (playerWindow.bridge) playerWindow.bridge.setVolume(value)
                    }
                }
            }

            Item { Layout.fillHeight: true }
        }

        // ════════════════ RIGHT COLUMN: AUTO-SCROLLING SYNCED LYRICS ════════════════
        Rectangle {
            id: lyricsCard
            objectName: "lyricsCard"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.52
            radius: playerWindow.themeColors.shape.extraLarge
            color: Qt.rgba(playerWindow.themeColors.surfaceContainerHigh.r, playerWindow.themeColors.surfaceContainerHigh.g, playerWindow.themeColors.surfaceContainerHigh.b, 0.45)
            border.color: Qt.rgba(playerWindow.themeColors.outlineVariant.r, playerWindow.themeColors.outlineVariant.g, playerWindow.themeColors.outlineVariant.b, 0.35)
            border.width: 1
            clip: true

            readonly property var lyricsData: playerWindow.bridge ? playerWindow.bridge.lyrics : null
            readonly property bool hasLyrics: Boolean(lyricsData && lyricsData.available && lyricsData.lines && lyricsData.lines.length > 0)
            readonly property bool isSync: Boolean(lyricsData && lyricsData.hasTimestamps)

            // Find current active line based on playback positionMs
            function getActiveIndex(ms, has, sync, data) {
                if (!has || !sync || !data || !data.lines || data.lines.length === 0) return -1
                let lines = data.lines
                if (ms < lines[0].startTime) return -1
                for (let i = lines.length - 1; i >= 0; i--) {
                    if (ms >= lines[i].startTime) {
                        return i
                    }
                }
                return -1
            }

            property int activeLineIndex: getActiveIndex(playerWindow.posMs, hasLyrics, isSync, lyricsData)
            onActiveLineIndexChanged: {
                if (hasLyrics && isSync && activeLineIndex >= 0) {
                    lyricsView.currentIndex = activeLineIndex
                    lyricsView.positionViewAtIndex(activeLineIndex, ListView.Center)
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 12

                // Lyrics Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: "lyrics"
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 22
                        color: playerWindow.themeColors.primary
                    }

                    Label {
                        text: "Lyrics"
                        color: playerWindow.themeColors.onSurface
                        font.family: playerWindow.themeColors.fontFamily
                        font.pixelSize: playerWindow.themeColors.type.titleMedium
                        font.weight: Font.Bold
                    }

                    Item { Layout.fillWidth: true }

                    Label {
                        visible: Boolean(lyricsCard.lyricsData && lyricsCard.lyricsData.source)
                        text: (lyricsCard.lyricsData && lyricsCard.lyricsData.source) ? lyricsCard.lyricsData.source : ""
                        color: playerWindow.themeColors.onSurfaceVariant
                        font.family: playerWindow.themeColors.fontFamily
                        font.pixelSize: 11
                        opacity: 0.7
                    }
                }

                // Lyrics Content View
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    // Loading State
                    Column {
                        anchors.centerIn: parent
                        spacing: 12
                        visible: Boolean(lyricsCard.lyricsData && lyricsCard.lyricsData.loading)

                        LoadingIndicator {
                            themeColors: playerWindow.themeColors
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: 32
                            height: 32
                            running: visible
                            color: playerWindow.themeColors.primary
                        }
                        Label {
                            text: "Loading lyrics…"
                            color: playerWindow.themeColors.onSurfaceVariant
                            font.family: playerWindow.themeColors.fontFamily
                            font.pixelSize: 14
                        }
                    }

                    // Empty State
                    Column {
                        anchors.centerIn: parent
                        spacing: 10
                        visible: !lyricsCard.lyricsData || (!lyricsCard.lyricsData.loading && !lyricsCard.hasLyrics)

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "queue_music"
                            color: playerWindow.themeColors.onSurfaceVariant
                            font.family: "Material Symbols Rounded"
                            font.pixelSize: 42
                            opacity: 0.5
                        }
                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Lyrics not available for this track"
                            color: playerWindow.themeColors.onSurface
                            font.family: playerWindow.themeColors.fontFamily
                            font.pixelSize: playerWindow.themeColors.type.titleSmall
                            font.weight: Font.Medium
                        }
                        Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Sit back and enjoy the music"
                            color: playerWindow.themeColors.onSurfaceVariant
                            font.family: playerWindow.themeColors.fontFamily
                            font.pixelSize: 13
                        }
                    }

                    // Lyrics Scroll List
                    ListView {
                        id: lyricsView
                        anchors.fill: parent
                        clip: true
                        spacing: 16
                        visible: lyricsCard.hasLyrics && !(lyricsCard.lyricsData && lyricsCard.lyricsData.loading)
                        model: lyricsCard.hasLyrics ? lyricsCard.lyricsData.lines : null
                        boundsBehavior: Flickable.StopAtBounds
                        highlightRangeMode: ListView.NoHighlightRange
                        highlightMoveDuration: 0

                        Behavior on contentY {
                            enabled: !lyricsView.moving && !lyricsView.flicking
                            NumberAnimation {
                                duration: 420
                                easing.type: Easing.OutCubic
                            }
                        }

                        ScrollBar.vertical: ThemeScrollBar {
                            themeColors: playerWindow.themeColors
                            policy: ScrollBar.AsNeeded
                        }

                        delegate: Item {
                            id: lineDelegate
                            required property var modelData
                            required property int index

                            readonly property bool isCurrent: lyricsCard.isSync && (index === lyricsCard.activeLineIndex)
                            readonly property real lineDuration: {
                                if (modelData && modelData.endTime > modelData.startTime && modelData.endTime > 0) {
                                    return modelData.endTime - modelData.startTime
                                }
                                return 3500
                            }

                            // Continuous floating-point font swell delta (+4.00 -> 3.99 -> 3.98 -> ... -> 0.00)
                            property real fontSwell: 0.0

                            width: lyricsView.width - 16
                            height: Math.max(56, lineText.implicitHeight + 24)

                            // 1. Ambient Diffuse Glowing Light Beam Aura
                            Rectangle {
                                id: glowAura
                                anchors.fill: parent
                                anchors.margins: -4
                                radius: 16
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: Qt.rgba(playerWindow.themeColors.primary.r, playerWindow.themeColors.primary.g, playerWindow.themeColors.primary.b, 0.38) }
                                    GradientStop { position: 0.55; color: Qt.rgba(playerWindow.themeColors.primary.r, playerWindow.themeColors.primary.g, playerWindow.themeColors.primary.b, 0.18) }
                                    GradientStop { position: 1.0; color: "transparent" }
                                }
                                opacity: lineDelegate.isCurrent ? pulseGlow.glowVal : 0.0
                                visible: opacity > 0.01

                                Behavior on opacity {
                                    NumberAnimation { duration: 280; easing.type: Easing.OutCubic }
                                }
                            }

                            // 2. Core Focused Luminous Pill
                            Rectangle {
                                id: glowPill
                                anchors.fill: parent
                                radius: 12
                                color: lineDelegate.isCurrent
                                    ? Qt.rgba(playerWindow.themeColors.primary.r, playerWindow.themeColors.primary.g, playerWindow.themeColors.primary.b, 0.28)
                                    : (mouseLine.containsMouse ? Qt.rgba(playerWindow.themeColors.onSurface.r, playerWindow.themeColors.onSurface.g, playerWindow.themeColors.onSurface.b, 0.06) : "transparent")
                                border.color: lineDelegate.isCurrent
                                    ? Qt.rgba(playerWindow.themeColors.primary.r, playerWindow.themeColors.primary.g, playerWindow.themeColors.primary.b, 0.70)
                                    : "transparent"
                                border.width: 1.5

                                Behavior on color {
                                    ColorAnimation { duration: 250 }
                                }
                                Behavior on border.color {
                                    ColorAnimation { duration: 250 }
                                }

                                // Glowing active vertical beacon pill on the left
                                Rectangle {
                                    anchors.left: parent.left
                                    anchors.leftMargin: 4
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 4
                                    height: parent.height - 18
                                    radius: 2
                                    color: playerWindow.themeColors.primary
                                    opacity: lineDelegate.isCurrent ? 1.0 : 0.0
                                    visible: opacity > 0.01

                                    Behavior on opacity {
                                        NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
                                    }
                                }
                            }

                            QtObject {
                                id: pulseGlow
                                property real glowVal: 0.70
                            }

                            SequentialAnimation {
                                running: lineDelegate.isCurrent
                                loops: Animation.Infinite
                                NumberAnimation {
                                    target: pulseGlow
                                    property: "glowVal"
                                    to: 1.0
                                    duration: 950
                                    easing.type: Easing.OutCubic
                                }
                                NumberAnimation {
                                    target: pulseGlow
                                    property: "glowVal"
                                    to: 0.55
                                    duration: 950
                                    easing.type: Easing.OutCubic
                                }
                            }

                            // 3. Continuous Subpixel Font Size Swell & Return with Cubic Ease Out
                            SequentialAnimation {
                                id: sizePulseAnim
                                running: false

                                // Step 1: Smoothly swell up (+4.0 font size equivalent) with cubic ease out
                                NumberAnimation {
                                    target: lineDelegate
                                    property: "fontSwell"
                                    from: 0.0
                                    to: 4.0
                                    duration: Math.min(360, Math.max(180, lineDelegate.lineDuration * 0.18))
                                    easing.type: Easing.OutCubic
                                }

                                // Step 2: Hold briefly at peak size
                                PauseAnimation {
                                    duration: Math.max(50, lineDelegate.lineDuration * 0.12)
                                }

                                // Step 3: Continuously glide from 4.00 down to 0.00 (like 4 -> 3.99 -> 3.98...) with cubic ease out
                                NumberAnimation {
                                    target: lineDelegate
                                    property: "fontSwell"
                                    from: 4.0
                                    to: 0.0
                                    duration: Math.min(2200, Math.max(550, lineDelegate.lineDuration * 0.70))
                                    easing.type: Easing.OutCubic
                                }
                            }

                            onIsCurrentChanged: {
                                if (isCurrent) {
                                    sizePulseAnim.restart()
                                } else {
                                    sizePulseAnim.stop()
                                    fontSwell = 0.0
                                }
                            }

                            Text {
                                id: lineText
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.leftMargin: 20
                                anchors.rightMargin: 28
                                anchors.verticalCenter: parent.verticalCenter
                                text: (lineDelegate.modelData && lineDelegate.modelData.text) ? lineDelegate.modelData.text : ""
                                color: lineDelegate.isCurrent ? playerWindow.themeColors.primary : playerWindow.themeColors.onSurface
                                opacity: lineDelegate.isCurrent ? 1.0 : (mouseLine.containsMouse ? 0.95 : 0.68)
                                font.family: playerWindow.themeColors.fontFamily
                                font.pixelSize: 20
                                font.weight: lineDelegate.isCurrent ? Font.Bold : Font.Medium
                                wrapMode: Text.Wrap
                                transformOrigin: Item.Left
                                scale: 1.0 + (lineDelegate.fontSwell / 20.0)

                                Behavior on opacity {
                                    NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
                                }
                                Behavior on color {
                                    ColorAnimation { duration: 250 }
                                }
                            }

                            MouseArea {
                                id: mouseLine
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: lineDelegate.modelData.startTime >= 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                                onClicked: {
                                    if (lineDelegate.modelData.startTime >= 0 && playerWindow.durMs > 0) {
                                        let targetFrac = lineDelegate.modelData.startTime / playerWindow.durMs
                                        if (playerWindow.bridge) {
                                            playerWindow.bridge.seek(targetFrac)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
