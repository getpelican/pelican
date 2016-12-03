Settings
########

Pelican is configurable thanks to a settings file you can pass to
the command line::

    pelican content -s path/to/your/pelicanconf.py

If you used the ``pelican-quickstart`` command, your primary settings file will
be named ``pelicanconf.py`` by default.

.. note::

   When experimenting with different settings (especially the metadata
   ones) caching may interfere and the changes may not be visible. In
   such cases disable caching with ``LOAD_CONTENT_CACHE = False`` or
   use the ``--ignore-cache`` command-line switch.

Settings are configured in the form of a Python module (a file). There is an
`example settings file
<https://github.com/getpelican/pelican/raw/master/samples/pelican.conf.py>`_
available for reference.

All the setting identifiers must be set in all-caps, otherwise they will not be
processed. Setting values that are numbers (5, 20, etc.), booleans (True,
False, None, etc.), dictionaries, or tuples should *not* be enclosed in
quotation marks. All other values (i.e., strings) *must* be enclosed in
quotation marks.

Unless otherwise specified, settings that refer to paths can be either absolute
or relative to the configuration file.

The settings you define in the configuration file will be passed to the
templates, which allows you to use your settings to add site-wide content.

Here is a list of settings for Pelican:


Basic settings
==============

.. data:: USE_FOLDER_AS_CATEGORY = True

   When you don't specify a category in your post metadata, set this setting to
   ``True``, and organize your articles in subfolders, the subfolder will
   become the category of your post. If set to ``False``, ``DEFAULT_CATEGORY``
   will be used as a fallback.

.. data:: DEFAULT_CATEGORY = 'misc'

   The default category to fall back on.

.. data:: DISPLAY_PAGES_ON_MENU = True

   Whether to display pages on the menu of the template. Templates may or may
   not honor this setting.

.. data:: DISPLAY_CATEGORIES_ON_MENU = True

   Whether to display categories on the menu of the template. Templates may or
   not honor this setting.

.. data:: DOCUTILS_SETTINGS = {}

   Extra configuration settings for the docutils publisher (applicable only to
   reStructuredText). See `Docutils Configuration`_ settings for more details.

.. data:: DELETE_OUTPUT_DIRECTORY = False

   Delete the output directory, and **all** of its contents, before generating
   new files. This can be useful in preventing older, unnecessary files from
   persisting in your output. However, **this is a destructive setting and
   should be handled with extreme care.**

.. data:: OUTPUT_RETENTION = []

   A list of filenames that should be retained and not deleted from the output
   directory. One use case would be the preservation of version control data.

   Example::

      OUTPUT_RETENTION = [".hg", ".git", ".bzr"]

.. data:: JINJA_ENVIRONMENT = {'trim_blocks': True, 'lstrip_blocks': True}

   A dictionary of custom Jinja2 environment variables you want to use. This
   also includes a list of extensions you may want to include.
   See `Jinja Environment documentation`_.

.. data:: JINJA_FILTERS = {}

   A dictionary of custom Jinja2 filters you want to use.  The dictionary
   should map the filtername to the filter function.

   Example::

    JINJA_FILTERS = {'urlencode': urlencode_filter}

   See `Jinja custom filters documentation`_.

.. data:: LOG_FILTER = []

   A list of tuples containing the logging level (up to ``warning``) and the
   message to be ignored.

   Example::

      LOG_FILTER = [(logging.WARN, 'TAG_SAVE_AS is set to False')]

.. data:: READERS = {}

   A dictionary of file extensions / Reader classes for Pelican to process or
   ignore.

   For example, to avoid processing .html files, set::

      READERS = {'html': None}

   To add a custom reader for the ``foo`` extension, set::

      READERS = {'foo': FooReader}

.. data:: IGNORE_FILES = ['.#*']

   A list of glob patterns.  Files and directories matching any of these
   patterns will be ignored by the processor. For example, the default
   ``['.#*']`` will ignore emacs lock files, and ``['__pycache__']`` would
   ignore Python 3's bytecode caches.

.. data:: MARKDOWN = {...}

   Extra configuration settings for the Markdown processor. Refer to the Python
   Markdown documentation's `Options section
   <http://pythonhosted.org/Markdown/reference.html#markdown>`_ for a complete
   list of supported options. The ``extensions`` option will be automatically
   computed from the ``extension_configs`` option.

   Defaults to::

        MARKDOWN = {
            'extension_configs': {
                'markdown.extensions.codehilite': {'css_class': 'highlight'},
                'markdown.extensions.extra': {},
                'markdown.extensions.meta': {},
            },
            'output_format': 'html5',
        }

   .. Note::
      The dictionary defined in your settings file will update this default
      one.

.. data:: OUTPUT_PATH = 'output/'

   Where to output the generated files.

.. data:: PATH

   Path to content directory to be processed by Pelican. If undefined, and
   content path is not specified via an argument to the ``pelican`` command,
   Pelican will use the current working directory.

