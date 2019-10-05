# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import copy
import inspect
import locale
import logging
import os
import re
from os.path import isabs
from posixpath import join as posix_join

import six

from pelican.log import LimitFilter


try:
    # spec_from_file_location is the recommended way in Python 3.5+
    import importlib.util

    def load_source(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
except ImportError:
    # but it does not exist in Python 2.7, so fall back to imp
    import imp
    load_source = imp.load_source


logger = logging.getLogger(__name__)

DEFAULT_THEME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'themes', 'notmyidea')
DEFAULT_CONFIG = {
    'PATH': os.curdir,
    'ARTICLE_PATHS': [''],
    'ARTICLE_EXCLUDES': [],
    'PAGE_PATHS': ['pages'],
    'PAGE_EXCLUDES': [],
    'THEME': DEFAULT_THEME,
    'OUTPUT_PATH': 'output',
    'READERS': {},
    'STATIC_PATHS': ['images'],
    'STATIC_EXCLUDES': [],
    'STATIC_EXCLUDE_SOURCES': True,
    'THEME_STATIC_DIR': 'theme',
    'THEME_STATIC_PATHS': ['static', ],
    'FEED_ALL_ATOM': posix_join('feeds', 'all.atom.xml'),
    'CATEGORY_FEED_ATOM': posix_join('feeds', '{slug}.atom.xml'),
    'AUTHOR_FEED_ATOM': posix_join('feeds', '{slug}.atom.xml'),
    'AUTHOR_FEED_RSS': posix_join('feeds', '{slug}.rss.xml'),
    'TRANSLATION_FEED_ATOM': posix_join('feeds', 'all-{lang}.atom.xml'),
    'FEED_MAX_ITEMS': '',
    'RSS_FEED_SUMMARY_ONLY': True,
    'SITEURL': '',
    'SITENAME': 'A Pelican Blog',
    'DISPLAY_PAGES_ON_MENU': True,
    'DISPLAY_CATEGORIES_ON_MENU': True,
    'DOCUTILS_SETTINGS': {},
    'OUTPUT_SOURCES': False,
    'OUTPUT_SOURCES_EXTENSION': '.text',
    'USE_FOLDER_AS_CATEGORY': True,
    'DEFAULT_CATEGORY': 'misc',
    'WITH_FUTURE_DATES': True,
    'CSS_FILE': 'main.css',
    'NEWEST_FIRST_ARCHIVES': True,
    'REVERSE_CATEGORY_ORDER': False,
    'DELETE_OUTPUT_DIRECTORY': False,
    'OUTPUT_RETENTION': [],
    'INDEX_SAVE_AS': 'index.html',
    'ARTICLE_URL': '{slug}.html',
    'ARTICLE_SAVE_AS': '{slug}.html',
    'ARTICLE_ORDER_BY': 'reversed-date',
    'ARTICLE_LANG_URL': '{slug}-{lang}.html',
    'ARTICLE_LANG_SAVE_AS': '{slug}-{lang}.html',
    'DRAFT_URL': 'drafts/{slug}.html',
    'DRAFT_SAVE_AS': posix_join('drafts', '{slug}.html'),
    'DRAFT_LANG_URL': 'drafts/{slug}-{lang}.html',
    'DRAFT_LANG_SAVE_AS': posix_join('drafts', '{slug}-{lang}.html'),
    'PAGE_URL': 'pages/{slug}.html',
    'PAGE_SAVE_AS': posix_join('pages', '{slug}.html'),
    'PAGE_ORDER_BY': 'basename',
    'PAGE_LANG_URL': 'pages/{slug}-{lang}.html',
    'PAGE_LANG_SAVE_AS': posix_join('pages', '{slug}-{lang}.html'),
    'DRAFT_PAGE_URL': 'drafts/pages/{slug}.html',
    'DRAFT_PAGE_SAVE_AS': posix_join('drafts', 'pages', '{slug}.html'),
    'DRAFT_PAGE_LANG_URL': 'drafts/pages/{slug}-{lang}.html',
    'DRAFT_PAGE_LANG_SAVE_AS': posix_join('drafts', 'pages',
                                          '{slug}-{lang}.html'),
    'STATIC_URL': '{path}',
    'STATIC_SAVE_AS': '{path}',
    'STATIC_CREATE_LINKS': False,
    'STATIC_CHECK_IF_MODIFIED': False,
    'CATEGORY_URL': 'category/{slug}.html',
    'CATEGORY_SAVE_AS': posix_join('category', '{slug}.html'),
    'TAG_URL': 'tag/{slug}.html',
    'TAG_SAVE_AS': posix_join('tag', '{slug}.html'),
    'AUTHOR_URL': 'author/{slug}.html',
    'AUTHOR_SAVE_AS': posix_join('author', '{slug}.html'),
    'PAGINATION_PATTERNS': [
        (1, '{name}{extension}', '{name}{extension}'),
        (2, '{name}{number}{extension}', '{name}{number}{extension}'),
    ],
    'YEAR_ARCHIVE_URL': '',
    'YEAR_ARCHIVE_SAVE_AS': '',
    'MONTH_ARCHIVE_URL': '',
    'MONTH_ARCHIVE_SAVE_AS': '',
    'DAY_ARCHIVE_URL': '',
    'DAY_ARCHIVE_SAVE_AS': '',
    'RELATIVE_URLS': False,
    'DEFAULT_LANG': 'en',
    'ARTICLE_TRANSLATION_ID': 'slug',
    'PAGE_TRANSLATION_ID': 'slug',
    'DIRECT_TEMPLATES': ['index', 'tags', 'categories', 'authors', 'archives'],
    'THEME_TEMPLATES_OVERRIDES': [],
    'PAGINATED_TEMPLATES': {'index': None, 'tag': None, 'category': None,
                            'author': None},
    'PELICAN_CLASS': 'pelican.Pelican',
    'DEFAULT_DATE_FORMAT': '%a %d %B %Y',
    'DATE_FORMATS': {},
    'MARKDOWN': {
        'extension_configs': {
            'markdown.extensions.codehilite': {'css_class': 'highlight'},
            'markdown.extensions.extra': {},
            'markdown.extensions.meta': {},
        },
        'output_format': 'html5',
    },
    'JINJA_FILTERS': {},
    'JINJA_ENVIRONMENT': {
        'trim_blocks': True,
        'lstrip_blocks': True,
        'extensions': [],
    },
    'LOG_FILTER': [],
    'LOCALE': [''],  # defaults to user locale
    'DEFAULT_PAGINATION': False,
    'DEFAULT_ORPHANS': 0,
    'DEFAULT_METADATA': {},
    'FILENAME_METADATA': r'(?P<date>\d{4}-\d{2}-\d{2}).*',
    'PATH_METADATA': '',
    'EXTRA_PATH_METADATA': {},
    'ARTICLE_PERMALINK_STRUCTURE': '',
    'TYPOGRIFY': False,
    'TYPOGRIFY_IGNORE_TAGS': [],
    'SUMMARY_MAX_LENGTH': 50,
    'PLUGIN_PATHS': [],
    'PLUGINS': [],
    'PYGMENTS_RST_OPTIONS': {},
    'TEMPLATE_PAGES': {},
    'TEMPLATE_EXTENSIONS': ['.html'],
    'IGNORE_FILES': ['.#*'],
    'SLUG_REGEX_SUBSTITUTIONS': [
        (r'[^\w\s-]', ''),  # remove non-alphabetical/whitespace/'-' chars
        (r'(?u)\A\s*', ''),  # strip leading whitespace
        (r'(?u)\s*\Z', ''),  # strip trailing whitespace
        (r'[-\s]+', '-'),  # reduce multiple whitespace or '-' to single '-'
    ],
    'INTRASITE_LINK_REGEX': '[{|](?P<what>.*?)[|}]',
    'SLUGIFY_SOURCE': 'title',
    'CACHE_CONTENT': False,
    'CONTENT_CACHING_LAYER': 'reader',
    'CACHE_PATH': 'cache',
    'GZIP_CACHE': True,
    'CHECK_MODIFIED_METHOD': 'mtime',
    'LOAD_CONTENT_CACHE': False,
    'WRITE_SELECTED': [],
    'FORMATTED_FIELDS': ['summary'],
    'PORT': 8000,
    'BIND': '127.0.0.1',
}

