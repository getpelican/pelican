#!/usr/bin/env python

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import argparse
try:
    # py3k import
    from html.parser import HTMLParser
except ImportError:
    # py2 import
    from HTMLParser import HTMLParser  # NOQA
import os
import re
import subprocess
import sys
import time
import logging

from codecs import open

from pelican.utils import slugify
from pelican.log import init

logger = logging.getLogger(__name__)


def decode_wp_content(content, br=True):
    pre_tags = {}
    if content.strip() == "":
        return ""

    content += "\n"
    if "<pre" in content:
        pre_parts = content.split("</pre>")
        last_pre = pre_parts.pop()
        content = ""
        pre_index = 0

        for pre_part in pre_parts:
            start = pre_part.index("<pre")
            if start == -1:
                content = content + pre_part
                continue
            name = "<pre wp-pre-tag-{0}></pre>".format(pre_index)
            pre_tags[name] = pre_part[start:] + "</pre>"
            content = content + pre_part[0:start] + name
            pre_index += 1
        content = content + last_pre

    content = re.sub(r'<br />\s*<br />', "\n\n", content)
    allblocks = ('(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|'
                 'td|th|div|dl|dd|dt|ul|ol|li|pre|select|option|form|'
                 'map|area|blockquote|address|math|style|p|h[1-6]|hr|'
                 'fieldset|noscript|samp|legend|section|article|aside|'
                 'hgroup|header|footer|nav|figure|figcaption|details|'
                 'menu|summary)')
    content = re.sub(r'(<' + allblocks + r'[^>]*>)', "\n\\1", content)
    content = re.sub(r'(</' + allblocks + r'>)', "\\1\n\n", content)
    #    content = content.replace("\r\n", "\n")
    if "<object" in content:
        # no <p> inside object/embed
        content = re.sub(r'\s*<param([^>]*)>\s*', "<param\\1>", content)
        content = re.sub(r'\s*</embed>\s*', '</embed>', content)
        #    content = re.sub(r'/\n\n+/', '\n\n', content)
    pgraphs = filter(lambda s: s != "", re.split(r'\n\s*\n', content))
    content = ""
    for p in pgraphs:
        content = content + "<p>" + p.strip() + "</p>\n"
    # under certain strange conditions it could create a P of entirely whitespace
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<p>([^<]+)</(div|address|form)>', "<p>\\1</p></\\2>", content)
    # don't wrap tags
    content = re.sub(r'<p>\s*(</?' + allblocks + r'[^>]*>)\s*</p>', "\\1", content)
    #problem with nested lists
    content = re.sub(r'<p>(<li.*)</p>', "\\1", content)
    content = re.sub(r'<p><blockquote([^>]*)>', "<blockquote\\1><p>", content)
    content = content.replace('</blockquote></p>', '</p></blockquote>')
    content = re.sub(r'<p>\s*(</?' + allblocks + '[^>]*>)', "\\1", content)
    content = re.sub(r'(</?' + allblocks + '[^>]*>)\s*</p>', "\\1", content)
    if br:
        def _preserve_newline(match):
            return match.group(0).replace("\n", "<WPPreserveNewline />")
        content = re.sub(r'/<(script|style).*?<\/\\1>/s', _preserve_newline, content)
        # optionally make line breaks
        content = re.sub(r'(?<!<br />)\s*\n', "<br />\n", content)
        content = content.replace("<WPPreserveNewline />", "\n")
    content = re.sub(r'(</?' + allblocks + r'[^>]*>)\s*<br />', "\\1", content)
    content = re.sub(r'<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)', '\\1', content)
    content = re.sub(r'\n</p>', "</p>", content)

    if pre_tags:
        def _multi_replace(dic, string):
            pattern = r'|'.join(map(re.escape, dic.keys()))
            return re.sub(pattern, lambda m: dic[m.group()], string)
        content = _multi_replace(pre_tags, content)

    return content


def wp2fields(xml):
    """Opens a wordpress XML file, and yield pelican fields"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        error = ('Missing dependency '
                 '"BeautifulSoup4" and "lxml" required to import Wordpress XML files.')
        sys.exit(error)


    with open(xml, encoding='utf-8') as infile:
        xmlfile = infile.read()
    soup = BeautifulSoup(xmlfile, "xml")
    items = soup.rss.channel.findAll('item')

    for item in items:

        if item.find('status').string == "publish":

            try:
                # Use HTMLParser due to issues with BeautifulSoup 3
                title = HTMLParser().unescape(item.title.contents[0])
            except IndexError:
                title = 'No title [%s]' % item.find('post_name').string
                logger.warn('Post "%s" is lacking a proper title' % title)

            content = item.find('encoded').string
            filename = item.find('post_name').string

            raw_date = item.find('post_date').string
            date_object = time.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            date = time.strftime("%Y-%m-%d %H:%M", date_object)
            author = item.find('creator').string
 
            categories = [cat.string for cat in item.findAll('category', {'domain' : 'category'})]
            # caturl = [cat['nicename'] for cat in item.find(domain='category')]

            tags = [tag.string for tag in item.findAll('category', {'domain' : 'post_tag'})]

            yield (title, content, filename, date, author, categories, tags, "wp-html")

def dc2fields(file):
    """Opens a Dotclear export file, and yield pelican fields"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        error = ('Missing dependency '
                 '"BeautifulSoup4" and "lxml" required to import Dotclear files.')
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
                tags.append(
                    BeautifulSoup(
                        newtag
                        , "xml"
                    )
                    # bs4 always outputs UTF-8
                    .decode('utf-8')
                )
            else:
                i=1
                j=1
                while(i <= int(tag[:1])):
                    newtag = tag.split('"')[j].replace('\\','')
                    tags.append(
                        BeautifulSoup(
                            newtag
                            , "xml"
                        )
                        # bs4 always outputs UTF-8
                        .decode('utf-8')
                    )
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


