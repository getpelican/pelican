Pelican
#######

Pelican is a simple weblog generator, writen in python.

* Write your weblog entries directly with your editor of choice (vim!) and
  directly in restructured text, or markdown.
* A simple cli-tool to (re)generate the weblog.
* Easy to interface with DVCSes and web hooks
* Completely static output, so easy to host anywhere !

Files metadata
--------------

Pelican tries to be smart enough to get the informations he needs from the
file system (for instance, about the category of your articles), but you need to
provide by hand some of those informations in your files.

You could provide the metadata in the restructured text files, using the
following syntax (give your file the `.rst` extension)::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :tags: thats, awesome
    :category: yeah
    :author: Alexis Metaireau


You can also use a markdown syntax (with a file ending in `.md`)::

    Date: 2010-12-03
    Title: My super title

    Put you content here.

Note that none of those are mandatory: if the date is not specified, pelican will
rely on the mtime of your file, and the category can also be determined by the
directory where the rst file is. For instance, the category of
`python/foobar/myfoobar.rst` is `foobar`.

Features
--------

Pelican currently supports:

* blog articles
* comments, via an external service (disqus). Please notice that while
  it's useful, it's an external service, and you'll not manage the
  comments by yourself. It could potentially eat your data.
* theming support (themes are done using `jinja2 <http://jinjna.pocoo.org>`_)
* PDF generation of the articles/pages (optional).

Getting started — Generate your blog
-------------------------------------

You're ready? Let's go ! You can install pelican in a lot of different ways,
the simpler one is via `pip <http://pip.openplans.org/>`_::

    $ pip install pelican

Then, you have just to launch pelican, like this::

    $ pelican /path/to/your/content/

And… that's all! You can see your weblog generated on the `content/` folder.

This one will just generate a simple output, with the default theme. It's not
really sexy, as it's a simple HTML output (without any style).

You can create your own style if you want, have a look to the help to see all
the options you can use::

    $ pelican --help

Settings
--------

Pelican is configurable thanks a configuration file, that you can pass to
the command line::

    $ pelican -s path/to/your/settingsfile.py path

Here are the available settings. Please note that all the settings you put in
this file will be passed to the templates as well.

=======================   =======================================================
Setting name              what it does ?
=======================   =======================================================
`SITEURL`                 base URL of your website.
`PATH`                    path to look at for input files.
`THEME`                   theme to use to product the output. can be the
                          complete static path to a theme folder, or chosen
                          between the list of default themes (see below)
`OUTPUT_PATH`             Where to output the generated files. Default to
                          "output"
`SITENAME`                Your site name,
`DISPLAY_PAGES_ON_MENU`   Display or not the pages on the menu of the template.
                          Templates can follow or not this settings.
`PDF_PROCESSOR`           Put True if you want to have PDF versions of your
                          documents. You will need to install `rst2pdf`.
`DEFAULT_CATEGORY`        The default category to fallback on. `misc` by default.
`FALLBACK_ON_FS_DATE`     If True, pelican will use the file system dates infos
                          (mtime) if it can't get informations from the
                          metadata?
`MARKUP`                  A list of available markup languages you want to use.
                          moment, only available values are `rst` and `md`.
`STATIC_PATHS`            The static paths you want to have accessible on the
                          output path "static". By default, pelican will copy
                          the 'images' folder to the output folder.
`STATIC_THEME_PATHS`      Static theme paths you want to copy. Default values
                          is `static`, but if your theme have others static paths,
                          you can put them here.
`FEED`                    relative url to output the atom feed. Default is
                          `feeds/all.atom.xml`
`FEED_RSS`                relative url to output the rss feed. Default is
                          None (no rss)
`CATEGORY_FEED`           Where to put the atom categories feeds. default is
                          `feeds/%s.atom.xml`, where %s is the name of the
                          category.
`CATEGORY_FEED_RSS`       Where to put the categories rss feeds. default is None
                          (no rss)
`CSS_FILE`                To specify the CSS file you want to load, if it's not
                          the default one ('main.css')
=======================   =======================================================

Themes
------

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

Why the name "Pelican" ?
------------------------

Heh, you didn't noticed? "Pelican" is an anagram for "Calepin" ;)

Dependencies
------------

At this time, pelican is dependent of the following python packages:

* feedgenerator, to generate the ATOM feeds.
* jinja2, for templating support.
* pygments, to have syntactic colorization
* docutils and Markdown

If you're not using python 2.7, you will also need `argparse`.

All those dependencies will be processed automatically if you install pelican
using setuptools/distribute or pip.

Source code
-----------

You can access the source code via mercurial at http://hg.notmyidea.org/pelican/
or via git on http://github.com/ametaireau/pelican/

If you feel hackish, have a look to the `pelican's internals explanations
<http://alexis.notmyidea.org/pelican/internals.html>`_.


Feedback !
----------

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback !
