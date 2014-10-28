import os
from PIL import Image, ImageQt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
try:
    import pygame.camera
    import pygame.image
    pygame_available = True
except ImportError:
    pygame_available = False

WWIDTH = 320
WHEIGHT = 240


class WebcamSource:
    def __init__(self):
        self.sources = []
        self.get_image = None
        self.stop_source = None

        if pygame_available:
            pygame.camera.init()
            for camera in pygame.camera.list_cameras():
                camurl = 'cam://{0}'.format(camera)
                self.sources.append(camurl)

        self.sources.append('image://')
        self.sources.append('video://')
        self.sources.append('ymsg://')

    def start(self, source):
        url = QUrl(source)
        if url.scheme() == 'cam':
            self.start_webcam(url.path())
        elif url.scheme() == 'image':
            self.start_image(url.path())
        elif url.scheme() == 'video':
            self.start_video(url.path())
        elif url.scheme() == 'ymsg':
            self.start_ymsg(url.path())

    def stop(self):
        self.get_image = None
        self.stop_source()

    def start_webcam(self, source):
        webcam = pygame.camera.Camera(source)

        def get_image():
            img = webcam.get_image()
            rgb_data = pygame.image.tostring(img, 'RGB')
            image = Image.fromstring("RGB", webcam.get_size(), rgb_data)
            qimage = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            return pixmap.scaled(WWIDTH, WHEIGHT)

        def stop_source():
            webcam.stop()

        self.get_image = get_image
        self.stop_source = stop_source
        webcam.start()

    def start_image(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        pixmap = QPixmap(path)

        def get_image():
            return pixmap.scaled(WWIDTH, WHEIGHT)

        def stop_source():
            pass

        self.get_image = get_image
        self.stop_source = stop_source

    def start_video(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        self.player = Phonon.VideoPlayer(Phonon.VideoCategory)

        def replay():
            self.player.play()

        def get_image():
            return QPixmap.fromImage(
                self.player.videoWidget().snapshot()).scaled(WWIDTH, WHEIGHT)

        def stop_source():
            self.player.stop()

        self.player.load(Phonon.MediaSource(path))
        self.player.setVolume(0.0)
        self.player.finished.connect(replay)
        self.player.play()
        self.get_image = get_image
        self.stop_source = stop_source
