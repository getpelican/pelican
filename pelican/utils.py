# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import codecs
import errno
import fnmatch
import locale
import logging
import os
import pytz
import re
import shutil
import sys
import traceback
import pickle
import datetime

from collections import Hashable
from contextlib import contextmanager
import dateutil.parser
from functools import partial
from itertools import groupby
from jinja2 import Markup
from operator import attrgetter
from posixpath import join as posix_join

logger = logging.getLogger(__name__)


def strftime(date, date_format):
    '''
    Replacement for built-in strftime

    This is necessary because of the way Py2 handles date format strings.
    Specifically, Py2 strftime takes a bytestring. In the case of text output
    (e.g. %b, %a, etc), the output is encoded with an encoding defined by
    locale.LC_TIME. Things get messy if the formatting string has chars that
    are not valid in LC_TIME defined encoding.

    This works by 'grabbing' possible format strings (those starting with %),
    formatting them with the date, (if necessary) decoding the output and
    replacing formatted output back.
    '''

    c89_directives = 'aAbBcdfHIjmMpSUwWxXyYzZ%'
    strip_zeros = lambda x: x.lstrip('0') or '0'

    # grab candidate format options
    format_options = '%[-]?.'
    candidates = re.findall(format_options, date_format)

    # replace candidates with placeholders for later % formatting
    template = re.sub(format_options, '%s', date_format)

    # we need to convert formatted dates back to unicode in Py2
    # LC_TIME determines the encoding for built-in strftime outputs
    lang_code, enc = locale.getlocale(locale.LC_TIME)

    formatted_candidates = []
    for candidate in candidates:
        # test for valid C89 directives only
        if candidate[-1] in c89_directives:
            # check for '-' prefix
            if len(candidate) == 3:
                # '-' prefix
                candidate = '%{}'.format(candidate[-1])
                conversion = strip_zeros
            else:
                conversion = None

            # format date
            if isinstance(date, SafeDatetime):
                formatted = date.strftime(candidate, safe=False)
            else:
                formatted = date.strftime(candidate)

            # convert Py2 result to unicode
            if not six.PY3 and enc is not None:
                formatted = formatted.decode(enc)

            # strip zeros if '-' prefix is used
            if conversion:
                formatted = conversion(formatted)
        else:
            formatted = candidate
        formatted_candidates.append(formatted)

    # put formatted candidates back and return
    return template % tuple(formatted_candidates)


class SafeDatetime(datetime.datetime):
    '''Subclass of datetime that works with utf-8 format strings on PY2'''

    def strftime(self, fmt, safe=True):
        '''Uses our custom strftime if supposed to be *safe*'''
        if safe:
            return strftime(self, fmt)
        else:
            return super(SafeDatetime, self).strftime(fmt)


class DateFormatter(object):
    '''A date formatter object used as a jinja filter

    Uses the `strftime` implementation and makes sure jinja uses the locale
    defined in LOCALE setting
    '''

    def __init__(self):
        self.locale = locale.setlocale(locale.LC_TIME)

    def __call__(self, date, date_format):
        old_lc_time = locale.setlocale(locale.LC_TIME)
        old_lc_ctype = locale.setlocale(locale.LC_CTYPE)

        locale.setlocale(locale.LC_TIME, self.locale)
        # on OSX, encoding from LC_CTYPE determines the unicode output in PY3
        # make sure it's same as LC_TIME
        locale.setlocale(locale.LC_CTYPE, self.locale)

        formatted = strftime(date, date_format)

        locale.setlocale(locale.LC_TIME, old_lc_time)
        locale.setlocale(locale.LC_CTYPE, old_lc_ctype)
        return formatted


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.

    From django.utils.encoding.
    """
    if not six.PY3:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


class memoized(object):
    """Function decorator to cache return values.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return partial(self.__call__, obj)


