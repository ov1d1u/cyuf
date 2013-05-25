#
# Qt wrapper around libEmussa classes
#
import traceback
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

from singleton import Singleton
from libemussa import EmussaException, EmussaSession
from libemussa import callbacks, im

@Singleton
class CyEmussa(QThread, EmussaSession):
    signal = pyqtSignal(int, tuple)

    def __init__(self):
        QThread.__init__(self)
        EmussaSession.__init__(self)
        self.signal.connect(self.handle_signal)

    def disconnect(self, *args):
        if len(args):
            super(disconnect)
        else:
            self._disconnect()

    def handle_signal(self, callback_id, args):
        if callback_id in self.cbs:
            for func in self.cbs[callback_id]:
                try:
                    if len(args):
                        func(self, *args)
                    else:
                        func(self)
                except Exception as e:
                    print('CyEmussa: Error calling callback: {0}'.format(func))
                    print(traceback.format_exc())

    def _callback(self, callback_id, *args):
        if len(args):
            self.signal.emit(callback_id, args)
        else:
            self.signal.emit(callback_id, ())


class CyStatus(im.Status, QObject):
    update = pyqtSignal()

    def __init__(self, status = None, parentbuddy = None):
        QObject.__init__(self)
        super(CyStatus, self).__init__()
        if status:
            self.__dict__.update(status.__dict__)
        
        self._buddy = parentbuddy

    def __setattr__(self, name, value):
        super(CyStatus, self).__setattr__(name, value)
        self.update.emit()

class CyAvatar(QObject):
    update = pyqtSignal()

    def __init__(self, cybuddy = None):
        QObject.__init__(self)
        super(CyAvatar, self).__init__()
        self.buddy = cybuddy
        self.image = QPixmap("ui/resources/no-avatar.png")
        self.sizes = {}

        if self.buddy:
            self.get_from_yahoo()

    def scaled(self, px, pixmap = None):
        image = self.image
        if pixmap:
            image = pixmap
        if px in self.sizes:
            return self.sizes[px]
        scaled = image.scaled(QSize(px, px), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.sizes[px] = scaled
        return scaled

    def set_from_pixmap(self, pixmap):
        self.image = self.scaled(96, pixmap)
        self.update.emit()

    def get_from_yahoo(self):
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.set_from_yahoo)
        self.req = QNetworkRequest(QUrl("http://img.msg.yahoo.com/avatar.php?yids={0}".format(self.buddy.yahoo_id)))
        self.req.setRawHeader('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)')
        self.reply = self.manager.get(self.req)

    def set_from_yahoo(self, reply):
        imgdata = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(imgdata)
        if not pixmap.isNull():
            self.sizes = {}
            self.image = pixmap
            self.update.emit()


class CyBuddy(im.Buddy, QObject):
    update = pyqtSignal()

    def __init__(self, buddy = None):
        QObject.__init__(self)
        super(CyBuddy, self).__init__()
        if buddy:
            self.__dict__.update(buddy.__dict__)

        if buddy:
            self.status = CyStatus(buddy.status, self)
        else:
            self.status = CyStatus(None, self)
            
        self.avatar = CyAvatar(self)

        self.status.update.connect(self._emit_update)
        self.avatar.update.connect(self._emit_update)

    def __setattr__(self, name, value):
        if name == 'status' and value.__class__ == im.Status:
            value = CyStatus(value)
        super(CyBuddy, self).__setattr__(name, value)
        self._emit_update()

    def _emit_update(self):
        self.update.emit()

class CyPersonalMessage(im.PersonalMessage, QObject):
    def __init__(self, personal_msg = None):
        QObject.__init__(self)
        super(CyPersonalMessage, self).__init__()
        if personal_msg:
            self.__dict__.update(personal_msg.__dict__)
        
    def __setattr__(self, name, value):
        super(CyPersonalMessage, self).__setattr__(name, value)
    
