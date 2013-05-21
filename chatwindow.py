from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

from chatwidget import ChatWidget

class ChatWindow(QObject):
	def __init__(self, app, buddy):
		self.widget = uic.loadUi('ui/chatwindow.ui')
		self.app = app
		self.buddy = buddy
		self.chatwidgets = []

		self.widget.setWindowTitle('{0} - Cyuf'.format(self.buddy.yahoo_id))
		self.chatwidgets.append(ChatWidget(self, buddy))
		self.widget.tabWidget.addTab(self.chatwidgets[-1:][0].widget, buddy.yahoo_id)

		self.widget.show()