PYGMENTS_RST_OPTIONS = None


def read_settings(path=None, override=None):
    settings = override or {}

    if path:
        settings = dict(get_settings_from_file(path), **settings)

    if settings:
        settings = handle_deprecated_settings(settings)

    if path:
        # Make relative paths absolute
        def getabs(maybe_relative, base_path=path):
            if isabs(maybe_relative):
                return maybe_relative
            return os.path.abspath(os.path.normpath(os.path.join(
                os.path.dirname(base_path), maybe_relative)))

        for p in ['PATH', 'OUTPUT_PATH', 'THEME', 'CACHE_PATH']:
            if settings.get(p) is not None:
                absp = getabs(settings[p])
                # THEME may be a name rather than a path
                if p != 'THEME' or os.path.exists(absp):
                    settings[p] = absp

        if settings.get('PLUGIN_PATHS') is not None:
            settings['PLUGIN_PATHS'] = [getabs(pluginpath)
                                        for pluginpath
                                        in settings['PLUGIN_PATHS']]

    settings = dict(copy.deepcopy(DEFAULT_CONFIG), **settings)
    settings = configure_settings(settings)

    # This is because there doesn't seem to be a way to pass extra
    # parameters to docutils directive handlers, so we have to have a
    # variable here that we'll import from within Pygments.run (see
    # rstdirectives.py) to see what the user defaults were.
    global PYGMENTS_RST_OPTIONS
    PYGMENTS_RST_OPTIONS = settings.get('PYGMENTS_RST_OPTIONS', None)
    return settings


