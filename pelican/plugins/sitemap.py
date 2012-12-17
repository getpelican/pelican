import collections
import os.path

from datetime import datetime
from logging import warning, info
from codecs import open

from jinja2 import Template

from pelican import signals


TXT_TEMPLATE = u"""
{%- macro add_url(loc) -%}
  {{ siteurl }}/{{ loc }}
{% endmacro -%}

{%- for article in articles -%}
  {{ add_url(article.url) }}
{%- endfor -%}

{%- for page in pages -%}
  {{ add_url(page.url) }}
{%- endfor -%}

{%- for index in indexes -%}
  {{ add_url(index.url) }}
{%- endfor -%}
"""

XML_TEMPLATE = u"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

{%- macro add_url(loc, lastmod, changefreq, priority) %}
  <url>
    <loc>{{ siteurl }}/{{ loc }}</loc>
    {% if lastmod -%}<lastmod>{{ lastmod }}</lastmod>{% endif %}
    {% if changefreq -%}<changefreq>{{ changefreq }}</changefreq>{% endif %}
    {% if priority -%}<priority>{{ priority }}</priority>{% endif %}
  </url>
{%- endmacro -%}

{% for article in articles -%}
  {{ add_url(article.url, article.lastmod, changefreqs.articles,
             priorities.articles) }}
{% endfor %}

{% for page in pages -%}
  {{ add_url(page.url, page.lastmod, changefreqs.pages, priorities.pages) }}
{% endfor %}

{% for index in indexes -%}
  {{ add_url(index.url, index.lastmod, changefreqs.indexes,
             priorities.indexes) }}
{% endfor %}
</urlset>
"""


def format_date(date):
    if date.tzinfo:
        tz = date.strftime('%s')
        tz = tz[:-2] + ':' + tz[-2:]
    else:
        tz = "-00:00"
    return date.strftime("%Y-%m-%dT%H:%M:%S") + tz


class SitemapGenerator(object):

    def __init__(self, context, settings, path, theme, output_path, *null):

        self.output_path = output_path
        self.settings = settings
        self.context = context
        self.now = datetime.now()

        self.generate = ['articles', 'pages', 'indexes']
        self.format = 'xml'
        self.changefreqs = {
            'articles': 'monthly',
            'indexes': 'daily',
            'pages': 'monthly'
        }
        self.priorities = {
            'articles': 0.5,
            'indexes': 0.5,
            'pages': 0.5
        }

        config = self.settings.get('SITEMAP', {})
        if not isinstance(config, dict):
            warning("sitemap plugin: the SITEMAP setting must be a dict")
        else:
            fmt = config.get('format')
            gens = config.get('generate')
            pris = config.get('priorities')
            chfreqs = config.get('changefreqs')

            if isinstance(gens, list):
                for k in gens:
                    if k not in self.generate:
                        warning("sitemap plugin: `{0}' is incorrect value for "
                                "generate".format(k))
                # intersection
                self.generate = list(set(self.generate) & set(gens))

            if fmt not in ('xml', 'txt'):
                warning("sitemap plugin: SITEMAP['format'] "
                        "must be `txt' or `xml'")
                warning("sitemap plugin: Setting SITEMAP['format'] on `xml'")
            elif fmt == 'txt':
                self.format = fmt
                return

            valid_chfreqs = ('always', 'hourly', 'daily', 'weekly', 'monthly',
                             'yearly', 'never', None)

            if isinstance(pris, dict):
                for k, v in pris.iteritems():
                    if k in self.generate and \
                            not (isinstance(v, (int, float)) or v is None):
                        default = self.priorities[k]
                        warning("sitemap plugin: priorities must be numbers")
                        warning("sitemap plugin: setting SITEMAP['priorities']"
                                "['{0}'] on {1}".format(k, default))
                        pris[k] = default
                self.priorities.update(pris)
            elif pris is not None:
                warning("sitemap plugin: SITEMAP['priorities'] must be a dict")
                warning("sitemap plugin: using the default values")

            if isinstance(chfreqs, dict):
                for k, v in chfreqs.iteritems():
                    if k in self.generate and v not in valid_chfreqs:
                        default = self.changefreqs[k]
                        warning("sitemap plugin: invalid changefreq `{0}'"
                                .format(v))
                        warning(
                            "sitemap plugin: setting SITEMAP['changefreqs']"
                            "['{0}'] on '{1}'".format(k, default))
                        chfreqs[k] = default
                self.changefreqs.update(chfreqs)
            elif chfreqs is not None:
                warning(
                    "sitemap plugin: SITEMAP['changefreqs'] must be a dict")
                warning("sitemap plugin: using the default values")

    def generate_output(self, writer):
        path = os.path.join(
            self.output_path, 'sitemap.{0}'.format(self.format))

        # get all context objects
        articles = []
        if "articles" in self.generate and \
                self.settings.get('ARTICLE_SAVE_AS'):
            articles = list(self.context['articles'])
            for article in self.context['articles']:
                articles += article.translations
            for article in articles:
                article.lastmod = format_date(article.updated)

        pages = []
        if "pages" in self.generate and self.settings.get('PAGE_SAVE_AS'):
            pages = list(self.context['pages'])
            for page in self.context['pages']:
                pages += page.translations
            for page in pages:
                page.lastmod = format_date(getattr(page, 'updated', self.now))

        indexes = []
        if "indexes" in self.generate:
            if self.settings.get('CATEGORY_SAVE_AS'):
                indexes += [c for (c, a) in self.context['categories']]
            if self.settings.get('TAG_SAVE_AS'):
                indexes += [t for (t, a) in self.context['tags']]
            if self.settings.get('AUTHOR_SAVE_AS'):
                indexes += [a for (a, b) in self.context['authors']]

            if self.settings.get('CATEGORIES_SAVE_AS'):
                indexes.append({'url': self.settings.get('CATEGORIES_URL')})
            if self.settings.get('TAGS_SAVE_AS'):
                indexes.append({'url': self.settings.get('TAGS_URL')})
            if self.settings.get('ARCHIVES_SAVE_AS'):
                indexes.append({'url': self.settings.get('ARCHIVES_URL')})
            if self.settings.get('INDEX_SAVE_AS'):
                indexes.append({'url': self.settings.get('INDEX_URL')})

            for item in indexes:
                item.lastmod = format_date(getattr(item, 'updated', self.now))

        # remove unpublished posts
        def is_published(item):
            default_status = self.settings.get('DEFAULT_STATUS')
            return getattr(item, 'status', default_status) == 'published'

        articles = filter(is_published, articles)
        pages = filter(is_published, pages)

        # write to file
        info('writing {0}'.format(path))
        with open(path, 'w', encoding='utf-8') as fd:
            if self.format == 'xml':
                template = Template(XML_TEMPLATE)
            else:
                template = Template(TXT_TEMPLATE)

            fd.write(template.render(
                articles=articles,
                pages=pages,
                indexes=indexes,
                siteurl=self.settings.get('SITEURL'),
                changefreqs=self.changefreqs,
                priorities=self.priorities
            ))


def get_generators(generators):
    return SitemapGenerator


def register():
    signals.get_generators.connect(get_generators)
