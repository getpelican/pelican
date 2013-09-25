# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import copy
import inspect
import os
import locale
import logging

try:
    # SourceFileLoader is the recommended way in 3.3+
    from importlib.machinery import SourceFileLoader
    load_source = lambda name, path: SourceFileLoader(name, path).load_module()
except ImportError:
    # but it does not exist in 3.2-, so fall back to imp
    import imp
    load_source = imp.load_source

from os.path import isabs


logger = logging.getLogger(__name__)


DEFAULT_THEME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'themes', 'notmyidea')
DEFAULT_CONFIG = {
    'PATH': os.curdir,
    'ARTICLE_DIR': '',
    'ARTICLE_EXCLUDES': ('pages',),
    'PAGE_DIR': 'pages',
    'PAGE_EXCLUDES': (),
    'THEME': DEFAULT_THEME,
    'OUTPUT_PATH': 'output',
    'READERS': {},
    'STATIC_PATHS': ['images', ],
    'THEME_STATIC_DIR': 'theme',
    'THEME_STATIC_PATHS': ['static', ],
    'FEED_ALL_ATOM': os.path.join('feeds', 'all.atom.xml'),
    'CATEGORY_FEED_ATOM': os.path.join('feeds', '%s.atom.xml'),
    'TRANSLATION_FEED_ATOM': os.path.join('feeds', 'all-%s.atom.xml'),
    'FEED_MAX_ITEMS': '',
    'SITEURL': '',
    'SITENAME': 'A Pelican Blog',
    'DISPLAY_PAGES_ON_MENU': True,
    'DISPLAY_CATEGORIES_ON_MENU': True,
    'OUTPUT_SOURCES': False,
    'OUTPUT_SOURCES_EXTENSION': '.text',
    'USE_FOLDER_AS_CATEGORY': True,
    'DEFAULT_CATEGORY': 'misc',
    'WITH_FUTURE_DATES': True,
    'CSS_FILE': 'main.css',
    'NEWEST_FIRST_ARCHIVES': True,
    'REVERSE_CATEGORY_ORDER': False,
    'DELETE_OUTPUT_DIRECTORY': False,
    'OUTPUT_RETENTION': (),
    'ARTICLE_URL': '{slug}.html',
    'ARTICLE_SAVE_AS': '{slug}.html',
    'ARTICLE_LANG_URL': '{slug}-{lang}.html',
    'ARTICLE_LANG_SAVE_AS': '{slug}-{lang}.html',
    'PAGE_URL': 'pages/{slug}.html',
    'PAGE_SAVE_AS': os.path.join('pages', '{slug}.html'),
    'PAGE_LANG_URL': 'pages/{slug}-{lang}.html',
    'PAGE_LANG_SAVE_AS': os.path.join('pages', '{slug}-{lang}.html'),
    'STATIC_URL': '{path}',
    'STATIC_SAVE_AS': '{path}',
    'PDF_GENERATOR': False,
    'PDF_STYLE_PATH': '',
    'PDF_STYLE': 'twelvepoint',
    'CATEGORY_URL': 'category/{slug}.html',
    'CATEGORY_SAVE_AS': os.path.join('category', '{slug}.html'),
    'TAG_URL': 'tag/{slug}.html',
    'TAG_SAVE_AS': os.path.join('tag', '{slug}.html'),
    'AUTHOR_URL': 'author/{slug}.html',
    'AUTHOR_SAVE_AS': os.path.join('author', '{slug}.html'),
    'PAGINATION_PATTERNS': [
        (0, '{name}{number}.html', '{name}{number}.html'),
    ],
    'YEAR_ARCHIVE_SAVE_AS': False,
    'MONTH_ARCHIVE_SAVE_AS': False,
    'DAY_ARCHIVE_SAVE_AS': False,
    'RELATIVE_URLS': False,
    'DEFAULT_LANG': 'en',
    'TAG_CLOUD_STEPS': 4,
    'TAG_CLOUD_MAX_ITEMS': 100,
    'DIRECT_TEMPLATES': ('index', 'tags', 'categories', 'authors', 'archives'),
    'EXTRA_TEMPLATES_PATHS': [],
    'PAGINATED_DIRECT_TEMPLATES': ('index', ),
    'PELICAN_CLASS': 'pelican.Pelican',
    'DEFAULT_DATE_FORMAT': '%a %d %B %Y',
    'DATE_FORMATS': {},
    'ASCIIDOC_OPTIONS': [],
    'MD_EXTENSIONS': ['codehilite(css_class=highlight)', 'extra'],
    'JINJA_EXTENSIONS': [],
    'JINJA_FILTERS': {},
    'LOCALE': [''],  # defaults to user locale
    'DEFAULT_PAGINATION': False,
    'DEFAULT_ORPHANS': 0,
    'DEFAULT_METADATA': (),
    'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2}).*',
    'PATH_METADATA': '',
    'EXTRA_PATH_METADATA': {},
    'DEFAULT_STATUS': 'published',
    'ARTICLE_PERMALINK_STRUCTURE': '',
    'TYPOGRIFY': False,
    'SUMMARY_MAX_LENGTH': 50,
    'PLUGIN_PATH': '',
    'PLUGINS': [],
    'PYGMENTS_RST_OPTIONS': {},
    'TEMPLATE_PAGES': {},
    'IGNORE_FILES': ['.#*'],
    'SLUG_SUBSTITUTIONS': (),
    'INTRASITE_LINK_REGEX': '[{|](?P<what>.*?)[|}]',
    'CACHE_PATH': '_pelican_cache',
    'USE_CACHE': False,
    }