def deprecated_attribute(old, new, since=None, remove=None, doc=None):
    """Attribute deprecation decorator for gentle upgrades

    For example:

        class MyClass (object):
            @deprecated_attribute(
                old='abc', new='xyz', since=(3, 2, 0), remove=(4, 1, 3))
            def abc(): return None

            def __init__(self):
                xyz = 5

    Note that the decorator needs a dummy method to attach to, but the
    content of the dummy method is ignored.
    """
    def _warn():
        version = '.'.join(six.text_type(x) for x in since)
        message = ['{} has been deprecated since {}'.format(old, version)]
        if remove:
            version = '.'.join(six.text_type(x) for x in remove)
            message.append(
                ' and will be removed by version {}'.format(version))
        message.append('.  Use {} instead.'.format(new))
        logger.warning(''.join(message))
        logger.debug(''.join(
                six.text_type(x) for x in traceback.format_stack()))

    def fget(self):
        _warn()
        return getattr(self, new)

    def fset(self, value):
        _warn()
        setattr(self, new, value)

    def decorator(dummy):
        return property(fget=fget, fset=fset, doc=doc)

    return decorator


def get_date(string):
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValueError.
    """
    string = re.sub(' +', ' ', string)
    default = SafeDatetime.now().replace(hour=0, minute=0,
                                        second=0, microsecond=0)
    try:
        return dateutil.parser.parse(string, default=default)
    except (TypeError, ValueError):
        raise ValueError('{0!r} is not a valid date'.format(string))


@contextmanager
def pelican_open(filename, mode='rb', strip_crs=(sys.platform == 'win32')):
    """Open a file and return its content"""

    with codecs.open(filename, mode, encoding='utf-8') as infile:
        content = infile.read()
    if content[0] == codecs.BOM_UTF8.decode('utf8'):
        content = content[1:]
    if strip_crs:
        content = content.replace('\r\n', '\n')
    yield content


def slugify(value, substitutions=()):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from Django sources.
    """
    # TODO Maybe steal again from current Django 1.5dev
    value = Markup(value).striptags()
    # value must be unicode per se
    import unicodedata
    from unidecode import unidecode
    # unidecode returns str in Py2 and 3, so in Py2 we have to make
    # it unicode again
    value = unidecode(value)
    if isinstance(value, six.binary_type):
        value = value.decode('ascii')
    # still unicode
    value = unicodedata.normalize('NFKD', value).lower()
    for src, dst in substitutions:
        value = value.replace(src.lower(), dst.lower())
    value = re.sub('[^\w\s-]', '', value).strip()
    value = re.sub('[-\s]+', '-', value)
    # we want only ASCII chars
    value = value.encode('ascii', 'ignore')
    # but Pelican should generally use only unicode
    return value.decode('ascii')


def copy(source, destination, ignores=None):
    """Recursively copy source into destination.

    If source is a file, destination has to be a file as well.
    The function is able to copy either files or directories.

    :param source: the source file or directory
    :param destination: the destination file or directory
    :param ignores: either None, or a list of glob patterns;
        files matching those patterns will _not_ be copied.
    """

    def walk_error(err):
        logger.warning("While copying %s: %s: %s",
                       source_, err.filename, err.strerror)

    source_ = os.path.abspath(os.path.expanduser(source))
    destination_ = os.path.abspath(os.path.expanduser(destination))

    if ignores is None:
        ignores = []

    if any(fnmatch.fnmatch(os.path.basename(source), ignore)
           for ignore in ignores):
        logger.info('Not copying %s due to ignores', source_)
        return

    if os.path.isfile(source_):
        dst_dir = os.path.dirname(destination_)
        if not os.path.exists(dst_dir):
            logger.info('Creating directory %s', dst_dir)
            os.makedirs(dst_dir)
        logger.info('Copying %s to %s', source_, destination_)
        shutil.copy2(source_, destination_)

    elif os.path.isdir(source_):
        if not os.path.exists(destination_):
            logger.info('Creating directory %s', destination_)
            os.makedirs(destination_)
        if not os.path.isdir(destination_):
            logger.warning('Cannot copy %s (a directory) to %s (a file)',
                           source_, destination_)
            return

        for src_dir, subdirs, others in os.walk(source_):
            dst_dir = os.path.join(destination_,
                                    os.path.relpath(src_dir, source_))

            subdirs[:] = (s for s in subdirs if not any(fnmatch.fnmatch(s, i)
                                                        for i in ignores))
            others[:] =  (o for o in others  if not any(fnmatch.fnmatch(o, i)
                                                        for i in ignores))

            if not os.path.isdir(dst_dir):
                logger.info('Creating directory %s', dst_dir)
                # Parent directories are known to exist, so 'mkdir' suffices.
                os.mkdir(dst_dir)

            for o in others:
                src_path = os.path.join(src_dir, o)
                dst_path = os.path.join(dst_dir, o)
                if os.path.isfile(src_path):
                    logger.info('Copying %s to %s', src_path, dst_path)
                    shutil.copy2(src_path, dst_path)
                else:
                    logger.warning('Skipped copy %s (not a file or directory) to %s',
                                   src_path, dst_path)

