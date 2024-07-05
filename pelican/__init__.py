"""
Pelican - Extensible Static Site Generator, with plugin support.

Pelican is a static site generator, written in Python, that allows
you to create websites by composing text files in formats such as
Markdown, reStructuredText, and HTML.

With Pelican, you can create websites without worrying about
databases or server-side programming. Pelican generates static sites
that can be served via any web server or hosting service.

You can perform the following functions with Pelican:

*  Compose content in Markdown or reStructuredText using your
   editor of choice
*  Simple command-line tool (re)generates HTML, CSS, and JS from your
   source content
*  Easy to interface with version control systems and web hooks
*  Completely static output is simple to host anywhere

Pelican features main highlights include:

*  Chronological content (e.g., articles, blog posts) as
   well as static pages
*  Integration with external services
*  Site themes (created using Jinja2 templates)
*  Publication of articles in multiple languages
*  Generation of Atom and RSS feeds
*  Code syntax highlighting via Pygments
*  Import existing content from WordPress, Dotclear, or RSS feeds
*  Fast rebuild times due to content caching and selective output writing
*  Extensible via a rich plugin ecosystem: Pelican Plugins

URL: https://github.com/getpelican/pelican
Git Repo: https://github.com/getpelican/pelican.git
Issues: https://github.com/getpelican/pelican/issues
Wiki: https://github.com/getpelican/pelican/wiki
ReadTheDocs: https://docs.getpelican.com/en/latest/
Discussion: https://github.com/getpelican/pelican/discussions
"""

import argparse
import importlib.metadata
import json
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
from pelican.log import console, DEFAULT_LOG_HANDLER  # noqa: I001
from pelican.log import init as init_logging
from pelican.generators import (
    ArticlesGenerator,
    PagesGenerator,
    SourceFileGenerator,
    StaticGenerator,
    TemplatePagesGenerator,
)
from pelican.plugins import signals
from pelican.plugins._utils import get_plugin_name, load_plugins
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import read_settings
from pelican.utils import clean_output_dir, maybe_pluralize, wait_for_changes
from pelican.writers import Writer

try:
    __version__ = importlib.metadata.version("pelican")
except Exception:
    __version__ = "unknown"

DEFAULT_CONFIG_NAME = "pelicanconf.py"
logger = logging.getLogger(__name__)


