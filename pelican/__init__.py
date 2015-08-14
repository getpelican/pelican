# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import os
import re
import sys
import time
import logging
import argparse
import locale
import collections

# pelican.log has to be the first pelican module to be loaded
# because logging.setLoggerClass has to be called before logging.getLogger
from pelican.log import init

from pelican import signals

from pelican.generators import (ArticlesGenerator, PagesGenerator,
                                StaticGenerator, SourceFileGenerator,
                                TemplatePagesGenerator)
from pelican.readers import Readers
from pelican.settings import read_settings
from pelican.utils import (clean_output_dir, folder_watcher,
                           file_watcher, maybe_pluralize)
from pelican.writers import Writer

__version__ = "3.6.3"

DEFAULT_CONFIG_NAME = 'pelicanconf.py'


logger = logging.getLogger(__name__)


class Pelican(object):

    def __init__(self, settings):
        """
        Pelican initialisation, performs some checks on the environment before
        doing anything else.
        """

        # define the default settings
        self.settings = settings
        self._handle_deprecation()

        self.path = settings['PATH']
        self.theme = settings['THEME']
        self.output_path = settings['OUTPUT_PATH']
        self.ignore_files = settings['IGNORE_FILES']
        self.delete_outputdir = settings['DELETE_OUTPUT_DIRECTORY']
        self.output_retention = settings['OUTPUT_RETENTION']

        self.init_path()
        self.init_plugins()
        signals.initialized.send(self)

    def init_path(self):
        if not any(p in sys.path for p in ['', os.curdir]):
            logger.debug("Adding current directory to system path")
            sys.path.insert(0, '')

    def init_plugins(self):
        self.plugins = []
        logger.debug('Temporarily adding PLUGIN_PATHS to system path')
        _sys_path = sys.path[:]
        for pluginpath in self.settings['PLUGIN_PATHS']:
            sys.path.insert(0, pluginpath)
        for plugin in self.settings['PLUGINS']:
            # if it's a string, then import it
            if isinstance(plugin, six.string_types):
                logger.debug("Loading plugin `%s`", plugin)
                try:
                    plugin = __import__(plugin, globals(), locals(),
                                        str('module'))
                except ImportError as e:
                    logger.error(
                        "Cannot load plugin `%s`\n%s", plugin, e)
                    continue

            logger.debug("Registering plugin `%s`", plugin.__name__)
            plugin.register()
            self.plugins.append(plugin)
        logger.debug('Restoring system path')
        sys.path = _sys_path

    def _handle_deprecation(self):

        if self.settings.get('CLEAN_URLS', False):
            logger.warning('Found deprecated `CLEAN_URLS` in settings.'
                           ' Modifying the following settings for the'
                           ' same behaviour.')

            self.settings['ARTICLE_URL'] = '{slug}/'
            self.settings['ARTICLE_LANG_URL'] = '{slug}-{lang}/'
            self.settings['PAGE_URL'] = 'pages/{slug}/'
            self.settings['PAGE_LANG_URL'] = 'pages/{slug}-{lang}/'

            for setting in ('ARTICLE_URL', 'ARTICLE_LANG_URL', 'PAGE_URL',
                            'PAGE_LANG_URL'):
                logger.warning("%s = '%s'", setting, self.settings[setting])

        if self.settings.get('AUTORELOAD_IGNORE_CACHE'):
            logger.warning('Found deprecated `AUTORELOAD_IGNORE_CACHE` in '
                           'settings. Use --ignore-cache instead.')
            self.settings.pop('AUTORELOAD_IGNORE_CACHE')

        if self.settings.get('ARTICLE_PERMALINK_STRUCTURE', False):
            logger.warning('Found deprecated `ARTICLE_PERMALINK_STRUCTURE` in'
                           ' settings.  Modifying the following settings for'
                           ' the same behaviour.')

            structure = self.settings['ARTICLE_PERMALINK_STRUCTURE']

            # Convert %(variable) into {variable}.
            structure = re.sub('%\((\w+)\)s', '{\g<1>}', structure)

            # Convert %x into {date:%x} for strftime
            structure = re.sub('(%[A-z])', '{date:\g<1>}', structure)

            # Strip a / prefix
            structure = re.sub('^/', '', structure)

            for setting in ('ARTICLE_URL', 'ARTICLE_LANG_URL', 'PAGE_URL',
                            'PAGE_LANG_URL', 'DRAFT_URL', 'DRAFT_LANG_URL',
                            'ARTICLE_SAVE_AS', 'ARTICLE_LANG_SAVE_AS',
                            'DRAFT_SAVE_AS', 'DRAFT_LANG_SAVE_AS',
                            'PAGE_SAVE_AS', 'PAGE_LANG_SAVE_AS'):
                self.settings[setting] = os.path.join(structure,
                                                      self.settings[setting])
                logger.warning("%s = '%s'", setting, self.settings[setting])

        for new, old in [('FEED', 'FEED_ATOM'), ('TAG_FEED', 'TAG_FEED_ATOM'),
                         ('CATEGORY_FEED', 'CATEGORY_FEED_ATOM'),
                         ('TRANSLATION_FEED', 'TRANSLATION_FEED_ATOM')]:
            if self.settings.get(new, False):
                logger.warning(
                    'Found deprecated `%(new)s` in settings. Modify %(new)s '
                    'to %(old)s in your settings and theme for the same '
                    'behavior. Temporarily setting %(old)s for backwards '
                    'compatibility.',
                    {'new': new, 'old': old}
                )
                self.settings[old] = self.settings[new]

    def run(self):
        """Run the generators and return"""
        start_time = time.time()

        context = self.settings.copy()
        # Share these among all the generators and content objects:
        context['filenames'] = {}  # maps source path to Content object or None
        context['localsiteurl'] = self.settings['SITEURL'] 

        generators = [
            cls(
                context=context,
                settings=self.settings,
                path=self.path,
                theme=self.theme,
                output_path=self.output_path,
            ) for cls in self.get_generator_classes()
        ]

        # erase the directory if it is not the source and if that's
        # explicitly asked
        if (self.delete_outputdir and not
                os.path.realpath(self.path).startswith(self.output_path)):
            clean_output_dir(self.output_path, self.output_retention)

        for p in generators:
            if hasattr(p, 'generate_context'):
                p.generate_context()

        signals.all_generators_finalized.send(generators)

        writer = self.get_writer()

        for p in generators:
            if hasattr(p, 'generate_output'):
                p.generate_output(writer)

        signals.finalized.send(self)

        articles_generator = next(g for g in generators
                                  if isinstance(g, ArticlesGenerator))
        pages_generator = next(g for g in generators
                               if isinstance(g, PagesGenerator))

        pluralized_articles = maybe_pluralize(
            len(articles_generator.articles) +
                len(articles_generator.translations),
            'article',
            'articles')
        pluralized_drafts = maybe_pluralize(
            len(articles_generator.drafts) +
                len(articles_generator.drafts_translations),
            'draft',
            'drafts')
        pluralized_pages = maybe_pluralize(
            len(pages_generator.pages) +
                len(pages_generator.translations),
            'page',
            'pages')
        pluralized_hidden_pages = maybe_pluralize(
            len(pages_generator.hidden_pages) +
                len(pages_generator.hidden_translations),
            'hidden page',
            'hidden pages')

        print('Done: Processed {}, {}, {} and {} in {:.2f} seconds.'.format(
            pluralized_articles,
            pluralized_drafts,
            pluralized_pages,
            pluralized_hidden_pages,
            time.time() - start_time))

    def get_generator_classes(self):
        generators = [ArticlesGenerator, PagesGenerator]

        if self.settings['TEMPLATE_PAGES']:
            generators.append(TemplatePagesGenerator)
        if self.settings['OUTPUT_SOURCES']:
            generators.append(SourceFileGenerator)

        for pair in signals.get_generators.send(self):
            (funct, value) = pair

            if not isinstance(value, collections.Iterable):
                value = (value, )

            for v in value:
                if isinstance(v, type):
                    logger.debug('Found generator: %s', v)
                    generators.append(v)

        # StaticGenerator must run last, so it can identify files that
        # were skipped by the other generators, and so static files can
        # have their output paths overridden by the {attach} link syntax.
        generators.append(StaticGenerator)
        return generators

    def get_writer(self):
        writers = [ w for (_, w) in signals.get_writer.send(self)
                    if isinstance(w, type) ]
        writers_found = len(writers)
        if writers_found == 0:
            return Writer(self.output_path, settings=self.settings)
        else:
            writer = writers[0]
            if writers_found == 1:
                logger.debug('Found writer: %s', writer)
            else:
                logger.warning(
                    '%s writers found, using only first one: %s', 
                    writers_found, writer)
            return writer(self.output_path, settings=self.settings)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""A tool to generate a static blog,
        with restructured text input files.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(dest='path', nargs='?',
                        help='Path where to find the content files.',
                        default=None)

    parser.add_argument('-t', '--theme-path', dest='theme',
                        help='Path where to find the theme templates. If not '
                        'specified, it will use the default one included with '
                        'pelican.')

    parser.add_argument('-o', '--output', dest='output',
                        help='Where to output the generated files. If not '
                        'specified, a directory will be created, named '
                        '"output" in the current path.')

    parser.add_argument('-s', '--settings', dest='settings',
                        help='The settings of the application, this is '
                        'automatically set to {0} if a file exists with this '
                        'name.'.format(DEFAULT_CONFIG_NAME))

    parser.add_argument('-d', '--delete-output-directory',
                        dest='delete_outputdir', action='store_true',
                        default=None, help='Delete the output directory.')

    parser.add_argument('-v', '--verbose', action='store_const',
                        const=logging.INFO, dest='verbosity',
                        help='Show all messages.')

    parser.add_argument('-q', '--quiet', action='store_const',
                        const=logging.CRITICAL, dest='verbosity',
                        help='Show only critical errors.')

    parser.add_argument('-D', '--debug', action='store_const',
                        const=logging.DEBUG, dest='verbosity',
                        help='Show all messages, including debug messages.')

    parser.add_argument('--version', action='version', version=__version__,
                        help='Print the pelican version and exit.')

    parser.add_argument('-r', '--autoreload', dest='autoreload',
                        action='store_true',
                        help='Relaunch pelican each time a modification occurs'
                        ' on the content files.')

    parser.add_argument('--relative-urls', dest='relative_paths',
                        action='store_true',
                        help='Use relative urls in output, '
                             'useful for site development')

    parser.add_argument('--cache-path', dest='cache_path',
                        help=('Directory in which to store cache files. '
                              'If not specified, defaults to "cache".'))

    parser.add_argument('--ignore-cache', action='store_true',
                        dest='ignore_cache', help='Ignore content cache '
                        'from previous runs by not loading cache files.')

    parser.add_argument('-w', '--write-selected', type=str,
                        dest='selected_paths', default=None,
                        help='Comma separated list of selected paths to write')

    return parser.parse_args()


