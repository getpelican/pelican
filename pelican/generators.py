# -*- coding: utf-8 -*-
import os
from codecs import open

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from feedgenerator import Atom1Feed

from pelican.settings import read_settings

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives', 'page')


class Generator(object):
    """Base class generator"""
    
    def __init__(self, settings=None, path=None, theme=None, output_path=None, 
        markup=None):
        if settings is None:
            settings = {}
        self.settings = read_settings(settings)
        self.path = path or self.settings['PATH']
        self.theme = theme or self.settings['THEME']
        output_path = output_path or self.settings['OUTPUT_PATH']
        self.output_path = os.path.realpath(output_path)
        self.markup = markup or self.settings['MARKUP']

        if 'SITEURL' not in self.settings:
            self.settings['SITEURL'] = self.output_path

        # get the list of files to parse
        if not path:
            raise Exception('you need to specify a path to search the docs on !')

    def run(self, processors):
        context = self.settings.copy()
        processors = [p() for p in processors]

        for p in processors:
            if hasattr(p, 'preprocess'):
                p.preprocess(context, self)

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

        :param path: the path to load the templates from
        """
        path = os.path.expanduser(os.path.join(self.theme, 'templates'))
        env = Environment(loader=FileSystemLoader(path))
        templates = {}
        for template in _TEMPLATES:
            try:
                templates[template] = env.get_template('%s.html' % template)
            except TemplateNotFound:
                raise Exception('Unable to load %s.html from %s' % (
                    template, path))
        return templates

    def get_files(self, path, exclude=[]):
        """Return the files to use to use in this generator

        :param path: the path to search the file on
        :param exclude: the list of path to exclude
        """
        files = []
        for root, dirs, temp_files in os.walk(path, followlinks=True):
            for e in exclude:
                if e in dirs:
                    dirs.remove(e)
            files.extend([os.sep.join((root, f)) for f in temp_files
                if True in [f.endswith(markup) for markup in self.markup]])
        return files
