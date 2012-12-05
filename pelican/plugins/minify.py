"""A plugin which minifies your HTML page output."""


from logging import getLogger
from os import walk
from os.path import join

from htmlmin.minify import html_minify
from pelican import signals


logger = getLogger(__name__)


def minify_html(pelican):
    """Minify all HTML files.

    :param pelican: The Pelican instance.
    """
    for dirpath, _, filenames in walk(pelican.settings['OUTPUT_PATH']):
        for name in filenames:
            if name.endswith('.html'):
                filepath = join(dirpath, name)
                create_minified_file(filepath)


def create_minified_file(filename):
    """Create a minified HTML file, overwriting the original.

    :param str filename: The file to minify.
    """
    uncompressed = open(filename).read()
    with open(filename, 'wb') as f:
        try:
            logger.debug('Minifying: %s' % filename)
            compressed = html_minify(uncompressed)
            f.write(compressed)
        except Exception, ex:
            logger.critical('HTML Minification failed: %s' % ex)
        finally:
            f.close()


def register():
    """Run the HTML minification stuff after all articles have been generated,
    at the very end of the processing loop.
    """
    signals.finalized.connect(minify_html)
