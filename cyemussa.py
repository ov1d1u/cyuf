#
# Qt wrapper around libEmussa classes
#
import traceback
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

from singleton import Singleton
from libemussa import EmussaSession
from libemussa import im


@Singleton
class CyEmussa(QThread, EmussaSession):
    signal = pyqtSignal(int, tuple)

    def __init__(self):
        QThread.__init__(self)
        self.emussaSession = EmussaSession.__init__(self)
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
                except:
                    print('CyEmussa: Error calling callback: {0}'.format(func))
                    print(traceback.format_exc())

    def _callback(self, callback_id, *args):
        if len(args):
            self.signal.emit(callback_id, args)
        else:
            self.signal.emit(callback_id, ())


class CyStatus(im.Status, QObject):
    update = pyqtSignal()

    def __init__(self, status=None, parentbuddy=None):
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

    def __init__(self, cybuddy=None):
        QObject.__init__(self)
        super(CyAvatar, self).__init__()
        self.buddy = cybuddy
        self.t_cookie = CyEmussa.Instance().t_cookie
        self.y_cookie = CyEmussa.Instance().y_cookie
        self.image = QPixmap("ui/resources/no-avatar.png")
        self.sizes = {}

        if self.buddy:
            self.get_from_yahoo()

    def scaled(self, px, pixmap=None):
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
        self.req = QNetworkRequest(QUrl("http://rest-img.msg.yahoo.com/v1/displayImage/yahoo/{0}".format(self.buddy.yahoo_id)))
        self.req.setRawHeader('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)')
        self.req.setRawHeader('Cookie', 'Y={0}; T={1}'.format(self.y_cookie, self.t_cookie))
        self.reply = self.manager.get(self.req)

    def set_from_yahoo(self, reply):
        imgdata = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(imgdata)
        if not pixmap.isNull():
            self.sizes = {}
            self.image = pixmap
            self.update.emit()
        else:
            self.update.emit()


class CyContact(im.Contact, QObject):
    update = pyqtSignal()

    def __init__(self, contact=None):
        QObject.__init__(self)
        super(CyContact, self).__init__()
        if contact:
            self.__dict__.update(contact.__dict__)

    def __setattr__(self, name, value):
        super(CyContact, self).__setattr__(name, value)
        self.update.emit()


class CyBuddy(im.Buddy, QObject):
    update = pyqtSignal()
    update_status = pyqtSignal()
    update_avatar = pyqtSignal()
    update_all = pyqtSignal()

    def __init__(self, buddy=None):
        QObject.__init__(self)
        super(CyBuddy, self).__init__()
        if buddy:
            self.__dict__.update(buddy.__dict__)

        if buddy:
            self.status = CyStatus(buddy.status, self)
            self.display_name = buddy.yahoo_id
        else:
            self.status = CyStatus(None, self)
            self.display_name = ''

        self.avatar = CyAvatar(self)
        self.contact = CyContact(self)
        self.group = ''

        self.status.update.connect(self._emit_update(self.status))
        self.avatar.update.connect(self._emit_update(self.avatar))

    def __setattr__(self, name, value):
        if name == 'status' and value.__class__ == im.Status:
            value = CyStatus(value)
        if name == 'contact':
            if value.nickname:
                self.display_name = '{0}'.format(value.nickname)
            elif value.fname:
                self.display_name = '{0} {1}'.format(value.fname, value.lname)
        super(CyBuddy, self).__setattr__(name, value)

        if name == 'status':
            self._emit_update(self.status)()
        elif name == 'avatar':
            self._emit_update(self.avatar)()
        else:
            self._emit_update(self)()

    def _emit_update(self, obj):
        sender = obj

        def update_connector():
            if sender.__class__ == CyStatus:
                self.update_status.emit()
            elif sender.__class__ == CyAvatar:
                self.update_avatar.emit()
            elif sender == self:
                self.update.emit()
            self.update_all.emit()

        return update_connector


class CyPersonalMessage(im.PersonalMessage, QObject):
    def __init__(self, personal_msg=None):
        QObject.__init__(self)
        super(CyPersonalMessage, self).__init__()
        if personal_msg:
            self.__dict__.update(personal_msg.__dict__)

    def __setattr__(self, name, value):
        super(CyPersonalMessage, self).__setattr__(name, value)
