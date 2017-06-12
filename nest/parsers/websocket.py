from bitstring import BitArray

import math


class HeaderParser(object):
    LENGTH = 9
    MASK_BIT = 8

    def __init__(self):
        self._buffer = BitArray(b'')
        self.complete = False

    def feed(self, data):
        consumed_data = data[:self.LENGTH - self._buffer.length]
        self._buffer += consumed_data

        if self._buffer.length == self.LENGTH:
            self.complete = True

        return consumed_data.length

    def mask_bit(self):
        return self._buffer[self.MASK_BIT]


class PayloadLengthParser(object):
    MIN_LENGTH = 7

    def __init__(self):
        self._buffer = BitArray(b'')
        self.complete = False

    def feed(self, data):
        inital_size = self._buffer.length
        max_bits = max(self.MIN_LENGTH - self._buffer.length, 0)
        self._buffer += data[:max_bits]
        data = data[max_bits:]

        if self._buffer.length >= self.MIN_LENGTH:
            length = self.MIN_LENGTH
            value = self._buffer[:self.MIN_LENGTH].uint
            if value == 126:
                length += 16
            elif value == 127:
                length += 64

        max_bits = length - self._buffer.length
        self._buffer += data[:max_bits]
        if self._buffer.length == length:
            self.complete = True

        return self._buffer.length - inital_size

    def payload_length(self):
        value = self._buffer[:self.MIN_LENGTH].uint
        if value == 126:
            return self._buffer[self.MIN_LENGTH: self.MIN_LENGTH + 16].uint
        elif value == 127:
            return self._buffer[self.MIN_LENGTH: self.MIN_LENGTH + 64].uint
        return value


class MaskingKeyParser(object):
    LENGTH = 32

    def __init__(self):
        self._buffer = BitArray(b'')
        self.complete = False

    def feed(self, data):
        consumed_data = data[:self.LENGTH - self._buffer.length]
        self._buffer += consumed_data

        if self._buffer.length == self.LENGTH:
            self.complete = True

        return consumed_data.length

    def masking_key(self):
        return self._buffer


class PayloadDataParser(object):

    def __init__(self):
        self._buffer = BitArray(b'')
        self.complete = False

    def feed(self, data, length):
        length = length * 8  # Converting to number of bits
        consumed_data = data[:length - self._buffer.length]
        self._buffer += consumed_data

        if self._buffer.length == length:
            self.complete = True

        return consumed_data.length

    def data(self):
        return self._buffer


class WebsocketParser(object):

    def __init__(self):
        self.complete = False
        self.hparser = HeaderParser()
        self.plparser = PayloadLengthParser()
        self.mkparser = MaskingKeyParser()
        self.pdparser = PayloadDataParser()

    def feed(self, data):
        c = 0
        data = BitArray(data)

        if not self.hparser.complete:
            r = self.hparser.feed(data)
            c += r
            data = data[r:]

        if not self.plparser.complete:
            r = self.plparser.feed(data)
            c += r
            data = data[r:]

        if self.hparser.mask_bit():
            if not self.mkparser.complete:
                r = self.mkparser.feed(data)
                c += r
                data = data[r:]

        if not self.pdparser.complete:
            r = self.pdparser.feed(data, self.plparser.payload_length())
            c += r
            data = data[r:]

        self.complete = self.pdparser.complete

        return c

    def data(self):
        mask_bit = self.hparser.mask_bit()
        data = self.pdparser.data()

        if mask_bit:
            masking_key = self.mkparser.masking_key()
            reps = math.ceil(data.length / masking_key.length)
            masking_key *= reps
            data = data ^ masking_key[:data.length]

        return data.bytes