class Pelican:
    def __init__(self, settings):
        """Pelican initialization

        Performs the following steps:
           * obtain configuration file (-c), import its settings
           * supply missing configuration settings
           * update/delete any legacy settings
           * normalize any relative paths into absolute path
           * validate values of static current settings
           * check for valid file access on filespec-related settings
           * check for valid directory access on dirpath-related settings
           * find all the plugins (PLUGIN_PATH)
           * register and initialize each desired plugins (PLUGINS)
           * sends signals.initilized and let all participating plugins know

        :param self: Pelican configuration settings
        :type self: Settings
        """
        # define the default settings
        self.settings = settings

        self.path = settings["PATH"]
        self.theme = settings["THEME"]
        self.output_path = settings["OUTPUT_PATH"]
        self.ignore_files = settings["IGNORE_FILES"]
        self.delete_outputdir = settings["DELETE_OUTPUT_DIRECTORY"]
        self.output_retention = settings["OUTPUT_RETENTION"]

        self.init_path()
        self.init_plugins()
        signals.initialized.send(self)

    def init_path(self):
        """Add a path to Python system module search path, if missing.

        :param self: implicit Pelican class scope
        :type self: class
        """
        if not any(p in sys.path for p in ["", os.curdir]):
            logger.debug("Adding current directory to system path")
            sys.path.insert(0, "")

    def init_plugins(self):
        """Add all desired plugins, then initialize each

        :param self: implicit Pelican class scope
        :type self: class
        :return: None
        :raises Exception: any exception error
        """
        self.plugins = []
        for plugin in load_plugins(self.settings):
            name = get_plugin_name(plugin)
            logger.debug("Registering plugin `%s`", name)
            try:
                plugin.register()
                self.plugins.append(plugin)
            except Exception as e:
                logger.error(
                    "Cannot register plugin `%s`\n%s",
                    name,
                    e,
                    stacklevel=2,
                )
                if self.settings.get("DEBUG", False):
                    console.print_exception()

        self.settings["PLUGINS"] = [get_plugin_name(p) for p in self.plugins]

    def run(self):
        """Runs the Pelican generator

        Copies the current settings to this Pelican class context.

        Iterate each of the following subclasses of Content class
        for its Pelican module availability:

        * ArticlesGenerator
        * PagesGenerator
        * StaticGenerator

        Deletes the OUTPUT_PATH (`output/`) directory, if CLI
        option -d is supplied

        Iterate over each subclasses of Content class for:
        * being given with its current Pelican context
        * not having its reader disabled

        Sends signals.all_generators_finalized to all participating plugins.

        Iterate over each subclasses of Content class for:
        * Update the links between summaries
        * update metadata and make available to all contents

        Determine which writer to use (HTML, AsciiDoc, ...)

        :param self: implicit Pelican class scope
        :type self: class
        :return: None
        """
        start_time = time.time()

        context = self.settings.copy()
        # Share these among all the generators and content objects
        # They map source paths to Content objects or None
        context["generated_content"] = {}
        context["static_links"] = set()
        context["static_content"] = {}
        context["localsiteurl"] = self.settings["SITEURL"]

        generators = [
            cls(
                context=context,
                settings=self.settings,
                path=self.path,
                theme=self.theme,
                output_path=self.output_path,
            )
            for cls in self._get_generator_classes()
        ]

        # Delete the output directory if (1) the appropriate setting is True
        # and (2) that directory is not the parent of the source directory
        if self.delete_outputdir and os.path.commonpath(
            [os.path.realpath(self.output_path)]
        ) != os.path.commonpath(
            [os.path.realpath(self.output_path), os.path.realpath(self.path)]
        ):
            clean_output_dir(self.output_path, self.output_retention)

        for p in generators:
            if hasattr(p, "generate_context"):
                p.generate_context()
            if hasattr(p, "check_disabled_readers"):
                p.check_disabled_readers()

        # for plugins that create/edit the summary
        logger.debug("Signal all_generators_finalized.send(<generators>)")
        signals.all_generators_finalized.send(generators)

        # update links in the summary, etc
        for p in generators:
            if hasattr(p, "refresh_metadata_intersite_links"):
                p.refresh_metadata_intersite_links()

        writer = self._get_writer()

        for p in generators:
            if hasattr(p, "generate_output"):
                p.generate_output(writer)

        signals.finalized.send(self)

        articles_generator = next(
            g for g in generators if isinstance(g, ArticlesGenerator)
        )
        pages_generator = next(g for g in generators if isinstance(g, PagesGenerator))

        pluralized_articles = maybe_pluralize(
            (len(articles_generator.articles) + len(articles_generator.translations)),
            "article",
            "articles",
        )
        pluralized_drafts = maybe_pluralize(
            (
                len(articles_generator.drafts)
                + len(articles_generator.drafts_translations)
            ),
            "draft",
            "drafts",
        )
        pluralized_hidden_articles = maybe_pluralize(
            (
                len(articles_generator.hidden_articles)
                + len(articles_generator.hidden_translations)
            ),
            "hidden article",
            "hidden articles",
        )
        pluralized_pages = maybe_pluralize(
            (len(pages_generator.pages) + len(pages_generator.translations)),
            "page",
            "pages",
        )
        pluralized_hidden_pages = maybe_pluralize(
            (
                len(pages_generator.hidden_pages)
                + len(pages_generator.hidden_translations)
            ),
            "hidden page",
            "hidden pages",
        )
        pluralized_draft_pages = maybe_pluralize(
            (
                len(pages_generator.draft_pages)
                + len(pages_generator.draft_translations)
            ),
            "draft page",
            "draft pages",
        )

        console.print(
            f"Done: Processed {pluralized_articles}, {pluralized_drafts}, {pluralized_hidden_articles}, {pluralized_pages}, {pluralized_hidden_pages} and {pluralized_draft_pages} in {time.time() - start_time:.2f} seconds."
        )

    def _get_generator_classes(self):
        """
        Compile a list of generators

        Collect all the internal generators as well as any
        external generators (might be supplied by plugins)

        Such internal generators are but not limited to:

        * ArticlesGenerator()
        * PagesGenerator()
        * StaticGenerator()
        * TemplatePagesGenerator() (`TEMPLATE_PAGES`)
        * SourceFileGenerator()  (`OUTPUT_SOURCES`)

        And any external generator that might be supplied by
        any participating plugins (`PLUGINS`).

        :param self: implicit Pelican class scope
        :type self: class
        :return: generator
        :rtype: list
        """
        discovered_generators = [
            (ArticlesGenerator, "internal"),
            (PagesGenerator, "internal"),
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
        """
        Get a list of "approved" writer

        :param self: implicit Pelican class scope
        :type self: class
        :return: generator
        :rtype: list
        """
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
    """
    Printing out the current settings
    """

    def __call__(self, parser, namespace, values, option_string):
        """
        Get a list of "approved" writer

        :param self: implicit PrintingSettings class scope
        :type self: class
        :param parser:
        :type parser:
        :param namespace: an argument list supplied by CLI
        :type namespace: Namespace class
        :param values: a list of keyword/keyvalues
        :type values: list
        :param option_string: Unused
        :type option_string: list
        :return: generator
        :rtype: list
        :raises Exception: any exception error
        """
        init_logging(name=__name__)

        try:
            instance, settings = get_instance(namespace)
        except Exception as e:
            logger.critical("%s: %s", e.__class__.__name__, e)
            console.print_exception()
            sys.exit(getattr(e, "exitcode", 1))

        if values:
            # One or more arguments provided, so only print those settings
            for setting in values:
                if setting in settings:
                    # Only add newline between setting name and value if dict
                    if isinstance(settings[setting], (dict, tuple, list)):
                        setting_format = "\n{}:\n{}"
                    else:
                        setting_format = "\n{}: {}"
                    console.print(
                        setting_format.format(
                            setting, pprint.pformat(settings[setting])
                        )
                    )
                else:
                    console.print(f"\n{setting} is not a recognized setting.")
                    break
        else:
            # No argument was given to --print-settings, so print all settings
            console.print(settings)

        parser.exit()


class ParseOverrides(argparse.Action):
    """
    Overrides certain CLI argument options
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Get a list of "approved" writer

        :param self: implicit PrintingSettings class scope
        :type self: class
        :param parser:
        :type parser:
        :param namespace: an argument list supplied by CLI
        :type namespace: list args[]
        :param values: a list of keyword/keyvalues
        :type values: list
        :param option_string: Unused
        :type option_string: list
        :return: generator
        :rtype: list
        :raises ValueError: Raised when an operation or function receives
                            an argument that has the right type but an
                            inappropriate value, and the situation is not
                            described by a more precise exception such as
                            IndexError.
        """
        overrides = {}
        for item in values:
            try:
                k, v = item.split("=", 1)
            except ValueError:
                raise ValueError(
                    "Extra settings must be specified as KEY=VALUE pairs "
                    f"but you specified {item}"
                ) from None
            try:
                overrides[k] = json.loads(v)
            except json.decoder.JSONDecodeError:
                raise ValueError(
                    f"Invalid JSON value: {v}. "
                    "Values specified via -e / --extra-settings flags "
                    "must be in JSON notation. "
                    "Use -e KEY='\"string\"' to specify a string value; "
                    "-e KEY=null to specify None; "
                    "-e KEY=false (or true) to specify False (or True)."
                ) from None
        setattr(namespace, self.dest, overrides)


def parse_arguments(argv=None):
    """
    Received the argv list, check each arguments, each options and
    its option argument(s) from the command line (CLI),
    make any necessary adjustment then return it back to
    the caller this new argv list.

    :param argv: the CLI arguments provided by the main routine.
    :type argv: list
    :return: the argv which may have been modified
    :rtype: list
    """
    parser = argparse.ArgumentParser(
        description="A tool to generate a static blog, "
        " with restructured text input files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        dest="path",
        nargs="?",
        help="Path where to find the content files.",
        default=None,
    )

    parser.add_argument(
        "-t",
        "--theme-path",
        dest="theme",
        help="Path where to find the theme templates. If not "
        "specified, it will use the default one included with "
        "pelican.",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="Where to output the generated files. If not "
        "specified, a directory will be created, named "
        '"output" in the current path.',
    )

    parser.add_argument(
        "-s",
        "--settings",
        dest="settings",
        help="The settings of the application, this is "
        f"automatically set to {DEFAULT_CONFIG_NAME} if a file exists with this "
        "name.",
    )

    parser.add_argument(
        "-d",
        "--delete-output-directory",
        dest="delete_outputdir",
        action="store_true",
        default=None,
        help="Delete the output directory.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="verbosity",
        help="Show all messages.",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.CRITICAL,
        dest="verbosity",
        help="Show only critical errors.",
    )

    parser.add_argument(
        "-D",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="verbosity",
        help="Show all messages, including debug messages.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print the pelican version and exit.",
    )

    parser.add_argument(
        "-r",
        "--autoreload",
        dest="autoreload",
        action="store_true",
        help="Relaunch pelican each time a modification occurs"
        " on the content files.",
    )

    parser.add_argument(
        "--print-settings",
        dest="print_settings",
        nargs="*",
        action=PrintSettings,
        metavar="SETTING_NAME",
        help="Print current configuration settings and exit. "
        "Append one or more setting name arguments to see the "
        "values for specific settings only.",
    )

    parser.add_argument(
        "--relative-urls",
        dest="relative_paths",
        action="store_true",
        help="Use relative urls in output, useful for site development",
    )

    parser.add_argument(
        "--cache-path",
        dest="cache_path",
        help=(
            "Directory in which to store cache files. "
            'If not specified, defaults to "cache".'
        ),
    )

    parser.add_argument(
        "--ignore-cache",
        action="store_true",
        dest="ignore_cache",
        help="Ignore content cache from previous runs by not loading cache files.",
    )

    parser.add_argument(
        "--fatal",
        metavar="errors|warnings",
        choices=("errors", "warnings"),
        default="",
        help=(
            "Exit the program with non-zero status if any "
            "errors/warnings encountered."
        ),
    )

    LOG_HANDLERS = {"plain": None, "rich": DEFAULT_LOG_HANDLER}
    parser.add_argument(
        "--log-handler",
        default="rich",
        choices=LOG_HANDLERS,
        help=(
            "Which handler to use to format log messages. "
            "The `rich` handler prints output in columns."
        ),
    )

    parser.add_argument(
        "--logs-dedup-min-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help=(
            "Only enable log de-duplication for levels equal"
            " to or above the specified value"
        ),
    )

    parser.add_argument(
        "-l",
        "--listen",
        dest="listen",
        action="store_true",
        help="Serve content files via HTTP and port 8000.",
    )

    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        help="Port to serve HTTP files at. (default: 8000)",
    )

    parser.add_argument(
        "-b",
        "--bind",
        dest="bind",
        help="IP to bind to when serving files via HTTP (default: 127.0.0.1)",
    )

    parser.add_argument(
        "-e",
        "--extra-settings",
        dest="overrides",
        help="Specify one or more SETTING=VALUE pairs to "
        "override settings. VALUE must be in JSON notation: "
        "specify string values as SETTING='\"some string\"'; "
        "booleans as SETTING=true or SETTING=false; "
        "None as SETTING=null.",
        nargs="*",
        action=ParseOverrides,
        default={},
    )

    args = parser.parse_args(argv)

    if args.port is not None and not args.listen:
        logger.warning("--port without --listen has no effect")
    if args.bind is not None and not args.listen:
        logger.warning("--bind without --listen has no effect")

    args.log_handler = LOG_HANDLERS[args.log_handler]

    return args