.. data:: PAGE_PATHS = ['pages']

   A list of directories and files to look at for pages, relative to ``PATH``.

.. data:: PAGE_EXCLUDES = []

   A list of directories to exclude when looking for pages in addition to
   ``ARTICLE_PATHS``.

.. data:: ARTICLE_PATHS = ['']

   A list of directories and files to look at for articles, relative to
   ``PATH``.

.. data:: ARTICLE_EXCLUDES = []

   A list of directories to exclude when looking for articles in addition to
   ``PAGE_PATHS``.

.. data:: OUTPUT_SOURCES = False

   Set to True if you want to copy the articles and pages in their original
   format (e.g. Markdown or reStructuredText) to the specified ``OUTPUT_PATH``.

.. data:: OUTPUT_SOURCES_EXTENSION = '.text'

   Controls the extension that will be used by the SourcesGenerator.  Defaults
   to ``.text``. If not a valid string the default value will be used.

.. data:: PLUGINS = []

   The list of plugins to load. See :ref:`plugins`.

.. data:: PLUGIN_PATHS = []

   A list of directories where to look for plugins. See :ref:`plugins`.

.. data:: SITENAME = 'A Pelican Blog'

   Your site name

.. data:: SITEURL

   Base URL of your website. Not defined by default, so it is best to specify
   your SITEURL; if you do not, feeds will not be generated with
   properly-formed URLs. You should include ``http://`` and your domain, with
   no trailing slash at the end. Example: ``SITEURL = 'http://mydomain.com'``

.. data:: STATIC_PATHS = ['images']

   A list of directories (relative to ``PATH``) in which to look for static
   files. Such files will be copied to the output directory without
   modification. Articles, pages, and other content source files will normally
   be skipped, so it is safe for a directory to appear both here and in
   ``PAGE_PATHS`` or ``ARTICLE_PATHS``.  Pelican's default settings include the
   "images" directory here.

.. data:: STATIC_EXCLUDES = []

   A list of directories to exclude when looking for static files.

.. data:: STATIC_EXCLUDE_SOURCES = True

   If set to False, content source files will not be skipped when copying files
   found in ``STATIC_PATHS``. This setting is for backward compatibility with
   Pelican releases before version 3.5.  It has no effect unless
   ``STATIC_PATHS`` contains a directory that is also in ``ARTICLE_PATHS`` or
   ``PAGE_PATHS``. If you are trying to publish your site's source files,
   consider using the ``OUTPUT_SOURCES`` setting instead.

.. data:: TYPOGRIFY = False

   If set to True, several typographical improvements will be incorporated into
   the generated HTML via the `Typogrify
   <https://pypi.python.org/pypi/typogrify>`_ library, which can be installed
   via: ``pip install typogrify``

.. data:: TYPOGRIFY_IGNORE_TAGS = []

   A list of tags for Typogrify to ignore. By default Typogrify will ignore
   ``pre`` and ``code`` tags. This requires that Typogrify version 2.0.4 or
   later is installed

.. data:: SUMMARY_MAX_LENGTH = 50

   When creating a short summary of an article, this will be the default length
   (measured in words) of the text created.  This only applies if your content
   does not otherwise specify a summary. Setting to ``None`` will cause the
   summary to be a copy of the original content.

.. data:: WITH_FUTURE_DATES = True

   If disabled, content with dates in the future will get a default status of
   ``draft``. See :ref:`reading_only_modified_content` for caveats.

.. data:: INTRASITE_LINK_REGEX = '[{|](?P<what>.*?)[|}]'

   Regular expression that is used to parse internal links. Default syntax when
   linking to internal files, tags, etc., is to enclose the identifier, say
   ``filename``, in ``{}`` or ``||``. Identifier between ``{`` and ``}`` goes
   into the ``what`` capturing group.  For details see
   :ref:`ref-linking-to-internal-content`.

.. data:: PYGMENTS_RST_OPTIONS = []

   A list of default Pygments settings for your reStructuredText code blocks.
   See :ref:`internal_pygments_options` for a list of supported options.

.. data:: SLUGIFY_SOURCE = 'title'

   Specifies where you want the slug to be automatically generated from. Can be
   set to ``title`` to use the 'Title:' metadata tag or ``basename`` to use the
   article's file name when creating the slug.

.. data:: CACHE_CONTENT = False

   If ``True``, saves content in caches.  See
   :ref:`reading_only_modified_content` for details about caching.

.. data:: CONTENT_CACHING_LAYER = 'reader'

   If set to ``'reader'``, save only the raw content and metadata returned by
   readers. If set to ``'generator'``, save processed content objects.

.. data:: CACHE_PATH = 'cache'

   Directory in which to store cache files.

.. data:: GZIP_CACHE = True

   If ``True``, use gzip to (de)compress the cache files.

.. data:: CHECK_MODIFIED_METHOD = 'mtime'

   Controls how files are checked for modifications.

.. data:: LOAD_CONTENT_CACHE = False

   If ``True``, load unmodified content from caches.

