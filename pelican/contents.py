# -*- coding: utf-8 -*-
import copy
import locale
import logging
import functools

from datetime import datetime
from os import getenv
from sys import platform, stdin


from pelican.settings import _DEFAULT_CONFIG
from pelican.utils import slugify, truncate_html_words


logger = logging.getLogger(__name__)

class Page(object):
    """Represents a page
    Given a content, and metadata, create an adequate object.

    :param content: the string to parse, containing the original content.
    """
    mandatory_properties = ('title',)
    default_template = 'page'

    def __init__(self, content, metadata=None, settings=None,
                 filename=None):
        # init parameters
        if not metadata:
            metadata = {}
        if not settings:
            settings = copy.deepcopy(_DEFAULT_CONFIG)

        self.settings = settings
        self._content = content
        self.translations = []

        local_metadata = dict(settings.get('DEFAULT_METADATA', ()))
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            setattr(self, key.lower(), value)

        # also keep track of the metadata attributes available
        self.metadata = local_metadata

        #default template if it's not defined in page
        self.template = self._get_template()

        # default author to the one in settings if not defined
        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = Author(settings['AUTHOR'], settings)
            else:
                title = filename.decode('utf-8') if filename else self.title
                self.author = Author(getenv('USER', 'John Doe'), settings)
                logger.warning(u"Author of `{0}' unknown, assuming that his name is "
                         "`{1}'".format(title, self.author))

        # manage languages
        self.in_default_lang = True
        if 'DEFAULT_LANG' in settings:
            default_lang = settings['DEFAULT_LANG'].lower()
            if not hasattr(self, 'lang'):
                self.lang = default_lang

            self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing, from the title
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
            encoded_date = self.date.strftime(
                    self.date_format.encode('ascii', 'xmlcharrefreplace'))

            if platform == 'win32':
                self.locale_date = encoded_date.decode(stdin.encoding)
            else:
                self.locale_date = encoded_date.decode('utf')

        # manage status
        if not hasattr(self, 'status'):
            self.status = settings['DEFAULT_STATUS']
            if not settings['WITH_FUTURE_DATES']:
                if hasattr(self, 'date') and self.date > datetime.now():
                    self.status = 'draft'

        # store the summary metadata if it is set
        if 'summary' in metadata:
            self._summary = metadata['summary']

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

    def _expand_settings(self, key):
        fq_key = ('%s_%s' % (self.__class__.__name__, key)).upper()
        return self.settings[fq_key].format(**self.url_format)

    def get_url_setting(self, key):
        key = key if self.in_default_lang else 'lang_%s' % key
        return self._expand_settings(key)

    @property
    def content(self):
        if hasattr(self, "_get_content"):
            content = self._get_content()
        else:
            content = self._content
        return content

    def _get_summary(self):
        """Returns the summary of an article, based on the summary metadata
        if it is set, else truncate the content."""
        if hasattr(self, '_summary'):
            return self._summary
        else:
            if self.settings['SUMMARY_MAX_LENGTH']:
                return truncate_html_words(self.content, self.settings['SUMMARY_MAX_LENGTH'])
            return self.content

    def _set_summary(self, summary):
        """Dummy function"""
        pass

    summary = property(_get_summary, _set_summary, "Summary of the article."
                       "Based on the content. Can't be set")

    url = property(functools.partial(get_url_setting, key='url'))
    save_as = property(functools.partial(get_url_setting, key='save_as'))

    def _get_template(self):
        if hasattr(self, 'template') and self.template is not None:
            return self.template
        else:
            return self.default_template


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article'


class Quote(Page):
    base_properties = ('author', 'date')


class URLWrapper(object):
    def __init__(self, name, settings):
        self.name = unicode(name)
        self.slug = slugify(self.name)
        self.settings = settings

    def as_dict(self):
        return self.__dict__

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == unicode(other)

    def __str__(self):
        return str(self.name.encode('utf-8', 'replace'))

    def __unicode__(self):
        return self.name

    def _from_settings(self, key):
        setting = "%s_%s" % (self.__class__.__name__.upper(), key)
        value = self.settings[setting]
        if not isinstance(value, basestring):
            logger.warning(u'%s is set to %s' % (setting, value))
            return value
        else:
            return unicode(value).format(**self.as_dict())

    url = property(functools.partial(_from_settings, key='URL'))
    save_as = property(functools.partial(_from_settings, key='SAVE_AS'))


class Category(URLWrapper):
    pass


class Tag(URLWrapper):
    def __init__(self, name, *args, **kwargs):
        super(Tag, self).__init__(unicode.strip(name), *args, **kwargs)


class Author(URLWrapper):
    pass


def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError, e:
        logger.error(u"Skipping %s: impossible to find informations about '%s'"\
                % (f, e))
        return False
