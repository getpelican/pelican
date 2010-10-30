# -*- coding: utf-8 -*-
import os
import shutil
from codecs import open
from operator import attrgetter

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from feedgenerator import Atom1Feed

from pelican.utils import update_dict
from pelican.settings import read_settings
from pelican.contents import Article
from pelican.readers import read_file

## Constants ##########################################################

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives')

_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')


class Generator(object):
    """Base class generator"""
    
    def __init__(self, settings):
        self.settings = read_settings(settings)
    
    def _init_params(self, path=None, theme=None, output_path=None, fmt=None):
        """Initialize parameters for this object.

        :param path: the path where to find the files to parse
        :param theme: where to search for templates
        :param output_path: where to output the generated files
        :param settings: the settings file to use
        :param fmt: the format of the files to read. It's a list.
        """
        # get the settings
        self.path = path or self.settings['PATH']
        self.theme = theme or self.settings['THEME']
        output_path = output_path or self.settings['OUTPUT_PATH']
        self.output_path = os.path.realpath(output_path)
        self.format = fmt or self.settings['FORMAT']

        # get the list of files to parse
        if not path:
            raise Exception('you need to specify a path to search the docs on !')

    def generate_feed(self, elements, context, output_path=None, filename=None):
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

        if output_path and filename:
            complete_path = os.path.join(output_path, filename)
            try:
                os.makedirs(os.path.dirname(complete_path))
            except Exception:
                pass
            fp = open(complete_path, 'w')
            feed.write(fp, 'utf-8')
            print u' ✔ writing %s' % complete_path
            
            fp.close()
        return feed

    def generate_file(self, name, template, context, **kwargs):
        """Write the file with the given informations

        :param name: name of the file to output
        :param template: template to use to generate the content
        :param context: dict to pass to the templates.
        :param **kwargs: additional variables to pass to the templates
        """
        context.update(kwargs)
        output = template.render(context)
        filename = os.sep.join((self.output_path, name))
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception:
            pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print u' ✔ writing %s' % filename

    def get_templates(self, path=None):
        """Return the templates to use.

        :param path: the path to load the templates from
        """
        path = os.path.expanduser(os.path.join(path, 'templates'))
        env = Environment(loader=FileSystemLoader(path))
        templates = {}
        for template in _TEMPLATES:
            try:
                templates[template] = env.get_template('%s.html' % template)
            except TemplateNotFound:
                raise Exception('Unable to load %s.html from %s' % (
                    template, path))
        return templates

    def clean_output_dir(self):
        """Remove all the files from the output directory"""

        # remove all the existing content from the output folder
        try:
            shutil.rmtree(os.path.join(self.output_path))
        except:
            pass

    
class ArticlesGenerator(Generator):

    def __init__(self, settings=None):
        super(ArticlesGenerator, self).__init__(settings)
        self.articles = [] 
        self.dates = {}
        self.years = {}
        self.tags = {}
        self.categories = {} 
        
    def get_files(self, path):
        """Return the files to use to use in this generator"""
        files = []
        for root, dirs, temp_files in os.walk(path, followlinks=True):
            files.extend([os.sep.join((root, f)) for f in temp_files
                if f.endswith(self.format)])
        return files

    def process_files(self, files):
        """Process all the files and build the lists and dicts of
        articles/categories/etc.
        """
        for f in files:
            content, metadatas = read_file(f)
            if 'category' not in metadatas.keys():
                category = os.path.dirname(f).replace(
                    os.path.expanduser(self.path)+'/', '')

                if category != '':
                    metadatas['category'] = unicode(category)

            article = Article(content, metadatas, settings=self.settings)
            try:
                article.check_properties()
            except NameError as e:
                print u" ☓ Skipping %s: impossible to find informations about '%s'" % (f, e)
                continue

            update_dict(self.dates, article.date.strftime('%Y-%m-%d'), article)
            update_dict(self.years, article.date.year, article)
            update_dict(self.categories, article.category, article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    update_dict(self.tags, tag, article)
            self.articles.append(article)

    def _get_context(self):
        """Return the context to be used in templates"""

        context = self.settings.copy()
        # put all we need in the context, to generate the output
        for item in ('articles', 'dates', 'years', 'tags', 'categories'):
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = value.items()
            context[item] = value
        return context

    def generate_feeds(self, context):
        """Generate the feeds from the current context, and output files.""" 

        if 'SITEURL' not in context:
            context['SITEURL'] = self.output_path

        self.generate_feed(self.articles, context, self.output_path, 
            context['FEED'])

        for cat, arts in self.categories.items():
            arts.sort(key=attrgetter('date'), reverse=True)
            self.generate_feed(arts, context, self.output_path,
                context['CATEGORY_FEED'] % cat)

    def generate_pages(self, context):
        """Generate the pages on the disk"""

        templates = self.get_templates(self.theme)
        generate = self.generate_file
        for template in _DIRECT_TEMPLATES:
            generate('%s.html' % template, templates[template], context, blog=True)
        for tag in self.tags:
            generate('tag/%s.html' % tag, templates['tag'], context, tag=tag)
        for cat in self.categories:
            generate('category/%s.html' % cat, templates['category'], context,
                          category=cat, articles=self.categories[cat])
        for article in self.articles:
            generate('%s' % article.url,
                          templates['article'], context, article=article,
                          category=article.category)

    def generate_static_content(self):
        """copy static paths to output"""
        
        for path in self.settings['STATIC_PATHS']:
            try:
                fromp = os.path.expanduser(os.path.join(self.theme, path))
                to = os.path.expanduser(os.path.join(self.output_path, path))
                shutil.copytree(fromp, to)
                print u' ✔ copying %s to %s' % (fromp, to)

            except OSError:
                pass

    def generate(self, path=None, theme=None, output_path=None, fmt=None):
        """Search the given path for files, and generate a static blog in output,
        using the given theme.

        :param path: the path where to find the files to parse
        :param theme: where to search for templates
        :param output_path: where to output the generated files
        :param settings: the settings file to use
        :param fmt: the format of the files to read. It's a list.
        """

        self._init_params(path, theme, output_path, fmt)

        # build the list of articles / categories / etc.
        self.process_files(self.get_files(path))

        # sort the articles by date
        self.articles.sort(key=attrgetter('date'), reverse=True)
        # and generate the output :)
        context = self._get_context()
        self.generate_feeds(context)
        self.generate_pages(context)
        self.generate_static_content()
