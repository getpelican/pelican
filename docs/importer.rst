=================================
 Import from other blog software
=================================

Description
===========

``importer.py`` is a command line tool for converting articles from other
software to ReStructuredText. The supported formats are:

- Wordpress XML export
- Dotclear export
- RSS/ATOM feed

The conversion from HTML to ReStructuredText relies on `pandoc
<http://johnmacfarlane.net/pandoc/>`_. For Dotclear, if the source posts are
written with Markdown syntax, they will not be converted (as Pelican also
supports Markdown).

Usage
"""""

| importer.py [-h] [--wpfile] [--dotclear] [--feed] [-o OUTPUT]
|                    [--dir-cat]
|                    input

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

for Wordpress::

    $ python2 tools/importer.py --wpfile -o ~/output ~/posts.xml

for Dotclear::

    $ python2 tools/importer.py --dotclear -o ~/output ~/backup.txt


Tests
=====

To test the module, one can use sample files:

- for Wordpress: http://wpcandy.com/made/the-sample-post-collection
- for Dotclear: http://themes.dotaddict.org/files/public/downloads/lorem-backup.txt
