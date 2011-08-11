Settings
########

Pelican is configurable thanks to a configuration file you can pass to
the command line::

    $ pelican -s path/to/your/settingsfile.py path

Settings are given as the form of a python module (a file). You can have an
example by looking at `/samples/pelican.conf.py
<https://github.com/ametaireau/pelican/raw/master/samples/pelican.conf.py>`_

All the settings identifiers must be set in caps, otherwise they will not be
processed.

The settings you define in the configuration file will be passed to the
templates, it allows you to use them to add site-wide contents if you need.

Here is a list of settings for pelican, regarding the different features.

Basic settings
==============

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`AUTHOR`                                            Default author (put your name)
`SITENAME` (``'A Pelican Blog'``)                   Your site name
`DATE_FORMATS` (``{}``)                             If you do manage multiple languages, you can
                                                    set the date formatting here.
`DEFAULT_CATEGORY` (``'misc'``)                     The default category to fallback on.
`DEFAULT_DATE_FORMAT` (``'%a %d %B %Y'``)           The default date format you want to use.
`DISPLAY_PAGES_ON_MENU` (``True``)                  Display or not the pages on the menu of the
                                                    template. Templates can follow or not this
                                                    settings.
`FALLBACK_ON_FS_DATE` (``True``)                    If True, pelican will use the file system
                                                    dates infos (mtime) if it can't get
                                                    informations from the metadata
`JINJA_EXTENSIONS` (``[]``)                         A list of any Jinja2 extensions you want to use.
`DELETE_OUTPUT_DIRECTORY` (``False``)               Delete the output directory and just
                                                    the generated files.
`LOCALE` (''[1]_)                                   Change the locale. A list of locales can be provided 
                                                    here or a single string representing one locale.
                                                    When providing a list, all the locales will be tried 
                                                    until one works.
`MARKUP` (``('rst', 'md')``)                        A list of available markup languages you want
                                                    to use. For the moment, only available values
                                                    are `rst` and `md`.
`MD_EXTENSIONS` (``('codehilite','extra')``)        A list of the extensions that the markdown processor
                                                    will use. Refer to the extensions chapter in the
                                                    Python-Markdown documentation for a complete list of
                                                    supported extensions.
`OUTPUT_PATH` (``'output/'``)                       Where to output the generated files.
`PATH` (``None``)                                   path to look at for input files.
`PDF_GENERATOR` (``False``)                         Set to True if you want to have PDF versions
                                                    of your documents. You will need to install
                                                    `rst2pdf`.
`RELATIVE_URLS` (``True``)                          Defines if pelican should use relative urls or
                                                    not.
`SITEURL`                                           base URL of your website. Note that this is
                                                    not a way to tell pelican to use relative urls
                                                    or static ones. You should rather use the
                                                    `RELATIVE_URL` setting for such use.
`STATIC_PATHS` (``['images']``)                     The static paths you want to have accessible
                                                    on the output path "static". By default,
                                                    pelican will copy the 'images' folder to the
                                                    output folder.
`ARTICLE_PERMALINK_STRUCTURE` (``''``)              Empty by default. Allows to render URLs for 
                                                    articles sorted by date, in case you specify a 
                                                    format as specified in the example.
                                                    It follows the python datetime directives:
                                                     * %Y: Year with century as a decimal number.
                                                     * %m: Month as a decimal number [01,12].
                                                     * %d: Day of the month as a decimal number [01,31].

                                                     Note: if you specify a datetime directive, it will
                                                     be substituted using the date metadata field into 
                                                     the rest file. if the date is not specified, pelican
                                                     will rely on the mtime of your file.

                                                     Check the python datetime documentation 
                                                     at http://bit.ly/cNcJUC for more information.
                                                    
                                                    Also, you can use any metadata in the 
                                                    restructured text files:
                                                     * category: '%(category)s'
                                                     * author: '%(author)s'
                                                     * tags: '%(tags)s'
                                                     * date: '%(date)s'

                                                    Example usage:
                                                     * '/%Y/%m/' it will be something like 
                                                       '/2011/07/sample-post.html'.
                                                     * '/%Y/%(category)s/' it will be something like
                                                       '/2011/life/sample-post.html'.
================================================    =====================================================


.. [1] Default is the system locale. Default is to delete the output directory.

Feed settings
=============

By default, pelican uses atom feeds. However, it is possible to use RSS feeds
instead, at your covenience.

Pelican generates category feeds as well as feeds for all your articles. It does
not generate feeds for tags per default, but it is possible to do so using
the ``TAG_FEED`` and ``TAG_FEED_RSS`` settings:


================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`CATEGORY_FEED` ('feeds/%s.atom.xml'[2]_)           Where to put the atom categories feeds.
`CATEGORY_FEED_RSS` (``None``, i.e. no RSS)         Where to put the categories rss feeds.
`FEED` (``'feeds/all.atom.xml'``)                   relative url to output the atom feed.
`FEED_RSS` (``None``, i.e. no RSS)                  relative url to output the rss feed.
`TAG_FEED` (``None``, ie no tag feed)               relative url to output the tags atom feed. It should
                                                    be defined using a "%s" matchin the tag name