def clean_output_dir(path, retention):
    """Remove all files from output directory except those in retention list"""

    if not os.path.exists(path):
        logger.debug("Directory already removed: %s", path)
        return

    if not os.path.isdir(path):
        try:
            os.remove(path)
        except Exception as e:
            logger.error("Unable to delete file %s; %s", path, e)
        return

    # remove existing content from output folder unless in retention list
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if any(filename == retain for retain in retention):
            logger.debug("Skipping deletion; %s is on retention list: %s",
                         filename, file)
        elif os.path.isdir(file):
            try:
                shutil.rmtree(file)
                logger.debug("Deleted directory %s", file)
            except Exception as e:
                logger.error("Unable to delete directory %s; %s", 
                        file, e)
        elif os.path.isfile(file) or os.path.islink(file):
            try:
                os.remove(file)
                logger.debug("Deleted file/link %s", file)
            except Exception as e:
                logger.error("Unable to delete file %s; %s", file, e)
        else:
            logger.error("Unable to delete %s, file type unknown", file)


def get_relative_path(path):
    """Return the relative path from the given path to the root path."""
    components = split_all(path)
    if len(components) <= 1:
        return os.curdir
    else:
        parents = [os.pardir] * (len(components) - 1)
        return os.path.join(*parents)


def path_to_url(path):
    """Return the URL corresponding to a given path."""
    if os.sep == '/':
        return path
    else:
        return '/'.join(split_all(path))


def posixize_path(rel_path):
    """Use '/' as path separator, so that source references,
    like '{filename}/foo/bar.jpg' or 'extras/favicon.ico',
    will work on Windows as well as on Mac and Linux."""
    return rel_path.replace(os.sep, '/')


def truncate_html_words(s, num, end_text='...'):
    """Truncates HTML to a certain number of words.

    (not counting tags and comments). Closes opened tags if they were correctly
    closed in the given html. Takes an optional argument of what should be used
    to notify that the string has been truncated, defaulting to ellipsis (...).

    Newlines in the HTML are preserved. (From the django framework).
    """
    length = int(num)
    if length <= 0:
        return ''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area',
                      'hr', 'input')

    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    end_text_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or end_text_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:end_text_pos]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out


def process_translations(content_list, order_by=None):
    """ Finds translation and returns them.

    Returns a tuple with two lists (index, translations).  Index list includes
    items in default language or items which have no variant in default
    language. Items with the `translation` metadata set to something else than
    `False` or `false` will be used as translations, unless all the items with
    the same slug have that metadata.

    For each content_list item, sets the 'translations' attribute.

    order_by can be a string of an attribute or sorting function. If order_by
    is defined, content will be ordered by that attribute or sorting function.
    By default, content is ordered by slug.

    Different content types can have default order_by attributes defined
    in settings, e.g. PAGES_ORDER_BY='sort-order', in which case `sort-order`
    should be a defined metadata attribute in each page.
    """
    content_list.sort(key=attrgetter('slug'))
    grouped_by_slugs = groupby(content_list, attrgetter('slug'))
    index = []
    translations = []

    for slug, items in grouped_by_slugs:
        items = list(items)
        # items with `translation` metadata will be used as translations…
        default_lang_items = list(filter(
                lambda i: i.metadata.get('translation', 'false').lower()
                        == 'false',
                items))
        # …unless all items with that slug are translations
        if not default_lang_items:
            default_lang_items = items

        # display warnings if several items have the same lang
        for lang, lang_items in groupby(items, attrgetter('lang')):
            lang_items = list(lang_items)
            len_ = len(lang_items)
            if len_ > 1:
                logger.warning('There are %s variants of "%s" with lang %s',
                    len_, slug, lang)
                for x in lang_items:
                    logger.warning('\t%s', x.source_path)

        # find items with default language
        default_lang_items = list(filter(attrgetter('in_default_lang'),
                default_lang_items))

        # if there is no article with default language, take an other one
        if not default_lang_items:
            default_lang_items = items[:1]

        if not slug:
            logger.warning(
                    'empty slug for %s. '
                    'You can fix this by adding a title or a slug to your '
                    'content',
                    default_lang_items[0].source_path)
        index.extend(default_lang_items)
        translations.extend([x for x in items if x not in default_lang_items])
        for a in items:
            a.translations = [x for x in items if x != a]

    if order_by:
        if callable(order_by):
            try:
                index.sort(key=order_by)
            except Exception:
                logger.error('Error sorting with function %s', order_by)
        elif isinstance(order_by, six.string_types):
            if order_by.startswith('reversed-'):
                order_reversed = True
                order_by = order_by.replace('reversed-', '', 1)
            else:
                order_reversed = False

            if order_by == 'basename':
                index.sort(key=lambda x: os.path.basename(x.source_path or ''),
                           reverse=order_reversed)
            # already sorted by slug, no need to sort again
            elif not (order_by == 'slug' and not order_reversed):
                try:
                    index.sort(key=attrgetter(order_by),
                               reverse=order_reversed)
                except AttributeError:
                    logger.warning('There is no "%s" attribute in the item '
                        'metadata. Defaulting to slug order.', order_by)
        else:
            logger.warning('Invalid *_ORDER_BY setting (%s).'
                'Valid options are strings and functions.', order_by)

    return index, translations


