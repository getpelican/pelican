"""
To support multiple categories in Pelican, we treat the `category` attribute
like the `tag` attribute.

Note we must also make a one line tweak to a file.

"""
from collections import defaultdict

from pelican import signals
from pelican.contents import Category as BaseCategory
from pelican.readers import _METADATA_PROCESSORS
from pelican.utils import slugify


_METADATA_PROCESSORS["category"] = lambda x, y: [
        Category(category.strip(), y)
        for category in unicode(x).split(",")
    ]



class Category(BaseCategory):
    """
    Category whose slug can be remapped using the setting `CATEGORY_MAP`.

    """
    def __init__(self, name, settings):
        self.name = unicode(name)
        slug = slugify(self.name)
        slug = settings["CATEGORY_MAP"].get(slug, slug)
        self.slug = slug
        self.settings = settings



def fix_categories(generator):
    generator.categories = defaultdict(list)

    for article in generator.articles:
        # TODO: IF ANY ARTICLE DOESNT HAVE A CATEGORY.... THIS WONT WORK.
        if not isinstance(article.category, list):
            print 'NO CATEGORY:', article.title
            continue

        for category in article.category:
            generator.categories[category].append(article)

    generator.categories = list(generator.categories.items())
    generator._update_context(("categories",))

def register():
    signals.article_generator_finalized.connect(fix_categories)