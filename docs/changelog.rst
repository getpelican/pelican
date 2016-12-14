Release history
###############

Next release
============

- Nothing yet

3.7.0 (2016-12-12)
==================

* Atom feeds output ``<content>`` in addition to ``<summary>``
* Atom feeds use ``<published>`` for the original publication date and
  ``<updated>`` for modifications
* Simplify Atom feed ID generation and support URL fragments
* Produce category feeds with category-specific titles
* RSS feeds now default to summary instead of full content —
  set ``RSS_FEED_SUMMARY_ONLY = False`` to revert to previous behavior
* Replace ``MD_EXTENSIONS`` with ``MARKDOWN`` setting
* Replace ``JINJA_EXTENSIONS`` with more-robust ``JINJA_ENVIRONMENT`` setting
* Improve summary truncation logic to handle special characters and tags that
  span multiple lines, using HTML parser instead of regular expressions
* Include summary when looking for intra-site link substitutions
* Link to authors and index via ``{author}name`` and ``{index}`` syntax
* Override widget names via ``LINKS_WIDGET_NAME`` and ``SOCIAL_WIDGET_NAME``
* Add ``INDEX_SAVE_AS`` option to override default ``index.html`` value
* Remove ``PAGES`` context variable for themes in favor of ``pages``
* ``SLUG_SUBSTITUTIONS`` now accepts 3-tuple elements, allowing URL slugs to
  contain non-alphanumeric characters
* Tag and category slugs can be controlled with greater precision using the
  ``TAG_SUBSTITUTIONS`` and ``CATEGORY_SUBSTITUTIONS`` settings
* Author slugs can be controlled with greater precision using the
  ``AUTHOR_SUBSTITUTIONS`` setting
* ``DEFAULT_DATE`` can be defined as a string
* Use ``mtime`` instead of ``ctime`` when ``DEFAULT_DATE = 'fs'``
* Add ``--fatal=errors|warnings`` option for use with continuous integration
* When using generator-level caching, ensure previously-cached files are
  processed instead of just new files.
* Add Python and Pelican version information to debug output
* Improve compatibility with Python 3.5
* Comply with and enforce PEP8 guidelines
* Replace tables in settings documentation with ``data::`` directives

3.6.3 (2015-08-14)
==================

* Fix permissions issue in release tarball

3.6.2 (2015-08-01)
==================

* Fix installation errors related to Unicode in tests
* Don't show pagination in ``notmyidea`` theme if there's only one page
* Make hidden pages available in context
* Improve URLWrapper comparison

3.6.0 (2015-06-15)
==================

* Disable caching by default in order to prevent potential confusion
* Improve caching behavior, replacing ``pickle`` with ``cpickle``
* Allow Markdown or reST content in metadata fields other than ``summary``
* Support semicolon-separated author/tag lists
* Improve flexibility of article sorting
* Add ``--relative-urls`` argument
* Support devserver listening on addresses other than localhost
* Unify HTTP server handlers to ``pelican.server`` throughout
* Handle intra-site links to draft posts
* Move ``tag_cloud`` from core to plugin
* Load default theme's external resources via HTTPS
* Import drafts from WordPress XML
* Improve support for Windows users
* Enhance logging and test suite
* Clean up and refactor codebase
* New signals: ``all_generators_finalized`` and ``page_writer_finalized``

3.5.0 (2014-11-04)
==================

* Introduce ``ARTICLE_ORDER_BY`` and ``PAGE_ORDER_BY`` settings to control the
  order of articles and pages.
* Include time zone information in dates rendered in templates.
* Expose the reader name in the metadata for articles and pages.
* Add the ability to store static files along with content in the same
  directory as articles and pages using ``{attach}`` in the path.
* Prevent Pelican from raising an exception when there are duplicate pieces of
  metadata in a Markdown file.
* Introduce the ``TYPOGRIFY_IGNORE_TAGS`` setting to add HTML tags to be ignored
  by Typogrify.
* Add the ability to use ``-`` in date formats to strip leading zeros. For
  example, ``%-d/%-m/%y`` will now result in the date ``9/8/12``.
