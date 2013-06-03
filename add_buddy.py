from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import cyemussa
from libemussa import callbacks as cb
ym = cyemussa.CyEmussa.Instance()


class AddBuddyAddressbook(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent):
        QObject.__init__(parent)
        super(AddBuddyAddressbook, self).__init__()
        self.parent = parent

        self.dialog = uic.loadUi('ui/add_buddy_addressbook.ui')
        self.dialog.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.dialog.accepted.connect(self._finished)
        self.dialog.listWidget.itemDoubleClicked.connect(self._finished)
        self.dialog.listWidget.currentRowChanged.connect(self._item_changed)

        self._populateAddressbook()
        self.dialog.show()

    def _populateAddressbook(self):
        for contact in ym.addressbook:
            if contact.yahoo_id:
                item = QListWidgetItem()
                item.contact = contact
                item.setIcon(QIcon(QPixmap('ui/resources/view-conversation-balloon.png')))
                if contact.nickname:
                    item.setText(contact.nickname)
                elif contact.fname or contact.lname:
                    item.setText('{0} {1}'.format(contact.fname, contact.lname))
                else:
                    item.setText(contact.yahoo_id)
                self.dialog.listWidget.addItem(item)
            elif contact.email:
                item = QListWidgetItem()
                item.contact = contact
                item.setIcon(QIcon(QPixmap('ui/resources/mail-mark-unread.png')))
                item.setText(contact.email)
                self.dialog.listWidget.addItem(item)

    def _item_changed(self, item):
        if not item == -1:
            self.dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.dialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def _finished(self):
        item = self.dialog.listWidget.currentItem()
        if item.contact.email:
            self.finished.emit(item.contact.email)
        else:
            self.finished.emit(item.contact.yahoo_id)
        self.dialog.close()


class ChangeName(QObject):
    finished = pyqtSignal(str, str)

    def __init__(self, parent, fname, lname):
        QObject.__init__(parent)
        super(ChangeName, self).__init__()
        self.dialog = uic.loadUi('ui/add_buddy_changename.ui')
        self.dialog.accepted.connect(self._finished)

        self.dialog.fname.setText(fname)
        self.dialog.lname.setText(lname)

        self.dialog.show()

    def _finished(self):
        self.finished.emit(self.dialog.fname.text(), self.dialog.lname.text())