def get_settings_from_module(module=None):
    """Loads settings from a module, returns a dictionary."""

    context = {}
    if module is not None:
        context.update(
            (k, v) for k, v in inspect.getmembers(module) if k.isupper())
    return context


def get_settings_from_file(path):
    """Loads settings from a file path, returning a dict."""

    name, ext = os.path.splitext(os.path.basename(path))
    module = load_source(name, path)
    return get_settings_from_module(module)


def get_jinja_environment(settings):
    """Sets the environment for Jinja"""

    jinja_env = settings.setdefault('JINJA_ENVIRONMENT',
                                    DEFAULT_CONFIG['JINJA_ENVIRONMENT'])

    # Make sure we include the defaults if the user has set env variables
    for key, value in DEFAULT_CONFIG['JINJA_ENVIRONMENT'].items():
        if key not in jinja_env:
            jinja_env[key] = value

    return settings


def _printf_s_to_format_field(printf_string, format_field):
    """Tries to replace %s with {format_field} in the provided printf_string.
    Raises ValueError in case of failure.
    """
    TEST_STRING = 'PELICAN_PRINTF_S_DEPRECATION'
    expected = printf_string % TEST_STRING

    result = printf_string.replace('{', '{{').replace('}', '}}') \
        % '{{{}}}'.format(format_field)
    if result.format(**{format_field: TEST_STRING}) != expected:
        raise ValueError('Failed to safely replace %s with {{{}}}'.format(
            format_field))

    return result