PYGMENTS_RST_OPTIONS = None


def read_settings(path=None, override=None):
    if path:
        local_settings = get_settings_from_file(path)
        # Make the paths relative to the settings file
        for p in ['PATH', 'OUTPUT_PATH', 'THEME', 'PLUGIN_PATH', 'CACHE_PATH']:
            if p in local_settings and local_settings[p] is not None \
                    and not isabs(local_settings[p]):
                absp = os.path.abspath(os.path.normpath(os.path.join(
                    os.path.dirname(path), local_settings[p])))
                if p not in ('THEME', 'PLUGIN_PATH') or os.path.exists(absp):
                    local_settings[p] = absp
    else:
        local_settings = copy.deepcopy(DEFAULT_CONFIG)

    if override:
        local_settings.update(override)

    parsed_settings = configure_settings(local_settings)
    # This is because there doesn't seem to be a way to pass extra
    # parameters to docutils directive handlers, so we have to have a
    # variable here that we'll import from within Pygments.run (see
    # rstdirectives.py) to see what the user defaults were.
    global PYGMENTS_RST_OPTIONS
    PYGMENTS_RST_OPTIONS = parsed_settings.get('PYGMENTS_RST_OPTIONS', None)
    return parsed_settings


def get_settings_from_module(module=None, default_settings=DEFAULT_CONFIG):
    """Loads settings from a module, returns a dictionary."""

    context = copy.deepcopy(default_settings)
    if module is not None:
        context.update(
            (k, v) for k, v in inspect.getmembers(module) if k.isupper())
    return context


def get_settings_from_file(path, default_settings=DEFAULT_CONFIG):
    """Loads settings from a file path, returning a dict."""

    name, ext = os.path.splitext(os.path.basename(path))
    module = load_source(name, path)
    return get_settings_from_module(module, default_settings=default_settings)


