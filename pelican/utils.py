# -*- coding: utf-8 -*-
import re
import os
import shutil
from datetime import datetime
from codecs import open as _open
from itertools import groupby
from operator import attrgetter
from pelican.log import warning, info


def get_date(string):
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValuEerror
    """
    formats = ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M', '%Y-%m-%d', '%Y/%m/%d',
               '%d/%m/%Y']
    for date_format in formats:
        try:
            return datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise ValueError("'%s' is not a valid date" % string)


def open(filename):
    """Open a file and return it's content"""
    return _open(filename, encoding='utf-8').read()


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from django sources.
    """
    if type(value) == unicode:
        import unicodedata
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def copytree(path, origin, destination, topath=None):
    """Copy path from origin to destination, silent any errors"""
    
    if not topath:
        topath = path
    try:
        fromp = os.path.expanduser(os.path.join(origin, path))
        to = os.path.expanduser(os.path.join(destination, topath))
        shutil.copytree(fromp, to)
        info('copying %s to %s' % (fromp, to))

    except OSError:
        pass


def clean_output_dir(path):
    """Remove all the files from the output directory"""

    # remove all the existing content from the output folder
    try:
        shutil.rmtree(path)
    except Exception:
        pass


def get_relative_path(filename):
    """Return the relative path to the given filename"""
    return '../' * filename.count('/') + '.'


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
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')

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
                # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i+1:]
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
    """ Finds all translation and returns
        tuple with two lists (index, translations).
        Index list includes items in default language
        or items which have no variant in default language.

        Also, for each content_list item, it
        sets attribute 'translations'
    """
    content_list.sort(key=attrgetter('slug'))
    grouped_by_slugs = groupby(content_list, attrgetter('slug'))
    index = []
    translations = []

    for slug, items in grouped_by_slugs:
        items = list(items)
        # find items with default language
        default_lang_items = filter(
            attrgetter('in_default_lang'),
            items
        )
        len_ = len(default_lang_items)
        if len_ > 1:
            warning(u'there are %s variants of "%s"' % (len_, slug))
        elif len_ == 0:
            default_lang_items = items[:1]

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

    def with_extension(f):
        return True if True in [f.endswith(ext) for ext in extensions] else False

    def file_times(path):
        """Return the last time files have been modified"""
        for top_level in os.listdir(path):
            for root, dirs, files in os.walk(top_level):
                for file in filter(with_extension, files):
                    yield os.stat(os.path.join(root, file)).st_mtime

    global LAST_MTIME
    mtime = max(file_times(path))
    if mtime > LAST_MTIME:
        LAST_MTIME = mtime
        return True
    return False
