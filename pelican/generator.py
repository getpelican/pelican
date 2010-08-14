from docutils import core
from datetime import datetime
import re
import os
from jinja2 import Environment, FileSystemLoader
from functools import partial

_TEMPLATES = ('index', 'tag', 'tags', 'article', 'category', 'categories',
              'archives')
_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')
_DEFAULT_TEMPLATE_PATH =\
    os.sep.join([os.path.dirname(os.path.abspath(__file__)), "templates"])


def generate_output(files, templates_path=None, output_path=None, markup=None):
    """Given a list of files, a template and a destination,
    output the static files.

    :param files: the list of files to parse
    :param templates_path: where to search for templates
    :param output_path: where to output the generated files
    :param markup: the markup language to use while parsing
    """
    if not templates_path:
        templates_path = _DEFAULT_TEMPLATE_PATH
    if not output_path:
        output_path = './output'
    output_path = os.path.realpath(output_path)

    articles, months, years, tags, categories = [], {}, {}, {}, {}

    # for each file, get the informations.
    for f in files:
        f = os.path.abspath(f)
        article = Article(file(f).read(), markup)
        articles.append(article)
        if hasattr(article, 'date'):
            update_dict(months, article.date.month, article)
            update_dict(years, article.date.year, article)
        if hasattr(article, 'tags'):
            for tag in article.tags:
                update_dict(tags, tag, article)
        if hasattr(article, 'category'):
            update_dict(categories, article.category, article)

    templates = get_templates(templates_path)
    context = {}
    for item in ('articles', 'months', 'years', 'tags', 'categories'):
        context[item] = locals()[item]

    generate = partial(generate_file, output_path)
    for template in _DIRECT_TEMPLATES:
        generate(template, templates[template], context)
    for tag in tags:
        generate('tag/%s' % tag, templates['tag'], context, tag=tag)
    for cat in categories:
        generate('category/%s' % cat, templates['category'], context,
                      category=cat)
    for article in articles:
        generate('%s' % article.url,
                      templates['article'], context, article=article)


def generate_file(path, name, template, context, **kwargs):
    context.update(kwargs)
    output = template.render(context)
    filename = os.sep.join((path, '%s.html' % name))
    try:
        os.makedirs(os.path.dirname(filename))
    except Exception:
        pass
    with open(filename, 'w') as f:
        f.write(output)
    print filename


def get_templates(path=None):
    env = Environment(loader=FileSystemLoader(path))
    templates = {}
    for template in _TEMPLATES:
        templates[template] = env.get_template('%s.html' % template)
    return templates

_METADATA = re.compile('.. ([a-z]+): (.*)', re.M)
_METADATAS_FIELDS = {'tags': lambda x: x.split(', '),
                     'date': lambda x: datetime.strptime(x, '%Y/%m/%d %H:%M'),
                     'category': lambda x: x}


def update_dict(mapping, key, value):
    if key not in mapping:
        mapping[key] = []
    mapping[key].append(value)


def parse_metadatas(string):
    """Return a dict, containing a list of metadatas informations, found
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

    def __init__(self, string, markup=None):
        if markup == None:
            markup = 'rest'

        for key, value in parse_metadatas(string).items():
            setattr(self, key, value)
        if markup == 'rest':
            rendered_content = core.publish_parts(string, writer_name='html')
            self.title = rendered_content.get('title')
            self.content = rendered_content.get('body')
    
    @property
    def url(self):
        return slugify(self.title)

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.title)
