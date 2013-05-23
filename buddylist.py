import sys
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

import cyemussa
from libemussa import callbacks as cb
from libemussa.const import *
import buddylist_rc, cyemussa, insider, chatwindow

ym = cyemussa.CyEmussa.Instance()

class BuddyItem(QTreeWidgetItem):
    def __init__(self, cybuddy, compact = True):
        super(BuddyItem, self).__init__()
        self.compact = compact
        self._cybuddy = cybuddy
        self._cybuddy.update.connect(self._update)
        self._initWidget()
        self._update()

    def _initWidget(self):
        # create item's widget
        self._widget = QWidget()

        # avatar icon
        self.avatar_holder = QLabel()
        self.avatar_holder.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        # status icon
        self.icon_holder = QLabel()
        self.icon_holder.setPixmap(QPixmap(":status/resources/user-offline.png"))
        self.icon_holder.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        # cybuddy label
        self.buddyname = QLabel(self._cybuddy.yahoo_id)

        # cybuddy status text
        self.status_label = QLabel()
        self.status_label.setText(self._get_link_from_status())
        self.status_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.status_label.setOpenExternalLinks(True)

    def _setupLayout(self):
        self.layout = QHBoxLayout()

        if not self.compact:
            self.right_widget = QWidget()
            self.vertical_layout = QVBoxLayout(self.right_widget)
            self.horizontal_layout = QHBoxLayout()

        self.layout.addWidget(self.avatar_holder)
        self._setAvatar()

        if self.compact:
            self.layout.addWidget(self.icon_holder)
        else:
            self.horizontal_layout.addWidget(self.icon_holder)

        if self.compact:
            self.buddyname.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            self.layout.addWidget(self.buddyname)
        else:
            self.buddyname.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.horizontal_layout.addWidget(self.buddyname)
            self.vertical_layout.addLayout(self.horizontal_layout)

        if self.compact:
            self.layout.addWidget(self.status_label)
        else:
            self.vertical_layout.addWidget(self.status_label)
            self.layout.addWidget(self.right_widget)

        # add layout to widget, and set the widget to item
        self._widget = QWidget()
        self._widget.setLayout(self.layout)

    def _get_link_from_status(self):
        sep = ''
        if self.compact:
            sep = ' - '
        statusmsg = self._cybuddy.status.message
        if 'http://' in statusmsg:
            href = statusmsg[statusmsg.index('http://'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            return '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
        elif 'https://' in statusmsg:
            href = statusmsg[statusmsg.index('https://'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            return '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
        elif 'www.' in statusmsg:
            href = statusmsg[statusmsg.index('www.'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            return '<font color="#8C8C8C">{0}<a href="http://{1}">{2}</a></font>'.format(sep, href, statusmsg)
        else:
            return '<font color="#8C8C8C">{0}{1}</font>'.format(sep, self._cybuddy.status.message)

    def _update(self):
        #print 'cybuddy updated:', self._cybuddy.status.online
        self._setAvatar()
        self.buddyname.setText(self._cybuddy.yahoo_id)

        self.status_label.setText('')
        if self._cybuddy.status.message:
            self.status_label.setText(self._get_link_from_status())

        if self._cybuddy.status.online:
            if self._cybuddy.status.idle_time:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-away.png"))
            elif self._cybuddy.status.code == YAHOO_STATUS_BUSY:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-busy.png"))
            else:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-online.png"))
        else:
            self.icon_holder.setPixmap(QPixmap(":status/resources/user-offline.png"))

    def _setAvatar(self):
        size = 16
        if not self.compact:
            size = 32
        self.avatar_holder.setPixmap(self._cybuddy.avatar.scaled(size))

    @property
    def widget(self):
        self._setupLayout()
        return self._widget

    @widget.setter
    def widget(self, widget):
         raise AttributeError('Why are you setting the widget from outside?')

    @property
    def cybuddy(self):
        return self._cybuddy

    @cybuddy.setter
    def cybuddy(self, cybuddy):
        self._cybuddy = cybuddy
        self._update()


class BuddyList(QWidget):
    def __init__(self, app):
        super(BuddyList, self).__init__()
        self.widget = uic.loadUi('ui/buddylist.ui')
        self.app = app
        self.group_items = {}
        self.buddy_items = {}
        self.chat_windows = []
        self.last_group_received = None

        ym.register_callback(cb.EMUSSA_CALLBACK_GROUP_RECEIVED, self.new_group_recv)
        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDY_RECEIVED, self.new_buddy_recv)
        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDY_UPDATE, self.update_buddy)
        ym.register_callback(cb.EMUSSA_CALLBACK_MESSAGE_IN, self.received_message)
        self.app.me.update.connect(self._update_myself)

        self.widget.insiderButton.clicked.connect(self.show_insider)
        self.widget.customStatusCombo.lineEdit().setPlaceholderText("Have something to share?")
        
        # old-style connect to force the calling of activated(QString), not activated(int)
        self.widget.connect(self.widget.customStatusCombo, SIGNAL("activated(const QString&)"), self._set_status_text)
        self.widget.buddyTree.itemDoubleClicked.connect(self.btree_open_chat)

        self._setup_tab_menus()
        self._set_statuses()
        self._set_avatar()
        self._build_toolbar()

    def _setup_tab_menus(self):
        menu = QMenu()
        menuitems = []

        """ BuddyList style actions """
        listStyleGroup = QActionGroup(self)

        action = QAction('Compact list', menu, checkable = True)
        action.triggered.connect(self._change_list_style(True))
        listStyleGroup.addAction(action)

        action = QAction('Detailed list', menu, checkable = True)
        action.triggered.connect(self._change_list_style(False))
        listStyleGroup.addAction(action)
        
        menuitems.extend(listStyleGroup.actions())
        """ ---- """

        self.widget.tab1Btn = QPushButton()
        self.widget.tab1Btn.setFlat(True)
        self.widget.tab1Btn.setMaximumSize(QSize(34, 20))
        
        for action in menuitems:
            menu.addAction(action)

        self.widget.tab1Btn.setMenu(menu)
        self.widget.tab1Btn.clicked.connect(self._pop_tab_menu)

        self.widget.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, self.widget.tab1Btn)

    def _pop_tab_menu(self):
        self.widget.tab1Btn.showMenu()

    def _change_list_style(self, compact):
        # function closure for change_list_style
        def change_list_style():
            for item in self.buddy_items:
                self.buddy_items[item].compact = compact
                self.widget.buddyTree.setItemWidget(self.buddy_items[item], 0, self.buddy_items[item].widget)
            # hack to force properly update of buddyTree
            self.widget.buddyTree.resize(self.widget.buddyTree.size().width() - 1, self.widget.buddyTree.size().height())
            self.widget.buddyTree.resize(self.widget.buddyTree.size().width() + 1, self.widget.buddyTree.size().height())
        return change_list_style

    def _set_statuses(self):
        self.statuses = [
            ['menu-user-online.png', 'Online', YAHOO_STATUS_AVAILABLE],
            ['menu-user-busy.png', 'Busy', YAHOO_STATUS_BUSY],
            ['menu-user-invisible.png', 'Invisible', YAHOO_STATUS_INVISIBLE]
        ]

        menu = QMenu()
        for status in self.statuses:
            pixmap = QPixmap(":status/resources/" + status[0])
            action = QAction(QIcon(pixmap), status[1], self)
            action.setData(status[2])
            menu.addAction(action)
        menu.triggered.connect(self._set_availability)

        self.widget.fakeStatusCombo.setMenu(menu)
        #self.widget.fakeStatusCombo.setText('{0} {1}'.format(self.app.me.contact.name, self.app.me.contact.surname))
        self.widget.fakeStatusCombo.setText('{0}'.format(self.app.me.nickname))

    def _set_avatar(self):
        self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))

    def _build_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.addAction(QIcon(QPixmap(":actions/resources/list-add-user.png")), 'Add cybuddy')
        self.searchField = QLineEdit()
        self.toolbar.setIconSize(QSize(16, 16))
        self.widget.tbContainer.addWidget(self.toolbar)
        self.widget.tbContainer.addWidget(self.searchField)

    def _set_availability(self, action):
        if type(action) == QAction:
            avlbcode = action.data().toInt()[0]
        else:
            avlbcode = int(action)

        if not avlbcode == self.app.me.status.code:
            # toggle visibility
            if avlbcode == YAHOO_STATUS_INVISIBLE:
                ym.toggle_visibility(True)
            else:
                ym.toggle_visibility(False)
            self.app.me.status.code = avlbcode

        if avlbcode == YAHOO_STATUS_INVISIBLE:
            self.widget.customStatusCombo.lineEdit().setText('')

    def _set_status_text(self, text):
        if text and self.app.me.status.code == YAHOO_STATUS_INVISIBLE:
            self._set_availability(YAHOO_STATUS_AVAILABLE)
        ym.set_status(self.app.me.status.code, str(text))

    def _update_myself(self):
        icon = None
        for status in self.statuses:
            if status[2] == self.app.me.status.code:
                icon = QIcon(QPixmap(":status/resources/" + status[0]))
                break
        if icon:
            self.widget.fakeStatusCombo.setIcon(icon)

        ym.set_status(self.app.me.status.code, self.app.me.status.message)
        self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))

    def _get_buddy(self, yahoo_id):
        if self.buddy_items.has_key(yahoo_id):
            return self.buddy_items[yahoo_id]._cybuddy
        # create a new cybuddy
        cybuddy = cyemussa.CyBuddy()
        cybuddy.yahoo_id = yahoo_id
        cybuddy.nickname = yahoo_id
        cybuddy.status = cyemussa.CyStatus()
        return cybuddy

    def _create_chat_for_buddy(self, cybuddy, focus_chat = False):
        for win in self.chat_windows:
            for chat in win.chatwidgets:
                if chat.cybuddy.yahoo_id == cybuddy.yahoo_id:
                    if focus_chat:
                        win.focus_chat(cybuddy)
                    return chat

        # no already opened chat, open a new one
        cybuddy = self._get_buddy(cybuddy.yahoo_id)
        if not len(self.chat_windows):
            win = chatwindow.ChatWindow(self.app, cybuddy)
            win.widget.closeEvent = self._chatwindow_closed(win)
            self.chat_windows.append(win)
        else:
            win = self.chat_windows[0]
            win.new_chat(cybuddy)
        return win.chatwidgets[-1:][0]

    def _chatwindow_closed(self, window):
        def event_handler(event):
            window.close_all_tabs()
            self.chat_windows.remove(window)
        return event_handler

    def show_insider(self):
        self.i = insider.Insider(
            {'T' : ym.t_cookie,
             'Y' : ym.y_cookie})

    def new_group_recv(self, emussa, group):
        self.last_group_received = group
        item = QTreeWidgetItem()
        self.widget.buddyTree.addTopLevelItem(item)
        layout = QHBoxLayout()
        label = QLabel('<b>{0}</b>'.format(group.name))
        layout.addWidget(label)
        item_widget = QWidget()
        item_widget.setLayout(layout)
        item_widget.setMinimumSize(QSize(0, 24))
        self.widget.buddyTree.setItemWidget(item, 0, item_widget)
        self.group_items[group.name] = item

    def new_buddy_recv(self, emussa, buddy):
        item = BuddyItem(cyemussa.CyBuddy(buddy), False)
        parent_item = self.group_items[self.last_group_received.name]
        parent_item.addChild(item)
        self.widget.buddyTree.setItemWidget(item, 0, item.widget)
        self.buddy_items[buddy.yahoo_id] = item

    def update_buddy(self, emussa, cybuddy):
        for yid in self.buddy_items:
            if cybuddy.yahoo_id == yid:
                item = self.buddy_items[yid]
                item.cybuddy.status = cybuddy.status

    def received_message(self, emussa, personal_msg):
        message = cyemussa.CyPersonalMessage(personal_msg)
        if personal_msg.sender:
            cybuddy = self._get_buddy(personal_msg.sender)
        else:
            # we sent this message, from another device
            cybuddy = self._get_buddy(personal_msg.receiver)
        chat = self._create_chat_for_buddy(cybuddy)
        chat.receive_message(message)

    def btree_open_chat(self, buddy_item):
        chat = self._create_chat_for_buddy(buddy_item._cybuddy, True)