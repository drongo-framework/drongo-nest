from .multipart import MultipartParser
from .raw import RawParser
from .urlencoded import UrlEncodedParser


__all__ = ['BodyParser']


class BodyParser(object):
    __slots__ = ['_buffer', '_parser', 'complete']

    RETAIN_KEYS = set(['CONTENT_TYPE', 'CONTENT_LENGTH'])

    def __init__(self):
        self._buffer = b''
        self.complete = False
        self._parser = None

    def feed(self, data, env):
        if self._parser is None:
            if env['CONTENT_TYPE'].startswith(
                    'application/x-www-form-urlencoded'):
                self._parser = UrlEncodedParser()
            elif env['CONTENT_TYPE'].startswith('multipart/form-data'):
                self._parser = MultipartParser()
            else:
                self._parser = RawParser()

        res = self._parser.feed(data, env)
        self.complete = self._parser.complete
        return res
