import os

_DEFAULT_THEME = os.sep.join([os.path.dirname(os.path.abspath(__file__)),
                              "themes/notmyidea"])
_DEFAULT_CONFIG = {'PATH': None,
                   'THEME': _DEFAULT_THEME,
                   'OUTPUT_PATH': 'output/',
                   'MARKUP': ('rst', 'md'),
                   'STATIC_PATHS': ['images',],
                   'THEME_STATIC_PATHS': ['static',],
                   'FEED': 'feeds/all.atom.xml',
                   'CATEGORY_FEED': 'feeds/%s.atom.xml',
                   'TRANSLATION_FEED': 'feeds/all-%s.atom.xml',
                   'SITENAME': 'A Pelican Blog',
                   'DISPLAY_PAGES_ON_MENU': True,
                   'PDF_GENERATOR': False,
                   'DEFAULT_CATEGORY': 'misc',
                   'FALLBACK_ON_FS_DATE': True,
                   'CSS_FILE': 'main.css',
                   'REVERSE_ARCHIVE_ORDER': False,
                   'KEEP_OUTPUT_DIRECTORY': False,
                   'CLEAN_URLS': False, # use /blah/ instead /blah.html in urls
                   'RELATIVE_URLS': True,
                   'DEFAULT_LANG': 'en',
                   'TAG_CLOUD_STEPS': 4,
                   'TAG_CLOUD_MAX_ITEMS': 100,
                   'DIRECT_TEMPLATES': ('index', 'tags', 'categories', 'archives'),
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
    return context
