import logging
import os
from posixpath import join as posix_join
from urllib.parse import urljoin

from feedgenerator import Atom1Feed, Rss201rev2Feed, get_tag_uri

from markupsafe import Markup

from pelican.paginator import Paginator
from pelican.plugins import signals
from pelican.utils import (get_relative_path, is_selected_for_writing,
                           path_to_url, sanitised_join, set_date_tzinfo)

logger = logging.getLogger(__name__)


class Writer:

    def __init__(self, output_path, settings=None):
        self.output_path = output_path
        self.reminder = dict()
        self.settings = settings or {}
        self._written_files = set()
        self._overridden_files = set()

        # See Content._link_replacer for details
        if "RELATIVE_URLS" in self.settings and self.settings['RELATIVE_URLS']:
            self.urljoiner = posix_join
        else:
            self.urljoiner = lambda base, url: urljoin(
                base if base.endswith('/') else base + '/', url)

    def _create_new_feed(self, feed_type, feed_title, context):
        feed_class = Rss201rev2Feed if feed_type == 'rss' else Atom1Feed
        if feed_title:
            feed_title = context['SITENAME'] + ' - ' + feed_title
        else:
            feed_title = context['SITENAME']
        feed = feed_class(
            title=Markup(feed_title).striptags(),
            link=(self.site_url + '/'),
            feed_url=self.feed_url,
            description=context.get('SITESUBTITLE', ''),
            subtitle=context.get('SITESUBTITLE', None))
        return feed

    def _add_item_to_the_feed(self, feed, item):
        title = Markup(item.title).striptags()
        link = self.urljoiner(self.site_url, item.url)

        if isinstance(feed, Rss201rev2Feed):
            # RSS feeds use a single tag called 'description' for both the full
            # content and the summary
            content = None
            if self.settings.get('RSS_FEED_SUMMARY_ONLY'):
                description = item.summary
            else:
                description = item.get_content(self.site_url)

        else:
            # Atom feeds have two different tags for full content (called
            # 'content' by feedgenerator) and summary (called 'description' by
            # feedgenerator).
            #
            # It does not make sense to have the summary be the
            # exact same thing as the full content. If we detect that
            # they are we just remove the summary.
            content = item.get_content(self.site_url)
            description = item.summary
            if description == content:
                description = None

        categories = list()
        if hasattr(item, 'category'):
            categories.append(item.category)
        if hasattr(item, 'tags'):
            categories.extend(item.tags)

        feed.add_item(
            title=title,
            link=link,
            unique_id=get_tag_uri(link, item.date),
            description=description,
            content=content,
            categories=categories if categories else None,
            author_name=getattr(item, 'author', ''),
            pubdate=set_date_tzinfo(
                item.date, self.settings.get('TIMEZONE', None)),
            updateddate=set_date_tzinfo(
                item.modified, self.settings.get('TIMEZONE', None)
                ) if hasattr(item, 'modified') else None)

    def _open_w(self, filename, encoding, override=False):
        """Open a file to write some content to it.

        Exit if we have already written to that file, unless one (and no more
        than one) of the writes has the override parameter set to True.
        """
        if filename in self._overridden_files:
            if override:
                raise RuntimeError('File %s is set to be overridden twice'
                                   % filename)
            else:
                logger.info('Skipping %s', filename)
                filename = os.devnull
        elif filename in self._written_files:
            if override:
                logger.info('Overwriting %s', filename)
            else:
                raise RuntimeError('File %s is to be overwritten' % filename)
        if override:
            self._overridden_files.add(filename)
        self._written_files.add(filename)
        return open(filename, 'w', encoding=encoding)

    def write_feed(self, elements, context, path=None, url=None,
                   feed_type='atom', override_output=False, feed_title=None):
        """Generate a feed with the list of articles provided

        Return the feed. If no path or output_path is specified, just
        return the feed object.

        :param elements: the articles to put on the feed.
        :param context: the context to get the feed metadata.
        :param path: the path to output.
        :param url: the publicly visible feed URL; if None, path is used
            instead
        :param feed_type: the feed type to use (atom or rss)
        :param override_output: boolean telling if we can override previous
            output with the same name (and if next files written with the same
            name should be skipped to keep that one)
        :param feed_title: the title of the feed.o
        """
        if not is_selected_for_writing(self.settings, path):
            return

        self.site_url = context.get(
            'SITEURL', path_to_url(get_relative_path(path)))

        self.feed_domain = context.get('FEED_DOMAIN')
        self.feed_url = self.urljoiner(self.feed_domain, url if url else path)

        feed = self._create_new_feed(feed_type, feed_title, context)

        max_items = len(elements)
        if self.settings['FEED_MAX_ITEMS']:
            max_items = min(self.settings['FEED_MAX_ITEMS'], max_items)
        for i in range(max_items):
            self._add_item_to_the_feed(feed, elements[i])

        signals.feed_generated.send(context, feed=feed)
        if path:
            complete_path = sanitised_join(self.output_path, path)

            try:
                os.makedirs(os.path.dirname(complete_path))
            except Exception:
                pass

            with self._open_w(complete_path, 'utf-8', override_output) as fp:
                feed.write(fp, 'utf-8')
                logger.info('Writing %s', complete_path)

            signals.feed_written.send(
                complete_path, context=context, feed=feed)
        return feed

    def write_file(self, name, template, context, relative_urls=False,
                   paginated=None, template_name=None, override_output=False,
                   url=None, **kwargs):
        """Render the template and write the file.

        :param name: name of the file to output
        :param template: template to use to generate the content
        :param context: dict to pass to the templates.
        :param relative_urls: use relative urls or absolutes ones
        :param paginated: dict of article list to paginate - must have the
            same length (same list in different orders)
        :param template_name: the template name, for pagination
        :param override_output: boolean telling if we can override previous
            output with the same name (and if next files written with the same
            name should be skipped to keep that one)
        :param url: url of the file (needed by the paginator)
        :param **kwargs: additional variables to pass to the templates
        """

        if name is False or \
           name == "" or \
           not is_selected_for_writing(self.settings,
                                       os.path.join(self.output_path, name)):
            return
        elif not name:
            # other stuff, just return for now
            return

        def _write_file(template, localcontext, output_path, name, override):
            """Render the template write the file."""
            # set localsiteurl for context so that Contents can adjust links
            if localcontext['localsiteurl']:
                context['localsiteurl'] = localcontext['localsiteurl']
            output = template.render(localcontext)
            path = sanitised_join(output_path, name)

            try:
                os.makedirs(os.path.dirname(path))
            except Exception:
                pass

            with self._open_w(path, 'utf-8', override=override) as f:
                f.write(output)
            logger.info('Writing %s', path)

            # Send a signal to say we're writing a file with some specific
            # local context.
            signals.content_written.send(path, context=localcontext)

        def _get_localcontext(context, name, kwargs, relative_urls):
            localcontext = context.copy()
            localcontext['localsiteurl'] = localcontext.get(
                'localsiteurl', None)
            if relative_urls:
                relative_url = path_to_url(get_relative_path(name))
                localcontext['SITEURL'] = relative_url
                localcontext['localsiteurl'] = relative_url
            localcontext['output_file'] = name
            localcontext.update(kwargs)
            return localcontext

        if paginated is None:
            paginated = {key: val for key, val in kwargs.items()
                         if key in {'articles', 'dates'}}

        # pagination
        if paginated and template_name in self.settings['PAGINATED_TEMPLATES']:
            # pagination needed
            per_page = self.settings['PAGINATED_TEMPLATES'][template_name] \
                or self.settings['DEFAULT_PAGINATION']

            # init paginators
            paginators = {key: Paginator(name, url, val, self.settings,
                                         per_page)
                          for key, val in paginated.items()}

            # generated pages, and write
            for page_num in range(list(paginators.values())[0].num_pages):
                paginated_kwargs = kwargs.copy()
                for key in paginators.keys():
                    paginator = paginators[key]
                    previous_page = paginator.page(page_num) \
                        if page_num > 0 else None
                    page = paginator.page(page_num + 1)
                    next_page = paginator.page(page_num + 2) \
                        if page_num + 1 < paginator.num_pages else None
                    paginated_kwargs.update(
                        {'%s_paginator' % key: paginator,
                         '%s_page' % key: page,
                         '%s_previous_page' % key: previous_page,
                         '%s_next_page' % key: next_page})

                localcontext = _get_localcontext(
                    context, page.save_as, paginated_kwargs, relative_urls)
                _write_file(template, localcontext, self.output_path,
                            page.save_as, override_output)
        else:
            # no pagination
            localcontext = _get_localcontext(
                context, name, kwargs, relative_urls)
            _write_file(template, localcontext, self.output_path, name,
                        override_output)
