#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cyemussa, loginui, buddylist

class Cyuf:
    personal_info = None

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.me = cyemussa.CyBuddy()         # our buddy instance
        self.init_emussa()

    def init_emussa(self):
        self.ym = cyemussa.CyEmussa.Instance()
        self.ym.debug.level = 3

    def main(self):
        self.mainw = uic.loadUi('ui/main.ui')
        self.mainw.show()

        # show the login form
        self.login()

        self.app.exec_()
        self.ym.disconnect()
        self.quit()

    def login(self):
        self.loginUI = loginui.LoginWindow(self)
        self.mainw.setCentralWidget(self.loginUI.widget)

    def signed_in(self, cybuddy):
        # TODO: change Buddy() class to have a Contact() property
        self.me = cybuddy

        # show the buddylist
        self.buddyList = buddylist.BuddyList(self)
        self.mainw.setCentralWidget(self.buddyList.widget)

    def quit(self):
        sys.exit(0)

if __name__ == '__main__':
    cyuf = Cyuf()
    cyuf.main()