import QtQuick
import QtQuick.Controls

ScrollBar {
    id: sb
    property var themeColors: null
    property Flickable target
    orientation: Qt.Vertical
    policy: ScrollBar.AsNeeded
    anchors {
        right: parent ? parent.right : undefined
        top: parent ? parent.top : undefined
        bottom: parent ? parent.bottom : undefined
    }

    contentItem: Rectangle {
        implicitWidth: sb.active ? 10 : 6
        radius: implicitWidth / 2
        color: sb.themeColors ? sb.themeColors.onSurfaceVariant : "#C4C6D0"
        opacity: sb.active ? 0.65 : 0.0

        Behavior on opacity {
            NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
        }
        Behavior on implicitWidth {
            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
        }
    }

    background: Item {}
}
