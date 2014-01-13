import sip
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import cyemussa, settingsManager
from libemussa import callbacks as cb
from libemussa.const import *
from add_buddy import AddBuddyWizard
from auth_response_dialog import AuthResponseDialog
from auth_request_dialog import AuthRequestDialog
import buddylist_rc, insider, chatwindow, avatar_menu

ym = cyemussa.CyEmussa.Instance()
settings = settingsManager.Settings.Instance()


class GroupItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupItem, self).__init__()
        self.group = group
        self.setHidden(True)

        # Prepare item's widget
        self.widget = QWidget()
        self.label = QLabel('<b>{0}</b>'.format(self.group.name))
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.widget.setLayout(layout)

    def _count_visibles_onlines(self):
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
        if child.cybuddy.status.online:
            child.setHidden(False)
        elif not settings.show_offlines:
            child.setHidden(True)

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
        self._cybuddy.update.connect(self._update)
        self._cybuddy.update_status.connect(self._update_status)
        self._cybuddy.update_avatar.connect(self._setAvatar)

        # Helper timer for renaming a buddy
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._startRename)

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
        self.buddyname.mousePressEvent = self._mousePress
        self.buddyname.mouseReleaseEvent = self._mouseRelease

        # cybuddy status text
        self.status_label = QLabel()
        statusText = self._get_link_from_status()
        self.status_label.setText(statusText[1])
        self.status_label.setToolTip(statusText[0])
        self.status_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.status_label.setOpenExternalLinks(True)

        # Call _update() to populate the widget's data
        self._update()

    def __lt__(self, otherItem):
        if settings.buddylist_sort == 'name':
            return self._cybuddy.display_name.lower() < otherItem.cybuddy.display_name.lower()
        elif settings.buddylist_sort == 'availability':
            if self._cybuddy.status.idle_time:
                if not otherItem.cybuddy.status.online:
                    return True
                return False
            if self._cybuddy.status.code == YAHOO_STATUS_BUSY:
                if otherItem.cybuddy.status.online:
                    return False
                return True
            if self._cybuddy.status.online:
                return True
            return False
        else:
            return self._cybuddy.display_name.lower() < otherItem.cybuddy.display_name.lower()

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
        statusText = self._get_link_from_status()
        self.status_label.setText(statusText[1])
        self.status_label.setToolTip(statusText[0])

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
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        elif 'https://' in statusmsg:
            href = statusmsg[statusmsg.index('https://'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        elif 'www.' in statusmsg:
            href = statusmsg[statusmsg.index('www.'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        else:
            text = '<font color="#8C8C8C">{0}{1}</font>'.format(sep, self._cybuddy.status.message)
            return ['', text]

    def _update(self):
        self.buddyname.setText('{0}'.format(self._cybuddy.display_name))

    def _update_status(self):
        if self._cybuddy.status.online:
            self.setHidden(False)
        else:
            self.setHidden(True)

        self.status_label.setText('')
        if self._cybuddy.status.message:
            statusText = self._get_link_from_status()
            self.status_label.setText(statusText[1])
            self.status_label.setToolTip(statusText[0])

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

    def _mousePress(self, event):
        if event.button() == 1:
            self.timer.start()
        QWidget.mouseReleaseEvent(self._widget, event)

    def _mouseRelease(self, event):
        if event.button() == 1:
            self.timer.stop()
        QWidget.mouseReleaseEvent(self._widget, event)

    def _startRename(self):
        def keyPressed(event):
            QWidget.keyPressEvent(self.lineEdit, event)
            if event.key() == Qt.Key_Escape:
                self._endRename(False)
            elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self._endRename(True)
            else:
                QLineEdit.keyPressEvent(self.lineEdit, event)
        self.timer.stop()
        self.lineEdit = QLineEdit()
        self.lineEdit.keyPressEvent = keyPressed
        self.lineEdit.setFrame(False)
        self.lineEdit.resize(200, 20)
        self.lineEdit.setText(self.buddyname.text())
        self.lineEdit.selectAll()
        self.buddyname.hide()
        if self.compact:
            self.lineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding))
            self.layout.removeWidget(self.buddyname)
            self.layout.insertWidget(2, self.lineEdit)
        else:
            self.lineEdit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.horizontal_layout.removeWidget(self.buddyname)
            self.horizontal_layout.insertWidget(1, self.lineEdit)
        self.lineEdit.show()
        self.lineEdit.setFocus()

    def _endRename(self, save=False):
        if hasattr(self, 'lineEdit'):
            new_name = self.lineEdit.text()
            if self.compact:
                self.layout.removeWidget(self.lineEdit)
                self.layout.insertWidget(2, self.buddyname)
            else:
                self.horizontal_layout.removeWidget(self.lineEdit)
                self.horizontal_layout.insertWidget(1, self.buddyname)
            self.buddyname.show()
            self.lineEdit.close()
            del self.lineEdit
            if save:
                self.cybuddy.display_name = new_name
                contact = self.cybuddy.contact
                contact.yahoo_id = self._cybuddy.yahoo_id
                contact.nickname = new_name
                ym.update_contact(contact)

    def rowChanged(self):
        self._endRename()

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
        self.known_buddies = []  # all known buddies, not just the ones in our buddylist
        self.chat_windows = []
        self.last_group_received = None
        self.avatar_arrow = None

        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDYLIST_RECEIVED, self._buddylist_received)
        ym.register_callback(cb.EMUSSA_CALLBACK_ADDRESSBOOK_RECEIVED, self.addressbook_recv)
        ym.register_callback(cb.EMUSSA_CALLBACK_BUDDY_UPDATE_LIST, self.update_buddies)
        ym.register_callback(cb.EMUSSA_CALLBACK_MESSAGE_IN, self.received_message)
        ym.register_callback(cb.EMUSSA_CALLBACK_AUDIBLE_RECEIVED, self.received_audible)
        ym.register_callback(cb.EMUSSA_CALLBACK_AUTH_REQUEST, self.add_request)
        ym.register_callback(cb.EMUSSA_CALLBACK_AUTH_RESPONSE, self.add_request_response)
        ym.register_callback(cb.EMUSSA_CALLBACK_AUTH_ACCEPTED, self.add_request_accepted)
        ym.register_callback(cb.EMUSSA_CALLBACK_AUTH_REJECTED, self.add_request_rejected)
        ym.register_callback(cb.EMUSSA_CALLBACK_REMOVEBUDDY, self._remove_buddy_remote)
        ym.register_callback(cb.EMUSSA_CALLBACK_MOVEBUDDY, self._move_buddy_remote)
        ym.register_callback(cb.EMUSSA_CALLBACK_AVATAR_UPDATED, self._avatar_updated)
        self.app.me.update_status.connect(self._update_myself)
        self.app.me.update_avatar.connect(self._update_myself)
        self.widget.insiderButton.clicked.connect(self.show_insider)
        # old-style connect to force the calling of activated(QString), not activated(int)
        self.widget.connect(self.widget.customStatusCombo, SIGNAL("activated(const QString&)"), self._set_status_text)
        self.widget.buddyTree.contextMenuEvent = self._buddylist_context_menu
        self.widget.buddyTree.itemDoubleClicked.connect(self.btree_open_chat)
        self.widget.buddyTree.itemCollapsed.connect(self._btree_expand_or_collapse)
        self.widget.buddyTree.itemExpanded.connect(self._btree_expand_or_collapse)
        self.widget.buddyTree.itemSelectionChanged.connect(self._btree_selection_changed)
        self.widget.searchField.textChanged.connect(self._filter_contacts)
        self.widget.addBuddyButton.clicked.connect(self._add_buddy)
        self.widget.avatarButton.clicked.connect(self._showAvatarMenu)

        self.widget.avatarButton.enterEvent = self._avatarButtonEnter
        self.widget.avatarButton.leaveEvent = self._avatarButtonLeave

        self.widget.customStatusCombo.lineEdit().setPlaceholderText("Have something to share?")
        self.widget.customStatusCombo.addItems(settings.statuses)
        self._set_avatar()

        ##################################################
        ## Set up the UI elements (menus, buttons, etc) ##
        ##################################################

        # Buddylist menu
        menu = QMenu(self)
        menuitems = []

        # Action for showing offline contacts
        action = QAction('Show offline contacts', menu, checkable=True)
        action.setShortcut(QKeySequence('Ctrl+H'))
        action.setChecked(settings.show_offlines)
        action.triggered.connect(self._filter_contacts)
        menuitems.append(action)

        # Separator
        action = QAction(self)
        action.setSeparator(True)
        menuitems.append(action)

        # Actions for setting buddylist style (compact/detailed)
        listStyleGroup = QActionGroup(self)  # buddylist style QAction group
        action = QAction('Compact list', menu, checkable=True)
        if settings.compact_list:
            action.setChecked(True)
        action.setShortcut(QKeySequence('Ctrl+Alt+C'))
        action.triggered.connect(self._change_list_style(True))
        listStyleGroup.addAction(action)

        action = QAction('Detailed list', menu, checkable=True)
        if not settings.compact_list:
            action.setChecked(True)
        action.setShortcut(QKeySequence('Ctrl+Alt+D'))
        action.triggered.connect(self._change_list_style(False))
        listStyleGroup.addAction(action)

        menuitems.extend(listStyleGroup.actions())

        # Separator
        action = QAction(self)
        action.setSeparator(True)
        menuitems.append(action)

        # Actions for setting sorting mode
        sortByGroup = QActionGroup(self)  # buddylist style QAction group

        action = QAction('Sort by name', menu, checkable=True)
        if settings.buddylist_sort == 'name':
            action.setChecked(True)
        action.triggered.connect(self._change_list_order('name'))
        sortByGroup.addAction(action)

        action = QAction('Sort by Availability', menu, checkable=True)
        if settings.buddylist_sort == 'availability':
            action.setChecked(True)
        action.triggered.connect(self._change_list_order('availability'))
        sortByGroup.addAction(action)

        action = QAction('Sort by Recent Activity', menu, checkable=True)
        if settings.buddylist_sort == 'activity':
            action.setChecked(True)
        action.triggered.connect(self._change_list_order('activity'))
        sortByGroup.addAction(action)

        menuitems.extend(sortByGroup.actions())
        for action in menuitems:
            menu.addAction(action)

        # Create a button and put it in the 'Buddylist' tab
        self.widget.tab1Btn = QPushButton()
        self.widget.tab1Btn.setFlat(True)
        self.widget.tab1Btn.setMaximumWidth(32)
        self.widget.tab1Btn.setMenu(menu)
        self.widget.tab1Btn.clicked.connect(self._pop_tab_menu)

        self.widget.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, self.widget.tab1Btn)

        # Build status chooser menu
        self.statuses = [
            ['menu-user-online.png', 'Online', YAHOO_STATUS_AVAILABLE],
            ['menu-user-busy.png', 'Busy', YAHOO_STATUS_BUSY],
            ['menu-user-invisible.png', 'Invisible', YAHOO_STATUS_INVISIBLE],
            None,
            ['menu-user-offline.png', 'Sign out', YAHOO_STATUS_STEPPEDOUT]
        ]

        menu = QMenu(self)
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
        self.widget.fakeStatusCombo.setText('{0}'.format(self.app.me.nickname))

    def _avatarButtonEnter(self, event):
        if not self.avatar_arrow:
            self.avatar_arrow = QLabel()
            self.avatar_arrow.setPixmap(QPixmap(":misc/arrow-left.png"))
            self.avatar_arrow.resize(16, 16)
            self.avatar_arrow.move(
                0,
                self.widget.avatarButton.height() - self.avatar_arrow.pixmap().height()
            )
            self.avatar_arrow.setParent(self.widget.avatarButton)
        self.avatar_arrow.show()

    def _avatarButtonLeave(self, event):
        if self.avatar_arrow:
            self.avatar_arrow.hide()

    def _showAvatarMenu(self):
        self.avatarMenu = avatar_menu.AvatarMenu(self.app)
        avatarButtonPos = self.widget.avatarButton.mapToGlobal(self.widget.avatarButton.pos())
        x = avatarButtonPos.x() - self.avatarMenu.widget.width()
        y = avatarButtonPos.y()
        if x < 0:
            x = self.widget.mapToGlobal(self.widget.pos()).x() + self.widget.width()
        self.avatarMenu.widget.move(x, y)
        self.avatarMenu.widget.show()

    def _buddylist_context_menu(self, event):
        item = self.widget.buddyTree.currentItem()
        if not item.__class__ == BuddyItem:
            return

        menu = QMenu(self.widget.buddyTree)

        # Instant message...
        def instant_message():
            self._create_chat_for_buddy(item.cybuddy, True)
        pixmap = QPixmap('ui/resources/view-conversation-balloon.png')
        action = QAction(QIcon(pixmap), 'Instant message...', menu)
        action.triggered.connect(instant_message)
        menu.addAction(action)

        # separator
        action = QAction(menu)
        action.setSeparator(True)
        menu.addAction(action)

        # Start video call
        pixmap = QPixmap('ui/resources/camera-web.png')
        action = QAction(QIcon(pixmap), 'Start video call...', menu)
        menu.addAction(action)

        # Start voice call
        pixmap = QPixmap('ui/resources/audio-headset.png')
        action = QAction(QIcon(pixmap), 'Start voice call...', menu)
        menu.addAction(action)

        # separator
        action = QAction(menu)
        action.setSeparator(True)
        menu.addAction(action)

        ########################
        # More actions... menu #
        ########################
        moremenu = QMenu('More', menu)

        # Send file...
        action = QAction('Send file...', moremenu)
        moremenu.addAction(action)

        # Share photos...
        action = QAction('Share photos...', moremenu)
        moremenu.addAction(action)

        # Invite to an Activity...
        action = QAction('Invite to an Activity...', moremenu)
        moremenu.addAction(action)

        # View webcam
        action = QAction('View webcam...', moremenu)
        moremenu.addAction(action)

        # Invite to view my webcam
        action = QAction('Invite to view my webcam...', moremenu)
        moremenu.addAction(action)

        # Invite to a conference
        action = QAction('Invite to a conference...', moremenu)
        moremenu.addAction(action)

        # Send email
        action = QAction('Send email...', moremenu)
        moremenu.addAction(action)

        # Ringtone
        action = QAction('Ringtone', moremenu)
        moremenu.addAction(action)

        # separator
        action = QAction(menu)
        action.setSeparator(True)
        moremenu.addAction(action)

        # Merge with another contact
        action = QAction('Merge with another contact...', moremenu)
        moremenu.addAction(action)
        ############################

        menu.addMenu(moremenu)

        # separator
        action = QAction(menu)
        action.setSeparator(True)
        menu.addAction(action)

        #########################
        # Stealth settings menu #
        #########################
        stealthmenu = QMenu('Stealth settings', menu)

        action = QAction('Appear Online to {0}'.format(item.cybuddy.display_name), stealthmenu)
        stealthmenu.addAction(action)

        action = QAction('Appear Offline to {0}'.format(item.cybuddy.display_name), stealthmenu)
        stealthmenu.addAction(action)

        action = QAction('Appear Permanently Offline to {0}'.format(item.cybuddy.display_name), stealthmenu)
        stealthmenu.addAction(action)

        # separator
        action = QAction(stealthmenu)
        action.setSeparator(True)
        menu.addAction(action)

        # separator
        action = QAction(stealthmenu)
        action.setSeparator(True)
        stealthmenu.addAction(action)

        action = QAction('Learn More', stealthmenu)
        stealthmenu.addAction(action)

        menu.addMenu(stealthmenu)
        #########################

        # Conversation History
        action = QAction('Conversation History', menu)
        menu.addAction(action)

        # Contact details
        action = QAction('Contact Details', menu)
        menu.addAction(action)

        # View profile
        action = QAction('View Profile', menu)
        menu.addAction(action)

        # separator
        action = QAction(menu)
        action.setSeparator(True)
        menu.addAction(action)

        # Move to group
        def move_buddy():
            from move_buddy import MoveBuddyDialog
            self.movedialog = MoveBuddyDialog(self.app, item.cybuddy)
            self.movedialog.finished.connect(self._move_buddy)
        action = QAction('Move to Group...', menu)
        action.triggered.connect(move_buddy)
        menu.addAction(action)

        # Delete
        def remove_buddy():
            from remove_buddy import RemoveBuddyDialog
            self.removedialog = RemoveBuddyDialog(self.app, item.cybuddy)
            self.removedialog.finished.connect(self._remove_buddy)
        action = QAction('Delete...', menu)
        action.triggered.connect(remove_buddy)
        menu.addAction(action)

        menu.popup(event.globalPos())

    def _buddylist_received(self, emussa, buddylist):
        for group in buddylist:
            parent = self.new_group(group)
            for buddy in buddylist[group]:
                buddy = self.new_buddy(buddy, parent)

        # update groups text
        for gname in self.group_items:
            self.group_items[gname].update()
        ym.get_addressbook()

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
            if not self.app.me.status.code == YAHOO_STATUS_INVISIBLE:
                ym.toggle_visibility(True)

        elif self.app.me.status.code == YAHOO_STATUS_INVISIBLE:
            if not avlbcode == YAHOO_STATUS_INVISIBLE:
                ym.toggle_visibility(False)

        if not avlbcode == YAHOO_STATUS_INVISIBLE:
            ym.set_status(avlbcode, self.app.me.status.message)

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
                self.buddy_items[item].rowChanged()
                self.buddy_items[item].compact = compact
                self.widget.buddyTree.setItemWidget(self.buddy_items[item], 0, self.buddy_items[item].widget)
            # hack to force properly update of buddyTree
            self.widget.buddyTree.resize(self.widget.buddyTree.size().width() - 1, self.widget.buddyTree.size().height())
            self.widget.buddyTree.resize(self.widget.buddyTree.size().width() + 1, self.widget.buddyTree.size().height())
            settings.compact_list = compact
        return change_list_style

    def _change_list_order(self, order):
        def change_list_order():
            settings.buddylist_sort = order
            self.widget.buddyTree.sortItems(0, Qt.AscendingOrder)
        return change_list_order

    def _filter_contacts(self, filter):
        # bool means that the filter was applied from 'Show offline buddies' menu
        if type(filter) == bool:
            settings.show_offlines = filter
        self._filter_buddylist()

        # update groups text
        for gname in self.group_items:
            self.group_items[gname].update()

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

    def _btree_expand_or_collapse(self, item):
        if not item.group.name in settings.group_settings:
            settings.group_settings[item.group.name] = {}
        settings.group_settings[item.group.name]['collapsed'] = not item.isExpanded()
        settings.settings.setValue('group_settings', settings.group_settings)

    def _btree_selection_changed(self):
        for yid in self.buddy_items:
            self.buddy_items[yid].rowChanged()

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
        self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))

        # update ourself entry from the buddylist, if it exists
        cybuddy = self._get_buddy(self.app.me.yahoo_id)
        if cybuddy:
            cybuddy.avatar.image = QIcon(self.app.me.avatar.image).pixmap(QSize(96, 96))

    def _get_buddy(self, yahoo_id):
        for cybuddy in self.known_buddies:
            if yahoo_id == cybuddy.yahoo_id:
                return cybuddy
        # create a new cybuddy
        cybuddy = cyemussa.CyBuddy()
        cybuddy.yahoo_id = yahoo_id
        cybuddy.display_name = yahoo_id
        cybuddy.status = cyemussa.CyStatus()
        self.known_buddies.append(cybuddy)
        return cybuddy

    def _get_item_for_buddy(self, yahoo_id):
        iterator = QTreeWidgetItemIterator(self.widget.buddyTree)
        while iterator.value():
            if type(iterator.value()) == BuddyItem:
                item = iterator.value()
                if item.cybuddy.yahoo_id == yahoo_id:
                    return item
            iterator += 1
        return None

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

    def _add_buddy(self):
        self.wizard = AddBuddyWizard(self.app)

    def _remove_buddy(self, cybuddy, rm_contact=False, reverse=False):
        ym.remove_buddy(cybuddy.yahoo_id, cybuddy.group.name)
        if reverse:
            ym.reject_auth_request(cybuddy.yahoo_id)
        self.remove_from_btree(cybuddy.yahoo_id)

    def _remove_buddy_remote(self, emussa, rem):
        self.remove_from_btree(rem.yahoo_id)

    def _move_buddy_remote(self, emussa, mv):
        self.move_buddy(mv.yahoo_id, mv.to_group)

    def _move_buddy(self, who, where):
        cybuddy = self._get_buddy(who)
        if cybuddy:
            cgroup = cybuddy.group.name     # current group name
            ym.move_buddy(who, cgroup, where)
            self.move_buddy(who, where)

    def _avatar_updated(self, emussa, display_image):
        if display_image.yahoo_id == self.app.me.yahoo_id:
            self.app.me.avatar = display_image
            self.widget.avatarButton.setIcon(QIcon(self.app.me.avatar.image))
        buddy = self._get_buddy(display_image.yahoo_id)
        if buddy:
            buddy.avatar = display_image

    def show_insider(self):
        self.i = insider.Insider(
            {'T': ym.t_cookie,
             'Y': ym.y_cookie})

    def addressbook_recv(self, emussa, contacts):
        for contact in contacts:
            for cybuddy in self.known_buddies:
                if cybuddy.yahoo_id == contact.yahoo_id:
                    cybuddy.contact = contact

    def update_buddies(self, emussa, buddies):
        for cybuddy in buddies:
            for yid in self.buddy_items:
                if cybuddy.yahoo_id == yid:
                    item = self.buddy_items[yid]
                    item.cybuddy.status = cybuddy.status

        self._filter_buddylist()
        self.widget.buddyTree.sortItems(0, Qt.AscendingOrder)

    def new_group(self, group):
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

    def new_buddy(self, buddy, parent):
        if buddy.ignored:
            return
        if buddy.pending:
            buddy.status.message = '<i>Add request pending</i>'
        compact = settings.compact_list
        cybuddy = cyemussa.CyBuddy(buddy)
        cybuddy.group = parent.group
        item = BuddyItem(cybuddy, compact)
        parent.addChild(item)
        self.widget.buddyTree.setItemWidget(item, 0, item.widget)
        self.buddy_items[buddy.yahoo_id] = item
        self.known_buddies.append(cybuddy)
        ym.get_display_image(cybuddy.yahoo_id)
        return item

    def received_message(self, emussa, personal_msg):
        message = cyemussa.CyPersonalMessage(personal_msg)
        if personal_msg.sender:
            cybuddy = self._get_buddy(personal_msg.sender)
        else:
            # we sent this message, but from another device
            cybuddy = self._get_buddy(personal_msg.receiver)
        chat = self._create_chat_for_buddy(cybuddy)
        chat.receive_message(message)

    def received_audible(self, emussa, audible):
        if audible.sender:
            cybuddy = self._get_buddy(audible.sender)
        else:
            # we sent this message, but from another device
            cybuddy = self._get_buddy(audible.receiver)
        chat = self._create_chat_for_buddy(cybuddy)
        chat.receive_audible(audible)

    def add_request(self, emussa, auth):
        # Somebody asks us to authorize his add request
        self.authrequest = AuthRequestDialog(self.app, auth)
        pass

    def add_request_response(self, emussa, auth):
        # This is called while adding a user in our buddylist
        # and Yahoo! servers confirms the adding
        buddyItem = self._get_item_for_buddy(auth.sender)
        if buddyItem:
            buddyItem.cybuddy.pending = False
            buddyItem.cybuddy.status.message = ''

    def add_request_accepted(self, emussa, auth):
        buddyItem = self._get_item_for_buddy(auth.sender)
        buddyItem.cybuddy.status.pending = False
        buddyItem.cybuddy.status.message = ''

    def add_request_rejected(self, emussa, auth):
        self.authresponse = AuthResponseDialog(self.app, auth)

    def btree_open_chat(self, buddy_item):
        self._create_chat_for_buddy(buddy_item.cybuddy, True)

    def remove_from_btree(self, yahoo_id):
        item = self._get_item_for_buddy(yahoo_id)
        if item:
            sip.delete(item)
            del self.buddy_items[yahoo_id]

    def move_buddy(self, yahoo_id, group_name):
        item = self._get_item_for_buddy(yahoo_id)
        if item:
            # remove first from its current group
            for group in self.group_items:
                if group == item.cybuddy.group.name:
                    self.group_items[group].removeChild(item)

            # add it to the new group
            for group in self.group_items:
                if group == group_name:
                    self.group_items[group].addChild(item)
                    item.cybuddy.group = self.group_items[group].group
                    self.widget.buddyTree.setItemWidget(
                        self.buddy_items[item.cybuddy.yahoo_id],
                        0,
                        self.buddy_items[item.cybuddy.yahoo_id].widget
                    )

    def sign_out(self):
        ym.signout()

    def close(self, emussa=None):
        ym.unregister_callback(cb.EMUSSA_CALLBACK_BUDDYLIST_RECEIVED, self._buddylist_received)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_ADDRESSBOOK_RECEIVED, self.addressbook_recv)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_BUDDY_UPDATE_LIST, self.update_buddies)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_MESSAGE_IN, self.received_message)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AUDIBLE_RECEIVED, self.received_audible)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_SIGNED_OUT, self.close)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AUTH_REQUEST, self.add_request)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AUTH_RESPONSE, self.add_request_response)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AUTH_ACCEPTED, self.add_request_accepted)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AUTH_REJECTED, self.add_request_rejected)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_REMOVEBUDDY, self._remove_buddy_remote)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_MOVEBUDDY, self._move_buddy_remote)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_AVATAR_UPDATED, self._avatar_updated)
