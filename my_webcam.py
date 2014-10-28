from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from libemussa import callbacks as cb
from webcam_source import WebcamSource
import cyemussa
import settingsManager

ym = cyemussa.CyEmussa.Instance()
settings = settingsManager.Settings.Instance()


class MyWebcam(QWidget):
    def __init__(self, parent):
        super(MyWebcam, self).__init__(parent)
        self.parent = parent
        self.webcam_source = WebcamSource()

        ym.register_callback(cb.EMUSSA_CALLBACK_WEBCAM_READY_FOR_TRANSMISSION,
                             self.ready)

        self.widget = uic.loadUi('ui/my_webcam.ui')
        self.widget.closeEvent = self._closed
        self.widget.show()

        self.image_timer = QTimer()
        self.image_timer.timeout.connect(self.show_image)

        self.start_broadcast()

    def _closed(self, event):
        self.image_timer.stop()
        self.webcam_source.stop()
        ym.unregister_callback(
            cb.EMUSSA_CALLBACK_WEBCAM_READY_FOR_TRANSMISSION,
            self.ready)

    def start_broadcast(self):
        self.webcam_source.start(settings.get('webcamSource', ''))
        self.image_timer.start(1000)

    def show_image(self):
        self.widget.webcamImageLabel.setPixmap(self.webcam_source.get_image())

    def ready(self, emussa, w):
        print('GO GO GO!!!')
