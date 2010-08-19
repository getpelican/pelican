# -*- coding: utf-8 -*-
import os
import re
import shutil
from codecs import open
from datetime import datetime
from docutils import core
from functools import partial
from operator import attrgetter

from jinja2 import Environment, FileSystemLoader
from feedgenerator import Atom1Feed

import rstdirectives   # import the directives to have pygments support

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives')
_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')
_DEFAULT_THEME =\
    os.sep.join([os.path.dirname(os.path.abspath(__file__)), "themes"])
_DEFAULT_CONFIG = {'PATH': None, 
                   'THEME': _DEFAULT_THEME,
                   'OUTPUT_PATH': 'output/',
                   'MARKUP': 'rst', 
                   'STATIC_PATHS': ['css', 'images'], 
                   'FEED_FILENAME': 'atom.xml'}

def generate_output(path=None, theme=None, output_path=None, markup=None,
                    settings=None):
    """Given a list of files, a template and a destination,
    output the static files.

    :param path: the path where to find the files to parse
    :param theme: where to search for templates
    :param output_path: where to output the generated files
    :param markup: the markup language to use while parsing
    :param settings: the settings file to use
    """
    # get the settings
    context = read_settings(settings)
    path = path or context['PATH']
    theme = theme or context['THEME']
    output_path = output_path or context['OUTPUT_PATH']
    output_path = os.path.realpath(output_path)
    markup = markup or context['MARKUP']
    
    # get the list of files to parse
    files = []
    for root, dirs, temp_files in os.walk(path, followlinks=True):
        files.extend([os.sep.join((root, f)) for f in temp_files 
                      if f.endswith('.%s' % markup)])

    articles, dates, years, tags, categories = [], {}, {}, {}, {}
    # for each file, get the informations.
    for f in files:
        f = os.path.abspath(f)
        article = Article(open(f, encoding='utf-8').read(), markup, context)
        articles.append(article)
        if hasattr(article, 'date'):
            update_dict(dates, article.date.strftime('%Y-%m-%d'), article)
            update_dict(years, article.date.year, article)
        if hasattr(article, 'tags'):
            for tag in article.tags:
                update_dict(tags, tag, article)
        if hasattr(article, 'category'):
            update_dict(categories, article.category, article)

    # order the articles by date
    articles.sort(key=attrgetter('date'), reverse=True)
    templates = get_templates(theme)
    for item in ('articles', 'dates', 'years', 'tags', 'categories'):
        value = locals()[item]
        if hasattr(value, 'items'):
            value = value.items()
        context[item] = value
    
    # generate the output
    generate = partial(generate_file, output_path)
    for template in _DIRECT_TEMPLATES:
        generate('%s.html' % template, templates[template], context)
    for tag in tags:
        generate('tag/%s.html' % tag, templates['tag'], context, tag=tag)
    for cat in categories:
        generate('category/%s.html' % cat, templates['category'], context,
                      category=cat)
    for article in articles:
        generate('%s' % article.url,
                      templates['article'], context, article=article)

    # generate atom feed
    feed = Atom1Feed(
        title=context['BLOGNAME'],
        link=context['BLOGURL'],
        feed_url='%s/%s' % (context['BLOGURL'], context['FEED_FILENAME']),
        description=context['BLOGSUBTITLE'])
    for article in articles:
        feed.add_item(
            title=article.title,
            link='%s/%s' % (context['BLOGURL'], article.url),
            description=article.content,
            author_name=article.author,
            pubdate=article.date)

    fp = open(os.path.join(output_path, context['FEED_FILENAME']), 'w')
    feed.write(fp, 'utf-8')
    fp.close()

    # copy static paths to output
    for path in context['STATIC_PATHS']:
        try:
            shutil.copytree(os.path.join(theme, path), 
                            os.path.join(output_path, path))
        except OSError:
            pass


def generate_file(path, name, template, context, **kwargs):
    context.update(kwargs)
    output = template.render(context)
    filename = os.sep.join((path, name))
    try:
        os.makedirs(os.path.dirname(filename))
    except Exception:
        pass
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)
    print filename


def get_templates(path=None):
    path = os.path.join(path, 'templates')
    env = Environment(loader=FileSystemLoader(path))
    templates = {}
    for template in _TEMPLATES:
        templates[template] = env.get_template('%s.html' % template)
    return templates


def update_dict(mapping, key, value):
    if key not in mapping:
        mapping[key] = []
    mapping[key].append(value)


def read_settings(filename):
    """Load a Python file into a dictionary.
    """
    context = _DEFAULT_CONFIG.copy()
    if filename:
        tempdict = {}
        execfile(filename, tempdict)
        for key in tempdict:
            if key.isupper():
                context[key] = tempdict[key]
    return context

_METADATA = re.compile('.. ([a-z]+): (.*)', re.M)
_METADATAS_FIELDS = {'tags': lambda x: x.split(', '),
                     'date': lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'),
                     'category': lambda x: x,
                     'author': lambda x: x}


def parse_metadata(string):
    """Return a dict, containing a list of metadata informations, found
    whithin the given string.

    :param string: the string to search the metadata in
    """
    output = {}
    for m in _METADATA.finditer(string):
        name = m.group(1)
        value = m.group(2)
        if name in _METADATAS_FIELDS:
            output[name] = _METADATAS_FIELDS[name](value)
    return output


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from django sources.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


class Article(object):
    """Represents an article.
    Given a string, complete it's properties from here.

    :param string: the string to parse, containing the original content.
    :param markup: the markup language to use while parsing.
    """

    def __init__(self, string, markup=None, config={}):
        if markup == None:
            markup = 'rst'

        for key, value in parse_metadata(string).items():
            setattr(self, key, value)
        if markup == 'rst':
            extra_params = {'input_encoding': 'unicode',
                            'initial_header_level': '2'}
            rendered_content = core.publish_parts(string, writer_name='html',
                settings_overrides=extra_params)
            self.title = rendered_content.get('title')
            self.content = rendered_content.get('body')

        if not hasattr(self, 'author'):
            if 'AUTHOR' in config:
                self.author = config['AUTHOR']

    @property
    def url(self):
        return '%s.html' % slugify(self.title)

    @property
    def summary(self):
        return self.content

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.title)
