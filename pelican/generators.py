# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import six
import logging
import shutil
import fnmatch
import calendar

from codecs import open
from collections import defaultdict
from functools import partial
from itertools import chain, groupby
from operator import attrgetter

from jinja2 import (Environment, FileSystemLoader, PrefixLoader, ChoiceLoader,
                    BaseLoader, TemplateNotFound)

from pelican.cache import FileStampDataCacher
from pelican.contents import Article, Draft, Page, Static, is_valid_content
from pelican.readers import Readers
from pelican.utils import (copy, process_translations, mkdir_p, DateFormatter,
                           python_2_unicode_compatible, posixize_path)
from pelican import signals


logger = logging.getLogger(__name__)


class PelicanTemplateNotFound(Exception):
    pass

@python_2_unicode_compatible
class Generator(object):
    """Baseclass generator"""

    def __init__(self, context, settings, path, theme, output_path,
                 readers_cache_name='', **kwargs):
        self.context = context
        self.settings = settings
        self.path = path
        self.theme = theme
        self.output_path = output_path

        for arg, value in kwargs.items():
            setattr(self, arg, value)

        self.readers = Readers(self.settings, readers_cache_name)

        # templates cache
        self._templates = {}
        self._templates_path = []
        self._templates_path.append(os.path.expanduser(
            os.path.join(self.theme, 'templates')))
        self._templates_path += self.settings['EXTRA_TEMPLATES_PATHS']

        theme_path = os.path.dirname(os.path.abspath(__file__))

        simple_loader = FileSystemLoader(os.path.join(theme_path,
                                         "themes", "simple", "templates"))
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=ChoiceLoader([
                FileSystemLoader(self._templates_path),
                simple_loader,  # implicit inheritance
                PrefixLoader({'!simple': simple_loader})  # explicit one
            ]),
            extensions=self.settings['JINJA_EXTENSIONS'],
        )

        logger.debug('Template list: %s', self.env.list_templates())

        # provide utils.strftime as a jinja filter
        self.env.filters.update({'strftime': DateFormatter()})

        # get custom Jinja filters from user settings
        custom_filters = self.settings['JINJA_FILTERS']
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
                raise PelicanTemplateNotFound('[templates] unable to load %s.html from %s'
                                % (name, self._templates_path))
        return self._templates[name]

    def _include_path(self, path, extensions=None):
        """Inclusion logic for .get_files(), returns True/False

        :param path: the path which might be including
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        """
        if extensions is None:
            extensions = tuple(self.readers.extensions)
        basename = os.path.basename(path)

        #check IGNORE_FILES
        ignores = self.settings['IGNORE_FILES']
        if any(fnmatch.fnmatch(basename, ignore) for ignore in ignores):
            return False

        if extensions is False or basename.endswith(extensions):
            return True
        return False

    def get_files(self, paths, exclude=[], extensions=None):
        """Return a list of files to use, based on rules

        :param paths: the list pf paths to search (relative to self.path)
        :param exclude: the list of path to exclude
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        """
        if isinstance(paths, six.string_types):
            paths = [paths] # backward compatibility for older generators

        # group the exclude dir names by parent path, for use with os.walk()
        exclusions_by_dirpath = {}
        for e in exclude:
            parent_path, subdir = os.path.split(os.path.join(self.path, e))
            exclusions_by_dirpath.setdefault(parent_path, set()).add(subdir)

        files = []
        ignores = self.settings['IGNORE_FILES']
        for path in paths:
            # careful: os.path.join() will add a slash when path == ''.
            root = os.path.join(self.path, path) if path else self.path

            if os.path.isdir(root):
                for dirpath, dirs, temp_files in os.walk(root, followlinks=True):
                    drop = []
                    excl = exclusions_by_dirpath.get(dirpath, ())
                    for d in dirs:
                        if (d in excl or
                            any(fnmatch.fnmatch(d, ignore)
                                for ignore in ignores)):
                            drop.append(d)
                    for d in drop:
                        dirs.remove(d)

                    reldir = os.path.relpath(dirpath, self.path)
                    for f in temp_files:
                        fp = os.path.join(reldir, f)
                        if self._include_path(fp, extensions):
                            files.append(fp)
            elif os.path.exists(root) and self._include_path(path, extensions):
                files.append(path)  # can't walk non-directories
        return files

    def add_source_path(self, content):
        """Record a source file path that a Generator found and processed.
        Store a reference to its Content object, for url lookups later.
        """
        location = content.get_relative_source_path()
        self.context['filenames'][location] = content

    def _add_failed_source_path(self, path):
        """Record a source file path that a Generator failed to process.
        (For example, one that was missing mandatory metadata.)
        The path argument is expected to be relative to self.path.
        """
        self.context['filenames'][posixize_path(os.path.normpath(path))] = None

    def _is_potential_source_path(self, path):
        """Return True if path was supposed to be used as a source file.
        (This includes all source files that have been found by generators
        before this method is called, even if they failed to process.)
        The path argument is expected to be relative to self.path.
        """
        return posixize_path(os.path.normpath(path)) in self.context['filenames']

    def _update_context(self, items):
        """Update the context with the given items from the currrent
        processor.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = list(value.items())  # py3k safeguard for iterators
            self.context[item] = value

    def __str__(self):
        # return the name of the class for logging purposes
        return self.__class__.__name__


class CachingGenerator(Generator, FileStampDataCacher):
    '''Subclass of Generator and FileStampDataCacher classes

    enables content caching, either at the generator or reader level
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize the generator, then set up caching

        note the multiple inheritance structure
        '''
        cls_name = self.__class__.__name__
        Generator.__init__(self, *args,
                           readers_cache_name=(cls_name + '-Readers'),
                           **kwargs)

        cache_this_level = self.settings['CONTENT_CACHING_LAYER'] == 'generator'
        caching_policy = cache_this_level and self.settings['CACHE_CONTENT']
        load_policy = cache_this_level and self.settings['LOAD_CONTENT_CACHE']
        FileStampDataCacher.__init__(self, self.settings, cls_name,
                                     caching_policy, load_policy
                                     )

    def _get_file_stamp(self, filename):
        '''Get filestamp for path relative to generator.path'''
        filename = os.path.join(self.path, filename)
        return super(CachingGenerator, self)._get_file_stamp(filename)


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
                rurls = self.settings['RELATIVE_URLS']
                writer.write_file(dest, template, self.context, rurls,
                                  override_output=True)
            finally:
                del self.env.loader.loaders[0]


class ArticlesGenerator(CachingGenerator):
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
        self.drafts = [] # only drafts in default language
        self.drafts_translations = []
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

        for auth, arts in self.authors:
            arts.sort(key=attrgetter('date'), reverse=True)
            if self.settings.get('AUTHOR_FEED_ATOM'):
                writer.write_feed(arts, self.context,
                                  self.settings['AUTHOR_FEED_ATOM']
                                  % auth.slug)

            if self.settings.get('AUTHOR_FEED_RSS'):
                writer.write_feed(arts, self.context,
                                  self.settings['AUTHOR_FEED_RSS']
                                  % auth.slug, feed_type='rss')

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
                    writer.write_feed(
                        items, self.context,
                        self.settings['TRANSLATION_FEED_ATOM'] % lang)
                if self.settings.get('TRANSLATION_FEED_RSS'):
                    writer.write_feed(
                        items, self.context,
                        self.settings['TRANSLATION_FEED_RSS'] % lang,
                        feed_type='rss')

    def generate_articles(self, write):
        """Generate the articles."""
        for article in chain(self.translations, self.articles):
            signals.article_generator_write_article.send(self, content=article)
            write(article.save_as, self.get_template(article.template),
                  self.context, article=article, category=article.category,
                  override_output=hasattr(article, 'override_save_as'),
                  blog=True)

    def generate_period_archives(self, write):
        """Generate per-year, per-month, and per-day archives."""
        try:
            template = self.get_template('period_archives')
        except PelicanTemplateNotFound:
            template = self.get_template('archives')

        period_save_as = {
            'year': self.settings['YEAR_ARCHIVE_SAVE_AS'],
            'month': self.settings['MONTH_ARCHIVE_SAVE_AS'],
            'day': self.settings['DAY_ARCHIVE_SAVE_AS'],
        }

        period_date_key = {
            'year': attrgetter('date.year'),
            'month': attrgetter('date.year', 'date.month'),
            'day': attrgetter('date.year', 'date.month', 'date.day')
        }

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
                context = self.context.copy()

                if key == period_date_key['year']:
                    context["period"] = (_period,)
                else:
                    month_name = calendar.month_name[_period[1]]
                    if not six.PY3:
                        month_name = month_name.decode('utf-8')
                    if key == period_date_key['month']:
                        context["period"] = (_period[0],
                                             month_name)
                    else:
                        context["period"] = (_period[0],
                                             month_name,
                                             _period[2])

                write(save_as, template, context,
                      dates=archive, blog=True)

        for period in 'year', 'month', 'day':
            save_as = period_save_as[period]
            if save_as:
                key = period_date_key[period]
                _generate_period_archives(self.dates, key, save_as)

    def generate_direct_templates(self, write):
        """Generate direct templates pages"""
        PAGINATED_TEMPLATES = self.settings['PAGINATED_DIRECT_TEMPLATES']
        for template in self.settings['DIRECT_TEMPLATES']:
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
                  paginated={'articles': articles, 'dates': dates}, blog=True,
                  page_name=tag.page_name, all_articles=self.articles)

    def generate_categories(self, write):
        """Generate category pages."""
        category_template = self.get_template('category')
        for cat, articles in self.categories:
            articles.sort(key=attrgetter('date'), reverse=True)
            dates = [article for article in self.dates if article in articles]
            write(cat.save_as, category_template, self.context,
                  category=cat, articles=articles, dates=dates,
                  paginated={'articles': articles, 'dates': dates}, blog=True,
                  page_name=cat.page_name, all_articles=self.articles)

    def generate_authors(self, write):
        """Generate Author pages."""
        author_template = self.get_template('author')
        for aut, articles in self.authors:
            articles.sort(key=attrgetter('date'), reverse=True)
            dates = [article for article in self.dates if article in articles]
            write(aut.save_as, author_template, self.context,
                  author=aut, articles=articles, dates=dates,
                  paginated={'articles': articles, 'dates': dates}, blog=True,
                  page_name=aut.page_name, all_articles=self.articles)

    def generate_drafts(self, write):
        """Generate drafts pages."""
        for draft in chain(self.drafts_translations, self.drafts):
            write(draft.save_as, self.get_template(draft.template),
                self.context, article=draft, category=draft.category,
                override_output=hasattr(draft, 'override_save_as'),
                blog=True, all_articles=self.articles)

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file,
                        relative_urls=self.settings['RELATIVE_URLS'])

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

        all_articles = []
        all_drafts = []
        for f in self.get_files(
                self.settings['ARTICLE_PATHS'],
                exclude=self.settings['ARTICLE_EXCLUDES']):
            article_or_draft = self.get_cached_data(f, None)
            if article_or_draft is None:
            #TODO needs overhaul, maybe nomad for read_file solution, unified behaviour
                try:
                    article_or_draft = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Article,
                        context=self.context,
                        preread_signal=signals.article_generator_preread,
                        preread_sender=self,
                        context_signal=signals.article_generator_context,
                        context_sender=self)
                except Exception as e:
                    logger.error('Could not process %s\n%s', f, e,
                        exc_info=self.settings.get('DEBUG', False))
                    self._add_failed_source_path(f)
                    continue

                if not is_valid_content(article_or_draft, f):
                    self._add_failed_source_path(f)
                    continue

                if article_or_draft.status.lower() == "published":
                    all_articles.append(article_or_draft)
                elif article_or_draft.status.lower() == "draft":
                    article_or_draft = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Draft,
                        context=self.context,
                        preread_signal=signals.article_generator_preread,
                        preread_sender=self,
                        context_signal=signals.article_generator_context,
                        context_sender=self)
                    self.add_source_path(article_or_draft)
                    all_drafts.append(article_or_draft)
                else:
                    logger.error("Unknown status '%s' for file %s, skipping it.",
                                   article_or_draft.status, f)
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, article_or_draft)

            self.add_source_path(article_or_draft)


        self.articles, self.translations = process_translations(all_articles,
                order_by=self.settings['ARTICLE_ORDER_BY'])
        self.drafts, self.drafts_translations = \
            process_translations(all_drafts)

        signals.article_generator_pretaxonomy.send(self)

        for article in self.articles:
            # only main articles are listed in categories and tags
            # not translations
            self.categories[article.category].append(article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    self.tags[tag].append(article)
            for author in getattr(article, 'authors', []):
                self.authors[author].append(article)

        self.dates = list(self.articles)
        self.dates.sort(key=attrgetter('date'),
                        reverse=self.context['NEWEST_FIRST_ARCHIVES'])

        # and generate the output :)

        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(
            reverse=self.settings['REVERSE_CATEGORY_ORDER'])

        self.authors = list(self.authors.items())
        self.authors.sort()

        self._update_context(('articles', 'dates', 'tags', 'categories',
                              'authors', 'related_posts', 'drafts'))
        self.save_cache()
        self.readers.save_cache()
        signals.article_generator_finalized.send(self)

    def generate_output(self, writer):
        self.generate_feeds(writer)
        self.generate_pages(writer)
        signals.article_writer_finalized.send(self, writer=writer)


class PagesGenerator(CachingGenerator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        self.pages = []
        self.hidden_pages = []
        self.hidden_translations = []
        super(PagesGenerator, self).__init__(*args, **kwargs)
        signals.page_generator_init.send(self)

    def generate_context(self):
        all_pages = []
        hidden_pages = []
        for f in self.get_files(
                self.settings['PAGE_PATHS'],
                exclude=self.settings['PAGE_EXCLUDES']):
            page = self.get_cached_data(f, None)
            if page is None:
                try:
                    page = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Page,
                        context=self.context,
                        preread_signal=signals.page_generator_preread,
                        preread_sender=self,
                        context_signal=signals.page_generator_context,
                        context_sender=self)
                except Exception as e:
                    logger.error('Could not process %s\n%s', f, e,
                        exc_info=self.settings.get('DEBUG', False))
                    self._add_failed_source_path(f)
                    continue

                if not is_valid_content(page, f):
                    self._add_failed_source_path(f)
                    continue

                if page.status.lower() == "published":
                    all_pages.append(page)
                elif page.status.lower() == "hidden":
                    hidden_pages.append(page)
                else:
                    logger.error("Unknown status '%s' for file %s, skipping it.",
                                   page.status, f)
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, page)

            self.add_source_path(page)

        self.pages, self.translations = process_translations(all_pages,
                order_by=self.settings['PAGE_ORDER_BY'])
        self.hidden_pages, self.hidden_translations = (
            process_translations(hidden_pages))

        self._update_context(('pages', 'hidden_pages'))
        self.context['PAGES'] = self.pages

        self.save_cache()
        self.readers.save_cache()
        signals.page_generator_finalized.send(self)

    def generate_output(self, writer):
        for page in chain(self.translations, self.pages,
                          self.hidden_translations, self.hidden_pages):
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(page, 'override_save_as'))
        signals.page_writer_finalized.send(self, writer=writer)


class StaticGenerator(Generator):
    """copy static paths (what you want to copy, like images, medias etc.
    to output"""

    def __init__(self, *args, **kwargs):
        super(StaticGenerator, self).__init__(*args, **kwargs)
        signals.static_generator_init.send(self)

    def _copy_paths(self, paths, source, destination, output_path,
                    final_path=None):
        """Copy all the paths from source to destination"""
        for path in paths:
            if final_path:
                copy(os.path.join(source, path),
                     os.path.join(output_path, destination, final_path),
                     self.settings['IGNORE_FILES'])
            else:
                copy(os.path.join(source, path),
                     os.path.join(output_path, destination, path),
                     self.settings['IGNORE_FILES'])

    def generate_context(self):
        self.staticfiles = []
        for f in self.get_files(self.settings['STATIC_PATHS'],
                                exclude=self.settings['STATIC_EXCLUDES'],
                                extensions=False):

            # skip content source files unless the user explicitly wants them
            if self.settings['STATIC_EXCLUDE_SOURCES']:
                if self._is_potential_source_path(f):
                    continue

            static = self.readers.read_file(
                base_path=self.path, path=f, content_class=Static,
                fmt='static', context=self.context,
                preread_signal=signals.static_generator_preread,
                preread_sender=self,
                context_signal=signals.static_generator_context,
                context_sender=self)
            self.staticfiles.append(static)
            self.add_source_path(static)
        self._update_context(('staticfiles',))
        signals.static_generator_finalized.send(self)

    def generate_output(self, writer):
        self._copy_paths(self.settings['THEME_STATIC_PATHS'], self.theme,
                         self.settings['THEME_STATIC_DIR'], self.output_path,
                         os.curdir)
        # copy all Static files
        for sc in self.context['staticfiles']:
            source_path = os.path.join(self.path, sc.source_path)
            save_as = os.path.join(self.output_path, sc.save_as)
            mkdir_p(os.path.dirname(save_as))
            shutil.copy2(source_path, save_as)
            logger.info('Copying %s to %s', sc.source_path, sc.save_as)


class SourceFileGenerator(Generator):

    def generate_context(self):
        self.output_extension = self.settings['OUTPUT_SOURCES_EXTENSION']

    def _create_source(self, obj):
        output_path, _ = os.path.splitext(obj.save_as)
        dest = os.path.join(self.output_path,
                            output_path + self.output_extension)
        copy(obj.source_path, dest)

    def generate_output(self, writer=None):
        logger.info('Generating source files...')
        for obj in chain(self.context['articles'], self.context['pages']):
            self._create_source(obj)
            for obj_trans in obj.translations:
                self._create_source(obj_trans)
