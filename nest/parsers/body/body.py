from .multipart import MultipartParser
from .raw import RawParser
from .urlencoded import UrlEncodedParser


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
                boundary = (
                    env['CONTENT_TYPE'].split('boundary=', 1)[1].split(';')[0]
                    .strip().encode('ascii'))
                self.parser = MultipartParser(boundary)
            else:
                self.parser = RawParser()
        res = self.parser.feed(data, env)
        self.complete = self.parser.complete
        return res
