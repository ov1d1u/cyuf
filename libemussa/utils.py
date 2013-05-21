from hashlib import md5 
import base64, os


class YDict:
    def __init__(self, d = None):
        self.keyvals = []
        self.iters = {}
        if d:
            self.import_dictionary(d)

    def __setitem__(self, key, value):
        if not key in self.iters:
            self.iters[key] = 0
        self.keyvals.append([key, value])

    def __getitem__(self, key):
        if type(key) == int:
            if key < len(self.keyvals):
                return self.keyvals[key][0]
            else:
                raise IndexError('Index out of bounds')
        elif type(key) == str:
            i = self.get_seek(key)
            for keyval in self._filter_by_key(key)[i:]:
                if keyval[0] == key:
                    self.set_seek(key, i+1)
                    return keyval[1]
            raise KeyError(key)
        else:
            TypeError('Key indices must be str')

    def __delitem__(self, key):
        i = self.get_seek(key)
        for keyval in self._filter_by_key(key)[i:]:
            if keyval[0] == key:
                self.keyvals.remove([keyval[0], keyval[1]])
                self._fix_seek(key)
                return
        raise KeyError(key)

    def __len__(self):
        return len(self.keyvals)

    def __contains__(self, value):
        for keyval in self.keyvals:
            if keyval[1] == value:
                return True
        return False

    def __str__(self):
        text = '{' + os.linesep
        for keyval in self.keyvals:
            text += '  {0} : {1},{2}'.format(keyval[0], keyval[1], os.linesep)
        text += '}'
        return text

    def __repr__(self):
        return str(self)

    def _filter_by_key(self, key):
        l = []
        for keyval in self.keyvals: 
            if keyval[0] == key:
                l.append(keyval)
        return l

    def _count_key(self, key):
        i = 0
        for keyval in self.keyvals:
            if keyval[0] == key:
                i += 1
        return i

    def _fix_seek(self, key):
        if self.get_seek(key) >= self._count_key(key):
            self.set_seek(key, self._count_key(key)-1)

    def import_dictionary(self, d):
        for key in d:
            self[key] = d[key]

    def export_dictionary(self, d):
        d = {}
        for keyval in self.keyvals:
            d[keyval[0]] = keyval[1]
        return d

    def update_keyval(self, key, oldvalue, newvalue):
        for keyval in list(self.keyvals):
            if keyval[0] == key and keyval[1] == oldvalue:
                self.keyvals.remove(keyval)
                self.keyvals.append([key, newvalue])
                return [key, newvalue]
        raise IndexError('No such keyval')

    def remove_keyval(self, key, value):
        i = self.get_seek(key)
        for keyval in self._filter_by_key(key)[i:]:
            if keyval[0] == key and keyval[1] == value:
                self.keyvals.remove(keyval)
                self._fix_seek(key)
                return keyval
        raise IndexError('No such keyval')

    def remove_key(self, key):
        for keyval in list(self.keyvals):
            if keyval[0] == key:
                self.keyvals.remove(keyval)

    def replace_key(self, key, index_of_key, value):
        for keyval in list(self.keyvals[index_of_key:]):
            if keyval[0] == key:
                self.update_keyval(keyval[0], keyval[1], value)
                return
        raise KeyError(key)

    def keys(self):
        keys = []
        for keyval in self.keyvals:
            keys.append(keyval[0])
        return keys

    def values(self):
        values = []
        for keyval in self.keyvals:
            values.append(keyval[1])
        return values

    def items(self):
        items = []
        for keyval in self.keyvals:
            items.append((keyval[0], keyval[1]))
        return items

    def has_key(self, key):
        for keyval in self.keyvals:
            if keyval[0] == key:
                return True
        return False

    def get(self, key):
        for keyval in self.keyvals:
            if keyval[0] == key:
                return keyval[1]
        return None

    def clear(self):
        self.keyvals = []
        self.iters = {}

    def setdefault(self, key):
        self.keyvals.append([key, ''])

    def pop(self, key):
        i = self.get_seek(key)
        for keyval in self._filter_by_key(key)[i:]:
            if keyval[0] == key:
                popped = keyval[1]
                self.keyvals.remove(keyval)
                self._fix_seek(key)
                return popped
        raise KeyError(key)

    def copy(self):
        return list(self.keyvals)

    def set_seek(self, key, position):
        keycount = self._count_key(key)
        if position < keycount:
            self.iters[key] = position

    def get_seek(self, key):
        return self.iters[key]

    def reset(self):
        for key in self.keys():
            self.seek_reset(key)

    def seek_reset(self, key):
        self.set_seek(key, 0)

    def get_range(self, key):
        return (0, self._count_key())


def yahoo_generate_hash(str_data):
    m = md5()
    m.update(str_data)
    hash = m.digest()
    ybase64 = base64.b64encode(hash)
    ybase64 = ybase64.replace('+', '.')
    ybase64 = ybase64.replace('/', '_')
    ybase64 = ybase64.replace('=', '-')

    return ybase64