from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from util import grayscale_pixmap

from chatwidget import ChatWidget


class ChatWindow(QObject):
    def __init__(self, app, cybuddy):
        super().__init__()
        self.widget = uic.loadUi('ui/chatwindow.ui')
        self.app = app
        self.chatwidgets = []

        self.widget.setWindowTitle('{0} - Cyuf'.format(cybuddy.display_name))
        self.widget.setWindowIcon(QIcon(cybuddy.avatar.image))
        self.widget.setAttribute(Qt.WA_DeleteOnClose, True)
        self.widget.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.widget.tabWidget.currentChanged.connect(self.change_tab)
        self.widget.viewWebcamMenu.triggered.connect(self.view_webcam)
        self.widget.inviteWebcamMenu.triggered.connect(self.invite_webcam)

        self.current_buddy = cybuddy
        self.new_chat(cybuddy)

    def _setup_tab(self, chat):
        i = self.widget.tabWidget.indexOf(chat.widget)
        self.widget.tabWidget.setTabText(i, chat.cybuddy.display_name)
        if chat.cybuddy.status.online:
            self.widget.tabWidget.\
                setTabIcon(i, QIcon(chat.cybuddy.avatar.scaled(16)))
        else:
            self.widget.tabWidget.setTabIcon(
                i, QIcon(grayscale_pixmap(chat.cybuddy.avatar.scaled(16)))
            )

    def _update_tab(self):
        for chat in self.chatwidgets:
            if self.sender() == chat.cybuddy:
                self._setup_tab(chat)
                self.change_tab(self.widget.tabWidget.indexOf(chat.widget))
                return

        # cannot find buddy, seems that his tab was closed?
        self.sender().update_all.disconnect(self._update_tab)

    def new_chat(self, cybuddy):
        for chat in self.chatwidgets:
            if chat.cybuddy.yahoo_id == cybuddy.yahoo_id:
                self.widget.tabWidget.setCurrentIndex(
                    self.chatwidgets.index(chat))
                chat.widget.textEdit.setFocus(Qt.ActiveWindowFocusReason)
                self.widget.activateWindow()
                return

        chat = ChatWidget(self, cybuddy)
        self.chatwidgets.append(chat)
        self.widget.tabWidget.addTab(chat.widget, '')
        self.widget.show()
        self.widget.tabWidget.setCurrentIndex(self.chatwidgets.index(chat))
        chat.widget.textEdit.setFocus(Qt.ActiveWindowFocusReason)
        self.widget.activateWindow()
        cybuddy.update_all.connect(self._update_tab)
        self._setup_tab(chat)

    def get_current_chat(self):
        return self.chatwidgets[self.widget.tabWidget.currentIndex()]

    def change_tab(self, index):
        if index < len(self.chatwidgets):
            selected = self.chatwidgets[index]
            self.widget.setWindowTitle(
                '{0} - Cyuf'.format(selected.cybuddy.display_name)
            )
            self.widget.setWindowIcon(QIcon(selected.cybuddy.avatar.image))
            self.current_buddy = selected.cybuddy

    def close_tab(self, index):
        chat = None
        for _chat in self.chatwidgets:
            if self.widget.tabWidget.widget(index) == _chat.widget:
                chat = _chat
        chat.close()
        self.chatwidgets.remove(chat)
        self.widget.tabWidget.removeTab(index)

        if not len(self.chatwidgets):
            self.widget.close()

    def close_all_tabs(self):
        index = 0
        for chat in self.chatwidgets:
            self.close_tab(index)
            index += 1

    def focus_chat(self, cybuddy):
        for chat in self.chatwidgets:
            if chat.cybuddy.yahoo_id == cybuddy.yahoo_id:
                self.widget.tabWidget.\
                    setCurrentIndex(self.chatwidgets.index(chat))

    def view_webcam(self):
        self.get_current_chat().view_webcam()

    def invite_webcam(self):
        self.get_current_chat().invite_webcam()
