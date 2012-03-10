Settings
########

Pelican is configurable thanks to a configuration file you can pass to
the command line::

    $ pelican -s path/to/your/settingsfile.py path

Settings are configured in the form of a Python module (a file). You can see an
example by looking at `/samples/pelican.conf.py
<https://github.com/ametaireau/pelican/raw/master/samples/pelican.conf.py>`_

All the setting identifiers must be set in all-caps, otherwise they will not be
processed.

The settings you define in the configuration file will be passed to the
templates, which allows you to use your settings to add site-wide content.

Here is a list of settings for Pelican:

Basic settings
==============

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`AUTHOR`                                            Default author (put your name)
`DATE_FORMATS` (``{}``)                             If you do manage multiple languages, you can
                                                    set the date formatting here. See "Date format and locales"
                                                    section below for details.
`DEFAULT_CATEGORY` (``'misc'``)                     The default category to fall back on.
`DEFAULT_DATE_FORMAT` (``'%a %d %B %Y'``)           The default date format you want to use.
`DISPLAY_PAGES_ON_MENU` (``True``)                  Whether to display pages on the menu of the
                                                    template. Templates may or not honor this
                                                    setting.
`FALLBACK_ON_FS_DATE` (``True``)                    If True, Pelican will use the file system
                                                    timestamp information (mtime) if it can't get
                                                    date information from the metadata.
`JINJA_EXTENSIONS` (``[]``)                         A list of any Jinja2 extensions you want to use.
`DELETE_OUTPUT_DIRECTORY` (``False``)               Delete the output directory as well as
                                                    the generated files.
