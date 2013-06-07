from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import cyemussa
from libemussa import im
from add_buddy import ChangeName
ym = cyemussa.CyEmussa.Instance()


class AuthRequestDialog(QObject):
    def __init__(self, app, auth):
        QObject.__init__(app)
        super(AuthRequestDialog, self).__init__()
        self.app = app
        self.auth = auth
        self.wizard = uic.loadUi('ui/add_confirm_request.ui')

        self.wizard.refuse.toggled.connect(self._change_accept)
        self.wizard.ignore.toggled.connect(self._change_ignore)
        self.wizard.currentIdChanged.connect(self._page_changed)
        self.wizard.accepted.connect(self._finished)
        self.wizard.changeName.clicked.connect(self._change_name)
        self.wizard.nextId = self._nextId

        self.wizard.mainMessage.setText(self.wizard.mainMessage.text().format(
            self.auth.fname, self.auth.lname, self.auth.sender))

        self.wizard.show()

    def _page_changed(self, index):
        if index == 1:
            self.wizard.chooseLabelGroup.setText(self.wizard.chooseLabelGroup.text().format(
                self.auth.sender))
            self.wizard.addRequestMsg.setText(self.wizard.addRequestMsg.text().format(
                self.auth.sender))
            self.wizard.labelName.setText(self.wizard.labelName.text().format(
                self.app.me.contact.fname, self.app.me.contact.lname))

            for group_name in self.app.buddylist.group_items:
                self.wizard.groupsCombo.addItem(group_name, None)
        if index == 2:
            self.wizard.willNotAdd.setText(self.wizard.willNotAdd.text().format(
                self.auth.sender))

    def _nextId(self):
        if self.wizard.currentId() == 0:
            if self.wizard.allow.isChecked():
                return 1
            else:
                return 2
        return -1

    def _change_accept(self, checked):
        self.wizard.addToMyMessenger.setEnabled(not checked)

    def _change_ignore(self, checked):
        self.wizard.labelMessage.setEnabled(not checked)
        self.wizard.rejectMessage.setEnabled(not checked)

    def _finished(self):
        if self.wizard.currentId() == 1:
            ym.accept_auth_request(self.auth.sender)
            if self.wizard.groupsCombo.currentText() in self.app.buddylist.group_items:
                group_item = self.app.buddylist.group_items[self.wizard.groupsCombo.currentText()]
            else:
                new_group = im.Group()
                new_group.name = self.wizard.groupsCombo.currentText()
                group_item = self.app.buddylist.new_group(new_group)

            new_buddy = im.Buddy()
            new_buddy.yahoo_id = self.auth.sender
            self.app.buddylist.new_buddy(new_buddy, group_item)
            group_item.update()
        if self.wizard.currentId() == 2:
            if self.wizard.ignore.isChecked():
                pass  # ignore user
            else:
                message = self.wizard.rejectMessage.toPlainText()
                ym.reject_auth_request(self.auth.sender, message)

    def _change_name(self):
        def change_name_finished(fname, lname):
            self.fname = fname
            self.lname = lname
            self.wizard.myNameLabel.setText('{0} {1}'.format(fname, lname))

        self.changename_dialog = ChangeName(
            self,
            self.fname,
            self.lname)
        self.changename_dialog.finished.connect(change_name_finished)
