import sys
import re
import six
import base64
import hashlib
import struct
import socket
import time
import threading
import logging
try:
    import SocketServer as socketserver
except:
    import socketserver

last_reload_time = time.time()
cond_last_reload_time = threading.Condition()
force_close = False


def set_reload_time():
    global last_reload_time
    last_reload_time = time.time()


def get_reload_time():
    return last_reload_time


class ReloadWebScoketHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.request.settimeout(5)
        data = self.request.recv(4096)
        if six.PY3:
            data = data.decode("utf-8")
        headers = dict(re.findall(r"(.*): (.*)\r\n", data))
        # if Pelican send reload-request
        if "PELICAN-RELOAD-REQUEST" in headers:
            logging.info("reloading browser pages")
            with cond_last_reload_time:
                set_reload_time()
                cond_last_reload_time.notify_all()
            return

        # is it websocket request?
        if "Upgrade" not in headers or \
           headers["Upgrade"] not in "websocket" or \
           "Sec-WebSocket-Version" not in headers or \
           headers["Sec-WebSocket-Version"] != "13":
            return
        key = ""
        if "Sec-WebSocket-Key" in headers:
            key = headers["Sec-WebSocket-Key"]
        else:
            return
        self.ws_handshake(key)

        reload_time = time.time()
        while(self.heartbeat()):
            with cond_last_reload_time:
                cond_last_reload_time.wait(30)
                if force_close:
                    break
                if reload_time < get_reload_time():
                    self.send_dataframe(0x1, b"RELOAD")
                    break

    def ws_handshake(self, key):
        magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        h = hashlib.sha1()
        if isinstance(key, six.text_type):
            key = key.encode("utf-8")
        h.update(key)
        h.update(magic)
        accept = base64.b64encode(h.digest())
        output = \
            b"HTTP/1.1 101 Switching Protocols\r\n" \
            b"Upgrade: websocket\r\n" \
            b"Connection: Upgrade\r\n" \
            b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n"
        self.request.sendall(output)

    def send_dataframe(self, opecode, payload):
        # payload length <= 125
        b0 = 0x80 + opecode
        b1 = len(payload)
        dataframe = struct.pack("!BB", b0, b1) + payload
        self.request.sendall(dataframe)

    def recv_dataframe(self):
        # if we recv invalid data, return -1, ""
        dataframe = self.request.recv(4096)
        b0, b1 = struct.unpack("!BB", dataframe[0:2])
        opecode = 0x0f & b0
        # payload_len = 0x7f & b1
        # this implement requires [payload <= 125]
        # 0b 1000 **** 1*** ****
        if not (0x80 <= b0 <= 0x8f) or not (0x80 <= b1 <= 0xfd) or \
           not (opecode in [0x1, 0x8, 0xA]):
            return -1, ""
        mask = dataframe[2:6]
        payload = dataframe[6:]
        if six.PY2:
            mask = [ord(x) for x in mask]
            payload = [ord(x) for x in payload]
        # decode payload
        dec_payload = ""
        for i in range(len(payload)):
            dec_payload += chr(payload[i] ^ mask[i % 4])
        return opecode, dec_payload

    def heartbeat(self):
        # checking whether the connection is alive
        try:
            self.send_dataframe(0x9, b"PELICAN-PING")
            opecode, payload = self.recv_dataframe()
            if opecode == 0x8 or opecode == -1:  # close or invalid
                self.send_dataframe(0x8, b"")  # close
                return False
        except socket.timeout:
            return False
        except IOError:
            return False

        return True


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
socketserver.TCPServer.allow_reuse_address = True
ThreadedTCPServer.daemon_threads = True

PORT = len(sys.argv) == 2 and int(sys.argv[1]) or 9000


try:
    server = ThreadedTCPServer(("", PORT), ReloadWebScoketHandler)
except OSError as e:
    logging.error("Could not listen on port %s", PORT)
    sys.exit(getattr(e, 'exitcode', 1))

logging.info("Serving at port %s", PORT)

try:
    server.serve_forever()
except KeyboardInterrupt as e:
    logging.info("Shutting down server")
finally:
    with cond_last_reload_time:
        force_close = True
        cond_last_reload_time.notify_all()
