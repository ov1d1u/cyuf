from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from webcam_source import WebcamSource


class WebcamSourceDialog(QObject):
    def __init__(self, parent, settings):
        super(WebcamSourceDialog, self).__init__(parent)
        self.settings = settings
        self.widget = uic.loadUi('ui/preferences_webcam_source.ui')
        self.widget.accepted.connect(self.accept)
        self.widget.rejected.connect(self.reject)
        self.widget.browseBtn.clicked.connect(self.browse_files)
        self.widget.sourcesComboBox.currentIndexChanged.connect(
            self.source_changed)
        self.loadSettings()

    def loadSettings(self):
        wsource = WebcamSource()
        self.widget.sourcesComboBox.addItem('')
        for source in wsource.sources:
            url = QUrl(source)
            if url.scheme() == 'cam':
                self.widget.sourcesComboBox.addItem(
                    'Camera at {0}'.format(url.path()),
                    source)
            elif url.scheme() == 'image':
                self.widget.sourcesComboBox.addItem(
                    'Image file',
                    source)
            elif url.scheme() == 'video':
                self.widget.sourcesComboBox.addItem(
                    'Video file',
                    source)
            elif url.scheme() == 'ymsg':
                pass

            self.widget.sourceURL.setText(
                QUrl(self.settings.get('webcamSource', '')).path()
            )
            if self.settings.get('webcamSource', '').startswith(source):
                    self.widget.sourcesComboBox.setCurrentIndex(
                        wsource.sources.index(source) + 1)

    def browse_files(self):
        source = self.widget.sourcesComboBox.itemData(
            self.widget.sourcesComboBox.currentIndex())
        if source.startswith('image://'):
            file_types = "Image Files (*.png *.jpg *.bmp)"
        elif source.startswith('video://'):
            file_types = "Video Files (*.avi *.mp4 *.mkv *.wmv)"
        else:
            file_types = "Any File (*.*)"

        filepath = QFileDialog.getOpenFileName(
            self.widget,
            "Select a source file",
            QDir.homePath(),
            file_types
        )

        self.widget.sourceURL.setText(filepath)

    def accept(self):
        source = self.widget.sourcesComboBox.itemData(
            self.widget.sourcesComboBox.currentIndex())
        if not source.startswith('cam://'):
            source += self.widget.sourceURL.text()
        self.settings['webcamSource'] = source
        self.widget.close()

    def reject(self):
        self.widget.close()

    def source_changed(self, index):
        item_data = self.widget.sourcesComboBox.itemData(
            self.widget.sourcesComboBox.currentIndex())

        if item_data and item_data.startswith('cam://'):
            self.widget.srcLocationFrame.hide()
        else:
            self.widget.srcLocationFrame.show()


class Preference(QObject):
    def __init__(self, parent, settings):
        super(Preference, self).__init__(parent)

        self.settings = settings
        self.widget = uic.loadUi('ui/preferences_webcam.ui')
        self.widget.cameraSourceButton.clicked.connect(self.source_choose)
        self.loadSettings()

    def loadSettings(self):
        self.widget.cameraQualitySlider.setValue(
            int(self.settings.get('webcamQuality', 0))
        )
        if self.settings.get('webcamPrivacy', 'ask') == 'ask':
            self.widget.webcamAsk.setChecked(True)
        elif self.settings.get('webcamPrivacy', 'ask') == 'allowEveryone':
            self.widget.webcamAllowEveryone.setChecked(True)
        elif self.settings.get('webcamPrivacy', 'ask') == 'allowSelected':
            self.widget.webcamAllowSelected.setChecked(True)
        for people in self.settings.get('webcamPeople', []):
            self.widget.webcamPeopleList.addItem(people)
        if self.settings.get('webcamIgnore', False):
            self.widget.webcamIgnoreOther.setChecked(True)
        if self.settings.get('webcamInChat', False):
            self.widget.webcamInChat.setChecked(True)
        if self.settings.get('webcamChangeStatus', True):
            self.widget.webcamChangeStatus.setChecked(True)
        self.widget.webcamStatus.setText(
            self.settings.get('webcamStatus', 'View My Webcam')
        )

    def apply(self):
        self.save()

    def save(self):
        self.settings['webcamQuality'] = self.widget.cameraQualitySlider.\
            value()
        if self.widget.webcamAsk.isChecked():
            self.settings['webcamPrivacy'] = 'ask'
        elif self.widget.webcamAllowEveryone.isChecked():
            self.settings['webcamPrivacy'] = 'allowEveryone'
        elif self.widget.webcamAllowSelected.isChecked():
            self.settings['webcamPrivacy'] = 'allowSelected'
        people = []
        for index in range(self.widget.webcamPeopleList.count()):
            people.append(self.widget.webcamPeopleList.text())
        self.settings['webcamPeople'] = people
        if self.widget.webcamIgnoreOther.isChecked():
            self.settings['webcamIgnore'] = True
        if self.widget.webcamInChat.isChecked():
            self.settings['webcamInChat'] = True
        if self.widget.webcamChangeStatus.isChecked():
            self.settings['webcamChangeStatus'] = True
        self.settings['webcamStatus'] = self.widget.webcamStatus.text()

    def source_choose(self):
        wsdialog = WebcamSourceDialog(self.widget, self.settings)
        wsdialog.widget.show()
