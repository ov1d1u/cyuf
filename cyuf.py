#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cyemussa, loginui, buddylist, settingsManager
from preferences import Preferences
from libemussa import callbacks as cb
settings = settingsManager.Settings.Instance()
ym = cyemussa.CyEmussa.Instance()

QCoreApplication.setApplicationName("Cyuf Messenger")
QCoreApplication.setOrganizationName("Ovidiu Nitan")
QCoreApplication.setApplicationVersion("0.1 alpha")
QDir().mkpath(QStandardPaths.standardLocations(QStandardPaths.DataLocation)[0])


class Cyuf(QObject):
    buddylist = None
    will_close = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.qapp = QApplication(sys.argv)
        #self.qapp.setStyle("Cleanlooks")
        self.init_emussa()

    def init_emussa(self):
        self.ym = cyemussa.CyEmussa.Instance()
        self.ym.debug.level = 3
        self.ym.register_callback(cb.EMUSSA_CALLBACK_DISCONNECTED, self.disconnected)

    def main(self):
        self.mainw = uic.loadUi('ui/main.ui')
        self.mainw.actionPreferences.triggered.connect(self.show_preferences)
        self.mainw.actionMyWebcam.triggered.connect(self.show_my_webcam)

        self.mainw.setGeometry(settings.winrect)
        self.mainw.show()
        self.mainw.closeEvent = self.closeMainWindow

        # show the login form
        self.login()

        self.qapp.exec_()
        self.ym.disconnect()
        self.quit()

    def login(self):
        self.loginUI = loginui.LoginWindow(self)
        self.loginUI.auto_signin()
        self.mainw.setCentralWidget(self.loginUI.widget)

    def signed_in(self, cybuddy):
        # TODO: change Buddy() class to have a Contact() property
        self.me = cybuddy

        # show the buddylist
        self.loginUI.close()
        if self.buddylist:
            self.buddylist.close()
        self.buddylist = buddylist.BuddyList(self)
        self.mainw.setCentralWidget(self.buddylist.widget)

    def show_preferences(self):
        self.preferences = Preferences(self.mainw)
        self.preferences.populateCategories()

    def show_my_webcam(self):
        if self.buddylist:
            self.buddylist.show_my_webcam()

    def disconnected(self, emussa=None):
        self.loginUI = loginui.LoginWindow(self)
        self.mainw.setCentralWidget(self.loginUI.widget)

    def closeMainWindow(self, event):
        self.will_close.emit()
        settings.winrect = self.mainw.geometry()

    def quit(self):
        sys.exit(0)

if __name__ == '__main__':
    cyuf = Cyuf()
    cyuf.main()
