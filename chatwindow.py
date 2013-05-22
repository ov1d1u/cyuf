from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

from chatwidget import ChatWidget

class ChatWindow(QObject):
    def __init__(self, app, cybuddy):
        self.widget = uic.loadUi('ui/chatwindow.ui')
        self.app = app
        self.chatwidgets = []

        self.widget.setWindowTitle('{0} - Cyuf'.format(cybuddy.yahoo_id))
        self.widget.setAttribute(Qt.WA_DeleteOnClose, True)
        self.widget.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.new_chat(cybuddy)

    def new_chat(self, cybuddy):
        for chat in self.chatwidgets:
            if chat.cybuddy.yahoo_id == cybuddy.yahoo_id:
                self.widget.tabWidget.setCurrentIndex(self.chatwidgets.index(chat))
                return

        chat = ChatWidget(self, cybuddy)
        self.chatwidgets.append(chat)
        self.widget.tabWidget.addTab(chat.widget, cybuddy.yahoo_id)
        self.widget.show()
        self.widget.tabWidget.setCurrentIndex(self.chatwidgets.index(chat))

    def close_tab(self, index):
        chat = None
        for _chat in self.chatwidgets:
            if self.widget.tabWidget.widget(index) == _chat.widget:
                chat = _chat
        self.chatwidgets.remove(chat)
        self.widget.tabWidget.removeTab(index)

        if not len(self.chatwidgets):
            self.widget.close()

    def focus_chat(self, cybuddy):
        for chat in self.chatwidgets:
            if chat.cybuddy.yahoo_id == cybuddy.yahoo_id:
                self.widget.tabWidget.setCurrentIndex(self.chatwidgets.index(chat))
