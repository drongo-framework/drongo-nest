import ast

import urllib.parse


class UrlEncodedParser(object):
    __slots__ = ['_buffer', 'complete']

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def feed(self, data, env):
        leng = int(env['CONTENT_LENGTH'])
        initial_size = len(self._buffer)
        self._buffer += data
        if len(self._buffer) >= leng:
            env['BODY'] = self._buffer[:leng].strip().decode('utf8')
            env['BODY_REQUEST'] = urllib.parse.parse_qs(env['BODY'])
            self.complete = True
            return leng - initial_size
        else:
            return len(data)


class MultipartParser(object):
    __slots__ = ['_buffer', 'complete']

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def feed(self, data, env):
        pass


class RawParser(object):
    __slots__ = ['_buffer', 'complete']

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def feed(self, data, env):
        leng = int(env['CONTENT_LENGTH'])
        initial_size = len(self._buffer)
        self._buffer += data
        if len(self._buffer) >= leng:
            env['BODY'] = self._buffer[:leng].strip().decode('utf8')
            self.complete = True
            return leng - initial_size
        else:
            return len(data)


class BodyParser(object):
    __slots__ = ['_buffer', 'complete', 'parser']

    RETAIN_KEYS = set(['CONTENT_TYPE', 'CONTENT_LENGTH'])

    def __init__(self):
        self._buffer = b''
        self.complete = False
        self.parser = None

    def feed(self, data, env):
        if self.parser is None:
            if env['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
                self.parser = UrlEncodedParser()
            elif env['CONTENT_TYPE'].startswith('multipart/form-data'):
                self.parser = MultipartParser()
            else:
                self.parser = RawParser()
        res = self.parser.feed(data, env)
        self.complete = self.parser.complete
        return res
