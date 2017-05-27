class TempFile(object):
    def __add__(self, data):
        # TODO: Implement
        return self

    def get(self):
        return self


class ByteBuffer(object):
    def __init__(self):
        self._buffer = []

    def __add__(self, data):
        self._buffer.append(data)
        return self

    def get(self):
        return b''.join(self._buffer).decode('utf8')
