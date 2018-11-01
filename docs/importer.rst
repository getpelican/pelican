.. _import:

Importing an existing site
##########################

Description
===========

``pelican-import`` is a command-line tool for converting articles from other
software to reStructuredText or Markdown. The supported import formats are:

- Blogger XML export
- Dotclear export
- Posterous API
- Tumblr API
- WordPress XML export
- RSS/Atom feed

The conversion from HTML to reStructuredText or Markdown relies on `Pandoc`_.
For Dotclear, if the source posts are written with Markdown syntax, they will
not be converted (as Pelican also supports Markdown).


Dependencies
============

``pelican-import`` has some dependencies not required by the rest of Pelican:

- *BeautifulSoup4* and *lxml*, for WordPress and Dotclear import. Can be installed like
  any other Python package (``pip install BeautifulSoup4 lxml``).
- *Feedparser*, for feed import (``pip install feedparser``).
- *Pandoc*, see the `Pandoc site`_ for installation instructions on your
  operating system.

.. _Pandoc: http://johnmacfarlane.net/pandoc/
.. _Pandoc site: http://johnmacfarlane.net/pandoc/installing.html


Usage
=====

::

    pelican-import [-h] [--blogger] [--dotclear] [--posterous] [--tumblr] [--wpfile] [--feed]
                   [-o OUTPUT] [-m MARKUP] [--dir-cat] [--dir-page] [--strip-raw] [--wp-custpost]
                   [--wp-attach] [--disable-slugs] [-e EMAIL] [-p PASSWORD] [-b BLOGNAME]
                   input|api_token|api_key

Positional arguments
--------------------
  =============         ============================================================================
  ``input``             The input file to read
  ``api_token``         (Posterous only) api_token can be obtained from http://posterous.com/api/
  ``api_key``           (Tumblr only) api_key can be obtained from http://www.tumblr.com/oauth/apps
  =============         ============================================================================

Optional arguments
------------------

  -h, --help            Show this help message and exit
  --blogger             Blogger XML export (default: False)
  --dotclear            Dotclear export (default: False)
  --posterous           Posterous API (default: False)
  --tumblr              Tumblr API (default: False)
  --wpfile              WordPress XML export (default: False)
  --feed                Feed to parse (default: False)
  -o OUTPUT, --output OUTPUT
                        Output path (default: content)
  -m MARKUP, --markup MARKUP
                        Output markup format (supports rst & markdown)
                        (default: rst)
  --dir-cat             Put files in directories with categories name
                        (default: False)
  --dir-page            Put files recognised as pages in "pages/" sub-
                          directory (blogger and wordpress import only)
                          (default: False)
  --filter-author       Import only post from the specified author
  --strip-raw           Strip raw HTML code that can't be converted to markup
                        such as flash embeds or iframes (wordpress import
                        only) (default: False)
  --wp-custpost         Put wordpress custom post types in directories. If
                        used with --dir-cat option directories will be created
                        as "/post_type/category/" (wordpress import only)
  --wp-attach           Download files uploaded to wordpress as attachments.
                        Files will be added to posts as a list in the post
                        header and links to the files within the post will be
                        updated. All files will be downloaded, even if they
                        aren't associated with a post. Files will be downloaded
                        with their original path inside the output directory,
                        e.g. "output/wp-uploads/date/postname/file.jpg".
                        (wordpress import only) (requires an internet
                        connection)
  --disable-slugs       Disable storing slugs from imported posts within
                        output. With this disabled, your Pelican URLs may not
                        be consistent with your original posts. (default:
                        False)
  -e EMAIL, --email=EMAIL
                        Email used to authenticate Posterous API
  -p PASSWORD, --password=PASSWORD
                        Password used to authenticate Posterous API
  -b BLOGNAME, --blogname=BLOGNAME
                        Blog name used in Tumblr API


Examples
========

For Blogger::

    $ pelican-import --blogger -o ~/output ~/posts.xml

For Dotclear::

    $ pelican-import --dotclear -o ~/output ~/backup.txt

for Posterous::

    $ pelican-import --posterous -o ~/output --email=<email_address> --password=<password> <api_token>

For Tumblr::

    $ pelican-import --tumblr -o ~/output --blogname=<blogname> <api_token>

For WordPress::

    $ pelican-import --wpfile -o ~/output ~/posts.xml

Tests
=====

To test the module, one can use sample files:

- for WordPress: http://www.wpbeginner.com/wp-themes/how-to-add-dummy-content-for-theme-development-in-wordpress/
- for Dotclear: http://media.dotaddict.org/tda/downloads/lorem-backup.txt
