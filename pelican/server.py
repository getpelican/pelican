from __future__ import print_function
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

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