* Ensure feed generation is correctly disabled during quickstart configuration.
* Fix ``PAGE_EXCLUDES`` and ``ARTICLE_EXCLUDES`` from incorrectly matching
  sub-directories.
* Introduce ``STATIC_EXCLUDE`` setting to add static file excludes.
* Fix an issue when using ``PAGINATION_PATTERNS`` while ``RELATIVE_URLS``
  is enabled.
* Fix feed generation causing links to use the wrong language for month
  names when using other locales.
* Fix an issue where the authors list in the simple template wasn't correctly
  formatted.
* Fix an issue when parsing non-string URLs from settings.
* Improve consistency of debug and warning messages.

3.4.0 (2014-07-01)
==================

* Speed up content generation via new caching mechanism
* Add selective post generation (instead of always building entire site)
* Many documentation improvements, including switching to prettier RtD theme
* Add support for multiple content and plugin paths
* Add ``:modified:`` metadata field to complement ``:date:``.
  Used to specify the last date and time an article was updated independently
  from the date and time it was published.
* Add support for multiple authors via new ``:authors:`` metadata field
* Watch for changes in static directories when in auto-regeneration mode
* Add filters to limit log output when desired
* Add language support to drafts
* Add ``SLUGIFY_SOURCE`` setting to control how post slugs are generated
* Fix many issues relating to locale and encoding
* Apply Typogrify filter to post summary
* Preserve file metadata (e.g. time stamps) when copying static files to output
* Move AsciiDoc support from Pelican core into separate plugin
* Produce inline links instead of reference-style links when importing content
* Improve handling of ``IGNORE_FILES`` setting behavior
* Properly escape symbol characters in tag names (e.g., ``C++``)
* Minor tweaks for Python 3.4 compatibility
* Add several new signals

3.3.0 (2013-09-24)
==================

* Drop Python 3.2 support in favor of Python 3.3
* Add ``Fabfile`` so Fabric can be used for workflow automation instead of Make
* ``OUTPUT_RETENTION`` setting can be used to preserve metadata (e.g., VCS
  data such as ``.hg`` and ``.git``) from being removed from output directory
* Tumblr import
* Improve logic and consistency when cleaning output folder
* Improve documentation versioning and release automation
* Improve pagination flexibility
* Rename signals for better consistency (some plugins may need to be updated)
* Move metadata extraction from generators to readers; metadata extraction no
  longer article-specific
* Deprecate ``FILES_TO_COPY`` in favor of ``STATIC_PATHS`` and
  ``EXTRA_PATH_METADATA``
* Summaries in Markdown posts no longer include footnotes
* Remove unnecessary whitespace in output via ``lstrip_blocks`` Jinja parameter
* Move PDF generation from core to plugin
* Replace ``MARKUP`` setting with ``READERS``
* Add warning if img tag is missing ``alt`` attribute
* Add support for ``{}`` in relative links syntax, besides ``||``
* Add support for ``{tag}`` and ``{category}`` relative links
* Add a ``content_written`` signal

3.2.1 and 3.2.2
===============

* Facilitate inclusion in FreeBSD Ports Collection

3.2 (2013-04-24)
================

