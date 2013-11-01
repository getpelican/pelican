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

from pelican import signals

from pelican.generators import (ArticlesGenerator, PagesGenerator,
                                StaticGenerator, SourceFileGenerator,
                                TemplatePagesGenerator)
from pelican.log import init
from pelican.readers import Readers
from pelican.settings import read_settings
from pelican.utils import clean_output_dir, folder_watcher, file_watcher
from pelican.writers import Writer

__version__ = "3.3.1.dev"

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
        logger.debug('Temporarily adding PLUGIN_PATH to system path')
        _sys_path = sys.path[:]
        sys.path.insert(0, self.settings['PLUGIN_PATH'])
        for plugin in self.settings['PLUGINS']:
            # if it's a string, then import it
            if isinstance(plugin, six.string_types):
                logger.debug("Loading plugin `{0}`".format(plugin))
                try:
                    plugin = __import__(plugin, globals(), locals(), str('module'))
                except ImportError as e:
                    logger.error("Can't find plugin `{0}`: {1}".format(plugin, e))
                    continue

            logger.debug("Registering plugin `{0}`".format(plugin.__name__))
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
                logger.warning("%s = '%s'" % (setting, self.settings[setting]))

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
                            'PAGE_LANG_URL', 'ARTICLE_SAVE_AS',
                            'ARTICLE_LANG_SAVE_AS', 'PAGE_SAVE_AS',
                            'PAGE_LANG_SAVE_AS'):
                self.settings[setting] = os.path.join(structure,
                                                      self.settings[setting])
                logger.warning("%s = '%s'" % (setting, self.settings[setting]))

        if self.settings.get('FEED', False):
            logger.warning('Found deprecated `FEED` in settings. Modify FEED'
            ' to FEED_ATOM in your settings and theme for the same behavior.'
            ' Temporarily setting FEED_ATOM for backwards compatibility.')
            self.settings['FEED_ATOM'] = self.settings['FEED']

        if self.settings.get('TAG_FEED', False):
            logger.warning('Found deprecated `TAG_FEED` in settings. Modify '
            ' TAG_FEED to TAG_FEED_ATOM in your settings and theme for the '
            'same behavior. Temporarily setting TAG_FEED_ATOM for backwards '
            'compatibility.')
            self.settings['TAG_FEED_ATOM'] = self.settings['TAG_FEED']

        if self.settings.get('CATEGORY_FEED', False):
            logger.warning('Found deprecated `CATEGORY_FEED` in settings. '
            'Modify CATEGORY_FEED to CATEGORY_FEED_ATOM in your settings and '
            'theme for the same behavior. Temporarily setting '
            'CATEGORY_FEED_ATOM for backwards compatibility.')
            self.settings['CATEGORY_FEED_ATOM'] =\
                    self.settings['CATEGORY_FEED']

        if self.settings.get('TRANSLATION_FEED', False):
            logger.warning('Found deprecated `TRANSLATION_FEED` in settings. '
            'Modify TRANSLATION_FEED to TRANSLATION_FEED_ATOM in your '
            'settings and theme for the same behavior. Temporarily setting '
            'TRANSLATION_FEED_ATOM for backwards compatibility.')
            self.settings['TRANSLATION_FEED_ATOM'] =\
                    self.settings['TRANSLATION_FEED']

    def run(self):
        """Run the generators and return"""
        start_time = time.time()

        context = self.settings.copy()
        context['filenames'] = {}  # share the dict between all the generators
        context['localsiteurl'] = self.settings['SITEURL']  # share
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
        # explicitely asked
        if (self.delete_outputdir and not
                os.path.realpath(self.path).startswith(self.output_path)):
            clean_output_dir(self.output_path, self.output_retention)

        for p in generators:
            if hasattr(p, 'generate_context'):
                p.generate_context()

        writer = self.get_writer()

        for p in generators:
            if hasattr(p, 'generate_output'):
                p.generate_output(writer)

        signals.finalized.send(self)

        articles_generator = next(g for g in generators if isinstance(g, ArticlesGenerator))
        pages_generator = next(g for g in generators if isinstance(g, PagesGenerator))

        print('Done: Processed {} articles and {} pages in {:.2f} seconds.'.format(
            len(articles_generator.articles) + len(articles_generator.translations),
            len(pages_generator.pages) + len(pages_generator.translations),
            time.time() - start_time))

    def get_generator_classes(self):
        generators = [StaticGenerator, ArticlesGenerator, PagesGenerator]

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
                    logger.debug('Found generator: {0}'.format(v))
                    generators.append(v)

        return generators

    def get_writer(self):
        return Writer(self.output_path, settings=self.settings)


def parse_arguments():
    parser = argparse.ArgumentParser(description="""A tool to generate a
    static blog, with restructured text input files.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(dest='path', nargs='?',
        help='Path where to find the content files.',
        default=None)

    parser.add_argument('-t', '--theme-path', dest='theme',
        help='Path where to find the theme templates. If not specified, it '
             'will use the default one included with pelican.')

    parser.add_argument('-o', '--output', dest='output',
        help='Where to output the generated files. If not specified, a '
             'directory will be created, named "output" in the current path.')

    parser.add_argument('-s', '--settings', dest='settings',
        help='The settings of the application, this is automatically set to '
        '{0} if a file exists with this name.'.format(DEFAULT_CONFIG_NAME))

    parser.add_argument('-d', '--delete-output-directory',
        dest='delete_outputdir',
        action='store_true',
        default=None,
        help='Delete the output directory.')

    parser.add_argument('-v', '--verbose', action='store_const',
        const=logging.INFO, dest='verbosity',
        help='Show all messages.')

    parser.add_argument('-q', '--quiet', action='store_const',
        const=logging.CRITICAL, dest='verbosity',
        help='Show only critical errors.')

    parser.add_argument('-D', '--debug', action='store_const',
        const=logging.DEBUG, dest='verbosity',
        help='Show all message, including debug messages.')

    parser.add_argument('--version', action='version', version=__version__,
        help='Print the pelican version and exit.')

    parser.add_argument('-r', '--autoreload', dest='autoreload',
        action='store_true',
        help="Relaunch pelican each time a modification occurs"
                             " on the content files.")
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
                        pelican, settings  = get_instance(args)

                    if any(modified.values()):
                        print('\n-> Modified: {}. re-generating...'.format(
                                ', '.join(k for k, v in modified.items() if v)))

                        if modified['content'] is None:
                            logger.warning('No valid files found in content.')

                        if modified['theme'] is None:
                            logger.warning('Empty theme folder. Using `basic` theme.')

                        pelican.run()

                except KeyboardInterrupt:
                    logger.warning("Keyboard interrupt, quitting.")
                    break

                except Exception as e:
                    if (args.verbosity == logging.DEBUG):
                        logger.critical(e.args)
                        raise
                    logger.warning(
                            'Caught exception "{0}". Reloading.'.format(e))

                finally:
                    time.sleep(.5)  # sleep to avoid cpu load

        else:
            if next(watchers['content']) is None:
                logger.warning('No valid files found in content.')

            if next(watchers['theme']) is None:
                logger.warning('Empty theme folder. Using `basic` theme.')

            pelican.run()

    except Exception as e:
        # localized systems have errors in native language if locale is set
        # so convert the message to unicode with the correct encoding
        msg = str(e)
        if not six.PY3:
            msg = msg.decode(locale.getpreferredencoding())

        logger.critical(msg)

        if (args.verbosity == logging.DEBUG):
            raise
        else:
            sys.exit(getattr(e, 'exitcode', 1))