class AddBuddyWizard(QObject):
    def __init__(self, parent, yahoo_id=None):
        QObject.__init__(parent)
        super(AddBuddyWizard, self).__init__()
        self.parent = parent
        self.success = False
        self.timeout = False
        self.fname = ym.me.contact.fname
        self.lname = ym.me.contact.lname

        self.wizard = uic.loadUi('ui/add_buddy.ui')
        self.wizard.setWindowFlags(Qt.Dialog)
        self.wizard.nextId = self._nextId
        self.wizard.myNameLabel.setText('{0} {1}'.format(
            self.fname,
            self.lname)
        )

        if yahoo_id:
            self.wizard.buddyID.setText(yahoo_id)

        ym.register_callback(cb.EMUSSA_CALLBACK_ADDRESPONSE, self._request_response)
        self.wizard.currentIdChanged.connect(self._page_changed)
        self.wizard.buddyID.textChanged.connect(self._id_changed)
        self.wizard.addFromAddressbook.clicked.connect(self._add_from_addressbook)
        self.wizard.changeNameButton.clicked.connect(self._change_name)
        self.wizard.closeEvent = self._closeEvent

        self.wizard.show()
        if not yahoo_id:
            self.wizard.button(QWizard.NextButton).setEnabled(False)
        self._populateGroups()

    def _id_changed(self, text):
        if text:
            self.wizard.button(QWizard.NextButton).setEnabled(True)
        else:
            self.wizard.button(QWizard.NextButton).setEnabled(False)

    def _page_changed(self, index):
        if self.wizard.currentId() == 2:
            self.wizard.choseGroupLabel.setText(
                'Chose or enter a Messenger List group for {0}'.format(self.wizard.buddyID.text())
            )
        if self.wizard.currentId() == 3:
            self.wizard.button(QWizard.NextButton).setEnabled(False)
            self.wizard.button(QWizard.BackButton).setEnabled(False)
            self.wizard.button(QWizard.CancelButton).setEnabled(False)
            self.wizard.labelWait.setText(
                'Please wait while {0} is added to your Messenger List...'.format(self.wizard.buddyID.text())
            )
            ym.add_buddy(
                self.wizard.buddyID.text(),
                self.wizard.groupsCombo.currentText(),
                self.wizard.plainTextEdit.toPlainText(),
                'fname',
                'lname',
                1
            )
            self.timer = QTimer()
            self.timer.timeout.connect(self._timeout)
            self.timer.setSingleShot(True)
            self.timer.start(20000)

        if self.wizard.currentId() == 4:
            self.wizard.button(QWizard.NextButton).setEnabled(False)
            self.wizard.button(QWizard.BackButton).clicked.connect(self._restart)
            self.wizard.button(QWizard.CancelButton).setEnabled(False)
            service = 'Yahoo! Messenger'
            self.wizard.labelError.setText(
                '{0} is not a valid {1} ID. Please check the ID and try again.'.format(
                    self.wizard.buddyID.text(), service
                )
            )
        if self.wizard.currentId() == 5:
            self.wizard.labelSuccess.setText(
                '{0} has been added to your Messenger List and Address Book, pending his or her response to your request.'
                .format(self.wizard.buddyID.text()))
        if self.wizard.currentId() == 6:
            self.wizard.button(QWizard.NextButton).setEnabled(False)
            self.wizard.button(QWizard.BackButton).clicked.connect(self._restart)
            self.wizard.labelTimeout.setText(
                """Your request to add a contact has taken longer than expected to complete.

The operation may have succeeded. Please check your Messenger List later."""
                .format(self.wizard.buddyID.text())
            )

    def _nextId(self):
        if self.wizard.currentId() == 0:    # first page
            # check if buddyID field is empty
            if not self.wizard.buddyID.text():
                return 0
            # check if buddyID already exists
            for yahoo_id in ym.buddy_items:
                if yahoo_id == self.wizard.buddyID.text():
                    text = '{0} already exists in your Messenger List.'.format(self.wizard.buddyID.text())
                    self.wizard.alreadyExistsText.setText(text)
                    return 1
            return 2
        if self.wizard.currentId() == 1:    # buddy already exists page
            return -1
        if self.wizard.currentId() == 2:    # choose group page
            return 3
        if self.wizard.currentId() == 3:    # wait page
            if self.timeout:
                return 6
            if self.success:
                return 5
            else:
                return 4
        if self.wizard.currentId() == 4:    # failure page
            return 0
        if self.wizard.currentId() == 5:    # success page
            return -1
        if self.wizard.currentId() == 6:    # timeout page
            return -1
        return -1

    def _populateGroups(self):
        for group_name in ym.group_items:
            self.wizard.groupsCombo.addItem(group_name, None)

    def _add_from_addressbook(self):
        def addressbook_finished(address):
            self.wizard.buddyID.setText(address)
        self.addressbook_dialog = AddBuddyAddressbook(self)
        self.addressbook_dialog.finished.connect(addressbook_finished)

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

    def _request_response(self, emussa, re):
        self.success = re.success
        self.wizard.next()

    def _closeEvent(self, event):
        ym.unregister_callback(cb.EMUSSA_CALLBACK_ADDRESPONSE, self._request_response)
        event.accept()

    def _restart(self):
        self.wizard.button(QWizard.CancelButton).setEnabled(True)
        self.wizard.button(QWizard.BackButton).clicked.disconnect(self._restart)
        self.wizard.setStartId(0)
        self.wizard.restart()

    def _timeout(self):
        self.timeout = True
        self.wizard.next()
