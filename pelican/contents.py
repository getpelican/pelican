# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import copy
import locale
import logging
import functools
import os
import re
import sys

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

from datetime import datetime


from pelican import signals
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import (slugify, truncate_html_words, memoized, strftime,
                           python_2_unicode_compatible, deprecated_attribute,
                           path_to_url)

# Import these so that they're avalaible when you import from pelican.contents.
from pelican.urlwrappers import (URLWrapper, Author, Category, Tag)  # NOQA

logger = logging.getLogger(__name__)


class Content(object):
    """Represents a content.

    :param content: the string to parse, containing the original content.
    :param metadata: the metadata associated to this page (optional).
    :param settings: the settings dictionary (optional).
    :param source_path: The location of the source of this content (if any).
    :param context: The shared context between generators.

    """
    @deprecated_attribute(old='filename', new='source_path', since=(3, 2, 0))
    def filename():
        return None

    def __init__(self, content, metadata=None, settings=None,
                 source_path=None, context=None):
        if metadata is None:
            metadata = {}
        if settings is None:
            settings = copy.deepcopy(DEFAULT_CONFIG)

        self.settings = settings
        self._content = content
        if context is None:
            context = {}
        self._context = context
        self.translations = []

        local_metadata = dict(settings['DEFAULT_METADATA'])
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            if key in ('save_as', 'url'):
                key = 'override_' + key
            setattr(self, key.lower(), value)

        # also keep track of the metadata attributes available
        self.metadata = local_metadata

        #default template if it's not defined in page
        self.template = self._get_template()

        # default author to the one in settings if not defined
        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = Author(settings['AUTHOR'], settings)

        # XXX Split all the following code into pieces, there is too much here.

        # manage languages
        self.in_default_lang = True
        if 'DEFAULT_LANG' in settings:
            default_lang = settings['DEFAULT_LANG'].lower()
            if not hasattr(self, 'lang'):
                self.lang = default_lang

            self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing, from the title
        if not hasattr(self, 'slug') and hasattr(self, 'title'):
            self.slug = slugify(self.title,
                                settings.get('SLUG_SUBSTITUTIONS', ()))

        self.source_path = source_path

        # manage the date format
        if not hasattr(self, 'date_format'):
            if hasattr(self, 'lang') and self.lang in settings['DATE_FORMATS']:
                self.date_format = settings['DATE_FORMATS'][self.lang]
            else:
                self.date_format = settings['DEFAULT_DATE_FORMAT']

        if isinstance(self.date_format, tuple):
            locale_string = self.date_format[0]
            if sys.version_info < (3, ) and isinstance(locale_string,
                                                       six.text_type):
                locale_string = locale_string.encode('ascii')
            locale.setlocale(locale.LC_ALL, locale_string)
            self.date_format = self.date_format[1]

        if hasattr(self, 'date'):
            self.locale_date = strftime(self.date, self.date_format)

        # manage status
        if not hasattr(self, 'status'):
            self.status = settings['DEFAULT_STATUS']
            if not settings['WITH_FUTURE_DATES']:
                if hasattr(self, 'date') and self.date > datetime.now():
                    self.status = 'draft'

        # store the summary metadata if it is set
        if 'summary' in metadata:
            self._summary = metadata['summary']

        signals.content_object_init.send(self)

    def __str__(self):
        if self.source_path is None:
            return repr(self)
        elif six.PY3:
            return self.source_path or repr(self)
        else:
            return str(self.source_path.encode('utf-8', 'replace'))

    def check_properties(self):
        """Test mandatory properties are set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                raise NameError(prop)

    @property
    def url_format(self):
        """Returns the URL, formatted with the proper values"""
        metadata = copy.copy(self.metadata)
        path = self.metadata.get('path', self.get_relative_source_path())
        default_category = self.settings['DEFAULT_CATEGORY']
        slug_substitutions = self.settings.get('SLUG_SUBSTITUTIONS', ())
        metadata.update({
            'path': path_to_url(path),
            'slug': getattr(self, 'slug', ''),
            'lang': getattr(self, 'lang', 'en'),
            'date': getattr(self, 'date', datetime.now()),
            'author': slugify(
                getattr(self, 'author', ''),
                slug_substitutions
            ),
            'category': slugify(
                getattr(self, 'category', default_category),
                slug_substitutions
            )
        })
        return metadata

    def _expand_settings(self, key):
        fq_key = ('%s_%s' % (self.__class__.__name__, key)).upper()
        return self.settings[fq_key].format(**self.url_format)

    def get_url_setting(self, key):
        if hasattr(self, 'override_' + key):
            return getattr(self, 'override_' + key)
        key = key if self.in_default_lang else 'lang_%s' % key
        return self._expand_settings(key)

    def _update_content(self, content, siteurl):
        """Update the content attribute.

        Change all the relative paths of the content to relative paths
        suitable for the ouput content.

        :param content: content resource that will be passed to the templates.
        :param siteurl: siteurl which is locally generated by the writer in
                        case of RELATIVE_URLS.
        """
        if not content:
            return content

        instrasite_link_regex = self.settings['INTRASITE_LINK_REGEX']
        regex = r"""
            (?P<markup><\s*[^\>]*  # match tag with src and href attr
                (?:href|src)\s*=)

            (?P<quote>["\'])      # require value to be quoted
            (?P<path>{0}(?P<value>.*?))  # the url value
            \2""".format(instrasite_link_regex)
        hrefs = re.compile(regex, re.X)

        def replacer(m):
            what = m.group('what')
            value = urlparse(m.group('value'))
            path = value.path
            origin = m.group('path')

            # XXX Put this in a different location.
            if what == 'filename':
                if path.startswith('/'):
                    path = path[1:]
                else:
                    # relative to the source path of this content
                    path = self.get_relative_source_path(
                        os.path.join(self.relative_dir, path)
                    )

                if path in self._context['filenames']:
                    origin = '/'.join((siteurl,
                             self._context['filenames'][path].url))
                    origin = origin.replace('\\', '/')  # for Windows paths.
                elif path.replace('%20', ' ') in self._context['filenames']:
                    path_with_spaces = path.replace('%20', ' ')
                    origin = '/'.join((siteurl,
                             self._context['filenames'][path_with_spaces].url))
                    origin = origin.replace('\\', '/')  # for Windows paths.
                else:
                    logger.warning("Unable to find {fn}, skipping url"
                                   " replacement".format(fn=path))
            elif what == 'category':
                origin = Category(path, self.settings).url
            elif what == 'tag':
                origin = Tag(path, self.settings).url

            # keep all other parts, such as query, fragment, etc.
            parts = list(value)
            parts[2] = origin
            origin = urlunparse(parts)

            return ''.join((m.group('markup'), m.group('quote'), origin,
                            m.group('quote')))

        return hrefs.sub(replacer, content)

    @memoized
    def get_content(self, siteurl):

        if hasattr(self, '_get_content'):
            content = self._get_content()
        else:
            content = self._content
        return self._update_content(content, siteurl)

    @property
    def content(self):
        return self.get_content(self._context.get('localsiteurl', ''))

    def _get_summary(self):
        """Returns the summary of an article.

        This is based on the summary metadata if set, otherwise truncate the
        content.
        """
        if hasattr(self, '_summary'):
            return self._summary

        if self.settings['SUMMARY_MAX_LENGTH'] is None:
            return self.content

        return truncate_html_words(self.content,
                                   self.settings['SUMMARY_MAX_LENGTH'])

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

    def get_relative_source_path(self, source_path=None):
        """Return the relative path (from the content path) to the given
        source_path.

        If no source path is specified, use the source path of this
        content object.
        """
        if not source_path:
            source_path = self.source_path
        if source_path is None:
            return None

        return os.path.relpath(
            os.path.abspath(os.path.join(self.settings['PATH'], source_path)),
            os.path.abspath(self.settings['PATH'])
        )

    @property
    def relative_dir(self):
        return os.path.dirname(os.path.relpath(
            os.path.abspath(self.source_path),
            os.path.abspath(self.settings['PATH']))
        )


class Page(Content):
    mandatory_properties = ('title',)
    default_template = 'page'


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article'


class Quote(Page):
    base_properties = ('author', 'date')


@python_2_unicode_compatible
class Static(Page):
    @deprecated_attribute(old='filepath', new='source_path', since=(3, 2, 0))
    def filepath():
        return None

    @deprecated_attribute(old='src', new='source_path', since=(3, 2, 0))
    def src():
        return None

    @deprecated_attribute(old='dst', new='save_as', since=(3, 2, 0))
    def dst():
        return None


def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError as e:
        logger.error("Skipping %s: could not find information about "
                     "'%s'" % (f, e))
        return False