def posterous2fields(api_token, email, password):
    """Imports posterous posts"""
    import base64
    from datetime import datetime, timedelta
    try:
        # py3k import
        import json
    except ImportError:
        # py2 import
        import simplejson as json

    try:
        # py3k import
        import urllib.request as urllib_request
    except ImportError:
        # py2 import
        import urllib2 as urllib_request


    def get_posterous_posts(api_token, email, password, page = 1):
        base64string = base64.encodestring(("%s:%s" % (email, password)).encode('utf-8')).replace(b'\n', b'')
        url = "http://posterous.com/api/v2/users/me/sites/primary/posts?api_token=%s&page=%d" % (api_token, page)
        request = urllib_request.Request(url)
        request.add_header("Authorization", "Basic %s" % base64string.decode())
        handle = urllib_request.urlopen(request)
        posts = json.loads(handle.read().decode('utf-8'))
        return posts

    page = 1
    posts = get_posterous_posts(api_token, email, password, page)
    while len(posts) > 0:
        posts = get_posterous_posts(api_token, email, password, page)
        page += 1

        for post in posts:
            slug = post.get('slug')
            if not slug:
                slug = slugify(post.get('title'))
            tags = [tag.get('name') for tag in post.get('tags')]
            raw_date = post.get('display_date')
            date_object = datetime.strptime(raw_date[:-6], "%Y/%m/%d %H:%M:%S")
            offset = int(raw_date[-5:])
            delta = timedelta(hours = offset / 100)
            date_object -= delta
            date = date_object.strftime("%Y-%m-%d %H:%M")

            yield (post.get('title'), post.get('body_cleaned'), slug, date,
                post.get('user').get('display_name'), [], tags, "html")

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


def build_header(title, date, author, categories, tags, slug):
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
    if slug:
        header += ':slug: %s\n' % slug
    header += '\n'
    return header

def build_markdown_header(title, date, author, categories, tags, slug):
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
    if slug:
        header += 'Slug: %s\n' % slug
    header += '\n'
    return header

def fields2pelican(fields, out_markup, output_path, dircat=False, strip_raw=False, disable_slugs=False):
    for title, content, filename, date, author, categories, tags, in_markup in fields:
        slug = not disable_slugs and filename or None
        if (in_markup == "markdown") or (out_markup == "markdown") :
            ext = '.md'
            header = build_markdown_header(title, date, author, categories, tags, slug)
        else:
            out_markup = "rst"
            ext = '.rst'
            header = build_header(title, date, author, categories, tags, slug)

        filename = os.path.basename(filename)

        # Enforce filename restrictions for various filesystems at once; see
        # http://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
        # we do not need to filter words because an extension will be appended
        filename = re.sub(r'[<>:"/\\|?*^% ]', '-', filename) # invalid chars
        filename = filename.lstrip('.') # should not start with a dot
        if not filename:
            filename = '_'
        filename = filename[:249] # allow for 5 extra characters

        # option to put files in directories with categories names
        if dircat and (len(categories) > 0):
            catname = slugify(categories[0])
            out_filename = os.path.join(output_path, catname, filename+ext)
            if not os.path.isdir(os.path.join(output_path, catname)):
                os.mkdir(os.path.join(output_path, catname))
        else:
            out_filename = os.path.join(output_path, filename+ext)

        print(out_filename)

        if in_markup in ("html", "wp-html"):
            html_filename = os.path.join(output_path, filename+'.html')

            with open(html_filename, 'w', encoding='utf-8') as fp:
                # Replace newlines with paragraphs wrapped with <p> so
                # HTML is valid before conversion
                if in_markup == "wp-html":
                    new_content = decode_wp_content(content)
                else:
                    paragraphs = content.splitlines()
                    paragraphs = ['<p>{0}</p>'.format(p) for p in paragraphs]
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
            except OSError as e:
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
        description="Transform feed, Wordpress or Dotclear files to reST (rst) "
                    "or Markdown (md) files. Be sure to have pandoc installed.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(dest='input', help='The input file to read')
    parser.add_argument('--wpfile', action='store_true', dest='wpfile',
        help='Wordpress XML export')
    parser.add_argument('--dotclear', action='store_true', dest='dotclear',
        help='Dotclear export')
    parser.add_argument('--posterous', action='store_true', dest='posterous',
        help='Posterous export')
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
    parser.add_argument('--disable-slugs', action='store_true',
        dest='disable_slugs',
        help='Disable storing slugs from imported posts within output. '
             'With this disabled, your Pelican URLs may not be consistent '
             'with your original posts.')
    parser.add_argument('-e', '--email', dest='email',
        help="Email address (posterous import only)")
    parser.add_argument('-p', '--password', dest='password',
        help="Password (posterous import only)")

    args = parser.parse_args()

    input_type = None
    if args.wpfile:
        input_type = 'wordpress'
    elif args.dotclear:
        input_type = 'dotclear'
    elif args.posterous:
        input_type = 'posterous'
    elif args.feed:
        input_type = 'feed'
    else:
        error = "You must provide either --wpfile, --dotclear, --posterous or --feed options"
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
    elif input_type == 'posterous':
        fields = posterous2fields(args.input, args.email, args.password)
    elif input_type == 'feed':
        fields = feed2fields(args.input)

    init() # init logging

    fields2pelican(fields, args.markup, args.output,
                   dircat=args.dircat or False,
                   strip_raw=args.strip_raw or False,
                   disable_slugs=args.disable_slugs or False)
