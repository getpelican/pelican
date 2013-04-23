# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import math
import random
import logging
import datetime
import shutil

from codecs import open
from collections import defaultdict
from functools import partial
from itertools import chain, groupby
from operator import attrgetter, itemgetter

from jinja2 import (
        Environment, FileSystemLoader, PrefixLoader, ChoiceLoader, BaseLoader,
        TemplateNotFound
)

from pelican.contents import (
        Article, Page, Category, Static, is_valid_content
)
from pelican.readers import read_file
from pelican.utils import copy, process_translations, mkdir_p, DateFormatter
from pelican import signals
import pelican.utils


logger = logging.getLogger(__name__)


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
        self._templates_path = []
        self._templates_path.append(os.path.expanduser(
                os.path.join(self.theme, 'templates')))
        self._templates_path += self.settings.get('EXTRA_TEMPLATES_PATHS', [])

        theme_path = os.path.dirname(os.path.abspath(__file__))

        simple_loader = FileSystemLoader(os.path.join(theme_path,
                                         "themes", "simple", "templates"))
        self.env = Environment(
            trim_blocks=True,
            loader=ChoiceLoader([
                FileSystemLoader(self._templates_path),
                simple_loader,  # implicit inheritance
                PrefixLoader({'!simple': simple_loader})  # explicit one
            ]),
            extensions=self.settings.get('JINJA_EXTENSIONS', []),
        )

        logger.debug('template list: {0}'.format(self.env.list_templates()))

        # provide utils.strftime as a jinja filter
        self.env.filters.update({'strftime': DateFormatter()})

        # get custom Jinja filters from user settings
        custom_filters = self.settings.get('JINJA_FILTERS', {})
        self.env.filters.update(custom_filters)

        signals.generator_init.send(self)

    def get_template(self, name):
        """Return the template by name.
        Use self.theme to get the templates to use, and return a list of
        templates ready to use with Jinja2.
        """
        if name not in self._templates:
            try:
                self._templates[name] = self.env.get_template(name + '.html')
            except TemplateNotFound:
                raise Exception(
                        ('[templates] unable to load %s.html from %s'
                         % (name, self._templates_path)))
        return self._templates[name]

    def _include_path(self, path, extensions=None):
        """Inclusion logic for .get_files(), returns True/False

        :param path: the path which might be including
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        """
        if extensions is None:
            extensions = self.markup
        basename = os.path.basename(path)
        if extensions is False or basename.endswith(extensions):
            return True
        return False

    def get_files(self, path, exclude=[], extensions=None):
        """Return a list of files to use, based on rules

        :param path: the path to search the file on
        :param exclude: the list of path to exclude
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        """
        files = []

        if os.path.isdir(path):
            for root, dirs, temp_files in os.walk(path, followlinks=True):
                for e in exclude:
                    if e in dirs:
                        dirs.remove(e)
                for f in temp_files:
                    fp = os.path.join(root, f)
                    if self._include_path(fp, extensions):
                        files.append(fp)
        elif os.path.exists(path) and self._include_path(path, extensions):
            files.append(path)  # can't walk non-directories
        return files

    def add_source_path(self, content):
        location = content.get_relative_source_path()
        self.context['filenames'][location] = content

    def _update_context(self, items):
        """Update the context with the given items from the currrent
        processor.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = list(value.items())  # py3k safeguard for iterators
            self.context[item] = value


class _FileLoader(BaseLoader):

    def __init__(self, path, basedir):
        self.path = path
        self.fullpath = os.path.join(basedir, path)

    def get_source(self, environment, template):
        if template != self.path or not os.path.exists(self.fullpath):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(self.fullpath)
        with open(self.fullpath, 'r', encoding='utf-8') as f:
            source = f.read()
        return (source, self.fullpath,
                lambda: mtime == os.path.getmtime(self.fullpath))


class TemplatePagesGenerator(Generator):

    def generate_output(self, writer):
        for source, dest in self.settings['TEMPLATE_PAGES'].items():
            self.env.loader.loaders.insert(0, _FileLoader(source, self.path))
            try:
                template = self.env.get_template(source)
                rurls = self.settings.get('RELATIVE_URLS')
                writer.write_file(dest, template, self.context, rurls)
            finally:
                del self.env.loader.loaders[0]


class ArticlesGenerator(Generator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        """initialize properties"""
        self.articles = []  # only articles in default language
        self.translations = []
        self.dates = {}
        self.tags = defaultdict(list)
        self.categories = defaultdict(list)
        self.related_posts = []
        self.authors = defaultdict(list)
        self.drafts = []
        super(ArticlesGenerator, self).__init__(*args, **kwargs)
        signals.article_generator_init.send(self)

    def generate_feeds(self, writer):
        """Generate the feeds from the current context, and output files."""

        if self.settings.get('FEED_ATOM'):
            writer.write_feed(self.articles, self.context,
                              self.settings['FEED_ATOM'])

        if self.settings.get('FEED_RSS'):
            writer.write_feed(self.articles, self.context,
                              self.settings['FEED_RSS'], feed_type='rss')

        if (self.settings.get('FEED_ALL_ATOM')
                or self.settings.get('FEED_ALL_RSS')):
            all_articles = list(self.articles)
            for article in self.articles:
                all_articles.extend(article.translations)
            all_articles.sort(key=attrgetter('date'), reverse=True)

            if self.settings.get('FEED_ALL_ATOM'):
                writer.write_feed(all_articles, self.context,
                                  self.settings['FEED_ALL_ATOM'])

            if self.settings.get('FEED_ALL_RSS'):
                writer.write_feed(all_articles, self.context,
                                  self.settings['FEED_ALL_RSS'],
                                  feed_type='rss')

        for cat, arts in self.categories:
            arts.sort(key=attrgetter('date'), reverse=True)
            if self.settings.get('CATEGORY_FEED_ATOM'):
                writer.write_feed(arts, self.context,
                                  self.settings['CATEGORY_FEED_ATOM']
                                  % cat.slug)

            if self.settings.get('CATEGORY_FEED_RSS'):
                writer.write_feed(arts, self.context,
                                  self.settings['CATEGORY_FEED_RSS']
                                  % cat.slug, feed_type='rss')

        if (self.settings.get('TAG_FEED_ATOM')
                or self.settings.get('TAG_FEED_RSS')):
            for tag, arts in self.tags.items():
                arts.sort(key=attrgetter('date'), reverse=True)
                if self.settings.get('TAG_FEED_ATOM'):
                    writer.write_feed(arts, self.context,
                                      self.settings['TAG_FEED_ATOM']
                                      % tag.slug)

                if self.settings.get('TAG_FEED_RSS'):
                    writer.write_feed(arts, self.context,
                                      self.settings['TAG_FEED_RSS'] % tag.slug,
                                      feed_type='rss')

        if (self.settings.get('TRANSLATION_FEED_ATOM')
                or self.settings.get('TRANSLATION_FEED_RSS')):
            translations_feeds = defaultdict(list)
            for article in chain(self.articles, self.translations):
                translations_feeds[article.lang].append(article)

            for lang, items in translations_feeds.items():
                items.sort(key=attrgetter('date'), reverse=True)
                if self.settings.get('TRANSLATION_FEED_ATOM'):
                    writer.write_feed(items, self.context,
                            self.settings['TRANSLATION_FEED_ATOM'] % lang)
                if self.settings.get('TRANSLATION_FEED_RSS'):
                    writer.write_feed(items, self.context,
                            self.settings['TRANSLATION_FEED_RSS'] % lang,
                            feed_type='rss')

    def generate_articles(self, write):
        """Generate the articles."""
        for article in chain(self.translations, self.articles):
            write(article.save_as, self.get_template(article.template),
                self.context, article=article, category=article.category)

    def generate_period_archives(self, write):
        """Generate per-year, per-month, and per-day archives."""
        try:
            template = self.get_template('period_archives')
        except Exception:
            template = self.get_template('archives')

        def _generate_period_archives(dates, key, save_as_fmt):
            """Generate period archives from `dates`, grouped by
            `key` and written to `save_as`.
            """
            # `dates` is already sorted by date
            for _period, group in groupby(dates, key=key):
                archive = list(group)
                # arbitrarily grab the first date so that the usual
                # format string syntax can be used for specifying the
                # period archive dates
                date = archive[0].date
                save_as = save_as_fmt.format(date=date)
                write(save_as, template, self.context,
                      dates=archive, blog=True)

        period_save_as = {
                'year' : self.settings.get('YEAR_ARCHIVE_SAVE_AS'),
                'month': self.settings.get('MONTH_ARCHIVE_SAVE_AS'),
                'day'  : self.settings.get('DAY_ARCHIVE_SAVE_AS')
                }

        period_date_key = {
                'year' : attrgetter('date.year'),
                'month': attrgetter('date.year', 'date.month'),
                'day'  : attrgetter('date.year', 'date.month', 'date.day')
                }

        for period in 'year', 'month', 'day':
            save_as = period_save_as[period]
            if save_as:
                key = period_date_key[period]
                _generate_period_archives(self.dates, key, save_as)

    def generate_direct_templates(self, write):
        """Generate direct templates pages"""
        PAGINATED_TEMPLATES = self.settings.get('PAGINATED_DIRECT_TEMPLATES')
        for template in self.settings.get('DIRECT_TEMPLATES'):
            paginated = {}
            if template in PAGINATED_TEMPLATES:
                paginated = {'articles': self.articles, 'dates': self.dates}
            save_as = self.settings.get("%s_SAVE_AS" % template.upper(),
                                                        '%s.html' % template)
            if not save_as:
                continue

            write(save_as, self.get_template(template),
                self.context, blog=True, paginated=paginated,
                page_name=os.path.splitext(save_as)[0])

    def generate_tags(self, write):
        """Generate Tags pages."""
        tag_template = self.get_template('tag')
        for tag, articles in self.tags.items():
            articles.sort(key=attrgetter('date'), reverse=True)
            dates = [article for article in self.dates if article in articles]
            write(tag.save_as, tag_template, self.context, tag=tag,
                articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=tag.page_name, all_articles=self.articles)

    def generate_categories(self, write):
        """Generate category pages."""
        category_template = self.get_template('category')
        for cat, articles in self.categories:
            dates = [article for article in self.dates if article in articles]
            write(cat.save_as, category_template, self.context,
                category=cat, articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=cat.page_name, all_articles=self.articles)

    def generate_authors(self, write):
        """Generate Author pages."""
        author_template = self.get_template('author')
        for aut, articles in self.authors:
            dates = [article for article in self.dates if article in articles]
            write(aut.save_as, author_template, self.context,
                author=aut, articles=articles, dates=dates,
                paginated={'articles': articles, 'dates': dates},
                page_name=aut.page_name, all_articles=self.articles)

    def generate_drafts(self, write):
        """Generate drafts pages."""
        for article in self.drafts:
            write(os.path.join('drafts', '%s.html' % article.slug),
                self.get_template(article.template), self.context,
                article=article, category=article.category,
                all_articles=self.articles)

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file,
                        relative_urls=self.settings.get('RELATIVE_URLS'))

        # to minimize the number of relative path stuff modification
        # in writer, articles pass first
        self.generate_articles(write)
        self.generate_period_archives(write)
        self.generate_direct_templates(write)

        # and subfolders after that
        self.generate_tags(write)
        self.generate_categories(write)
        self.generate_authors(write)
        self.generate_drafts(write)

    def generate_context(self):
        """Add the articles into the shared context"""

        article_path = os.path.normpath(  # we have to remove trailing slashes
            os.path.join(self.path, self.settings['ARTICLE_DIR'])
        )
        all_articles = []
        for f in self.get_files(
                article_path,
                exclude=self.settings['ARTICLE_EXCLUDES']):
            try:
                signals.article_generate_preread.send(self)
                content, metadata = read_file(f, settings=self.settings)
            except Exception as e:
                logger.warning('Could not process %s\n%s' % (f, str(e)))
                continue

            # if no category is set, use the name of the path as a category
            if 'category' not in metadata:

                if (self.settings['USE_FOLDER_AS_CATEGORY']
                    and os.path.dirname(f) != article_path):
                    # if the article is in a subdirectory
                    category = os.path.basename(os.path.dirname(f))
                else:
                    # if the article is not in a subdirectory
                    category = self.settings['DEFAULT_CATEGORY']

                if category != '':
                    metadata['category'] = Category(category, self.settings)

            if 'date' not in metadata and self.settings.get('DEFAULT_DATE'):
                if self.settings['DEFAULT_DATE'] == 'fs':
                    metadata['date'] = datetime.datetime.fromtimestamp(
                            os.stat(f).st_ctime)
                else:
                    metadata['date'] = datetime.datetime(
                            *self.settings['DEFAULT_DATE'])

            signals.article_generate_context.send(self, metadata=metadata)
            article = Article(content, metadata, settings=self.settings,
                              source_path=f, context=self.context)
            if not is_valid_content(article, f):
                continue

            self.add_source_path(article)

            if article.status == "published":
                all_articles.append(article)
            elif article.status == "draft":
                self.drafts.append(article)
            else:
                logger.warning("Unknown status %s for file %s, skipping it." %
                               (repr(article.status),
                                repr(f)))

        self.articles, self.translations = process_translations(all_articles)

        for article in self.articles:
            # only main articles are listed in categories and tags
            # not translations
            self.categories[article.category].append(article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    self.tags[tag].append(article)
            # ignore blank authors as well as undefined
            if hasattr(article, 'author') and article.author.name != '':
                self.authors[article.author].append(article)


        # sort the articles by date
        self.articles.sort(key=attrgetter('date'), reverse=True)
        self.dates = list(self.articles)
        self.dates.sort(key=attrgetter('date'),
                reverse=self.context['NEWEST_FIRST_ARCHIVES'])

        # create tag cloud
        tag_cloud = defaultdict(int)
        for article in self.articles:
            for tag in getattr(article, 'tags', []):
                tag_cloud[tag] += 1

        tag_cloud = sorted(tag_cloud.items(), key=itemgetter(1), reverse=True)
        tag_cloud = tag_cloud[:self.settings.get('TAG_CLOUD_MAX_ITEMS')]

        tags = list(map(itemgetter(1), tag_cloud))
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
        self.categories.sort(
                reverse=self.settings['REVERSE_CATEGORY_ORDER'])

        self.authors = list(self.authors.items())
        self.authors.sort()

        self._update_context(('articles', 'dates', 'tags', 'categories',
                              'tag_cloud', 'authors', 'related_posts'))

        signals.article_generator_finalized.send(self)

    def generate_output(self, writer):
        self.generate_feeds(writer)
        self.generate_pages(writer)


class PagesGenerator(Generator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        self.pages = []
        self.hidden_pages = []
        self.hidden_translations = []
        super(PagesGenerator, self).__init__(*args, **kwargs)
        signals.pages_generator_init.send(self)

    def generate_context(self):
        all_pages = []
        hidden_pages = []
        for f in self.get_files(
                os.path.join(self.path, self.settings['PAGE_DIR']),
                exclude=self.settings['PAGE_EXCLUDES']):
            try:
                content, metadata = read_file(f, settings=self.settings)
            except Exception as e:
                logger.warning('Could not process %s\n%s' % (f, str(e)))
                continue
            signals.pages_generate_context.send(self, metadata=metadata)
            page = Page(content, metadata, settings=self.settings,
                        source_path=f, context=self.context)
            if not is_valid_content(page, f):
                continue

            self.add_source_path(page)

            if page.status == "published":
                all_pages.append(page)
            elif page.status == "hidden":
                hidden_pages.append(page)
            else:
                logger.warning("Unknown status %s for file %s, skipping it." %
                               (repr(page.status),
                                repr(f)))

        self.pages, self.translations = process_translations(all_pages)
        self.hidden_pages, self.hidden_translations = (
                process_translations(hidden_pages))

        self._update_context(('pages', ))
        self.context['PAGES'] = self.pages

        signals.pages_generator_finalized.send(self)

    def generate_output(self, writer):
        for page in chain(self.translations, self.pages,
                            self.hidden_translations, self.hidden_pages):
            writer.write_file(page.save_as, self.get_template(page.template),
                    self.context, page=page,
                    relative_urls=self.settings.get('RELATIVE_URLS'))


class StaticGenerator(Generator):
    """copy static paths (what you want to copy, like images, medias etc.
    to output"""

    def _copy_paths(self, paths, source, destination, output_path,
            final_path=None):
        """Copy all the paths from source to destination"""
        for path in paths:
            copy(path, source, os.path.join(output_path, destination),
                 final_path, overwrite=True)

    def generate_context(self):
        self.staticfiles = []

        # walk static paths
        for static_path in self.settings['STATIC_PATHS']:
            for f in self.get_files(
                    os.path.join(self.path, static_path), extensions=False):
                f_rel = os.path.relpath(f, self.path)
                content, metadata = read_file(
                    f, fmt='static', settings=self.settings)
                # TODO remove this hardcoded 'static' subdirectory
                metadata['save_as'] = os.path.join('static', f_rel)
                metadata['url'] = pelican.utils.path_to_url(metadata['save_as'])
                sc = Static(
                    content=None,
                    metadata=metadata,
                    settings=self.settings,
                    source_path=f_rel)
                self.staticfiles.append(sc)
                self.add_source_path(sc)
        # same thing for FILES_TO_COPY
        for src, dest in self.settings['FILES_TO_COPY']:
            content, metadata = read_file(
                src, fmt='static', settings=self.settings)
            metadata['save_as'] = dest
            metadata['url'] = pelican.utils.path_to_url(metadata['save_as'])
            sc = Static(
                content=None,
                metadata={'save_as': dest},
                settings=self.settings,
                source_path=src)
            self.staticfiles.append(sc)
            self.add_source_path(sc)

    def generate_output(self, writer):
        self._copy_paths(self.settings['THEME_STATIC_PATHS'], self.theme,
                         'theme', self.output_path, os.curdir)
        # copy all Static files
        for sc in self.staticfiles:
            source_path = os.path.join(self.path, sc.source_path)
            save_as = os.path.join(self.output_path, sc.save_as)
            mkdir_p(os.path.dirname(save_as))
            shutil.copy(source_path, save_as)
            logger.info('copying {} to {}'.format(sc.source_path, sc.save_as))


class PdfGenerator(Generator):
    """Generate PDFs on the output dir, for all articles and pages coming from
    rst"""
    def __init__(self, *args, **kwargs):
        super(PdfGenerator, self).__init__(*args, **kwargs)
        try:
            from rst2pdf.createpdf import RstToPdf
            if 'PDF_STYLE_PATH' in self.settings.keys():
                pdf_style_path = os.path.join(self.settings['PDF_STYLE_PATH'])
            else:
                pdf_style_path = ''

            if 'PDF_STYLE' in self.settings.keys():
                pdf_style = self.settings.get('PDF_STYLE', 'twelvepoint')

            self.pdfcreator = RstToPdf(breakside=0,
                                       stylesheets=[pdf_style],
                                       style_path=[pdf_style_path])
        except ImportError:
            raise Exception("unable to find rst2pdf")

    def _create_pdf(self, obj, output_path):
        if obj.source_path.endswith('.rst'):
            filename = obj.slug + ".pdf"
            output_pdf = os.path.join(output_path, filename)
            # print('Generating pdf for', obj.source_path, 'in', output_pdf)
            with open(obj.source_path) as f:
                self.pdfcreator.createPdf(text=f.read(), output=output_pdf)
            logger.info(' [ok] writing %s' % output_pdf)

    def generate_context(self):
        pass

    def generate_output(self, writer=None):
        # we don't use the writer passed as argument here
        # since we write our own files
        logger.info(' Generating PDF files...')
        pdf_path = os.path.join(self.output_path, 'pdf')
        if not os.path.exists(pdf_path):
            try:
                os.mkdir(pdf_path)
            except OSError:
                logger.error("Couldn't create the pdf output folder in " +
                             pdf_path)

        for article in self.context['articles']:
            self._create_pdf(article, pdf_path)

        for page in self.context['pages']:
            self._create_pdf(page, pdf_path)


class SourceFileGenerator(Generator):
    def generate_context(self):
        self.output_extension = self.settings['OUTPUT_SOURCES_EXTENSION']

    def _create_source(self, obj):
        output_path, _ = os.path.splitext(obj.save_as)
        dest = os.path.join(self.output_path,
                            output_path + self.output_extension)
        copy('', obj.source_path, dest)

    def generate_output(self, writer=None):
        logger.info(' Generating source files...')
        for obj in chain(self.context['articles'], self.context['pages']):
            self._create_source(obj)
            for obj_trans in obj.translations:
                self._create_source(obj_trans)