def get_config(args):
    """
    Builds a config dictionary based on supplied `args`.

    Of the mandatory minimum settings requires, fill in the blank
    ones from the supplied Pelican settings list in args.

    :param args: the provided CLI arguments.
    :type args: list
    :return: the entire working Pelican configuration settings
    :rtype: dict
    """
    config = {}
    if args.path:
        config["PATH"] = os.path.abspath(os.path.expanduser(args.path))
    if args.output:
        config["OUTPUT_PATH"] = os.path.abspath(os.path.expanduser(args.output))
    if args.theme:
        abstheme = os.path.abspath(os.path.expanduser(args.theme))
        config["THEME"] = abstheme if os.path.exists(abstheme) else args.theme
    if args.delete_outputdir is not None:
        config["DELETE_OUTPUT_DIRECTORY"] = args.delete_outputdir
    if args.ignore_cache:
        config["LOAD_CONTENT_CACHE"] = False
    if args.cache_path:
        config["CACHE_PATH"] = args.cache_path
    if args.relative_paths:
        config["RELATIVE_URLS"] = args.relative_paths
    if args.port is not None:
        config["PORT"] = args.port
    if args.bind is not None:
        config["BIND"] = args.bind
    config["DEBUG"] = args.verbosity == logging.DEBUG
    config.update(args.overrides)

    return config


