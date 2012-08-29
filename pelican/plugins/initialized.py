from pelican import signals

def test(sender):
    print("%s initialized !!" % sender)

def register():
    signals.initialized.connect(test)