.. data:: WRITE_SELECTED = []

   If this list is not empty, **only** output files with their paths in this
   list are written. Paths should be either absolute or relative to the current
   Pelican working directory. For possible use cases see
   :ref:`writing_only_selected_content`.

.. data:: FORMATTED_FIELDS = ['summary']

   A list of metadata fields containing reST/Markdown content to be parsed and
   translated to HTML.


URL settings
============

The first thing to understand is that there are currently two supported methods
for URL formation: *relative* and *absolute*. Relative URLs are useful
when testing locally, and absolute URLs are reliable and most useful when
publishing. One method of supporting both is to have one Pelican configuration
file for local development and another for publishing. To see an example of this
type of setup, use the ``pelican-quickstart`` script as described in the
:doc:`Installation <install>` section, which will produce two separate
configuration files for local development and publishing, respectively.

You can customize the URLs and locations where files will be saved. The
``*_URL`` and ``*_SAVE_AS`` variables use Python's format strings. These
variables allow you to place your articles in a location such as
``{slug}/index.html`` and link to them as ``{slug}`` for clean URLs (see
example below). These settings give you the flexibility to place your articles
and pages anywhere you want.

.. note::
    If you specify a ``datetime`` directive, it will be substituted using the
    input files' date metadata attribute. If the date is not specified for a
    particular file, Pelican will rely on the file's ``mtime`` timestamp.
    Check the `Python datetime documentation`_ for more information.

.. _Python datetime documentation:
    http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

Also, you can use other file metadata attributes as well:

* slug
* date
* lang
* author
* category

Example usage::

   ARTICLE_URL = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/'
   ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/index.html'
   PAGE_URL = 'pages/{slug}/'
   PAGE_SAVE_AS = 'pages/{slug}/index.html'

This would save your articles into something like
``/posts/2011/Aug/07/sample-post/index.html``,
save your pages into ``/pages/about/index.html``, and render them available at
URLs of ``/posts/2011/Aug/07/sample-post/`` and ``/pages/about/``,
respectively.

.. data:: RELATIVE_URLS = False

   Defines whether Pelican should use document-relative URLs or not. Only set
   this to ``True`` when developing/testing and only if you fully understand
   the effect it can have on links/feeds.

.. data:: ARTICLE_URL = '{slug}.html'

   The URL to refer to an article.

.. data:: ARTICLE_SAVE_AS = '{slug}.html'

   The place where we will save an article.

.. data:: ARTICLE_LANG_URL = '{slug}-{lang}.html'

   The URL to refer to an article which doesn't use the default language.

.. data:: ARTICLE_LANG_SAVE_AS = '{slug}-{lang}.html'

   The place where we will save an article which doesn't use the default
   language.

.. data:: DRAFT_URL = 'drafts/{slug}.html'

   The URL to refer to an article draft.

.. data:: DRAFT_SAVE_AS = 'drafts/{slug}.html'

   The place where we will save an article draft.

.. data:: DRAFT_LANG_URL = 'drafts/{slug}-{lang}.html'

   The URL to refer to an article draft which doesn't use the default language.

.. data:: DRAFT_LANG_SAVE_AS = 'drafts/{slug}-{lang}.html'

   The place where we will save an article draft which doesn't use the default
   language.

.. data:: PAGE_URL = 'pages/{slug}.html'

   The URL we will use to link to a page.

.. data:: PAGE_SAVE_AS = 'pages/{slug}.html'

   The location we will save the page. This value has to be the same as
   PAGE_URL or you need to use a rewrite in your server config.

.. data:: PAGE_LANG_URL = 'pages/{slug}-{lang}.html'

   The URL we will use to link to a page which doesn't use the default
   language.

.. data:: PAGE_LANG_SAVE_AS = 'pages/{slug}-{lang}.html'

   The location we will save the page which doesn't use the default language.

.. data:: CATEGORY_URL = 'category/{slug}.html'

   The URL to use for a category.

.. data:: CATEGORY_SAVE_AS = 'category/{slug}.html'

   The location to save a category.

.. data:: TAG_URL = 'tag/{slug}.html'

   The URL to use for a tag.

.. data:: TAG_SAVE_AS = 'tag/{slug}.html'

   The location to save the tag page.

.. data:: AUTHOR_URL = 'author/{slug}.html'

   The URL to use for an author.

.. data:: AUTHOR_SAVE_AS = 'author/{slug}.html'

   The location to save an author.

.. data:: YEAR_ARCHIVE_SAVE_AS = ''

   The location to save per-year archives of your posts.

.. data:: MONTH_ARCHIVE_SAVE_AS = ''

   The location to save per-month archives of your posts.

.. data:: DAY_ARCHIVE_SAVE_AS = ''

   The location to save per-day archives of your posts.

.. data:: SLUG_SUBSTITUTIONS = ()

   Substitutions to make prior to stripping out non-alphanumerics when
   generating slugs. Specified as a list of 3-tuples of ``(from, to, skip)``
   which are applied in order. ``skip`` is a boolean indicating whether or not
   to skip replacement of non-alphanumeric characters.  Useful for backward
   compatibility with existing URLs.