def handle_deprecated_settings(settings):
    """Converts deprecated settings and issues warnings. Issues an exception
    if both old and new setting is specified.
    """

    # PLUGIN_PATH -> PLUGIN_PATHS
    if 'PLUGIN_PATH' in settings:
        logger.warning('PLUGIN_PATH setting has been replaced by '
                       'PLUGIN_PATHS, moving it to the new setting name.')
        settings['PLUGIN_PATHS'] = settings['PLUGIN_PATH']
        del settings['PLUGIN_PATH']

    # PLUGIN_PATHS: str -> [str]
    if isinstance(settings.get('PLUGIN_PATHS'), six.string_types):
        logger.warning("Defining PLUGIN_PATHS setting as string "
                       "has been deprecated (should be a list)")
        settings['PLUGIN_PATHS'] = [settings['PLUGIN_PATHS']]

    # JINJA_EXTENSIONS -> JINJA_ENVIRONMENT > extensions
    if 'JINJA_EXTENSIONS' in settings:
        logger.warning('JINJA_EXTENSIONS setting has been deprecated, '
                       'moving it to JINJA_ENVIRONMENT setting.')
        settings['JINJA_ENVIRONMENT']['extensions'] = \
            settings['JINJA_EXTENSIONS']
        del settings['JINJA_EXTENSIONS']

    # {ARTICLE,PAGE}_DIR -> {ARTICLE,PAGE}_PATHS
    for key in ['ARTICLE', 'PAGE']:
        old_key = key + '_DIR'
        new_key = key + '_PATHS'
        if old_key in settings:
            logger.warning(
                'Deprecated setting %s, moving it to %s list',
                old_key, new_key)
            settings[new_key] = [settings[old_key]]   # also make a list
            del settings[old_key]

    # EXTRA_TEMPLATES_PATHS -> THEME_TEMPLATES_OVERRIDES
    if 'EXTRA_TEMPLATES_PATHS' in settings:
        logger.warning('EXTRA_TEMPLATES_PATHS is deprecated use '
                       'THEME_TEMPLATES_OVERRIDES instead.')
        if ('THEME_TEMPLATES_OVERRIDES' in settings and
                settings['THEME_TEMPLATES_OVERRIDES']):
            raise Exception(
                'Setting both EXTRA_TEMPLATES_PATHS and '
                'THEME_TEMPLATES_OVERRIDES is not permitted. Please move to '
                'only setting THEME_TEMPLATES_OVERRIDES.')
        settings['THEME_TEMPLATES_OVERRIDES'] = \
            settings['EXTRA_TEMPLATES_PATHS']
        del settings['EXTRA_TEMPLATES_PATHS']

    # MD_EXTENSIONS -> MARKDOWN
    if 'MD_EXTENSIONS' in settings:
        logger.warning('MD_EXTENSIONS is deprecated use MARKDOWN '
                       'instead. Falling back to the default.')
        settings['MARKDOWN'] = DEFAULT_CONFIG['MARKDOWN']

    # LESS_GENERATOR -> Webassets plugin
    # FILES_TO_COPY -> STATIC_PATHS, EXTRA_PATH_METADATA
    for old, new, doc in [
            ('LESS_GENERATOR', 'the Webassets plugin', None),
            ('FILES_TO_COPY', 'STATIC_PATHS and EXTRA_PATH_METADATA',
                'https://github.com/getpelican/pelican/'
                'blob/master/docs/settings.rst#path-metadata'),
    ]:
        if old in settings:
            message = 'The {} setting has been removed in favor of {}'.format(
                old, new)
            if doc:
                message += ', see {} for details'.format(doc)
            logger.warning(message)

    # PAGINATED_DIRECT_TEMPLATES -> PAGINATED_TEMPLATES
    if 'PAGINATED_DIRECT_TEMPLATES' in settings:
        message = 'The {} setting has been removed in favor of {}'.format(
            'PAGINATED_DIRECT_TEMPLATES', 'PAGINATED_TEMPLATES')
        logger.warning(message)

        # set PAGINATED_TEMPLATES
        if 'PAGINATED_TEMPLATES' not in settings:
            settings['PAGINATED_TEMPLATES'] = {
                'tag': None, 'category': None, 'author': None}

        for t in settings['PAGINATED_DIRECT_TEMPLATES']:
            if t not in settings['PAGINATED_TEMPLATES']:
                settings['PAGINATED_TEMPLATES'][t] = None
        del settings['PAGINATED_DIRECT_TEMPLATES']

    # {SLUG,CATEGORY,TAG,AUTHOR}_SUBSTITUTIONS ->
    # {SLUG,CATEGORY,TAG,AUTHOR}_REGEX_SUBSTITUTIONS
    url_settings_url = \
        'http://docs.getpelican.com/en/latest/settings.html#url-settings'
    flavours = {'SLUG', 'CATEGORY', 'TAG', 'AUTHOR'}
    old_values = {f: settings[f + '_SUBSTITUTIONS']
                  for f in flavours if f + '_SUBSTITUTIONS' in settings}
    new_values = {f: settings[f + '_REGEX_SUBSTITUTIONS']
                  for f in flavours if f + '_REGEX_SUBSTITUTIONS' in settings}
    if old_values and new_values:
        raise Exception(
            'Setting both {new_key} and {old_key} (or variants thereof) is '
            'not permitted. Please move to only setting {new_key}.'
            .format(old_key='SLUG_SUBSTITUTIONS',
                    new_key='SLUG_REGEX_SUBSTITUTIONS'))
    if old_values:
        message = ('{} and variants thereof are deprecated and will be '
                   'removed in the future. Please use {} and variants thereof '
                   'instead. Check {}.'
                   .format('SLUG_SUBSTITUTIONS', 'SLUG_REGEX_SUBSTITUTIONS',
                           url_settings_url))
        logger.warning(message)
        if old_values.get('SLUG'):
            for f in {'CATEGORY', 'TAG'}:
                if old_values.get(f):
                    old_values[f] = old_values['SLUG'] + old_values[f]
            old_values['AUTHOR'] = old_values.get('AUTHOR', [])
        for f in flavours:
            if old_values.get(f) is not None:
                regex_subs = []
                # by default will replace non-alphanum characters
                replace = True
                for tpl in old_values[f]:
                    try:
                        src, dst, skip = tpl
                        if skip:
                            replace = False
                    except ValueError:
                        src, dst = tpl
                    regex_subs.append(
                        (re.escape(src), dst.replace('\\', r'\\')))

                if replace:
                    regex_subs += [
                        (r'[^\w\s-]', ''),
                        (r'(?u)\A\s*', ''),
                        (r'(?u)\s*\Z', ''),
                        (r'[-\s]+', '-'),
                    ]
                else:
                    regex_subs += [
                        (r'(?u)\A\s*', ''),
                        (r'(?u)\s*\Z', ''),
                    ]
                settings[f + '_REGEX_SUBSTITUTIONS'] = regex_subs
            settings.pop(f + '_SUBSTITUTIONS', None)

    # `%s` -> '{slug}` or `{lang}` in FEED settings
    for key in ['TRANSLATION_FEED_ATOM',
                'TRANSLATION_FEED_RSS'
                ]:
        if settings.get(key) and '%s' in settings[key]:
            logger.warning('%%s usage in %s is deprecated, use {lang} '
                           'instead.', key)
            try:
                settings[key] = _printf_s_to_format_field(
                    settings[key], 'lang')
            except ValueError:
                logger.warning('Failed to convert %%s to {lang} for %s. '
                               'Falling back to default.', key)
                settings[key] = DEFAULT_CONFIG[key]
    for key in ['AUTHOR_FEED_ATOM',
                'AUTHOR_FEED_RSS',
                'CATEGORY_FEED_ATOM',
                'CATEGORY_FEED_RSS',
                'TAG_FEED_ATOM',
                'TAG_FEED_RSS',
                ]:
        if settings.get(key) and '%s' in settings[key]:
            logger.warning('%%s usage in %s is deprecated, use {slug} '
                           'instead.', key)
            try:
                settings[key] = _printf_s_to_format_field(
                    settings[key], 'slug')
            except ValueError:
                logger.warning('Failed to convert %%s to {slug} for %s. '
                               'Falling back to default.', key)
                settings[key] = DEFAULT_CONFIG[key]

    # CLEAN_URLS
    if settings.get('CLEAN_URLS', False):
        logger.warning('Found deprecated `CLEAN_URLS` in settings.'
                       ' Modifying the following settings for the'
                       ' same behaviour.')

        settings['ARTICLE_URL'] = '{slug}/'
        settings['ARTICLE_LANG_URL'] = '{slug}-{lang}/'
        settings['PAGE_URL'] = 'pages/{slug}/'
        settings['PAGE_LANG_URL'] = 'pages/{slug}-{lang}/'

        for setting in ('ARTICLE_URL', 'ARTICLE_LANG_URL', 'PAGE_URL',
                        'PAGE_LANG_URL'):
            logger.warning("%s = '%s'", setting, settings[setting])

    # AUTORELOAD_IGNORE_CACHE -> --ignore-cache
    if settings.get('AUTORELOAD_IGNORE_CACHE'):
        logger.warning('Found deprecated `AUTORELOAD_IGNORE_CACHE` in '
                       'settings. Use --ignore-cache instead.')
        settings.pop('AUTORELOAD_IGNORE_CACHE')

    # ARTICLE_PERMALINK_STRUCTURE
    if settings.get('ARTICLE_PERMALINK_STRUCTURE', False):
        logger.warning('Found deprecated `ARTICLE_PERMALINK_STRUCTURE` in'
                       ' settings.  Modifying the following settings for'
                       ' the same behaviour.')

        structure = settings['ARTICLE_PERMALINK_STRUCTURE']

        # Convert %(variable) into {variable}.
        structure = re.sub(r'%\((\w+)\)s', r'{\g<1>}', structure)

        # Convert %x into {date:%x} for strftime
        structure = re.sub(r'(%[A-z])', r'{date:\g<1>}', structure)

        # Strip a / prefix
        structure = re.sub('^/', '', structure)

        for setting in ('ARTICLE_URL', 'ARTICLE_LANG_URL', 'PAGE_URL',
                        'PAGE_LANG_URL', 'DRAFT_URL', 'DRAFT_LANG_URL',
                        'ARTICLE_SAVE_AS', 'ARTICLE_LANG_SAVE_AS',
                        'DRAFT_SAVE_AS', 'DRAFT_LANG_SAVE_AS',
                        'PAGE_SAVE_AS', 'PAGE_LANG_SAVE_AS'):
            settings[setting] = os.path.join(structure,
                                             settings[setting])
            logger.warning("%s = '%s'", setting, settings[setting])

    # {,TAG,CATEGORY,TRANSLATION}_FEED -> {,TAG,CATEGORY,TRANSLATION}_FEED_ATOM
    for new, old in [('FEED', 'FEED_ATOM'), ('TAG_FEED', 'TAG_FEED_ATOM'),
                     ('CATEGORY_FEED', 'CATEGORY_FEED_ATOM'),
                     ('TRANSLATION_FEED', 'TRANSLATION_FEED_ATOM')]:
        if settings.get(new, False):
            logger.warning(
                'Found deprecated `%(new)s` in settings. Modify %(new)s '
                'to %(old)s in your settings and theme for the same '
                'behavior. Temporarily setting %(old)s for backwards '
                'compatibility.',
                {'new': new, 'old': old}
            )
            settings[old] = settings[new]

    return settings


