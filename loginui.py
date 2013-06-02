import sys
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cyemussa, settingsManager
from libemussa import callbacks as cb
from libemussa import const
from libemussa.im import Buddy, Status

ym = cyemussa.CyEmussa.Instance()
settings = settingsManager.Settings.Instance()

class LoginWindow(QObject):
    def __init__(self, app):
        QObject.__init__(app)
        self.app = app
        self.widget = uic.loadUi('ui/login.ui')

        # bind handlers and callbacks
        self.widget.signInButton.clicked.connect(self.do_signin)
        self.widget.invisibleCheckbox.stateChanged.connect(self.set_invisible_login)
        self.app.will_close.connect(self.close)

        ym.register_callback(cb.EMUSSA_CALLBACK_ISCONNECTING, self.is_connecting)
        ym.register_callback(cb.EMUSSA_CALLBACK_CONNECTIONFAILED, self.connection_error)
        ym.register_callback(cb.EMUSSA_CALLBACK_SIGNINERROR, self.signin_error)
        ym.register_callback(cb.EMUSSA_CALLBACK_SELFCONTACT, self.signin_done)

        # load settings
        self.widget.yahooID.setText(settings.username)
        self.widget.yahooPasswd.setText(settings.password)
        self.widget.rememberCheckbox.setChecked(settings.remember_me in [True, 'true'])
        self.widget.invisibleCheckbox.setChecked(settings.signin_invisible in [True, 'true'])
        self.widget.autoSignInCheckbox.setChecked(settings.signin_auto in [True, 'true'])

        # wait for user input
        self.animate_sleeping()

    def set_invisible_login(self, invisible):
        if not invisible:
            ym.is_invisible = False
        else:
            ym.is_invisible = True

    def animate_sleeping(self):
        for widget in self.widget.findChildren((QLineEdit, QCheckBox, QPushButton, QMenuBar)):
            widget.setEnabled(True)

    def animate_connecting(self):
        for widget in self.widget.findChildren((QLineEdit, QCheckBox, QPushButton, QMenuBar)):
            widget.setEnabled(False)
        # create animation
        pixmap = QPixmap('ui/resources/cyuf-loggedin.png')
        self.widget.loginAnimation.setPixmap(pixmap)

    def auto_signin(self):
        if self.widget.autoSignInCheckbox.isChecked() \
        and self.widget.yahooID.text() \
        and self.widget.yahooPasswd.text():
            self.do_signin()

    def do_signin(self):
        yahoo_id = str(self.widget.yahooID.text())
        yahoo_passwd = str(self.widget.yahooPasswd.text())
        self.save_settings()
        ym.signin(yahoo_id, yahoo_passwd)

    def is_connecting(self, emussa):
        self.animate_connecting()

    def connection_error(self, emussa, e):
        self.animate_sleeping()
        QMessageBox.critical(self.widget, "Connection error", "Connection error. Please check your internet connection and try again.")

    def signin_error(self, emussa, e):
        self.animate_sleeping()
        QMessageBox.critical(self.app.mainw,
                             "Sign in error",
                             "Error while signing in. Please check the provided credentials and try again.\n\n" +
                             "Error reported by the backend: '{0}'".format(e.message)
                             )

    def signin_done(self, emussa, personal_info):
        if self.widget.invisibleCheckbox.isChecked():
            emussa.toggle_visibility(True)
        buddy = cyemussa.CyBuddy()
        buddy.yahoo_id = personal_info.yahoo_id
        buddy.nickname = personal_info.yahoo_id
        buddy.contact.fname = personal_info.name
        buddy.contact.lname = personal_info.surname
        buddy.avatar.get_from_yahoo()

        if emussa.is_invisible:
            buddy.status.code = const.YAHOO_STATUS_INVISIBLE
        else:
            buddy.status.code = const.YAHOO_STATUS_AVAILABLE
        self.app.signed_in(buddy)    # todo: change this into a signal

    def show(self):
        self.widget.show()

    def close(self):
        ym.unregister_callback(cb.EMUSSA_CALLBACK_ISCONNECTING, self.is_connecting)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_CONNECTIONFAILED, self.connection_error)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_SIGNINERROR, self.signin_error)
        ym.unregister_callback(cb.EMUSSA_CALLBACK_SELFCONTACT, self.signin_done)
        self.save_settings()

    def save_settings(self):
        settings.remember_me = self.widget.rememberCheckbox.isChecked()
        settings.signin_invisible = self.widget.invisibleCheckbox.isChecked()
        settings.signin_auto = self.widget.autoSignInCheckbox.isChecked()
        if settings.remember_me:
            settings.username = str(self.widget.yahooID.text())
            settings.password = str(self.widget.yahooPasswd.text())
        else:
            settings.username = ''
            settings.password = ''
