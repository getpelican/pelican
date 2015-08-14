from __future__ import print_function
import os
import os.path
import posixpath
import sys
import logging


import threading
from six.moves.urllib import parse as url_parse

from six.moves import SimpleHTTPServer as srvmod
from six.moves import socketserver

try:
    from magic import from_file as magic_from_file
except ImportError:
    magic_from_file = None


class ComplexHTTPRequestHandler(srvmod.SimpleHTTPRequestHandler):
    SUFFIXES = ['', '.html', '/index.html']
    SERVPATH = ''

    def translate_path(self, path):
        """Add the ability to serve a file from a given directory (not cwd)
        """
        path = super(ComplexHTTPRequestHandler, self).translate_path(path)
        return os.path.join(self.SERVPATH, os.path.relpath(path, os.getcwd()))

    def do_GET(self):
        self.original_path = self.path
        # Try to detect file by applying various suffixes
        for suffix in self.SUFFIXES:
            self.path = self.original_path + suffix
            path = self.translate_path(self.path)

            if os.path.exists(path):
                super(ComplexHTTPRequestHandler, self).do_GET()
                logging.info("Found `%s`." % self.path)
                break

            logging.info("Tried to find `%s`, but it doesn't exist.",
                         self.path)
        else:
            # Fallback if there were no matches
            logging.warning("Unable to find `%s` or variations.",
                            self.original_path)

    def guess_type(self, path):
        """Guess at the mime type for the specified file.
        """
        mimetype = srvmod.SimpleHTTPRequestHandler.guess_type(self, path)

        # If the default guess is too generic, try the python-magic library
        if mimetype == 'application/octet-stream' and magic_from_file:
            mimetype = magic_from_file(path, mime=True)

        return mimetype


def serve(path, server, port):
    ComplexHTTPRequestHandler.SERVPATH = path
    try:
        httpd = socketserver.TCPServer((server, port), ComplexHTTPRequestHandler)
        httpd.allow_reuse_address = True
    except OSError as e:
        logging.error("Could not listen on port %s, server %s.", port, server)
        sys.exit(getattr(e, 'exitcode', 1))

    logging.info("Serving %s at port %s, server %s.", path, port, server)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server.")
        httpd.socket.close()
        raise


class ServeThread(threading.Thread):
    def __init__(self, path, server, port):
        super(ServeThread, self).__init__()
        self.path = path
        self.server = server
        self.port = port

    def run(self):
        serve(self.path, self.server, self.port)


if __name__ == '__main__':
    PORT = len(sys.argv) in (2, 3) and int(sys.argv[1]) or 8000
    SERVER = len(sys.argv) == 3 and sys.argv[2] or ""
    serve('', SERVER, PORT)
