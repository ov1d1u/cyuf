from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork  import *

class Avatar(QObject):
    avatar_fetched_signal = pyqtSignal(str, QPixmap)

    def __init__(self, yahoo_id):
        super(Avatar, self).__init__()
        self.yahoo_id = yahoo_id
        self._get_avatar()

    def _get_avatar(self):
        self.manager = QNetworkAccessManager()
        QObject.connect(self.manager, SIGNAL("finished(QNetworkReply *)"),self.avatar_done)
        self.req = QNetworkRequest(QUrl("http://img.msg.yahoo.com/avatar.php?yids={0}".format(self.yahoo_id)))
        self.req.setRawHeader('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)')
        self.reply = self.manager.get(self.req)

    def avatar_done(self, reply):
        imgdata = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(imgdata)
        self.avatar_fetched_signal.emit(self.yahoo_id, pixmap)