.. data:: AUTHOR_SUBSTITUTIONS = ()

   Substitutions for authors. ``SLUG_SUBSTITUTIONS`` is not taken into account
   here!

.. data:: CATEGORY_SUBSTITUTIONS = ()

   Added to ``SLUG_SUBSTITUTIONS`` for categories.

.. data:: TAG_SUBSTITUTIONS = ()

   Added to ``SLUG_SUBSTITUTIONS`` for tags.

.. note::

    If you do not want one or more of the default pages to be created (e.g.,
    you are the only author on your site and thus do not need an Authors page),
    set the corresponding ``*_SAVE_AS`` setting to ``''`` to prevent the
    relevant page from being generated.

.. note::

    Substitutions are applied in order with the side effect that keeping
    non-alphanum characters applies to the whole string when a replacement
    is made.

    For example if you have the following setting::

       SLUG_SUBSTITUTIONS = (('C++', 'cpp'), ('keep dot', 'keep.dot', True))

    the string ``Keep Dot`` will be converted to ``keep.dot``, however
    ``C++ will keep dot`` will be converted to ``cpp will keep.dot`` instead
    of ``cpp-will-keep.dot``!

    If you want to keep non-alphanum characters only for tags or categories
    but not other slugs then configure ``TAG_SUBSTITUTIONS`` and
    ``CATEGORY_SUBSTITUTIONS`` respectively!

Pelican can optionally create per-year, per-month, and per-day archives of your
posts. These secondary archives are disabled by default but are automatically
enabled if you supply format strings for their respective ``_SAVE_AS`` settings.
Period archives fit intuitively with the hierarchical model of web URLs and can
make it easier for readers to navigate through the posts you've written over time.

Example usage::

   YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
   MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'

With these settings, Pelican will create an archive of all your posts for the
year at (for instance) ``posts/2011/index.html`` and an archive of all your
posts for the month at ``posts/2011/Aug/index.html``.

.. note::
    Period archives work best when the final path segment is ``index.html``.
    This way a reader can remove a portion of your URL and automatically
    arrive at an appropriate archive of posts, without having to specify
    a page name.

``DIRECT_TEMPLATES`` work a bit differently than noted above. Only the
``_SAVE_AS`` settings are available, but it is available for any direct
template.

.. data:: ARCHIVES_SAVE_AS = 'archives.html'

   The location to save the article archives page.

.. data:: YEAR_ARCHIVE_SAVE_AS = ''

   The location to save per-year archives of your posts.

.. data:: MONTH_ARCHIVE_SAVE_AS = ''

   The location to save per-month archives of your posts.

.. data:: DAY_ARCHIVE_SAVE_AS = ''

   The location to save per-day archives of your posts.

.. data:: AUTHORS_SAVE_AS = 'authors.html'

   The location to save the author list.

.. data:: CATEGORIES_SAVE_AS = 'categories.html'

   The location to save the category list.

.. data:: TAGS_SAVE_AS = 'tags.html'

   The location to save the tag list.

.. data:: INDEX_SAVE_AS = 'index.html'

   The location to save the list of all articles.

URLs for direct template pages are theme-dependent. Some themes use
corresponding ``*_URL`` setting as string, while others hard-code them:
``'archives.html'``, ``'authors.html'``, ``'categories.html'``, ``'tags.html'``.

Time and Date
=============

.. data:: TIMEZONE

   The timezone used in the date information, to generate Atom and RSS feeds.

   If no timezone is defined, UTC is assumed. This means that the generated
   Atom and RSS feeds will contain incorrect date information if your locale is
   not UTC.

   Pelican issues a warning in case this setting is not defined, as it was not
   mandatory in previous versions.

   Have a look at `the wikipedia page`_ to get a list of valid timezone values.

.. _the wikipedia page: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones

.. data:: DEFAULT_DATE = None

   The default date you want to use.  If ``'fs'``, Pelican will use the file
   system timestamp information (mtime) if it can't get date information from
   the metadata.  If given any other string, it will be parsed by the same
   method as article metadata.  If set to a tuple object, the default datetime
   object will instead be generated by passing the tuple to the
   ``datetime.datetime`` constructor.

.. data:: DEFAULT_DATE_FORMAT = '%a %d %B %Y'

   The default date format you want to use.

