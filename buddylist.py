from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import cyemussa, settingsManager
from libemussa import callbacks as cb
from libemussa.const import *
import buddylist_rc, insider, chatwindow

ym = cyemussa.CyEmussa.Instance()
settings = settingsManager.Settings.Instance()


class GroupItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupItem, self).__init__()
        self.group = group
        self._initWidget()

    def _initWidget(self):
        self.widget = QWidget()
        self.label = QLabel('<b>{0}</b>'.format(self.group.name))
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.widget.setLayout(layout)

    def _count_visibles_onlines(self):  # merge these two methods for performance
        onlines = 0
        visibles = 0
        for i in range(0, self.childCount()):
            if not self.child(i).isHidden():
                visibles += 1
            if self.child(i).cybuddy.status.online:
                onlines += 1
        return (visibles, onlines)

    def addChild(self, child):
        super(GroupItem, self).addChild(child)
        self.update()

    def update(self):
        text = '<b>{0}</b>'.format(self.group.name)
        visibles, on = self._count_visibles_onlines()
        show_offlines = settings.show_offlines
        if not visibles:
            self.setHidden(True)
        elif not on and not show_offlines:
            self.setHidden(True)
        else:
            self.setHidden(False)
            if show_offlines:
                text = '{0} ({1}/{2})'.format(text, on, self.childCount())
            else:
                text = '{0} ({1})'.format(text, on)
            self.label.setText(text)


class BuddyItem(QTreeWidgetItem):
    def __init__(self, cybuddy, compact=True):
        super(BuddyItem, self).__init__()
        self.compact = compact
        self._cybuddy = cybuddy
        self._initWidget()
        self._update()
        self._cybuddy.update.connect(self._update)

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
        self.layout.setContentsMargins(2, 1, 2, 1)

        if not self.compact:
            self.right_widget = QWidget()
            self.vertical_layout = QVBoxLayout(self.right_widget)
            self.vertical_layout.setContentsMargins(2, 1, 2, 1)
            self.horizontal_layout = QHBoxLayout()

        self.layout.addWidget(self.avatar_holder)
        self._setAvatar()
        self.status_label.setText(self._get_link_from_status())

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
        if self.compact and self._cybuddy.status.message:
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
        self._setAvatar()
        self.buddyname.setText('{0}'.format(self._cybuddy.display_name))

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

        if self.parent():  # item doesn't have a parent() yet when it's created
            self.parent().update()

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


