Writing content
###############

Articles and pages
==================

Pelican considers "articles" to be chronological content, such as posts on a
blog, and thus associated with a date.

The idea behind "pages" is that they are usually not temporal in nature and are
used for content that does not change very often (e.g., "About" or "Contact"
pages).

You can find sample content in the repository at: ``pelican/samples/content/``

.. _internal_metadata:

File metadata
=============

Pelican tries to be smart enough to get the information it needs from the
file system (for instance, about the category of your articles), but some
information you need to provide in the form of metadata inside your files.

If you are writing your content in reStructuredText format, you can provide
this metadata in text files via the following syntax (give your file the
``.rst`` extension)::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :modified: 2010-10-04 18:40
    :tags: thats, awesome
    :category: yeah
    :slug: my-super-post
    :authors: Alexis Metaireau, Conan Doyle
    :summary: Short version for index and feeds

Author and tag lists may be semicolon-separated instead, which allows
you to write authors and tags containing commas::

    :tags: pelican, publishing tool; pelican, bird
    :authors: Metaireau, Alexis; Doyle, Conan

Pelican implements an extension to reStructuredText to enable support for the
``abbr`` HTML tag. To use it, write something like this in your post::

    This will be turned into :abbr:`HTML (HyperText Markup Language)`.

You can also use Markdown syntax (with a file ending in ``.md``,
``.markdown``, ``.mkd``, or ``.mdown``). Markdown generation requires that you
first explicitly install the ``Markdown`` package, which can be done via ``pip
install Markdown``.

Pelican also supports `Markdown Extensions`_, which might have to be installed
separately if they are not included in the default ``Markdown`` package and can
be configured and loaded via the ``MARKDOWN`` setting.

Metadata syntax for Markdown posts should follow this pattern::

    Title: My super title
    Date: 2010-12-03 10:20
    Modified: 2010-12-05 19:30
    Category: Python
    Tags: pelican, publishing
    Slug: my-super-post
    Authors: Alexis Metaireau, Conan Doyle
    Summary: Short version for index and feeds

    This is the content of my super blog post.

Readers for additional formats (such as AsciiDoc_) are available via plugins.
Refer to `pelican-plugins`_ repository for those.

Pelican can also process HTML files ending in ``.html`` and ``.htm``. Pelican
interprets the HTML in a very straightforward manner, reading metadata from
``meta`` tags, the title from the ``title`` tag, and the body out from the
``body`` tag::

    <html>
        <head>
            <title>My super title</title>
            <meta name="tags" content="thats, awesome" />
            <meta name="date" content="2012-07-09 22:28" />
            <meta name="modified" content="2012-07-10 20:14" />
            <meta name="category" content="yeah" />
            <meta name="authors" content="Alexis Métaireau, Conan Doyle" />
            <meta name="summary" content="Short version for index and feeds" />
        </head>
        <body>
            This is the content of my super blog post.
        </body>
    </html>

With HTML, there is one simple exception to the standard metadata: ``tags`` can
be specified either via the ``tags`` metadata, as is standard in Pelican, or
via the ``keywords`` metadata, as is standard in HTML. The two can be used
interchangeably.

Note that, aside from the title, none of this article metadata is mandatory:
if the date is not specified and ``DEFAULT_DATE`` is set to ``'fs'``, Pelican
will rely on the file's "mtime" timestamp, and the category can be determined
by the directory in which the file resides. For example, a file located at
``python/foobar/myfoobar.rst`` will have a category of ``foobar``. If you would
like to organize your files in other ways where the name of the subfolder would
not be a good category name, you can set the setting ``USE_FOLDER_AS_CATEGORY``
to ``False``.  When parsing dates given in the page metadata, Pelican supports
the W3C's `suggested subset ISO 8601`__.

.. note::

   When experimenting with different settings (especially the metadata
   ones) caching may interfere and the changes may not be visible. In
   such cases disable caching with ``LOAD_CONTENT_CACHE = False`` or
   use the ``--ignore-cache`` command-line switch.

__ `W3C ISO 8601`_

``modified`` should be last time you updated the article, and defaults to ``date`` if not specified.
Besides you can show ``modified`` in the templates, feed entries in feed readers will be updated automatically
when you set ``modified`` to the current date after you modified your article.

``authors`` is a comma-separated list of article authors. If there's only one author you
can use ``author`` field.

If you do not explicitly specify summary metadata for a given post, the
``SUMMARY_MAX_LENGTH`` setting can be used to specify how many words from the
beginning of an article are used as the summary.

