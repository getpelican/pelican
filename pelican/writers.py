# -*- coding: utf-8 -*-
import os
from codecs import open

from feedgenerator import Atom1Feed, Rss201rev2Feed

from pelican.utils import get_relative_path

class Writer(object):

    def __init__(self, output_path):
        self.output_path = output_path

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
        site_url = context.get('SITEURL', get_relative_path(filename))

        feed_class = Rss201rev2Feed if feed_type == 'rss' else Atom1Feed

        feed = feed_class(
            title=context['SITENAME'],
            link=site_url,
            feed_url= "%s/%s" % (site_url, filename),
            description=context.get('SITESUBTITLE', ''))
        for element in elements:
            feed.add_item(
                title=element.title,
                link= "%s/%s" % (site_url, element.url),
                description=element.content,
                categories=element.tags if hasattr(element, "tags") else None,
                author_name=getattr(element, 'author', 'John Doe'),
                pubdate=element.date)

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