def folder_watcher(path, extensions, ignores=[]):
    '''Generator for monitoring a folder for modifications.

    Returns a boolean indicating if files are changed since last check.
    Returns None if there are no matching files in the folder'''

    def file_times(path):
        '''Return `mtime` for each file in path'''

        for root, dirs, files in os.walk(path, followlinks=True):
            dirs[:] = [x for x in dirs if not x.startswith(os.curdir)]

            for f in files:
                if (f.endswith(tuple(extensions)) and
                    not any(fnmatch.fnmatch(f, ignore) for ignore in ignores)):
                    try:
                        yield os.stat(os.path.join(root, f)).st_mtime
                    except OSError as e:
                        logger.warning('Caught Exception: %s', e)

    LAST_MTIME = 0
    while True:
        try:
            mtime = max(file_times(path))
            if mtime > LAST_MTIME:
                LAST_MTIME = mtime
                yield True
        except ValueError:
            yield None
        else:
            yield False


def file_watcher(path):
    '''Generator for monitoring a file for modifications'''
    LAST_MTIME = 0
    while True:
        if path:
            try:
                mtime = os.stat(path).st_mtime
            except OSError as e:
                logger.warning('Caught Exception: %s', e)
                continue

            if mtime > LAST_MTIME:
                LAST_MTIME = mtime
                yield True
            else:
                yield False
        else:
            yield None


def set_date_tzinfo(d, tz_name=None):
    """Set the timezone for dates that don't have tzinfo"""
    if tz_name and not d.tzinfo:
        tz = pytz.timezone(tz_name)
        d = tz.localize(d)
        return SafeDatetime(d.year, d.month, d.day, d.hour, d.minute, d.second,
                            d.microsecond, d.tzinfo)
    return d


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def split_all(path):
    """Split a path into a list of components

    While os.path.split() splits a single component off the back of
    `path`, this function splits all components:

    >>> split_all(os.path.join('a', 'b', 'c'))
    ['a', 'b', 'c']
    """
    components = []
    path = path.lstrip('/')
    while path:
        head, tail = os.path.split(path)
        if tail:
            components.insert(0, tail)
        elif head == path:
            components.insert(0, head)
            break
        path = head
    return components


def is_selected_for_writing(settings, path):
    '''Check whether path is selected for writing
    according to the WRITE_SELECTED list

    If WRITE_SELECTED is an empty list (default),
    any path is selected for writing.
    '''
    if settings['WRITE_SELECTED']:
        return path in settings['WRITE_SELECTED']
    else:
        return True


def path_to_file_url(path):
    '''Convert file-system path to file:// URL'''
    return six.moves.urllib_parse.urljoin(
        "file://", six.moves.urllib.request.pathname2url(path))


def maybe_pluralize(count, singular, plural):
    '''
    Returns a formatted string containing count and plural if count is not 1
    Returns count and singular if count is 1

    maybe_pluralize(0, 'Article', 'Articles') -> '0 Articles'
    maybe_pluralize(1, 'Article', 'Articles') -> '1 Article'
    maybe_pluralize(2, 'Article', 'Articles') -> '2 Articles'

    '''
    selection = plural
    if count == 1:
        selection = singular
    return '{} {}'.format(count, selection)
