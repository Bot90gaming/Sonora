import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

// M3 filled cards for playlists and albums. Cards lift slightly on hover and
// expose a filled affordance for opening the collection.
ColumnLayout {
    id: playlistGrid
    required property var model
    required property var service
    required property var themeColors
    required property string emptyLabel

    spacing: 12

    RowLayout {
        Layout.fillWidth: true
        Label {
            Layout.fillWidth: true
            text: "Play List"
            color: playlistGrid.themeColors.onSurface
            font.family: playlistGrid.themeColors.fontFamily
            font.pixelSize: playlistGrid.themeColors.type.titleLarge
            font.weight: playlistGrid.themeColors.type.weightMedium
            font.letterSpacing: playlistGrid.themeColors.type.trackingTitleLarge
        }
        Label {
            visible: playlistGrid.model.length === 0
            text: playlistGrid.emptyLabel
            color: playlistGrid.themeColors.onSurfaceVariant
            font.family: playlistGrid.themeColors.fontFamily
            font.pixelSize: playlistGrid.themeColors.type.bodySmall
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
            id: cell
            required property var modelData

            width: grid.cellWidth
            height: grid.cellHeight

            Item {
                id: card
                anchors.fill: parent
                anchors.rightMargin: 10
                anchors.bottomMargin: 10
                scale: hover.hovered ? 1.025 : 1
                transformOrigin: Item.Center

                Behavior on scale {
                    NumberAnimation {
                        duration: playlistGrid.themeColors.motion.expressiveFastSpatialDuration
                        easing.type: Easing.BezierSpline
                        easing.bezierCurve: playlistGrid.themeColors.motion.expressiveFastSpatialCurve
                    }
                }

                Rectangle {
                    id: shadowSource
                    anchors.fill: parent
                    radius: playlistGrid.themeColors.shape.large
                    color: playlistGrid.themeColors.surfaceContainerLow
                    visible: false
                }

                MultiEffect {
                    anchors.fill: shadowSource
                    source: shadowSource
                    autoPaddingEnabled: true
                    shadowEnabled: true
                    shadowColor: playlistGrid.themeColors.shadow
                    shadowBlur: 0.35
                    shadowOpacity: hover.hovered ? 0.85 : 0.5
                    shadowHorizontalOffset: 0
                    shadowVerticalOffset: hover.hovered ? 4 : 2
                    shadowScale: 1.02
                    z: 0

                    Behavior on shadowOpacity {
                        NumberAnimation {
                            duration: playlistGrid.themeColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playlistGrid.themeColors.motion.expressiveFastEffectsCurve
                        }
                    }
                    Behavior on shadowVerticalOffset {
                        NumberAnimation {
                            duration: playlistGrid.themeColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playlistGrid.themeColors.motion.expressiveFastEffectsCurve
                        }
                    }
                }

                Rectangle {
                    id: playlistCard
                    anchors.fill: parent
                    radius: playlistGrid.themeColors.shape.large
                    color: playlistGrid.themeColors.surfaceContainerLow
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
                        opacity: playlistArtwork.status === Image.Ready ? 1 : 0
                        z: 0

                        Behavior on opacity {
                            NumberAnimation {
                                duration: playlistGrid.themeColors.motion.expressiveDefaultEffectsDuration
                                easing.type: Easing.BezierSpline
                                easing.bezierCurve: playlistGrid.themeColors.motion.expressiveDefaultEffectsCurve
                            }
                        }
                    }

                    // Tonal placeholder when artwork is missing.
                    Rectangle {
                        anchors.fill: parent
                        radius: playlistCard.radius
                        visible: playlistArtwork.status !== Image.Ready
                        color: playlistGrid.themeColors.surfaceContainerHigh
                    }
                    Text {
                        anchors.centerIn: parent
                        visible: playlistArtwork.status !== Image.Ready
                        text: "album"
                        color: playlistGrid.themeColors.primary
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 40
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: playlistCard.radius
                        gradient: Gradient {
                            GradientStop { position: 0.35; color: "transparent" }
                            GradientStop { position: 1.0; color: "#d9000000" }
                        }
                    }

                    Label {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 14
                        text: modelData.title || "Playlist"
                        color: "#ffffff"
                        font.family: playlistGrid.themeColors.fontFamily
                        font.pixelSize: playlistGrid.themeColors.type.titleSmall
                        font.weight: playlistGrid.themeColors.type.weightDemiBold
                        elide: Text.ElideRight
                        maximumLineCount: 2
                        wrapMode: Text.Wrap
                    }
                }

                Rectangle {
                    id: openAffordance
                    width: 40
                    height: 40
                    radius: 20
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 12
                    color: playlistGrid.themeColors.primaryContainer
                    opacity: hover.hovered ? 1 : 0
                    scale: hover.hovered ? 1 : 0.8
                    z: 2

                    Behavior on opacity {
                        NumberAnimation {
                            duration: playlistGrid.themeColors.motion.expressiveFastEffectsDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playlistGrid.themeColors.motion.expressiveFastEffectsCurve
                        }
                    }
                    Behavior on scale {
                        NumberAnimation {
                            duration: playlistGrid.themeColors.motion.expressiveFastSpatialDuration
                            easing.type: Easing.BezierSpline
                            easing.bezierCurve: playlistGrid.themeColors.motion.expressiveFastSpatialCurve
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "arrow_forward"
                        color: playlistGrid.themeColors.onPrimaryContainer
                        font.family: "Material Symbols Rounded"
                        font.pixelSize: 22
                    }
                }

                StateLayer {
                    motion: playlistGrid.themeColors.motion
                    anchors.fill: playlistCard
                    radius: playlistCard.radius
                    stateColor: playlistGrid.themeColors.onSurface
                    hovered: hover.hovered
                    pressed: tap.pressed
                    z: 3
                }

                HoverHandler {
                    id: hover
                }

                TapHandler {
                    id: tap
                    onTapped: playlistGrid.service.openCollection(modelData)
                }

                Accessible.role: Accessible.Button
                Accessible.name: modelData.title || "Playlist"
            }
        }
    }
}
