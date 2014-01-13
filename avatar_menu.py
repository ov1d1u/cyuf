from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import avatar_prechooser
import cyemussa
ym = cyemussa.CyEmussa.Instance()


class AvatarMenu(QObject):
    def __init__(self, app):
        QObject.__init__(app)
        super(AvatarMenu, self).__init__()
        self.app = app

        self.widget = uic.loadUi('ui/avatar_menu.ui')
        self.widget.setWindowFlags(self.widget.windowFlags() | Qt.Popup)
        self.widget.setWindowTitle(self.app.me.yahoo_id)
        self.widget.avatarHolder.setPixmap(QPixmap(self.app.me.avatar.image))

        self.widget.label_displayImage.linkActivated.connect(self._openLink)
        self.widget.label_contactDetails.linkActivated.connect(self._openLink)
        self.widget.label_accountInfo.linkActivated.connect(self._openLink)
        self.widget.label_manageUpdates.linkActivated.connect(self._openLink)
        self.widget.label_myProfile.linkActivated.connect(self._openLink)

        self.widget.setFocus(Qt.MouseFocusReason)
        self.widget.focusOutEvent = self._focusOutEvent

    def _focusOutEvent(self, event):
        if not self.widget.findChild(QLabel,
                                     self.widget.focusWidget().objectName()):
            self.widget.hide()
            self.setParent(None)

    def _openLink(self, link_url):
        url = QUrl(link_url)
        if url.scheme() == 'cyuf':
            if url.host() == 'choose-avatar':
                self.avatarPrechooser = avatar_prechooser.AvatarPrechooser(
                    self.app
                )
                self.avatarPrechooser.widget.show()

            self.widget.hide()
            self.setParent(None)
        else:
            QDesktopServices.openUrl(url)
