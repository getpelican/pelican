.. _import:

=================================
 Import from other blog software
=================================

Description
===========

``pelican-import`` is a command line tool for converting articles from other
software to ReStructuredText. The supported formats are:

- WordPress XML export
- Dotclear export
- RSS/Atom feed

The conversion from HTML to reStructuredText relies on `pandoc
<http://johnmacfarlane.net/pandoc/>`_. For Dotclear, if the source posts are
written with Markdown syntax, they will not be converted (as Pelican also
supports Markdown).

Usage
"""""

| pelican-import [-h] [--wpfile] [--dotclear] [--feed] [-o OUTPUT]
|                [--dir-cat]
|                input

Optional arguments:
"""""""""""""""""""

  -h, --help            show this help message and exit
  --wpfile              Wordpress XML export
  --dotclear            Dotclear export
  --feed                Feed to parse
  -o OUTPUT, --output OUTPUT
                        Output path
  --dir-cat             Put files in directories with categories name

Examples
========

for WordPress::

    $ pelican-import --wpfile -o ~/output ~/posts.xml

for Dotclear::

    $ pelican-import --dotclear -o ~/output ~/backup.txt

Tests
=====

To test the module, one can use sample files:

- for Wordpress: http://wpcandy.com/made/the-sample-post-collection
- for Dotclear: http://themes.dotaddict.org/files/public/downloads/lorem-backup.txt
