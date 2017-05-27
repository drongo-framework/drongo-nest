from nest.parsers import RequestParser, HeaderParser, BodyParser


def test_benchmark_post_basic(benchmark):
    request = (
        b'POST / HTTP/1.1\r\n'
        b'Content-Type: application/x-www-form-urlencoded\r\n'
        b'content-length: 11\r\n'
        b'hello=world'
    )

    def http_parse_post():
        rparser = RequestParser()
        hparser = HeaderParser()
        bparser = BodyParser()

        req = request

        env = dict()
        req = req[rparser.feed(req, env):]
        req = req[hparser.feed(req, env):]
        req = req[bparser.feed(req, env):]
        assert req == b''

    benchmark(http_parse_post)


def test_benchmark_post_multipart(benchmark):
    request = (
        b'POST / HTTP/1.1\r\n'
        b'content-type: multipart/form-data; '
        b'boundary=--------------------------830469423478890278155034\r\n'
        b'content-length: 434\r\n'
        b'Connection: keep-alive\r\n\r\n'
        b'----------------------------830469423478890278155034\r\n'
        b'Content-Disposition: form-data; name="test"; '
        b'filename="hello.txt"\r\n'
        b'Content-Type: text/plain\r\n\r\n'
        b'Hello world\r\n\r\n'
        b'----------------------------830469423478890278155034\r\n'
        b'Content-Disposition: form-data; name="a"\r\n\r\n'
        b'100\r\n'
        b'----------------------------830469423478890278155034\r\n'
        b'Content-Disposition: form-data; name="b"\r\n\r\n'
        b'hello world\r\n'
        b'----------------------------830469423478890278155034--\r\n'
    )

    def http_parse_post():
        rparser = RequestParser()
        hparser = HeaderParser()
        bparser = BodyParser()

        req = request

        env = dict()
        req = req[rparser.feed(req, env):]
        req = req[hparser.feed(req, env):]
        req = req[bparser.feed(req, env):]
        assert req == b''

    benchmark(http_parse_post)
