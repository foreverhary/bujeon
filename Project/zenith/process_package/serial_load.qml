import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Window {
    id : window
    width: 600
    height: 600
    visible: true
    color: "#00000000"
    title: qsTr("Hellow World")
    // REMOVE TITLE BAR
    flags: Qt.Window | Qt.FrameLessWindowHint

    Rectangle{
        width: 420
        height: 420
        opacity: 0.85
        color: "#191919"
        radius: 300
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        DragHandler {
            onActiveChanged: if (active) {
                                window.startSystemMove()
                                internal.ifMaximizedWindowRestore()
                            }
            target: null
        }
    }
}