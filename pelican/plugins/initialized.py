from blinker import signal


def test(sender):
    print "%s initialized !!" % sender

def register():
    signal('pelican_initialized').connect(test)
