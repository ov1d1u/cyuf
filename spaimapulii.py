from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
  
import sys
  
class Formaa(QObject):
  def __init__(self, parent=None):
      print "init"
  
  def proccess_finished(self, reply):
      print reply.header(QNetworkRequest.ContentTypeHeader).toString()
      QCoreApplication.quit()
  
  def readyRead(self, bytesReceived, bytesTotal):
      d = bytesReceived*100/bytesTotal
      print "bytesReceived: "+ str(d) + " bytesTotal: "+ str(bytesTotal) 
  
  def download(self):
      self.manager = QNetworkAccessManager() 
  
      QObject.connect(self.manager, SIGNAL("finished(QNetworkReply *)"),self.proccess_finished)
      self.request = QNetworkRequest(QUrl("http://img.msg.yahoo.com/avatar.php?yids=startx.ovidiu"))
      #self.request = QNetworkRequest(QUrl("http://www.google.com/"))
      self.request.setRawHeader('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)')
      self.reply = self.manager.get(self.request)
      self.reply.downloadProgress.connect(self.readyRead)
      #QObject.connect(self.reply,SIGNAL("downloadProgress(int, int)"), self.readyRead)
  
if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    test = Formaa()
    test.download()
    sys.exit(app.exec_())