from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *


class AuthResponseDialog(QObject):
    def __init__(self, parent, auth):
        QObject.__init__(parent)
        super(AuthResponseDialog, self).__init__()
        self.dialog = uic.loadUi('ui/add_request_denied.ui')

        self.dialog.mainLabel.setText(
            '{0} has denied your request to add them to your Messenger List, and sent this message:'
            .format(auth.sender)
        )
        self.dialog.secondaryLabel.setText(
            '{0} will no longer appear in your Messenger List, but you may want to keep the contact information in your Address Book.'
            .format(auth.sender)
        )

        self.dialog.show()
