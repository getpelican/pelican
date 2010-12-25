# -*- coding: utf-8 -*-
import os
from codecs import open

from feedgenerator import Atom1Feed, Rss201rev2Feed

from pelican.utils import get_relative_path

class Writer(object):

    def __init__(self, output_path):
        self.output_path = output_path

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
            print u' [ok] writing %s' % complete_path

            fp.close()
        return feed

    def write_file(self, name, template, context, relative_urls=True,
        **kwargs):
        """Render the template and write the file.

        :param name: name of the file to output
        :param template: template to use to generate the content
        :param context: dict to pass to the templates.
        :param relative_urls: use relative urls or absolutes ones
        :param **kwargs: additional variables to pass to the templates
        """
        localcontext = context.copy()
        if relative_urls:
            localcontext['SITEURL'] = get_relative_path(name)

        localcontext.update(kwargs)
        output = template.render(localcontext)
        filename = os.sep.join((self.output_path, name))
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception:
            pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print u' [ok] writing %s' % filename
