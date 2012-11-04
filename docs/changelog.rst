Release history
###############

3.1 (XXXX-XX-XX)
================

* Improve handling of links to intra-site resources
* Ensure WordPress import adds paragraphs in for all types of line endings
  in post content.

3.0 (2012-08-08)
==================

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

* Import from Wordpress
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
