#!/usr/bin/env python3
"""Local static preview with GitHub Pages style extensionless URLs and a 404 page."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import gzip
import io
import mimetypes

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, gzip_enabled=False, **kwargs):
        self.gzip_enabled = gzip_enabled
        super().__init__(*args, **kwargs)

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / 'index.html'
        if self.gzip_enabled and 'gzip' in self.headers.get('Accept-Encoding', '') and path.is_file() and path.suffix in ['.html','.css','.js','.svg','.json','.txt']:
            body = gzip.compress(path.read_bytes(), mtime=0)
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'text/plain')
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            return io.BytesIO(body)
        return super().send_head()

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if not Path(path).suffix and path != '/' and (Path(self.directory) / (path.lstrip('/') + '.html')).is_file():
            self.path = path + '.html'
        super().do_GET()

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            body = (ROOT / '404.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().send_error(code, message, explain)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--directory', type=Path, default=ROOT)
    parser.add_argument('--gzip', action='store_true', help='Compress text assets for a production-like comparison')
    args = parser.parse_args()
    print(f'Preview: http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(args.directory), gzip_enabled=args.gzip)).serve_forever()
