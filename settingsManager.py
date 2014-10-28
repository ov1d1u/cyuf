from singleton import Singleton
from PyQt5.QtCore import *


@Singleton
class Settings:
    keys = {}
    settings = QSettings('Cyuf', 'Cyuf Messenger')

    def __init__(self):
        self._set_defaults()
        self._load_settings()

    def __setattr__(self, name, value):
        self.keys[name] = value
        self.settings.setValue(name, value)

    def __getattr__(self, name, default=None):
        try:
            return object.__getattribute__(self, name, default)
        except:
            if name in self.keys:
                if self.keys[name] in ['true', True]:
                    return True
                elif self.keys[name] in ['false', False]:
                    return False
                return self.keys[name]
            else:
                print('{0} not found, returning default ({1})'.format(name, default))
                return default

    def get(self, name, default=None):
        return self.__getattr__(name, default)

    def _load_settings(self):
        for key in self.settings.allKeys():
            value = self.settings.value(key)
            if value:
                print('self.keys[{0}] = {1}'.format(key, value))
                self.keys[key] = value
            else:
                print('HURR')

    def _set_defaults(self):
        self.keys['winrect'] = QRect(QPoint(0, 0), QSize(308, 607))
        self.keys['username'] = ''
        self.keys['password'] = ''
        self.keys['remember_me'] = False
        self.keys['signin_auto'] = False
        self.keys['signin_invisible'] = False
        self.keys['compact_list'] = False
        self.keys['show_offlines'] = True
        self.keys['group_settings'] = {}
        self.keys['statuses'] = []
        self.keys['buddylist_sort'] = 'name'
