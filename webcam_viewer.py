from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libemussa import callbacks as cb
import cyemussa

ym = cyemussa.CyEmussa.Instance()


class WebcamViewer(QWidget):
    def __init__(self, parent):
        super(WebcamViewer, self).__init__()
        self.parent = parent
        ym.register_callback(
            cb.EMUSSA_CALLBACK_WEBCAM_IMAGE_READY,
            self.show_image)

        self.widget = uic.loadUi('ui/webcam.ui')
        self.widget.destroyed.connect(self._closed)
        self.widget.buttonBox.clicked.connect(self.close)
        self.widget.setWindowTitle(
            'Webcam for {0}'.format(self.parent.cybuddy.yahoo_id)
        )
        self.widget.timestampLabel.setText('Waiting for permission...')
        self.widget.show()
        pass

    def _closed(self, obj):
        ym.unregister_callback(
            cb.EMUSSA_CALLBACK_WEBCAM_IMAGE_READY,
            self.show_image)

    def show_image(self, ym, wr):
        cdate = QDate.currentDate().toString()
        ctime = QTime.currentTime().toString()
        self.widget.timestampLabel.setText(
            'Last image received at ({0} {1})'.format(cdate, ctime)
        )
        if wr.image:
            pixmap = QPixmap()
            pixmap.loadFromData(wr.image)
            self.widget.webcamImageLabel.setPixmap(pixmap)

    def close(self, button):
        self.widget.destroy()
