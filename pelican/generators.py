# -*- coding: utf-8 -*-
import os
import datetime
import math
import random

from collections import defaultdict
from functools import partial
from itertools import chain
from operator import attrgetter, itemgetter

from jinja2 import Environment, FileSystemLoader, PrefixLoader, ChoiceLoader
from jinja2.exceptions import TemplateNotFound

from pelican.contents import Article, Page, Category, is_valid_content
from pelican.log import warning, error, debug, info
from pelican.readers import read_file
from pelican.utils import copy, process_translations, open


class Generator(object):
    """Baseclass generator"""

    def __init__(self, *args, **kwargs):
        for idx, item in enumerate(('context', 'settings', 'path', 'theme',
                'output_path', 'markup')):
            setattr(self, item, args[idx])

        for arg, value in kwargs.items():
            setattr(self, arg, value)

        # templates cache
        self._templates = {}
        self._templates_path = os.path.expanduser(
                os.path.join(self.theme, 'templates'))

        theme_path = os.path.dirname(os.path.abspath(__file__))

        simple_loader = FileSystemLoader(os.path.join(theme_path,
                                         "themes", "simple", "templates"))
        self._env = Environment(
            loader=ChoiceLoader([
                FileSystemLoader(self._templates_path),
                simple_loader,  # implicit inheritance
                PrefixLoader({'!simple': simple_loader})  # explicit one
            ]),
            extensions=self.settings.get('JINJA_EXTENSIONS', []),
        )

        debug('template list: {0}'.format(self._env.list_templates()))

        # get custom Jinja filters from user settings
        custom_filters = self.settings.get('JINJA_FILTERS', {})
        self._env.filters.update(custom_filters)

    def get_template(self, name):
        """Return the template by name.
        Use self.theme to get the templates to use, and return a list of
        templates ready to use with Jinja2.
        """
        if name not in self._templates:
            try:
                self._templates[name] = self._env.get_template(name + '.html')
            except TemplateNotFound:
                raise Exception('[templates] unable to load %s.html from %s' \
                        % (name, self._templates_path))
        return self._templates[name]

    def get_files(self, path, exclude=[], extensions=None):
        """Return a list of files to use, based on rules

        :param path: the path to search the file on
        :param exclude: the list of path to exclude
        """
        if not extensions:
            extensions = self.markup

        files = []

        try:
            iter = os.walk(path, followlinks=True)
        except TypeError:  # python 2.5 does not support followlinks
            iter = os.walk(path)

        for root, dirs, temp_files in iter:
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
        self.articles = []  # only articles in default language
        self.translations = []
        self.dates = {}
        self.tags = defaultdict(list)
        self.categories = defaultdict(list)
        self.authors = defaultdict(list)
        super(ArticlesGenerator, self).__init__(*args, **kwargs)
        self.drafts = []

    def generate_feeds(self, writer):
        """Generate the feeds from the current context, and output files."""

        if self.settings.get('FEED'):
            writer.write_feed(self.articles, self.context,
                              self.settings['FEED'])

        if self.settings.get('FEED_RSS'):
            writer.write_feed(self.articles, self.context,
                              self.settings['FEED_RSS'], feed_type='rss')

        for cat, arts in self.categories:
            arts.sort(key=attrgetter('date'), reverse=True)
            if self.settings.get('CATEGORY_FEED'):
                writer.write_feed(arts, self.context,
                                  self.settings['CATEGORY_FEED'] % cat)

            if self.settings.get('CATEGORY_FEED_RSS'):
                writer.write_feed(arts, self.context,
                                  self.settings['CATEGORY_FEED_RSS'] % cat,
                                  feed_type='rss')

        if self.settings.get('TAG_FEED') or self.settings.get('TAG_FEED_RSS'):
            for tag, arts in self.tags.items():
                arts.sort(key=attrgetter('date'), reverse=True)
                if self.settings.get('TAG_FEED'):
                    writer.write_feed(arts, self.context,
                                      self.settings['TAG_FEED'] % tag)

                if self.settings.get('TAG_FEED_RSS'):
                    writer.write_feed(arts, self.context,
                                      self.settings['TAG_FEED_RSS'] % tag,
                                      feed_type='rss')

        if self.settings.get('TRANSLATION_FEED'):
            translations_feeds = defaultdict(list)
            for article in chain(self.articles, self.translations):
                translations_feeds[article.lang].append(article)

            for lang, items in translations_feeds.items():
                items.sort(key=attrgetter('date'), reverse=True)
                writer.write_feed(items, self.context,
                                  self.settings['TRANSLATION_FEED'] % lang)

    def generate_pages(self, writer):
        """Generate the pages on the disk"""

        write = partial(writer.write_file,
                        relative_urls=self.settings.get('RELATIVE_URLS'))

        # to minimize the number of relative path stuff modification
        # in writer, articles pass first
        article_template = self.get_template('article')
        for article in chain(self.translations, self.articles):
            write(article.save_as,
                          article_template, self.context, article=article,
                          category=article.category)

        PAGINATED_TEMPLATES = self.settings.get('PAGINATED_DIRECT_TEMPLATES')
        for template in self.settings.get('DIRECT_TEMPLATES'):
            paginated = {}
            if template in PAGINATED_TEMPLATES:
                paginated = {'articles': self.articles, 'dates': self.dates}

            write('%s.html' % template, self.get_template(template),
                  self.context, blog=True, paginated=paginated,
                  page_name=template)

        # and subfolders after that
        tag_template = self.get_template('tag')
        for tag, articles in self.tags.items():
            articles.sort(key=attrgetter('date'), reverse=True)
            dates = [article for article in self.dates if article in articles]
            write(tag.save_as, tag_template, self.context, tag=tag,
                articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=u'tag/%s' % tag)

        category_template = self.get_template('category')
        for cat, articles in self.categories:
            dates = [article for article in self.dates if article in articles]
            write(cat.save_as, category_template, self.context,
                category=cat, articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=u'category/%s' % cat)

        author_template = self.get_template('author')
        for aut, articles in self.authors:
            dates = [article for article in self.dates if article in articles]
            write(aut.save_as, author_template, self.context,
                author=aut, articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=u'author/%s' % aut)

        for article in self.drafts:
            write('drafts/%s.html' % article.slug, article_template,
                  self.context, article=article, category=article.category)

    def generate_context(self):
        """change the context"""

        all_articles = []
        for f in self.get_files(
                os.path.join(self.path, self.settings['ARTICLE_DIR']),
                exclude=self.settings['ARTICLE_EXCLUDES']):
            try:
                content, metadata = read_file(f, settings=self.settings)
            except Exception, e:
                warning(u'Could not process %s\n%s' % (f, str(e)))
                continue

            # if no category is set, use the name of the path as a category
            if 'category' not in metadata.keys():

                if os.path.dirname(f) == self.path:
                    category = self.settings['DEFAULT_CATEGORY']
                else:
                    category = os.path.basename(os.path.dirname(f))\
                                .decode('utf-8')

                if category != '':
                    metadata['category'] = Category(category, self.settings)

            if 'date' not in metadata.keys()\
                and self.settings['FALLBACK_ON_FS_DATE']:
                    metadata['date'] = datetime.datetime.fromtimestamp(
                                        os.stat(f).st_ctime)

            article = Article(content, metadata, settings=self.settings,
                              filename=f)
            if not is_valid_content(article, f):
                continue

            if article.status == "published":
                if hasattr(article, 'tags'):
                    for tag in article.tags:
                        self.tags[tag].append(article)
                all_articles.append(article)
            elif article.status == "draft":
                self.drafts.append(article)

        self.articles, self.translations = process_translations(all_articles)

        for article in self.articles:
            # only main articles are listed in categories, not translations
            self.categories[article.category].append(article)
            self.authors[article.author].append(article)

        # sort the articles by date
        self.articles.sort(key=attrgetter('date'), reverse=True)
        self.dates = list(self.articles)
        self.dates.sort(key=attrgetter('date'),
                reverse=self.context['REVERSE_ARCHIVE_ORDER'])

        # create tag cloud
        tag_cloud = defaultdict(int)
        for article in self.articles:
            for tag in getattr(article, 'tags', []):
                tag_cloud[tag] += 1

        tag_cloud = sorted(tag_cloud.items(), key=itemgetter(1), reverse=True)
        tag_cloud = tag_cloud[:self.settings.get('TAG_CLOUD_MAX_ITEMS')]

        tags = map(itemgetter(1), tag_cloud)
        if tags:
            max_count = max(tags)
        steps = self.settings.get('TAG_CLOUD_STEPS')

        # calculate word sizes
        self.tag_cloud = [
            (
                tag,
                int(math.floor(steps - (steps - 1) * math.log(count)
                    / (math.log(max_count)or 1)))
            )
            for tag, count in tag_cloud
        ]
        # put words in chaos
        random.shuffle(self.tag_cloud)

        # and generate the output :)

        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(reverse=self.settings['REVERSE_CATEGORY_ORDER'])

        self.authors = list(self.authors.items())
        self.authors.sort()

        self._update_context(('articles', 'dates', 'tags', 'categories',
                              'tag_cloud', 'authors'))

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
        for f in self.get_files(
                os.path.join(self.path, self.settings['PAGE_DIR']),
                exclude=self.settings['PAGE_EXCLUDES']):
            try:
                content, metadata = read_file(f)
            except Exception, e:
                error(u'Could not process %s\n%s' % (f, str(e)))
                continue
            page = Page(content, metadata, settings=self.settings,
                        filename=f)
            if not is_valid_content(page, f):
                continue
            all_pages.append(page)

        self.pages, self.translations = process_translations(all_pages)

        self._update_context(('pages', ))
        self.context['PAGES'] = self.pages

    def generate_output(self, writer):
        for page in chain(self.translations, self.pages):
            writer.write_file(page.save_as, self.get_template('page'),
                    self.context, page=page,
                    relative_urls=self.settings.get('RELATIVE_URLS'))


