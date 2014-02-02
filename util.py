from functools import wraps
from time import time


def sanitize_html(value):
    VALID_TAGS = ['b', 'i', 'u', 's', 'ding', 'br', 'font']
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True

    return soup.renderContents().decode()


def yahoo_rich_to_html(text):
    import re
    message = text.replace('[1m', '<b>')
    message = message.replace('[x1m', '</b>')
    message = message.replace('[2m', '<i>')
    message = message.replace('[x2m', '</i>')
    message = message.replace('[4m', '<u>')
    message = message.replace('[x4m', '</u>')
    message = re.sub(r'\[#(.*?)m', r'<font color="#\1">', message)
    return message


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time()
        result = f(*args, **kwds)
        elapsed = time() - start
        print("{0} took {1} time to finish".format(f.__name__, elapsed))
        return result
    return wrapper


def grayscale_pixmap(pixmap):
    from PyQt4.QtGui import qGray, qRgb
    image = pixmap.toImage()
    width = pixmap.width()
    height = pixmap.height()
    for i in range(0, width):
        for j in range(0, height):
            col = image.pixel(i, j)
            gray = qGray(col)
            image.setPixel(i, j, qRgb(gray, gray, gray))
    pixmap = pixmap.fromImage(image)
    return pixmap

def scalePixmapAspectFill(pixmap, size):
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QPixmap
    scaled_pixmap = pixmap.scaled(size,
                                  Qt.KeepAspectRatioByExpanding,
                                  Qt.SmoothTransformation)
    x_offset = 0
    y_offset = 0

    if scaled_pixmap.size().width() > size.width():
        x_offset = scaled_pixmap.size().width() - size.width()
    elif scaled_pixmap.size().height() > size.height():
        y_offset = scaled_pixmap.size().height() - size.height()
    
    image_copy = scaled_pixmap.toImage().copy(x_offset, y_offset, size.width(), size.height())
    return QPixmap.fromImage(image_copy)


def pixmap_to_imgformat(pixmap, format):
    import io
    from PyQt4.QtCore import QBuffer, QByteArray, QIODevice

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, format)
    string_io = io.BytesIO(byte_array)
    string_io.seek(0)
    return string_io.read()

def pixmap_to_base64(pixmap, format='PNG'):
    import base64
    return base64.b64encode(pixmap_to_imgformat(pixmap, format)).decode()

def random_string(length):
    import random, string
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def string_to_md5(string):
    import hashlib
    if type(string) == str:
        string = string.encode()
    return hashlib.md5(string).hexdigest()

def string_to_base64(string):
    import base64
    if type(string) == str:
        string = string.encode()
    return base64.b64encode(string).decode()