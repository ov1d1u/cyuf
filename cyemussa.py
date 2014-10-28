#
# Qt wrapper around libEmussa classes
#
import traceback
import util
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

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


class CyAvatar(im.DisplayImage, QObject):
    update = pyqtSignal()

    def __init__(self, avatar=None):
        QObject.__init__(self)
        super(CyAvatar, self).__init__()
        if avatar:
            self.__dict__.update(avatar.__dict__)
        self.sizes = {}

    def scaled(self, px, pixmap=None):
        image = self.image
        if pixmap:
            image = pixmap
        if px in self.sizes:
            return self.sizes[px]
        scaled = image.scaled(QSize(px, px),
                              Qt.KeepAspectRatio,
                              Qt.SmoothTransformation)
        self.sizes[px] = scaled
        return scaled

    @property
    def image(self):
        if self.image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(self.image_data)
        else:
            pixmap = QPixmap("ui/resources/no-avatar.png")
        return pixmap

    @image.setter
    def image(self, pixmap):
        self.image_data = util.pixmap_to_imgformat(pixmap, 'PNG')
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

        self.avatar = CyAvatar()
        self.contact = CyContact(self)
        self.group = ''

        self.status.update.connect(self._emit_update(self.status))
        self.avatar.update.connect(self._emit_update(self.avatar))

    def __setattr__(self, name, value):
        if name == 'status' and value.__class__ == im.Status:
            value = CyStatus(value)
            value.update.connect(self._emit_update(value))
        if name == 'contact':
            if value.nickname:
                self.display_name = '{0}'.format(value.nickname)
            elif value.fname:
                self.display_name = '{0} {1}'.format(value.fname, value.lname)
        if name == 'avatar':
            if value.__class__ == im.DisplayImage:
                value = CyAvatar(value)
            value.update.connect(self._emit_update(value))

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


class CyFile(im.File, QObject):
    def __init__(self, file=None):
        QObject.__init__(self)
        super(CyFile, self).__init__()
        if file:
            self.__dict__.update(file.__dict__)

    def __setattr__(self, name, value):
        super(CyFile, self).__setattr__(name, value)


class CyFileTransfer(im.FileTransfer, QObject):
    def __init__(self, file_transfer=None):
        QObject.__init__(self)
        super(CyFileTransfer, self).__init__()
        if file_transfer:
            self.__dict__.update(file_transfer.__dict__)

    def __setattr__(self, name, value):
        super(CyFileTransfer, self).__setattr__(name, value)


class CyFileTransferInfo(im.FileTransferInfo, QObject):
    def __init__(self, file_transfer_info=None):
        QObject.__init__(self)
        super(CyFileTransferInfo, self).__init__()
        if file_transfer_info:
            self.__dict__.update(file_transfer_info.__dict__)

    def __setattr__(self, name, value):
        super(CyFileTransferInfo, self).__setattr__(name, value)


class CyWebcamNotify(im.WebcamNotify, QObject):
    def __init__(self, file_transfer_info=None):
        QObject.__init__(self)
        super(CyWebcamNotify, self).__init__()
        if file_transfer_info:
            self.__dict__.update(file_transfer_info.__dict__)

    def __setattr__(self, name, value):
        super(CyWebcamNotify, self).__setattr__(name, value)
