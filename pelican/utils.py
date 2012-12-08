# -*- coding: utf-8 -*-
import os
import re
import pytz
import shutil
import logging
import errno
from collections import defaultdict, Hashable
from functools import partial

from codecs import open
from datetime import datetime
from itertools import groupby
from jinja2 import Markup
from operator import attrgetter

logger = logging.getLogger(__name__)


class NoFilesError(Exception):
    pass


class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
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
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return partial(self.__call__, obj)

def get_date(string):
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValueError.
    """
    string = re.sub(' +', ' ', string)
    formats = ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
               '%Y-%m-%d', '%Y/%m/%d',
               '%d-%m-%Y', '%Y-%d-%m',  # Weird ones
               '%d/%m/%Y', '%d.%m.%Y',
               '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']
    for date_format in formats:
        try:
            return datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise ValueError("'%s' is not a valid date" % string)


def pelican_open(filename):
    """Open a file and return it's content"""
    return open(filename, encoding='utf-8').read()


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from django sources.
    """
    value = Markup(value).striptags()
    if type(value) == unicode:
        import unicodedata
        from unidecode import unidecode
        value = unicode(unidecode(value))
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


def copy(path, source, destination, destination_path=None, overwrite=False):
    """Copy path from origin to destination.

    The function is able to copy either files or directories.

    :param path: the path to be copied from the source to the destination
    :param source: the source dir
    :param destination: the destination dir
    :param destination_path: the destination path (optional)
    :param overwrite: whether to overwrite the destination if already exists
                      or not
    """
    if not destination_path:
        destination_path = path

    source_ = os.path.abspath(os.path.expanduser(os.path.join(source, path)))
    destination_ = os.path.abspath(
        os.path.expanduser(os.path.join(destination, destination_path)))

    if os.path.isdir(source_):
        try:
            shutil.copytree(source_, destination_)
            logger.info('copying %s to %s' % (source_, destination_))
        except OSError:
            if overwrite:
                shutil.rmtree(destination_)
                shutil.copytree(source_, destination_)
                logger.info('replacement of %s with %s' % (source_,
                    destination_))

    elif os.path.isfile(source_):
        dest_dir = os.path.dirname(destination_)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy(source_, destination_)
        logger.info('copying %s to %s' % (source_, destination_))
    else:
        logger.warning('skipped copy %s to %s' % (source_, destination_))

def clean_output_dir(path):
    """Remove all the files from the output directory"""

    if not os.path.exists(path):
        logger.debug("Directory already removed: %s" % path)
        return

    if not os.path.isdir(path):
        try:
            os.remove(path)
        except Exception, e:
            logger.error("Unable to delete file %s; %e" % path, e)
        return

    # remove all the existing content from the output folder
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if os.path.isdir(file):
            try:
                shutil.rmtree(file)
                logger.debug("Deleted directory %s" % file)
            except Exception, e:
                logger.error("Unable to delete directory %s; %e" % file, e)
        elif os.path.isfile(file) or os.path.islink(file):
            try:
                os.remove(file)
                logger.debug("Deleted file/link %s" % file)
            except Exception, e:
                logger.error("Unable to delete file %s; %e" % file, e)
        else:
            logger.error("Unable to delete %s, file type unknown" % file)


def get_relative_path(filename):
    """Return the relative path from the given filename to the root path."""
    nslashes = filename.count('/')
    if nslashes == 0:
        return '.'
    else:
        return '/'.join(['..'] * nslashes)


def truncate_html_words(s, num, end_text='...'):
    """Truncates HTML to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html. Takes an optional argument of what should be used to notify that the
    string has been truncated, defaulting to ellipsis (...).

    Newlines in the HTML are preserved.
    From the django framework.
    """
    length = int(num)
    if length <= 0:
        return u''
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


def process_translations(content_list):
    """ Finds all translation and returns tuple with two lists (index,
    translations).  Index list includes items in default language or items
    which have no variant in default language.

    Also, for each content_list item, it sets attribute 'translations'
    """
    content_list.sort(key=attrgetter('slug'))
    grouped_by_slugs = groupby(content_list, attrgetter('slug'))
    index = []
    translations = []

    for slug, items in grouped_by_slugs:
        items = list(items)
        # find items with default language
        default_lang_items = filter(attrgetter('in_default_lang'), items)
        len_ = len(default_lang_items)
        if len_ > 1:
            logger.warning(u'there are %s variants of "%s"' % (len_, slug))
            for x in default_lang_items:
                logger.warning('    %s' % x.filename)
        elif len_ == 0:
            default_lang_items = items[:1]

        if not slug:
            msg = 'empty slug for %r. ' % default_lang_items[0].filename\
                + 'You can fix this by adding a title or a slug to your '\
                + 'content'
            logger.warning(msg)
        index.extend(default_lang_items)
        translations.extend(filter(
            lambda x: x not in default_lang_items,
            items
        ))
        for a in items:
            a.translations = filter(lambda x: x != a, items)
    return index, translations


LAST_MTIME = 0


def files_changed(path, extensions):
    """Return True if the files have changed since the last check"""

    def file_times(path):
        """Return the last time files have been modified"""
        for root, dirs, files in os.walk(path):
            dirs[:] = [x for x in dirs if x[0] != '.']
            for f in files:
                if any(f.endswith(ext) for ext in extensions):
                    yield os.stat(os.path.join(root, f)).st_mtime

    global LAST_MTIME
    try:
        mtime = max(file_times(path))
        if mtime > LAST_MTIME:
            LAST_MTIME = mtime
            return True
    except ValueError:
        raise NoFilesError("No files with the given extension(s) found.")
    return False


FILENAMES_MTIMES = defaultdict(int)


def file_changed(filename):
    mtime = os.stat(filename).st_mtime
    if FILENAMES_MTIMES[filename] == 0:
        FILENAMES_MTIMES[filename] = mtime
        return False
    else:
        if mtime > FILENAMES_MTIMES[filename]:
            FILENAMES_MTIMES[filename] = mtime
            return True
        return False


def set_date_tzinfo(d, tz_name=None):
    """ Date without tzinfo shoudbe utc.
    This function set the right tz to date that aren't utc and don't have
    tzinfo.
    """
    if tz_name is not None:
        tz = pytz.timezone(tz_name)
        return tz.localize(d)
    else:
        return d


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
