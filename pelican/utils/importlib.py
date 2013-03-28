# Taken from Python 2.7 with permission from/by the original author.
# Taken from django source:
# -*- coding: utf-8 -*-
#  https://github.com/django/django/blob/a84d79f572fbe7512b999c6b3cd7667cbe3138ff/django/utils/importlib.py
import sys

def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in range(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)


def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]

def import_class(name, package=None):
    """
    Imports just the class and not the module. 
    """
    if package is None:
        package = '.'.join(name.split('.')[:-1])
        name = ''.join(name.split('.')[-1:])
        
        if package == '':
            package = None

    module = import_module(package)
    if not hasattr(module, name):
        raise AttributeError("%s is not part of %s" % (name, package))

    return getattr(module, name)
