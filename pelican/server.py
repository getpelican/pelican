from __future__ import print_function
import os
import sys
import logging

from six.moves import SimpleHTTPServer as srvmod
from six.moves import socketserver

try:
    from magic import from_file as magic_from_file
except ImportError:
    magic_from_file = None


class ComplexHTTPRequestHandler(srvmod.SimpleHTTPRequestHandler):
    SUFFIXES = ['', '.html', '/index.html']

    def do_GET(self):
        # Try to detect file by applying various suffixes
        for suffix in self.SUFFIXES:
            if not hasattr(self, 'original_path'):
                self.original_path = self.path

            self.path = self.original_path + suffix
            path = self.translate_path(self.path)

            if os.path.exists(path):
                srvmod.SimpleHTTPRequestHandler.do_GET(self)
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


if __name__ == '__main__':
    PORT = len(sys.argv) in (2, 3) and int(sys.argv[1]) or 8000
    SERVER = len(sys.argv) == 3 and sys.argv[2] or ""

    socketserver.TCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.TCPServer((SERVER, PORT), ComplexHTTPRequestHandler)
    except OSError as e:
        logging.error("Could not listen on port %s, server %s.", PORT, SERVER)
        sys.exit(getattr(e, 'exitcode', 1))


    logging.info("Serving at port %s, server %s.", PORT, SERVER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server.")
        httpd.socket.close()