.. data:: DATE_FORMATS = {}

   If you manage multiple languages, you can set the date formatting here.

   If no ``DATE_FORMATS`` are set, Pelican will fall back to
   ``DEFAULT_DATE_FORMAT``. If you need to maintain multiple languages with
   different date formats, you can set the ``DATE_FORMATS`` dictionary using
   the language name (``lang`` metadata in your post content) as the key.

   In addition to the standard C89 strftime format codes that are listed in
   `Python strftime documentation`_, you can use the ``-`` character between
   ``%`` and the format character to remove any leading zeros. For example,
   ``%d/%m/%Y`` will output ``01/01/2014`` whereas ``%-d/%-m/%Y`` will result
   in ``1/1/2014``.

   .. parsed-literal::

       DATE_FORMATS = {
           'en': '%a, %d %b %Y',
           'jp': '%Y-%m-%d(%a)',
       }

   It is also possible to set different locale settings for each language by
   using a ``(locale, format)`` tuple as a dictionary value which will override
   the ``LOCALE`` setting:

   .. parsed-literal::

      # On Unix/Linux
      DATE_FORMATS = {
          'en': ('en_US','%a, %d %b %Y'),
          'jp': ('ja_JP','%Y-%m-%d(%a)'),
      }

      # On Windows
      DATE_FORMATS = {
          'en': ('usa','%a, %d %b %Y'),
          'jp': ('jpn','%Y-%m-%d(%a)'),
      }

.. data:: LOCALE

   Change the locale [#]_. A list of locales can be provided here or a single
   string representing one locale.  When providing a list, all the locales will
   be tried until one works.

   You can set locale to further control date format:

   .. parsed-literal::

       LOCALE = ('usa', 'jpn',      # On Windows
                 'en_US', 'ja_JP'   # On Unix/Linux
      )

   For a list of available locales refer to `locales on Windows`_  or on
   Unix/Linux, use the ``locale -a`` command; see manpage
   `locale(1)`_ for more information.


.. [#] Default is the system locale.

.. _Python strftime documentation: http://docs.python.org/library/datetime.html#strftime-strptime-behavior

.. _locales on Windows: http://msdn.microsoft.com/en-us/library/cdax410z%28VS.71%29.aspx

.. _locale(1): http://linux.die.net/man/1/locale


.. _template_pages:

Template pages
==============

.. data:: TEMPLATE_PAGES = None

   A mapping containing template pages that will be rendered with the blog
   entries. See :ref:`template_pages`.

   If you want to generate custom pages besides your blog entries, you can
   point any Jinja2 template file with a path pointing to the file and the
   destination path for the generated file.

   For instance, if you have a blog with three static pages — a list of books,
   your resume, and a contact page — you could have::

       TEMPLATE_PAGES = {'src/books.html': 'dest/books.html',
                         'src/resume.html': 'dest/resume.html',
                         'src/contact.html': 'dest/contact.html'}

.. data:: DIRECT_TEMPLATES = ['index', 'categories', 'authors', 'archives']

   List of templates that are used directly to render content. Typically direct
   templates are used to generate index pages for collections of content (e.g.,
   tags and category index pages). If the tag and category collections are not
   needed, set ``DIRECT_TEMPLATES = ['index', 'archives']``

.. data:: PAGINATED_DIRECT_TEMPLATES = ['index']

   Provides the direct templates that should be paginated.

.. data:: EXTRA_TEMPLATES_PATHS = []

   A list of paths you want Jinja2 to search for templates.  Can be used to
   separate templates from the theme.  Example: projects, resume, profile ...
   These templates need to use ``DIRECT_TEMPLATES`` setting.


Metadata
========

.. data:: AUTHOR

   Default author (usually your name).

.. data:: DEFAULT_METADATA = {}

   The default metadata you want to use for all articles and pages.

.. data:: FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2}).*'

   The regexp that will be used to extract any metadata from the filename. All
   named groups that are matched will be set in the metadata object.  The
   default value will only extract the date from the filename.

   For example, to extract both the date and the slug::

      FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'

   See also ``SLUGIFY_SOURCE``.

.. data:: PATH_METADATA = ''

   Like ``FILENAME_METADATA``, but parsed from a page's full path relative to
   the content source directory.

.. data:: EXTRA_PATH_METADATA = {}

   Extra metadata dictionaries keyed by relative path. Relative paths require
   correct OS-specific directory separators (i.e. / in UNIX and \\ in Windows)
   unlike some other Pelican file settings.

Not all metadata needs to be :ref:`embedded in source file itself
<internal_metadata>`. For example, blog posts are often named
following a ``YYYY-MM-DD-SLUG.rst`` pattern, or nested into
``YYYY/MM/DD-SLUG`` directories. To extract metadata from the
filename or path, set ``FILENAME_METADATA`` or ``PATH_METADATA`` to
regular expressions that use Python's `group name notation`_ ``(?P<name>…)``.
If you want to attach additional metadata but don't want to encode
it in the path, you can set ``EXTRA_PATH_METADATA``:

.. parsed-literal::

    EXTRA_PATH_METADATA = {
        'relative/path/to/file-1': {
            'key-1a': 'value-1a',
            'key-1b': 'value-1b',
            },
        'relative/path/to/file-2': {
            'key-2': 'value-2',
            },
        }

This can be a convenient way to shift the installed location of a
particular file:

.. parsed-literal::

    # Take advantage of the following defaults
    # STATIC_SAVE_AS = '{path}'
    # STATIC_URL = '{path}'
    STATIC_PATHS = [
        'static/robots.txt',
        ]
    EXTRA_PATH_METADATA = {
        'static/robots.txt': {'path': 'robots.txt'},
        }

.. _group name notation:
   http://docs.python.org/3/library/re.html#regular-expression-syntax


Feed settings
=============

By default, Pelican uses Atom feeds. However, it is also possible to use RSS
feeds if you prefer.

Pelican generates category feeds as well as feeds for all your articles. It does
not generate feeds for tags by default, but it is possible to do so using
the ``TAG_FEED_ATOM`` and ``TAG_FEED_RSS`` settings:

.. data:: FEED_DOMAIN = None, i.e. base URL is "/"

   The domain prepended to feed URLs. Since feed URLs should always be
   absolute, it is highly recommended to define this (e.g.,
   "http://feeds.example.com"). If you have already explicitly defined SITEURL
   (see above) and want to use the same domain for your feeds, you can just
   set:  ``FEED_DOMAIN = SITEURL``.

.. data:: FEED_ATOM = None, i.e. no Atom feed

   Relative URL to output the Atom feed.

.. data:: FEED_RSS = None, i.e. no RSS

   Relative URL to output the RSS feed.

.. data:: FEED_ALL_ATOM = 'feeds/all.atom.xml'

   Relative URL to output the all-posts Atom feed: this feed will contain all
   posts regardless of their language.

.. data:: FEED_ALL_RSS = None, i.e. no all-posts RSS

   Relative URL to output the all-posts RSS feed: this feed will contain all
   posts regardless of their language.

.. data:: CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

   Where to put the category Atom feeds. [2]_

.. data:: CATEGORY_FEED_RSS = None, i.e. no RSS

   Where to put the category RSS feeds.

.. data:: AUTHOR_FEED_ATOM = 'feeds/%s.atom.xml'

   Where to put the author Atom feeds. [2]_

.. data:: AUTHOR_FEED_RSS = 'feeds/%s.rss.xml'

   Where to put the author RSS feeds. [2]_

.. data:: TAG_FEED_ATOM = None, i.e. no tag feed

   Relative URL to output the tag Atom feed. It should be defined using a "%s"
   match in the tag name.

.. data:: TAG_FEED_RSS = None, i.e. no RSS tag feed

   Relative URL to output the tag RSS feed

.. data:: FEED_MAX_ITEMS

   Maximum number of items allowed in a feed. Feed item quantity is
   unrestricted by default.

.. data:: RSS_FEED_SUMMARY_ONLY = True

   Only include item summaries in the ``description`` tag of RSS feeds. If set
   to ``False``, the full content will be included instead. This setting
   doesn't affect Atom feeds, only RSS ones.

If you don't want to generate some or any of these feeds, set the above variables to ``None``.

.. [2] %s is the name of the category.


FeedBurner
----------

