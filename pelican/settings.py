# -*- coding: utf-8 -*-
import copy
import imp
import inspect
import os
import locale
import logging

from os.path import isabs


logger = logging.getLogger(__name__)


DEFAULT_THEME = os.sep.join([os.path.dirname(os.path.abspath(__file__)),
                              "themes/notmyidea"])
_DEFAULT_CONFIG = {'PATH': '.',
                   'ARTICLE_DIR': '',
                   'ARTICLE_EXCLUDES': ('pages',),
                   'PAGE_DIR': 'pages',
                   'PAGE_EXCLUDES': (),
                   'THEME': DEFAULT_THEME,
                   'OUTPUT_PATH': 'output/',
                   'MARKUP': ('rst', 'md'),
                   'STATIC_PATHS': ['images', ],
                   'THEME_STATIC_PATHS': ['static', ],
                   'FEED_ATOM': 'feeds/all.atom.xml',
                   'CATEGORY_FEED_ATOM': 'feeds/%s.atom.xml',
                   'TRANSLATION_FEED': 'feeds/all-%s.atom.xml',
                   'FEED_MAX_ITEMS': '',
                   'SITEURL': '',
                   'SITENAME': 'A Pelican Blog',
                   'DISPLAY_PAGES_ON_MENU': True,
                   'PDF_GENERATOR': False,
                   'DEFAULT_CATEGORY': 'misc',
                   'DEFAULT_DATE': 'fs',
                   'WITH_FUTURE_DATES': True,
                   'CSS_FILE': 'main.css',
                   'NEWEST_FIRST_ARCHIVES': True,
                   'REVERSE_CATEGORY_ORDER': False,
                   'DELETE_OUTPUT_DIRECTORY': False,
                   'ARTICLE_URL': '{slug}.html',
                   'ARTICLE_SAVE_AS': '{slug}.html',
                   'ARTICLE_LANG_URL': '{slug}-{lang}.html',
                   'ARTICLE_LANG_SAVE_AS': '{slug}-{lang}.html',
                   'PAGE_URL': 'pages/{slug}.html',
                   'PAGE_SAVE_AS': 'pages/{slug}.html',
                   'PAGE_LANG_URL': 'pages/{slug}-{lang}.html',
                   'PAGE_LANG_SAVE_AS': 'pages/{slug}-{lang}.html',
                   'CATEGORY_URL': 'category/{slug}.html',
                   'CATEGORY_SAVE_AS': 'category/{slug}.html',
                   'TAG_URL': 'tag/{slug}.html',
                   'TAG_SAVE_AS': 'tag/{slug}.html',
                   'AUTHOR_URL': u'author/{slug}.html',
                   'AUTHOR_SAVE_AS': u'author/{slug}.html',
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
                   'LOCALE': '',  # default to user locale
                   'DEFAULT_PAGINATION': False,
                   'DEFAULT_ORPHANS': 0,
                   'DEFAULT_METADATA': (),
                   'FILES_TO_COPY': (),
                   'DEFAULT_STATUS': 'published',
                   'ARTICLE_PERMALINK_STRUCTURE': '',
                   'TYPOGRIFY': False,
                   'LESS_GENERATOR': False,
                   'SUMMARY_MAX_LENGTH': 50,
                   'WEBASSETS': False,
                   'PLUGINS': [],
                   }


def read_settings(filename=None):
    if filename:
        local_settings = get_settings_from_file(filename)
    else:
        local_settings = copy.deepcopy(_DEFAULT_CONFIG)
    configured_settings = configure_settings(local_settings, None, filename)
    return configured_settings


def get_settings_from_module(module=None, default_settings=_DEFAULT_CONFIG):
    """
    Load settings from a module, returning a dict.
    """

    context = copy.deepcopy(default_settings)
    if module is not None:
         context.update(
             (k, v) for k, v in inspect.getmembers(module) if k.isupper()
         )
    return context


def get_settings_from_file(filename, default_settings=_DEFAULT_CONFIG):
    """
    Load settings from a file path, returning a dict.

    """

    name = os.path.basename(filename).rpartition(".")[0]
    module = imp.load_source(name, filename)
    return get_settings_from_module(module, default_settings=default_settings)


def configure_settings(settings, default_settings=None, filename=None):
    """Provide optimizations, error checking, and warnings for loaded settings"""
    if default_settings is None:
        default_settings = copy.deepcopy(_DEFAULT_CONFIG)

    # Make the paths relative to the settings file
    if filename:
        for path in ['PATH', 'OUTPUT_PATH']:
            if path in settings:
                if settings[path] is not None and not isabs(settings[path]):
                    settings[path] = os.path.abspath(os.path.normpath(
                        os.path.join(os.path.dirname(filename), settings[path]))
                    )

    # if locales is not a list, make it one
    locales = settings['LOCALE']

    if isinstance(locales, basestring):
        locales = [locales]

    # try to set the different locales, fallback on the default.
    if not locales:
        locales = _DEFAULT_CONFIG['LOCALE']

    for locale_ in locales:
        try:
            locale.setlocale(locale.LC_ALL, locale_)
            break  # break if it is successful
        except locale.Error:
            pass
    else:
        logger.warn("LOCALE option doesn't contain a correct value")

    if ('SITEURL' in settings):
        # If SITEURL has a trailing slash, remove it and provide a warning
        siteurl = settings['SITEURL']
        if (siteurl.endswith('/')):
            settings['SITEURL'] = siteurl[:-1]
            logger.warn("Removed extraneous trailing slash from SITEURL.")
        # If SITEURL is defined but FEED_DOMAIN isn't, set FEED_DOMAIN = SITEURL
        if not 'FEED_DOMAIN' in settings:
            settings['FEED_DOMAIN'] = settings['SITEURL']

    # Warn if feeds are generated with both SITEURL & FEED_DOMAIN undefined
    if (('FEED_ATOM' in settings) or ('FEED_RSS' in settings)) and (not 'FEED_DOMAIN' in settings):
        logger.warn("Since feed URLs should always be absolute, you should specify "
                 "FEED_DOMAIN in your settings. (e.g., 'FEED_DOMAIN = "
                 "http://www.example.com')")

    if not 'TIMEZONE' in settings:
        logger.warn("No timezone information specified in the settings. Assuming"
                 " your timezone is UTC for feed generation. Check "
                 "http://docs.notmyidea.org/alexis/pelican/settings.html#timezone "
                 "for more information")

    if 'WEBASSETS' in settings and settings['WEBASSETS'] is not False:
        try:
            from webassets.ext.jinja2 import AssetsExtension
            settings['JINJA_EXTENSIONS'].append(AssetsExtension)
        except ImportError:
            logger.warn("You must install the webassets module to use WEBASSETS.")
            settings['WEBASSETS'] = False

    return settings
