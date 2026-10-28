import QtQuick

Text {
    id: iconRoot
    property string icon: ""
    property int size: 24
    property color iconColor: "#E2E2E9"

    font.family: "Material Symbols Rounded"
    font.pixelSize: size
    text: icon
    color: iconColor
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
}
