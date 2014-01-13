import os
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import avatar_prechooser
import util
import cyemussa
ym = cyemussa.CyEmussa.Instance()


class AvatarChooser(QObject):
    def __init__(self, app):
        QObject.__init__(app)
        super(AvatarChooser, self).__init__()
        self.app = app
        self.avatars = {}

        self.widget = uic.loadUi('ui/avatar_chooser.ui')
        self.widget.setWindowFlags(self.widget.windowFlags() | Qt.Popup)
        self.widget.label_avatar.setPixmap(QPixmap(self.app.me.avatar.image))
        self.widget.button_delete.setEnabled(False)
        self.widget.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.widget.avatarListWidget.currentItemChanged.connect(
            self._itemChanged
        )
        self.widget.avatarListWidget.itemDoubleClicked.connect(self._submit)
        self.widget.button_browse.clicked.connect(self._browseFiles)
        self.widget.button_delete.clicked.connect(self._deleteAvatar)

        self._listIcons()

    def _listIcons(self):
        paths = [
            '{0}/ui/resources/avatars/'.format(QDir().currentPath()),
            '{0}/avatars/'.format(QDesktopServices.storageLocation(
                QDesktopServices.DataLocation
            ))
        ]

        files = []

        for path in paths:
            if os.path.exists(path):
                path_files = os.listdir(path)
                for f in path_files:
                    full_path = '{0}/{1}'.format(path, f)
                    if not os.path.isdir(full_path):
                        if QImageReader().imageFormat(full_path):
                            files.append(full_path)

        for avatar in files:
            icon = QIcon(util.scalePixmapAspectFill(
                QPixmap(avatar),
                QSize(64, 64))
            )
            item = QListWidgetItem(self.widget.avatarListWidget)
            item.setIcon(icon)
            item.avatarPath = avatar
            self.widget.avatarListWidget.addItem(item)

    def _itemChanged(self, item, prev_item):
        if item:
            self.widget.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.widget.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        pixmap = util.scalePixmapAspectFill(
            QPixmap(item.avatarPath),
            QSize(96, 96)
        )
        self.widget.label_avatar.setPixmap(pixmap)

        fileInfo = QFileInfo(item.avatarPath)
        if QFileInfo(fileInfo.absoluteDir().absolutePath()).isWritable():
            self.widget.button_delete.setEnabled(True)
        else:
            self.widget.button_delete.setEnabled(False)

    def _browseFiles(self):
        self.fileDialog = QFileDialog(self.widget, Qt.Dialog)
        self.fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        self.fileDialog.setFileMode(QFileDialog.ExistingFile)
        self.fileDialog.setNameFilter('Image files (*.png *.xpm *.jpg)')
        self.fileDialog.fileSelected.connect(self._addAvatar)
        self.fileDialog.show()

    def _addAvatar(self, avatar):
        storagePath = QDesktopServices.storageLocation(
            QDesktopServices.DataLocation
        )
        if not os.path.exists('{0}/avatars/'.format(storagePath)):
            QDir().mkpath('{0}/avatars/'.format(storagePath))
        QFile.copy(avatar, '{0}/avatars/{1}'.format(
            storagePath,
            QFileInfo(avatar).fileName())
        )
        pixmap = util.scalePixmapAspectFill(QPixmap(avatar), QSize(64, 64))
        icon = QIcon(pixmap)
        item = QListWidgetItem(self.widget.avatarListWidget)
        item.setIcon(icon)
        item.avatarPath = avatar
        self.widget.avatarListWidget.addItem(item)
        self.fileDialog = None

    def _deleteAvatar(self):
        item = self.widget.avatarListWidget.currentItem()
        QFile.remove(item.avatarPath)
        self.widget.avatarListWidget.takeItem(
            self.widget.avatarListWidget.row(item)
        )

        if self.widget.avatarListWidget.count():
            self.widget.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def _submit(self):
        self.widget.accept()
