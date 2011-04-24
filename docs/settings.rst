Settings
########

Specifying the settings
=======================

Pelican is configurable thanks to a configuration file, that you can pass to
the command line::

    $ pelican -s path/to/your/settingsfile.py path

Settings are given as the form of a python module (a file). You can have an
example by looking at `/samples/pelican.conf.py
<https://github.com/ametaireau/pelican/raw/master/samples/pelican.conf.py>`_

All the settings identifiers must be set in caps, otherwise they will not be
processed.

Here are the available settings. Please note that all the settings you put in
this file will be passed to the templates as well.


========================    =======================================================
Setting name                what it does ?
========================    =======================================================
`AUTHOR`                    Default author (put your name)
`CATEGORY_FEED`             Where to put the atom categories feeds. default is
                            `feeds/%s.atom.xml`, where %s is the name of the
                            category.
`CATEGORY_FEED_RSS`         Where to put the categories rss feeds. default is None
                            (no rss)
`CSS_FILE`                  To specify the CSS file you want to load, if it's not
                            the default one ('main.css')
`DATE_FORMATS`              If you do manage multiple languages, you can set
                            the date formatting here.
`DEFAULT_CATEGORY`          The default category to fallback on. `misc` by default.
`DEFAULT_DATE_FORMAT`       The default date format you want to use.
`DEFAULT_LANG`              The default language to use. Default is 'en'.
`DEFAULT_ORPHANS`           The minimum number of articles allowed on the last
                            page, defaults to zero. Use this when you don't want
                            to have a last page with very few articles.
`DEFAULT_PAGINATION`        The maximum number of articles to include on a page,
                            not including orphans. Default is 5.
`DISPLAY_PAGES_ON_MENU`     Display or not the pages on the menu of the template.
                            Templates can follow or not this settings.
`FALLBACK_ON_FS_DATE`       If True, pelican will use the file system dates infos
                            (mtime) if it can't get informations from the
                            metadata?
`FEED`                      relative url to output the atom feed. Default is
                            `feeds/all.atom.xml`
`FEED_RSS`                  relative url to output the rss feed. Default is
                            None (no rss)
`JINJA_EXTENSIONS`          A list of any Jinja2 extensions you want to use.
                            Default is no extensions (the empty list).
`KEEP_OUTPUT_DIRECTORY`     Keep the output directory and just update all the 
                            generated files. 
`LOCALE`                    Change the locale. Default is the system locale.
                            Default is to delete the output directory.   
`MARKUP`                    A list of available markup languages you want to use.
                            For the moment, only available values are `rst` and `md`.
`OUTPUT_PATH`               Where to output the generated files. Default to
                            "output"
`PATH`                      path to look at for input files.
`PDF_PROCESSOR`             Put True if you want to have PDF versions of your
                            documents. You will need to install `rst2pdf`.
`RELATIVE_URL`              Defines if pelican should use relative urls or not.
                            It is set to True per default.
`REVERSE_ARCHIVE_ORDER`     Reverse the archives order. (True makes it in
                            descending order: the newer first)
`REVERSE_CATEGORY_ORDER`    Reverse the category order. (True makes it in
                            descending order, default is alphabetically)
`SITEURL`                   base URL of your website. Note that this is not
                            a way to tell pelican to use relative urls or
                            static ones. You should rather use the `RELATIVE_URL`
                            setting for such use.
`SITENAME`                  Your site name,
`SKRIBIT_TYPE`              The type of skribit widget (TAB or WIDGET).
`SKRIBIT_TAB_COLOR`         Tab color (#XXXXXX, default #333333).
`SKRIBIT_TAB_HORIZ`         Tab Distance from Left (% or distance, default Null).
`SKRIBIT_TAB_VERT`          Tab Distance from Top (% or distance, default 20%).
`SKRIBIT_TAB_PLACEMENT`     Tab placement (Top, Bottom, Left or Right, default
                            LEFT).
`SKRIBIT_TAB_SITENAME`      Tab identifier (See Skribit part below).
`SKRIBIT_WIDGET_ID`         Widget identifier (See Skribit part below).
`STATIC_PATHS`              The static paths you want to have accessible on the
                            output path "static". By default, pelican will copy
                            the 'images' folder to the output folder.
`STATIC_THEME_PATHS`        Static theme paths you want to copy. Default values
                            is `static`, but if your theme have others static paths,
                            you can put them here.
`TAG_CLOUD_STEPS`           Count of different font sizes in the tag cloud.
`TAG_CLOUD_MAX_ITEMS`       Maximum tags count in the cloud.
`THEME`                     theme to use to product the output. can be the
                            complete static path to a theme folder, or chosen
                            between the list of default themes (see below)
`TRANSLATION_FEED`          Where to put the RSS feed for translations. Default
                            is feeds/all-%s.atom.xml where %s is the name of the
                            lang.
`WITH_PAGINATION`           Activate pagination. Default is False.
========================    =======================================================

Skribit
=======

Skribit has two ways to display suggestions : as a sidebar widget or as a
suggestions tab. You can choose one of the display by setting the SKRIBIT_TYPE
in your config.

Sidebar widget
--------------

The settings for sidebar widget is :

 * SKRIBIT_WIDGET_ID : the identifier of your blog.

All the customizations are done in the skribit web interface.

To retrieve your identifier from the code snippet, you can use this python code::

    import re
    regex = re.compile('.*http://assets.skribit.com/javascripts/SkribitWidget.\
        js\?renderTo=writeSkribitHere&amp;blog=(.*)&amp;.*')
    snippet = '''SNIPPET CONTENT'''
    snippet = snippet.replace('\n', '')
    identifier = regex.match(snippet).groups()[0]

Suggestion tab
--------------

The setting for suggestion tab's customizations are :

 * SKRIBIT_TAB_COLOR
 * SKRIBIT_TAB_DISTANCE_HORIZ
 * SKRIBIT_TAB_DISTANCE_VERT
 * SKRIBIT_TAB_PLACEMENT

The identifier is :

 * SKRIBIT_TAB_SITENAME : the identifier of your blog

To retrieve your sitename from the code snippet, you can use this python code::

    import re
    regex = re.compile('.*http://skribit.com/lightbox/(.*)\',.*')
    snippet = '''SNIPPET CONTENT'''
    snippet = snippet.replace('\n', '')
    identifier = regex.match(snippet).groups()[0]

Themes
======

By default, two themes are availablee. You can specify them using the `-t` option:

* notmyidea
* simple (a synonym for "full text" :)

You can define your own theme too, and specify it's emplacement in the same
way (be sure to specify the full absolute path to it).

Here is `a guide on how to create your theme
<http://alexis.notmyidea.org/pelican/themes.html>`_

You can find a list of themes at http://github.com/ametaireau/pelican-themes.

The `notmyidea` theme can make good use of the following settings. I recommend
to use them too in your themes.

=======================   =======================================================
Setting name              what it does ?
=======================   =======================================================
`DISQUS_SITENAME`         Pelican can handle disqus comments, specify the
                          sitename you've filled in on disqus
`GITHUB_URL`              Your github URL (if you have one), it will then
                          use it to create a github ribbon.
`GOOGLE_ANALYTICS`        'UA-XXXX-YYYY' to activate google analytics.
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
