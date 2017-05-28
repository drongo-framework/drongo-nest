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
            env['BODY'] = self._buffer[:leng].strip()
            self.complete = True
            return leng - initial_size
        else:
            return len(data)
