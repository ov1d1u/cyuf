from collections import OrderedDict
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialogButtonBox
import cyemussa
import settingsManager

settings = settingsManager.Settings.Instance()
ym = cyemussa.CyEmussa.Instance()


class FakeSettings(dict):
    """
    Fake settingsManager which allows read-only access to settings
    until the save() method is called
    """
    def __init__(self, *arg, **kw):
        super(FakeSettings, self).__init__(*arg, **kw)

    def __getattr__(self, value):
        return settings.get(value)

    def get(self, value, default=None):
        return settings.get(value, default)

    def save(self):
        for key in self.keys():
            setattr(settings, key, self[key])


class Preferences(QObject):
    def __init__(self, parent):
        super(Preferences, self).__init__(parent)
        self.parent = parent
        self.settings = FakeSettings()
        self.currentCategory = None
        # "Title": "pymodyule"
        self.categories = OrderedDict([
            ("General", ""),
            ("Alerts & Sounds", ""),
            ("Appearance", ""),
            ("Archive", ""),
            ("Chat", ""),
            ("Connection", ""),
            ("Ignore List", ""),
            ("Language", ""),
            ("Messages", ""),
            ("Privacy", ""),
            ("Video & Voice", ""),
            ("Webcam Broadcast", "preferences_webcam"),
            ("Yahoo! Music", ""),
            ("Yahoo! Updates", "")
        ])

        self.widget = uic.loadUi('ui/preferences.ui')
        self.widget.optionsListWidget.itemClicked.connect(self.select_category)
        self.widget.buttonBox.clicked.connect(self.buttonBoxClicked)
        self.widget.show()

    def populateCategories(self):
        self.widget.optionsListWidget.clear()
        if ym.is_connected:
            for title in self.categories:
                self.widget.optionsListWidget.addItem(title)
        else:
            self.widget.optionsListWidget.addItem("Connection")

    def select_category(self, item):
        if self.currentCategory:
            self.currentCategory.save()
        self.widget.sectionTitleLabel.setText(item.text())
        for i in range(self.widget.childContainer.count()):
            self.widget.childContainer.itemAt(i).widget().close()

        module = __import__(self.categories[item.text()])
        self.currentCategory = module.Preference(self.widget, self.settings)
        self.widget.childContainer.addWidget(self.currentCategory.widget)

    def buttonBoxClicked(self, button):
        role = self.widget.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.AcceptRole:
            self.currentCategory.save()
            self.settings.save()
            self.widget.close()
        elif role == QDialogButtonBox.ApplyRole:
            self.currentCategory.save()
            self.settings.save()
        elif role == QDialogButtonBox.RejectRole:
            self.widget.close()
