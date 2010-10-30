from pelican.utils import slugify, truncate_html_words


class Page(object):
    """Represents a page..
    Given a content, and metadatas, create an adequate object.

    :param string: the string to parse, containing the original content.
    :param markup: the markup language to use while parsing.
    """
    mandatory_properties = ('title',)

    def __init__(self, content, metadatas={}, settings={}):
        self.content = content
        for key, value in metadatas.items():
            setattr(self, key, value)

        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = settings['AUTHOR']

    def check_properties(self):
        """test that each mandatory property is set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                raise NameError(prop)

    @property
    def url(self):
        return '%s.html' % slugify(self.title)

    @property
    def summary(self):
        return truncate_html_words(self.content, 50)


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')


class Quote(Page):
    base_properties = ('author', 'date')
