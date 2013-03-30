# -*- coding: utf-8 -*-
__all__ = ['load_settings_into_global_conf']

class settings(object):
    """
    Just a wrapper to the object interface.
    We're generating a module so we can import from it:

    >>> from pelican.conf import settings
    >>> settings.PATH
    "/Users/jbcurtin/workspace/blog/content"
    >>> from pelican.conf.settings import PATH
    >>> PATH
    "/Users/jbcurtin/workspace/blog/content"

    """
    pass

def load_settings_into_global_conf(new_settings):
    for key, value in new_settings.iteritems():
    # for key,value in read_settings(args.settings, override=get_config(args)).iteritems():
        setattr(settings, key, value)

    return settings