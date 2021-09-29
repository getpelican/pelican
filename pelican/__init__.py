import argparse
import logging
import multiprocessing
import os
import pprint
import sys
import time
import traceback
from collections.abc import Iterable
# Combines all paths to `pelican` package accessible from `sys.path`
# Makes it possible to install `pelican` and namespace plugins into different
# locations in the file system (e.g. pip with `-e` or `--user`)
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

# pelican.log has to be the first pelican module to be loaded
# because logging.setLoggerClass has to be called before logging.getLogger
from pelican.log import console
from pelican.log import init as init_logging
from pelican.generators import (ArticlesGenerator,  # noqa: I100
                                PagesGenerator, SourceFileGenerator,
                                StaticGenerator, TemplatePagesGenerator)
from pelican.plugins import signals
from pelican.plugins._utils import get_plugin_name, load_plugins
from pelican.readers import Readers
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import coerce_overrides, read_settings
from pelican.utils import (FileSystemWatcher, clean_output_dir, maybe_pluralize)
from pelican.writers import Writer

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('pelican').version
except Exception:
    __version__ = "unknown"

DEFAULT_CONFIG_NAME = 'pelicanconf.py'
logger = logging.getLogger(__name__)


class Pelican:

    def __init__(self, settings):
        """Pelican initialization

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
        for plugin in load_plugins(self.settings):
            name = get_plugin_name(plugin)
            logger.debug('Registering plugin `%s`', name)
            try:
                plugin.register()
                self.plugins.append(plugin)
            except Exception as e:
                logger.error('Cannot register plugin `%s`\n%s',
                             name, e)

        self.settings['PLUGINS'] = [get_plugin_name(p) for p in self.plugins]

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
            ) for cls in self._get_generator_classes()
        ]

        # Delete the output directory if (1) the appropriate setting is True
        # and (2) that directory is not the parent of the source directory
        if (self.delete_outputdir
                and os.path.commonpath([os.path.realpath(self.output_path)]) !=
                os.path.commonpath([os.path.realpath(self.output_path),
                                    os.path.realpath(self.path)])):
            clean_output_dir(self.output_path, self.output_retention)

        for p in generators:
            if hasattr(p, 'generate_context'):
                p.generate_context()

        for p in generators:
            if hasattr(p, 'refresh_metadata_intersite_links'):
                p.refresh_metadata_intersite_links()

        signals.all_generators_finalized.send(generators)

        writer = self._get_writer()

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
        pluralized_hidden_articles = maybe_pluralize(
            (len(articles_generator.hidden_articles) +
             len(articles_generator.hidden_translations)),
            'hidden article',
            'hidden articles')
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

        console.print('Done: Processed {}, {}, {}, {}, {} and {} in {:.2f} seconds.'
                      .format(
                              pluralized_articles,
                              pluralized_drafts,
                              pluralized_hidden_articles,
                              pluralized_pages,
                              pluralized_hidden_pages,
                              pluralized_draft_pages,
                              time.time() - start_time))

    def _get_generator_classes(self):
        discovered_generators = [
            (ArticlesGenerator, "internal"),
            (PagesGenerator, "internal")
        ]

        if self.settings["TEMPLATE_PAGES"]:
            discovered_generators.append((TemplatePagesGenerator, "internal"))

        if self.settings["OUTPUT_SOURCES"]:
            discovered_generators.append((SourceFileGenerator, "internal"))

        for receiver, values in signals.get_generators.send(self):
            if not isinstance(values, Iterable):
                values = (values,)
            for generator in values:
                if generator is None:
                    continue  # plugin did not return a generator
                discovered_generators.append((generator, receiver.__module__))

        # StaticGenerator must run last, so it can identify files that
        # were skipped by the other generators, and so static files can
        # have their output paths overridden by the {attach} link syntax.
        discovered_generators.append((StaticGenerator, "internal"))

        generators = []

        for generator, origin in discovered_generators:
            if not isinstance(generator, type):
                logger.error("Generator %s (%s) cannot be loaded", generator, origin)
                continue

            logger.debug("Found generator: %s (%s)", generator.__name__, origin)
            generators.append(generator)

        return generators

    def _get_writer(self):
        writers = [w for _, w in signals.get_writer.send(self) if isinstance(w, type)]
        num_writers = len(writers)

        if num_writers == 0:
            return Writer(self.output_path, settings=self.settings)

        if num_writers > 1:
            logger.warning("%s writers found, using only first one", num_writers)

        writer = writers[0]

        logger.debug("Found writer: %s (%s)", writer.__name__, writer.__module__)
        return writer(self.output_path, settings=self.settings)


class PrintSettings(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        init_logging(name=__name__)

        try:
            instance, settings = get_instance(namespace)
        except Exception as e:
            logger.critical("%s: %s", e.__class__.__name__, e)
            console.print_exception()
            sys.exit(getattr(e, 'exitcode', 1))

        if values:
            # One or more arguments provided, so only print those settings
            for setting in values:
                if setting in settings:
                    # Only add newline between setting name and value if dict
                    if isinstance(settings[setting], (dict, tuple, list)):
                        setting_format = '\n{}:\n{}'
                    else:
                        setting_format = '\n{}: {}'
                    console.print(setting_format.format(
                        setting,
                        pprint.pformat(settings[setting])))
                else:
                    console.print('\n{} is not a recognized setting.'.format(setting))
                    break
        else:
            # No argument was given to --print-settings, so print all settings
            console.print(settings)

        parser.exit()


class ParseDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        d = {}
        if values:
            for item in values:
                split_items = item.split("=", 1)
                key = split_items[0].strip()
                value = split_items[1].strip()
                d[key] = value
        setattr(namespace, self.dest, d)


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
                        'automatically set to {} if a file exists with this '
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

    parser.add_argument('-e', '--extra-settings', dest='overrides',
                        help='Specify one or more SETTING=VALUE pairs to '
                             'override settings. If VALUE contains spaces, '
                             'add quotes: SETTING="VALUE". Values other than '
                             'integers and strings can be specified via JSON '
                             'notation. (e.g., SETTING=none)',
                        nargs='*',
                        action=ParseDict
                        )

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
    config.update(coerce_overrides(args.overrides))

    return config


def get_instance(args):

    config_file = args.settings
    if config_file is None and os.path.isfile(DEFAULT_CONFIG_NAME):
        config_file = DEFAULT_CONFIG_NAME
        args.settings = DEFAULT_CONFIG_NAME

    settings = read_settings(config_file, override=get_config(args))

    cls = settings['PELICAN_CLASS']
    if isinstance(cls, str):
        module, cls_name = cls.rsplit('.', 1)
        module = __import__(module)
        cls = getattr(module, cls_name)

    return cls(settings), settings


def autoreload(args, excqueue=None):
    console.print('  --- AutoReload Mode: Monitoring `content`, `theme` and'
                  ' `settings` for changes. ---')
    pelican, settings = get_instance(args)
    watcher = FileSystemWatcher(args.settings, Readers, settings)
    sleep = False
    while True:
        try:
            # Don't sleep first time, but sleep afterwards to reduce cpu load
            if sleep:
                time.sleep(0.5)
            else:
                sleep = True

            modified = watcher.check()

            if modified['settings']:
                pelican, settings = get_instance(args)
                watcher.update_watchers(settings)

            if any(modified.values()):
                console.print('\n-> Modified: {}. re-generating...'.format(
                              ', '.join(k for k, v in modified.items() if v)))
                pelican.run()

        except KeyboardInterrupt:
            if excqueue is not None:
                excqueue.put(None)
                return
            raise

        except Exception as e:
            if (args.verbosity == logging.DEBUG):
                if excqueue is not None:
                    excqueue.put(
                        traceback.format_exception_only(type(e), e)[-1])
                else:
                    raise
            logger.warning(
                'Caught exception:\n"%s".', e,
                exc_info=settings.get('DEBUG', False))


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

    try:
        print("\nServing site at: http://{}:{} - Tap CTRL-C to stop".format(
            server, port))
        httpd.serve_forever()
    except Exception as e:
        if excqueue is not None:
            excqueue.put(traceback.format_exception_only(type(e), e)[-1])
        return

    except KeyboardInterrupt:
        httpd.socket.close()
        if excqueue is not None:
            return
        raise


def main(argv=None):
    args = parse_arguments(argv)
    logs_dedup_min_level = getattr(logging, args.logs_dedup_min_level)
    init_logging(level=args.verbosity, fatal=args.fatal,
                 name=__name__, logs_dedup_min_level=logs_dedup_min_level)

    logger.debug('Pelican version: %s', __version__)
    logger.debug('Python version: %s', sys.version.split()[0])

    try:
        pelican, settings = get_instance(args)

        if args.autoreload and args.listen:
            excqueue = multiprocessing.Queue()
            p1 = multiprocessing.Process(
                target=autoreload,
                args=(args, excqueue))
            p2 = multiprocessing.Process(
                target=listen,
                args=(settings.get('BIND'), settings.get('PORT'),
                      settings.get("OUTPUT_PATH"), excqueue))
            p1.start()
            p2.start()
            exc = excqueue.get()
            p1.terminate()
            p2.terminate()
            if exc is not None:
                logger.critical(exc)
        elif args.autoreload:
            autoreload(args)
        elif args.listen:
            listen(settings.get('BIND'), settings.get('PORT'),
                   settings.get("OUTPUT_PATH"))
        else:
            watcher = FileSystemWatcher(args.settings, Readers, settings)
            watcher.check()
            with console.status("Generating..."):
                pelican.run()
    except KeyboardInterrupt:
        logger.warning('Keyboard interrupt received. Exiting.')
    except Exception as e:
        logger.critical("%s: %s", e.__class__.__name__, e)

        if args.verbosity == logging.DEBUG:
            console.print_exception()
        sys.exit(getattr(e, 'exitcode', 1))
