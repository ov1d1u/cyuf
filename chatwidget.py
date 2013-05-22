from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

from libemussa.const import *
import cyemussa

ym = cyemussa.CyEmussa.Instance()

class ChatWidget(QWidget):
    def __init__(self, parent, cybuddy):
        super(ChatWidget, self).__init__()
        self.widget = uic.loadUi('ui/chatwidget.ui')
        self.parent_window = parent
        self.me = parent.app.me
        self.cybuddy = cybuddy
        self.typing = False

        self.widget.textEdit.keyPressEvent = self._writing_message
        self.widget.sendButton.clicked.connect(self._send_message)
        self.widget.myAvatar.setPixmap(self.me.avatar.image)
        self.widget.hisAvatar.setPixmap(self.cybuddy.avatar.image)

        self.widget.messagesView.setHtml('<i>Conversation started</i><br/>', QUrl())
        self.cybuddy.update.connect(self._update_buddy)
        self._update_buddy()

    def _writing_message(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.widget.sendButton.click()
        else:
            QTextEdit.keyPressEvent(self.widget.textEdit, e)
            if not self.typing:
                self.typing = True

    def _send_message(self):
        message = self.widget.textEdit.toPlainText()
        self.widget.textEdit.setDocument(QTextDocument())
        ym.send_message(self.cybuddy.yahoo_id, str(message))
        self._new_message(self.me.yahoo_id, message)
        self.typing = False

    def _new_message(self, sender, message):
        htmltext = '<b>{0}</b>: {1}'.format(sender, message)
        self.widget.messagesView.page().mainFrame().evaluateJavaScript('document.body.innerHTML += "{0}<br/>"'.format(htmltext))

    def _update_buddy(self):
        self.widget.contactName.setText(self.cybuddy.yahoo_id)

        if self.cybuddy.status.online:
            if self.cybuddy.status.idle_time:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-away.png"))
            elif self.cybuddy.status.code == YAHOO_STATUS_BUSY:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-busy.png"))
            else:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-online.png"))
        else:
            self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-offline.png"))

    def income_message(self, cymessage):
        self._new_message(cymessage.sender, cymessage.message)