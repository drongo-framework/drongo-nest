import ast

from .utils import TempFile, ByteBuffer


class PartBoundaryParser(object):
    __slots__ = ['_buffer', 'complete', 'end', '_boundary', '_b1', '_b2']

    def __init__(self, boundary):
        self._boundary = boundary
        self._buffer = b''
        self.complete = False
        self.end = False

        # 2 types of boundaries
        self._b1 = self._boundary + b'\r\n'
        self._b2 = self._boundary + b'--\r\n'  # Unused for now

    def feed(self, data, env):
        initial_size = len(self._buffer)
        self._buffer += data

        if self._buffer.startswith(self._b1):
            self.complete = True
            return len(self._b1) - initial_size

        else:
            # Everything got consumed as buffer hasn't seen the boundary yet!
            return len(data)


class PartHeaderParser(object):
    __slots__ = ['_buffer', 'complete']

    def __init__(self):
        self._buffer = b''
        self.complete = False

    def _make_key(self, key):
        key = key.strip().upper().replace('-', '_')
        return 'PART_' + key

    def feed(self, data, env):
        initial_size = len(self._buffer)
        consumed_size = 0
        self._buffer += data

        while True:
            if self._buffer[:2] == b'\r\n':
                self.complete = True
                self._buffer = self._buffer[2:]
                self.post_process(env)
                consumed_size += 2
                break

            try:
                i = self._buffer.index(b'\r\n')
                line = self._buffer[:i].decode('utf8')
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

    def post_process(self, env):
        nenv = {}
        for key, val in env.items():
            for v in val.split(';'):
                v = v.strip()
                if '=' in v:
                    name, value = v.split('=')
                    nenv[key + '_' + name.upper()] = ast.literal_eval(value)
                else:
                    nenv[key] = v
        env.clear()
        env.update(nenv)


class PartBodyParser(object):
    def __init__(self, boundary):
        self.complete = False
        self._buffer = b''
        self._contents = None
        self._boundary = boundary
        self._b = b'\r\n' + boundary

    def feed(self, data, env):
        if self._contents is None:
            if 'PART_CONTENT_DISPOSITION_FILENAME' in env:
                self._contents = TempFile()
            else:
                self._contents = ByteBuffer()

        initial_size = len(self._buffer)
        self._buffer += data
        try:
            i = self._buffer.index(self._b)
            self._contents += self._buffer[:i]
            self.complete = True
            return i - initial_size + len(self._b)
        except Exception as _:
            if len(self._buffer) > len(self._b):
                si = len(self._buffer)-len(self._b)
                self._contents += self._buffer[:si]
                self._buffer = self._buffer[si:]
            return len(data)

    def get_value(self):
        if self._contents:
            return self._contents.get()


class PartTrailParser(object):
    def __init__(self):
        self._buffer = b''
        self.complete = False
        self.end = False

    def feed(self, data, env):
        initial_size = len(self._buffer)
        self._buffer += data
        if len(self._buffer) >= 4:
            if self._buffer[:4] == b'--\r\n':
                self.complete = True
                self.end = True
                return 4 - initial_size

        if len(self._buffer) >= 2:
            if self._buffer[:2] == b'\r\n':
                self.complete = True
                return 2 - initial_size

        return len(data)


class PartParser(object):
    def __init__(self, boundary):
        self.complete = False
        self.end = False
        self._boundary = boundary

        # Sub-parsers
        self._header_parser = PartHeaderParser()
        self._body_parser = PartBodyParser(boundary)
        self._trail_parser = PartTrailParser()
        self._env = {}

    def feed(self, data, env):
        c = 0
        while data:
            if not self._header_parser.complete:
                i = self._header_parser.feed(data, self._env)
                data = data[i:]
                c += i

            elif not self._body_parser.complete:
                i = self._body_parser.feed(data, self._env)
                data = data[i:]
                c += i

            elif not self._trail_parser.complete:
                i = self._trail_parser.feed(data, self._env)
                data = data[i:]
                c += i
                self.complete = self._trail_parser.complete
                self.end = self._trail_parser.end

            if self.complete:
                name = self._env.get('PART_CONTENT_DISPOSITION_NAME')
                value = self._body_parser.get_value()
                env.setdefault('POST', {}).setdefault(name, []).append(value)
                break
        return c


class MultipartParser(object):
    __slots__ = ['_boundary', '_b1', '_b2', 'complete', '_boundary_parser',
                 '_part_parser']

    def __init__(self, boundary):
        self.complete = False

        self._boundary = b'--' + boundary
        self._boundary_parser = PartBoundaryParser(self._boundary)
        self._part_parser = None

    def feed(self, data, env):
        c = 0

        while data:
            if not self._boundary_parser.complete:
                i = self._boundary_parser.feed(data, None)
                data = data[i:]
                c += i

                # Assuming it will not end here!
                # if self._boundary_parser.end:
                #     self.complete = True
                #     return c

            else:
                if self._part_parser is None:  # Create a new part parser
                    self._part_parser = PartParser(self._boundary)

                i = self._part_parser.feed(data, env)
                if self._part_parser.complete:
                    self.complete = self._part_parser.end
                    self._part_parser = None
                data = data[i:]
                c += i

        return c
