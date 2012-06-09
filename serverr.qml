
/*

# Copyright (c) 2012 Thomas Perl <m@thp.io>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

*/

import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
    initialPage: Page {
        orientationLock: PageOrientation.LockPortrait

        Rectangle {
            id: headerRect
            height: 100
            anchors {
                left: parent.left
                top: parent.top
                right: parent.right
            }
            color: '#8bb92d'

            Text {
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    margins: 20
                }
                font.pixelSize: 30
                font.bold: true
                color: 'white'
                text: 'Personal Web Server<br><span style="font-size: 20px;">' + serverr.currentStatus + '</span>'
            }

            Switch {
                id: onOffSwitch
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    margins: 20
                }

                onCheckedChanged: {
                    if (checked) {
                        serverr.start();
                    } else {
                        serverr.stop();
                    }
                }
            }
        }

        Text {
            id: loginDataText
            anchors {
                margins: 10
                top: headerRect.bottom
                left: parent.left
                right: parent.right
            }

            font.pixelSize: 40
            color: 'white'
            text: 'Username: <b>client</b><br>Password: <b>' + serverr.currentPassword + '</b>'
            /*'<p style="text-align: center;">
            <b>Current password: serverr.currentPassword</b><br><br>
            While this application is running, you can<br>
            use the <b>Volume +</b> button on your N9<br>
            to capture photos in the camera application.<br>
            <br><br>
            http://thp.io/2012/serverr/
            </p>'*/
        }

        Button {
            id: btnPwGen
            anchors {
                top: loginDataText.bottom
                margins: 10
                horizontalCenter: parent.horizontalCenter
            }

            text: 'Generate new password'
            onClicked: serverr.generateNewPassword()
        }

        ListView {
            id: listView
            clip: true

            anchors {
                left: parent.left
                top: btnPwGen.bottom
                right: parent.right
                bottom: ipInfo.top
                margins: 10
            }

            model: ListModel {
                id: myModel
                ListElement { modelData: 'Personal Web Server for MeeGo' }
                ListElement { modelData: 'http://thp.io/2012/serverr/' }
                ListElement { modelData: '' }
                ListElement { modelData: 'Only use on trusted networks.' }
            }
            delegate: Text {
                text: modelData
                color: 'white'
                font.pixelSize: 20
                elide: Text.ElideRight
                anchors {
                    left: parent.left
                    right: parent.right
                    margins: 10
                }
            }
        }

        Connections {
            target: serverr
            onLogMessage: {
                myModel.append({'modelData': serverr.getLogMessage()})
                listView.positionViewAtEnd()
            }
        }

        ScrollDecorator { flickableItem: listView }

        Text {
            id: ipInfo
            visible: onOffSwitch.checked
            anchors {
                horizontalCenter: parent.horizontalCenter
                bottom: parent.bottom
                margins: 70
            }
            color: 'white'
            text: serverr.get_ips()
            font.pixelSize: 30
        }

        Connections {
            target: serverr
            onCurrentStatusChanged: ipInfo.text = serverr.get_ips()
        }

        /*CheckBox {
            x: 50
            y: 50
            text: 'Launch Camera app on start'
            //checked: settings.get('startupLaunch')
            onClicked: settings.set('startupLaunch', checked)
        }*/

        /*CheckBox {
            x: 50
            y: 110
            text: 'Focus mode (takes longer)'
            checked: settings.get('withFocus')
            onClicked: settings.set('withFocus', checked)
        }*/

        Button {
            anchors {
                right: parent.right
                bottom: parent.bottom
                margins: 10
            }
            width: parent.width * .5
            text: 'Get more apps'
            onClicked: Qt.openUrlExternally('http://store.ovi.com/publisher/Thomas+Perl/')
        }
    }

    Component.onCompleted: {
        theme.inverted = true
    }
}
