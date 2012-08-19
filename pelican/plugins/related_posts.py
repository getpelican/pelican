from pelican import signals

"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context

Settings
--------
To enable, add

    from pelican.plugins import related_posts
    PLUGINS = [related_posts]

to your settings.py.

Optionally, set MAX_RELATED_POSTS in settings.py to control the
maximum number of related posts to return.

Usage
-----
    {% if article.related_posts %}
        <ul>
        {% for post in article.related_posts %}
            <li><a href="/{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
        </ul>
    {% endif %}


"""


class RelatedPosts(object):
    """The related posts for an article. Instances of RelatedPosts can
    be iterated over, but will only return correct results AFTER
    the given generator's get_context_data method has run. RelatedPosts
    is safe to use in a template."""

    # ArticlesGenerator.generate_context() behaves roughly like this:
    # for each file:
    #     read content & metadata from file
    #     send article_generate_context signal
    #         -> triggers add_related_posts
    #     construct Article object with content & metadata
    #     update generator.tags with the article's tags

    # this means that add_related_posts is called before
    # generator.tags has been populated with all articles.
    # So calculating related posts should be deferred until
    # after every file/article has been processed by the
    # ArticlesGenerator.

    MAX_RELATED_POSTS = 5
    NOT_GIVEN = object()

    def __init__(self, generator, metadata):
        self.generator = generator
        self.metadata = metadata
        self._related = self.NOT_GIVEN

    def __iter__(self):
        return iter(self.related)

    def __nonzero__(self):
        return bool(self.related)

    def get_related(self):
        if self._related is not self.NOT_GIVEN:
            return self._related

        related_posts = []
        for tag in self.metadata.get('tags', []):
            for related_article in self.generator.tags[tag]:
                # an article is not related to itself
                # same metadata == same slug, treat as the same
                if related_article.metadata != self.metadata:
                    related_posts.append(related_article)

        if not related_posts:
            return []

        relation_score = dict(zip(set(related_posts),
                                  map(related_posts.count,
                                      set(related_posts))))
        ranked_related = sorted(relation_score, key=relation_score.get,
                                reverse=True)

        num_related_posts = self.generator.settings.get(
            'MAX_RELATED_POSTS', self.MAX_RELATED_POSTS)

        self._related = ranked_related[:num_related_posts]
        return self._related

    def set_related(self, related):
        self._related = related

    related = property(get_related, set_related)


def add_related_posts(generator, metadata):
    metadata['related_posts'] = RelatedPosts(generator, metadata)


def register():
    signals.article_generate_context.connect(add_related_posts)
