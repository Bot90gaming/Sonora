import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
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
    color: uiColors.background
    palette.window: uiColors.background
    palette.windowText: uiColors.text
    palette.base: uiColors.panel
    palette.alternateBase: uiColors.surface
    palette.text: uiColors.text
    palette.button: uiColors.surface
    palette.buttonText: uiColors.text
    palette.brightText: uiColors.accent
    palette.highlight: uiColors.accent
    palette.highlightedText: uiColors.accentText
    palette.placeholderText: uiColors.muted
    palette.toolTipBase: uiColors.tooltip
    palette.toolTipText: uiColors.tooltipText
    palette.light: uiColors.raised
    palette.midlight: uiColors.surface
    palette.mid: uiColors.border
    palette.dark: uiColors.background
    palette.shadow: uiColors.scrim
    palette.link: uiColors.accent
    palette.linkVisited: uiColors.accent

    Overlay.modal: Rectangle {
        color: uiColors.scrim
    }

    ThemeConfig {
        id: uiColors
        bridge: appWindow.bridge
    }

    function navigate(page) {
        appWindow.bridge.setPage(page)
        if (pageStack.currentItem && pageStack.currentItem.pageName === page)
            return
        pageStack.replace(pageComponent, { pageName: page })
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
                            color: uiColors.text
                            font.pixelSize: 29
                            font.weight: Font.DemiBold
                        }
                        Label {
                            text: appWindow.pageSubtitle(pageName)
                            color: uiColors.muted
                            font.pixelSize: 13
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
                                spacing: 26

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 1.6
                                    spacing: 12

                                    RowLayout {
                                        Layout.fillWidth: true
                                        Label {
                                            Layout.fillWidth: true
                                            text: "Newest"
                                            color: uiColors.text
                                            font.pixelSize: 20
                                            font.weight: Font.DemiBold
                                        }
                                        Label {
                                            visible: appWindow.bridge.busy
                                            text: "Refreshing..."
                                            color: uiColors.muted
                                            font.pixelSize: 12
                                        }
                                        ShellButton {
                                            themeColors: uiColors
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

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 12
                            RowLayout {
                                Layout.fillWidth: true
                                Repeater {
                                    model: [
                                        { title: "Songs", value: "songs" },
                                        { title: "Albums", value: "albums" },
                                        { title: "Playlists", value: "playlists" }
                                    ]
                                    delegate: ShellButton {
                                        required property var modelData
                                        themeColors: uiColors
                                        text: modelData.title
                                        primary: appWindow.bridge.searchFilter === modelData.value
                                        onClicked: appWindow.bridge.setSearchFilter(modelData.value)
                                    }
                                }
                                Item { Layout.fillWidth: true }
                            }
                            Label {
                                visible: appWindow.bridge.searchResults.length === 0
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                                text: appWindow.bridge.busy ? "Searching..." : "Search for something you love"
                                color: uiColors.muted
                                font.pixelSize: 15
                            }
                            TrackList {
                                themeColors: uiColors
                                service: appWindow.bridge
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: appWindow.bridge.searchResults
                            }
                        }
                    }

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 14
                            Rectangle {
                                visible: !appWindow.bridge.authenticated
                                Layout.fillWidth: true
                                Layout.preferredHeight: 92
                                radius: 22
                                color: uiColors.surface
                                border.color: uiColors.border
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 22
                                    anchors.rightMargin: 18
                                    Label {
                                        Layout.fillWidth: true
                                        text: "Sign in to browse your Liked Songs."
                                        color: uiColors.text
                                    }
                                    ShellButton {
                                        themeColors: uiColors
                                        text: "Sign in"
                                        primary: true
                                        onClicked: accountDialog.open()
                                    }
                                }
                            }
                            TrackList {
                                themeColors: uiColors
                                service: appWindow.bridge
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: appWindow.bridge.libraryItems
                                visible: appWindow.bridge.authenticated
                            }
                        }
                    }

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 14
                            Label {
                                text: "Your downloads are saved to your Music folder."
                                color: uiColors.muted
                                font.pixelSize: 14
                            }
                            Label {
                                text: "Choose Download on any track to save an offline copy."
                                color: uiColors.muted
                                font.pixelSize: 13
                            }
                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 8
                                model: appWindow.bridge.downloads
                                ScrollBar.vertical: ThemeScrollBar {
                                    themeColors: uiColors
                                    policy: ScrollBar.AsNeeded
                                }
                                delegate: Rectangle {
                                    required property var modelData
                                    width: ListView.view.width - 8
                                    height: 64
                                    radius: 18
                                    color: uiColors.surface
                                    border.color: uiColors.border
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 16
                                        anchors.rightMargin: 16
                                        Label {
                                            Layout.fillWidth: true
                                            text: modelData.title + " · " + modelData.artist
                                            color: uiColors.text
                                            elide: Text.ElideRight
                                        }
                                        Label {
                                            text: modelData.status
                                            color: uiColors.muted
                                        }
                                        Label {
                                            text: modelData.progress + "%"
                                            color: uiColors.accent
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 18
                            Label {
                                text: "Appearance"
                                color: uiColors.text
                                font.pixelSize: 18
                                font.weight: Font.DemiBold
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 104
                                radius: 22
                                color: uiColors.surface
                                border.color: uiColors.border
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 18
                                    Label {
                                        text: "Color scheme"
                                        color: uiColors.text
                                        Layout.fillWidth: true
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
                                            primary: appWindow.bridge.theme === modelData.value
                                            onClicked: appWindow.bridge.setTheme(modelData.value)
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 104
                                radius: 22
                                color: uiColors.surface
                                border.color: uiColors.border
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 18
                                    Label {
                                        text: "Accent"
                                        color: uiColors.text
                                        Layout.fillWidth: true
                                    }
                                    Repeater {
                                        model: [
                                            { name: "violet", color: "#d0bcff" },
                                            { name: "blue", color: "#b3c5ff" },
                                            { name: "green", color: "#a8d4ae" },
                                            { name: "rose", color: "#f2b8b5" },
                                            { name: "orange", color: "#ffb77d" }
                                        ]
                                        delegate: Rectangle {
                                            required property var modelData
                                            width: 34
                                            height: 34
                                            radius: 17
                                            color: modelData.color
                                            border.width: appWindow.bridge.accent === modelData.name ? 3 : 0
                                            border.color: uiColors.text
                                            scale: accentMouse.containsMouse ? 1.12 : 1
                                            Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutBack } }
                                            MouseArea {
                                                id: accentMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                onClicked: appWindow.bridge.setAccent(modelData.name)
                                            }
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 104
                                radius: 22
                                color: uiColors.surface
                                border.color: uiColors.border
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 18
                                    Label {
                                        Layout.fillWidth: true
                                        text: appWindow.bridge.authenticated ? "YouTube Music connected" : "Connect YouTube Music"
                                        color: uiColors.text
                                    }
                                    ShellButton {
                                        themeColors: uiColors
                                        text: appWindow.bridge.authenticated ? "Sign out" : "Sign in"
                                        onClicked: appWindow.bridge.authenticated ? appWindow.bridge.signOut() : accountDialog.open()
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

    header: Rectangle {
        implicitHeight: 72
        color: uiColors.panel
        border.color: uiColors.border
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 24
            spacing: 14
            Rectangle {
                width: 38
                height: 38
                radius: 14
                color: uiColors.accent
                Text {
                    anchors.centerIn: parent
                    text: "♫"
                    color: uiColors.accentText
                    font.pixelSize: 22
                    font.weight: Font.Bold
                }
            }
            Label {
                text: "sonora"
                color: uiColors.text
                font.pixelSize: 19
                font.weight: Font.DemiBold
                Layout.preferredWidth: 112
            }
            TextField {
                id: globalSearch
                objectName: "globalSearch"
                Layout.preferredWidth: 330
                Layout.maximumWidth: 430
                Layout.fillWidth: true
                placeholderText: "Search songs, artists, albums..."
                selectByMouse: true
                color: uiColors.text
                placeholderTextColor: uiColors.muted
                leftPadding: 42
                rightPadding: 16
                onAccepted: {
                    appWindow.bridge.setPage("search")
                    appWindow.navigate("search")
                    appWindow.bridge.search(text)
                }
                background: Rectangle {
                    radius: 12
                    color: uiColors.surface
                    border.color: globalSearch.activeFocus
                        ? uiColors.accent : uiColors.border
                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "⌕"
                        color: uiColors.muted
                        font.pixelSize: 20
                    }
                    Behavior on border.color { ColorAnimation { duration: 160 } }
                }
            }
            Item { Layout.fillWidth: true }
            Label {
                text: appWindow.bridge.authenticated ? "CONNECTED" : "YOUR MUSIC SPACE"
                color: uiColors.muted
                font.pixelSize: 10
                font.letterSpacing: 1.2
                font.weight: Font.Bold
            }
            ThemeToolButton {
                themeColors: uiColors
                text: appWindow.bridge.darkTheme ? "☾" : "☀"
                contentItem: Text {
                    text: parent.text
                    color: uiColors.text
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                ToolTip.text: "Toggle color scheme"
                ToolTip.visible: hovered
                onClicked: appWindow.bridge.setTheme(
                    appWindow.bridge.darkTheme ? "light" : "dark")
            }
            ShellButton {
                themeColors: uiColors
                text: appWindow.bridge.authenticated ? "Account" : "Sign in"
                primary: !appWindow.bridge.authenticated
                onClicked: accountDialog.open()
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.bottomMargin: 104
        spacing: 0

        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 220
            Layout.minimumWidth: 190
            Layout.maximumWidth: 240
            color: uiColors.panel
            border.color: uiColors.border
            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                anchors.topMargin: 18
                anchors.bottomMargin: 16
                spacing: 6
                Label {
                    Layout.fillWidth: true
                    Layout.leftMargin: 10
                    Layout.bottomMargin: 6
                    text: "Main page"
                    color: uiColors.muted
                    font.pixelSize: 11
                }
                Repeater {
                    model: [
                        { name: "Home", page: "home", icon: "⌂" },
                        { name: "Search", page: "search", icon: "⌕" },
                        { name: "Library", page: "library", icon: "♫" },
                        { name: "Downloads", page: "downloads", icon: "↓" }
                    ]
                    delegate: Item {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        Rectangle {
                            anchors.fill: parent
                            radius: 12
                            color: appWindow.bridge.currentPage === modelData.page ? uiColors.accent : navMouse.containsMouse ? uiColors.raised : "transparent"
                            Behavior on color { ColorAnimation { duration: 190 } }
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                spacing: 12
                                Text {
                                    Layout.preferredWidth: 18
                                    text: modelData.icon
                                    color: appWindow.bridge.currentPage === modelData.page ? uiColors.accentText : uiColors.muted
                                    font.pixelSize: 19
                                    horizontalAlignment: Text.AlignHCenter
                                    Behavior on color { ColorAnimation { duration: 190 } }
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: modelData.name
                                    color: appWindow.bridge.currentPage === modelData.page ? uiColors.accentText : uiColors.text
                                    font.pixelSize: 13
                                }
                            }
                            MouseArea {
                                id: navMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: appWindow.navigate(modelData.page)
                            }
                        }
                        ToolTip.visible: navMouse.containsMouse
                        ToolTip.text: modelData.name
                    }
                }
                Item { Layout.fillHeight: true }
                Label {
                    Layout.fillWidth: true
                    Layout.leftMargin: 10
                    Layout.bottomMargin: 4
                    text: "For Me"
                    color: uiColors.muted
                    font.pixelSize: 11
                }
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    Rectangle {
                        anchors.fill: parent
                        radius: 12
                        color: appWindow.bridge.currentPage === "settings" ? uiColors.accent : settingsMouse.containsMouse ? uiColors.raised : "transparent"
                    }
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        spacing: 12
                        Text {
                            Layout.preferredWidth: 18
                            text: "⚙"
                            color: appWindow.bridge.currentPage === "settings" ? uiColors.accentText : uiColors.muted
                            font.pixelSize: 18
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "Settings"
                            color: appWindow.bridge.currentPage === "settings" ? uiColors.accentText : uiColors.text
                            font.pixelSize: 13
                        }
                    }
                    MouseArea {
                        id: settingsMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: appWindow.navigate("settings")
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            StackView {
                id: pageStack
                anchors.fill: parent
                anchors.leftMargin: 32
                anchors.rightMargin: 32
                anchors.topMargin: 28
                anchors.bottomMargin: 24
                initialItem: pageComponent
                replaceEnter: Transition {
                    ParallelAnimation {
                        NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 260; easing.type: Easing.OutCubic }
                        NumberAnimation { property: "y"; from: 12; to: 0; duration: 260; easing.type: Easing.OutCubic }
                    }
                }
                replaceExit: Transition {
                    ParallelAnimation {
                        NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 150; easing.type: Easing.InCubic }
                        NumberAnimation { property: "y"; from: 0; to: -6; duration: 150; easing.type: Easing.InCubic }
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
    }

    Dialog {
        id: queueDialog
        objectName: "queueDialog"
        palette: appWindow.palette
        anchors.centerIn: parent
        width: Math.min(560, appWindow.width - 48)
        height: Math.min(620, appWindow.height - 100)
        modal: true
        title: "Playback queue"
        header: Rectangle {
            implicitHeight: 56
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 12
                Label {
                    Layout.fillWidth: true
                    text: queueDialog.title
                    color: uiColors.text
                    font.pixelSize: 17
                    font.weight: Font.DemiBold
                }
                ThemeToolButton {
                    themeColors: uiColors
                    text: "×"
                    font.pixelSize: 22
                    ToolTip.text: "Close queue"
                    onClicked: queueDialog.close()
                }
            }
        }
        background: Rectangle {
            color: uiColors.panel
            radius: 26
            border.color: uiColors.border
        }
        contentItem: ColumnLayout {
            spacing: 12
            RowLayout {
                Layout.fillWidth: true
                Label {
                    Layout.fillWidth: true
                    text: appWindow.bridge.queueItems.length + " tracks"
                    color: uiColors.muted
                }
                ShellButton {
                    themeColors: uiColors
                    text: "Clear upcoming"
                    enabled: appWindow.bridge.queueItems.length > 0
                    onClicked: appWindow.bridge.clearUpcoming()
                }
            }
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 8
                model: appWindow.bridge.queueItems
                ScrollBar.vertical: ThemeScrollBar {
                    themeColors: uiColors
                    policy: ScrollBar.AsNeeded
                }
                delegate: Rectangle {
                    required property var modelData
                    required property int index
                    width: ListView.view.width - 8
                    height: 60
                    radius: 16
                    color: index === appWindow.bridge.queueIndex
                        ? uiColors.raised : uiColors.surface
                    border.color: index === appWindow.bridge.queueIndex
                        ? uiColors.accent : uiColors.border
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 8
                        Label {
                            Layout.fillWidth: true
                            text: modelData.title + " · " + modelData.artist
                            color: uiColors.text
                            elide: Text.ElideRight
                        }
                        ThemeToolButton {
                            themeColors: uiColors
                            text: "↑"
                            enabled: index > appWindow.bridge.queueIndex + 1
                            onClicked: appWindow.bridge.moveQueueItem(index, -1)
                        }
                        ThemeToolButton {
                            themeColors: uiColors
                            text: "↓"
                            enabled: index > appWindow.bridge.queueIndex
                                && index < appWindow.bridge.queueItems.length - 1
                            onClicked: appWindow.bridge.moveQueueItem(index, 1)
                        }
                        ThemeToolButton {
                            themeColors: uiColors
                            text: "▶"
                            onClicked: appWindow.bridge.playQueueItem(index)
                        }
                        ThemeToolButton {
                            themeColors: uiColors
                            text: "×"
                            onClicked: appWindow.bridge.removeQueueItem(index)
                        }
                    }
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
        header: Rectangle {
            implicitHeight: 56
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 12
                Label {
                    Layout.fillWidth: true
                    text: accountDialog.title
                    color: uiColors.text
                    font.pixelSize: 17
                    font.weight: Font.DemiBold
                }
                ThemeToolButton {
                    themeColors: uiColors
                    text: "×"
                    font.pixelSize: 22
                    ToolTip.text: "Close sign-in"
                    onClicked: accountDialog.close()
                }
            }
        }
        background: Rectangle {
            color: uiColors.panel
            radius: 26
            border.color: uiColors.border
        }
        ColumnLayout {
            width: parent.width
            spacing: 14
            Label {
                Layout.fillWidth: true
                text: "Paste request headers copied from a signed-in music.youtube.com browser session. Treat these headers like a password."
                wrapMode: Text.Wrap
                color: uiColors.muted
            }
            TextArea {
                id: headersText
                Layout.fillWidth: true
                Layout.preferredHeight: 160
                placeholderText: "Paste request headers here…"
                wrapMode: TextEdit.Wrap
                selectByMouse: true
                color: uiColors.text
                background: Rectangle {
                    color: uiColors.surface
                    radius: 16
                    border.color: headersText.activeFocus ? uiColors.accent : uiColors.border
                    Behavior on border.color { ColorAnimation { duration: 180 } }
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

    Rectangle {
        id: toastCard
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: playerDock.top
        anchors.bottomMargin: 16
        width: Math.min(toastText.implicitWidth + 36, appWindow.width - 48)
        height: toastText.implicitHeight + 24
        radius: 18
        color: uiColors.raised
        border.color: uiColors.border
        opacity: 0
        y: 12
        z: 10
        Text {
            id: toastText
            anchors.centerIn: parent
            width: Math.min(implicitWidth, appWindow.width - 84)
            text: ""
            color: uiColors.text
            font.pixelSize: 13
            wrapMode: Text.Wrap
        }
        Connections {
            target: appWindow.bridge
            function onToast(message) {
                toastText.text = message
                toastCard.opacity = 1
                toastCard.y = 0
                toastTimer.restart()
            }
        }
        Behavior on opacity { NumberAnimation { duration: 180 } }
        Behavior on y { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
        Timer {
            id: toastTimer
            interval: 3000
            onTriggered: {
                toastCard.opacity = 0
                toastCard.y = 12
            }
        }
    }
}