class BuddyList(QWidget, QObject):
    def __init__(self, app):
        QObject.__init__(app)
        super(BuddyList, self).__init__()
        self.widget = uic.loadUi('ui/buddylist.ui')
        self.app = app
        self.group_items = {}
        self.buddy_items = {}
        self.chat_windows = []
        self.last_group_received = None

        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDYLIST_RECEIVED, self._buddylist_received)
        ym.register_callback(cb.EMUSSA_CALLBACK_ADDRESSBOOK_RECEIVED, self.addressbook_recv)
        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDY_UPDATE, self.update_buddy)
        ym.register_callback(cb.EMUSSA_CALLBACK_MESSAGE_IN, self.received_message)
        self.app.me.update.connect(self._update_myself)
        self.widget.insiderButton.clicked.connect(self.show_insider)
        # old-style connect to force the calling of activated(QString), not activated(int)
        self.widget.connect(self.widget.customStatusCombo, SIGNAL("activated(const QString&)"), self._set_status_text)
        self.widget.buddyTree.itemDoubleClicked.connect(self.btree_open_chat)
        self.widget.buddyTree.itemCollapsed.connect(self._btree_expand_or_collapse)
        self.widget.buddyTree.itemExpanded.connect(self._btree_expand_or_collapse)
        self.widget.searchField.textChanged.connect(self._filter_contacts)

        self.widget.customStatusCombo.lineEdit().setPlaceholderText("Have something to share?")
        self.widget.customStatusCombo.addItems(settings.statuses)
        self._build_tab_menus()
        self._build_statuses()
        self._set_avatar()

    def _build_tab_menus(self):
        menu = QMenu()
        menuitems = []

        action = QAction('Show offline contacts', menu, checkable=True)
        action.setShortcut(QKeySequence('Ctrl+H'))
        action.setChecked(settings.show_offlines)
        action.triggered.connect(self._filter_contacts)
        menuitems.append(action)

        action = QAction(self)
        action.setSeparator(True)
        menuitems.append(action)

        """ BuddyList style actions """
        listStyleGroup = QActionGroup(self)  # buddylist style QAction group

        action = QAction('Compact list', menu, checkable=True)
        if settings.compact_list:
            action.setChecked(True)
        action.triggered.connect(self._change_list_style(True))
        listStyleGroup.addAction(action)

        action = QAction('Detailed list', menu, checkable=True)
        if not settings.compact_list:
            action.setChecked(True)
        action.triggered.connect(self._change_list_style(False))
        listStyleGroup.addAction(action)

        menuitems.extend(listStyleGroup.actions())
        """ ---- """

        self.widget.tab1Btn = QPushButton()
        self.widget.tab1Btn.setFlat(True)
        self.widget.tab1Btn.setMaximumWidth(32)

        for action in menuitems:
            menu.addAction(action)

        self.widget.tab1Btn.setMenu(menu)
        self.widget.tab1Btn.clicked.connect(self._pop_tab_menu)

        self.widget.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, self.widget.tab1Btn)

    def _build_statuses(self):
        self.statuses = [
            ['menu-user-online.png', 'Online', YAHOO_STATUS_AVAILABLE],
            ['menu-user-busy.png', 'Busy', YAHOO_STATUS_BUSY],
            ['menu-user-invisible.png', 'Invisible', YAHOO_STATUS_INVISIBLE],
            None,
            ['menu-user-offline.png', 'Sign out', YAHOO_STATUS_STEPPEDOUT]
        ]

        menu = QMenu()
        for status in self.statuses:
            if not status:
                action = QAction(self)
                action.setSeparator(True)
                menu.addAction(action)
            else:
                pixmap = QPixmap(":status/resources/" + status[0])
                action = QAction(QIcon(pixmap), status[1], self)
                action.setData(status[2])
                menu.addAction(action)
        menu.triggered.connect(self._set_availability)

        self.widget.fakeStatusCombo.setMenu(menu)
        #self.widget.fakeStatusCombo.setText('{0} {1}'.format(self.app.me.contact.name, self.app.me.contact.surname))
        self.widget.fakeStatusCombo.setText('{0}'.format(self.app.me.nickname))

    def _buddylist_received(self, emussa, buddylist):
        for group in buddylist:
            parent = self._new_group(group)
            for buddy in buddylist[group]:
                buddy = self._new_buddy(buddy, parent)

    def _new_group(self, group):
        item = GroupItem(group)
        self.widget.buddyTree.addTopLevelItem(item)
        self.widget.buddyTree.setItemWidget(item, 0, item.widget)
        self.group_items[group.name] = item
        if group.name in settings.group_settings:
            if 'collapsed' in settings.group_settings[group.name]:
                item.setExpanded(not settings.group_settings[group.name]['collapsed'])
        else:
            item.setExpanded(True)
        return item

    def _new_buddy(self, buddy, parent):
        if buddy.ignored:
            return
        compact = settings.compact_list
        item = BuddyItem(cyemussa.CyBuddy(buddy), compact)
        parent.addChild(item)
        self.widget.buddyTree.setItemWidget(item, 0, item.widget)
        self.buddy_items[buddy.yahoo_id] = item
        # connect to buddy updates for updating its visibility in buddylist
        item.cybuddy.update.connect(self._filter_buddylist)
        return item


    def _set_avatar(self):
        self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))

    def _set_availability(self, action):
        if type(action) == QAction:
            avlbcode = action.data()
        else:
            avlbcode = int(action)

        if avlbcode == YAHOO_STATUS_STEPPEDOUT:
            self.sign_out()
            return

        if avlbcode == YAHOO_STATUS_INVISIBLE:
            self.widget.customStatusCombo.lineEdit().setText('')

        if not avlbcode == self.app.me.status.code:
            # toggle visibility
            if avlbcode == YAHOO_STATUS_INVISIBLE:
                ym.toggle_visibility(True)
            else:
                ym.toggle_visibility(False)
            self.app.me.status.code = avlbcode

    def _set_status_text(self, text):
        if text and self.app.me.status.code == YAHOO_STATUS_INVISIBLE:
            self._set_availability(YAHOO_STATUS_AVAILABLE)
        ym.set_status(self.app.me.status.code, str(text))
        statuses = settings.statuses
        if not text in statuses:
            statuses.append(text)
        settings.statuses = statuses

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
            settings.compact_list = compact
        return change_list_style

    def _filter_contacts(self, filter):
        # bool means that the filter was applied from 'Show offline buddies' menu
        if type(filter) == bool:
            settings.show_offlines = filter
        self._filter_buddylist()

    def _filter_buddylist(self):
        iterator = QTreeWidgetItemIterator(self.widget.buddyTree)
        filtertext = self.widget.searchField.text()
        if filtertext:
            self.widget.buddyTree.expandAll()

        while iterator.value():
            if type(iterator.value()) == BuddyItem:
                item = iterator.value()
                if filtertext:
                    searchables = [item.cybuddy.yahoo_id, item.cybuddy.contact.fname,
                        item.cybuddy.contact.lname, item.cybuddy.contact.nickname]
                    if any(filtertext.lower() in field.lower() for field in searchables):
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                elif not settings.show_offlines and not item.cybuddy.status.online:
                    item.setHidden(True)
                else:
                    item.setHidden(False)
            iterator += 1

        # update groups text
        for gname in self.group_items:
            self.group_items[gname].update()

    def _btree_expand_or_collapse(self, item):
        if not item.group.name in settings.group_settings:
            settings.group_settings[item.group.name] = {}
        settings.group_settings[item.group.name]['collapsed'] = not item.isExpanded()
        # force setting value because changing dict content
        # doesn't triggers __setattr__ in Settings() class
        settings.settings.setValue('group_settings', settings.group_settings)

    def _update_myself(self):
        icon = None
        for status in self.statuses:
            if not status:
                continue
            if status[2] == self.app.me.status.code:
                icon = QIcon(QPixmap(":status/resources/" + status[0]))
                break
        if icon:
            self.widget.fakeStatusCombo.setIcon(icon)

        ym.set_status(self.app.me.status.code, self.app.me.status.message)
        self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))
        ym.get_addressbook()

    def _get_buddy(self, yahoo_id):
        if yahoo_id in self.buddy_items:
            return self.buddy_items[yahoo_id].cybuddy
        # create a new cybuddy
        cybuddy = cyemussa.CyBuddy()
        cybuddy.yahoo_id = yahoo_id
        cybuddy.nickname = yahoo_id
        cybuddy.status = cyemussa.CyStatus()
        return cybuddy

    def _create_chat_for_buddy(self, cybuddy, focus_chat=False):
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
            {'T': ym.t_cookie,
             'Y': ym.y_cookie})

    def addressbook_recv(self, emussa, contacts):
        for contact in contacts:
            if contact.yahoo_id and contact.yahoo_id in self.buddy_items:
                self.buddy_items[contact.yahoo_id].cybuddy.contact = contact

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
            # we sent this message, but from another device
            cybuddy = self._get_buddy(personal_msg.receiver)
        chat = self._create_chat_for_buddy(cybuddy)
        chat.receive_message(message)

    def btree_open_chat(self, buddy_item):
        self._create_chat_for_buddy(buddy_item.cybuddy, True)

    def sign_out(self):
        ym.signout()

    def close(self, emussa=None):
        ym.unregister_callback(cb.EMUSSA_CALLBACK_BUDDYLIST_RECEIVED, self._buddylist_received)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_ADDRESSBOOK_RECEIVED, self.addressbook_recv)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_BUDDY_UPDATE, self.update_buddy)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_MESSAGE_IN, self.received_message)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_SIGNED_OUT, self.close)
