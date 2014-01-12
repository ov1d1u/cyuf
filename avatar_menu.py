from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cyemussa
ym = cyemussa.CyEmussa.Instance()


class AvatarMenu(QObject):
    def __init__(self, app):
        QObject.__init__(app)
        super(AvatarMenu, self).__init__()
        self.app = app

        self.widget = uic.loadUi('ui/avatar_menu.ui')
        self.widget.setWindowTitle(self.app.me.yahoo_id)
        self.widget.avatarHolder.setPixmap(QPixmap(self.app.me.avatar.image))

        self.widget.setFocus(Qt.MouseFocusReason)
        self.widget.focusOutEvent = self.focusOutEvent

    def focusOutEvent(self, event):
        self.widget.hide()
        self.setParent(None)
