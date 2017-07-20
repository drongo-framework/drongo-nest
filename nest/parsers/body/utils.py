import tempfile


class TempFile(object):
    def __init__(self, headers=None):
        self._tempfile = tempfile.NamedTemporaryFile(delete=True)
        self._headers = headers

    def __add__(self, data):
        self._tempfile.write(data)
        return self

    def get(self):
        # FIXME: Think about something better
        self._tempfile.flush()
        self._tempfile.seek(0)
        return self

    @property
    def headers(self):
        return self._headers

    @property
    def fd(self):
        return self._tempfile

    @property
    def filename(self):
        return self._headers.get('PART_CONTENT_DISPOSITION_FILENAME')

    @property
    def content_type(self):
        return self._headers.get('PART_CONTENT_TYPE') \
            or 'application/octet-stream'


class ByteBuffer(object):
    def __init__(self):
        self._buffer = []

    def __add__(self, data):
        self._buffer.append(data)
        return self

    def get(self):
        return b''.join(self._buffer).decode('utf8')
