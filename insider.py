import os
from PyQt5 import uic, QtWebKit
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *

class InsiderWebPage(QWebPage):
    def acceptNavigationRequest(self, frame, req, nav_type):
        if nav_type == QWebPage.NavigationTypeFormSubmitted:
            QDesktopServices.openUrl(req.url())
            return True
        else:
            return super(InsiderWebPage, self).acceptNavigationRequest(frame, req, nav_type)

class Insider(QObject):
    def __init__(self, cookies):
        super(Insider, self).__init__()
        self.widget = uic.loadUi('ui/insider.ui')
        self.widget.setFixedSize(700, 550)

        self.cookies = QNetworkCookie.parseCookies('T=' + cookies['T'] + '\r\nY=' + cookies['Y'])
        self.cookieJar = QNetworkCookieJar()
        self.cookieJar.setAllCookies(self.cookies)
        self.widget.webView.setPage(InsiderWebPage())
        self.widget.webView.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(os.getcwd() + '/ui/insider.css'))
        self.widget.webView.page().networkAccessManager().setCookieJar(self.cookieJar)
        self.widget.webView.setUrl(QUrl('http://insider.msg.yahoo.com/?fmt=2.0&intl=us&os=win&ver=11.5.0.192&lang=en-US&fr=cwbtn&t=0'))
        self.widget.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.widget.webView.linkClicked.connect(self.open_url)

        self.widget.show()

    def open_url(self, url):
        QDesktopServices.openUrl(url)
