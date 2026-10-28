import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"
import "config"

ApplicationWindow {
    id: appWindow
    required property var bridge
    visible: true
    width: 1280
    height: 820
    minimumWidth: 880
    minimumHeight: 600
    title: "Sonora"
    color: uiColors.md3Bg
    font.family: uiColors.fontFamily

    FontLoader {
        id: iconFont
        source: Qt.resolvedUrl("../../assets/fonts/MaterialSymbolsRounded.ttf")
    }

    // ─── AMBIENT BACKGROUND GLOW (from current album art) ────
    Image {
        id: ambientBg
        anchors.fill: parent
        source: appWindow.bridge.nowPlaying.thumbnail || ""
        fillMode: Image.PreserveAspectCrop
        opacity: appWindow.bridge.playing ? 0.20 : 0.08
        visible: source !== ""

        Behavior on opacity {
            NumberAnimation { duration: 700; easing.type: Easing.OutCubic }
        }

        SequentialAnimation on opacity {
            running: appWindow.bridge.playing && ambientBg.source !== ""
            loops: Animation.Infinite
            NumberAnimation { to: 0.25; duration: 3400; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.15; duration: 3400; easing.type: Easing.InOutSine }
        }

        layer.enabled: true
        layer.effect: FastBlur {
            radius: 80
        }
    }

    palette.window: uiColors.surface
    palette.windowText: uiColors.onSurface
    palette.base: uiColors.surfaceContainerLow
    palette.alternateBase: uiColors.surfaceContainer
    palette.text: uiColors.onSurface
    palette.button: uiColors.surfaceContainerHigh
    palette.buttonText: uiColors.onSurface
    palette.brightText: uiColors.primary
    palette.highlight: uiColors.primary
    palette.highlightedText: uiColors.onPrimary
    palette.placeholderText: uiColors.onSurfaceVariant
    palette.toolTipBase: uiColors.inverseSurface
    palette.toolTipText: uiColors.inverseOnSurface
    palette.light: uiColors.surfaceContainerHighest
    palette.midlight: uiColors.surfaceContainerHigh
    palette.mid: uiColors.outline
    palette.dark: uiColors.surfaceContainerLowest
    palette.shadow: uiColors.shadow
    palette.link: uiColors.primary
    palette.linkVisited: uiColors.primary

    Overlay.modal: Rectangle {
        color: uiColors.scrim
    }

    ThemeConfig {
        id: uiColors
        objectName: "uiColors"
        bridge: appWindow.bridge
    }

    property string pendingPage: ""
    property bool pageTransitioning: false

    Timer {
        id: pageTransitionTimer
        interval: 220
        repeat: false
        onTriggered: {
            if (pendingPage !== "") {
                pageStack.replace(pageComponent, { pageName: pendingPage })
                appWindow.bridge.setPage(pendingPage)
                pendingPage = ""
            }
            pageTransitioning = false
        }
    }

    function navigate(page) {
        if (pageStack.currentItem && pageStack.currentItem.pageName === page && !pageTransitioning)
            return
        if (pageTransitioning && pendingPage === page)
            return

        pendingPage = page
        pageTransitioning = true
        pageTransitionTimer.restart()
    }

    Shortcut {
        sequences: ["Ctrl+F", "Ctrl+K"]
        onActivated: {
            globalSearch.forceActiveFocus()
            globalSearch.selectAll()
        }
    }

    Shortcut {
        sequences: ["Ctrl+M"]
        onActivated: {
            if (appWindow.bridge && appWindow.bridge.switchUi) {
                appWindow.bridge.switchUi("mini")
            }
        }
    }

    Component {
        id: pageComponent
        Item {
            property string pageName: "home"

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                RowLayout {
                    visible: pageName !== "home"
                    Layout.fillWidth: true
                    Layout.bottomMargin: 24
                    spacing: 16

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3
                        Label {
                            text: appWindow.pageTitle(pageName)
                            color: uiColors.onSurface
                            font.family: uiColors.fontFamily
                            font.pixelSize: uiColors.type.headlineSmall
                            font.weight: uiColors.type.weightMedium
                            font.letterSpacing: 0
                        }
                        Label {
                            text: appWindow.pageSubtitle(pageName)
                            color: uiColors.onSurfaceVariant
                            font.family: uiColors.fontFamily
                            font.pixelSize: uiColors.type.bodyMedium
                            font.letterSpacing: uiColors.type.trackingBodyMedium
                        }
                    }
                }

                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: pageName === "home" ? 0
                        : pageName === "search" ? 1
                        : pageName === "library" ? 2
                        : pageName === "downloads" ? 3 : 4

                    // -------------------------------------------------- home
                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 18

                            FeaturedCarousel {
                                Layout.fillWidth: true
                                model: appWindow.bridge.homeItems
                                service: appWindow.bridge
                                themeColors: uiColors
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: 24

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 1.6
                                    spacing: 10

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10

                                        Label {
                                            Layout.fillWidth: true
                                            text: "Newest"
                                            color: uiColors.onSurface
                                            font.family: uiColors.fontFamily
                                            font.pixelSize: uiColors.type.titleLarge
                                            font.weight: uiColors.type.weightMedium
                                            font.letterSpacing: uiColors.type.trackingTitleLarge
                                        }
                                        LoadingIndicator {
                                            themeColors: uiColors
                                            width: 16
                                            height: 16
                                            visible: appWindow.bridge.busy
                                            running: appWindow.bridge.busy
                                            color: uiColors.primary
                                            Layout.alignment: Qt.AlignVCenter
                                        }
                                        Label {
                                            visible: appWindow.bridge.busy
                                            text: "Refreshing"
                                            color: uiColors.onSurfaceVariant
                                            font.family: uiColors.fontFamily
                                            font.pixelSize: uiColors.type.bodySmall
                                            Layout.alignment: Qt.AlignVCenter
                                        }
                                        ShellButton {
                                            themeColors: uiColors
                                            variant: "text"
                                            text: "Refresh"
                                            onClicked: appWindow.bridge.loadHome()
                                        }
                                    }

                                    TrackList {
                                        themeColors: uiColors
                                        service: appWindow.bridge
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        model: appWindow.bridge.homeItems
                                    }
                                }

                                PlaylistGrid {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 0.9
                                    Layout.minimumWidth: 240
                                    Layout.maximumWidth: 410
                                    model: appWindow.bridge.homeCollections.slice(0, 4)
                                    service: appWindow.bridge
                                    themeColors: uiColors
                                    emptyLabel: appWindow.bridge.authenticated
                                        ? "No playlists yet" : "Sign in"
                                }
                            }
                        }
                    }

                    // ------------------------------------------------ search
                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 14

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                Repeater {
                                    model: [
                                        { title: "Songs", value: "songs" },
                                        { title: "Albums", value: "albums" },
                                        { title: "Playlists", value: "playlists" }
                                    ]
                                    delegate: FilterChip {
                                        required property var modelData
                                        themeColors: uiColors
                                        text: modelData.title
                                        selected: appWindow.bridge.searchFilter === modelData.value
                                        onClicked: appWindow.bridge.setSearchFilter(modelData.value)
                                    }
                                }
                                Item { Layout.fillWidth: true }
                            }

                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                TrackList {
                                    anchors.fill: parent
                                    themeColors: uiColors
                                    service: appWindow.bridge
                                    model: appWindow.bridge.searchResults
                                }

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 12
                                    visible: appWindow.bridge.searchResults.length === 0

                                    LoadingIndicator {
                                        themeColors: uiColors
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        width: 28
                                        height: 28
                                        visible: appWindow.bridge.busy
                                        running: appWindow.bridge.busy
                                        color: uiColors.primary
                                    }
                                    Label {
                                        text: appWindow.bridge.busy
                                            ? "Searching…" : "Search for something you love"
                                        color: uiColors.onSurfaceVariant
                                        font.family: uiColors.fontFamily
                                        font.pixelSize: uiColors.type.bodyLarge
                                    }
                                }
                            }
                        }
                    }

                    // ----------------------------------------------- library
                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 14

                            Rectangle {
                                visible: !appWindow.bridge.authenticated
                                Layout.fillWidth: true
                                Layout.preferredHeight: 92
                                radius: uiColors.shape.large
                                color: uiColors.surfaceContainerLow

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 20
                                    anchors.rightMargin: 16
                                    spacing: 14

                                    Rectangle {
                                        width: 40
                                        height: 40
                                        radius: 20
                                        color: uiColors.primaryContainer
                                        Text {
                                            anchors.centerIn: parent
                                            text: "favorite"
                                            color: uiColors.onPrimaryContainer
                                            font.family: "Material Symbols Rounded"
                                            font.pixelSize: 22
                                        }
                                    }

                                    Label {
                                        Layout.fillWidth: true
                                        text: "Sign in to browse your Liked Songs."
                                        color: uiColors.onSurface
                                        font.family: uiColors.fontFamily
                                        font.pixelSize: uiColors.type.bodyMedium
                                    }
                                    ShellButton {
                                        themeColors: uiColors
                                        text: "Sign in"
                                        primary: true
                                        onClicked: accountDialog.open()
                                    }
                                }
                            }

                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                TrackList {
                                    anchors.fill: parent
                                    themeColors: uiColors
                                    service: appWindow.bridge
                                    model: appWindow.bridge.libraryItems
                                    visible: appWindow.bridge.authenticated
                                }

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 12
                                    visible: appWindow.bridge.authenticated
                                        && appWindow.bridge.libraryItems.length === 0

                                    LoadingIndicator {
                                        themeColors: uiColors
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        width: 28
                                        height: 28
                                        visible: appWindow.bridge.busy
                                        running: appWindow.bridge.busy
                                        color: uiColors.primary
                                    }
                                    Label {
                                        text: appWindow.bridge.busy
                                            ? "Loading your library…"
                                            : "Your liked songs will appear here"
                                        color: uiColors.onSurfaceVariant
                                        font.family: uiColors.fontFamily
                                        font.pixelSize: uiColors.type.bodyLarge
                                    }
                                }
                            }
                        }
                    }

                    // --------------------------------------------- downloads
                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 6

                            Label {
                                text: "Your downloads are saved to your Music folder."
                                color: uiColors.onSurfaceVariant
                                font.family: uiColors.fontFamily
                                font.pixelSize: uiColors.type.bodyMedium
                            }
                            Label {
                                text: "Choose Download on any track to save an offline copy."
                                color: uiColors.onSurfaceVariant
                                font.family: uiColors.fontFamily
                                font.pixelSize: uiColors.type.bodySmall
                                Layout.bottomMargin: 8
                            }

                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                ListView {
                                    id: downloadsList
                                    anchors.fill: parent
                                    clip: true
                                    spacing: 8
                                    model: appWindow.bridge.downloads
                                    boundsBehavior: Flickable.StopAtBounds
                                    ScrollBar.vertical: ThemeScrollBar {
                                        themeColors: uiColors
                                        policy: ScrollBar.AsNeeded
                                    }

                                    delegate: Rectangle {
                                        required property var modelData
                                        width: downloadsList.width - 10
                                        height: 72
                                        radius: uiColors.shape.medium
                                        color: uiColors.surfaceContainerLow

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 16
                                            anchors.rightMargin: 16
                                            anchors.topMargin: 10
                                            anchors.bottomMargin: 10
                                            spacing: 4

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 10

                                                Label {
                                                    Layout.fillWidth: true
                                                    text: modelData.title + " · " + modelData.artist
                                                    color: uiColors.onSurface
                                                    font.family: uiColors.fontFamily
                                                    font.pixelSize: uiColors.type.bodyMedium
                                                    elide: Text.ElideRight
                                                }
                                                Label {
                                                    text: modelData.status
                                                    color: uiColors.onSurfaceVariant
                                                    font.family: uiColors.fontFamily
                                                    font.pixelSize: uiColors.type.labelMedium
                                                }
                                                Label {
                                                    text: modelData.progress + "%"
                                                    color: uiColors.primary
                                                    font.family: uiColors.fontFamily
                                                    font.pixelSize: uiColors.type.labelMedium
                                                    font.weight: uiColors.type.weightMedium
                                                }
                                            }

                                            LinearProgress {
                                                themeColors: uiColors
                                                Layout.fillWidth: true
                                                Layout.preferredHeight: 6
                                                value: (modelData.progress || 0) / 100
                                                color: uiColors.primary
                                                trackColor: uiColors.secondaryContainer
                                            }
                                        }
                                    }
                                }

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 10
                                    visible: appWindow.bridge.downloads.length === 0

                                    Rectangle {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        width: 48
                                        height: 48
                                        radius: 24
                                        color: uiColors.surfaceContainerHigh
                                        Text {
                                            anchors.centerIn: parent
                                            text: "download"
                                            color: uiColors.onSurfaceVariant
                                            font.family: "Material Symbols Rounded"
                                            font.pixelSize: 26
                                        }
                                    }
                                    Label {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "No downloads yet"
                                        color: uiColors.onSurface
                                        font.family: uiColors.fontFamily
                                        font.pixelSize: uiColors.type.titleMedium
                                        font.weight: uiColors.type.weightMedium
                                    }
                                    Label {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "Saved tracks will show their progress here."
                                        color: uiColors.onSurfaceVariant
                                        font.family: uiColors.fontFamily
                                        font.pixelSize: uiColors.type.bodySmall
                                    }
                                }
                            }
                        }
                    }

                    // ---------------------------------------------- settings
                    Item {
                        Flickable {
                            anchors.fill: parent
                            contentWidth: width
                            contentHeight: settingsColumn.height
                            clip: true

                            ScrollBar.vertical: ThemeScrollBar {
                                themeColors: uiColors
                                policy: ScrollBar.AsNeeded
                            }

                            Column {
                                id: settingsColumn
                                width: parent.width
                                spacing: 14

                                Label {
                                    text: "Appearance"
                                    color: uiColors.onSurface
                                    font.family: uiColors.fontFamily
                                    font.pixelSize: uiColors.type.titleLarge
                                    font.weight: uiColors.type.weightMedium
                                    font.letterSpacing: uiColors.type.trackingTitleLarge
                                }

                                Rectangle {
                                    width: parent.width
                                    height: 104
                                    radius: uiColors.shape.medium
                                    color: uiColors.surfaceContainerLow

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 20
                                        spacing: 16

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 3
                                            Label {
                                                text: "Color scheme"
                                                color: uiColors.onSurface
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.titleMedium
                                                font.weight: uiColors.type.weightMedium
                                            }
                                            Label {
                                                text: "Choose how Sonora looks."
                                                color: uiColors.onSurfaceVariant
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.bodySmall
                                            }
                                        }

                                        Repeater {
                                            model: [
                                                { label: "Dark", value: "dark" },
                                                { label: "Light", value: "light" },
                                                { label: "System", value: "system" }
                                            ]
                                            delegate: ShellButton {
                                                themeColors: uiColors
                                                required property var modelData
                                                text: modelData.label
                                                Layout.preferredWidth: 96
                                                variant: appWindow.bridge.theme === modelData.value
                                                    ? "tonal" : "outlined"
                                                leadingIcon: appWindow.bridge.theme === modelData.value
                                                    ? "check" : ""
                                                onClicked: appWindow.bridge.setTheme(modelData.value)
                                            }
                                        }
                                    }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: 104
                                    radius: uiColors.shape.medium
                                    color: uiColors.surfaceContainerLow

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 20
                                        spacing: 12

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 3
                                            Label {
                                                text: "Accent"
                                                color: uiColors.onSurface
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.titleMedium
                                                font.weight: uiColors.type.weightMedium
                                            }
                                            Label {
                                                text: "Pick a colour for buttons and highlights."
                                                color: uiColors.onSurfaceVariant
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.bodySmall
                                            }
                                        }

                                        RowLayout {
                                            spacing: 6
                                            Repeater {
                                                model: [
                                                    { name: "violet", color: "#d0bcff" },
                                                    { name: "blue", color: "#b3c5ff" },
                                                    { name: "green", color: "#a8d4ae" },
                                                    { name: "rose", color: "#f2b8b5" },
                                                    { name: "orange", color: "#ffb77d" }
                                                ]
                                                delegate: Item {
                                                    required property var modelData
                                                    width: 44
                                                    height: 44

                                                    Rectangle {
                                                        anchors.centerIn: parent
                                                        width: 42
                                                        height: 42
                                                        radius: 21
                                                        color: "transparent"
                                                        border.width: appWindow.bridge.accent === modelData.name ? 2 : 0
                                                        border.color: uiColors.primary
                                                        scale: appWindow.bridge.accent === modelData.name ? 1 : 0.82
                                                        opacity: appWindow.bridge.accent === modelData.name ? 1 : 0
                                                        Behavior on scale {
                                                            NumberAnimation {
                                                                duration: uiColors.motion.expressiveFastSpatialDuration
                                                                easing.type: Easing.BezierSpline
                                                                easing.bezierCurve: uiColors.motion.expressiveFastSpatialCurve
                                                            }
                                                        }
                                                        Behavior on opacity {
                                                            NumberAnimation {
                                                                duration: uiColors.motion.expressiveFastEffectsDuration
                                                                easing.type: Easing.BezierSpline
                                                                easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                                                            }
                                                        }
                                                    }

                                                    Rectangle {
                                                        id: swatch
                                                        width: 32
                                                        height: 32
                                                        radius: 16
                                                        anchors.centerIn: parent
                                                        color: modelData.color
                                                        scale: swatchHover.hovered ? 1.12 : 1
                                                        Behavior on scale {
                                                            NumberAnimation {
                                                                duration: uiColors.motion.expressiveFastSpatialDuration
                                                                easing.type: Easing.BezierSpline
                                                                easing.bezierCurve: uiColors.motion.expressiveFastSpatialCurve
                                                            }
                                                        }

                                                        Text {
                                                            anchors.centerIn: parent
                                                            visible: appWindow.bridge.accent === modelData.name
                                                            text: "check"
                                                            color: uiColors.contrastText(modelData.color)
                                                            font.family: "Material Symbols Rounded"
                                                            font.pixelSize: 18
                                                        }

                                                        HoverHandler {
                                                            id: swatchHover
                                                            cursorShape: Qt.PointingHandCursor
                                                        }
                                                        TapHandler {
                                                            onTapped: appWindow.bridge.setAccent(modelData.name)
                                                        }
                                                    }

                                                    Accessible.role: Accessible.Button
                                                    Accessible.name: modelData.name + " accent"
                                                }
                                            }
                                        }
                                    }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: 104
                                    radius: uiColors.shape.medium
                                    color: uiColors.surfaceContainerLow

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 20
                                        spacing: 16

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 3
                                            Label {
                                                text: appWindow.bridge.authenticated
                                                    ? "YouTube Music connected"
                                                    : "Connect YouTube Music"
                                                color: uiColors.onSurface
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.titleMedium
                                                font.weight: uiColors.type.weightMedium
                                            }
                                            Label {
                                                text: appWindow.bridge.authenticated
                                                    ? "Your library and liked songs are ready."
                                                    : "Use request headers from a signed-in browser."
                                                color: uiColors.onSurfaceVariant
                                                font.family: uiColors.fontFamily
                                                font.pixelSize: uiColors.type.bodySmall
                                            }
                                        }

                                        ShellButton {
                                            themeColors: uiColors
                                            text: appWindow.bridge.authenticated ? "Sign out" : "Sign in"
                                            variant: appWindow.bridge.authenticated ? "outlined" : "filled"
                                            onClicked: appWindow.bridge.authenticated
                                                ? appWindow.bridge.signOut() : accountDialog.open()
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

    function pageTitle(page) {
        return ({
            home: "Home",
            search: "Search",
            library: "Your library",
            downloads: "Downloads",
            settings: "Settings"
        })[page] || "Sonora"
    }

    function pageSubtitle(page) {
        return ({
            home: "Settle in and find your next favorite.",
            search: "Find the track that fits this moment.",
            library: "Your music, all in one place.",
            downloads: "Keep your favorites close.",
            settings: "Make Sonora feel like yours."
        })[page] || ""
    }

    function formatDuration(seconds) {
        const duration = Math.max(0, Number(seconds) || 0)
        return Math.floor(duration / 60) + ":" + String(Math.floor(duration % 60)).padStart(2, "0")
    }

    // ------------------------------------------------------------ app bar
    header: Rectangle {
        implicitHeight: 72
        color: uiColors.surface

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
            color: uiColors.outlineVariant
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 20
            spacing: 14

            Rectangle {
                width: 38
                height: 38
                radius: uiColors.shape.medium
                color: uiColors.primaryContainer
                Text {
                    anchors.centerIn: parent
                    text: "graphic_eq"
                    color: uiColors.onPrimaryContainer
                    font.family: "Material Symbols Rounded"
                    font.pixelSize: 24
                }
            }

            Label {
                text: "sonora"
                color: uiColors.onSurface
                font.family: uiColors.fontFamily
                font.pixelSize: uiColors.type.titleLarge
                font.weight: uiColors.type.weightMedium
                font.letterSpacing: -0.2
                Layout.preferredWidth: 112
            }

            TextField {
                id: globalSearch
                objectName: "globalSearch"
                Layout.preferredWidth: 330
                Layout.maximumWidth: 430
                Layout.fillWidth: true
                implicitHeight: 48
                placeholderText: "Search songs, artists, albums…"
                selectByMouse: true
                hoverEnabled: true
                color: uiColors.onSurface
                placeholderTextColor: uiColors.onSurfaceVariant
                font.family: uiColors.fontFamily
                font.pixelSize: uiColors.type.bodyMedium
                leftPadding: 44
                rightPadding: text !== "" ? 38 : 16
                topPadding: 0
                bottomPadding: 0
                verticalAlignment: TextInput.AlignVCenter
                onAccepted: {
                    appWindow.bridge.setPage("search")
                    appWindow.navigate("search")
                    appWindow.bridge.search(text)
                }
                background: Rectangle {
                    radius: height / 2
                    color: globalSearch.activeFocus
                        ? uiColors.surfaceContainerHighest
                        : globalSearch.hovered
                            ? uiColors.surfaceContainerHigh
                            : uiColors.surfaceContainerHigh
                    border.width: globalSearch.activeFocus ? 1 : 0
                    border.color: uiColors.primary

                    Behavior on color {
                        ColorAnimation {
                            duration: uiColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                        }
                    }
                    Behavior on border.color {
                        ColorAnimation {
                            duration: uiColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                        }
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 15
                        anchors.verticalCenter: parent.verticalCenter
                        text: "search"
                        color: globalSearch.activeFocus
                            ? uiColors.primary : uiColors.onSurfaceVariant
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 22
                        Behavior on color {
                            ColorAnimation {
                                duration: uiColors.motion.expressiveFastEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                            }
                        }
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: "close"
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 18
                        color: uiColors.onSurfaceVariant
                        visible: globalSearch.text !== ""
                        opacity: globalSearch.text !== "" ? 1 : 0

                        Behavior on opacity {
                            NumberAnimation { duration: 150 }
                        }

                        MouseArea {
                            anchors.fill: parent
                            anchors.margins: -4
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                globalSearch.text = ""
                                globalSearch.forceActiveFocus()
                            }
                        }
                    }
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                implicitWidth: statusRow.implicitWidth + 24
                implicitHeight: 28
                radius: 14
                color: uiColors.surfaceContainerHigh

                RowLayout {
                    id: statusRow
                    anchors.centerIn: parent
                    spacing: 7

                    Rectangle {
                        width: 6
                        height: 6
                        radius: 3
                        color: appWindow.bridge.authenticated
                            ? uiColors.primary : uiColors.outline
                        Behavior on color {
                            ColorAnimation {
                                duration: uiColors.motion.expressiveDefaultEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: uiColors.motion.expressiveDefaultEffectsCurve
                            }
                        }
                    }
                    Label {
                        text: appWindow.bridge.authenticated ? "CONNECTED" : "OFFLINE"
                        color: uiColors.onSurfaceVariant
                        font.family: uiColors.fontFamily
                        font.pixelSize: uiColors.type.labelSmall
                        font.weight: uiColors.type.weightMedium
                        font.letterSpacing: 0.9
                    }
                }
            }

            ThemeToolButton {
                themeColors: uiColors
                icon: appWindow.bridge.darkTheme ? "dark_mode" : "light_mode"
                iconSize: 22
                ToolTip.text: "Toggle color scheme"
                ToolTip.visible: hovered
                onClicked: appWindow.bridge.setTheme(
                    appWindow.bridge.darkTheme ? "light" : "dark")
            }

            ShellButton {
                themeColors: uiColors
                text: appWindow.bridge.authenticated ? "Account" : "Sign in"
                variant: appWindow.bridge.authenticated ? "tonal" : "filled"
                onClicked: accountDialog.open()
            }
        }
    }

    // --------------------------------------------------- rail + content
    RowLayout {
        anchors.fill: parent
        anchors.bottomMargin: 104
        spacing: 0

        Rectangle {
            id: sidebar
            Layout.fillHeight: true
            Layout.preferredWidth: navRail.expanded ? 240 : 76
            Layout.minimumWidth: navRail.expanded ? 240 : 76
            Layout.maximumWidth: navRail.expanded ? 240 : 76
            color: uiColors.surfaceContainerLow
            clip: true

            Behavior on Layout.preferredWidth {
                NumberAnimation {
                    duration: uiColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultSpatialCurve
                }
            }
            Behavior on Layout.minimumWidth {
                NumberAnimation {
                    duration: uiColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultSpatialCurve
                }
            }
            Behavior on Layout.maximumWidth {
                NumberAnimation {
                    duration: uiColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultSpatialCurve
                }
            }

            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 1
                color: uiColors.outlineVariant
            }

            NavRail {
                id: navRail
                anchors.fill: parent
                anchors.leftMargin: 4
                anchors.rightMargin: 4
                anchors.topMargin: 8
                anchors.bottomMargin: 4
                themeColors: uiColors
                currentPage: appWindow.bridge.currentPage
                onNavigate: function(page) { appWindow.navigate(page) }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            LinearProgress {
                themeColors: uiColors
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 6
                visible: appWindow.bridge.busy
                value: -1
                color: uiColors.primary
                z: 50
            }

            StackView {
                id: pageStack
                anchors.fill: parent
                anchors.leftMargin: 32
                anchors.rightMargin: 32
                anchors.topMargin: 28
                anchors.bottomMargin: 24
                initialItem: pageComponent

                // M3 top-level transition: the outgoing view fades away
                // quickly, then the incoming view fades through.
                replaceEnter: Transition {
                    SequentialAnimation {
                        PauseAnimation { duration: uiColors.motion.short1 }
                        NumberAnimation {
                            property: "opacity"
                            from: 0
                            to: 1
                            duration: uiColors.motion.expressiveDefaultEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: uiColors.motion.expressiveDefaultEffectsCurve
                        }
                    }
                }
                replaceExit: Transition {
                    NumberAnimation {
                        property: "opacity"
                        from: 1
                        to: 0
                        duration: uiColors.motion.expressiveFastEffectsDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                    }
                }
            }

            // ─── SHORT PAGE TRANSITION LOADING OVERLAY ───
            Rectangle {
                id: pageTransitionOverlay
                anchors.fill: parent
                color: Qt.rgba(uiColors.surface.r, uiColors.surface.g, uiColors.surface.b, 0.94)
                opacity: pageTransitioning ? 1.0 : 0.0
                visible: opacity > 0.001
                z: 60

                Behavior on opacity {
                    NumberAnimation {
                        duration: pageTransitioning ? 100 : 180
                        easing.type: Easing.OutCubic
                    }
                }

                // Absorb clicks during page loading
                MouseArea {
                    anchors.fill: parent
                    enabled: pageTransitioning
                }

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    LoadingIndicator {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 44
                        height: 44
                        themeColors: uiColors
                        running: pageTransitioning
                        color: uiColors.primary
                    }

                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: pendingPage !== "" ? ("Loading " + appWindow.pageTitle(pendingPage) + "…") : "Loading…"
                        color: uiColors.onSurface
                        font.family: uiColors.fontFamily
                        font.pixelSize: uiColors.type.titleSmall
                        font.weight: uiColors.type.weightMedium
                        font.letterSpacing: 0.1
                    }
                }
            }
        }
    }

    PlayerBar {
        id: playerDock
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        bridge: appWindow.bridge
        themeColors: uiColors
        onQueueRequested: queueDialog.open()
        onExpandRequested: fullPlayer.isExpanded = true
    }

    FullPlayerWindow {
        id: fullPlayer
        bridge: appWindow.bridge
        themeColors: uiColors
        z: 80
        onQueueRequested: queueDialog.open()
    }

    Connections {
        target: appWindow.bridge
        ignoreUnknownSignals: true
        function onNowPlayingChanged() {
            if (appWindow.bridge && appWindow.bridge.nowPlaying && appWindow.bridge.nowPlaying.title) {
                fullPlayer.isExpanded = true
            }
        }
    }

    // ------------------------------------------------------------ dialogs
    Dialog {
        id: queueDialog
        objectName: "queueDialog"
        palette: appWindow.palette
        anchors.centerIn: parent
        width: Math.min(560, appWindow.width - 48)
        height: Math.min(620, appWindow.height - 100)
        modal: true
        title: "Playback queue"

        enter: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: uiColors.motion.expressiveDefaultEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultEffectsCurve
                }
                NumberAnimation {
                    property: "scale"
                    from: 0.92
                    to: 1
                    duration: uiColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultSpatialCurve
                }
            }
        }
        exit: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: uiColors.motion.expressiveFastEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                }
                NumberAnimation {
                    property: "scale"
                    from: 1
                    to: 0.96
                    duration: uiColors.motion.expressiveFastSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveFastSpatialCurve
                }
            }
        }

        header: Rectangle {
            implicitHeight: 64
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 12
                Label {
                    Layout.fillWidth: true
                    text: queueDialog.title
                    color: uiColors.onSurface
                    font.family: uiColors.fontFamily
                    font.pixelSize: uiColors.type.titleLarge
                    font.weight: uiColors.type.weightMedium
                }
                ThemeToolButton {
                    themeColors: uiColors
                    icon: "close"
                    iconSize: 22
                    ToolTip.text: "Close queue"
                    onClicked: queueDialog.close()
                }
            }
        }

        background: Rectangle {
            color: uiColors.surfaceContainerHigh
            radius: uiColors.shape.extraLarge
        }

        contentItem: ColumnLayout {
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                Label {
                    Layout.fillWidth: true
                    text: appWindow.bridge.queueItems.length + " tracks"
                    color: uiColors.onSurfaceVariant
                    font.family: uiColors.fontFamily
                    font.pixelSize: uiColors.type.bodyMedium
                }
                ShellButton {
                    themeColors: uiColors
                    variant: "text"
                    text: "Clear upcoming"
                    enabled: appWindow.bridge.queueItems.length > 0
                    onClicked: appWindow.bridge.clearUpcoming()
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: queueList
                    anchors.fill: parent
                    clip: true
                    spacing: 6
                    model: appWindow.bridge.queueItems
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: ThemeScrollBar {
                        themeColors: uiColors
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                        required property var modelData
                        required property int index

                        readonly property bool current: index === appWindow.bridge.queueIndex

                        width: queueList.width - 10
                        height: 60
                        radius: uiColors.shape.medium
                        color: current
                            ? uiColors.primaryContainer : uiColors.surfaceContainerLow
                        border.width: 1
                        border.color: current
                            ? uiColors.primary : uiColors.outlineVariant

                        Behavior on color {
                            ColorAnimation {
                                duration: uiColors.motion.expressiveDefaultEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: uiColors.motion.expressiveDefaultEffectsCurve
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 14
                            anchors.rightMargin: 6
                            spacing: 4

                            EqualizerBars {
                                themeColors: uiColors
                                visible: current && appWindow.bridge.playing
                                width: 14
                                height: 14
                                color: uiColors.onPrimaryContainer
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1
                                Label {
                                    Layout.fillWidth: true
                                    text: modelData.title || "Unknown title"
                                    color: current
                                        ? uiColors.onPrimaryContainer : uiColors.onSurface
                                    font.family: uiColors.fontFamily
                                    font.pixelSize: uiColors.type.bodyMedium
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: modelData.artist || "Unknown artist"
                                    color: current
                                        ? uiColors.onPrimaryContainer : uiColors.onSurfaceVariant
                                    opacity: 0.8
                                    font.family: uiColors.fontFamily
                                    font.pixelSize: uiColors.type.bodySmall
                                    elide: Text.ElideRight
                                }
                            }

                            ThemeToolButton {
                                themeColors: uiColors
                                iconColor: current
                                    ? uiColors.onPrimaryContainer : uiColors.onSurfaceVariant
                                icon: "arrow_upward"
                                iconSize: 20
                                enabled: index > appWindow.bridge.queueIndex + 1
                                ToolTip.text: "Move up"
                                ToolTip.visible: hovered
                                onClicked: appWindow.bridge.moveQueueItem(index, -1)
                            }
                            ThemeToolButton {
                                themeColors: uiColors
                                iconColor: current
                                    ? uiColors.onPrimaryContainer : uiColors.onSurfaceVariant
                                icon: "arrow_downward"
                                iconSize: 20
                                enabled: index > appWindow.bridge.queueIndex
                                    && index < appWindow.bridge.queueItems.length - 1
                                ToolTip.text: "Move down"
                                ToolTip.visible: hovered
                                onClicked: appWindow.bridge.moveQueueItem(index, 1)
                            }
                            ThemeToolButton {
                                themeColors: uiColors
                                iconColor: current
                                    ? uiColors.onPrimaryContainer : uiColors.onSurfaceVariant
                                icon: "play_arrow"
                                iconSize: 22
                                ToolTip.text: "Play"
                                ToolTip.visible: hovered
                                onClicked: appWindow.bridge.playQueueItem(index)
                            }
                            ThemeToolButton {
                                themeColors: uiColors
                                iconColor: current
                                    ? uiColors.onPrimaryContainer : uiColors.onSurfaceVariant
                                icon: "delete"
                                iconSize: 20
                                ToolTip.text: "Remove"
                                ToolTip.visible: hovered
                                onClicked: appWindow.bridge.removeQueueItem(index)
                            }
                        }
                    }
                }

                Label {
                    anchors.centerIn: parent
                    visible: appWindow.bridge.queueItems.length === 0
                    text: "Nothing queued"
                    color: uiColors.onSurfaceVariant
                    font.family: uiColors.fontFamily
                    font.pixelSize: uiColors.type.bodyMedium
                }
            }
        }
    }

    Dialog {
        id: accountDialog
        objectName: "accountDialog"
        palette: appWindow.palette
        anchors.centerIn: parent
        width: Math.min(520, appWindow.width - 48)
        modal: true
        title: "Connect YouTube Music"

        enter: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: uiColors.motion.expressiveDefaultEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultEffectsCurve
                }
                NumberAnimation {
                    property: "scale"
                    from: 0.92
                    to: 1
                    duration: uiColors.motion.expressiveDefaultSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveDefaultSpatialCurve
                }
            }
        }
        exit: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: uiColors.motion.expressiveFastEffectsDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                }
                NumberAnimation {
                    property: "scale"
                    from: 1
                    to: 0.96
                    duration: uiColors.motion.expressiveFastSpatialDuration
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: uiColors.motion.expressiveFastSpatialCurve
                }
            }
        }

        header: Rectangle {
            implicitHeight: 64
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 12
                Label {
                    Layout.fillWidth: true
                    text: accountDialog.title
                    color: uiColors.onSurface
                    font.family: uiColors.fontFamily
                    font.pixelSize: uiColors.type.titleLarge
                    font.weight: uiColors.type.weightMedium
                }
                ThemeToolButton {
                    themeColors: uiColors
                    icon: "close"
                    iconSize: 22
                    ToolTip.text: "Close sign-in"
                    onClicked: accountDialog.close()
                }
            }
        }

        background: Rectangle {
            color: uiColors.surfaceContainerHigh
            radius: uiColors.shape.extraLarge
        }

        ColumnLayout {
            width: parent.width
            spacing: 14

            Label {
                Layout.fillWidth: true
                text: "Paste request headers copied from a signed-in music.youtube.com browser session. Treat these headers like a password."
                wrapMode: Text.Wrap
                color: uiColors.onSurfaceVariant
                font.family: uiColors.fontFamily
                font.pixelSize: uiColors.type.bodyMedium
                lineHeight: 1.35
            }

            Label {
                text: "Request headers"
                color: uiColors.onSurfaceVariant
                font.family: uiColors.fontFamily
                font.pixelSize: uiColors.type.labelMedium
                font.weight: uiColors.type.weightMedium
                font.letterSpacing: uiColors.type.trackingLabelMedium
            }

            TextArea {
                id: headersText
                Layout.fillWidth: true
                Layout.preferredHeight: 160
                placeholderText: "Paste request headers here…"
                placeholderTextColor: uiColors.onSurfaceVariant
                wrapMode: TextEdit.Wrap
                selectByMouse: true
                color: uiColors.onSurface
                font.family: uiColors.fontFamily
                font.pixelSize: uiColors.type.bodyMedium
                leftPadding: 14
                rightPadding: 14
                topPadding: 12
                bottomPadding: 12
                background: Rectangle {
                    color: uiColors.surfaceContainerLow
                    radius: uiColors.shape.extraSmall
                    border.width: headersText.activeFocus ? 2 : 1
                    border.color: headersText.activeFocus
                        ? uiColors.primary : uiColors.outline
                    Behavior on border.color {
                        ColorAnimation {
                            duration: uiColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: uiColors.motion.expressiveFastEffectsCurve
                        }
                    }
                }
            }

            ShellButton {
                themeColors: uiColors
                Layout.alignment: Qt.AlignRight
                text: "Save headers"
                primary: true
                onClicked: {
                    if (headersText.text.trim().length === 0) {
                        appWindow.bridge.showToast("Paste request headers before saving.")
                        return
                    }
                    appWindow.bridge.signInWithHeaders(headersText.text)
                    headersText.clear()
                    accountDialog.close()
                }
            }
        }
    }

    // ----------------------------------------------------------- snackbar
    Snackbar {
        id: toastCard
        z: 20
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: playerDock.top
        anchors.bottomMargin: 16
        themeColors: uiColors
        maxWidth: Math.min(460, appWindow.width - 48)
    }

    Timer {
        id: toastTimer
        interval: 4000
        onTriggered: toastCard.shown = false
    }

    Connections {
        target: appWindow.bridge
        function onToast(message) {
            toastCard.message = message
            toastCard.shown = true
            toastTimer.restart()
        }
    }
}
