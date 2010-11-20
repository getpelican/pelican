# -*- coding: utf-8 -*-
import os
from codecs import open

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from feedgenerator import Atom1Feed

from pelican.settings import read_settings
from pelican.utils import clean_output_dir

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives', 'page')


class Generator(object):
    """Handle all generation process: files writes, feed creation, and this
    kind of basic stuff"""

    def __init__(self, settings=None, path=None, theme=None, output_path=None,
        markup=None):
        """Read the settings, and performs some checks on the environement
        before doing anything else.
        """
        if settings is None:
            settings = {}
        self.settings = read_settings(settings)
        self.path = path or self.settings['PATH']
        if self.path.endswith('/'):
            self.path = self.path[:-1]

        self.theme = theme or self.settings['THEME']
        output_path = output_path or self.settings['OUTPUT_PATH']
        self.output_path = os.path.realpath(output_path)
        self.markup = markup or self.settings['MARKUP']

        if not os.path.exists(self.theme):
            theme_path = os.sep.join([os.path.dirname(
                os.path.abspath(__file__)), "themes/%s" % self.theme])
            if os.path.exists(theme_path):
                self.theme = theme_path
            else:
                raise Exception("Impossible to find the theme %s" % self.theme)

        if 'SITEURL' not in self.settings:
            self.settings['SITEURL'] = self.output_path

        # get the list of files to parse
        if not path:
            raise Exception('you need to specify a path to search the docs on !')

    def run(self, processors):
        """Get the context from each processor, and then process them"""
        context = self.settings.copy()
        processors = [p() for p in processors]

        for p in processors:
            if hasattr(p, 'preprocess'):
                p.preprocess(context, self)

        if self.output_path not in os.path.realpath(self.path):
            clean_output_dir(self.output_path)

        for p in processors:
            p.process(context, self)

    def generate_feed(self, elements, context, filename=None):
        """Generate a feed with the list of articles provided

        Return the feed. If no output_path or filename is specified, just return
        the feed object.

        :param articles: the articles to put on the feed.
        :param context: the context to get the feed metadatas.
        :param output_path: where to output the file.
        :param filename: the filename to output.
        """
        feed = Atom1Feed(
            title=context['SITENAME'],
            link=context['SITEURL'],
            feed_url='%s/%s' % (context['SITEURL'], filename),
            description=context.get('SITESUBTITLE', ''))
        for element in elements:
            feed.add_item(
                title=element.title,
                link='%s/%s' % (context['SITEURL'], element.url),
                description=element.content,
                author_name=getattr(element, 'author', 'John Doe'),
                pubdate=element.date)

        if filename:
            complete_path = os.path.join(self.output_path, filename)
            try:
                os.makedirs(os.path.dirname(complete_path))
            except Exception:
                pass
            fp = open(complete_path, 'w')
            feed.write(fp, 'utf-8')
            print u' [ok] writing %s' % complete_path

            fp.close()
        return feed

    def generate_file(self, name, template, context, **kwargs):
        """Write the file with the given informations

        :param name: name of the file to output
        :param template: template to use to generate the content
        :param context: dict to pass to the templates.
        :param **kwargs: additional variables to pass to the templates
        """
        context = context.copy()
        context.update(kwargs)
        output = template.render(context)
        filename = os.sep.join((self.output_path, name))
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception:
            pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print u' [ok] writing %s' % filename

    def get_templates(self):
        """Return the templates to use.
        Use self.theme to get the templates to use, and return a list of
        templates ready to use with Jinja2.
        """
        path = os.path.expanduser(os.path.join(self.theme, 'templates'))
        env = Environment(loader=FileSystemLoader(path))
        templates = {}
        for template in _TEMPLATES:
            try:
                templates[template] = env.get_template('%s.html' % template)
            except TemplateNotFound:
                raise Exception('[templates] unable to load %s.html from %s' % (
                    template, path))
        return templates

    def get_files(self, path, exclude=[], extensions=None):
        """Return a list of files to use, based on rules

        :param path: the path to search the file on
        :param exclude: the list of path to exclude
        """
        if not extensions:
            extensions = self.markup

        files = []
        for root, dirs, temp_files in os.walk(path, followlinks=True):
            for e in exclude:
                if e in dirs:
                    dirs.remove(e)
            files.extend([os.sep.join((root, f)) for f in temp_files
                if True in [f.endswith(ext) for ext in extensions]])
        return files
