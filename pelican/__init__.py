import argparse
import os

from pelican.settings import read_settings
from pelican.utils import clean_output_dir
from pelican.writers import Writer
from pelican.generators import (ArticlesGenerator, PagesGenerator, 
                                StaticGenerator, PdfGenerator)


def init_params(settings=None, path=None, theme=None, output_path=None, 
        markup=None):
    """Read the settings, and performs some checks on the environment
    before doing anything else.
    """
    if settings is None:
        settings = {}
    settings = read_settings(settings)
    path = path or settings['PATH']
    if path.endswith('/'):
        path = path[:-1]

    # define the default settings
    theme = theme or settings['THEME']
    output_path = output_path or settings['OUTPUT_PATH']
    output_path = os.path.realpath(output_path)
    markup = markup or settings['MARKUP']

    # find the theme in pelican.theme if the given one does not exists
    if not os.path.exists(theme):
        theme_path = os.sep.join([os.path.dirname(
            os.path.abspath(__file__)), "themes/%s" % theme])
        if os.path.exists(theme_path):
            theme = theme_path
        else:
            raise Exception("Impossible to find the theme %s" % theme)

    if 'SITEURL' not in settings:
        settings['SITEURL'] = output_path

    # get the list of files to parse
    if not path:
        raise Exception('you need to specify a path to search the docs on !')

    return settings, path, theme, output_path, markup


def run_generators(generators, settings, path, theme, output_path, markup):
    """Run the generators and return"""

    context = settings.copy()
    generators = [p(context, settings, path, theme, output_path, markup) 
            for p in generators]

    writer = Writer(output_path)

    for p in generators:
        if hasattr(p, 'generate_context'):
            p.generate_context()

    # erase the directory if it is not the source
    if output_path not in os.path.realpath(path):
        clean_output_dir(output_path)

    for p in generators:
        if hasattr(p, 'generate_output'):
            p.generate_output(writer)


def run_pelican(settings, path, theme, output_path, markup):
    """Run pelican with the given parameters"""

    params = init_params(settings, path, theme, output_path, markup)
    generators = [ArticlesGenerator, PagesGenerator, StaticGenerator]
    if params[0]['PDF_GENERATOR']:  # param[0] is settings
        processors.append(PdfGenerator)
    run_generators(generators, *params)


def main():
    parser = argparse.ArgumentParser(description="""A tool to generate a
    static blog, with restructured text input files.""")

    parser.add_argument(dest='path',
        help='Path where to find the content files')
    parser.add_argument('-t', '--theme-path', dest='theme',
        help='Path where to find the theme templates. If not specified, it will'
             'use the default one included with pelican.')
    parser.add_argument('-o', '--output', dest='output',
        help='Where to output the generated files. If not specified, a directory'
             ' will be created, named "output" in the current path.')
    parser.add_argument('-m', '--markup', default='rst, md', dest='markup',
        help='the markup language to use. Currently only ReSTreucturedtext is'
              ' available.')
    parser.add_argument('-s', '--settings', dest='settings',
        help='the settings of the application. Default to None.')
    args = parser.parse_args()
    markup = [a.split()[0] for a in args.markup.split(',')]

    run_pelican(args.settings, args.path, args.theme, args.output, markup)


if __name__ == '__main__':
    main()
