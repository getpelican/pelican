#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import sys
import datetime

from pelican.utils import slugify
from pelican.tools.pelican_import import build_markdown_header, build_header


def create_template(args):

    if not os.path.exists(args.path):
        try:
            os.mkdir(args.path)
        except OSError:
            error = 'Unable to create the output folder: ' + args.path
            exit(error)

    title =  args.title.decode('utf-8')
    slug = slugify(title)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    categories = args.categories.split('\W+') if args.categories else None
    tags = args.tags.split('\W+') if args.tags else None

    if (args.markup == 'markdown') or (args.markup == 'md') :
        ext = '.md'
        header = build_markdown_header(title, date, args.author, categories, tags, slug)
    else:
        ext = '.rst'
        header = build_header(title, date, args.author, categories, tags, slug)

    filename = os.path.join(args.path, slug+ext) 
    header = header.encode('utf-8')

    with open(filename, 'w') as fs:
        fs.write(header)

    print 'Article template create in "%s"' % filename


def main():

    argv = sys.argv[1:]
    argv.append('-h') if len(argv) == 0 else None

    parser = argparse.ArgumentParser(description='Create article with templation')

    parser.add_argument('title', help='article title')
    parser.add_argument('-a', '--author', dest='author', default='[name]', help='Article author')
    parser.add_argument('-t', '--tags', dest='tags', default=None, help='Article tags(separated by comma)')
    parser.add_argument('-c', '--categories', dest='categories', default=None, help='Article categories')
    parser.add_argument('-s', '--slug', dest='slug', default=None, help='Article slug')
    parser.add_argument('-p', '--path', dest='path', default='content/posts', help='Article save directory')
    parser.add_argument('-m', '--markup', dest='markup', default='md', help='Article markup format (supports rst & markdown)')
    args = parser.parse_args(argv)

    create_template(args);