def get_config(args):
    config = {}
    if args.path:
        config['PATH'] = os.path.abspath(os.path.expanduser(args.path))
    if args.output:
        config['OUTPUT_PATH'] = \
            os.path.abspath(os.path.expanduser(args.output))
    if args.theme:
        abstheme = os.path.abspath(os.path.expanduser(args.theme))
        config['THEME'] = abstheme if os.path.exists(abstheme) else args.theme
    if args.delete_outputdir is not None:
        config['DELETE_OUTPUT_DIRECTORY'] = args.delete_outputdir
    if args.ignore_cache:
        config['LOAD_CONTENT_CACHE'] = False
    if args.cache_path:
        config['CACHE_PATH'] = args.cache_path
    if args.selected_paths:
        config['WRITE_SELECTED'] = args.selected_paths.split(',')
    if args.relative_paths:
        config['RELATIVE_URLS'] = args.relative_paths
    config['DEBUG'] = args.verbosity == logging.DEBUG

    # argparse returns bytes in Py2. There is no definite answer as to which
    # encoding argparse (or sys.argv) uses.
    # "Best" option seems to be locale.getpreferredencoding()
    # ref: http://mail.python.org/pipermail/python-list/2006-October/405766.html
    if not six.PY3:
        enc = locale.getpreferredencoding()
        for key in config:
            if key in ('PATH', 'OUTPUT_PATH', 'THEME'):
                config[key] = config[key].decode(enc)
    return config


