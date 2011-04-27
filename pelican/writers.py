# -*- coding: utf-8 -*-
import os
import re
from codecs import open
from functools import partial
import locale

from feedgenerator import Atom1Feed, Rss201rev2Feed
from pelican.utils import get_relative_path
from pelican.paginator import Paginator
from pelican.log import *


class Writer(object):

    def __init__(self, output_path, settings=None):
        self.output_path = output_path
        self.reminder = dict()
        self.settings = settings or {}

    def _create_new_feed(self, feed_type, context):
        feed_class = Rss201rev2Feed if feed_type == 'rss' else Atom1Feed
        feed = feed_class(
            title=context['SITENAME'],
            link=self.site_url,
            feed_url=self.feed_url,
            description=context.get('SITESUBTITLE', ''))
        return feed


    def _add_item_to_the_feed(self, feed, item):

        feed.add_item(
            title=item.title,
            link='%s/%s' % (self.site_url, item.url),
            description=item.content,
            categories=item.tags if hasattr(item, 'tags') else None,
            author_name=getattr(item, 'author', 'John Doe'),
            pubdate=item.date)

    def write_feed(self, elements, context, filename=None, feed_type='atom'):
        """Generate a feed with the list of articles provided

        Return the feed. If no output_path or filename is specified, just return
        the feed object.

        :param articles: the articles to put on the feed.
        :param context: the context to get the feed metadata.
        :param output_path: where to output the file.
        :param filename: the filename to output.
        :param feed_type: the feed type to use (atom or rss)
        """
        old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
        try:
            self.site_url = context.get('SITEURL', get_relative_path(filename))
            self.feed_url= '%s/%s' % (self.site_url, filename)

            feed = self._create_new_feed(feed_type, context)

            for item in elements:
                self._add_item_to_the_feed(feed, item)

            if filename:
                complete_path = os.path.join(self.output_path, filename)
                try:
                    os.makedirs(os.path.dirname(complete_path))
                except Exception:
                    pass
                fp = open(complete_path, 'w')
                feed.write(fp, 'utf-8')
                info('writing %s' % complete_path)

                fp.close()
            return feed
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)

    def write_file(self, name, template, context, relative_urls=True,
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

        def _write_file(template, localcontext, output_path, name):
            """Render the template write the file."""
            old_locale = locale.setlocale(locale.LC_ALL)
            locale.setlocale(locale.LC_ALL, 'C')
            try:
                output = template.render(localcontext)
            finally:
                locale.setlocale(locale.LC_ALL, old_locale)
            filename = os.sep.join((output_path, name))
            try:
                os.makedirs(os.path.dirname(filename))
            except Exception:
                pass
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            info(u'writing %s' % filename)

        localcontext = context.copy()
        if relative_urls:
            localcontext['SITEURL'] = get_relative_path(name)

        localcontext.update(kwargs)
        self.update_context_contents(name, localcontext)

        # check paginated
        paginated = paginated or {}
        if paginated:
            # pagination needed, init paginators
            paginators = {}
            for key in paginated.iterkeys():
                object_list = paginated[key]

                if self.settings.get('WITH_PAGINATION'):
                    paginators[key] = Paginator(object_list,
                        self.settings.get('DEFAULT_PAGINATION'),
                        self.settings.get('DEFAULT_ORPHANS'))
                else:
                    paginators[key] = Paginator(object_list, len(object_list), 0)

            # generated pages, and write
            for page_num in range(paginators.values()[0].num_pages):
                paginated_localcontext = localcontext.copy()
                paginated_name = name
                for key in paginators.iterkeys():
                    paginator = paginators[key]
                    page = paginator.page(page_num+1)
                    paginated_localcontext.update({'%s_paginator' % key: paginator,
                                                   '%s_page' % key: page})
                if page_num > 0:
                    ext = '.' + paginated_name.rsplit('.')[-1]
                    paginated_name = paginated_name.replace(ext, 
                            '%s%s' % (page_num + 1, ext))

                _write_file(template, paginated_localcontext, self.output_path,
                        paginated_name)
        else:
            # no pagination
            _write_file(template, localcontext, self.output_path, name)

    def update_context_contents(self, name, context):
        """Recursively run the context to find elements (articles, pages, etc) 
        whose content getter needs to
        be modified in order to deal with relative paths.

        :param name: name of the file to output.
        :param context: dict that will be passed to the templates.
        """
        if context is None:
            return None

        if type(context) == tuple:
            context = list(context)

        if type(context) == dict:
            context = list(context.values())

        for i in xrange(len(context)):
            if type(context[i]) == tuple or type(context[i]) == list:
                context[i] = self.update_context_contents(name, context[i])

            elif type(context[i]) == dict:
                context[i] = self.update_context_contents(name, context[i].values())

            elif hasattr(context[i], '_content'):
                relative_path = get_relative_path(name)
                item = context[i]

                if item in self.reminder:
                    if relative_path not in self.reminder[item]:
                        l = self.reminder[item]
                        l.append(relative_path)
                        self.inject_update_method(name, item)
                else:
                    l = list(relative_path)
                    self.reminder[item] = l
                    self.inject_update_method(name, item)
        return context

    def inject_update_method(self, name, item):
        """Replace the content attribute getter of an element by a function 
        that will deals with its relatives paths.
        """

        def _update_object_content(name, input):
            """Change all the relatives paths of the input content to relatives 
            paths suitable fot the ouput content

            :param name: path of the output.
            :param input: input resource that will be passed to the templates.
            """
            content = input._content

            hrefs = re.compile(r'<\s*[^\>]*href\s*=(^!#)\s*(["\'])(.*?)\1')
            srcs = re.compile(r'<\s*[^\>]*src\s*=\s*(["\'])(.*?)\1')

            matches = hrefs.findall(content)
            matches.extend(srcs.findall(content))
            relative_paths = []
            for found in matches:
                found = found[1]
                if found not in relative_paths:
                    relative_paths.append(found)

            for relative_path in relative_paths:
                if not ":" in relative_path: # we don't want to rewrite protocols
                    dest_path = os.sep.join((get_relative_path(name), "static",
                        relative_path))
                    content = content.replace(relative_path, dest_path)

            return content

        if item:
            setattr(item, "_get_content",
                partial(_update_object_content, name, item))
