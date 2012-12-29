# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals, print_function
import six

import os
import locale
import logging

if not six.PY3:
    from codecs import open

from feedgenerator import Atom1Feed, Rss201rev2Feed
from jinja2 import Markup
from pelican.paginator import Paginator
from pelican.utils import get_relative_path, path_to_url, set_date_tzinfo

logger = logging.getLogger(__name__)


class Writer(object):

    def __init__(self, output_path, settings=None):
        self.output_path = output_path
        self.reminder = dict()
        self.settings = settings or {}
        self._written_files = set()

    def _create_new_feed(self, feed_type, context):
        feed_class = Rss201rev2Feed if feed_type == 'rss' else Atom1Feed
        sitename = Markup(context['SITENAME']).striptags()
        feed = feed_class(
            title=sitename,
            link=(self.site_url + '/'),
            feed_url=self.feed_url,
            description=context.get('SITESUBTITLE', ''))
        return feed

    def _add_item_to_the_feed(self, feed, item):

        title = Markup(item.title).striptags()
        feed.add_item(
            title=title,
            link='%s/%s' % (self.site_url, item.url),
            unique_id='tag:%s,%s:%s' % (self.site_url.replace('http://', ''),
                                        item.date.date(), item.url),
            description=item.get_content(self.site_url),
            categories=item.tags if hasattr(item, 'tags') else None,
            author_name=getattr(item, 'author', ''),
            pubdate=set_date_tzinfo(item.date,
                self.settings.get('TIMEZONE', None)))

    def _open_w(self, filename, encoding):
        """Open a file to write some content to it.

        Exit if we have already written to that file.
        """
        if filename in self._written_files:
            raise IOError('File %s is to be overwritten' % filename)
        self._written_files.add(filename)
        return open(filename, 'w', encoding=encoding)

    def write_feed(self, elements, context, path=None, feed_type='atom'):
        """Generate a feed with the list of articles provided

        Return the feed. If no path or output_path is specified, just
        return the feed object.

        :param elements: the articles to put on the feed.
        :param context: the context to get the feed metadata.
        :param path: the path to output.
        :param feed_type: the feed type to use (atom or rss)
        """
        old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))
        try:
            self.site_url = context.get(
                'SITEURL', path_to_url(get_relative_path(path)))

            self.feed_domain = context.get('FEED_DOMAIN')
            self.feed_url = '{}/{}'.format(self.feed_domain, path)

            feed = self._create_new_feed(feed_type, context)

            max_items = len(elements)
            if self.settings['FEED_MAX_ITEMS']:
                max_items = min(self.settings['FEED_MAX_ITEMS'], max_items)
            for i in range(max_items):
                self._add_item_to_the_feed(feed, elements[i])

            if path:
                complete_path = os.path.join(self.output_path, path)
                try:
                    os.makedirs(os.path.dirname(complete_path))
                except Exception:
                    pass

                encoding = 'utf-8' if six.PY3 else None
                with self._open_w(complete_path, encoding) as fp:
                    feed.write(fp, 'utf-8')
                    logger.info('writing %s' % complete_path)
            return feed
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)

    def write_file(self, name, template, context, relative_urls=False,
        paginated=None, **kwargs):
        """Render the template and write the file.

        :param name: name of the file to output
        :param template: template to use to generate the content
        :param context: dict to pass to the templates.
        :param relative_urls: use relative urls or absolutes ones
        :param paginated: dict of article list to paginate - must have the
            same length (same list in different orders)
        :param **kwargs: additional variables to pass to the templates
        """

        if name is False:
            return
        elif not name:
            # other stuff, just return for now
            return

        def _write_file(template, localcontext, output_path, name):
            """Render the template write the file."""
            old_locale = locale.setlocale(locale.LC_ALL)
            locale.setlocale(locale.LC_ALL, str('C'))
            try:
                output = template.render(localcontext)
            finally:
                locale.setlocale(locale.LC_ALL, old_locale)
            path = os.path.join(output_path, name)
            try:
                os.makedirs(os.path.dirname(path))
            except Exception:
                pass
            with self._open_w(path, 'utf-8') as f:
                f.write(output)
            logger.info('writing {}'.format(path))

        localcontext = context.copy()
        if relative_urls:
            relative_url = path_to_url(get_relative_path(name))
            context['localsiteurl'] = relative_url
            localcontext['SITEURL'] = relative_url

        localcontext['output_file'] = name
        localcontext.update(kwargs)

        # check paginated
        paginated = paginated or {}
        if paginated:
            name_root, ext = os.path.splitext(name)

            # pagination needed, init paginators
            paginators = {}
            for key in paginated.keys():
                object_list = paginated[key]

                paginators[key] = Paginator(
                    name_root,
                    object_list,
                    self.settings,
                )

            # generated pages, and write
            for page_num in range(list(paginators.values())[0].num_pages):
                paginated_localcontext = localcontext.copy()
                for key in paginators.keys():
                    paginator = paginators[key]
                    previous_page = paginator.page(page_num) \
                            if page_num > 0 else None
                    page = paginator.page(page_num + 1)
                    next_page = paginator.page(page_num + 2) \
                            if page_num + 1 < paginator.num_pages else None
                    paginated_localcontext.update(
                            {'%s_paginator' % key: paginator,
                             '%s_page' % key: page,
                             '%s_previous_page' % key: previous_page,
                             '%s_next_page' % key: next_page})

                _write_file(template, paginated_localcontext, self.output_path,
                            page.save_as)
        else:
            # no pagination
            _write_file(template, localcontext, self.output_path, name)
