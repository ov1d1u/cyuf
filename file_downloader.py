import requests
import threading, time
from socket import socket
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *

import cyemussa
ym = cyemussa.CyEmussa.Instance()


class FileUploader(QObject):
    progress = pyqtSignal(str, str, int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str, str)

    def __init__(self, transfer_task):
        QObject.__init__(self)
        self.transfer_task = transfer_task

    def upload(self, url, filepath):
        self.filename = QFileInfo(filepath).fileName()
        threading.Thread(target=self.do_upload, args=(url, filepath)).start()

    def do_upload(self, url, filepath):
        fh = QFile(filepath)
        self.fsize = fh.size()
        if not fh.open(QIODevice.ReadOnly) :
            self.error.emit(
                self.transfer_task.transfer_id,
                "Error opening file {0} for reading".format(fh.fileName())
            )
            return

        headers = {
            'Accept': '*/*',
            'Cookie': 'Y={0}; T={1}'.format(ym.y_cookie, ym.t_cookie),
            'User-agent': 'net_http_transaction_impl_manager/0.1',
            'Content-Length': str(self.fsize),
            'Connection': 'Keep-Alive'
        }
        fh.close()

        self.bytes_count = 0
        f = open(filepath, 'rb')
        requests.post(url, data=self.file_data(f), headers=headers, stream=True)

    def file_data(self, fh):
        data = fh.read(1024)
        while data:
            self.bytes_count += len(data)
            self.progress.emit(
                self.transfer_task.transfer_info.transfer_id, self.filename,
                int(self.bytes_count / self.fsize * 100)
            )
            yield data
            data = fh.read(1024)


class FileDownloader(QObject):
    progress = pyqtSignal(str, str, int)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str, str)

    def __init__(self, transfer_task, filename):
        QObject.__init__(self)
        self.transfer_task = transfer_task
        self.filename = filename
    
    def download(self, url):
        threading.Thread(target=self.do_download, args=(url, )).start()

    def do_download(self, url):
        headers = {
            'Accept': '*/*',
            'Cookie': 'Y={0}; T={1}'.format(ym.y_cookie, ym.t_cookie),
            'User-agent': 'net_http_transaction_impl_manager/0.1',
            'Content-Length' : '0',
            'Connection': 'Keep-Alive'
        }

        response = requests.get(url, headers=headers, stream=True)
        clength = int(response.headers['content-length'])

        fh = QFile(self.filename)

        if not fh.open(QIODevice.Append):
            self.error.emit(
                self.transfer_task.transfer_info.transfer_id,
                "Error opening file {0} for writing".format(fh.fileName())
            )
            return
        if response.status_code != 200:
            self.error.emit(
                self.transfer_task.transfer_info.transfer_id,
                "Error while transferring file. Transfer stopped."
            )
            return

        bytes_count = 0
        for byte in response.iter_content(1024):
            if byte:
                fh.write(byte)
                bytes_count += len(byte)
                self.progress.emit(
                    self.transfer_task.transfer_info.transfer_id, self.filename,
                    int(bytes_count / clength * 100)
                )
            else:
                break;

        fh.close()

        self.finished.emit(self.transfer_task.transfer_info.transfer_id)