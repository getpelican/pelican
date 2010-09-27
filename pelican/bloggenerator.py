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

# import the directives to have pygments support
import rstdirectives

## Constants ##########################################################

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives')

_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')

_DEFAULT_THEME = os.sep.join([os.path.dirname(os.path.abspath(__file__)),
                              "themes"])
_DEFAULT_CONFIG = {'PATH': None,
                   'THEME': _DEFAULT_THEME,
                   'OUTPUT_PATH': 'output/',
                   'MARKUP': 'rst',
                   'STATIC_PATHS': ['css', 'images'],
                   'FEED': 'feeds/all.atom.xml',
                   'CATEGORY_FEED': 'feeds/%s.atom.xml',
                   'BLOGNAME': 'A Pelican Blog',
                  }


def generate_blog(path=None, theme=None, output_path=None, markup=None, 
                  settings=None):
    """Search the given path for files, and generate a static blog in output,
    using the given theme.

    That's the main logic of pelican.

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
    if not path:
        raise Exception('you need to specify a path to search the docs on !')
    files = []
    for root, dirs, temp_files in os.walk(path, followlinks=True):
        files.extend([os.sep.join((root, f)) for f in temp_files
                      if f.endswith('.%s' % markup)])

    articles, dates, years, tags, categories = [], {}, {}, {}, {}
    # for each file, get the informations.
    for f in files:
        f = os.path.abspath(f)
        content = open(f, encoding='utf-8').read()
        article = Article(content, markup, context, os.stat(f))
        if not hasattr(article, 'category'):
            # try to get the category from the dirname
            category = os.path.dirname(f).replace(os.path.abspath(path)+'/', '')
            if category != '':
                article.category = unicode(category)

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

    if 'BLOGURL' not in context:
        context['BLOGURL'] = output_path

    # generate the output
    generate = partial(generate_file, output_path)
    for template in _DIRECT_TEMPLATES:
        generate('%s.html' % template, templates[template], context, blog=True)
    for tag in tags:
        generate('tag/%s.html' % tag, templates['tag'], context, tag=tag)
    for cat in categories:
        generate('category/%s.html' % cat, templates['category'], context,
                      category=cat, articles=categories[cat])
    for article in articles:
        generate('%s' % article.url,
                      templates['article'], context, article=article)

    generate_feed(articles, context, output_path, context['FEED'])
    for category, articles in categories.items():
        articles.sort(key=attrgetter('date'), reverse=True)
        generate_feed(articles, context, output_path,
                      context['CATEGORY_FEED'] % category)

    # copy static paths to output
    for path in context['STATIC_PATHS']:
        try:
            real_output = os.path.join(output_path, path)
            theme_path = os.path.join(theme, path)

            print "updating %s" % real_output
            shutil.rmtree(real_output)
            shutil.copytree(theme_path, real_output)

        except OSError as e:
            pass


def generate_feed(articles, context, output_path=None, filename=None):
    """Generate a feed with the list of articles provided

    Return the feed. If no output_path or filename is specified, just return
    the feed object.

    :param articles: the articles to put on the feed.
    :param context: the context to get the feed metadatas.
    :param output_path: where to output the file.
    :param filename: the filename to output.
    """
    feed = Atom1Feed(
        title=context['BLOGNAME'],
        link=context['BLOGURL'],
        feed_url='%s/%s' % (context['BLOGURL'], filename),
        description=context.get('BLOGSUBTITLE', ''))
    for article in articles:
        feed.add_item(
            title=article.title,
            link='%s/%s' % (context['BLOGURL'], article.url),
            description=article.content,
            author_name=getattr(article, 'author', 'John Doe'),
            pubdate=article.date)

    if output_path and filename:
        complete_path = os.path.join(output_path, filename)
        try:
            os.makedirs(os.path.dirname(complete_path))
        except Exception:
            pass
        fp = open(complete_path, 'w')
        feed.write(fp, 'utf-8')
        fp.close()
    return feed


def generate_file(path, name, template, context, **kwargs):
    """Write the file with the given informations

    :param path: where to generate the file.
    :param name: name of the file to output
    :param template: template to use to generate the content
    :param context: dict to pass to the templates.
    :param **kwargs: additional variables to pass to the templates
    """
    context.update(kwargs)
    output = template.render(context)
    filename = os.sep.join((path, name))
    try:
        os.makedirs(os.path.dirname(filename))
    except Exception:
        pass
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)
    print 'writing %s' % filename


def get_templates(path=None):
    """Return the templates to use"""
    path = os.path.join(path, 'templates')
    env = Environment(loader=FileSystemLoader(path))
    templates = {}
    for template in _TEMPLATES:
        templates[template] = env.get_template('%s.html' % template)
    return templates


def update_dict(mapping, key, value):
    """Update a dict intenal list

    :param mapping: the mapping to update
    :param key: the key of the mapping to update.
    :param value: the value to append to the list.
    """
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
                     'date': lambda x: get_date(x),
                     'category': lambda x: x,
                     'author': lambda x: x}

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
    raise ValueError("%s is not a valid date" % string)

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

    def __init__(self, string, markup=None, config={}, file_infos=None):
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

        if not hasattr(self, 'date'):
            self.date = datetime.fromtimestamp(file_infos.st_ctime)

    @property
    def url(self):
        return '%s.html' % slugify(self.title)

    @property
    def summary(self):
        return self.content