* Support for Python 3!
* Override page save-to location from meta-data (enables using a static page as
  the site's home page, for example)
* Time period archives (per-year, per-month, and per-day archives of posts)
* Posterous blog import
* Improve WordPress blog import
* Migrate plugins to separate repository
* Improve HTML parser
* Provide ability to show or hide categories from menu using
  ``DISPLAY_CATEGORIES_ON_MENU`` option
* Auto-regeneration can be told to ignore files via ``IGNORE_FILES`` setting
* Improve post-generation feedback to user
* For multilingual posts, use meta-data to designate which is the original
  and which is the translation
* Add ``.mdown`` to list of supported Markdown file extensions
* Document-relative URL generation (``RELATIVE_URLS``) is now off by default

3.1 (2012-12-04)
================

* Importer now stores slugs within files by default. This can be disabled with
  the ``--disable-slugs`` option.
* Improve handling of links to intra-site resources
* Ensure WordPress import adds paragraphs for all types of line endings
  in post content
* Decode HTML entities within WordPress post titles on import
* Improve appearance of LinkedIn icon in default theme
* Add GitHub and Google+ social icons support in default theme
* Optimize social icons
* Add ``FEED_ALL_ATOM`` and ``FEED_ALL_RSS`` to generate feeds containing all posts regardless of their language
* Split ``TRANSLATION_FEED`` into ``TRANSLATION_FEED_ATOM`` and ``TRANSLATION_FEED_RSS``
* Different feeds can now be enabled/disabled individually
* Allow for blank author: if ``AUTHOR`` setting is not set, author won't
  default to ``${USER}`` anymore, and a post won't contain any author
  information if the post author is empty
* Move LESS and Webassets support from Pelican core to plugin
* The ``DEFAULT_DATE`` setting now defaults to ``None``, which means that
  articles won't be generated unless date metadata is specified
* Add ``FILENAME_METADATA`` setting to support metadata extraction from filename
* Add ``gzip_cache`` plugin to compress common text files into a ``.gz``
  file within the same directory as the original file, preventing the server
  (e.g. Nginx) from having to compress files during an HTTP call
* Add support for AsciiDoc-formatted content
* Add ``USE_FOLDER_AS_CATEGORY`` setting so that feature can be toggled on/off
* Support arbitrary Jinja template files
* Restore basic functional tests
* New signals: ``generator_init``, ``get_generators``, and
  ``article_generate_preread``

3.0 (2012-08-08)
================

* Refactored the way URLs are handled
* Improved the English documentation
* Fixed packaging using ``setuptools`` entrypoints
* Added ``typogrify`` support
* Added a way to disable feed generation
* Added support for ``DIRECT_TEMPLATES``
* Allow multiple extensions for content files
* Added LESS support
* Improved the import script
* Added functional tests
* Rsync support in the generated Makefile
* Improved feed support (easily pluggable with Feedburner for instance)
* Added support for ``abbr`` in reST
* Fixed a bunch of bugs :-)

2.8 (2012-02-28)
==================

* Dotclear importer
* Allow the usage of Markdown extensions
* Themes are now easily extensible
* Don't output pagination information if there is only one page
* Add a page per author, with all their articles
* Improved the test suite
* Made the themes easier to extend
* Removed Skribit support
* Added a ``pelican-quickstart`` script
* Fixed timezone-related issues
* Added some scripts for Windows support
* Date can be specified in seconds
* Never fail when generating posts (skip and continue)
* Allow the use of future dates
* Support having different timezones per language
* Enhanced the documentation

2.7 (2011-06-11)
==================

* Use ``logging`` rather than echoing to stdout
* Support custom Jinja filters
* Compatibility with Python 2.5
* Added a theme manager
* Packaged for Debian
* Added draft support

2.6 (2011-03-08)
==================

* Changes in the output directory structure
* Makes templates easier to work with / create
* Added RSS support (was Atom-only)
* Added tag support for the feeds
* Enhance the documentation
* Added another theme (brownstone)
* Added translations
* Added a way to use cleaner URLs with a rewrite url module (or equivalent)
* Added a tag cloud
* Added an autoreloading feature: the blog is automatically regenerated each time a modification is detected
* Translate the documentation into French
* Import a blog from an RSS feed
* Pagination support
* Added Skribit support

2.5 (2010-11-20)
==================

* Import from WordPress
* Added some new themes (martyalchin / wide-notmyidea)
* First bug report!
* Linkedin support
* Added a FAQ
* Google Analytics support
* Twitter support
* Use relative URLs, not static ones

2.4 (2010-11-06)
================

* Minor themes changes
* Add Disqus support (so we have comments)
* Another code refactoring
* Added config settings about pages
* Blog entries can also be generated in PDF

2.3 (2010-10-31)
================

* Markdown support

2.2 (2010-10-30)
================

* Prettify output
* Manages static pages as well

2.1 (2010-10-30)
================

* Make notmyidea the default theme

2.0 (2010-10-30)
================

* Refactoring to be more extensible
* Change into the setting variables

1.2 (2010-09-28)
================

* Added a debug option
* Added per-category feeds
* Use filesystem to get dates if no metadata is provided
* Add Pygments support

1.1 (2010-08-19)
================

* First working version
