from pelican.utils import slugify, truncate_html_words


class Page(object):
    """Represents a page
    Given a content, and metadatas, create an adequate object.

    :param string: the string to parse, containing the original content.
    :param markup: the markup language to use while parsing.
    """
    mandatory_properties = ('title',)

    def __init__(self, content, metadatas={}, settings={}, filename=None):
        self.content = content
        self.status = "published"  # default value
        for key, value in metadatas.items():
            setattr(self, key, value)

        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = settings['AUTHOR']

        if not hasattr(self, 'slug'):
            self.slug = slugify(self.title)

        if not hasattr(self, 'url'):
            self.url = '%s.html' % self.slug

        if filename:
            self.filename = filename

    def check_properties(self):
        """test that each mandatory property is set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                raise NameError(prop)

    @property
    def summary(self):
        return truncate_html_words(self.content, 50)


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')


class Quote(Page):
    base_properties = ('author', 'date')


def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError as e:
        print u" [info] Skipping %s: impossible to find informations about '%s'" % (f, e)
        return False