def get_instance(args):
    """
    Determine its Pelican class

    :param args: the CLI arguments provided by the main routine.
    :type args: list
    :return: the entire working Pelican configuration settings
    :rtype: class, list
    """
    config_file = args.settings
    if config_file is None and os.path.isfile(DEFAULT_CONFIG_NAME):
        config_file = DEFAULT_CONFIG_NAME
        args.settings = DEFAULT_CONFIG_NAME

    settings = read_settings(config_file, override=get_config(args))

    cls = settings["PELICAN_CLASS"]
    if isinstance(cls, str):
        module, cls_name = cls.rsplit(".", 1)
        module = __import__(module)
        cls = getattr(module, cls_name)

    return cls(settings), settings


def autoreload(args, excqueue=None):
    """
    Runs Pelican generator, while taking in any updated settings LIVE.

    Useful if running in server mode where changes can be
    made to its setting file and not have to restart the
    server?

    :param args: the CLI arguments provided by the main routine.
    :type args: list
    :param excqueue:  A method having a .put() function.
    :type excqueue: method
    :return: None
    :raises KeyboardInterrupt: Raised when the user hits the interrupt
            key (normally Control-C or Delete).
    :raises Exception: any exception error
    """
    console.print(
        "  --- AutoReload Mode: Monitoring `content`, `theme` and"
        " `settings` for changes. ---"
    )
    pelican, settings = get_instance(args)
    settings_file = os.path.abspath(args.settings)
    while True:
        try:
            pelican.run()

            changed_files = wait_for_changes(args.settings, settings)
            changed_files = {c[1] for c in changed_files}

            if settings_file in changed_files:
                pelican, settings = get_instance(args)

            console.print(
                "\n-> Modified: {}. re-generating...".format(", ".join(changed_files))
            )

        except KeyboardInterrupt:
            if excqueue is not None:
                excqueue.put(None)
                return
            raise

        except Exception as e:
            if args.verbosity == logging.DEBUG:
                if excqueue is not None:
                    excqueue.put(traceback.format_exception_only(type(e), e)[-1])
                else:
                    raise
            logger.warning(
                'Caught exception:\n"%s".', e, exc_info=settings.get("DEBUG", False)
            )