`LOCALE` (''[#]_)                                   Change the locale. A list of locales can be provided 
                                                    here or a single string representing one locale.
                                                    When providing a list, all the locales will be tried 
                                                    until one works.
`MARKUP` (``('rst', 'md')``)                        A list of available markup languages you want
                                                    to use. For the moment, the only available values
                                                    are `rst` and `md`.
`MD_EXTENSIONS` (``('codehilite','extra')``)        A list of the extensions that the Markdown processor
                                                    will use. Refer to the extensions chapter in the
                                                    Python-Markdown documentation for a complete list of
                                                    supported extensions.
`OUTPUT_PATH` (``'output/'``)                       Where to output the generated files.
`PATH` (``None``)                                   Path to look at for input files.
`PDF_GENERATOR` (``False``)                         Set to True if you want to have PDF versions
                                                    of your documents. You will need to install
                                                    `rst2pdf`.
`RELATIVE_URLS` (``True``)                          Defines whether Pelican should use relative URLs or
                                                    not.
`SITENAME` (``'A Pelican Blog'``)                   Your site name
`SITEURL`                                           Base URL of your website. Note that this is
                                                    not a way to tell Pelican whether to use relative URLs
                                                    or static ones. You should instead use the
                                                    `RELATIVE_URL` setting for that purpose.
`STATIC_PATHS` (``['images']``)                     The static paths you want to have accessible
                                                    on the output path "static". By default,
                                                    Pelican will copy the 'images' folder to the
                                                    output folder.
`TIMEZONE`                                          The timezone used in the date information, to
                                                    generate Atom and RSS feeds. See the "timezone"
                                                    section below for more info.
================================================    =====================================================

.. [#] Default is the system locale.


URL Settings
------------

You can customize the URL's and locations where files will be saved. The URL's and
SAVE_AS variables use python's format strings. These variables allow you to place
your articles in a location such as '{slug}/index.html' and link to then as
'{slug}' for clean urls. These settings give you the flexibility to place your
articles and pages anywhere you want.

Note: If you specify a datetime directive, it will be substituted using the
input files' date metadata attribute. If the date is not specified for a
particular file, Pelican will rely on the file's mtime timestamp.

Check the Python datetime documentation at http://bit.ly/cNcJUC for more
information.

Also, you can use other file metadata attributes as well: 

* slug
* date
* lang
* author
* category

Example usage: 

* ARTICLE_URL = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/'
* ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/index.html'

This would save your articles in something like '/posts/2011/Aug/07/sample-post/index.html',
and the URL to this would be '/posts/2011/Aug/07/sample-post/'.

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`ARTICLE_URL` ('{slug}.html')                       The URL to refer to an ARTICLE.
`ARTICLE_SAVE_AS` ('{slug}.html')                   The place where we will save an article.
`ARTICLE_LANG_URL` ('{slug}-{lang}.html')           The URL to refer to an ARTICLE which doesn't use the
                                                    default language.
`ARTICLE_LANG_SAVE_AS` ('{slug}-{lang}.html'        The place where we will save an article which
                                                    doesn't use the default language.
`PAGE_URL` ('pages/{slug}.html')                    The URL we will use to link to a page.
`PAGE_SAVE_AS` ('pages/{slug}.html')                The location we will save the page.
`PAGE_LANG_URL` ('pages/{slug}-{lang}.html')        The URL we will use to link to a page which doesn't
                                                    use the default language.
`PAGE_LANG_SAVE_AS` ('pages/{slug}-{lang}.html')    The location we will save the page which doesn't
                                                    use the default language.
`AUTHOR_URL` ('author/{name}.html')                 The URL to use for an author.
`AUTHOR_SAVE_AS` ('author/{name}.html')             The location to save an author.
`CATEGORY_URL` ('category/{name}.html')             The URL to use for a category.
`CATEGORY_SAVE_AS` ('category/{name}.html')         The location to save a category.
`TAG_URL` ('tag/{name}.html')                       The URL to use for a tag.
`TAG_SAVE_AS` ('tag/{name}.html')                   The location to save the tag page.
================================================    =====================================================

Timezone
--------

If no timezone is defined, UTC is assumed. This means that the generated Atom
and RSS feeds will contain incorrect date information if your locale is not UTC.

Pelican issues a warning in case this setting is not defined, as it was not
mandatory in previous versions.

Have a look at `the wikipedia page`_ to get a list of valid timezone values.

.. _the wikipedia page: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones


Date format and locale
----------------------

If no DATE_FORMAT is set, fall back to DEFAULT_DATE_FORMAT. If you need to
maintain multiple languages with different date formats, you can set this dict
using language name (``lang`` in your posts) as key. Regarding available format
codes, see `strftime document of python`_ :

    DATE_FORMAT = {
        'en': '%a, %d %b %Y',
        'jp': '%Y-%m-%d(%a)',
    }

You can set locale to further control date format:

    LOCALE = ('usa', 'jpn',  # On Windows
        'en_US', 'ja_JP'     # On Unix/Linux
        )

Also, it is possible to set different locale settings for each language. If you
put (locale, format) tuples in the dict, this will override the LOCALE setting
above:

    # On Unix/Linux
    DATE_FORMAT = {
        'en': ('en_US','%a, %d %b %Y'),
        'jp': ('ja_JP','%Y-%m-%d(%a)'),
    }

    # On Windows
    DATE_FORMAT = {
        'en': ('usa','%a, %d %b %Y'),
        'jp': ('jpn','%Y-%m-%d(%a)'),
    }

This is a list of available `locales on Windows`_ . On Unix/Linux, usually you
can get a list of available locales via the ``locale -a`` command; see manpage
`locale(1)`_ for more information.


.. _strftime document of python: http://docs.python.org/library/datetime.html#strftime-strptime-behavior

.. _locales on Windows: http://msdn.microsoft.com/en-us/library/cdax410z%28VS.71%29.aspx

.. _locale(1): http://linux.die.net/man/1/locale

Feed settings
=============

By default, Pelican uses Atom feeds. However, it is also possible to use RSS
feeds if you prefer.

Pelican generates category feeds as well as feeds for all your articles. It does
not generate feeds for tags by default, but it is possible to do so using
the ``TAG_FEED`` and ``TAG_FEED_RSS`` settings:

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`CATEGORY_FEED` ('feeds/%s.atom.xml'[2]_)           Where to put the category Atom feeds.
`CATEGORY_FEED_RSS` (``None``, i.e. no RSS)         Where to put the category RSS feeds.
`FEED` (``'feeds/all.atom.xml'``)                   Relative URL to output the Atom feed.
`FEED_RSS` (``None``, i.e. no RSS)                  Relative URL to output the RSS feed.
`TAG_FEED` (``None``, ie no tag feed)               Relative URL to output the tag Atom feed. It should
                                                    be defined using a "%s" match in the tag name.
`TAG_FEED_RSS` (``None``, ie no RSS tag feed)       Relative URL to output the tag RSS feed
`FEED_MAX_ITEMS`                                    Maximum number of items allowed in a feed. Feed item
                                                    quantity is unrestricted by default.
================================================    =====================================================

If you don't want to generate some of these feeds, set ``None`` to the
variables above.

.. [2] %s is the name of the category.

Pagination
==========

The default behaviour of Pelican is to list all the article titles along
with a short description on the index page. While it works pretty well
for small-to-medium blogs, for sites with large quantity of articles it would
be convenient to have a way to paginate the list.

You can use the following settings to configure the pagination.

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`DEFAULT_ORPHANS` (0)                               The minimum number of articles allowed on the
                                                    last page. Use this when you don't want to
                                                    have a last page with very few articles.
`DEFAULT_PAGINATION` (False)                        The maximum number of articles to include on a
                                                    page, not including orphans. False to disable
                                                    pagination.
================================================    =====================================================

Tag cloud
=========

If you want to generate a tag cloud with all your tags, you can do so using the
following settings.

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`TAG_CLOUD_STEPS` (4)                               Count of different font sizes in the tag
                                                    cloud.
`TAG_CLOUD_MAX_ITEMS` (100)                         Maximum number of tags in the cloud.
================================================    =====================================================

The default theme does not support tag clouds, but it is pretty easy to add::

    <ul>
        {% for tag in tag_cloud %}
            <li class="tag-{{ tag.1 }}"><a href="/tag/{{ tag.0 }}/">{{ tag.0 }}</a></li>
        {% endfor %}
    </ul>

You should then also define a CSS style with the appropriate classes (tag-0 to tag-N, where
N matches `TAG_CLOUD_STEPS` -1).

Translations
============

Pelican offers a way to translate articles. See the Getting Started section for
more information.

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`DEFAULT_LANG` (``'en'``)                           The default language to use.
`TRANSLATION_FEED` ('feeds/all-%s.atom.xml'[3]_)    Where to put the feed for translations.
================================================    =====================================================

.. [3] %s is the language

Ordering content
=================

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`REVERSE_ARCHIVE_ORDER` (``False``)                 Reverse the archives list order. (True: orders by date
                                                    in descending order, with newer articles first.)
`REVERSE_CATEGORY_ORDER` (``False``)                Reverse the category order. (True: lists by reverse 
                                                    alphabetical order; default lists alphabetically.)
================================================    =====================================================

Theming
=======

Theming is addressed in a dedicated section (see :ref:`theming-pelican`).
However, here are the settings that are related to theming.

================================================    =====================================================
Setting name (default value)                        What does it do?
================================================    =====================================================
`THEME`                                             Theme to use to produce the output. Can be the
                                                    complete static path to a theme folder, or
                                                    chosen between the list of default themes (see
                                                    below)
`THEME_STATIC_PATHS` (``['static']``)               Static theme paths you want to copy. Default
                                                    value is `static`, but if your theme has
                                                    other static paths, you can put them here.
`CSS_FILE` (``'main.css'``)                         Specify the CSS file you want to load.
================================================    =====================================================

By default, two themes are available. You can specify them using the `-t` option:

* notmyidea
* simple (a synonym for "full text" :)

You can define your own theme too, and specify its placement in the same
manner. (Be sure to specify the full absolute path to it.)

Here is `a guide on how to create your theme
<http://pelican.notmyidea.org/en/latest/themes.html>`_

You can find a list of themes at http://github.com/ametaireau/pelican-themes.

Pelican comes with :doc:`pelican-themes`, a small script for managing themes.

The `notmyidea` theme can make good use of the following settings. I recommend
using them in your themes as well.

=======================   =======================================================
Setting name              What does it do ?
=======================   =======================================================
`DISQUS_SITENAME`         Pelican can handle Disqus comments. Specify the
                          Disqus sitename identifier here.
`GITHUB_URL`              Your GitHub URL (if you have one). It will then
                          use this information to create a GitHub ribbon.
`GOOGLE_ANALYTICS`        'UA-XXXX-YYYY' to activate Google Analytics.
`MENUITEMS`               A list of tuples (Title, URL) for additional menu
                          items to appear at the beginning of the main menu.
`PIWIK_URL`               URL to your Piwik server - without 'http://' at the
                          beginning.
`PIWIK_SSL_URL`           If the SSL-URL differs from the normal Piwik-URL
                          you have to include this setting too. (optional)
`PIWIK_SITE_ID`           ID for the monitored website. You can find the ID
                          in the Piwik admin interface > settings > websites.
`LINKS`                   A list of tuples (Title, URL) for links to appear on
                          the header.
`SOCIAL`                  A list of tuples (Title, URL) to appear in the
                          "social" section.
`TWITTER_USERNAME`        Allows for adding a button to articles to encourage
                          others to tweet about them. Add your Twitter username
                          if you want this button to appear.
=======================   =======================================================

In addition, you can use the "wide" version of the `notmyidea` theme by
adding the following to your configuration::

    CSS_FILE = "wide.css"

.. _pelican-themes: :doc:`pelican-themes`

Example settings
================

.. literalinclude:: ../samples/pelican.conf.py
    :language: python
