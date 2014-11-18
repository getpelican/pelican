import os
import sys
import time
import subprocess
import shlex
import signal
import six

PY = "python"
if six.PY3:
    PY += "3"
PELICAN = "pelican"
PELICANOPTS = ""

BASEDIR = os.getcwd()
INPUTDIR = BASEDIR + "/content"
OUTPUTDIR = BASEDIR + "/output"
CONFFILE = BASEDIR + "/pelicanconf.py"

HTTPD_PORT = 8000
RELOAD_PORT = 9000

PIDS_FILE = BASEDIR + "/devser.pids"


def alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def print_usage():
    # copy from develop_server.sh
    message = """usage: $0 (stop) (start) (restart) [httpd_port] [reload_port]
    This starts Pelican in debug and reload mode and then launches
    an HTTP server to help site development. It doesn't read
    your Pelican settings, so if you edit any paths in your Makefile
    you will need to edit your settings as well.
    """
    print(message)


def start_up():
    pelican_com = "{0} --debug --autoreload --browser-reload {1} " \
                  "-r {2} -o {3} -s {4} {5}" \
                  .format(PELICAN, RELOAD_PORT,
                          INPUTDIR, OUTPUTDIR, CONFFILE, PELICANOPTS)
    pelican_com = shlex.split(pelican_com)
    p = subprocess.Popen(pelican_com)
    peli_pid = p.pid

    os.chdir(OUTPUTDIR)

    httpd_com = "{0} -m pelican.reload_httpd {1} {2}" \
                .format(PY, HTTPD_PORT, RELOAD_PORT)
    httpd_com = shlex.split(httpd_com)
    p = subprocess.Popen(httpd_com)
    http_pid = p.pid

    reload_com = "{0} -m pelican.reload_server {1}".format(PY, RELOAD_PORT)
    reload_com = shlex.split(reload_com)
    p = subprocess.Popen(reload_com)
    relo_pid = p.pid

    os.chdir(BASEDIR)

    with open(PIDS_FILE, "w") as f:
        f.write("{0},{1},{2}".format(peli_pid, http_pid, relo_pid))
    # save pids

    time.sleep(1)
    if not alive(peli_pid):
        print("Pelican didn't start. Is the Pelican package installed?")
        return
    if not alive(http_pid):
        print("The HTTP server didn't start. "
              "Is there another service using port {0} ?".format(HTTPD_PORT))
        return
    if not alive(relo_pid):
        print("The reload server didn't start. "
              "Is there another service using port {0} ?".format(RELOAD_PORT))
        return

    print('Pelican and HTTP server processes now running in background.')


def shut_down():
    pids = None
    f = None
    try:
        f = open(PIDS_FILE)
        pids = dict(zip(["peli", "http", "relo"],
                    map(int, f.read().strip().split(","))))
    except IOError:
        print("shutdown servers failed ({0})".format(PIDS_FILE))
    finally:
        if f:
            f.close()
    if pids:
        print("shutdown servers ->", pids)
        pid = pids["peli"]
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
        else:
            print("pelican already died")

        pid = pids["http"]
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
        else:
            print("httpd server already died")

        pid = pids["relo"]
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
        else:
            print("reload server already died")


if len(sys.argv) >= 3:
    HTTPD_PORT = int(sys.argv[2])
if len(sys.argv) >= 4:
    RELOAD_PORT = int(sys.argv[3])
if HTTPD_PORT == RELOAD_PORT:
    RELOAD_PORT += 1
    print("conflicting ports, "
          "fallback http={0} reload={1}".format(HTTPD_PORT, RELOAD_PORT))

if len(sys.argv) >= 2:
    command = sys.argv[1]
    if command == "start":
        start_up()
    elif command == "restart":
        shut_down()
        start_up()
    elif command == "stop":
        shut_down()
    else:
        print_usage()
else:
    print_usage()
