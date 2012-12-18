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
- Posterous API
- RSS/Atom feed

The conversion from HTML to reStructuredText relies on `pandoc
<http://johnmacfarlane.net/pandoc/>`_. For Dotclear, if the source posts are
written with Markdown syntax, they will not be converted (as Pelican also
supports Markdown).

Dependencies
""""""""""""

``pelican-import`` has two dependencies not required by the rest of pelican:

- BeautifulSoup
- pandoc

BeatifulSoup can be installed like any other Python package::

    $ pip install BeautifulSoup

For pandoc, install a package for your operating system from the
`pandoc site <http://johnmacfarlane.net/pandoc/installing.html>`_.


Usage
"""""

| pelican-import [-h] [--wpfile] [--dotclear] [--posterous] [--feed] [-o OUTPUT]
|                [-m MARKUP][--dir-cat] [-e EMAIL] [-p PASSWORD]
|                input

Optional arguments
""""""""""""""""""

  -h, --help            show this help message and exit
  --wpfile              Wordpress XML export
  --dotclear            Dotclear export
  --posterous           Posterous API
  --feed                Feed to parse
  -o OUTPUT, --output OUTPUT
                        Output path
  -m MARKUP             Output markup
  --dir-cat             Put files in directories with categories name
  -e EMAIL              Email used to authenticate Posterous API
  -p PASSWORD           Password used to authenticate Posterous API

Examples
========

for WordPress::

    $ pelican-import --wpfile -o ~/output ~/posts.xml

for Dotclear::

    $ pelican-import --dotclear -o ~/output ~/backup.txt

for Posterous::

    $ pelican-import --posterous -o ~/output <api_token> --email=<email_address> --password=<password>

api_token can be obtained from http://posterous.com/api/

Tests
=====

To test the module, one can use sample files:

- for Wordpress: http://wpcandy.com/made/the-sample-post-collection
- for Dotclear: http://themes.dotaddict.org/files/public/downloads/lorem-backup.txt
