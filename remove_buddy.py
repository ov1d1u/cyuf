from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

from cyemussa import CyBuddy


class RemoveBuddyDialog(QObject):
    finished = pyqtSignal(CyBuddy, bool, bool)

    def __init__(self, parent, cybuddy):
        QObject.__init__(parent)
        super(RemoveBuddyDialog, self).__init__()
        self.cybuddy = cybuddy
        self.dialog = uic.loadUi('ui/delete_buddy.ui')
        self.dialog.yahooID.setText(cybuddy.yahoo_id)

        self.dialog.accepted.connect(self._finished)

        self.dialog.show()

    def _finished(self):
        self.finished.emit(self.cybuddy,
                           self.dialog.deleteAddressbook.isChecked(),
                           self.dialog.reverseDelete.isChecked())