You can also extract any metadata from the filename through a regular
expression to be set in the ``FILENAME_METADATA`` setting. All named groups
that are matched will be set in the metadata object. The default value for the
``FILENAME_METADATA`` setting will only extract the date from the filename. For
example, if you would like to extract both the date and the slug, you could set
something like: ``'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'``

Please note that the metadata available inside your files takes precedence over
the metadata extracted from the filename.

Pages
=====

If you create a folder named ``pages`` inside the content folder, all the
files in it will be used to generate static pages, such as **About** or
**Contact** pages. (See example filesystem layout below.)

You can use the ``DISPLAY_PAGES_ON_MENU`` setting to control whether all those
pages are displayed in the primary navigation menu. (Default is ``True``.)

If you want to exclude any pages from being linked to or listed in the menu
then add a ``status: hidden`` attribute to its metadata. This is useful for
things like making error pages that fit the generated theme of your site.

.. _ref-linking-to-internal-content:

Linking to internal content
===========================

From Pelican 3.1 onwards, it is now possible to specify intra-site links to
files in the *source content* hierarchy instead of files in the *generated*
hierarchy. This makes it easier to link from the current post to other content
that may be sitting alongside that post (instead of having to determine where
the other content will be placed after site generation).

To link to internal content (files in the ``content`` directory), use the
following syntax for the link target: ``{filename}path/to/file``
Note: forward slashes, ``/``,
are the required path separator in the ``{filename}`` directive
on all operating systems, including Windows.

For example, a Pelican project might be structured like this::

    website/
    ├── content
    │   ├── category/
    │   │   └── article1.rst
    │   ├── article2.md
    │   └── pages
    │       └── about.md
    └── pelican.conf.py

In this example, ``article1.rst`` could look like this::

    The first article
    #################

    :date: 2012-12-01 10:02

    See below intra-site link examples in reStructuredText format.

    `a link relative to the current file <{filename}../article2.md>`_
    `a link relative to the content root <{filename}/article2.md>`_

and ``article2.md``::

    Title: The second article
    Date: 2012-12-01 10:02

    See below intra-site link examples in Markdown format.

    [a link relative to the current file]({filename}category/article1.rst)
    [a link relative to the content root]({filename}/category/article1.rst)

Linking to static files
-----------------------

Linking to non-article or non-page content uses the same ``{filename}`` syntax
as described above. It is important to remember that those files will not be
copied to the output directory unless the source directories containing them
are included in the ``STATIC_PATHS`` setting of the project's ``pelicanconf.py``
file. Pelican's default configuration includes the ``images`` directory for
this, but others must be added manually. Forgetting to do so will result in
broken links.

For example, a project's content directory might be structured like this::

    content
    ├── images
    │   └── han.jpg
    ├── pdfs
    │   └── menu.pdf
    └── pages
        └── test.md

``test.md`` would include::

    ![Alt Text]({filename}/images/han.jpg)
    [Our Menu]({filename}/pdfs/menu.pdf)

``pelicanconf.py`` would include::

    STATIC_PATHS = ['images', 'pdfs']

Site generation would then copy ``han.jpg`` to ``output/images/han.jpg``,
``menu.pdf`` to ``output/pdfs/menu.pdf``, and write the appropriate links
in ``test.md``.

Mixed content in the same directory
-----------------------------------

Starting with Pelican 3.5, static files can safely share a source directory with
page source files, without exposing the page sources in the generated site.
Any such directory must be added to both ``STATIC_PATHS`` and ``PAGE_PATHS``
(or ``STATIC_PATHS`` and ``ARTICLE_PATHS``). Pelican will identify and process
the page source files normally, and copy the remaining files as if they lived
in a separate directory reserved for static files.

Note: Placing static and content source files together in the same source
directory does not guarantee that they will end up in the same place in the
generated site. The easiest way to do this is by using the ``{attach}`` link
syntax (described below). Alternatively, the ``STATIC_SAVE_AS``,
``PAGE_SAVE_AS``, and ``ARTICLE_SAVE_AS`` settings (and the corresponding
``*_URL`` settings) can be configured to place files of different types
together, just as they could in earlier versions of Pelican.

Attaching static files
----------------------

Starting with Pelican 3.5, static files can be "attached" to a page or article
using this syntax for the link target: ``{attach}path/to/file`` This works
like the ``{filename}`` syntax, but also relocates the static file into the
linking document's output directory. If the static file originates from a
subdirectory beneath the linking document's source, that relationship will be
preserved on output. Otherwise, it will become a sibling of the linking
document.

