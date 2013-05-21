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
    def __init__(self, buddy, compact = True):
        super(BuddyItem, self).__init__()
        self.compact = compact
        self._buddy = buddy
        self._buddy.update.connect(self._update)
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

        # buddy label
        self.buddyname = QLabel(self._buddy.yahoo_id)

        # buddy status text
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
        statusmsg = self._buddy.status.message
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
            return '<font color="#8C8C8C">{0}{1}</font>'.format(sep, self._buddy.status.message)

    def _update(self):
        #print 'buddy updated:', self._buddy.status.online
        self._setAvatar()
        self.buddyname.setText(self._buddy.yahoo_id)

        self.status_label.setText('')
        if self._buddy.status.message:
            self.status_label.setText(self._get_link_from_status())

        if self._buddy.status.online:
            if self._buddy.status.idle_time:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-away.png"))
            elif self._buddy.status.code == YAHOO_STATUS_BUSY:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-busy.png"))
            else:
                self.icon_holder.setPixmap(QPixmap(":status/resources/user-online.png"))
        else:
            self.icon_holder.setPixmap(QPixmap(":status/resources/user-offline.png"))

    def _setAvatar(self):
        size = 16
        if not self.compact:
            size = 32
        self.avatar_holder.setPixmap(self._buddy.avatar.scaled(size))

    @property
    def widget(self):
        self._setupLayout()
        return self._widget

    @widget.setter
    def widget(self, widget):
         raise AttributeError('Why are you setting the widget from outside?')

    @property
    def buddy(self):
        return self._buddy

    @buddy.setter
    def buddy(self, buddy):
        self._buddy = buddy
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
        self.toolbar.addAction(QIcon(QPixmap(":actions/resources/list-add-user.png")), 'Add buddy')
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
            self.customStatusCombo.lineEdit().setText('')

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

    def update_buddy(self, emussa, buddy):
        for yid in self.buddy_items:
            if buddy.yahoo_id == yid:
                item = self.buddy_items[yid]
                item.buddy.status = buddy.status

    def received_message(self, emussa, personal_msg):
        message = cyemussa.CyPersonalMessage(personal_msg)
        # find a opened chat with message's sender
        for win in self.chat_windows:
            for chat in win.chatwidgets:
                if chat.buddy.yahoo_id == message.sender:
                    chat.income_message(message)
                    return

        # no already opened chat, open a new one
        if self.buddy_items.has_key(message.sender):
            # buddy already exists, use it
            buddy = buddy_items[message.sender].buddy
        else:
            # create a new buddy
            buddy = cyemussa.CyBuddy()
            buddy.yahoo_id = message.sender
            buddy.nickname = message.sender
            buddy.status = cyemussa.CyStatus()

        win = chatwindow.ChatWindow(self.app, buddy)
        self.chat_windows.append(win)

    def btree_open_chat(self, buddy_item):
        win = chatwindow.ChatWindow(self.app, buddy_item._buddy)
        self.chat_windows.append(win)