`TAG_FEED_RSS` (``None``, ie no RSS tag feed)       relative url to output the tag RSS feed
`FEED_MAX_ITEMS`                                    Maximum number of items allowed in a feed. Feeds are
                                                    unrestricted by default.
================================================    =====================================================

.. [2] %s is the name of the category.

Pagination
==========

The default behaviour of pelican is to list all the articles titles alongside
with a short description of them on the index page. While it works pretty well
for little to medium blogs, it is convenient to have a way to paginate this.

You can use the following settings to configure the pagination.

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`DEFAULT_ORPHANS` (0)                               The minimum number of articles allowed on the
                                                    last page. Use this when you don't want to
                                                    have a last page with very few articles.
`DEFAULT_PAGINATION` (5)                            The maximum number of articles to include on a
                                                    page, not including orphans.
`WITH_PAGINATION` (``False``)                       Activate pagination.
================================================    =====================================================

Tag cloud
=========

If you want to generate a tag cloud with all your tags, you can do so using the
following settings.

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`TAG_CLOUD_STEPS` (4)                               Count of different font sizes in the tag
                                                    cloud.
`TAG_CLOUD_MAX_ITEMS` (100)                         Maximum tags count in the cloud.
================================================    =====================================================

The default theme does not support tag clouds, but it is pretty easy to add::

    <ul>
        {% for tag in tag_cloud %}
            <li class="tag-{{ tag.1 }}"><a href="/tag/{{ tag.0 }}/">{{ tag.0 }}</a></li>
        {% endfor %}
    </ul>

You should then also define a CSS with the appropriate classes (tag-0 to tag-N, where
N matches `TAG_CLOUD_STEPS` -1.

Translations
============

Pelican offers a way to translate articles. See the section on getting started for
more information about that.

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`DEFAULT_LANG` (``'en'``)                           The default language to use.
`TRANSLATION_FEED` ('feeds/all-%s.atom.xml'[3]_)    Where to put the RSS feed for translations.
================================================    =====================================================

.. [3] %s is the language

Ordering contents
=================

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`REVERSE_ARCHIVE_ORDER` (``False``)                 Reverse the archives order. (True makes it in
                                                    descending order: the newer first)
`REVERSE_CATEGORY_ORDER` (``False``)                Reverse the category order. (True makes it in
                                                    descending order, default is alphabetically)
================================================    =====================================================

Theming
=======

Theming is addressed in a dedicated section (see :ref:`theming-pelican`).
However, here are the settings that are related to theming.

================================================    =====================================================
Setting name (default value)                        what does it do?
================================================    =====================================================
`THEME`                                             theme to use to produce the output. can be the
                                                    complete static path to a theme folder, or
                                                    chosen between the list of default themes (see
                                                    below)
`THEME_STATIC_PATHS` (``['static']``)               Static theme paths you want to copy. Default
                                                    values is `static`, but if your theme has
                                                    other static paths, you can put them here.
`CSS_FILE` (``'main.css'``)                         specify the CSS file you want to load
================================================    =====================================================

By default, two themes are availablee. You can specify them using the `-t` option:

* notmyidea
* simple (a synonym for "full text" :)

You can define your own theme too, and specify it's emplacement in the same
way (be sure to specify the full absolute path to it).

Here is `a guide on how to create your theme
<http://alexis.notmyidea.org/pelican/themes.html>`_

You can find a list of themes at http://github.com/ametaireau/pelican-themes.

Pelican comes with :doc:`pelican-themes` a small script for managing themes.

The `notmyidea` theme can make good use of the following settings. I recommend
to use them too in your themes.

=======================   =======================================================
Setting name              what does it do ?
=======================   =======================================================
`DISQUS_SITENAME`         Pelican can handle disqus comments, specify the
                          sitename you've filled in on disqus
`GITHUB_URL`              Your github URL (if you have one), it will then
                          use it to create a github ribbon.
`GOOGLE_ANALYTICS`        'UA-XXXX-YYYY' to activate google analytics.
`PIWIK_URL`               URL to your Piwik server - without 'http://' at the
                          beginning.
`PIWIK_SSL_URL`           If the SSL-URL differs from the normal Piwik-URL
                          you have to include this setting too. (optional)
`PIWIK_SITE_ID`           ID for the monitored website. You can find the ID
                          in the Piwik admin interface > settings > websites.
`LINKS`                   A list of tuples (Title, Url) for links to appear on
                          the header.
`SOCIAL`                  A list of tuples (Title, Url) to appear in the "social"
                          section.
`TWITTER_USERNAME`        Allows to add a button on the articles to tweet about
                          them. Add you twitter username if you want this
                          button to appear.
=======================   =======================================================

In addition, you can use the "wide" version of the `notmyidea` theme, by
adding that in your configuration::

    CSS_FILE = "wide.css"

.. _pelican-themes: :doc:`pelican-themes`

Example settings
================

.. literalinclude:: ../samples/pelican.conf.py
    :language: python
