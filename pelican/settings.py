# -*- coding: utf-8 -*-
import os
import locale

from pelican import log

DEFAULT_THEME = os.sep.join([os.path.dirname(os.path.abspath(__file__)),
                              "themes/notmyidea"])
_DEFAULT_CONFIG = {'PATH': None,
                   'THEME': DEFAULT_THEME,
                   'OUTPUT_PATH': 'output/',
                   'MARKUP': ('rst', 'md'),
                   'STATIC_PATHS': ['images',],
                   'THEME_STATIC_PATHS': ['static',],
                   'FEED': 'feeds/all.atom.xml',
                   'CATEGORY_FEED': 'feeds/%s.atom.xml',
                   'TRANSLATION_FEED': 'feeds/all-%s.atom.xml',
                   'FEED_MAX_ITEMS': '',
                   'SITENAME': 'A Pelican Blog',
                   'DISPLAY_PAGES_ON_MENU': True,
                   'PDF_GENERATOR': False,
                   'DEFAULT_CATEGORY': 'misc',
                   'FALLBACK_ON_FS_DATE': True,
                   'CSS_FILE': 'main.css',
                   'REVERSE_ARCHIVE_ORDER': False,
                   'REVERSE_CATEGORY_ORDER': False,
                   'DELETE_OUTPUT_DIRECTORY': False,
                   'CLEAN_URLS': False, # use /blah/ instead /blah.html in urls
                   'RELATIVE_URLS': True,
                   'DEFAULT_LANG': 'en',
                   'TAG_CLOUD_STEPS': 4,
                   'TAG_CLOUD_MAX_ITEMS': 100,
                   'DIRECT_TEMPLATES': ('index', 'tags', 'categories', 'archives'),
                   'PAGINATED_DIRECT_TEMPLATES': ('index', ),
                   'PELICAN_CLASS': 'pelican.Pelican',
                   'DEFAULT_DATE_FORMAT': '%a %d %B %Y',
                   'DATE_FORMATS': {},
                   'JINJA_EXTENSIONS': [],
                   'LOCALE': '', # default to user locale
                   'WITH_PAGINATION': False,
                   'DEFAULT_PAGINATION': 5,
                   'DEFAULT_ORPHANS': 0,
                   'DEFAULT_METADATA': (),
                   'FILES_TO_COPY': (),
                   'DEFAULT_STATUS': 'published',
                   'ARTICLE_PERMALINK_STRUCTURE': '',
                   'KEEP_ORIGINAL_FILENAME': False
                   }

def read_settings(filename):
    """Load a Python file into a dictionary.
    """
    context = _DEFAULT_CONFIG.copy()
    if filename:
        tempdict = {}
        execfile(filename, tempdict)
        for key in tempdict:
            if key.isupper():
                context[key] = tempdict[key]

        # Make the paths relative to the settings file
        for path in ['PATH', 'OUTPUT_PATH']:
            if path in context:
                if context[path] is not None and not os.path.isabs(context[path]):
                    # FIXME:
                    context[path] = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(filename), context[path])))

    # if locales is not a list, make it one
    locales = context['LOCALE']

    if isinstance(locales, basestring):
        locales = [locales]

    # try to set the different locales, fallback on the default.
    if not locales:
        locales = _DEFAULT_CONFIG['LOCALE']

    for locale_ in locales:
        try:
            locale.setlocale(locale.LC_ALL, locale_)
            break # break if it is successfull
        except locale.Error:
            pass
    else:
        log.warn("LOCALE option doesn't contain a correct value")

    if not 'TIMEZONE' in context:
        log.warn("No timezone information specified in the settings. Assuming your "\
                "timezone is UTC for feed generation. "\
                "Check http://docs.notmyidea.org/alexis/pelican/settings.html#timezone "\
                "for more information")

    # set the locale
    return context