This only works for linking to static files, and only when they originate from
a directory included in the ``STATIC_PATHS`` setting.

For example, a project's content directory might be structured like this::

    content
    ├── blog
    │   ├── icons
    │   │   └── icon.png
    │   ├── photo.jpg
    │   └── testpost.md
    └── downloads
        └── archive.zip

``pelicanconf.py`` would include::

    PATH = 'content'
    STATIC_PATHS = ['blog', 'downloads']
    ARTICLE_PATHS = ['blog']
    ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
    ARTICLE_URL = '{date:%Y}/{slug}.html'

``testpost.md`` would include::

    Title: Test Post
    Category: test
    Date: 2014-10-31

    ![Icon]({attach}icons/icon.png)
    ![Photo]({attach}photo.jpg)
    [Downloadable File]({attach}/downloads/archive.zip)

Site generation would then produce an output directory structured like this::

    output
    └── 2014
        ├── archive.zip
        ├── icons
        │   └── icon.png
        ├── photo.jpg
        └── test-post.html

Notice that all the files linked using ``{attach}`` ended up in or beneath
the article's output directory.

If a static file is linked multiple times, the relocating feature of
``{attach}`` will only work in the first of those links to be processed.
After the first link, Pelican will treat ``{attach}`` like ``{filename}``.
This avoids breaking the already-processed links.

**Be careful when linking to a file from multiple documents:**
Since the first link to a file finalizes its location and Pelican does
not define the order in which documents are processed, using ``{attach}`` on a
file linked by multiple documents can cause its location to change from one
site build to the next. (Whether this happens in practice will depend on the
operating system, file system, version of Pelican, and documents being added,
modified, or removed from the project.) Any external sites linking to the
file's old location might then find their links broken. **It is therefore
advisable to use {attach} only if you use it in all links to a file, and only
if the linking documents share a single directory.** Under these conditions,
the file's output location will not change in future builds. In cases where
these precautions are not possible, consider using ``{filename}`` links instead
of ``{attach}``, and letting the file's location be determined by the project's
``STATIC_SAVE_AS`` and ``STATIC_URL`` settings. (Per-file ``save_as`` and
``url`` overrides can still be set in ``EXTRA_PATH_METADATA``.)

Linking to authors, categories, index and tags
----------------------------------------------

You can link to authors, categories, index and tags using the ``{author}name``,
``{category}foobar``, ``{index}`` and ``{tag}tagname`` syntax.

Deprecated internal link syntax
-------------------------------

To remain compatible with earlier versions, Pelican still supports vertical bars
(``||``) in addition to curly braces (``{}``) for internal links. For example:
``|filename|an_article.rst``, ``|tag|tagname``, ``|category|foobar``.
The syntax was changed from ``||`` to ``{}`` to avoid collision with Markdown
extensions or reST directives. Support for the old syntax may eventually be
removed.


Importing an existing site
==========================

It is possible to import your site from WordPress, Tumblr, Dotclear, and RSS
feeds using a simple script. See :ref:`import`.

Translations
============

It is possible to translate articles. To do so, you need to add a ``lang`` meta
attribute to your articles/pages and set a ``DEFAULT_LANG`` setting (which is
English [en] by default). With those settings in place, only articles with the
default language will be listed, and each article will be accompanied by a list
of available translations for that article.

.. note::

   This core Pelican functionality does not create sub-sites
   (e.g. ``example.com/de``) with translated templates for each
   language. For such advanced functionality the `i18n_subsites
   plugin`_ can be used.

Pelican uses the article's URL "slug" to determine if two or more articles are
translations of one another. The slug can be set manually in the file's
metadata; if not set explicitly, Pelican will auto-generate the slug from the
title of the article.

Here is an example of two articles, one in English and the other in French.

The English article::

    Foobar is not dead
    ##################

    :slug: foobar-is-not-dead
    :lang: en

    That's true, foobar is still alive!

And the French version::

    Foobar n'est pas mort !
    #######################

    :slug: foobar-is-not-dead
    :lang: fr

    Oui oui, foobar est toujours vivant !

Post content quality notwithstanding, you can see that only item in common
between the two articles is the slug, which is functioning here as an
identifier. If you'd rather not explicitly define the slug this way, you must
then instead ensure that the translated article titles are identical, since the
slug will be auto-generated from the article title.