def get_instance(args):

    config_file = args.settings
    if config_file is None and os.path.isfile(DEFAULT_CONFIG_NAME):
            config_file = DEFAULT_CONFIG_NAME

    settings = read_settings(config_file, override=get_config(args))

    cls = settings['PELICAN_CLASS']
    if isinstance(cls, six.string_types):
        module, cls_name = cls.rsplit('.', 1)
        module = __import__(module)
        cls = getattr(module, cls_name)

    return cls(settings), settings


def main():
    args = parse_arguments()
    init(args.verbosity)
    pelican, settings = get_instance(args)
    readers = Readers(settings)

    watchers = {'content': folder_watcher(pelican.path,
                                          readers.extensions,
                                          pelican.ignore_files),
                'theme': folder_watcher(pelican.theme,
                                        [''],
                                        pelican.ignore_files),
                'settings': file_watcher(args.settings)}

    old_static = settings.get("STATIC_PATHS", [])
    for static_path in old_static:
        # use a prefix to avoid possible overriding of standard watchers above
        watchers['[static]%s' % static_path] = folder_watcher(
            os.path.join(pelican.path, static_path),
            [''],
            pelican.ignore_files)

    try:
        if args.autoreload:
            print('  --- AutoReload Mode: Monitoring `content`, `theme` and'
                  ' `settings` for changes. ---')

            while True:
                try:
                    # Check source dir for changed files ending with the given
                    # extension in the settings. In the theme dir is no such
                    # restriction; all files are recursively checked if they
                    # have changed, no matter what extension the filenames
                    # have.
                    modified = {k: next(v) for k, v in watchers.items()}

                    if modified['settings']:
                        pelican, settings = get_instance(args)

                        # Adjust static watchers if there are any changes
                        new_static = settings.get("STATIC_PATHS", [])

                        # Added static paths
                        # Add new watchers and set them as modified
                        for static_path in set(new_static).difference(old_static):
                            static_key = '[static]%s' % static_path
                            watchers[static_key] = folder_watcher(
                                os.path.join(pelican.path, static_path),
                                [''],
                                pelican.ignore_files)
                            modified[static_key] = next(watchers[static_key])

                        # Removed static paths
                        # Remove watchers and modified values
                        for static_path in set(old_static).difference(new_static):
                            static_key = '[static]%s' % static_path
                            watchers.pop(static_key)
                            modified.pop(static_key)

                        # Replace old_static with the new one
                        old_static = new_static

                    if any(modified.values()):
                        print('\n-> Modified: {}. re-generating...'.format(
                            ', '.join(k for k, v in modified.items() if v)))

                        if modified['content'] is None:
                            logger.warning('No valid files found in content.')

                        if modified['theme'] is None:
                            logger.warning('Empty theme folder. Using `basic` '
                                           'theme.')

                        pelican.run()

                except KeyboardInterrupt:
                    logger.warning("Keyboard interrupt, quitting.")
                    break

                except Exception as e:
                    if (args.verbosity == logging.DEBUG):
                        raise
                    logger.warning(
                        'Caught exception "%s". Reloading.', e)

                finally:
                    time.sleep(.5)  # sleep to avoid cpu load

        else:
            if next(watchers['content']) is None:
                logger.warning('No valid files found in content.')

            if next(watchers['theme']) is None:
                logger.warning('Empty theme folder. Using `basic` theme.')

            pelican.run()

    except Exception as e:
        logger.critical('%s', e)

        if args.verbosity == logging.DEBUG:
            raise
        else:
            sys.exit(getattr(e, 'exitcode', 1))
