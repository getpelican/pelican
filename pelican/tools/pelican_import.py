#!/usr/bin/env python

import argparse
from HTMLParser import HTMLParser
import os
import subprocess
import sys
import time

from codecs import open

from pelican.utils import slugify


def wp2fields(xml):
    """Opens a wordpress XML file, and yield pelican fields"""
    try:
        from BeautifulSoup import BeautifulStoneSoup
    except ImportError:
        error = ('Missing dependency '
                 '"BeautifulSoup" required to import Wordpress XML files.')
        sys.exit(error)

    xmlfile = open(xml, encoding='utf-8').read()
    soup = BeautifulStoneSoup(xmlfile)
    items = soup.rss.channel.findAll('item')

    for item in items:

        if item.fetch('wp:status')[0].contents[0] == "publish":

            try:
                # Use HTMLParser due to issues with BeautifulSoup 3
                title = HTMLParser().unescape(item.title.contents[0])
            except IndexError:
                continue

            content = item.fetch('content:encoded')[0].contents[0]
            filename = item.fetch('wp:post_name')[0].contents[0]

            raw_date = item.fetch('wp:post_date')[0].contents[0]
            date_object = time.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            date = time.strftime("%Y-%m-%d %H:%M", date_object)

            author = item.fetch('dc:creator')[0].contents[0].title()

            categories = [cat.contents[0] for cat in item.fetch(domain='category')]
            # caturl = [cat['nicename'] for cat in item.fetch(domain='category')]

            tags = [tag.contents[0] for tag in item.fetch(domain='post_tag')]

            yield (title, content, filename, date, author, categories, tags, "html")

def dc2fields(file):
    """Opens a Dotclear export file, and yield pelican fields"""
    try:
        from BeautifulSoup import BeautifulStoneSoup
    except ImportError:
        error = ('Missing dependency '
                 '"BeautifulSoup" required to import Dotclear files.')
        sys.exit(error)


    in_cat = False
    in_post = False
    category_list = {}
    posts = []

    with open(file, 'r', encoding='utf-8') as f:

        for line in f:
            # remove final \n
            line = line[:-1]

            if line.startswith('[category'):
                in_cat = True
            elif line.startswith('[post'):
                in_post = True
            elif in_cat:
                fields = line.split('","')
                if not line:
                    in_cat = False
                else:
                    # remove 1st and last ""
                    fields[0] = fields[0][1:]
                    # fields[-1] = fields[-1][:-1]
                    category_list[fields[0]]=fields[2]
            elif in_post:
                if not line:
                    in_post = False
                    break
                else:
                    posts.append(line)

    print("%i posts read." % len(posts))

    for post in posts:
        fields = post.split('","')

        # post_id = fields[0][1:]
        # blog_id = fields[1]
        # user_id = fields[2]
        cat_id = fields[3]
        # post_dt = fields[4]
        # post_tz = fields[5]
        post_creadt = fields[6]
        # post_upddt = fields[7]
        # post_password = fields[8]
        # post_type = fields[9]
        post_format = fields[10]
        # post_url = fields[11]
        # post_lang = fields[12]
        post_title = fields[13]
        post_excerpt = fields[14]
        post_excerpt_xhtml = fields[15]
        post_content = fields[16]
        post_content_xhtml = fields[17]
        # post_notes = fields[18]
        # post_words = fields[19]
        # post_status = fields[20]
        # post_selected = fields[21]
        # post_position = fields[22]
        # post_open_comment = fields[23]
        # post_open_tb = fields[24]
        # nb_comment = fields[25]
        # nb_trackback = fields[26]
        post_meta = fields[27]
        # redirect_url = fields[28][:-1]

        # remove seconds
        post_creadt = ':'.join(post_creadt.split(':')[0:2])

        author = ""
        categories = []
        tags = []

        if cat_id:
            categories = [category_list[id].strip() for id in cat_id.split(',')]

        # Get tags related to a post
        tag = post_meta.replace('{', '').replace('}', '').replace('a:1:s:3:\\"tag\\";a:', '').replace('a:0:', '')
        if len(tag) > 1:
            if int(tag[:1]) == 1:
                newtag = tag.split('"')[1]
                tags.append(unicode(BeautifulStoneSoup(newtag,convertEntities=BeautifulStoneSoup.HTML_ENTITIES )))
            else:
                i=1
                j=1
                while(i <= int(tag[:1])):
                    newtag = tag.split('"')[j].replace('\\','')
                    tags.append(unicode(BeautifulStoneSoup(newtag,convertEntities=BeautifulStoneSoup.HTML_ENTITIES )))
                    i=i+1
                    if j < int(tag[:1])*2:
                        j=j+2

        """
        dotclear2 does not use markdown by default unless you use the markdown plugin
        Ref: http://plugins.dotaddict.org/dc2/details/formatting-markdown
        """
        if post_format == "markdown":
            content = post_excerpt + post_content
        else:
            content = post_excerpt_xhtml + post_content_xhtml
            content = content.replace('\\n', '')
            post_format = "html"

        yield (post_title, content, slugify(post_title), post_creadt, author, categories, tags, post_format)


