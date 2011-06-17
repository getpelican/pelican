from blinker import signal


def test(sender):
    print "%s initialized !!" % sender

signal('pelican_initialized').connect(test)
