import argparse
import os
import time

from pelican.generators import (ArticlesGenerator, PagesGenerator,
        StaticGenerator, PdfGenerator)
from pelican.settings import read_settings
from pelican.utils import clean_output_dir, files_changed
from pelican.writers import Writer
from pelican import log

VERSION = "2.7.0"


class Pelican(object):
    def __init__(self, settings=None, path=None, theme=None, output_path=None,
            markup=None, delete_outputdir=False):
        """Read the settings, and performs some checks on the environment
        before doing anything else.
        """
        self.path = path or settings['PATH']
        if not self.path:
            raise Exception('you need to specify a path containing the content'
                    ' (see pelican --help for more information)')

        if self.path.endswith('/'):
            self.path = path[:-1]

        # define the default settings
        self.settings = settings
        self.theme = theme or settings['THEME']
        output_path = output_path or settings['OUTPUT_PATH']
        self.output_path = os.path.realpath(output_path)
        self.markup = markup or settings['MARKUP']
        self.delete_outputdir = delete_outputdir or settings['DELETE_OUTPUT_DIRECTORY']

        # find the theme in pelican.theme if the given one does not exists
        if not os.path.exists(self.theme):
            theme_path = os.sep.join([os.path.dirname(
                os.path.abspath(__file__)), "themes/%s" % self.theme])
            if os.path.exists(theme_path):
                self.theme = theme_path
            else:
                raise Exception("Impossible to find the theme %s" % theme)

    def run(self):
        """Run the generators and return"""

        context = self.settings.copy()
        generators = [
            cls(
                context,
                self.settings,
                self.path,
                self.theme,
                self.output_path,
                self.markup,
                self.delete_outputdir
            ) for cls in self.get_generator_classes()
        ]

        for p in generators:
            if hasattr(p, 'generate_context'):
                p.generate_context()

        # erase the directory if it is not the source and if that's 
        # explicitely asked
        if (self.delete_outputdir and 
                os.path.realpath(self.path).startswith(self.output_path)):
            clean_output_dir(self.output_path)

        writer = self.get_writer()

        for p in generators:
            if hasattr(p, 'generate_output'):
                p.generate_output(writer)


    def get_generator_classes(self):
        generators = [ArticlesGenerator, PagesGenerator, StaticGenerator]
        if self.settings['PDF_GENERATOR']:
            generators.append(PdfGenerator)
        return generators

    def get_writer(self):
        return Writer(self.output_path, settings=self.settings)



def main():
    parser = argparse.ArgumentParser(description="""A tool to generate a
    static blog, with restructured text input files.""")

    parser.add_argument(dest='path', nargs='?',
        help='Path where to find the content files')
    parser.add_argument('-t', '--theme-path', dest='theme',
        help='Path where to find the theme templates. If not specified, it'
             'will use the default one included with pelican.')
    parser.add_argument('-o', '--output', dest='output',
        help='Where to output the generated files. If not specified, a directory'
             ' will be created, named "output" in the current path.')
    parser.add_argument('-m', '--markup', default=None, dest='markup',
        help='the list of markup language to use (rst or md). Please indicate '
             'them separated by commas')
    parser.add_argument('-s', '--settings', dest='settings',
        help='the settings of the application. Default to False.')
    parser.add_argument('-d', '--delete-output-directory', dest='delete_outputdir',
        action='store_true', help='Delete the output directory.')
    parser.add_argument('-v', '--verbose', action='store_const', const=log.INFO, dest='verbosity',
            help='Show all messages')
    parser.add_argument('-q', '--quiet', action='store_const', const=log.CRITICAL, dest='verbosity',
            help='Show only critical errors')
    parser.add_argument('-D', '--debug', action='store_const', const=log.DEBUG, dest='verbosity',
            help='Show all message, including debug messages')
    parser.add_argument('--version', action='version', version=VERSION,
            help='Print the pelican version and exit')
    parser.add_argument('-r', '--autoreload', dest='autoreload', action='store_true',
            help="Relaunch pelican each time a modification occurs on the content"
                 "files")
    args = parser.parse_args()

    log.init(args.verbosity)
    # Split the markup languages only if some have been given. Otherwise, populate
    # the variable with None.
    markup = [a.strip().lower() for a in args.markup.split(',')] if args.markup else None

    if args.settings is None:
        settings = {}
    settings = read_settings(args.settings)

    cls = settings.get('PELICAN_CLASS')
    if isinstance(cls, basestring):
        module, cls_name = cls.rsplit('.', 1)
        module = __import__(module)
        cls = getattr(module, cls_name)

    try:
        pelican = cls(settings, args.path, args.theme, args.output, markup,
                args.delete_outputdir)
        if args.autoreload:
            while True:
                try:
                    # Check source dir for changed files ending with the given
                    # extension in the settings. In the theme dir is no such
                    # restriction; all files are recursively checked if they
                    # have changed, no matter what extension the filenames
                    # have.
                    if files_changed(pelican.path, pelican.markup) or \
                            files_changed(pelican.theme, ['']):
                        pelican.run()
                    time.sleep(.5)  # sleep to avoid cpu load
                except KeyboardInterrupt:
                    break
        else:
            pelican.run()
    except Exception, e:
        log.critical(str(e))


if __name__ == '__main__':
    main()
