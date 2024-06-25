import argparse
import logging
import os
import posixpath
import ssl
import sys
import urllib
from http import server

try:
    from magic import from_file as magic_from_file
except ImportError:
    magic_from_file = None

from pelican.log import console  # noqa: F401
from pelican.log import init as init_logging

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Pelican Development Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "port", default=8000, type=int, nargs="?", help="Port to Listen On"
    )
    parser.add_argument("server", default="", nargs="?", help="Interface to Listen On")
    parser.add_argument("--ssl", action="store_true", help="Activate SSL listener")
    parser.add_argument(
        "--cert",
        default="./cert.pem",
        nargs="?",
        help="Path to certificate file. Relative to current directory",
    )
    parser.add_argument(
        "--key",
        default="./key.pem",
        nargs="?",
        help="Path to certificate key file. Relative to current directory",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to pelican source directory to serve. Relative to current directory",
    )
    return parser.parse_args()


class ComplexHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    SUFFIXES = [".html", "/index.html", "/", ""]

    extensions_map = {
        **server.SimpleHTTPRequestHandler.extensions_map,
        # web fonts
        ".oft": "font/oft",
        ".sfnt": "font/sfnt",
        ".ttf": "font/ttf",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
    }

    def translate_path(self, path):
        # abandon query parameters
        path = path.split("?", 1)[0]
        path = path.split("#", 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith("/")
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split("/")
        words = filter(None, words)
        path = self.base_path
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += "/"
        return path

    def do_GET(self):
        # cut off a query string
        original_path = self.path.split("?", 1)[0]
        # try to find file
        self.path = self.get_path_that_exists(original_path)

        if not self.path:
            return

        server.SimpleHTTPRequestHandler.do_GET(self)

    def get_path_that_exists(self, original_path):
        # Try to strip trailing slash
        trailing_slash = original_path.endswith("/")
        original_path = original_path.rstrip("/")
        # Try to detect file by applying various suffixes
        tries = []
        for suffix in self.SUFFIXES:
            if not trailing_slash and suffix == "/":
                # if original request does not have trailing slash, skip the '/' suffix
                # so that base class can redirect if needed
                continue
            path = original_path + suffix
            if os.path.exists(self.translate_path(path)):
                return path
            tries.append(path)
        logger.warning(
            "Unable to find `%s` or variations:\n%s", original_path, "\n".join(tries)
        )
        return None

    def guess_type(self, path):
        """Guess at the mime type for the specified file."""
        mimetype = server.SimpleHTTPRequestHandler.guess_type(self, path)

        # If the default guess is too generic, try the python-magic library
        if mimetype == "application/octet-stream" and magic_from_file:
            mimetype = magic_from_file(path, mime=True)

        return mimetype

    def log_message(self, format, *args):
        logger.info(format, *args)


class RootedHTTPServer(server.HTTPServer):
    def __init__(self, base_path, *args, **kwargs):
        server.HTTPServer.__init__(self, *args, **kwargs)
        self.RequestHandlerClass.base_path = base_path


if __name__ == "__main__":
    init_logging(level=logging.INFO)
    logger.warning(
        "'python -m pelican.server' is deprecated.\nThe "
        "Pelican development server should be run via "
        "'pelican --listen' or 'pelican -l'.\nThis can be combined "
        "with regeneration as 'pelican -lr'.\nRerun 'pelican-"
        "quickstart' to get new Makefile and tasks.py files."
    )
    args = parse_arguments()
    RootedHTTPServer.allow_reuse_address = True
    try:
        httpd = RootedHTTPServer(
            args.path, (args.server, args.port), ComplexHTTPRequestHandler
        )
        if args.ssl:
            httpd.socket = ssl.wrap_socket(
                httpd.socket, keyfile=args.key, certfile=args.cert, server_side=True
            )
    except ssl.SSLError as e:
        logger.error(
            "Couldn't open certificate file %s or key file %s", args.cert, args.key
        )
        logger.error("Could not listen on port %s, server %s.", args.port, args.server)
        sys.exit(getattr(e, "exitcode", 1))

    logger.info("Serving at port %s, server %s.", args.port, args.server)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
        httpd.socket.close()
