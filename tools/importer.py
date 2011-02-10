#! /usr/bin/env python

from pelican.utils import slugify

from codecs import open
import os
import argparse
import time


def wp2fields(xml):
    """Opens a wordpress XML file, and yield pelican fields"""
    from BeautifulSoup import BeautifulStoneSoup

    xmlfile = open(xml, encoding='utf-8').read()
    soup = BeautifulStoneSoup(xmlfile)
    items = soup.rss.channel.findAll('item')

    for item in items:
        if item.fetch('wp:status')[0].contents[0] == "publish":
            title = item.title.contents[0]
            content = item.fetch('content:encoded')[0].contents[0]
            filename = item.fetch('wp:post_name')[0].contents[0]
            
            raw_date = item.fetch('wp:post_date')[0].contents[0]
            date_object = time.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            date = time.strftime("%Y-%m-%d %H:%M", date_object)
            
            author = item.fetch('dc:creator')[0].contents[0].title()
            categories = [(cat['nicename'],cat.contents[0]) for cat in item.fetch(domain='category')]
            
            tags = [tag.contents[0].title() for tag in item.fetch(domain='tag', nicename=None)]
            
            yield (title, content, filename, date, author, categories, tags)

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
        yield (entry.title, entry.description, slug, date, author, [], tags)


def build_header(title, date, author, categories, tags):
    """Build a header from a list of fields"""
    header = '%s\n%s\n' % (title, '#' * len(title))
    if date:
        header += ':date: %s\n' % date
    if categories:
        header += ':category: %s\n' % ', '.join(categories)
    if tags:
        header += ':tags: %s\n' % ', '.join(tags)
    header += '\n'
    return header


def fields2pelican(fields, output_path):
    for title, content, filename, date, author, categories, tags in fields: 
        html_filename = os.path.join(output_path, filename+'.html')
        
        if(len(categories) == 1):
            rst_filename = os.path.join(output_path, categories[0][0], filename+'.rst')
            if not os.path.isdir(os.path.join(output_path, categories[0][0])):
                os.mkdir(os.path.join(output_path, categories[0][0]))
        else:
            rst_filename = os.path.join(output_path, filename+'.rst')

        with open(html_filename, 'w', encoding='utf-8') as fp:
            fp.write(content)
            
        os.system('pandoc --from=html --to=rst -o %s %s' % (rst_filename,
            html_filename))
        
        os.remove(html_filename)
            
        with open(rst_filename, 'r', encoding='utf-8') as fs:
            content = fs.read()
        with open(rst_filename, 'w', encoding='utf-8') as fs:
            categories = [x[1] for x in categories]
            header = build_header(title, date, author, categories, tags)
            fs.write(header + content)


def main(input_type, input, output_path):
    if input_type == 'wordpress':
        fields = wp2fields(input)
    elif input_type == 'feed':
        fields = feed2fields(input)

    fields2pelican(fields, output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Transform even feed or XML files to rst files."
                    "Be sure to have pandoc installed")

    parser.add_argument(dest='input', help='The input file to read')
    parser.add_argument('--wpfile', action='store_true', dest='wpfile', 
            help='Wordpress XML export')
    parser.add_argument('--feed', action='store_true', dest='feed', 
            help='feed to parse')
    parser.add_argument('-o', '--output', dest='output', default='output', 
            help='Output path')
    args = parser.parse_args() 
    
    input_type = None
    if args.wpfile:
        input_type = 'wordpress'
    elif args.feed:
        input_type = 'feed'
    else:
        print "you must provide either --wpfile or --feed options"
        exit()
    main(input_type, args.input, args.output)
