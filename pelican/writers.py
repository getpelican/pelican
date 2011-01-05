# -*- coding: utf-8 -*-
import os
import re
from codecs import open
from functools import partial

from feedgenerator import Atom1Feed, Rss201rev2Feed

from pelican.utils import get_relative_path


class Writer(object):

    def __init__(self, output_path):
        self.output_path = output_path
        self.reminder = dict()

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
        self.update_context_contents(name, localcontext)

        output = template.render(localcontext)
        filename = os.sep.join((self.output_path, name))
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception:
            pass
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print u' [ok] writing %s' % filename

    def update_context_contents(self, name, context):
        """Recursively run the context to find elements (articles, pages, etc) whose content getter needs to
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
                context[i] = self.update_context_content(name, context[i].values())

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
        """Replace the content attribute getter of an element by a function that will deals with its
           relatives paths.
        """

        def _update_object_content(name, input):
            """Change all the relatives paths of the input content to relatives paths
               suitable fot the ouput content

            :param name: path of the output.
            :param input: input resource that will be passed to the templates.
            """
            content = input._content

            hrefs = re.compile(r'<\s*[^\>]*href\s*=\s*(["\'])(.*?)\1')
            srcs = re.compile(r'<\s*[^\>]*src\s*=\s*(["\'])(.*?)\1')

            matches = hrefs.findall(content)
            matches.extend(srcs.findall(content))
            relative_paths = []
            for found in matches:
                found = found[1]
                if found not in relative_paths:
                    relative_paths.append(found)

            for relative_path in relative_paths:
                if not relative_path.startswith("http://"):
                    dest_path = os.sep.join((get_relative_path(name), "static", relative_path))
                    content = content.replace(relative_path, dest_path)

            return content

        if item:
            setattr(item, "_get_content",
                partial(_update_object_content, name, item))
