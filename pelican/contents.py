# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six
from six.moves.urllib.parse import urlparse, urlunparse

import copy
import locale
import logging
import functools
import os
import re
import sys

import pytz

from pelican import signals
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import (slugify, truncate_html_words, memoized, strftime,
                           python_2_unicode_compatible, deprecated_attribute,
                           path_to_url, posixize_path, set_date_tzinfo, SafeDatetime)

# Import these so that they're avalaible when you import from pelican.contents.
from pelican.urlwrappers import (URLWrapper, Author, Category, Tag)  # NOQA

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
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

        local_metadata = dict()
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

        # First, read the authors from "authors", if not, fallback to "author"
        # and if not use the settings defined one, if any.
        if not hasattr(self, 'author'):
            if hasattr(self, 'authors'):
                self.author = self.authors[0]
            elif 'AUTHOR' in settings:
                self.author = Author(settings['AUTHOR'], settings)

        if not hasattr(self, 'authors') and hasattr(self, 'author'):
            self.authors = [self.author]

        # XXX Split all the following code into pieces, there is too much here.

        # manage languages
        self.in_default_lang = True
        if 'DEFAULT_LANG' in settings:
            default_lang = settings['DEFAULT_LANG'].lower()
            if not hasattr(self, 'lang'):
                self.lang = default_lang

            self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing, generate slug according to
        # setting of SLUG_ATTRIBUTE
        if not hasattr(self, 'slug'):
            if settings['SLUGIFY_SOURCE'] == 'title' and hasattr(self, 'title'):
                self.slug = slugify(self.title,
                                settings.get('SLUG_SUBSTITUTIONS', ()))
            elif settings['SLUGIFY_SOURCE'] == 'basename' and source_path != None:
                basename = os.path.basename(os.path.splitext(source_path)[0])
                self.slug = slugify(basename,
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

        # manage timezone
        default_timezone = settings.get('TIMEZONE', 'UTC')
        timezone = getattr(self, 'timezone', default_timezone)

        if hasattr(self, 'date'):
            self.date = set_date_tzinfo(self.date, timezone)
            self.locale_date = strftime(self.date, self.date_format)

        if hasattr(self, 'modified'):
            self.modified = set_date_tzinfo(self.modified, timezone)
            self.locale_modified = strftime(self.modified, self.date_format)

        # manage status
        if not hasattr(self, 'status'):
            self.status = settings['DEFAULT_STATUS']
            if not settings['WITH_FUTURE_DATES'] and hasattr(self, 'date'):
                if self.date.tzinfo is None:
                    now = SafeDatetime.now()
                else:
                    now = SafeDatetime.utcnow().replace(tzinfo=pytz.utc)
                if self.date > now:
                    self.status = 'draft'

        # store the summary metadata if it is set
        if 'summary' in metadata:
            self._summary = metadata['summary']

        signals.content_object_init.send(self)

    def __str__(self):
        return self.source_path or repr(self)

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
        metadata.update({
            'path': path_to_url(path),
            'slug': getattr(self, 'slug', ''),
            'lang': getattr(self, 'lang', 'en'),
            'date': getattr(self, 'date', SafeDatetime.now()),
            'author': self.author.slug if hasattr(self, 'author') else '',
            'category': self.category.slug if hasattr(self, 'category') else ''
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
        suitable for the output content.

        :param content: content resource that will be passed to the templates.
        :param siteurl: siteurl which is locally generated by the writer in
                        case of RELATIVE_URLS.
        """
        if not content:
            return content

        instrasite_link_regex = self.settings['INTRASITE_LINK_REGEX']
        regex = r"""
            (?P<markup><\s*[^\>]*  # match tag with all url-value attributes
                (?:href|src|poster|data|cite|formaction|action)\s*=)

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
            if what in {'filename', 'attach'}:
                if path.startswith('/'):
                    path = path[1:]
                else:
                    # relative to the source path of this content
                    path = self.get_relative_source_path(
                        os.path.join(self.relative_dir, path)
                    )

                if path not in self._context['filenames']:
                    unquoted_path = path.replace('%20', ' ')

                    if unquoted_path in self._context['filenames']:
                        path = unquoted_path

                linked_content = self._context['filenames'].get(path)
                if linked_content:
                    if what == 'attach':
                        if isinstance(linked_content, Static):
                            linked_content.attach_to(self)
                        else:
                            logger.warning("%s used {attach} link syntax on a "
                                "non-static file. Use {filename} instead.",
                                self.get_relative_source_path())
                    origin = '/'.join((siteurl, linked_content.url))
                    origin = origin.replace('\\', '/')  # for Windows paths.
                else:
                    logger.warning(
                        "Unable to find `%s`, skipping url replacement.",
                        value.geturl(), extra = {
                            'limit_msg': ("Other resources were not found "
                                          "and their urls not replaced")})
            elif what == 'category':
                origin = '/'.join((siteurl, Category(path, self.settings).url))
            elif what == 'tag':
                origin = '/'.join((siteurl, Tag(path, self.settings).url))

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

    def get_siteurl(self):
        return self._context.get('localsiteurl', '')

    @property
    def content(self):
        return self.get_content(self.get_siteurl())

    def _get_summary(self):
        """Returns the summary of an article.

        This is based on the summary metadata if set, otherwise truncate the
        content.
        """
        if hasattr(self, '_summary'):
            return self._update_content(self._summary,
                                        self.get_siteurl())

        if self.settings['SUMMARY_MAX_LENGTH'] is None:
            return self.content

        return truncate_html_words(self.content,
                                   self.settings['SUMMARY_MAX_LENGTH'])

    @memoized
    def get_summary(self, siteurl):
        """uses siteurl to be memoizable"""
        return self._get_summary()

    @property
    def summary(self):
        return self.get_summary(self.get_siteurl())

    @summary.setter
    def summary(self, value):
        """Dummy function"""
        pass

    @property
    def url(self):
        return self.get_url_setting('url')

    @property
    def save_as(self):
        return self.get_url_setting('save_as')

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

        return posixize_path(
            os.path.relpath(
                os.path.abspath(os.path.join(self.settings['PATH'], source_path)),
                os.path.abspath(self.settings['PATH'])
            ))

    @property
    def relative_dir(self):
        return posixize_path(
            os.path.dirname(
                os.path.relpath(
                    os.path.abspath(self.source_path),
                    os.path.abspath(self.settings['PATH']))))


class Page(Content):
    mandatory_properties = ('title',)
    default_template = 'page'


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')
    default_template = 'article'


class Draft(Page):
    mandatory_properties = ('title', 'category')
    default_template = 'article'


class Quote(Page):
    base_properties = ('author', 'date')


@python_2_unicode_compatible
class Static(Page):
    def __init__(self, *args, **kwargs):
        super(Static, self).__init__(*args, **kwargs)
        self._output_location_referenced = False

    @deprecated_attribute(old='filepath', new='source_path', since=(3, 2, 0))
    def filepath():
        return None

    @deprecated_attribute(old='src', new='source_path', since=(3, 2, 0))
    def src():
        return None

    @deprecated_attribute(old='dst', new='save_as', since=(3, 2, 0))
    def dst():
        return None

    @property
    def url(self):
        # Note when url has been referenced, so we can avoid overriding it.
        self._output_location_referenced = True
        return super(Static, self).url

    @property
    def save_as(self):
        # Note when save_as has been referenced, so we can avoid overriding it.
        self._output_location_referenced = True
        return super(Static, self).save_as

    def attach_to(self, content):
        """Override our output directory with that of the given content object.
        """
        # Determine our file's new output path relative to the linking document.
        # If it currently lives beneath the linking document's source directory,
        # preserve that relationship on output. Otherwise, make it a sibling.
        linking_source_dir = os.path.dirname(content.source_path)
        tail_path = os.path.relpath(self.source_path, linking_source_dir)
        if tail_path.startswith(os.pardir + os.sep):
            tail_path = os.path.basename(tail_path)
        new_save_as = os.path.join(
            os.path.dirname(content.save_as), tail_path)

        # We do not build our new url by joining tail_path with the linking
        # document's url, because we cannot know just by looking at the latter
        # whether it points to the document itself or to its parent directory.
        # (An url like 'some/content' might mean a directory named 'some'
        # with a file named 'content', or it might mean a directory named
        # 'some/content' with a file named 'index.html'.) Rather than trying
        # to figure it out by comparing the linking document's url and save_as
        # path, we simply build our new url from our new save_as path.
        new_url = path_to_url(new_save_as)

        def _log_reason(reason):
            logger.warning("The {attach} link in %s cannot relocate %s "
                "because %s. Falling back to {filename} link behavior instead.",
                content.get_relative_source_path(),
                self.get_relative_source_path(), reason,
                extra={'limit_msg': "More {attach} warnings silenced."})

        # We never override an override, because we don't want to interfere
        # with user-defined overrides that might be in EXTRA_PATH_METADATA.
        if hasattr(self, 'override_save_as') or hasattr(self, 'override_url'):
            if new_save_as != self.save_as or new_url != self.url:
                _log_reason("its output location was already overridden")
            return

        # We never change an output path that has already been referenced,
        # because we don't want to break links that depend on that path.
        if self._output_location_referenced:
            if new_save_as != self.save_as or new_url != self.url:
                _log_reason("another link already referenced its location")
            return

        self.override_save_as = new_save_as
        self.override_url = new_url


def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError as e:
        logger.error("Skipping %s: could not find information about '%s'", f, e)
        return False