def configure_settings(settings):
    """Provide optimizations, error checking, and warnings for the given
    settings.
    Also, specify the log messages to be ignored.
    """
    if 'PATH' not in settings or not os.path.isdir(settings['PATH']):
        raise Exception('You need to specify a path containing the content'
                        ' (see pelican --help for more information)')

    # specify the log messages to be ignored
    log_filter = settings.get('LOG_FILTER', DEFAULT_CONFIG['LOG_FILTER'])
    LimitFilter._ignore.update(set(log_filter))

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

    # make paths selected for writing absolute if necessary
    settings['WRITE_SELECTED'] = [
        os.path.abspath(path) for path in
        settings.get('WRITE_SELECTED', DEFAULT_CONFIG['WRITE_SELECTED'])
    ]

    # standardize strings to lowercase strings
    for key in ['DEFAULT_LANG']:
        if key in settings:
            settings[key] = settings[key].lower()

    # set defaults for Jinja environment
    settings = get_jinja_environment(settings)

    # standardize strings to lists
    for key in ['LOCALE']:
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
                'Detected misconfigured %s (%s), '
                'falling back to the default (%s)',
                key, value, DEFAULT_CONFIG[key])

    # try to set the different locales, fallback on the default.
    locales = settings.get('LOCALE', DEFAULT_CONFIG['LOCALE'])

    for locale_ in locales:
        try:
            locale.setlocale(locale.LC_ALL, str(locale_))
            break  # break if it is successful
        except locale.Error:
            pass
    else:
        logger.warning(
            "Locale could not be set. Check the LOCALE setting, ensuring it "
            "is valid and available on your system.")

    if ('SITEURL' in settings):
        # If SITEURL has a trailing slash, remove it and provide a warning
        siteurl = settings['SITEURL']
        if (siteurl.endswith('/')):
            settings['SITEURL'] = siteurl[:-1]
            logger.warning("Removed extraneous trailing slash from SITEURL.")
        # If SITEURL is defined but FEED_DOMAIN isn't,
        # set FEED_DOMAIN to SITEURL
        if 'FEED_DOMAIN' not in settings:
            settings['FEED_DOMAIN'] = settings['SITEURL']

    # check content caching layer and warn of incompatibilities
    if settings.get('CACHE_CONTENT', False) and \
            settings.get('CONTENT_CACHING_LAYER', '') == 'generator' and \
            settings.get('WITH_FUTURE_DATES', False):
        logger.warning(
            "WITH_FUTURE_DATES conflicts with CONTENT_CACHING_LAYER "
            "set to 'generator', use 'reader' layer instead")

    # Warn if feeds are generated with both SITEURL & FEED_DOMAIN undefined
    feed_keys = [
        'FEED_ATOM', 'FEED_RSS',
        'FEED_ALL_ATOM', 'FEED_ALL_RSS',
        'CATEGORY_FEED_ATOM', 'CATEGORY_FEED_RSS',
        'AUTHOR_FEED_ATOM', 'AUTHOR_FEED_RSS',
        'TAG_FEED_ATOM', 'TAG_FEED_RSS',
        'TRANSLATION_FEED_ATOM', 'TRANSLATION_FEED_RSS',
    ]

    if any(settings.get(k) for k in feed_keys):
        if not settings.get('SITEURL'):
            logger.warning('Feeds generated without SITEURL set properly may'
                           ' not be valid')

    if 'TIMEZONE' not in settings:
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
        'THEME_TEMPLATES_OVERRIDES',
        'FILES_TO_COPY',
        'IGNORE_FILES',
        'PAGINATED_DIRECT_TEMPLATES',
        'PLUGINS',
        'STATIC_EXCLUDES',
        'STATIC_PATHS',
        'THEME_STATIC_PATHS',
        'ARTICLE_PATHS',
        'PAGE_PATHS',
    )
    for PATH_KEY in filter(lambda k: k in settings, path_keys):
        if isinstance(settings[PATH_KEY], six.string_types):
            logger.warning("Detected misconfiguration with %s setting "
                           "(must be a list), falling back to the default",
                           PATH_KEY)
            settings[PATH_KEY] = DEFAULT_CONFIG[PATH_KEY]

    # Add {PAGE,ARTICLE}_PATHS to {ARTICLE,PAGE}_EXCLUDES
    mutually_exclusive = ('ARTICLE', 'PAGE')
    for type_1, type_2 in [mutually_exclusive, mutually_exclusive[::-1]]:
        try:
            includes = settings[type_1 + '_PATHS']
            excludes = settings[type_2 + '_EXCLUDES']
            for path in includes:
                if path not in excludes:
                    excludes.append(path)
        except KeyError:
            continue            # setting not specified, nothing to do

    return settings
