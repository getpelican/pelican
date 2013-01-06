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
from itertools import chain
from operator import attrgetter, itemgetter

from jinja2 import (Environment, FileSystemLoader, PrefixLoader, ChoiceLoader,
                    BaseLoader, TemplateNotFound)

import pelican.contents
from pelican.readers import read_file
from pelican.utils import copy, process_translations, mkdir_p
from pelican import signals


logger = logging.getLogger(__name__)


class InvalidContent (ValueError):
    pass


def relative_urls(fn):
    """Decorator to mark generator helpers that can use relative URLs"""
    def new(self, writer):
        relative_write_file = partial(
            writer.write_file,
            relative_urls=self.get_setting('RELATIVE_URLS', fallback=True))
        return fn(self, relative_write_file)
    return new


class Generator(object):
    """Baseclass generator"""

    def __init__(self, context, settings, path, theme, output_path, markup,
                 **kwargs):
        if 'filenames' not in context:
            context['filenames'] = {}
        self.context = context
        self.settings = settings
        self.path = path
        self.theme = theme
        self.output_path = output_path
        self.markup = markup
        self.fmt = None

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

        # get custom Jinja filters from user settings
        custom_filters = self.settings.get('JINJA_FILTERS', {})
        self.env.filters.update(custom_filters)

        signals.generator_init.send(self)

    def generate_context(self):
        """Dummy method, used by Pelican.run()"""
        pass

    def generate_output(self, writer):
        """Dummy method, used by Pelican.run()"""
        pass

    def get_template(self, name):
        """Return the template by name.
        Use self.theme to get the templates to use, and return a list of
        templates ready to use with Jinja2.
        """
        if name not in self._templates:
            try:
                self._templates[name] = self.env.get_template(name + '.html')
            except TemplateNotFound:
                raise Exception('[templates] unable to load %s.html from %s' \
                        % (name, self._templates_path))
        return self._templates[name]

    def _include_path(self, path, extensions=None, known=False):
        """Inclusion logic for .get_files()
        """
        if extensions is None:
            extensions = self.markup
        basename = os.path.basename(path)
        if extensions is False or \
                (True in [basename.endswith(ext) for ext in extensions]):
            if not known:
                location = os.path.relpath(
                    os.path.abspath(path), os.path.abspath(self.path))
                if location in self.context['filenames']:
                    return False
            return True
        return False

    def get_files(self, path, exclude=[], extensions=None, known=False):
        """Return a list of files to use, based on rules

        :param path: the path to search the file on
        :param exclude: the list of path to exclude
        :param extensions: the list of allowed extensions (if False, all
            extensions are allowed)
        :param known: return files already listed in .context['filenames']
        """
        files = []

        if os.path.isdir(path):
            for root, dirs, temp_files in os.walk(path, followlinks=True):
                for e in exclude:
                    if e in dirs:
                        dirs.remove(e)
                for f in temp_files:
                    fp = os.path.join(root, f)
                    if self._include_path(fp, extensions, known):
                        files.append(fp)
        elif (os.path.exists(path) and
              self._include_path(path, extensions, known)):
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
        return source, self.fullpath, \
                lambda: mtime == os.path.getmtime(self.fullpath)


