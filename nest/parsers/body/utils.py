import tempfile


class TempFile(object):
    def __init__(self):
        self._tempfile = tempfile.NamedTemporaryFile(delete=True)

    def __add__(self, data):
        self._tempfile.write(data)
        return self

    def get(self):
        # FIXME: Think about something better
        self._tempfile.flush()
        self._tempfile.seek(0)
        return self._tempfile


class ByteBuffer(object):
    def __init__(self):
        self._buffer = []

    def __add__(self, data):
        self._buffer.append(data)
        return self

    def get(self):
        return b''.join(self._buffer).decode('utf8')
