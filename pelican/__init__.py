# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
try:
    import collections.abc as collections
except ImportError:
    import collections
import locale
import logging
import multiprocessing
import os
import pprint
import sys
import time
import traceback

import six

# pelican.log has to be the first pelican module to be loaded
# because logging.setLoggerClass has to be called before logging.getLogger
from pelican.log import init as init_logging
from pelican import signals  # noqa
from pelican.generators import (ArticlesGenerator, PagesGenerator,
                                SourceFileGenerator, StaticGenerator,
                                TemplatePagesGenerator)
from pelican.readers import Readers
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import read_settings
from pelican.utils import (clean_output_dir, file_watcher,
                           folder_watcher, maybe_pluralize)
from pelican.writers import Writer

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('pelican').version
except Exception:
    __version__ = "unknown"

DEFAULT_CONFIG_NAME = 'pelicanconf.py'
logger = logging.getLogger(__name__)


class Pelican(object):

    def __init__(self, settings):
        """Pelican initialisation

        Performs some checks on the environment before doing anything else.
        """

        # define the default settings
        self.settings = settings

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

    def run(self):
        """Run the generators and return"""
        start_time = time.time()

        context = self.settings.copy()
        # Share these among all the generators and content objects
        # They map source paths to Content objects or None
        context['generated_content'] = {}
        context['static_links'] = set()
        context['static_content'] = {}
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

        for p in generators:
            if hasattr(p, 'refresh_metadata_intersite_links'):
                p.refresh_metadata_intersite_links()

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
            (len(articles_generator.articles) +
             len(articles_generator.translations)),
            'article',
            'articles')
        pluralized_drafts = maybe_pluralize(
            (len(articles_generator.drafts) +
             len(articles_generator.drafts_translations)),
            'draft',
            'drafts')
        pluralized_pages = maybe_pluralize(
            (len(pages_generator.pages) +
             len(pages_generator.translations)),
            'page',
            'pages')
        pluralized_hidden_pages = maybe_pluralize(
            (len(pages_generator.hidden_pages) +
             len(pages_generator.hidden_translations)),
            'hidden page',
            'hidden pages')
        pluralized_draft_pages = maybe_pluralize(
            (len(pages_generator.draft_pages) +
             len(pages_generator.draft_translations)),
            'draft page',
            'draft pages')

        print('Done: Processed {}, {}, {}, {} and {} in {:.2f} seconds.'
              .format(
                    pluralized_articles,
                    pluralized_drafts,
                    pluralized_pages,
                    pluralized_hidden_pages,
                    pluralized_draft_pages,
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
        writers = [w for (_, w) in signals.get_writer.send(self)
                   if isinstance(w, type)]
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


class PrintSettings(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        instance, settings = get_instance(namespace)

        if values:
            # One or more arguments provided, so only print those settings
            for setting in values:
                if setting in settings:
                    # Only add newline between setting name and value if dict
                    if isinstance(settings[setting], dict):
                        setting_format = '\n{}:\n{}'
                    else:
                        setting_format = '\n{}: {}'
                    print(setting_format.format(
                        setting,
                        pprint.pformat(settings[setting])))
                else:
                    print('\n{} is not a recognized setting.'.format(setting))
                    break
        else:
            # No argument was given to --print-settings, so print all settings
            pprint.pprint(settings)

        parser.exit()


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description='A tool to generate a static blog, '
                    ' with restructured text input files.',
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

    parser.add_argument('--print-settings', dest='print_settings', nargs='*',
                        action=PrintSettings, metavar='SETTING_NAME',
                        help='Print current configuration settings and exit. '
                        'Append one or more setting name arguments to see the '
                        'values for specific settings only.')

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

    parser.add_argument('--fatal', metavar='errors|warnings',
                        choices=('errors', 'warnings'), default='',
                        help=('Exit the program with non-zero status if any '
                              'errors/warnings encountered.'))

    parser.add_argument('--logs-dedup-min-level', default='WARNING',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
                        help=('Only enable log de-duplication for levels equal'
                              ' to or above the specified value'))

    parser.add_argument('-l', '--listen', dest='listen', action='store_true',
                        help='Serve content files via HTTP and port 8000.')

    parser.add_argument('-p', '--port', dest='port', type=int,
                        help='Port to serve HTTP files at. (default: 8000)')

    parser.add_argument('-b', '--bind', dest='bind',
                        help='IP to bind to when serving files via HTTP '
                        '(default: 127.0.0.1)')

    args = parser.parse_args(argv)

    if args.port is not None and not args.listen:
        logger.warning('--port without --listen has no effect')
    if args.bind is not None and not args.listen:
        logger.warning('--bind without --listen has no effect')

    return args


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
    if args.port is not None:
        config['PORT'] = args.port
    if args.bind is not None:
        config['BIND'] = args.bind
    config['DEBUG'] = args.verbosity == logging.DEBUG

    # argparse returns bytes in Py2. There is no definite answer as to which
    # encoding argparse (or sys.argv) uses.
    # "Best" option seems to be locale.getpreferredencoding()
    # http://mail.python.org/pipermail/python-list/2006-October/405766.html
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
        args.settings = DEFAULT_CONFIG_NAME

    settings = read_settings(config_file, override=get_config(args))

    cls = settings['PELICAN_CLASS']
    if isinstance(cls, six.string_types):
        module, cls_name = cls.rsplit('.', 1)
        module = __import__(module)
        cls = getattr(module, cls_name)

    return cls(settings), settings


def autoreload(watchers, args, old_static, reader_descs, excqueue=None):
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
                new_watchers = set(new_static).difference(old_static)
                for static_path in new_watchers:
                    static_key = '[static]%s' % static_path
                    watchers[static_key] = folder_watcher(
                        os.path.join(pelican.path, static_path),
                        [''],
                        pelican.ignore_files)
                    modified[static_key] = next(watchers[static_key])

                # Removed static paths
                # Remove watchers and modified values
                old_watchers = set(old_static).difference(new_static)
                for static_path in old_watchers:
                    static_key = '[static]%s' % static_path
                    watchers.pop(static_key)
                    modified.pop(static_key)

                # Replace old_static with the new one
                old_static = new_static

            if any(modified.values()):
                print('\n-> Modified: {}. re-generating...'.format(
                    ', '.join(k for k, v in modified.items() if v)))

                if modified['content'] is None:
                    logger.warning(
                        'No valid files found in content for '
                        + 'the active readers:\n'
                        + '\n'.join(reader_descs))

                if modified['theme'] is None:
                    logger.warning('Empty theme folder. Using `basic` '
                                   'theme.')

                pelican.run()

        except KeyboardInterrupt as e:
            logger.warning("Keyboard interrupt, quitting.")
            if excqueue is not None:
                excqueue.put(traceback.format_exception_only(type(e), e)[-1])
            return

        except Exception as e:
            if (args.verbosity == logging.DEBUG):
                if excqueue is not None:
                    excqueue.put(
                        traceback.format_exception_only(type(e), e)[-1])
                else:
                    raise
            logger.warning(
                'Caught exception "%s". Reloading.', e)

        finally:
            time.sleep(.5)  # sleep to avoid cpu load


def listen(server, port, output, excqueue=None):
    RootedHTTPServer.allow_reuse_address = True
    try:
        httpd = RootedHTTPServer(
            output, (server, port), ComplexHTTPRequestHandler)
    except OSError as e:
        logging.error("Could not listen on port %s, server %s.", port, server)
        if excqueue is not None:
            excqueue.put(traceback.format_exception_only(type(e), e)[-1])
        return

    logging.info("Serving at port %s, server %s.", port, server)
    try:
        httpd.serve_forever()
    except Exception as e:
        if excqueue is not None:
            excqueue.put(traceback.format_exception_only(type(e), e)[-1])
        return


def main(argv=None):
    args = parse_arguments(argv)
    logs_dedup_min_level = getattr(logging, args.logs_dedup_min_level)
    init_logging(args.verbosity, args.fatal,
                 logs_dedup_min_level=logs_dedup_min_level)

    logger.debug('Pelican version: %s', __version__)
    logger.debug('Python version: %s', sys.version.split()[0])

    try:
        pelican, settings = get_instance(args)

        readers = Readers(settings)
        reader_descs = sorted(set(['%s (%s)' %
                                   (type(r).__name__,
                                    ', '.join(r.file_extensions))
                                   for r in readers.readers.values()
                                   if r.enabled]))

        watchers = {'content': folder_watcher(pelican.path,
                                              readers.extensions,
                                              pelican.ignore_files),
                    'theme': folder_watcher(pelican.theme,
                                            [''],
                                            pelican.ignore_files),
                    'settings': file_watcher(args.settings)}

        old_static = settings.get("STATIC_PATHS", [])
        for static_path in old_static:
            # use a prefix to avoid possible overriding of standard watchers
            # above
            watchers['[static]%s' % static_path] = folder_watcher(
                os.path.join(pelican.path, static_path),
                [''],
                pelican.ignore_files)

        if args.autoreload and args.listen:
            excqueue = multiprocessing.Queue()
            p1 = multiprocessing.Process(
                target=autoreload,
                args=(watchers, args, old_static, reader_descs, excqueue))
            p2 = multiprocessing.Process(
                target=listen,
                args=(settings.get('BIND'), settings.get('PORT'),
                      settings.get("OUTPUT_PATH"), excqueue))
            p1.start()
            p2.start()
            exc = excqueue.get()
            p1.terminate()
            p2.terminate()
            logger.critical(exc)
        elif args.autoreload:
            print('  --- AutoReload Mode: Monitoring `content`, `theme` and'
                  ' `settings` for changes. ---')
            autoreload(watchers, args, old_static, reader_descs)
        elif args.listen:
            listen(settings.get('BIND'), settings.get('PORT'),
                   settings.get("OUTPUT_PATH"))
        else:
            if next(watchers['content']) is None:
                logger.warning(
                    'No valid files found in content for '
                    + 'the active readers:\n'
                    + '\n'.join(reader_descs))

            if next(watchers['theme']) is None:
                logger.warning('Empty theme folder. Using `basic` theme.')

            pelican.run()

    except Exception as e:
        logger.critical('%s', e)

        if args.verbosity == logging.DEBUG:
            raise
        else:
            sys.exit(getattr(e, 'exitcode', 1))
