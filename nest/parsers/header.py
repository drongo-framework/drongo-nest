import ast
import asyncio
import io
import os
import socket
import uuid

import urllib.parse


class HeaderParser(object):
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
            if self._buffer[:2] == b'\r\n':
                self.complete = True
                self._buffer = self._buffer[2:]
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
