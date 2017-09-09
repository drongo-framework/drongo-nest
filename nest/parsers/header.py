import six


NEW_LINE = b'\r\n'


__all__ = ['HeaderParser']


class HeaderParser(object):
    __slots__ = ['_buffer', 'complete']

    RETAIN_KEYS = set(['CONTENT_TYPE', 'CONTENT_LENGTH'])

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def _make_key(self, key):
        key = key.strip().upper().replace('-', '_')
        if key in self.RETAIN_KEYS:
            return key
        return 'HTTP_' + key

    def feed(self, data, env):
        initial_size = len(self._buffer)
        consumed_size = 0
        self._buffer += data

        while True:
            if self._buffer[:2] == NEW_LINE:
                self.complete = True
                self._buffer = self._buffer[2:]
                consumed_size += 2
                break

            try:
                i = self._buffer.index(NEW_LINE)
                line = self._buffer[:i]
                if six.PY3:
                    line = line.decode('ascii')

                self._buffer = self._buffer[i+2:]
                k, v = line.split(':', 1)
                k = self._make_key(k)
                v = v.strip()
                env[k] = v
                consumed_size += i + 2
            except Exception as _:
                return len(data)

        assert consumed_size > initial_size  # Safety check
        return consumed_size - initial_size
