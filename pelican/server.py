from __future__ import print_function
import sys
try:
    import SimpleHTTPServer as srvmod
except ImportError:
    import http.server as srvmod  # NOQA

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver  # NOQA

PORT = 8000

Handler = srvmod.SimpleHTTPRequestHandler

try:
    httpd = socketserver.TCPServer(("", PORT), Handler)
except OSError as e:
    print("Could not listen on port", PORT)
    sys.exit(getattr(e, 'exitcode', 1))


print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt as e:
    print("shutting down server")
    httpd.socket.close()