class ContentGenerator(Generator):
    """Base-class for content (e.g. Page, Article, ...) generators"""

    def __init__(self, name, *args, **kwargs):
        """initialize properties"""
        self.name = name
        self.all_content = []
        self.contents = []  # only content in the default language
        self.hidden = []
        self.drafts = []
        self.translations = []
        self.hidden_translations = []
        self.related = []
        self.dates = {}
        self.tags = defaultdict(list)
        self.categories = defaultdict(list)
        self.authors = defaultdict(list)
        self.signals = {}
        for sig_name in ['init', 'finalized', 'preread', 'context']:
            sig_fn_name = '{}_generator_{}'.format(self.name, sig_name)
            self.signals[sig_name] = getattr(signals, sig_fn_name, None)
        self.content_class = getattr(
            pelican.contents, self.name.title(), pelican.contents.Page)
        self._check_validity = True
        self._context_processors = [
            self._process_translations,  # sets up .content and .translations
            self._process_hidden_translations,
            self._process_sort,
            self._process_categories,
            self._process_authors,
            self._process_dates,
            self._process_tag_cloud,
            ]
        self._generators = [
            # to minimize the number of relative path stuff modification
            # in writer, articles pass first
            self._generate_content,
            self._generate_hidden,
            self._generate_direct_templates,
            # and subfolders after that
            self._generate_tags,
            self._generate_categories,
            self._generate_authors,
            self._generate_drafts,
            # Feeds can resort lists, so put them last
            self._generate_feeds,
            self._generate_all_feeds,
            self._generate_category_feeds,
            self._generate_tag_feeds,
            self._generate_translation_feeds,
            ]
        self._fallback_settings = False
        super(ContentGenerator, self).__init__(*args, **kwargs)
        if self.signals['init']:
            self.signals['init'].send(self)

    def get_setting(self, key, default=None, fallback=False):
        setting_name = self.name.upper()
        if fallback:
            default = self.settings.get(key, default)
        return self.settings.get('{}_{}'.format(setting_name, key), default)

    def _update_context(self, items):
        """Update the context with the given items from the currrent
        processor.

        Prefixes item keys with the generator name to avoid collisions
        beteween generators.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = value.items()
            key = '{}_{}'.format(self.name, item)
            self.context[key] = value

    def _content_paths(self):
        return [self.get_setting('DIR', default=os.curdir)]

    def generate_context(self):
        """Add the content into the shared context"""
        super(ContentGenerator, self).generate_context()
        exclude = self.get_setting('EXCLUDES', default=())
        contexts = set()
        for rel_path in self._content_paths():
            # we have to remove trailing slashes
            path = os.path.normpath(os.path.join(self.path, rel_path))
            for f in self.get_files(path, exclude=exclude):
                try:
                    content = read_file(
                        base_path=self.path, path=f,
                        content_class=self.content_class, fmt=self.fmt,
                        settings=self.settings, context=self.context,
                        preread_signal=self.signals['preread'],
                        preread_sender=self,
                        context_signal=self.signals['context'],
                        context_sender=self)
                except Exception as e:
                    logger.warning('Could not process {}\n{}'.format(f, e))
                    continue

                try:
                    new_contexts = self._process_content(content, f)
                except InvalidContent as e:
                    logger.warning('Could not process {}\n{}'.format(f, e))
                else:
                    contexts.update(new_contexts)

        contexts.update(self._process_context())

        self._update_context(contexts)

        if self.signals['finalized']:
            self.signals['finalized'].send(self)

    def _process_content(self, content, path):
        if (self._check_validity and 
                not pelican.contents.is_valid_content(content, path)):
            raise InvalidContent(content)

        self.add_source_path(content)
        self.all_content.append(content)

        status = getattr(content, 'status', None)
        if status == 'published':
            for tag in getattr(content, 'tags', []):
                self.tags[tag].append(content)
            self.contents.append(content)
        elif status == 'hidden':
            self.hidden.append(content)
        elif status == 'draft':
            self.drafts.append(content)
        else:
            logger.warning(
                'Unknown status {!r} for file {!r}, skipping it.'.format(
                    status, path))
        return set(('all_content', 'contents', 'tags', 'drafts'))

    def _process_context(self):
        contexts = set()
        for process in self._context_processors:
            contexts.update(process())
        return contexts

    def _process_translations(self):
        self.contents, self.translations = process_translations(
            self.contents)
        return set(('contents', 'translations'))

    def _process_hidden_translations(self):
        self.hidden, self.hidden_translations = process_translations(
            self.hidden)
        return set(('hidden', 'hidden_translations'))

    def _process_sort(self, all_content=None):
        # sort content by date.  Alternative sorting can be carried
        # out in the templates themselves.
        try:
            self.all_content.sort(key=attrgetter('date'), reverse=True)
            self.contents.sort(key=attrgetter('date'), reverse=True)
            self.hidden.sort(key=attrgetter('date'), reverse=True)
        except AttributeError as e:
            pass  # no 'date' attribute
        return set()

    def _process_categories(self, all_content=None):
        for content in self.contents:
            # only native content is listed in categories, not translations
            self.categories[content.category].append(content)
        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(reverse=self.settings['REVERSE_CATEGORY_ORDER'])
        return set(('categories',))

    def _process_authors(self, all_content=None):
        # ignore blank authors as well as undefined
        for content in self.contents:
            if hasattr(content, 'author') and content.author.name:
                self.authors[content.author].append(content)
        self.authors = list(self.authors.items())
        self.authors.sort()
        return set(('authors',))

    def _process_dates(self, all_content=None):
        self.dates = list(self.contents)
        try:
            self.dates.sort(
                key=attrgetter('date'),
                reverse=self.get_setting(
                    'NEWEST_FIRST_ARCHIVES', True, fallback=True))
        except AttributeError as e:
            pass  # no 'date' attribute
        return set(('dates',))

    def _process_tag_cloud(self, all_content=None):
        tag_cloud_max_items = self.get_setting(
            'TAG_CLOUD_MAX_ITEMS', 100, fallback=True)
        tag_cloud_steps = self.get_setting(
            'TAG_CLOUD_STEPS', 4, fallback=True)
        tag_cloud = defaultdict(int)
        for content in self.contents:
            for tag in getattr(content, 'tags', []):
                tag_cloud[tag] += 1

        tag_cloud = sorted(tag_cloud.items(), key=itemgetter(1), reverse=True)
        tag_cloud = tag_cloud[:tag_cloud_max_items]

        tags = list(map(itemgetter(1), tag_cloud))
        if tags:
            max_count = max(tags)

        # calculate word sizes
        self.tag_cloud = [
            (
                tag,
                int(math.floor(tag_cloud_steps -
                               (tag_cloud_steps - 1) * math.log(count) /
                               (math.log(max_count) or 1)))
            )
            for tag, count in tag_cloud
        ]

        # put words in chaos
        random.shuffle(self.tag_cloud)
        return set(('tag_cloud',))

    def generate_output(self, writer):
        super(ContentGenerator, self).generate_output(writer)
        for generator in self._generators:
            generator(writer=writer)

    def _generate_feeds(self, writer):
        """Generate the feeds from the current context, and output files."""
        feed_atom = self.get_setting(
            'FEED_ATOM', fallback=self._fallback_settings)
        if feed_atom:
            writer.write_feed(self.contents, self.context, feed_atom)

        feed_rss = self.get_setting(
            'FEED_RSS', fallback=self._fallback_settings)
        if feed_rss:
            writer.write_feed(
                self.contents, self.context, feed_rss, feed_type='rss')

    def _generate_all_feeds(self, writer):
        feed_atom = self.get_setting(
            'FEED_ALL_ATOM', fallback=self._fallback_settings)
        feed_rss = self.get_setting(
            'FEED_ALL_RSS', fallback=self._fallback_settings)
        if feed_atom or feed_rss:
            all_content = list(self.contents)
            for content in self.contents:
                all_content.extend(content.translations)
            self.all_content.sort(key=attrgetter('date'), reverse=True)
            if feed_atom:
                writer.write_feed(self.all_content, self.context, feed_atom)
            if feed_rss:
                writer.write_feed(
                    self.all_content, self.context, feed_rss, feed_type='rss')

    def _generate_category_feeds(self, writer):
        feed_atom = self.get_setting(
            'CATEGORY_FEED_ATOM', fallback=self._fallback_settings)
        feed_rss = self.get_setting(
            'CATEGORY_FEED_RSS', fallback=self._fallback_settings)
        if feed_atom or feed_rss:
            for cat, arts in self.categories:
                arts.sort(key=attrgetter('date'), reverse=True)
                if feed_atom:
                    writer.write_feed(
                        arts, self.context, feed_atom % cat)
                if feed_rss:
                    writer.write_feed(
                        arts, self.context, feed_rss % cat,feed_type='rss')

    def _generate_tag_feeds(self, writer):
        feed_atom = self.get_setting(
            'TAG_FEED_ATOM', fallback=self._fallback_settings)
        feed_rss = self.get_setting(
            'TAG_FEED_RSS', fallback=self._fallback_settings)
        if feed_atom or feed_rss:
            for tag, arts in self.tags.items():
                arts.sort(key=attrgetter('date'), reverse=True)
                if feed_atom:
                    writer.write_feed(
                        arts, self.context, feed_atom % tag)
                if feed_rss:
                    writer.write_feed(
                        arts, self.context, feed_rss % tag, feed_type='rss')

    def _generate_translation_feeds(self, writer):
        feed_atom = self.get_setting(
            'TRANSLATION_FEED_ATOM', fallback=self._fallback_settings)
        feed_rss = self.get_setting(
            'TRANSLATION_FEED_RSS', fallback=self._fallback_settings)
        if feed_atom or feed_rss:
            feeds = defaultdict(list)
            for content in chain(self.contents, self.translations):
                feeds[content.lang].append(content)

            for lang, items in feeds.items():
                items.sort(key=attrgetter('date'), reverse=True)
                if feed_atom:
                    writer.write_feed(items, self.context, feed_atom % lang)
                if feed_rss:
                    writer.write_feed(
                        items, self.context, feed_rss % lang, feed_type='rss')

    @relative_urls
    def _generate_content(self, writer):
        """Generate the content pages."""
        for content in chain(self.translations, self.contents):
            writer(content.save_as, self.get_template(content.template),
                   self.context, content=content, category=content.category)

    @relative_urls
    def _generate_hidden(self, writer):
        """Generate hidden content pages."""
        for content in chain(self.hidden_translations, self.hidden):
            writer(content.save_as, self.get_template(content.template),
                   self.context, content=content, category=content.category)

    @relative_urls
    def _generate_direct_templates(self, writer):
        """Generate direct templates pages

        This may not seem like a content-type specific generator, but
        the templates are paginated based on the particular content
        type.  For example, ARTICLE_PAGINATED_DIRECT_TEMPLATES and
        PAGE_PAGINATED_DIRECT_TEMPLATES will paginate by articles and
        pages respectively.
        """
        paginated_templates = self.get_setting(
            'PAGINATED_DIRECT_TEMPLATES', fallback=True)
        direct_templates = self.get_setting(
            'DIRECT_TEMPLATES', fallback=True)
        for template in direct_templates:
            paginated = {}
            if template in paginated_templates:
                paginated = {'contents': self.contents, 'dates': self.dates}
            save_as = self.get_setting(
                '{}_SAVE_AS'.format(template.upper()),
                '{}.html'.format(template),
                fallback=True)
            if not save_as:
                continue

            writer(save_as, self.get_template(template),
                   self.context, blog=True, paginated=paginated,
                   page_name=template)

    @relative_urls
    def _generate_tags(self, writer):
        """Generate Tags pages."""
        tag_template = self.get_template('tag')
        for tag, contents in self.tags.items():
            contents.sort(key=attrgetter('date'), reverse=True)
            dates = [content for content in self.dates if content in contents]
            writer(tag.save_as, tag_template, self.context, tag=tag,
                contents=contents, dates=dates,
                paginated={'contents': contents, 'dates': dates},
                page_name=tag.page_name)

    @relative_urls
    def _generate_categories(self, writer):
        """Generate category pages."""
        category_template = self.get_template('category')
        for cat, contents in self.categories:
            dates = [content for content in self.dates if content in contents]
            writer(cat.save_as, category_template, self.context,
                category=cat, contents=contents, dates=dates,
                paginated={'contents': contents, 'dates': dates},
                page_name=cat.page_name)

    @relative_urls
    def _generate_authors(self, writer):
        """Generate Author pages."""
        author_template = self.get_template('author')
        for aut, contents in self.authors:
            dates = [content for content in self.dates if content in contents]
            writer(aut.save_as, author_template, self.context,
                author=aut, contents=contents, dates=dates,
                paginated={'contents': contents, 'dates': dates},
                page_name=aut.page_name)

    @relative_urls
    def _generate_drafts(self, writer):
        """Generate drafts pages."""
        for content in self.drafts:
            writer(os.path.join('drafts', content.save_as),
                self.get_template(content.template), self.context,
                content=content, category=content.category)


class ArticlesGenerator(ContentGenerator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'article'
        super(ArticlesGenerator, self).__init__(*args, **kwargs)
        self._fallback_settings = True  # backwards compatibility


class PagesGenerator(ContentGenerator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'page'
        super(PagesGenerator, self).__init__(*args, **kwargs)
        self._generators = [
            # to minimize the number of relative path stuff modification
            # in writer, articles pass first
            self._generate_content,
            self._generate_hidden,
            ]


class StaticGenerator(ContentGenerator):
    """Copy static pages (images, medias etc.) to output"""

    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'static'
        super(StaticGenerator, self).__init__(*args, **kwargs)
        self._check_validity = False
        self._context_processors.insert(0, self._process_slugs)

        # don't try and match extensions for processing
        self.markup = False
        self.fmt = 'static'

    def _content_paths(self):
        return self.get_setting('PATHS', ())

    def _process_slugs(self):
        """Add slugs for process_translations"""
        for content in self.all_content:
            if 'slug' not in content.metadata:
                filename = os.path.basename(content.source_path)
                base, ext = os.path.splitext(filename)
                content.slug = content.metadata['slug'] = base
        return set()

    def _copy_paths(self, paths, source, destination, output_path,
            final_path=None):
        """Copy all the paths from source to destination"""
        for path in paths:
            copy(path, source, os.path.join(output_path, destination),
                 final_path, overwrite=True)

    def generate_output(self, writer):
        self._copy_paths(self.settings['THEME_STATIC_PATHS'], self.theme,
                         'theme', self.output_path, os.curdir)
        # copy all Static files
        for content in self.contents:
            source_path = os.path.join(self.path, content.source_path)
            save_as = os.path.join(self.output_path, content.save_as)
            mkdir_p(os.path.dirname(save_as))
            shutil.copy(source_path, save_as)
            logger.info('copying {} to {}'.format(
                    content.source_path, content.save_as))


class TemplatePagesGenerator(ContentGenerator):
    """Generate template pages

    This generator renders templates from the source directory (not
    from the theme) directly to the output.
    """
    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'template_page'
        super(TemplatePagesGenerator, self).__init__(*args, **kwargs)
        self._check_validity = False
        self._context_processors = []
        self._generators = [
            self._generate_content,
            ]

        # don't try and match extensions for processing
        self.markup = False
        self.fmt = 'static'

    def _content_paths(self):
        return self.get_setting('PATHS', ())

    @relative_urls
    def _generate_content(self, writer):
        for content in self.contents:
            self.env.loader.loaders.insert(
                0, _FileLoader(content.source_path, self.path))
            try:
                template = self.env.get_template(content.source_path)
                writer(content.save_as, template, self.context)
            finally:
                del self.env.loader.loaders[0]


class PdfGenerator(Generator):
    """Generate PDFs on the output dir, for all articles and pages coming from
    rst"""
    def __init__(self, *args, **kwargs):
        super(PdfGenerator, self).__init__(*args, **kwargs)
        try:
            from rst2pdf.createpdf import RstToPdf
            pdf_style_path = os.path.join(self.settings['PDF_STYLE_PATH']) \
                                if 'PDF_STYLE_PATH' in self.settings.keys() \
                                else ''
            pdf_style = self.settings['PDF_STYLE'] if 'PDF_STYLE' \
                                                    in self.settings.keys() \
                                                    else 'twelvepoint'
            self.pdfcreator = RstToPdf(breakside=0,
                                       stylesheets=[pdf_style],
                                       style_path=[pdf_style_path])
        except ImportError:
            raise Exception("unable to find rst2pdf")

    def _create_pdf(self, obj, output_path):
        if (obj.source_path.endswith('.rst') and
                getattr(obj, 'status', None) == 'published'):
            filename = obj.slug + '.pdf'
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

        for content in chain(
                self.context['article_all_content'],
                self.context['page_all_content'],
                ):
            self._create_pdf(article, pdf_path)


class SourceFileGenerator(Generator):
    def generate_context(self):
        self.output_extension = self.settings['OUTPUT_SOURCES_EXTENSION']

    def _create_source(self, obj, output_path):
        if getattr(obj, 'status', None) != 'published':
            return
        output_path = os.path.splitext(obj.save_as)[0]
        dest = os.path.join(output_path, output_path + self.output_extension)
        copy('', obj.source_path, dest)

    def generate_output(self, writer=None):
        logger.info(' Generating source files...')
        logger.info(u' Generating source files...')
        for object in chain(
                self.context['article_all_content'],
                self.context['page_all_content'],
                ):
            self._create_source(object, self.output_path)
