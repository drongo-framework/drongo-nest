import argparse
import importlib
import six

from nest import Nest


__all__ = ['main']


def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('app', help='py.module:app_instance')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--auto-reload', action='store_true')
    parser.add_argument('--async', action='store_true')
    return parser.parse_args()


def main():
    options = _parse()
    module, app = options.app.split(':')
    module = importlib.import_module(module)
    app = getattr(module, app)

    kwargs = dict(
        app=app,
        host=options.host,
        port=options.port,
        auto_reload=options.auto_reload
    )
    nest = Nest(**kwargs)
    try:
        nest.run()
    except KeyboardInterrupt:
        print('Exiting...')
        nest.shutdown()
