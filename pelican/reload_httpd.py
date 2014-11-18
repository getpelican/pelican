from __future__ import print_function
import codecs
import os
import sys
import logging
try:
    import HTMLParser as htmlparser
except ImportError:
    import html.parser as htmlparser  # NOQA

try:
    import SimpleHTTPServer as srvmod
except ImportError:
    import http.server as srvmod  # NOQA

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver  # NOQA

PORT = 8000
RELOAD_PORT = 9000

if len(sys.argv) == 2 or len(sys.argv) == 3:
    port = int(sys.argv[1])
    if port:
        PORT = port
if len(sys.argv) == 3:
    re_p = int(sys.argv[2])
    if re_p:
        RELOAD_PORT = re_p

if PORT == RELOAD_PORT:
    RELOAD_PORT = PORT + 1
    logging.warning("a conflict of ports! fallback: httpd=%d reload=%d",
                    PORT, RELOAD_PORT)


class HeadFinder(htmlparser.HTMLParser):
    def __init__(self):
        htmlparser.HTMLParser.__init__(self)
        self.head_pos = None

    def handle_endtag(self, tag):
        if tag == "head":
            self.head_pos = self.getpos()

LIVERELOAD_INJECTION_CODE = """
<script>
        var PELICAN_LIVE_RELOAD_SOCKET;
        function PELICAN_LIVE_RELOAD_SETUP() {
            PELICAN_LIVE_RELOAD_SOCKET =
                new WebSocket("ws://localhost:""" + str(RELOAD_PORT) + """");
            PELICAN_LIVE_RELOAD_SOCKET.onmessage = function(e) {
                console.log("get message" + e.data);
                if(e.data == "RELOAD") { window.location.reload(true); }
            }
        }
        function PELICAN_LIVE_RELOAD_CLOSE() {
            if(PELICAN_LIVE_RELOAD_SOCKET) {
                if(PELICAN_LIVE_RELOAD_SOCKET.readyState == 1) {
                    PELICAN_LIVE_RELOAD_SOCKET.close();
                }
            }
        }
        if(window.addEventListener) {
            window.addEventListener("load", PELICAN_LIVE_RELOAD_SETUP, false);
            window.addEventListener("beforeunload",PELICAN_LIVE_RELOAD_CLOSE,false);
        }
        else{
            window.attachEvent("onload", PELICAN_LIVE_RELOAD_SETUP);
            window.attachEvent("onbeforeunload",PELICAN_LIVE_RELOAD_CLOSE);
        }
</script>
"""

SUFFIXES = ['', '.html', '/index.html']


class ComplexHTTPRequestHandler(srvmod.SimpleHTTPRequestHandler):
    def write_html(self, f):
        parser = HeadFinder()
        output = ""
        for i, line in enumerate(f):
            if parser.head_pos is None:
                parser.feed(line)
                if parser.head_pos is not None:
                    offset = parser.head_pos[1]
                    output += line[:offset]
                    output += LIVERELOAD_INJECTION_CODE
                    output += line[offset:]
                else:
                    output += line
            else:
                output += line
        return output.encode(encoding="utf-8")

    def do_GET2(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ['index.html', 'index.htm']:
                _path = os.path.join(path, index)
                if os.path.exists(_path):
                    path = _path
                    break
            else:
                self.send_error(404, "File not found")
                return
        # check mime type
        mime = ""
        ext = os.path.splitext(path)[1].lower()
        if ext in self.extensions_map:
            mime = self.extensions_map[ext]
        else:
            self.send_error(404, "MIME error")
            return
        # open file and response
        f = None
        try:
            if mime == 'text/html':
                f = codecs.open(path, 'r', encoding="utf-8")
            else:
                f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        # send data
        self.send_response(200)
        self.send_header("Content-type", mime)
        if mime == 'text/html':
            output = self.write_html(f)
            self.send_header("Content-Length", len(output))
            self.end_headers()
            self.wfile.write(output)
        else:
            self.send_header("Content-Length", str(os.path.getsize(path)))
            self.end_headers()
            src = f.read()
            self.request.sendall(src)
        f.close()

    def do_GET(self):
        # we are trying to detect the file by having a fallback mechanism
        found = False
        for suffix in SUFFIXES:
            if not hasattr(self, 'original_path'):
                self.original_path = self.path
            self.path = self.original_path + suffix
            print(self.path)
            path = self.translate_path(self.path)
            if os.path.exists(path):
                self.do_GET2()
                logging.info("Found: %s" % self.path)
                found = True
                break
            logging.info("Tried to find file %s, but it doesn't exist. ", self.path)
        if not found:
            logging.warning("Unable to find file %s or variations.", self.path)

Handler = ComplexHTTPRequestHandler

socketserver.TCPServer.allow_reuse_address = True
try:
    httpd = socketserver.TCPServer(("", PORT), Handler)
except OSError as e:
    logging.error("Could not listen on port %s", PORT)
    sys.exit(getattr(e, 'exitcode', 1))


logging.info("Serving at port %s", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt as e:
    logging.info("Shutting down server")
    httpd.socket.close()
