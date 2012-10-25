# -*- coding: utf-8 -*-
"""
Copyright (c) FELD Boris <lothiraldan@gmail.com>

Multiple part support
=====================

Create a navigation menu for multi-part related_posts

Article metadata:
------------------

:parts:  a unique identifier for multi-part posts, must be the same in each
post part.

Usage
-----
    {% if article.metadata.parts_articles %}
        <ol>
        {% for part_article in article.metadata.parts_articles %}
            {% if part_article == article %}
                <li>
                    <a href='{{ SITEURL }}/{{ part_article.url }}'><b>{{ part_article.title }}</b>
                    </a>
                </li>
            {% else %}
                <li>
                    <a href='{{ SITEURL }}/{{ part_article.url }}'>{{ part_article.title }}
                    </a>
                </li>
            {% endif %}
        {% endfor %}
        </ol>
    {% endif %}
"""
from collections import defaultdict

from pelican import signals


def aggregate_multi_part(generator):
        multi_part = defaultdict(list)

        for article in generator.articles:
            if 'parts' in article.metadata:
                multi_part[article.metadata['parts']].append(article)

        for part_id in multi_part:
            parts = multi_part[part_id]

            # Sort by date
            parts.sort(key=lambda x: x.metadata['date'])

            for article in parts:
                article.metadata['parts_articles'] = parts


def register():
    signals.article_generator_finalized.connect(aggregate_multi_part)
