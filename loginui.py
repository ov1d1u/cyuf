import sys
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cyemussa
from libemussa import callbacks as cb
from libemussa import const
from libemussa.im import Buddy

ym = cyemussa.CyEmussa.Instance()

class LoginWindow:
    def __init__(self, app):
        self.app = app
        ym.register_callback(cb.EMUSSA_CALLBACK_ISCONNECTING, self.is_connecting)
        ym.register_callback(cb.EMUSSA_CALLBACK_CONNECTIONFAILED, self.connection_error)
        ym.register_callback(cb.EMUSSA_CALLBACK_SIGNINERROR, self.signin_error)
        ym.register_callback(cb.EMUSSA_CALLBACK_SELFCONTACT, self.signin_done)

        self.widget = uic.loadUi('ui/login.ui')

        # bind handlers
        self.widget.signInButton.clicked.connect(self.do_signin)

        # wait for user input
        self.animate_sleeping()

    def animate_sleeping(self):
        for widget in self.widget.findChildren((QLineEdit, QCheckBox, QPushButton, QMenuBar)):
            widget.setEnabled(True)
        # create animation
        movie = QMovie('ui/resources/sleeping.gif')
        self.widget.loginAnimation.setMovie(movie)
        movie.start()

    def animate_connecting(self):
        for widget in self.widget.findChildren((QLineEdit, QCheckBox, QPushButton, QMenuBar)):
            widget.setEnabled(False)
        # create animation
        movie = QMovie('ui/resources/joy.gif')
        self.widget.loginAnimation.setMovie(movie)
        movie.start()

    def do_signin(self):
        yahoo_id = str(self.widget.yahooID.text())
        yahoo_passwd = str(self.widget.yahooPasswd.text())
        ym.signin(yahoo_id, yahoo_passwd)

    def is_connecting(self, emmusa):
        self.animate_connecting()

    def connection_error(self, emmusa, e):
        self.animate_sleeping()
        QMessageBox.critical(self.widget, "Connection error", "Connection error. Please check your internet connection and try again.")

    def signin_error(self, emmusa, e):
        self.animate_sleeping()
        QMessageBox.critical(self.widget, 
            "Sign in error",
            "Error while signing in. Please check the provided credentials and try again.\n\n" + 
            "Error reported by the backend: '{0}'".format(e[0].message)
        )

    def signin_done(self, emmusa, personal_info):
        buddy = Buddy()
        buddy.yahoo_id = personal_info.yahoo_id
        buddy.nickname = personal_info.yahoo_id
        buddy.status = const.YAHOO_STATUS_AVAILABLE
        self.app.signed_in(cyemussa.CyBuddy(buddy))    # todo: change this into a signal

    def show(self):
        self.widget.show()
