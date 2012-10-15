import collections
import os.path

from datetime import datetime
from logging import warning, info
from codecs import open

from pelican import signals, contents

TXT_HEADER = u"""{0}/index.html
{0}/archives.html
{0}/tags.html
{0}/categories.html
"""

XML_HEADER = u"""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

XML_URL = u"""
<url>
<loc>{0}/{1}</loc>
<lastmod>{2}</lastmod>
<changefreq>{3}</changefreq>
<priority>{4}</priority>
</url>
"""

XML_FOOTER = u"""
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
        self.context = context
        self.now = datetime.now()
        self.siteurl = settings.get('SITEURL')

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

        config = settings.get('SITEMAP', {})

        if not isinstance(config, dict):
            warning("sitemap plugin: the SITEMAP setting must be a dict")
        else:
            fmt = config.get('format')
            pris = config.get('priorities')
            chfreqs = config.get('changefreqs')

            if fmt not in ('xml', 'txt'):
                warning("sitemap plugin: SITEMAP['format'] must be `txt' or `xml'")
                warning("sitemap plugin: Setting SITEMAP['format'] on `xml'")
            elif fmt == 'txt':
                self.format = fmt
                return

            valid_keys = ('articles', 'indexes', 'pages')
            valid_chfreqs = ('always', 'hourly', 'daily', 'weekly', 'monthly',
                    'yearly', 'never')

            if isinstance(pris, dict):
                for k, v in pris.iteritems():
                    if k in valid_keys and not isinstance(v, (int, float)):
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
                    if k in valid_keys and v not in valid_chfreqs:
                        default = self.changefreqs[k]
                        warning("sitemap plugin: invalid changefreq `{0}'".format(v))
                        warning("sitemap plugin: setting SITEMAP['changefreqs']"
                                "['{0}'] on '{1}'".format(k, default))
                        chfreqs[k] = default
                self.changefreqs.update(chfreqs)
            elif chfreqs is not None:
                warning("sitemap plugin: SITEMAP['changefreqs'] must be a dict")
                warning("sitemap plugin: using the default values")



    def write_url(self, page, fd):

        if getattr(page, 'status', 'published') != 'published':
            return

        page_path = os.path.join(self.output_path, page.url)
        if not os.path.exists(page_path):
            return

        lastmod = format_date(getattr(page, 'date', self.now))

        if isinstance(page, contents.Article):
            pri = self.priorities['articles']
            chfreq = self.changefreqs['articles']
        elif isinstance(page, contents.Page):
            pri = self.priorities['pages']
            chfreq = self.changefreqs['pages']
        else:
            pri = self.priorities['indexes']
            chfreq = self.changefreqs['indexes']


        if self.format == 'xml':
            fd.write(XML_URL.format(self.siteurl, page.url, lastmod, chfreq, pri))
        else:
            fd.write(self.siteurl + '/' + loc + '\n')


    def generate_output(self, writer):
        path = os.path.join(self.output_path, 'sitemap.{0}'.format(self.format))

        pages = self.context['pages'] + self.context['articles'] \
                + [ c for (c, a) in self.context['categories']] \
                + [ t for (t, a) in self.context['tags']] \
                + [ a for (a, b) in self.context['authors']]

        for article in self.context['articles']:
            pages += article.translations

        info('writing {0}'.format(path))

        with open(path, 'w', encoding='utf-8') as fd:

            if self.format == 'xml':
                fd.write(XML_HEADER)
            else:
                fd.write(TXT_HEADER.format(self.siteurl))

            FakePage = collections.namedtuple('FakePage',
                                              ['status',
                                               'date',
                                               'url'])

            for standard_page_url in ['index.html',
                                      'archives.html',
                                      'tags.html',
                                      'categories.html']:
                fake = FakePage(status='published',
                                date=self.now,
                                url=standard_page_url)
                self.write_url(fake, fd)

            for page in pages:
                self.write_url(page, fd)

            if self.format == 'xml':
                fd.write(XML_FOOTER)


def get_generators(generators):
    return SitemapGenerator


def register():
    signals.get_generators.connect(get_generators)