class StaticGenerator(Generator):
    """copy static paths (what you want to cpy, like images, medias etc.
    to output"""

    def _copy_paths(self, paths, source, destination, output_path,
            final_path=None):
        """Copy all the paths from source to destination"""
        for path in paths:
            copy(path, source, os.path.join(output_path, destination),
                 final_path, overwrite=True)

    def generate_output(self, writer):
        self._copy_paths(self.settings['STATIC_PATHS'], self.path,
                         'static', self.output_path)
        self._copy_paths(self.settings['THEME_STATIC_PATHS'], self.theme,
                         'theme', self.output_path, '.')

        # copy all the files needed
        for source, destination in self.settings['FILES_TO_COPY']:
            copy(source, self.path, self.output_path, destination,
                 overwrite=True)


class PdfGenerator(Generator):
    """Generate PDFs on the output dir, for all articles and pages coming from
    rst"""
    def __init__(self, *args, **kwargs):
        try:
            from rst2pdf.createpdf import RstToPdf
            self.pdfcreator = RstToPdf(breakside=0,
                                       stylesheets=['twelvepoint'])
        except ImportError:
            raise Exception("unable to find rst2pdf")
        super(PdfGenerator, self).__init__(*args, **kwargs)

    def _create_pdf(self, obj, output_path):
        if obj.filename.endswith(".rst"):
            filename = obj.slug + ".pdf"
            output_pdf = os.path.join(output_path, filename)
            # print "Generating pdf for", obj.filename, " in ", output_pdf
            with open(obj.filename) as f:
                self.pdfcreator.createPdf(text=f, output=output_pdf)
            info(u' [ok] writing %s' % output_pdf)

    def generate_context(self):
        pass

    def generate_output(self, writer=None):
        # we don't use the writer passed as argument here
        # since we write our own files
        info(u' Generating PDF files...')
        pdf_path = os.path.join(self.output_path, 'pdf')
        if not os.path.exists(pdf_path):
            try:
                os.mkdir(pdf_path)
            except OSError:
                error("Couldn't create the pdf output folder in " + pdf_path)
                pass

        for article in self.context['articles']:
            self._create_pdf(article, pdf_path)

        for page in self.context['pages']:
            self._create_pdf(page, pdf_path)
