"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context
"""

from pelican import signals
from collections import Counter


def add_related_posts(generator):
    # get the max number of entries from settings
    # or fall back to default (5)
    numentries = generator.settings.get('RELATED_POSTS_MAX', 5)

    for article in generator.articles:
        # no tag, no relation
        if not hasattr(article, 'tags'):
            continue

        # score = number of common tags
        scores = Counter()
        for tag in article.tags:
            scores += Counter(generator.tags[tag])

        # remove itself
        scores.pop(article)

        article.related_posts = [other for other, count 
            in scores.most_common(numentries)]


def register():
    signals.article_generator_finalized.connect(add_related_posts)