def listen(server, port, output, excqueue=None):
    """
    Listen on a port and dish out any HTML stuff, a web server

    :param server: this server name, in either a domain name or an
                   IP address (`BIND`)
    :type server: str
    :param port: port number to listen on. (`PORT`)
    :type port: str
    :param output: the CLI arguments provided by the main
                   routine (`OUTPUT_PATH`)
    :type output: str
    :param excqueue: Function of execution queue handler to use
    :type excqueue: Method
    :return: None
    :raises OSError: returns a system-related error, including I/O failures
            such as “file not found” or “disk full”
    :raises KeyboardInterrupt: Raised when the user hits the interrupt
            key (normally Control-C or Delete).
    :raises Exception: any exception error
    """
    # set logging level to at least "INFO" (so we can see the server requests)
    if logger.level < logging.INFO:
        logger.setLevel(logging.INFO)

    RootedHTTPServer.allow_reuse_address = True
    try:
        httpd = RootedHTTPServer(output, (server, port), ComplexHTTPRequestHandler)
    except OSError as e:
        logging.error("Could not listen on port %s, server %s.", port, server)
        if excqueue is not None:
            excqueue.put(traceback.format_exception_only(type(e), e)[-1])
        return

    try:
        console.print(f"Serving site at: http://{server}:{port} - Tap CTRL-C to stop")
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
    """
    Pelican's main routine

    :param argv: this server name, in either a domain name or an IP address (`BIND`)
    :type server: str
    :return: int
    :raises KeyboardInterrupt: Raised when the user hits the interrupt
            key (normally Control-C or Delete).
    :raises Exception: any exception error
    """
    args = parse_arguments(argv)
    logs_dedup_min_level = getattr(logging, args.logs_dedup_min_level)
    init_logging(
        level=args.verbosity,
        fatal=args.fatal,
        name=__name__,
        handler=args.log_handler,
        logs_dedup_min_level=logs_dedup_min_level,
    )

    logger.debug("Pelican version: %s", __version__)
    logger.debug("Python version: %s", sys.version.split()[0])

    try:
        pelican, settings = get_instance(args)

        if args.autoreload and args.listen:
            excqueue = multiprocessing.Queue()
            p1 = multiprocessing.Process(target=autoreload, args=(args, excqueue))
            p2 = multiprocessing.Process(
                target=listen,
                args=(
                    settings.get("BIND"),
                    settings.get("PORT"),
                    settings.get("OUTPUT_PATH"),
                    excqueue,
                ),
            )
            try:
                p1.start()
                p2.start()
                exc = excqueue.get()
                if exc is not None:
                    logger.critical(exc)
            finally:
                p1.terminate()
                p2.terminate()
        elif args.autoreload:
            autoreload(args)
        elif args.listen:
            listen(
                settings.get("BIND"), settings.get("PORT"), settings.get("OUTPUT_PATH")
            )
        else:
            with console.status("Generating..."):
                pelican.run()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received. Exiting.")
    except Exception as e:
        logger.critical("%s: %s", e.__class__.__name__, e)

        if args.verbosity == logging.DEBUG:
            console.print_exception()
        sys.exit(getattr(e, "exitcode", 1))
