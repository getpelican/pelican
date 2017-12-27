# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
import logging
import os
import ssl
import sys

try:
    from magic import from_file as magic_from_file
except ImportError:
    magic_from_file = None

from six.moves import SimpleHTTPServer as srvmod
from six.moves import socketserver


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Pelican Development Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("port", default=8000, type=int, nargs="?",
                        help="Port to Listen On")
    parser.add_argument("server", default="", nargs="?",
                        help="Interface to Listen On")
    parser.add_argument('--ssl', action="store_true",
                        help='Activate SSL listener')
    parser.add_argument('--cert', default="./cert.pem", nargs="?",
                        help='Path to certificate file. ' +
                        'Relative to current directory')
    parser.add_argument('--key', default="./key.pem", nargs="?",
                        help='Path to certificate key file. ' +
                        'Relative to current directory')
    return parser.parse_args()


class ComplexHTTPRequestHandler(srvmod.SimpleHTTPRequestHandler):
    SUFFIXES = ['', '.html', '/index.html']

    def do_GET(self):
        # cut off a query string
        if '?' in self.path:
            self.path, _ = self.path.split('?', 1)

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
    args = parse_arguments()
    socketserver.TCPServer.allow_reuse_address = True
    try:
        httpd = socketserver.TCPServer(
            (args.server, args.port),
            ComplexHTTPRequestHandler)
        if args.ssl:
            httpd.socket = ssl.wrap_socket(
                httpd.socket, keyfile=args.key,
                certfile=args.cert, server_side=True)
    except ssl.SSLError as e:
        logging.error("Couldn't open certificate file %s or key file %s",
                      args.cert, args.key)
    except OSError as e:
        logging.error("Could not listen on port %s, server %s.",
                      args.port, args.server)
        sys.exit(getattr(e, 'exitcode', 1))

    logging.info("Serving at port %s, server %s.",
                 args.port, args.server)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server.")
        httpd.socket.close()
