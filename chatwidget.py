import json
import base64
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4.QtWebKit import QWebSettings, QWebPage

import util
from libemussa.const import *
from libemussa import callbacks as cb
from emotes import emotes
from webcam_viewer import WebcamViewer
import cyemussa, util, datetime, re
from add_buddy import AddBuddyWizard
from file_downloader import FileDownloader, FileUploader

ym = cyemussa.CyEmussa.Instance()


class FileTransferTask:
    def __init__(self):
        self.transfer_info = None
        self.destination = ''
        self.files = []
        self.paths = [] # for remembering where we saved the downloaded files

    def remove_file(self, filename):
        for f in self.files:
            if f.filename == filename:
                self.files.pop(self.files.index(f))
                break


class ChatWidget(QWidget):
    def __init__(self, parent, cybuddy):
        super(ChatWidget, self).__init__()
        self.widget = uic.loadUi('ui/chatwidget.ui')
        self.parent_window = parent
        self.app = parent.app
        self.cybuddy = cybuddy
        self.typingTimer = None
        self.is_ready = False
        self.queue = []
        self.accepted_fts = []  # accepted file transfers
        self.transfer_tasks = {}
        self.webcam_viewer = None

        defaultSettings = QWebSettings.globalSettings()
        defaultSettings.setAttribute(QWebSettings.JavascriptEnabled, True)
        defaultSettings.setAttribute(QWebSettings.PluginsEnabled, True)
        defaultSettings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        ym.register_callback(cb.EMUSSA_CALLBACK_TYPING_NOTIFY, self._typing)
        self.widget.textEdit.keyPressEvent = self._writing_message
        self.widget.sendButton.clicked.connect(self._send_message)
        self.widget.filetransfer_btn.clicked.connect(self._send_file)
        self.widget.myAvatar.setPixmap(self.app.me.avatar.image)

        self.widget.messagesView.setUrl(QUrl('ui/resources/html/chat/index.html'))
        self.widget.messagesView.loadFinished.connect(self._document_ready)
        self.widget.messagesView.linkClicked.connect(self._link_clicked)
        self.widget.messagesView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.cybuddy.update.connect(self._update_buddy)
        self.cybuddy.update_status.connect(self._update_status)
        self.cybuddy.update_avatar.connect(self._update_avatar)
        self.widget.addUserBtn.clicked.connect(self.add_buddy)

        self._update_buddy()
        self._update_status()
        self._update_avatar()
        if cybuddy.yahoo_id in self.app.buddylist.buddy_items:
            self.widget.addUserBtn.setHidden(True)
            self.widget.ignoreUserBtn.setHidden(True)

    def _javascript(self, function, *args):
        # if the document is not ready, wait a while until we start calling JS functions on it
        if not self.is_ready:
            self.queue.append([function, args])
        arguments_list = []
        for arg in args:
            jsarg = str(arg).replace("'", "\\'")
            arguments_list.append("'" + jsarg + "'")
        jscode = function + "(" + ", ".join(arguments_list) + ")"
        self.widget.messagesView.page().mainFrame().evaluateJavaScript(jscode)

    def _document_ready(self):
        self.is_ready = True
        if self.app.me.status.code == YAHOO_STATUS_INVISIBLE:
            pixmap = QPixmap(":status/resources/user-invisible.png")
            self._add_info('You appear offline to <span class="buddyname">{0}</span>'.format(
                self.cybuddy.display_name)
            )
        elif not self.cybuddy.status.online:
            pixmap = QPixmap(":status/resources/user-offline.png")
            self._add_info('<span class="buddyname">{0}</span> seems to be offline and will'
                           'receive your messages next time when he/she logs in.'
                           .format(self.cybuddy.display_name),
                           pixmap)

        for task in self.queue:
            self._javascript(task[0], *task[1])
        self.queue = []
        self._javascript('show_timestamps', 'true')

    def _link_clicked(self, url):
        if url.scheme() == 'cyuf':
            transfer_id = QFileInfo(url.path()).fileName()
            if url.host() == 'save':
                transfer_task = self.transfer_tasks[transfer_id]

                path = None
                if len(transfer_task.files) == 1:
                    path = QFileDialog.getSaveFileName(
                        self.widget,
                        "Save file",
                        "{0}/{1}".format(QDir.homePath(), transfer_task.files[0].filename),
                        "Any file (*.*)"
                    )
                else:
                    path = QFileDialog.getExistingDirectory(
                        self.widget,
                        "Save file",
                        "{0}".format(QDir.homePath()),
                        QFileDialog.ShowDirsOnly
                    )

                if path:
                    print('Save as: {0}'.format(path))
                    transfer_task.destination = path
                    self.accepted_fts.append(transfer_id)
                    ym.accept_transfer(self.cybuddy.yahoo_id, transfer_id)

            if url.host() == 'decline':
                self._javascript('file_decline',
                                 self.cybuddy.yahoo_id,
                                 transfer_id)
                ym.decline_transfer(self.cybuddy.yahoo_id, transfer_id)

            if url.host() == 'cancel-send':
                self._javascript('cancel_send',
                                 self.cybuddy.yahoo_id,
                                 transfer_id)
                ym.cancel_transfer(self.cybuddy.yahoo_id, transfer_id)

            if url.host() == 'open-file' or url.host() == 'open-dir':
                QDesktopServices.openUrl(QUrl(url.path()))


    def _get_link_from_status(self):
        sep = ''
        statusmsg = self.cybuddy.status.message
        if statusmsg:
            sep = ' - '
        if 'http://' in statusmsg:
            href = statusmsg[statusmsg.index('http://'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        elif 'https://' in statusmsg:
            href = statusmsg[statusmsg.index('https://'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        elif 'www.' in statusmsg:
            href = statusmsg[statusmsg.index('www.'):].split(' ', 1)[0]
            statusmsg = statusmsg.replace(href, '').lstrip().rstrip()
            text = '<font color="#8C8C8C">{0}<a href="{1}">{2}</a></font>'.format(sep, href, statusmsg)
            return [href, text]
        else:
            text = '<font color="#8C8C8C">{0}{1}</font>'.format(sep, self.cybuddy.status.message)
            return ['', text]

    def _update_buddy(self):
        self.widget.contactName.setText(self.cybuddy.display_name)
        self._javascript('update_buddy_name', self.cybuddy.display_name)

    def _update_status(self):
        if self.cybuddy.status.online:
            if self.cybuddy.status.idle_time:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-away.png"))
                if self.sender().__class__.__name__ == 'CyBuddy':
                    self._notify_status('is Idle.')
            elif self.cybuddy.status.code == YAHOO_STATUS_BUSY:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-busy.png"))
                if self.sender().__class__.__name__ == 'CyBuddy':
                    self._notify_status('is Busy.')
            else:
                self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-online.png"))
                if self.sender().__class__.__name__ == 'CyBuddy':
                    self._notify_status('is now Available.')
            statusMsg = self._get_link_from_status()
            self.widget.contactStatusText.setText(statusMsg[1])
            self.widget.contactStatusText.setToolTip(statusMsg[0])
        else:
            self.widget.contactStatus.setPixmap(QPixmap(":status/resources/user-offline.png"))
            self.widget.contactStatusText.setText('')
            self.widget.contactStatusText.setToolTip('')
            if self.sender().__class__.__name__ == 'CyBuddy':
                self._notify_status('is now Offline.')

    def _notify_status(self, message):
        self._javascript('status_updated',
                         '<span class="buddy_items">{0}</span> {1}'
                         .format(self.cybuddy.display_name, message),
                         util.pixmap_to_base64(self.widget.contactStatus.pixmap()),
                         datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def _update_avatar(self):
        self.widget.hisAvatar.setPixmap(self.cybuddy.avatar.image)

    def _writing_message(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.widget.sendButton.click()
            ym.send_typing(self.cybuddy.yahoo_id, False)
            self.killTimer(self.typingTimer)
            self.typingTimer = None
        else:
            QTextEdit.keyPressEvent(self.widget.textEdit, e)
            if e.key() > Qt.Key_0 and e.key() < Qt.Key_Z:
                if self.typingTimer:
                    self.killTimer(self.typingTimer)
                else:
                    ym.send_typing(self.cybuddy.yahoo_id, True)
                self.typingTimer = self.startTimer(5000)

    def _typing(self, cyemussa, tn):
        sender = tn.sender
        if not sender:
            # we are typing this from somewhere else
            sender = self.app.me.yahoo_id
        if not sender == self.app.me.yahoo_id and not sender == self.cybuddy.yahoo_id:
            return
        if tn.status:
            self._javascript('start_typing', sender)
        else:
            self._javascript('stop_typing')

    def _add_info(self, text, pixmap=None):
        image = None
        if pixmap:
            image = util.pixmap_to_base64(pixmap)

        # text = util.sanitize_html(text)
        if image:
            self._javascript('add_info', text, image)
        else:
            self._javascript('add_info', text)

    def _send_message(self):
        raw_msg = self.widget.textEdit.toPlainText()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.widget.textEdit.setDocument(QTextDocument())
        ym.send_message(self.cybuddy.yahoo_id, str(raw_msg))
        self._javascript('message_out', self.app.me.yahoo_id, self._text_to_emotes(raw_msg), timestamp)

    def _send_file(self):
        files = QFileDialog.getOpenFileNames(
            self.widget,
            "Select one or more files to send",
            QDir.homePath(),
            "Any file (*.*)"
        )

        ftinfo = cyemussa.CyFileTransferInfo()
        ftinfo.sender = self.app.me.yahoo_id
        ftinfo.receiver = self.cybuddy.yahoo_id
        ftinfo.host = ym.ft_host
        ftinfo.transfer_id = util.string_to_base64(
            util.string_to_md5(util.random_string(25))
        )

        transfer_task = FileTransferTask()
        transfer_task.transfer_info = ftinfo

        files_absolute = []
        sizes = []
        for path in files:
            f = cyemussa.CyFile()
            f.filename = QFile(path).fileName()
            f.filesize = QFile(path).size()
            transfer_task.files.append(f)
            files_absolute.append(QFileInfo(f.filename).fileName())
            sizes.append(f.filesize)

        self.transfer_tasks[transfer_task.transfer_info.transfer_id] = transfer_task
        thumbnail = None

        if len(files) == 1 and QImageReader.imageFormat(files[0]):
            icon = util.scalePixmapAspectFill(QPixmap(files[0]), QSize(32, 32))
            icon_base64 = util.pixmap_to_base64(icon, 'JPG')
            thumbnail = icon_base64
        else:
            icon = QFileIconProvider().icon(QFileInfo(files[0]))
            icon_base64 = util.pixmap_to_base64(icon.pixmap(QSize(32, 32)))

        self._javascript(
            'file_out',
            ftinfo.receiver,
            json.dumps(files_absolute),
            json.dumps(sizes),
            ftinfo.transfer_id,
            icon_base64
        )

        ym.send_files(
            self.cybuddy.yahoo_id,
            transfer_task.transfer_info.transfer_id,
            files,
            thumbnail
        )

    def _text_to_emotes(self, text):
        words = text.split()
        for i, w in enumerate(words):
            for emo in emotes:
                pattern = re.compile(re.escape(emo), re.IGNORECASE)
                word = pattern.sub('<img src="{0}" alt="{1}" />'.format(emotes[emo], emo), w)
                if not word == w:           # a replacement was made, skip to the next word
                    words[i] = word
                    break
        text = ' '.join(words)
        return text

    def _download_progress(self, transfer_id, filename, progress):
        self._javascript(
            'file_progress',
            transfer_id,
            QFileInfo(filename).fileName(),
            progress
        )

    def _download_finished(self, transfer_id):
        transfer_task = self.transfer_tasks[transfer_id]
        if len(transfer_task.files):
            ym.accept_transfer_next_file(self.cybuddy.yahoo_id, transfer_id)
            self._download_progress(transfer_id, transfer_task.files[0], 0.0)
        else:
            del self.transfer_tasks[transfer_id]

        if QFileInfo(transfer_task.destination).isDir():
            action = 'open-dir'
        else:
            action = 'open-file'

        self._javascript(
            'transfer_finished',
            transfer_id,
            transfer_task.transfer_info.sender,
            len(transfer_task.paths),
            action,
            transfer_task.destination
        )

    def timerEvent(self, event):
        ym.send_typing(self.cybuddy.yahoo_id, False)
        if self.typingTimer:
            self.killTimer(self.typingTimer)
            self.typingTimer = None

    def close(self):
        # called by parent when the chat is closing
        ym.unregister_callback(cb.EMUSSA_CALLBACK_TYPING_NOTIFY, self._typing)
        self.cybuddy.update.disconnect(self._update_buddy)
        if self.typingTimer:
            ym.send_typing(self.cybuddy.yahoo_id, False)

    def add_buddy(self):
        self.add_buddy_wizard = AddBuddyWizard(self.app, self.cybuddy.yahoo_id)

    def receive_message(self, cymessage):
        message = util.yahoo_rich_to_html(cymessage.message)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not cymessage.sender:
            sender = self.app.me.yahoo_id
        else:
            sender = self.cybuddy.display_name
        if cymessage.offline:
            message = '(offline) {0}'.format(message)
        if cymessage.timestamp:
            timestamp = datetime.datetime.fromtimestamp(int(cymessage.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        self._javascript('message_in', sender, self._text_to_emotes(util.sanitize_html(message)), timestamp)

    def receive_file_transfer(self, cyfiletransfer):
        files = []
        sizes = []

        ftinfo = cyemussa.CyFileTransferInfo()
        ftinfo.transfer_id = cyfiletransfer.transfer_id
        ftinfo.sender = cyfiletransfer.sender

        transfer_task = FileTransferTask()
        transfer_task.transfer_info = ftinfo

        for f in cyfiletransfer.files:
            transfer_task.files.append(cyemussa.CyFile(f))
            files.append(f.filename)
            sizes.append(f.filesize)

        self.transfer_tasks[cyfiletransfer.transfer_id] = transfer_task

        if not cyfiletransfer.thumbnail:
            icon = QFileIconProvider().icon(QFileInfo(files[0]))
            icon_base64 = util.pixmap_to_base64(icon.pixmap(QSize(32, 32)))
        else:
            icon_base64 = cyfiletransfer.thumbnail

        self._javascript(
            'file_in',
            cyfiletransfer.sender,
            json.dumps(files),
            json.dumps(sizes),
            cyfiletransfer.transfer_id,
            icon_base64
        )

    def receive_file_info(self, cyftinfo):
        if cyftinfo.transfer_id in self.accepted_fts:
            ym.accept_file(
                cyftinfo.sender, cyftinfo.receiver, cyftinfo.filename,
                cyftinfo.transfer_id, cyftinfo.transfer_type, cyftinfo.host,
                cyftinfo.relay_id
            )

            transfer_task = self.transfer_tasks[cyftinfo.transfer_id]
            finfo = QFileInfo(transfer_task.destination)
            if finfo.isDir():
                path = '{0}/{1}'.format(transfer_task.destination, cyftinfo.filename)
            else:
                path = '{0}'.format(transfer_task.destination)

            # remove the current file from left files list and download it
            transfer_task.remove_file(cyftinfo.filename)
            transfer_task.paths.append(path)

            self._download_progress(cyftinfo.transfer_id, cyftinfo.filename, 0.0)

            self.downloader = FileDownloader(transfer_task, path)
            self.downloader.progress.connect(self._download_progress)
            self.downloader.finished.connect(self._download_finished)
            self.downloader.download(cyftinfo.get_download_url())

    def transfer_cancelled(self, cyfiletransfer):
        self._javascript(
            'file_cancel',
            cyfiletransfer.sender,
            cyfiletransfer.transfer_id
        )

    def transfer_accepted(self, cyfiletransfer):
        transfer_task = self.transfer_tasks[cyfiletransfer.transfer_id]
        ym.send_file_info(
            self.cybuddy.yahoo_id,
            cyfiletransfer.transfer_id,
            QFileInfo(transfer_task.files[0].filename).fileName()
        )

    def transfer_rejected(self, cyfiletransfer):
        self._javascript(
            'file_rejected',
            cyfiletransfer.sender,
            cyfiletransfer.transfer_id
        )

    def transfer_upload(self, cyftinfo):
        transfer_task = self.transfer_tasks[cyftinfo.transfer_id]
        if not cyftinfo.relay_id:
            # this is an already started multi-file transfer
            # which now requires us to upload the next file
            transfer_task.files.pop(0)
            if len(transfer_task.files):
                filepath = transfer_task.files[0].filename

                self.uploader = FileUploader(transfer_task)
                self.uploader.progress.connect(self._download_progress)
                self.uploader.finished.connect(self._download_finished)
                ym.send_file_info(
                    self.cybuddy.yahoo_id,
                    cyftinfo.transfer_id,
                    QFileInfo(filepath).fileName()
                )

                # self.uploader.upload(
                #     transfer_task.transfer_info.get_download_url(),
                #     filepath
                # )
            return

        filepath = transfer_task.files[0].filename
        transfer_task.transfer_info.relay_id = cyftinfo.relay_id
        self.uploader = FileUploader(transfer_task)
        self.uploader.progress.connect(self._download_progress)
        self.uploader.finished.connect(self._download_finished)
        self.uploader.upload(
            transfer_task.transfer_info.get_download_url(),
            filepath
        )

    def view_webcam(self):
        ym.send_webcam_request(self.cybuddy.yahoo_id)
        self.webcam_viewer = WebcamViewer(self)

    def receive_audible(self, audible):
        self.audible = audible
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.post_audible)
        self.req = QNetworkRequest(QUrl(self.audible.url))
        self.req.setRawHeader('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US)')
        self.reply = self.manager.get(self.req)

    def post_audible(self, swfdata):
        tmpfile = QTemporaryFile('XXXXXX.swf', self.widget)
        if tmpfile.open():
            tmpfile.write(swfdata.readAll())
            tmpfile.close()
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._javascript('audible_in', self.audible.sender, tmpfile.fileName(), self.audible.message, timestamp)
