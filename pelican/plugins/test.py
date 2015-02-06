#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# Just say "Hello world!".
# ----------------------------------------
import sitemap


# ----------------------------------------
# test cases
# ----------------------------------------
def run_doctest():
    '''python -B <__file__> -v
    '''
    import doctest
    doctest.testmod()


if '__main__' == __name__:
    print "Hello world!"

