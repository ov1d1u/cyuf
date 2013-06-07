from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import cyemussa
ym = cyemussa.CyEmussa.Instance()


class MoveBuddyDialog(QObject):
    finished = pyqtSignal(str, str)

    def __init__(self, app, cybuddy):
        QObject.__init__(app)
        super(MoveBuddyDialog, self).__init__()
        self.cybuddy = cybuddy
        self.app = app
        self.dialog = uic.loadUi('ui/move_buddy.ui')

        self.dialog.accepted.connect(self._finished)
        self.dialog.newGroupButton.clicked.connect(self._new_group)
        for groupname in self.app.buddylist.group_items:
            self.dialog.groupsList.addItem(groupname)

        self.dialog.show()

    def _new_group(self):
        pass

    def _finished(self):
        group = self.dialog.groupsList.currentItem().text()
        self.finished.emit(self.cybuddy.yahoo_id, group)
