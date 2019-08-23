# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import copy
import locale
import logging
import os
import re
import sys

import pytz

import six
from six.moves.urllib.parse import urljoin, urlparse, urlunparse

from pelican import signals
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import (SafeDatetime, deprecated_attribute, memoized,
                           path_to_url, posixize_path,
                           python_2_unicode_compatible, sanitised_join,
                           set_date_tzinfo, slugify, strftime,
                           truncate_html_words)

# Import these so that they're avalaible when you import from pelican.contents.
from pelican.urlwrappers import (Author, Category, Tag, URLWrapper)  # NOQA

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

        # default template if it's not defined in page
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
            if (settings['SLUGIFY_SOURCE'] == 'title' and
                    hasattr(self, 'title')):
                self.slug = slugify(
                    self.title,
                    regex_subs=settings.get('SLUG_REGEX_SUBSTITUTIONS', []))
            elif (settings['SLUGIFY_SOURCE'] == 'basename' and
                    source_path is not None):
                basename = os.path.basename(
                    os.path.splitext(source_path)[0])
                self.slug = slugify(
                    basename,
                    regex_subs=settings.get('SLUG_REGEX_SUBSTITUTIONS', []))

        self.source_path = source_path
        self.relative_source_path = self.get_relative_source_path()

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
            # Previous default of None broke comment plugins and perhaps others
            self.status = getattr(self, 'default_status', '')

        # store the summary metadata if it is set
        if 'summary' in metadata:
            self._summary = metadata['summary']

        signals.content_object_init.send(self)

    def __str__(self):
        return self.source_path or repr(self)

    def _has_valid_mandatory_properties(self):
        """Test mandatory properties are set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                logger.error(
                    "Skipping %s: could not find information about '%s'",
                    self, prop)
                return False
        return True

    def _has_valid_save_as(self):
        """Return true if save_as doesn't write outside output path, false
        otherwise."""
        try:
            output_path = self.settings["OUTPUT_PATH"]
        except KeyError:
            # we cannot check
            return True

        try:
            sanitised_join(output_path, self.save_as)
        except RuntimeError:  # outside output_dir
            logger.error(
                "Skipping %s: file %r would be written outside output path",
                self,
                self.save_as,
            )
            return False

        return True

    def _has_valid_status(self):
        if hasattr(self, 'allowed_statuses'):
            if self.status not in self.allowed_statuses:
                logger.error(
                    "Unknown status '%s' for file %s, skipping it.",
                    self.status,
                    self
                )
                return False

        # if undefined we allow all
        return True

    def is_valid(self):
        """Validate Content"""
        # Use all() to not short circuit and get results of all validations
        return all([self._has_valid_mandatory_properties(),
                    self._has_valid_save_as(),
                    self._has_valid_status()])

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

    def _expand_settings(self, key, klass=None):
        if not klass:
            klass = self.__class__.__name__
        fq_key = ('%s_%s' % (klass, key)).upper()
        return self.settings[fq_key].format(**self.url_format)

    def get_url_setting(self, key):
        if hasattr(self, 'override_' + key):
            return getattr(self, 'override_' + key)
        key = key if self.in_default_lang else 'lang_%s' % key
        return self._expand_settings(key)

    def _link_replacer(self, siteurl, m):
        what = m.group('what')
        value = urlparse(m.group('value'))
        path = value.path
        origin = m.group('path')

        # urllib.parse.urljoin() produces `a.html` for urljoin("..", "a.html")
        # so if RELATIVE_URLS are enabled, we fall back to os.path.join() to
        # properly get `../a.html`. However, os.path.join() produces
        # `baz/http://foo/bar.html` for join("baz", "http://foo/bar.html")
        # instead of correct "http://foo/bar.html", so one has to pick a side
        # as there is no silver bullet.
        if self.settings['RELATIVE_URLS']:
            joiner = os.path.join
        else:
            joiner = urljoin

            # However, it's not *that* simple: urljoin("blog", "index.html")
            # produces just `index.html` instead of `blog/index.html` (unlike
            # os.path.join()), so in order to get a correct answer one needs to
            # append a trailing slash to siteurl in that case. This also makes
            # the new behavior fully compatible with Pelican 3.7.1.
            if not siteurl.endswith('/'):
                siteurl += '/'

        # XXX Put this in a different location.
        if what in {'filename', 'static', 'attach'}:
            if path.startswith('/'):
                path = path[1:]
            else:
                # relative to the source path of this content
                path = self.get_relative_source_path(
                    os.path.join(self.relative_dir, path)
                )

            key = 'static_content' if what in ('static', 'attach')\
                else 'generated_content'

            def _get_linked_content(key, path):
                try:
                    return self._context[key][path]
                except KeyError:
                    try:
                        # Markdown escapes spaces, try unescaping
                        return self._context[key][path.replace('%20', ' ')]
                    except KeyError:
                        if what == 'filename' and key == 'generated_content':
                            key = 'static_content'
                            linked_content = _get_linked_content(key, path)
                            if linked_content:
                                logger.warning(
                                    '{filename} used for linking to static'
                                    ' content %s in %s. Use {static} instead',
                                    path,
                                    self.get_relative_source_path())
                                return linked_content
                        return None

            linked_content = _get_linked_content(key, path)
            if linked_content:
                if what == 'attach':
                    linked_content.attach_to(self)
                origin = joiner(siteurl, linked_content.url)
                origin = origin.replace('\\', '/')  # for Windows paths.
            else:
                logger.warning(
                    "Unable to find '%s', skipping url replacement.",
                    value.geturl(), extra={
                        'limit_msg': ("Other resources were not found "
                                      "and their urls not replaced")})
        elif what == 'category':
            origin = joiner(siteurl, Category(path, self.settings).url)
        elif what == 'tag':
            origin = joiner(siteurl, Tag(path, self.settings).url)
        elif what == 'index':
            origin = joiner(siteurl, self.settings['INDEX_SAVE_AS'])
        elif what == 'author':
            origin = joiner(siteurl, Author(path, self.settings).url)
        else:
            logger.warning(
                "Replacement Indicator '%s' not recognized, "
                "skipping replacement",
                what)

        # keep all other parts, such as query, fragment, etc.
        parts = list(value)
        parts[2] = origin
        origin = urlunparse(parts)

        return ''.join((m.group('markup'), m.group('quote'), origin,
                        m.group('quote')))

    def _get_intrasite_link_regex(self):
        intrasite_link_regex = self.settings['INTRASITE_LINK_REGEX']
        regex = r"""
            (?P<markup><[^\>]+  # match tag with all url-value attributes
                (?:href|src|poster|data|cite|formaction|action)\s*=\s*)

            (?P<quote>["\'])      # require value to be quoted
            (?P<path>{0}(?P<value>.*?))  # the url value
            \2""".format(intrasite_link_regex)
        return re.compile(regex, re.X)

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

        hrefs = self._get_intrasite_link_regex()
        return hrefs.sub(lambda m: self._link_replacer(siteurl, m), content)

    def get_static_links(self):
        static_links = set()
        hrefs = self._get_intrasite_link_regex()
        for m in hrefs.finditer(self._content):
            what = m.group('what')
            value = urlparse(m.group('value'))
            path = value.path
            if what not in {'static', 'attach'}:
                continue
            if path.startswith('/'):
                path = path[1:]
            else:
                # relative to the source path of this content
                path = self.get_relative_source_path(
                    os.path.join(self.relative_dir, path)
                )
            path = path.replace('%20', ' ')
            static_links.add(path)
        return static_links

    def get_siteurl(self):
        return self._context.get('localsiteurl', '')

    @memoized
    def get_content(self, siteurl):
        if hasattr(self, '_get_content'):
            content = self._get_content()
        else:
            content = self._content
        return self._update_content(content, siteurl)

    @property
    def content(self):
        return self.get_content(self.get_siteurl())

    @memoized
    def get_summary(self, siteurl):
        """Returns the summary of an article.

        This is based on the summary metadata if set, otherwise truncate the
        content.
        """
        if 'summary' in self.metadata:
            return self.metadata['summary']

        if self.settings['SUMMARY_MAX_LENGTH'] is None:
            return self.content

        return truncate_html_words(self.content,
                                   self.settings['SUMMARY_MAX_LENGTH'])

    @property
    def summary(self):
        return self.get_summary(self.get_siteurl())

    def _get_summary(self):
        """deprecated function to access summary"""

        logger.warning('_get_summary() has been deprecated since 3.6.4. '
                       'Use the summary decorator instead')
        return self.summary

    @summary.setter
    def summary(self, value):
        """Dummy function"""
        pass

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        # TODO maybe typecheck
        self._status = value.lower()

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
                os.path.abspath(os.path.join(
                    self.settings['PATH'],
                    source_path)),
                os.path.abspath(self.settings['PATH'])
            ))

    @property
    def relative_dir(self):
        return posixize_path(
            os.path.dirname(
                os.path.relpath(
                    os.path.abspath(self.source_path),
                    os.path.abspath(self.settings['PATH']))))

    def refresh_metadata_intersite_links(self):
        for key in self.settings['FORMATTED_FIELDS']:
            if key in self.metadata and key != 'summary':
                value = self._update_content(
                    self.metadata[key],
                    self.get_siteurl()
                )
                self.metadata[key] = value
                setattr(self, key.lower(), value)

        # _summary is an internal variable that some plugins may be writing to,
        # so ensure changes to it are picked up
        if ('summary' in self.settings['FORMATTED_FIELDS'] and
                'summary' in self.metadata):
            self._summary = self._update_content(
                self._summary,
                self.get_siteurl()
            )
            self.metadata['summary'] = self._summary


class Page(Content):
    mandatory_properties = ('title',)
    allowed_statuses = ('published', 'hidden', 'draft')
    default_status = 'published'
    default_template = 'page'

    def _expand_settings(self, key):
        klass = 'draft_page' if self.status == 'draft' else None
        return super(Page, self)._expand_settings(key, klass)


class Article(Content):
    mandatory_properties = ('title', 'date', 'category')
    allowed_statuses = ('published', 'draft')
    default_status = 'published'
    default_template = 'article'

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)

        # handle WITH_FUTURE_DATES (designate article to draft based on date)
        if not self.settings['WITH_FUTURE_DATES'] and hasattr(self, 'date'):
            if self.date.tzinfo is None:
                now = SafeDatetime.now()
            else:
                now = SafeDatetime.utcnow().replace(tzinfo=pytz.utc)
            if self.date > now:
                self.status = 'draft'

        # if we are a draft and there is no date provided, set max datetime
        if not hasattr(self, 'date') and self.status == 'draft':
            self.date = SafeDatetime.max

    def _expand_settings(self, key):
        klass = 'draft' if self.status == 'draft' else 'article'
        return super(Article, self)._expand_settings(key, klass)


@python_2_unicode_compatible
class Static(Content):
    mandatory_properties = ('title',)
    default_status = 'published'
    default_template = None

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

        # Determine our file's new output path relative to the linking
        # document. If it currently lives beneath the linking
        # document's source directory, preserve that relationship on output.
        # Otherwise, make it a sibling.

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
            logger.warning(
                "The {attach} link in %s cannot relocate "
                "%s because %s. Falling back to "
                "{filename} link behavior instead.",
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
