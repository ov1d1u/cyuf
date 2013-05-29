from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

from libemussa.const import *
from libemussa import callbacks as cb
from emotes import emotes
import cyemussa, util, datetime, re

ym = cyemussa.CyEmussa.Instance()

class ChatWidget(QWidget):
    def __init__(self, parent, cybuddy):
        super(ChatWidget, self).__init__()
        self.widget = uic.loadUi('ui/chatwidget.ui')
        self.parent_window = parent
        self.me = parent.app.me
        self.cybuddy = cybuddy
        self.typingTimer = None
        self.is_ready = False
        self.queue = []
        
        ym.register_callback(cb.EMUSSA_CALLBACK_TYPING_NOTIFY, self._typing)
        self.widget.textEdit.keyPressEvent = self._writing_message
        self.widget.sendButton.clicked.connect(self._send_message)
        self.widget.myAvatar.setPixmap(self.me.avatar.image)
        self.widget.hisAvatar.setPixmap(self.cybuddy.avatar.image)

        self.widget.messagesView.setUrl(QUrl('ui/resources/html/chat/index.html'))
        self.widget.messagesView.loadFinished.connect(self._document_ready)
        self.cybuddy.update.connect(self._update_buddy)
        self._update_buddy()

    def _javascript(self, function, *args):
        # if the document is not ready, wait a while until we start calling JS functions on it
        if not self.is_ready:
            self.queue.append([function, args])
        arguments_list = []
        for arg in args:
            jsarg = str(arg).replace("'", "\\'")
            arguments_list.append("'" + jsarg + "'")
        jscode = function + "(" + ", ".join(arguments_list) + ")"
        self.widget.messagesView.page().mainFrame().evaluateJavaScript(jscode)

    def _document_ready(self):
        self.is_ready = True
        if self.me.status.code == YAHOO_STATUS_INVISIBLE:
            pixmap = QPixmap(":status/resources/user-invisible.png")
            self._add_info('You appear offline to ' + 
                '<b>' + self.cybuddy.display_name + '</b>',
                pixmap
            )
        elif not self.cybuddy.status.online:
            pixmap = QPixmap(":status/resources/user-offline.png")
            self._add_info('<b>' + self.cybuddy.display_name + '</b>' + 
                ' seems to be offline and will receive your messages next time when he/she logs in.',
                pixmap
            )

        for task in self.queue:
            self._javascript(task[0], *task[1])
        self.queue = []
        self._javascript('show_timestamps', 'true')

    def _update_buddy(self):
        self.widget.contactName.setText(self.cybuddy.display_name)

        if self.cybuddy.status.online:
            if self.cybuddy.status.idle_time:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-away.png"))
            elif self.cybuddy.status.code == YAHOO_STATUS_BUSY:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-busy.png"))
            else:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-online.png"))
        else:
            self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-offline.png"))

    def _writing_message(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.widget.sendButton.click()
            ym.send_typing(self.cybuddy.yahoo_id, False)
            self.killTimer(self.typingTimer)
            self.typingTimer = None
        else:
            QTextEdit.keyPressEvent(self.widget.textEdit, e)
            if e.key() > Qt.Key_0 and e.key() < Qt.Key_Z:
                if self.typingTimer:
                    self.killTimer(self.typingTimer)
                else:
                    ym.send_typing(self.cybuddy.yahoo_id, True)
                self.typingTimer = self.startTimer(5000)

    def _typing(self, cyemussa, tn):
        sender = tn.sender
        if not sender:
            # we are typing this from somewhere else
            sender = self.me.yahoo_id
        if not sender == self.me.yahoo_id and not sender == self.cybuddy.yahoo_id:
            return
        if tn.status:
            self._javascript('start_typing', sender)
        else:
            self._javascript('stop_typing')

    def _add_info(self, text, pixmap = None):
        image = None
        if pixmap:
            image = util.pixmap_to_base64(pixmap)

        text = util.sanitize_html(text)
        if image:
            self._javascript('add_info', text, image)
        else:
            self._javascript('add_info', text)

    def _send_message(self):
        raw_msg = self.widget.textEdit.toPlainText()
        message = util.sanitize_html(raw_msg)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.widget.textEdit.setDocument(QTextDocument())
        ym.send_message(self.cybuddy.yahoo_id, str(raw_msg))
        self._javascript('message_out', self.me.yahoo_id, self._text_to_emotes(raw_msg), timestamp)

    def _text_to_emotes(self, text):
        words = text.split()
        for i, w in enumerate(words):
            for emo in emotes:
                pattern = re.compile(re.escape(emo), re.IGNORECASE)
                word = pattern.sub('<img src="{0}" alt="{1}" />'.format(emotes[emo], emo), w)
                if not word == w:           # a replacement was made, skip to the next word
                    words[i] = word
                    break
        text = ' '.join(words)
        return text

    def timerEvent(self, event):
        ym.send_typing(self.cybuddy.yahoo_id, False)
        if self.typingTimer:
            self.killTimer(self.typingTimer)
            self.typingTimer = None

    def close(self):
        # called by parent when the chat is closing
        ym.unregister_callback(cb.EMUSSA_CALLBACK_TYPING_NOTIFY, self._typing)
        self.cybuddy.update.disconnect(self._update_buddy)
        if self.typingTimer:
            ym.send_typing(self.cybuddy.yahoo_id, False)

    def receive_message(self, cymessage):
        message = util.yahoo_rich_to_html(cymessage.message)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not cymessage.sender:
            sender = self.me.yahoo_id
        else:
            sender = self.cybuddy.display_name
        if cymessage.offline:
            message = '(offline) {0}'.format(message)
        if cymessage.timestamp:
            timestamp = datetime.datetime.fromtimestamp(int(cymessage.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        self._javascript('message_in', sender, self._text_to_emotes(util.sanitize_html(message)), timestamp)
