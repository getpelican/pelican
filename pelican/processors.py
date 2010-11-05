from operator import attrgetter
import os

from pelican.utils import update_dict, copytree
from pelican.contents import Article, Page, is_valid_content
from pelican.readers import read_file

_DIRECT_TEMPLATES = ('index', 'tags', 'categories', 'archives')


class Processor(object):

    def _update_context(self, context, items):
        """Update the context with the given items from the currrent 
        processor.
        """
        for item in items:
            value = getattr(self, item)
            if hasattr(value, 'items'):
                value = value.items()
            context[item] = value


class ArticlesProcessor(Processor):

    def __init__(self, settings=None):
        self.articles = [] 
        self.dates = {}
        self.years = {}
        self.tags = {}
        self.categories = {} 
        
    def generate_feeds(self, context, generator):
        """Generate the feeds from the current context, and output files.""" 

        generator.generate_feed(self.articles, context, context['FEED'])

        for cat, arts in self.categories.items():
            arts.sort(key=attrgetter('date'), reverse=True)
            generator.generate_feed(arts, context, 
                                    context['CATEGORY_FEED'] % cat)

    def generate_pages(self, context, generator):
        """Generate the pages on the disk"""

        templates = generator.get_templates()
        generate = generator.generate_file
        for template in _DIRECT_TEMPLATES:
            generate('%s.html' % template, templates[template], context, blog=True)
        for tag in self.tags:
            generate('tag/%s.html' % tag, templates['tag'], context, tag=tag)
        for cat in self.categories:
            generate('category/%s.html' % cat, templates['category'], context,
                          category=cat, articles=self.categories[cat])
        for article in self.articles:
            generate('%s' % article.url,
                          templates['article'], context, article=article,
                          category=article.category)

    def preprocess(self, context, generator):

        # build the list of articles / categories / etc.
        files = generator.get_files(generator.path, exclude=['pages',])
        for f in files:
            content, metadatas = read_file(f)
            if 'category' not in metadatas.keys():
                category = os.path.dirname(f).replace(
                    os.path.expanduser(generator.path)+'/', '')

                if category != '':
                    metadatas['category'] = unicode(category)

            article = Article(content, metadatas, settings=generator.settings)
            if not is_valid_content(article, f):
                continue

            update_dict(self.dates, article.date.strftime('%Y-%m-%d'), article)
            update_dict(self.years, article.date.year, article)
            update_dict(self.categories, article.category, article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    update_dict(self.tags, tag, article)
            self.articles.append(article)

        # sort the articles by date
        self.articles.sort(key=attrgetter('date'), reverse=True)
        # and generate the output :)
        self._update_context(context, ('articles', 'dates', 'years', 
                                       'tags', 'categories'))

    def process(self, context, generator):
        self.generate_feeds(context, generator)
        self.generate_pages(context, generator)


class PagesProcessor(Processor):
    """Generate pages"""

    def __init__(self):
        self.pages = []

    def preprocess(self, context, generator):
        for f in generator.get_files(os.sep.join((generator.path, 'pages'))):
            content, metadatas = read_file(f)
            page = Page(content, metadatas, settings=generator.settings)
            if not is_valid_content(page, f):
                continue
            self.pages.append(page)
        
    def process(self, context, generator):
        templates = generator.get_templates()
        for page in self.pages:
            generator.generate_file('pages/%s' % page.url, 
                               templates['page'], context, page=page)
        self._update_context(context, ('pages',))


class StaticProcessor(Processor):
    """copy static paths to output"""

    def process(self, context, generator):
        for path in generator.settings['STATIC_PATHS']:
            copytree(path, generator.theme, generator.output_path)
        copytree('pics', generator.path, generator.output_path)