def configure_settings(settings):
    """Provide optimizations, error checking and warnings for the given
    settings.

    """
    if not 'PATH' in settings or not os.path.isdir(settings['PATH']):
        raise Exception('You need to specify a path containing the content'
                        ' (see pelican --help for more information)')

    # lookup the theme in "pelican/themes" if the given one doesn't exist
    if not os.path.isdir(settings['THEME']):
        theme_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'themes',
            settings['THEME'])
        if os.path.exists(theme_path):
            settings['THEME'] = theme_path
        else:
            raise Exception("Could not find the theme %s"
                            % settings['THEME'])

    # standardize strings to lowercase strings
    for key in [
            'DEFAULT_LANG',
            ]:
        if key in settings:
            settings[key] = settings[key].lower()

    # standardize strings to lists
    for key in [
            'LOCALE',
            ]:
        if key in settings and isinstance(settings[key], six.string_types):
            settings[key] = [settings[key]]

    # check settings that must be a particular type
    for key, types in [
            ('OUTPUT_SOURCES_EXTENSION', six.string_types),
            ('FILENAME_METADATA', six.string_types),
            ]:
        if key in settings and not isinstance(settings[key], types):
            value = settings.pop(key)
            logger.warn(
                'Detected misconfigured {} ({}), '
                'falling back to the default ({})'.format(
                    key, value, DEFAULT_CONFIG[key]))

    # try to set the different locales, fallback on the default.
    locales = settings.get('LOCALE', DEFAULT_CONFIG['LOCALE'])

    for locale_ in locales:
        try:
            locale.setlocale(locale.LC_ALL, str(locale_))
            break  # break if it is successful
        except locale.Error:
            pass
    else:
        logger.warning("LOCALE option doesn't contain a correct value")

    if ('SITEURL' in settings):
        # If SITEURL has a trailing slash, remove it and provide a warning
        siteurl = settings['SITEURL']
        if (siteurl.endswith('/')):
            settings['SITEURL'] = siteurl[:-1]
            logger.warning("Removed extraneous trailing slash from SITEURL.")
        # If SITEURL is defined but FEED_DOMAIN isn't,
        # set FEED_DOMAIN to SITEURL
        if not 'FEED_DOMAIN' in settings:
            settings['FEED_DOMAIN'] = settings['SITEURL']

    # Warn if feeds are generated with both SITEURL & FEED_DOMAIN undefined
    feed_keys = [
        'FEED_ATOM', 'FEED_RSS',
        'FEED_ALL_ATOM', 'FEED_ALL_RSS',
        'CATEGORY_FEED_ATOM', 'CATEGORY_FEED_RSS',
        'TAG_FEED_ATOM', 'TAG_FEED_RSS',
        'TRANSLATION_FEED_ATOM', 'TRANSLATION_FEED_RSS',
    ]

    if any(settings.get(k) for k in feed_keys):
        if not settings.get('SITEURL'):
            logger.warning('Feeds generated without SITEURL set properly may'
                           ' not be valid')

    if not 'TIMEZONE' in settings:
        logger.warning(
            'No timezone information specified in the settings. Assuming'
            ' your timezone is UTC for feed generation. Check '
            'http://docs.getpelican.com/en/latest/settings.html#timezone '
            'for more information')

    # fix up pagination rules
    from pelican.paginator import PaginationRule
    pagination_rules = [
        PaginationRule(*r) for r in settings.get(
            'PAGINATION_PATTERNS',
            DEFAULT_CONFIG['PAGINATION_PATTERNS'],
        )
    ]
    settings['PAGINATION_PATTERNS'] = sorted(
        pagination_rules,
        key=lambda r: r[0],
    )

    # Save people from accidentally setting a string rather than a list
    path_keys = (
        'ARTICLE_EXCLUDES',
        'DEFAULT_METADATA',
        'DIRECT_TEMPLATES',
        'EXTRA_TEMPLATES_PATHS',
        'FILES_TO_COPY',
        'IGNORE_FILES',
        'JINJA_EXTENSIONS',
        'PAGINATED_DIRECT_TEMPLATES',
        'PLUGINS',
        'STATIC_PATHS',
        'THEME_STATIC_PATHS',
    )
    for PATH_KEY in filter(lambda k: k in settings, path_keys):
            if isinstance(settings[PATH_KEY], six.string_types):
                logger.warning("Detected misconfiguration with %s setting "
                               "(must be a list), falling back to the default"
                               % PATH_KEY)
                settings[PATH_KEY] = DEFAULT_CONFIG[PATH_KEY]

    for old, new, doc in [
            ('LESS_GENERATOR', 'the Webassets plugin', None),
            ('FILES_TO_COPY', 'STATIC_PATHS and EXTRA_PATH_METADATA',
             'https://github.com/getpelican/pelican/blob/master/docs/settings.rst#path-metadata'),
            ]:
        if old in settings:
            message = 'The {} setting has been removed in favor of {}'.format(
                old, new)
            if doc:
                message += ', see {} for details'.format(doc)
            logger.warning(message)

    return settings
