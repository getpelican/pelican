from operator import attrgetter
from itertools import chain
from functools import partial
from datetime import datetime
from collections import defaultdict
import os

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from pelican.utils import copytree, process_translations, open
from pelican.contents import Article, Page, is_valid_content
from pelican.readers import read_file

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives', 'page')
_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')


class Generator(object):
    """Baseclass generator"""

    def __init__(self, *args, **kwargs):
        for idx, item in enumerate(('context', 'settings', 'path', 'theme',
                'output_path', 'markup')):
            setattr(self, item, args[idx])

        for arg, value in kwargs.items():
            setattr(self, arg, value)

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

    def _update_context(self, items):
        """Update the context with the given items from the currrent
        processor.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = value.items()
            self.context[item] = value


class ArticlesGenerator(Generator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        """initialize properties"""
        self.articles = [] # only articles in default language
        self.translations = []
        self.dates = {}
        self.tags = defaultdict(list)
        self.categories = defaultdict(list)
        super(ArticlesGenerator, self).__init__(*args, **kwargs)

    def generate_feeds(self, writer):
        """Generate the feeds from the current context, and output files."""

        writer.write_feed(self.articles, self.context, self.settings['FEED'])

        if 'FEED_RSS' in self.settings:
            writer.write_feed(self.articles, self.context,
                    self.settings['FEED_RSS'], feed_type='rss')

        for cat, arts in self.categories.items():
            arts.sort(key=attrgetter('date'), reverse=True)
            writer.write_feed(arts, self.context,
                              self.settings['CATEGORY_FEED'] % cat)

            if 'CATEGORY_FEED_RSS' in self.settings:
                writer.write_feed(arts, self.context,
                        self.settings['CATEGORY_FEED_RSS'] % cat,
                        feed_type='rss')

        if 'TAG_FEED' in self.settings:
            for tag, arts in self.tags.items():
                arts.sort(key=attrgetter('date'), reverse=True)
                writer.write_feed(arts, self.context, 
                        self.settings['TAG_FEED'] % tag)

                if 'TAG_FEED_RSS' in self.settings:
                    writer.write_feed(arts, self.context, 
                            self.settings['TAG_FEED_RSS'] % tag, feed_type='rss')

        translations_feeds = defaultdict(list)
        for article in chain(self.articles, self.translations):
            translations_feeds[article.lang].append(article)

        for lang, items in translations_feeds.items():
            items.sort(key=attrgetter('date'), reverse=True)
            writer.write_feed(items, self.context,
                              self.settings['TRANSLATION_FEED'] % lang)


    def generate_pages(self, writer):
        """Generate the pages on the disk
        TODO: change the name"""

        templates = self.get_templates()
        write = partial(
            writer.write_file,
            relative_urls = self.settings.get('RELATIVE_URLS')
        )
        for template in _DIRECT_TEMPLATES:
            write('%s.html' % template, templates[template], self.context,
                    blog=True)
        for tag, articles in self.tags.items():
            write('tag/%s.html' % tag, templates['tag'], self.context, tag=tag,
                    articles=articles)
        for cat in self.categories:
            write('category/%s.html' % cat, templates['category'], self.context,
                          category=cat, articles=self.categories[cat])
        for article in chain(self.translations, self.articles):
            write(article.save_as,
                          templates['article'], self.context, article=article,
                          category=article.category)

    def generate_context(self):
        """change the context"""

        # return the list of files to use
        files = self.get_files(self.path, exclude=['pages',])
        all_articles = []
        for f in files:
            content, metadatas = read_file(f)

            # if no category is set, use the name of the path as a category
            if 'category' not in metadatas.keys():
                category = os.path.dirname(f).replace(
                    os.path.expanduser(self.path)+'/', '')

                if category == self.path:
                    category = self.settings['DEFAULT_CATEGORY']

                if category != '':
                    metadatas['category'] = unicode(category)

            if 'date' not in metadatas.keys()\
                and self.settings['FALLBACK_ON_FS_DATE']:
                    metadatas['date'] = datetime.fromtimestamp(os.stat(f).st_ctime)

            article = Article(content, metadatas, settings=self.settings,
                              filename=f)
            if not is_valid_content(article, f):
                continue

            if hasattr(article, 'tags'):
                for tag in article.tags:
                    self.tags[tag].append(article)
            all_articles.append(article)

        self.articles, self.translations = process_translations(all_articles)

        for article in self.articles:
            # only main articles are listed in categories, not translations
            self.categories[article.category].append(article)


        # sort the articles by date
        self.articles.sort(key=attrgetter('date'), reverse=True)
        self.dates = list(self.articles)
        self.dates.sort(key=attrgetter('date'), 
                reverse=self.context['REVERSE_ARCHIVE_ORDER'])
        # and generate the output :)
        self._update_context(('articles', 'dates', 'tags', 'categories'))

    def generate_output(self, writer):
        self.generate_feeds(writer)
        self.generate_pages(writer)


class PagesGenerator(Generator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        self.pages = []
        super(PagesGenerator, self).__init__(*args, **kwargs)

    def generate_context(self):
        all_pages = []
        for f in self.get_files(os.sep.join((self.path, 'pages'))):
            content, metadatas = read_file(f)
            page = Page(content, metadatas, settings=self.settings,
                        filename=f)
            if not is_valid_content(page, f):
                continue
            all_pages.append(page)

        self.pages, self.translations = process_translations(all_pages)

        self._update_context(('pages', ))
        self.context['PAGES'] = self.pages

    def generate_output(self, writer):
        templates = self.get_templates()
        for page in chain(self.translations, self.pages):
            writer.write_file('pages/%s' % page.save_as, templates['page'],
                    self.context, page=page,
                    relative_urls = self.settings.get('RELATIVE_URLS'))


class StaticGenerator(Generator):
    """copy static paths (what you want to cpy, like images, medias etc.
    to output"""

    def _copy_paths(self, paths, source, destination, output_path,
            final_path=None):
        for path in paths:
            copytree(path, source, os.path.join(output_path, destination),
                    final_path)

    def generate_output(self, writer):
        self._copy_paths(self.settings['STATIC_PATHS'], self.path,
                         'static', self.output_path)
        self._copy_paths(self.settings['THEME_STATIC_PATHS'], self.theme,
                         'theme', self.output_path, '.')


class PdfGenerator(Generator):
    """Generate PDFs on the output dir, for all articles and pages coming from
    rst"""
    def __init__(self, *args, **kwargs):
        try:
            from rst2pdf.createpdf import RstToPdf
            self.pdfcreator = RstToPdf(breakside=0, stylesheets=['twelvepoint'])
        except ImportError:
            raise Exception("unable to find rst2pdf")
        super(PdfGenerator, self).__init__(*args, **kwargs)

    def _create_pdf(self, obj, output_path):
        if obj.filename.endswith(".rst"):
            filename = obj.slug + ".pdf"
            output_pdf=os.path.join(output_path, filename)
            # print "Generating pdf for", obj.filename, " in ", output_pdf
            self.pdfcreator.createPdf(text=open(obj.filename), output=output_pdf)
            print u' [ok] writing %s' % output_pdf
    
    def generate_context(self):
        pass

    def generate_output(self, writer=None):
        # we don't use the writer passed as argument here, since we write our own files
        print u' Generating PDF files...'
        pdf_path = os.path.join(self.output_path, 'pdf')
        try:
            os.mkdir(pdf_path)
        except OSError:
            print "Couldn't create the pdf output folder in ", pdf_path
            pass

        for article in self.context['articles']:
            self._create_pdf(article, pdf_path)

        for page in self.context['pages']:
            self._create_pdf(page, pdf_path)
