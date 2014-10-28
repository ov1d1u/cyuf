from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import util
import cyemussa
import avatar_chooser
ym = cyemussa.CyEmussa.Instance()


class AvatarPrechooser(QObject):
    def __init__(self, app):
        QObject.__init__(app)
        super(AvatarPrechooser, self).__init__()
        self.app = app

        self.widget = uic.loadUi('ui/avatar_prechooser.ui')
        self.widget.setWindowFlags(self.widget.windowFlags() | Qt.Popup)
        self.widget.button_selectAvatar.clicked.connect(
            self._openAvatarChooser
        )
        self.widget.label_avatar.setPixmap(QPixmap(self.app.me.avatar.image))

        self.widget.accepted.connect(self._setAvatar)

        self.widget.shareRadioButton.setChecked(True)

    def _openAvatarChooser(self):
        self.avatarchooser = avatar_chooser.AvatarChooser(self.app)
        self.avatarchooser.widget.show()
        self.avatarchooser.widget.accepted.connect(self._avatarChosed)
        self.widget.shareRadioButton.setChecked(True)

    def _avatarChosed(self):
        item = self.avatarchooser.widget.avatarListWidget.currentItem()
        pixmap = util.scalePixmapAspectFill(
            QPixmap(item.avatarPath),
            QSize(96, 96)
        )
        self.widget.label_avatar.setPixmap(pixmap)

    def _setAvatar(self):
        if self.widget.shareRadioButton.isChecked():
            self.app.me.avatar.image = self.widget.label_avatar.pixmap()

            # encode the pixmap to PNG and upload it
            image_data = util.pixmap_to_imgformat(self.widget.label_avatar.pixmap(), 'PNG')
            ym.upload_display_image(image_data)
        else:
            self.app.me.avatar.image = QPixmap("ui/resources/no-avatar.png")
            ym.delete_display_image()