def feed2fields(file):
    """Read a feed and yield pelican fields"""
    import feedparser
    d = feedparser.parse(file)
    for entry in d.entries:
        date = (time.strftime("%Y-%m-%d %H:%M", entry.updated_parsed)
            if hasattr(entry, "updated_parsed") else None)
        author = entry.author if hasattr(entry, "author") else None
        tags = [e['term'] for e in entry.tags] if hasattr(entry, "tags") else None

        slug = slugify(entry.title)
        yield (entry.title, entry.description, slug, date, author, [], tags, "html")


def build_header(title, date, author, categories, tags):
    """Build a header from a list of fields"""
    header = '%s\n%s\n' % (title, '#' * len(title))
    if date:
        header += ':date: %s\n' % date
    if author:
        header += ':author: %s\n' % author
    if categories:
        header += ':category: %s\n' % ', '.join(categories)
    if tags:
        header += ':tags: %s\n' % ', '.join(tags)
    header += '\n'
    return header

def build_markdown_header(title, date, author, categories, tags):
    """Build a header from a list of fields"""
    header = 'Title: %s\n' % title
    if date:
        header += 'Date: %s\n' % date
    if author:
        header += 'Author: %s\n' % author
    if categories:
        header += 'Category: %s\n' % ', '.join(categories)
    if tags:
        header += 'Tags: %s\n' % ', '.join(tags)
    header += '\n'
    return header

def fields2pelican(fields, out_markup, output_path, dircat=False, strip_raw=False):
    for title, content, filename, date, author, categories, tags, in_markup in fields:
        if (in_markup == "markdown") or (out_markup == "markdown") :
            ext = '.md'
            header = build_markdown_header(title, date, author, categories, tags)
        else:
            out_markup = "rst"
            ext = '.rst'
            header = build_header(title, date, author, categories, tags)

        filename = os.path.basename(filename)

        # option to put files in directories with categories names
        if dircat and (len(categories) > 0):
            catname = slugify(categories[0])
            out_filename = os.path.join(output_path, catname, filename+ext)
            if not os.path.isdir(os.path.join(output_path, catname)):
                os.mkdir(os.path.join(output_path, catname))
        else:
            out_filename = os.path.join(output_path, filename+ext)

        print(out_filename)

        if in_markup == "html":
            html_filename = os.path.join(output_path, filename+'.html')

            with open(html_filename, 'w', encoding='utf-8') as fp:
                # Replace newlines with paragraphs wrapped with <p> so
                # HTML is valid before conversion
                paragraphs = content.splitlines()
                paragraphs = [u'<p>{0}</p>'.format(p) for p in paragraphs]
                new_content = ''.join(paragraphs)

                fp.write(new_content)


            parse_raw = '--parse-raw' if not strip_raw else ''
            cmd = ('pandoc --normalize --reference-links {0} --from=html'
                   ' --to={1} -o "{2}" "{3}"').format(
                    parse_raw, out_markup, out_filename, html_filename)

            try:
                rc = subprocess.call(cmd, shell=True)
                if rc < 0:
                    error = "Child was terminated by signal %d" % -rc
                    exit(error)

                elif rc > 0:
                    error = "Please, check your Pandoc installation."
                    exit(error)
            except OSError, e:
                error = "Pandoc execution failed: %s" % e
                exit(error)

            os.remove(html_filename)

            with open(out_filename, 'r', encoding='utf-8') as fs:
                content = fs.read()
                if out_markup == "markdown":
                    # In markdown, to insert a <br />, end a line with two or more spaces & then a end-of-line
                    content = content.replace("\\\n ", "  \n")
                    content = content.replace("\\\n", "  \n")

        with open(out_filename, 'w', encoding='utf-8') as fs:
            fs.write(header + content)


def main():
    parser = argparse.ArgumentParser(
        description="Transform feed, Wordpress or Dotclear files to rst files."
            "Be sure to have pandoc installed",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(dest='input', help='The input file to read')
    parser.add_argument('--wpfile', action='store_true', dest='wpfile',
        help='Wordpress XML export')
    parser.add_argument('--dotclear', action='store_true', dest='dotclear',
        help='Dotclear export')
    parser.add_argument('--feed', action='store_true', dest='feed',
        help='Feed to parse')
    parser.add_argument('-o', '--output', dest='output', default='output',
        help='Output path')
    parser.add_argument('-m', '--markup', dest='markup', default='rst',
        help='Output markup format (supports rst & markdown)')
    parser.add_argument('--dir-cat', action='store_true', dest='dircat',
        help='Put files in directories with categories name')
    parser.add_argument('--strip-raw', action='store_true', dest='strip_raw',
        help="Strip raw HTML code that can't be converted to "
             "markup such as flash embeds or iframes (wordpress import only)")

    args = parser.parse_args()

    input_type = None
    if args.wpfile:
        input_type = 'wordpress'
    elif args.dotclear:
        input_type = 'dotclear'
    elif args.feed:
        input_type = 'feed'
    else:
        error = "You must provide either --wpfile, --dotclear or --feed options"
        exit(error)

    if not os.path.exists(args.output):
        try:
            os.mkdir(args.output)
        except OSError:
            error = "Unable to create the output folder: " + args.output
            exit(error)

    if input_type == 'wordpress':
        fields = wp2fields(args.input)
    elif input_type == 'dotclear':
        fields = dc2fields(args.input)
    elif input_type == 'feed':
        fields = feed2fields(args.input)

    fields2pelican(fields, args.markup, args.output,
                   dircat=args.dircat or False,
                   strip_raw=args.strip_raw or False)