If you want to use FeedBurner for your feed, you will likely need to decide
upon a unique identifier. For example, if your site were called "Thyme" and
hosted on the www.example.com domain, you might use "thymefeeds" as your
unique identifier, which we'll use throughout this section for illustrative
purposes. In your Pelican settings, set the ``FEED_ATOM`` attribute to
``thymefeeds/main.xml`` to create an Atom feed with an original address of
``http://www.example.com/thymefeeds/main.xml``. Set the ``FEED_DOMAIN``
attribute to ``http://feeds.feedburner.com``, or ``http://feeds.example.com`` if
you are using a CNAME on your own domain (i.e., FeedBurner's "MyBrand" feature).

There are two fields to configure in the `FeedBurner
<http://feedburner.google.com>`_ interface: "Original Feed" and "Feed
Address". In this example, the "Original Feed" would be
``http://www.example.com/thymefeeds/main.xml`` and the "Feed Address" suffix
would be ``thymefeeds/main.xml``.


Pagination
==========

The default behaviour of Pelican is to list all the article titles along
with a short description on the index page. While this works well for
small-to-medium sites, sites with a large quantity of articles will probably
benefit from paginating this list.

You can use the following settings to configure the pagination.

.. data:: DEFAULT_ORPHANS = 0

   The minimum number of articles allowed on the last page. Use this when you
   don't want the last page to only contain a handful of articles.

.. data:: DEFAULT_PAGINATION = False

   The maximum number of articles to include on a page, not including orphans.
   False to disable pagination.

.. data:: PAGINATION_PATTERNS

   A set of patterns that are used to determine advanced pagination output.


Using Pagination Patterns
-------------------------

The ``PAGINATION_PATTERNS`` setting can be used to configure where
subsequent pages are created. The setting is a sequence of three
element tuples, where each tuple consists of::

  (minimum page, URL setting, SAVE_AS setting,)

For example, if you wanted the first page to just be ``/``, and the
second (and subsequent) pages to be ``/page/2/``, you would set
``PAGINATION_PATTERNS`` as follows::

  PAGINATION_PATTERNS = (
      (1, '{base_name}/', '{base_name}/index.html'),
      (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
  )

This would cause the first page to be written to
``{base_name}/index.html``, and subsequent ones would be written into
``page/{number}`` directories.


Translations
============

Pelican offers a way to translate articles. See the :doc:`Content <content>` section for
more information.

.. data:: DEFAULT_LANG = 'en'

   The default language to use.

.. data:: TRANSLATION_FEED_ATOM = 'feeds/all-%s.atom.xml'

   Where to put the Atom feed for translations. [3]_

.. data:: TRANSLATION_FEED_RSS = None, i.e. no RSS

   Where to put the RSS feed for translations.

.. [3] %s is the language


Ordering content
================

.. data:: NEWEST_FIRST_ARCHIVES = True

   Order archives by newest first by date. (False: orders by date with older
   articles first.)

.. data:: REVERSE_CATEGORY_ORDER = False

   Reverse the category order. (True: lists by reverse alphabetical order;
   default lists alphabetically.)

.. data:: ARTICLE_ORDER_BY = 'reversed-date'

   Defines how the articles (``articles_page.object_list`` in the template) are
   sorted. Valid options are: metadata as a string (use ``reversed-`` prefix
   the reverse the sort order), special option ``'basename'`` which will use
   the basename of the file (without path) or a custom function to extract the
   sorting key from articles. The default value, ``'reversed-date'``, will sort
   articles by date in reverse order (i.e. newest article comes first).

.. data:: PAGE_ORDER_BY = 'basename'

   Defines how the pages (``PAGES`` variable in the template) are sorted.
   Options are same as ``ARTICLE_ORDER_BY``.  The default value, ``'basename'``
   will sort pages by their basename.



Themes
======

Creating Pelican themes is addressed in a dedicated section (see :ref:`theming-pelican`).
However, here are the settings that are related to themes.

.. data:: THEME

   Theme to use to produce the output. Can be a relative or absolute path to a
   theme folder, or the name of a default theme or a theme installed via
   ``pelican-themes`` (see below).

.. data:: THEME_STATIC_DIR = 'theme'

   Destination directory in the output path where Pelican will place the files
   collected from `THEME_STATIC_PATHS`. Default is `theme`.

.. data:: THEME_STATIC_PATHS = ['static']

   Static theme paths you want to copy. Default value is `static`, but if your
   theme has other static paths, you can put them here. If files or directories
   with the same names are included in the paths defined in this settings, they
   will be progressively overwritten.

.. data:: CSS_FILE = 'main.css'

   Specify the CSS file you want to load.

By default, two themes are available. You can specify them using the ``THEME``
setting or by passing the ``-t`` option to the ``pelican`` command:

* notmyidea
* simple (a synonym for "plain text" :)

There are a number of other themes available at https://github.com/getpelican/pelican-themes.
Pelican comes with :doc:`pelican-themes`, a small script for managing themes.

You can define your own theme, either by starting from scratch or by duplicating
and modifying a pre-existing theme. Here is :doc:`a guide on how to create your theme <themes>`.

Following are example ways to specify your preferred theme::

    # Specify name of a built-in theme
    THEME = "notmyidea"
    # Specify name of a theme installed via the pelican-themes tool
    THEME = "chunk"
    # Specify a customized theme, via path relative to the settings file
    THEME = "themes/mycustomtheme"
    # Specify a customized theme, via absolute path
    THEME = "/home/myuser/projects/mysite/themes/mycustomtheme"

The built-in ``notmyidea`` theme can make good use of the following settings. Feel
free to use them in your themes as well.

.. data:: SITESUBTITLE

   A subtitle to appear in the header.

.. data:: DISQUS_SITENAME

   Pelican can handle Disqus comments. Specify the Disqus sitename identifier
   here.

.. data:: GITHUB_URL

   Your GitHub URL (if you have one). It will then use this information to
   create a GitHub ribbon.

.. data:: GOOGLE_ANALYTICS

   Set to ``UA-XXXXX-Y`` Property's tracking ID to activate Google Analytics.

.. data:: GA_COOKIE_DOMAIN

   Set cookie domain field of Google Analytics tracking code. Defaults to
   ``auto``.

.. data:: GOSQUARED_SITENAME

   Set to 'XXX-YYYYYY-X' to activate GoSquared.

.. data:: MENUITEMS

   A list of tuples (Title, URL) for additional menu items to appear at the
   beginning of the main menu.

.. data:: PIWIK_URL

   URL to your Piwik server - without 'http://' at the beginning.

.. data:: PIWIK_SSL_URL

   If the SSL-URL differs from the normal Piwik-URL you have to include this
   setting too. (optional)

.. data:: PIWIK_SITE_ID

   ID for the monitored website. You can find the ID in the Piwik admin
   interface > Settings > Websites.

.. data:: LINKS

   A list of tuples (Title, URL) for links to appear on the header.

.. data:: SOCIAL

   A list of tuples (Title, URL) to appear in the "social" section.

.. data:: TWITTER_USERNAME

   Allows for adding a button to articles to encourage others to tweet about
   them. Add your Twitter username if you want this button to appear.

.. data:: LINKS_WIDGET_NAME

   Allows override of the name of the links widget.  If not specified, defaults
   to "links".

.. data:: SOCIAL_WIDGET_NAME

   Allows override of the name of the "social" widget.  If not specified,
   defaults to "social".

In addition, you can use the "wide" version of the ``notmyidea`` theme by
adding the following to your configuration::

    CSS_FILE = "wide.css"


Logging
=======

Sometimes, a long list of warnings may appear during site generation. Finding
the **meaningful** error message in the middle of tons of annoying log output
can be quite tricky. In order to filter out redundant log messages, Pelican
comes with the ``LOG_FILTER`` setting.

``LOG_FILTER`` should be a list of tuples ``(level, msg)``, each of them being
composed of the logging level (up to ``warning``) and the message to be ignored.
Simply populate the list with the log messages you want to hide, and they will
be filtered out.

For example::

   [(logging.WARN, 'TAG_SAVE_AS is set to False')]

It is possible to filter out messages by a template. Check out source code to
obtain a template.

For example::

   [(logging.WARN, 'Empty alt attribute for image %s in %s')]

.. Warning::
   Silencing messages by templates is a dangerous feature. It is possible to
   unintentionally filter out multiple message types with the same template
   (including messages from future Pelican versions). Proceed with caution.

.. note::

    This option does nothing if ``--debug`` is passed.

.. _reading_only_modified_content:


Reading only modified content
=============================

To speed up the build process, Pelican can optionally read only articles
and pages with modified content.

When Pelican is about to read some content source file:

1. The hash or modification time information for the file from a
   previous build are loaded from a cache file if ``LOAD_CONTENT_CACHE``
   is ``True``. These files are stored in the ``CACHE_PATH``
   directory.  If the file has no record in the cache file, it is read
   as usual.
2. The file is checked according to ``CHECK_MODIFIED_METHOD``:

    - If set to ``'mtime'``, the modification time of the file is
      checked.
    - If set to a name of a function provided by the ``hashlib``
      module, e.g. ``'md5'``, the file hash is checked.
    - If set to anything else or the necessary information about the
      file cannot be found in the cache file, the content is read as
      usual.

3. If the file is considered unchanged, the content data saved in a
   previous build corresponding to the file is loaded from the cache,
   and the file is not read.
4. If the file is considered changed, the file is read and the new
   modification information and the content data are saved to the
   cache if ``CACHE_CONTENT`` is ``True``.

If ``CONTENT_CACHING_LAYER`` is set to ``'reader'`` (the default),
the raw content and metadata returned by a reader are cached. If this
setting is instead set to ``'generator'``, the processed content
object is cached. Caching the processed content object may conflict
with plugins (as some reading related signals may be skipped) and the
``WITH_FUTURE_DATES`` functionality (as the ``draft`` status of the
cached content objects would not change automatically over time).

Checking modification times is faster than comparing file hashes,
but it is not as reliable because ``mtime`` information can be lost,
e.g., when copying content source files using the ``cp`` or ``rsync``
commands without the ``mtime`` preservation mode (which for ``rsync``
can be invoked by passing the ``--archive`` flag).

The cache files are Python pickles, so they may not be readable by
different versions of Python as the pickle format often changes. If
such an error is encountered, it is caught and the cache file is
rebuilt automatically in the new format. The cache files will also be
rebuilt after the ``GZIP_CACHE`` setting has been changed.

The ``--ignore-cache`` command-line option is useful when the
whole cache needs to be regenerated, such as when making modifications
to the settings file that will affect the cached content, or just for
debugging purposes. When Pelican runs in autoreload mode, modification
of the settings file will make it ignore the cache automatically if
``AUTORELOAD_IGNORE_CACHE`` is ``True``.

Note that even when using cached content, all output is always
written, so the modification times of the generated ``*.html`` files
will always change. Therefore, ``rsync``-based uploading may benefit
from the ``--checksum`` option.

.. _writing_only_selected_content:


Writing only selected content
=============================

When only working on a single article or page, or making tweaks to
your theme, it is often desirable to generate and review your work
as quickly as possible. In such cases, generating and writing the
entire site output is often unnecessary. By specifying only the
desired files as output paths in the ``WRITE_SELECTED`` list,
**only** those files will be written. This list can be also specified
on the command line using the ``--write-selected`` option, which
accepts a comma-separated list of output file paths. By default this
list is empty, so all output is written. See :ref:`site_generation` for
more details.


Example settings
================

.. literalinclude:: ../samples/pelican.conf.py
    :language: python


.. _Jinja custom filters documentation: http://jinja.pocoo.org/docs/api/#custom-filters
.. _Jinja Environment documentation: http://jinja.pocoo.org/docs/dev/api/#jinja2.Environment
.. _Docutils Configuration: http://docutils.sourceforge.net/docs/user/config.html
