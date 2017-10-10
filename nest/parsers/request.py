import six.moves.urllib.parse as urlparse


__all__ = ['RequestParser']


class RequestParser(object):
    __slots__ = ['_buffer', 'complete']

    VALID_METHODS = set(['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def feed(self, data, env):
        initial_size = len(self._buffer)

        self._buffer += data
        try:
            idx = self._buffer.index(b'\r\n')
        except Exception as _:
            return len(data)

        line = self._buffer[:idx]
        try:
            method, request, version = line.decode('ascii').split()
        except Exception as _:
            raise Exception('Invalid request!')

        assert method in self.VALID_METHODS

        if '?' in request:
            path, qs = request.split('?', 1)
        else:
            path, qs = request, ''

        env['REQUEST_METHOD'] = method.upper()
        env['PATH_INFO'] = path
        env['QUERY_STRING'] = qs
        env['GET'] = urlparse.parse_qs(qs)
        self.complete = True
        return idx + 2 - initial_size
