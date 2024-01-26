.. _import:

Importing an existing site
##########################

Description
===========

``pelican-import`` is a command-line tool for converting articles from other
software to reStructuredText or Markdown. The supported import formats are:

- Blogger XML export
- Dotclear export
- Medium export
- Tumblr API
- WordPress XML export
- RSS/Atom feed

The conversion from HTML to reStructuredText or Markdown relies on `Pandoc`_.
For Dotclear, if the source posts are written with Markdown syntax, they will
not be converted (as Pelican also supports Markdown).

.. note::

   Unlike Pelican, Wordpress supports multiple categories per article. These
   are imported as a comma-separated string. You have to resolve these
   manually, or use a plugin such as `More Categories`_ that enables multiple
   categories per article.

.. note::

   Imported pages may contain links to images that still point to the original site.
   So you might want to download those images into your local content and manually
   re-link them from the relevant pages of your site.

Dependencies
============

``pelican-import`` has some dependencies not required by the rest of Pelican:

- *BeautifulSoup4* and *lxml*, for WordPress and Dotclear import. Can be
  installed like any other Python package (``pip install BeautifulSoup4
  lxml``).
- *Feedparser*, for feed import (``pip install feedparser``).
- *Pandoc*, see the `Pandoc site`_ for installation instructions on your
  operating system.

.. _Pandoc: https://pandoc.org/
.. _Pandoc site: https://pandoc.org/installing.html


Usage
=====

::

    pelican-import [-h] [--blogger] [--dotclear] [--tumblr] [--wpfile] [--feed]
                   [-o OUTPUT] [-m MARKUP] [--dir-cat] [--dir-page] [--strip-raw] [--wp-custpost]
                   [--wp-attach] [--disable-slugs] [-b BLOGNAME]
                   input|api_key

Positional arguments
--------------------
  =============         ============================================================================
  ``input``             The input file to read
  ``api_key``           (Tumblr only) api_key can be obtained from https://www.tumblr.com/oauth/apps
  =============         ============================================================================

Optional arguments
------------------

  -h, --help            Show this help message and exit
  --blogger             Blogger XML export (default: False)
  --dotclear            Dotclear export (default: False)
  --medium              Medium export (default: False)
  --tumblr              Tumblr API (default: False)
  --wpfile              WordPress XML export (default: False)
  --feed                Feed to parse (default: False)
  -o OUTPUT, --output OUTPUT
                        Output path (default: content)
  -m MARKUP, --markup MARKUP
                        Output markup format: ``rst``, ``markdown``, or ``asciidoc``
                        (default: ``rst``)
  --dir-cat             Put files in directories with categories name
                        (default: False)
  --dir-page            Put files recognised as pages in "pages/" sub-
                          directory (blogger and wordpress import only)
                          (default: False)
  --filter-author       Import only post from the specified author
  --strip-raw           Strip raw HTML code that can't be converted to markup
                        such as flash embeds or iframes (default: False)
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
  -b BLOGNAME, --blogname=BLOGNAME
                        Blog name used in Tumblr API


Examples
========

For Blogger::

    $ pelican-import --blogger -o ~/output ~/posts.xml

For Dotclear::

    $ pelican-import --dotclear -o ~/output ~/backup.txt

For Medium::

    $ pelican-import --medium -o ~/output ~/medium-export/posts/

The Medium export is a zip file.  Unzip it, and point this tool to the
"posts" subdirectory.  For more information on how to export, see
https://help.medium.com/hc/en-us/articles/115004745787-Export-your-account-data.

For Tumblr::

    $ pelican-import --tumblr -o ~/output --blogname=<blogname> <api_key>

For WordPress::

    $ pelican-import --wpfile -o ~/output ~/posts.xml

For Medium (an example of using an RSS feed):

    $ python -m pip install feedparser
    $ pelican-import --feed https://medium.com/feed/@username

.. note::

   The RSS feed may only return the most recent posts — not all of them.

Tests
=====

To test the module, one can use sample files:

- for WordPress: https://www.wpbeginner.com/wp-themes/how-to-add-dummy-content-for-theme-development-in-wordpress/
- for Dotclear: http://media.dotaddict.org/tda/downloads/lorem-backup.txt

.. _More Categories: https://github.com/pelican-plugins/more-categories
