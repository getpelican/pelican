# -*- coding: utf-8 -*-
import copy
import imp
import inspect
import os
import locale
import logging
import re

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
                   'FEED_ALL_ATOM': 'feeds/all.atom.xml',
                   'CATEGORY_FEED_ATOM': 'feeds/%s.atom.xml',
                   'TRANSLATION_FEED_ATOM': 'feeds/all-%s.atom.xml',
                   'FEED_MAX_ITEMS': '',
                   'SITEURL': '',
                   'SITENAME': 'A Pelican Blog',
                   'DISPLAY_PAGES_ON_MENU': True,
                   'PDF_GENERATOR': False,
                   'OUTPUT_SOURCES': False,
                   'OUTPUT_SOURCES_EXTENSION': '.text',
                   'USE_FOLDER_AS_CATEGORY': True,
                   'DEFAULT_CATEGORY': 'misc',
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
                   'EXTRA_TEMPLATES_PATHS': [],
                   'PAGINATED_DIRECT_TEMPLATES': ('index', ),
                   'PELICAN_CLASS': 'pelican.Pelican',
                   'DEFAULT_DATE_FORMAT': '%a %d %B %Y',
                   'DATE_FORMATS': {},
                   'JINJA_EXTENSIONS': [],
                   'LOCALE': '',  # default to user locale
                   'DEFAULT_PAGINATION': False,
                   'DEFAULT_ORPHANS': 0,
                   'DEFAULT_METADATA': (),
                   'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2}).*',
                   'FILES_TO_COPY': (),
                   'DEFAULT_STATUS': 'published',
                   'ARTICLE_PERMALINK_STRUCTURE': '',
                   'TYPOGRIFY': False,
                   'SUMMARY_MAX_LENGTH': 50,
                   'PLUGINS': [],
                   'TEMPLATE_PAGES': {}
                   }


def read_settings(filename=None, override=None):
    if filename:
        local_settings = get_settings_from_file(filename)
        # Make the paths relative to the settings file
        for p in ['PATH', 'OUTPUT_PATH', 'THEME']:
            if p in local_settings and local_settings[p] is not None \
                    and not isabs(local_settings[p]):
                absp = os.path.abspath(os.path.normpath(os.path.join(
                            os.path.dirname(filename), local_settings[p])))
                if p != 'THEME' or os.path.exists(p):
                    local_settings[p] = absp
    else:
        local_settings = copy.deepcopy(_DEFAULT_CONFIG)

    if override:
        local_settings.update(override)

    return configure_settings(local_settings)


def get_settings_from_module(module=None, default_settings=_DEFAULT_CONFIG):
    """
    Load settings from a module, returning a dict.
    """

    context = copy.deepcopy(default_settings)
    if module is not None:
        context.update(
                (k, v) for k, v in inspect.getmembers(module) if k.isupper())
    return context


def get_settings_from_file(filename, default_settings=_DEFAULT_CONFIG):
    """
    Load settings from a file path, returning a dict.

    """

    name = os.path.basename(filename).rpartition(".")[0]
    module = imp.load_source(name, filename)
    return get_settings_from_module(module, default_settings=default_settings)


def configure_settings(settings):
    """
    Provide optimizations, error checking, and warnings for loaded settings
    """
    if not 'PATH' in settings or not os.path.isdir(settings['PATH']):
        raise Exception('You need to specify a path containing the content'
                        ' (see pelican --help for more information)')

    # find the theme in pelican.theme if the given one does not exists
    if not os.path.isdir(settings['THEME']):
        theme_path = os.sep.join([os.path.dirname(
            os.path.abspath(__file__)), "themes/%s" % settings['THEME']])
        if os.path.exists(theme_path):
            settings['THEME'] = theme_path
        else:
            raise Exception("Impossible to find the theme %s"
                            % settings['THEME'])

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
    feed_keys = ['FEED_ATOM', 'FEED_RSS',
                 'FEED_ALL_ATOM', 'FEED_ALL_RSS',
                 'CATEGORY_FEED_ATOM', 'CATEGORY_FEED_RSS',
                 'TAG_FEED_ATOM', 'TAG_FEED_RSS',
                 'TRANSLATION_FEED_ATOM', 'TRANSLATION_FEED_RSS',
                ]

    if any(settings.get(k) for k in feed_keys):
        if not settings.get('FEED_DOMAIN'):
            logger.warn("Since feed URLs should always be absolute, you should specify "
                     "FEED_DOMAIN in your settings. (e.g., 'FEED_DOMAIN = "
                     "http://www.example.com')")

        if not settings.get('SITEURL'):
            logger.warn("Feeds generated without SITEURL set properly may not be valid")

    if not 'TIMEZONE' in settings:
        logger.warn("No timezone information specified in the settings. Assuming"
                 " your timezone is UTC for feed generation. Check "
                 "http://docs.notmyidea.org/alexis/pelican/settings.html#timezone "
                 "for more information")

    if 'LESS_GENERATOR' in settings:
        logger.warn("The LESS_GENERATOR setting has been removed in favor "
                    "of the Webassets plugin")

    if 'OUTPUT_SOURCES_EXTENSION' in settings:
        if not isinstance(settings['OUTPUT_SOURCES_EXTENSION'], str):
            settings['OUTPUT_SOURCES_EXTENSION'] = _DEFAULT_CONFIG['OUTPUT_SOURCES_EXTENSION']
            logger.warn("Detected misconfiguration with OUTPUT_SOURCES_EXTENSION."
                       " falling back to the default extension " +
                       _DEFAULT_CONFIG['OUTPUT_SOURCES_EXTENSION'])

    filename_metadata = settings.get('FILENAME_METADATA')
    if filename_metadata and not isinstance(filename_metadata, basestring):
        logger.error("Detected misconfiguration with FILENAME_METADATA"
                " setting (must be string or compiled pattern), falling"
                "back to the default")
        settings['FILENAME_METADATA'] = \
                _DEFAULT_CONFIG['FILENAME_METADATA']

    return settings
