"""Serve only the public prototype assets, never private study keys or raw data."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
PUBLIC = {
    '/web/': 'web/index.html', '/web/index.html': 'web/index.html',
    '/web/styles.css': 'web/styles.css', '/web/app.js': 'web/app.js',
    '/web/data.json': 'web/data.json', '/web/vendor/d3.v7.min.js': 'web/vendor/d3.v7.min.js',
    '/study/': 'study/index.html', '/study/index.html': 'study/index.html',
    '/study/study.css': 'study/study.css', '/study/study.js': 'study/study.js',
    '/study/study_cards.json': 'study/study_cards.json',
}


class PrototypeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, root=ROOT, **kwargs):
        self.root = Path(root).resolve()
        super().__init__(*args, directory=str(self.root), **kwargs)

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/web/')
            self.end_headers()
            return None
        if path not in PUBLIC:
            self.send_error(404, 'Not a public prototype asset')
            return None
        target = (self.root / PUBLIC[path]).resolve()
        if not target.is_relative_to(self.root) or not target.is_file():
            self.send_error(404)
            return None
        self.path = '/' + PUBLIC[path]
        return super().send_head()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def log_message(self, format, *args):
        # The server does not log study answers, query strings, or participant IDs.
        pass


def make_server(host='127.0.0.1', port=8765, root=ROOT):
    return ThreadingHTTPServer((host, port), partial(PrototypeHandler, root=root))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    with make_server(args.host, args.port) as server:
        print(f'BridgeFinder assets served on {args.host}:{server.server_port}; study method keys remain private.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
