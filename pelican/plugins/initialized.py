# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from pelican import signals

def test(sender):
    print("%s initialized !!" % sender)

def register():
    signals.initialized.connect(test)
