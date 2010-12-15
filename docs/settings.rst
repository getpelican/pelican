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

Here are the available settings. Please note that all the settings you put in
this file will be passed to the templates as well.

=======================   =======================================================
Setting name              what it does ?
=======================   =======================================================
`AUTHOR`                  Default author (put your name)
`CATEGORY_FEED`           Where to put the atom categories feeds. default is
                          `feeds/%s.atom.xml`, where %s is the name of the
                          category.
`CATEGORY_FEED_RSS`       Where to put the categories rss feeds. default is None
                          (no rss)
`CSS_FILE`                To specify the CSS file you want to load, if it's not
                          the default one ('main.css')
`DEFAULT_CATEGORY`        The default category to fallback on. `misc` by default.
`DISPLAY_PAGES_ON_MENU`   Display or not the pages on the menu of the template.
                          Templates can follow or not this settings.
`FALLBACK_ON_FS_DATE`     If True, pelican will use the file system dates infos
                          (mtime) if it can't get informations from the
                          metadata?
`FEED`                    relative url to output the atom feed. Default is
                          `feeds/all.atom.xml`
`FEED_RSS`                relative url to output the rss feed. Default is
                          None (no rss)
`KEEP_OUTPUT_DIRECTORY`   Keep the output directory and just update all the generated files. 
                          Default is to delete the output directory.   
`MARKUP`                  A list of available markup languages you want to use.
                          moment, only available values are `rst` and `md`.
`OUTPUT_PATH`             Where to output the generated files. Default to
                          "output"
`PATH`                    path to look at for input files.
`PDF_PROCESSOR`           Put True if you want to have PDF versions of your
                          documents. You will need to install `rst2pdf`.
`REVERSE_ARCHIVE_ORDER`   Reverse the archives order. (True makes it in
                          descending order: the newer first)
`SITEURL`                 base URL of your website.
`SITENAME`                Your site name,
`STATIC_PATHS`            The static paths you want to have accessible on the
                          output path "static". By default, pelican will copy
                          the 'images' folder to the output folder.
`STATIC_THEME_PATHS`      Static theme paths you want to copy. Default values
                          is `static`, but if your theme have others static paths,
                          you can put them here.
`THEME`                   theme to use to product the output. can be the
                          complete static path to a theme folder, or chosen
                          between the list of default themes (see below)
=======================   =======================================================

Themes
======

3 themes are available. You can specify them using the `-t` option:

* notmyidea
* simple (a synonym for "full text" :)
* martyalchin

You can define your own theme too, and specify it's emplacement in the same
way (be sure to specify the full absolute path to it).

Here is `a guide on how to create your theme
<http://alexis.notmyidea.org/pelican/themes.html>`_

The `notmyidea` theme can make good use of the following settings. I recommend
to use them too in your themes.

=======================   =======================================================
Setting name              what it does ?
=======================   =======================================================
`GITHUB_URL`              Your github URL (if you have one), it will then
                          use it to create a github ribbon.
`DISQUS_SITENAME`         Pelican can handle disqus comments, specify the
                          sitename you've filled in on disqus
`LINKS`                   A list of tuples (Title, Url) for links to appear on
                          the header.
`SOCIAL`                  A list of tuples (Title, Url) to appear in the "social"
                          section.
`GOOGLE_ANALYTICS`        'UA-XXXX-YYYY' to activate google analytics.
=======================   =======================================================

In addition, you can use the "wide" version of the `notmyidea` theme, by
adding that in your configuration::

    CSS_FILE = "wide.css"
