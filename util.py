def pixmap_to_base64(pixmap):
    import cStringIO as StringIO
    import base64
    from PyQt4.QtCore import QBuffer, QByteArray, QIODevice

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, 'PNG')
    string_io = StringIO.StringIO(byte_array)
    string_io.seek(0)

    return base64.b64encode(string_io.read())


def sanitize_html(value):
    VALID_TAGS = ['b', 'i', 'u', 's', 'ding', 'br']
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True

    return soup.renderContents()