If you do not want the original version of one specific article to be detected
by the ``DEFAULT_LANG`` setting, use the ``translation`` metadata to specify
which posts are translations::

    Foobar is not dead
    ##################

    :slug: foobar-is-not-dead
    :lang: en
    :translation: true

    That's true, foobar is still alive!


.. _internal_pygments_options:

Syntax highlighting
===================

Pelican can provide colorized syntax highlighting for your code blocks.
To do so, you must use the following conventions inside your content files.

For reStructuredText, use the ``code-block`` directive to specify the type
of code to be highlighted (in these examples, we'll use ``python``)::

    .. code-block:: python

       print("Pelican is a static site generator.")

For Markdown, which utilizes the `CodeHilite extension`_ to provide syntax
highlighting, include the language identifier just above the code block,
indenting both the identifier and the code::

    There are two ways to specify the identifier:

        :::python
        print("The triple-colon syntax will *not* show line numbers.")

    To display line numbers, use a path-less shebang instead of colons:

        #!python
        print("The path-less shebang syntax *will* show line numbers.")

The specified identifier (e.g. ``python``, ``ruby``) should be one that
appears on the `list of available lexers <http://pygments.org/docs/lexers/>`_.

When using reStructuredText the following options are available in the
code-block directive:

=============   ============  =========================================
Option          Valid values  Description
=============   ============  =========================================
anchorlinenos   N/A           If present wrap line numbers in <a> tags.
classprefix     string        String to prepend to token class names
hl_lines        numbers       List of lines to be highlighted, where
                              line numbers to highlight are separated
                              by a space. This is similar to
                              ``emphasize-lines`` in Sphinx, but it
                              does not support a range of line numbers
                              separated by a hyphen, or comma-separated
                              line numbers.
lineanchors     string        Wrap each line in an anchor using this
                              string and -linenumber.
linenos         string        If present or set to "table" output line
                              numbers in a table, if set to
                              "inline" output them inline. "none" means
                              do not output the line numbers for this
                              table.
linenospecial   number        If set every nth line will be given the
                              'special' css class.
linenostart     number        Line number for the first line.
linenostep      number        Print every nth line number.
lineseparator   string        String to print between lines of code,
                              '\n' by default.
linespans       string        Wrap each line in a span using this and
                              -linenumber.
nobackground    N/A           If set do not output background color for
                              the wrapping element
nowrap          N/A           If set do not wrap the tokens at all.
tagsfile        string        ctags file to use for name definitions.
tagurlformat    string        format for the ctag links.
=============   ============  =========================================

Note that, depending on the version, your Pygments module might not have
all of these options available. Refer to the *HtmlFormatter* section of the
`Pygments documentation <http://pygments.org/docs/formatters/>`_ for more
details on each of the options.

For example, the following code block enables line numbers, starting at 153,
and prefixes the Pygments CSS classes with *pgcss* to make the names
more unique and avoid possible CSS conflicts::

    .. code-block:: identifier
        :classprefix: pgcss
        :linenos: table
        :linenostart: 153

       <indented code block goes here>

It is also possible to specify the ``PYGMENTS_RST_OPTIONS`` variable in your
Pelican settings file to include options that will be automatically applied to
every code block.

For example, if you want to have line numbers displayed for every code block
and a CSS prefix you would set this variable to::

    PYGMENTS_RST_OPTIONS = {'classprefix': 'pgcss', 'linenos': 'table'}

If specified, settings for individual code blocks will override the defaults in
your settings file.

Publishing drafts
=================

If you want to publish an article as a draft (for friends to review before
publishing, for example), you can add a ``Status: draft`` attribute to its
metadata. That article will then be output to the ``drafts`` folder and not
listed on the index page nor on any category or tag page.

If your articles should be automatically published as a draft (to not accidentally
publish an article before it is finished) include the status in the ``DEFAULT_METADATA``::

    DEFAULT_METADATA = {
        'status': 'draft',
    }

To publish a post when the default status is ``draft``, update the post's
metadata to include ``Status: published``.

.. _W3C ISO 8601: http://www.w3.org/TR/NOTE-datetime
.. _AsciiDoc: http://www.methods.co.nz/asciidoc/
.. _pelican-plugins: http://github.com/getpelican/pelican-plugins
.. _Markdown Extensions: http://pythonhosted.org/Markdown/extensions/
.. _CodeHilite extension: http://pythonhosted.org/Markdown/extensions/code_hilite.html#syntax
.. _i18n_subsites plugin: http://github.com/getpelican/pelican-plugins/tree/master/i18n_subsites
