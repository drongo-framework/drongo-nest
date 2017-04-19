from .body import BodyParser
from .header import HeaderParser
from .request import RequestParser


class HttpParser(object):
    def __init__(self):
        self.complete = False
        self.rparser = RequestParser()
        self.hparser = HeaderParser()
        self.bparser = BodyParser()

    def feed(self, data, env):
        c = 0
        if not self.rparser.complete:
            r = self.rparser.feed(data, env)
            c += r
            data = data[r:]

        if not self.hparser.complete:
            r = self.hparser.feed(data, env)
            c += r
            data = data[r:]

        if 'REQUEST_METHOD' in env and \
                env['REQUEST_METHOD'] in ['PUT', 'POST']:
            if not self.bparser.complete:
                r = self.bparser.feed(data, env)
                c += r
                data = data[r:]
            self.complete = self.bparser.complete
        else:
            self.complete = self.hparser.complete
        return c
