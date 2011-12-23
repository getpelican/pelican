# -*- coding: utf-8 -*-
import datetime
from os import getenv
from sys import platform, stdin
import locale

from pelican.log import *
from pelican.settings import _DEFAULT_CONFIG
from pelican.utils import slugify, truncate_html_words

class Page(object):
    """Represents a page
    Given a content, and metadata, create an adequate object.

    :param content: the string to parse, containing the original content.
    """
    mandatory_properties = ('title',)

    def __init__(self, content, metadata=None, settings=None,
                 filename=None):
        # init parameters
        if not metadata:
            metadata = {}
        if not settings:
            settings = _DEFAULT_CONFIG

        self.settings = settings
        self._content = content
        self.translations = []

        local_metadata = dict(settings.get('DEFAULT_METADATA', ()))
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            setattr(self, key.lower(), value)

        # default author to the one in settings if not defined
        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = Author(settings['AUTHOR'], settings)
            else:
                self.author = Author(getenv('USER', 'John Doe'), settings)
                warning(u"Author of `{0}' unknow, assuming that his name is `{1}'".format(filename or self.title, self.author))

        # manage languages
        self.in_default_lang = True
        if 'DEFAULT_LANG' in settings:
            default_lang = settings['DEFAULT_LANG'].lower()
            if not hasattr(self, 'lang'):
                self.lang = default_lang

            self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing, fro mthe title
        if not hasattr(self, 'slug') and hasattr(self, 'title'):
            self.slug = slugify(self.title)

        if filename:
            self.filename = filename

        # manage the date format
        if not hasattr(self, 'date_format'):
            if hasattr(self, 'lang') and self.lang in settings['DATE_FORMATS']:
                self.date_format = settings['DATE_FORMATS'][self.lang]
            else:
                self.date_format = settings['DEFAULT_DATE_FORMAT']

        if isinstance(self.date_format, tuple):
            locale.setlocale(locale.LC_ALL, self.date_format[0])
            self.date_format = self.date_format[1]

        if hasattr(self, 'date'):
            if platform == 'win32':
                self.locale_date = self.date.strftime(self.date_format.encode('ascii','xmlcharrefreplace')).decode(stdin.encoding)
            else:
                self.locale_date = self.date.strftime(self.date_format.encode('ascii','xmlcharrefreplace')).decode('utf')

        # manage status
        if not hasattr(self, 'status'):
            self.status = settings['DEFAULT_STATUS']
            if not settings['WITH_FUTURE_DATES']:
                if hasattr(self, 'date') and self.date > datetime.datetime.now():
                    self.status = 'draft'

        # set summary
        if not hasattr(self, 'summary'):
            self.summary = truncate_html_words(self.content, 50)

    def check_properties(self):
        """test that each mandatory property is set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                raise NameError(prop)

    @property
    def url_format(self):
        return {
            'slug': getattr(self, 'slug', ''),
            'lang': getattr(self, 'lang', 'en'),
            'date': getattr(self, 'date', datetime.now()),
            'author': self.author,
            'category': getattr(self, 'category', 'misc'),
        }

    @property
    def url(self):
        if self.in_default_lang:
            return self.settings.get('PAGE_URL', 'pages/{slug}.html').format(**self.url_format)

        return self.settings.get('PAGE_LANG_URL', 'pages/{slug}-{lang}.html').format(**self.url_format)

    @property
    def save_as(self):
        if self.in_default_lang:
            return self.settings.get('PAGE_SAVE_AS', 'pages/{slug}.html').format(**self.url_format)

        return self.settings.get('PAGE_LANG_SAVE_AS', 'pages/{slug}-{lang}.html').format(**self.url_format)

    @property
    def content(self):
        if hasattr(self, "_get_content"):
            content = self._get_content()
        else:
            content = self._content
        return content

    def _get_summary(self):
        """Returns the summary of an article, based on to the content"""
        return truncate_html_words(self.content, 50)

    def _set_summary(self, summary):
        """Dummy function"""
        pass

    summary = property(_get_summary, _set_summary,
                       "Summary of the article. Based on the content. Can't be set")


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')

    @property
    def url(self):
        if self.in_default_lang:
            return self.settings.get('ARTICLE_URL', '{slug}.html').format(**self.url_format)

        return self.settings.get('ARTICLE_LANG_URL', '{slug}-{lang}.html').format(**self.url_format)

    @property
    def save_as(self):
        if self.in_default_lang:
            return self.settings.get('ARTICLE_SAVE_AS', '{slug}.html').format(**self.url_format)

        return self.settings.get('ARTICLE_LANG_SAVE_AS', '{slug}-{lang}.html').format(**self.url_format)


class Quote(Page):
    base_properties = ('author', 'date')

class URLWrapper(object):
    def __init__(self, name, settings):
        self.name = unicode(name)
        self.settings = settings

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == unicode(other)

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return '%s.html' % self.name

class Category(URLWrapper):
    @property
    def url(self):
        return self.settings.get('CATEGORY_URL', 'category/{name}.html').format(name=self.name)

    @property
    def save_as(self):
        return self.settings.get('CATEGORY_SAVE_AS', 'category/{name}.html').format(name=self.name)

class Tag(URLWrapper):
    def __init__(self, name, *args, **kwargs):
        super(Tag, self).__init__(unicode.strip(name), *args, **kwargs)

    @property
    def url(self):
        return self.settings.get('TAG_URL', 'tag/{name}.html').format(name=self.name)

    @property
    def save_as(self):
        return self.settings.get('TAG_SAVE_AS', 'tag/{name}.html').format(name=self.name)

class Author(URLWrapper):
    @property
    def url(self):
        return self.settings.get('AUTHOR_URL', 'author/{name}.html').format(name=self.name)

    @property
    def save_as(self):
        return self.settings.get('AUTHOR_SAVE_AS', 'author/{name}.html').format(name=self.name)

def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError, e:
        error(u"Skipping %s: impossible to find informations about '%s'" % (f, e))
        return False
