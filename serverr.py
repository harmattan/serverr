
#
# N9 Personal Web Server
# 2012-02-19; Thomas Perl <thp.io/about>
# All rights reserved.
#


from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import *

import SimpleHTTPServer
import SocketServer

import threading
import sys
import subprocess
import re
import time
import string
import random
import os
from StringIO import StringIO
import cgi
import urllib
import mimetypes

app = QApplication(sys.argv)
settings = QSettings('thp.io', 'serverr')

def boolsetting(key, default=False):
    global settings
    # Kludge -> at startup we get 'false' instead of False
    return (settings.value(key, default) not in ('false', False))

class SettingsProxy(QObject):
    def __init__(self, settings):
        QObject.__init__(self)
        self._settings = settings

    @Slot(str, result='QVariant')
    def get(self, key):
        return self._settings.value(key)

    @Slot(str, 'QVariant')
    def set(self, key, value):
        self._settings.setValue(key, value)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def directory_entry(self, f, fullname):
        mimetype, _ = mimetypes.guess_type(fullname)
        name = os.path.basename(fullname)
        displayname = linkname = name
        # Append / for directories or @ for symbolic links
        if os.path.isdir(fullname):
            icon = '/:theme:/icon-m-common-directory.png'
            displayname = name + "/"
            linkname = name + "/"
        elif mimetype is None:
            icon = '/:theme:/icon-m-content-file-unknown.png'
        elif mimetype.startswith('audio/'):
            icon = '/:theme:/icon-m-content-audio.png'
        elif mimetype.startswith('video/'):
            icon = '/:theme:/icon-m-content-videos.png'
        elif mimetype.startswith('image/'):
            icon = '/:theme:/icon-m-content-image.png'
        elif mimetype == 'application/pdf':
            icon = '/:theme:/icon-m-content-pdf.png'
        elif mimetype == 'application/msword':
            icon = '/:theme:/icon-m-content-word.png'
        elif mimetype == 'application/vnd.ms-excel':
            icon = '/:theme:/icon-m-content-excel.png'
        elif mimetype == 'application/vnd.ms-powerpoint':
            icon = '/:theme:/icon-m-content-powerpoint.png'
        else:
            icon = '/:theme:/icon-m-content-file-unknown.png'

        f.write('<li><a href="%s"><img style="vertical-align: middle;" src="%s" width=32> %s</a>\n'
                % (urllib.quote(linkname), icon, cgi.escape(displayname)))

    def list_directory(self, path):
        try:
            listing = os.listdir(path)
        except os.error:
            self.send_error(404, "Cannot read directory")
            return None

        listing = filter(lambda x: not x.startswith('.'), sorted(listing, key=lambda x: (0 if os.path.isdir(os.path.join(path, x)) else 1, x.lower())))
        if self.path != '/':
            listing.insert(0, '..')

        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write("<html>\n<head><title>%s on N9</title>\n" % displaypath)
        f.write("""
                <style type="text/css">
                body { font-family: sans-serif; }
                li a { padding: 7px; background-color: #eee;
                    text-decoration: none; display: block;
                    color: #333; }
                li a:hover { background-color: #ddd; color: black; }
                ul { list-style: none; margin: 0px; padding: 0px; }
                img { width: 32px; height: 32px; border: 0px; }
                hr { border-width: 0px; border-bottom: 1px solid #aaa; }
                </style>
        </head>""")
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in listing:
            fullname = os.path.join(path, name)
            self.directory_entry(f, fullname)
        f.write("""
                </ul><hr>
                <address>
                Powered by <a href="http://thp.io/2012/serverr/">Personal Web Server for N9</a>
                </address>
                </body></html>
                """)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def do_GET(self):
        authorized = False
        auth_header = self.headers.get('authorization', '')
        m = re.match(r'^Basic (.*)$', auth_header)
        if m is not None:
            auth_data = m.group(1).decode('base64').split(':', 1)
            if len(auth_data) == 2:
                username, password = auth_data
                if username == 'client' and password == serverr.password:
                    authorized = True

        if authorized:
            if not self.path.startswith('/:theme:/'):
                serverr.log_message = u'<b>%s</b> %s %s' % (
                        self.client_address[0],
                        self.command, self.path)
                serverr.logMessage.emit()

            if self.path.startswith('/:theme:/'):
                filename = os.path.basename(self.path)
                fn = '/usr/share/themes/blanco/meegotouch/icons/'+filename
                if os.path.exists(fn):
                    f = open(fn, 'rb')
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.copyfile(f, self.wfile)
                    f.close()
                    self.wfile.close()
                    return

            path = self.translate_path(self.path)
            f = None
            if os.path.isdir(path) and path.endswith('/'):
                self.list_directory(path)
            else:
                SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(401)
            self.send_header('WWW-Authenticate',
                    'Basic realm="N9 Personal Web Server"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<em>401 Access denied - wrong username/password')
            self.wfile.close()
            return


class Serverr(QObject):
    PORT = 8888

    def __init__(self):
        QObject.__init__(self)
        self.httpd = None
        self.thread = None
        self.password = self._newpassword()
        self.log_message = u''
        self.port_number = self.PORT

    @Slot(result=unicode)
    def getLogMessage(self):
        return self.log_message

    def _newpassword(self, length=5):
        # Avoid some characters that look alike in certain fonts
        charset = [x for x in string.letters + string.digits if x not in 'IlO0']
        return ''.join([random.choice(charset) for _ in range(length)])

    logMessage = Signal()

    def getCurrentStatus(self):
        if self.httpd is not None:
            return u'Serving on port %d' % self.port_number
        else:
            return u'Not running'

    currentStatusChanged = Signal()

    currentStatus = Property(unicode,
            fget=getCurrentStatus,
            notify=currentStatusChanged)

    def getCurrentPassword(self):
        return unicode(self.password)

    currentPasswordChanged = Signal()

    currentPassword = Property(unicode,
            fget=getCurrentPassword,
            notify=currentPasswordChanged)

    @Slot()
    def generateNewPassword(self):
        self.password = self._newpassword()
        self.currentPasswordChanged.emit()

    @Slot()
    def start(self):
        if self.httpd is None:
            self.thread = threading.Thread(target=self.thread_proc)
            self.thread.setDaemon(True)
            self.thread.start()

    @Slot()
    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd = None
            self.currentStatusChanged.emit()

    @Slot(result=unicode)
    def get_ips(self):
        ifconfig = subprocess.Popen('/sbin/ifconfig', stdout=subprocess.PIPE)
        stdout, stderr = ifconfig.communicate()

        ips = re.findall('addr:([^ ]+)', stdout)
        ips = filter(lambda ip: not ip.startswith('127.'), ips) or None
        if ips is None:
            return u'You are offline.'

        return u'<center>Point your browser to:<br>' + u'<br>or '.join(u'http://%s:%d/' % (ip, self.port_number)
                for ip in ips) + '</center>'

    def thread_proc(self):
        os.chdir('/home/user/MyDocs/')
        self.port_number = self.PORT
        while self.port_number < self.PORT + 100:
            try:
                self.httpd = ThreadedTCPServer(("", self.port_number),
                        MyRequestHandler)
                break
            except:
                self.port_number += 1

        self.currentStatusChanged.emit()
        self.httpd.serve_forever()
        self.thread = None

view = QDeclarativeView()
rootContext = view.rootContext()

proxy = SettingsProxy(settings)
rootContext.setContextProperty('settings', proxy)

serverr = Serverr()
rootContext.setContextProperty('serverr', serverr)

view.setSource('/opt/serverr/serverr.qml')
view.showFullScreen()

app.exec_()

