Pelican
#######

Pelican is a simple weblog generator, writen in python.

* Write your weblog entries directly with your editor of choice (vim!) and
  directly in restructured text, or markdown.
* A simple cli-tool to (re)generate the weblog.
* Easy to interface with DVCSes and web hooks
* Completely static output, so easy to host anywhere !

Files metadatas
---------------

Pelican tries to be smart enough to get the informations he needs from the
filesystem (for instance, about the category of your articles), but you need to
provide by hand some of those informations in your files.

You could provide the metadata in the restructured text files, using the
following syntax (give your file the `.rst` extension)::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :tags: thats, awesome
    :category: yeah
    :author: Alexis Metaireau


You can also use a mardown syntax (with a file ending in `.md`)::

    Date: 2010-12-03
    Title: My super title

    Put you content here.

Note that only the `date` metadata is mandatory, so you just have to add that in i
your files. The category can also be determined by the directory where the rst file
is. For instance, the category of `python/foobar/myfoobar.rst` is `foobar`.

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

Yeah? You're ready? Let's go ! You can install pelican in a lot of different
ways, the simpler one is via pip::

    $ pip install pelican

Then, you have just to launch pelican, like this::

    $ pelican /path/to/your/content/

And… that's all! You can see your weblog generated on the content/ folder.

This one will just generate a simple output, with the default theme. It's not
really sexy, as it's a simple HTML output (without any style). 

You can create your own style if you want, have a look to the help to see all
the options you can use::

    $ pelican --help

Settings
--------

Pelican try to be configurable via a configuration file, that you can pass to
the command line. Here are the settings you can use, with some basic
description.

Please note that all the settings you put in this file will be passed to the
templates as well.

* `PATH` is the path to look at for input files.
* `THEME`: the theme to use to product the output. can be the complete static
  path to a theme folder, or choosed between the default pelican themes (see
  below)
* `OUTPUT_PATH`: Where to output the generated files. Default to "output"
* `SITENAME`: You site name,
* `DISPLAY_PAGES_ON_MENU`: Display or not the pages on the menu of the
  template. Templates can follow or not this settings.
* `PDF_PROCESSOR`: Put True if you want to have PDF outputs as well as HTML
  pages,
* `DEFAULT_CATEGORY`: The default category. `misc` by default.
* `FALLBACK_ON_FS_DATE`: Choose to fallback on filesystem dates informations if
  any other way to retreive the date currrently exists.,
* `MARKUP`: A list of available markup languages you want to use. At the
  moment, only available values are `rst` and `md`.
* `STATIC_PATHS`: The static paths you want to copy under "static"
* `FEED`: url to output the feed.,
* `CATEGORY_FEED`: Where to put the categories feeds. default is `feeds/%s.atom.xml`

Themes
------

3 themes are available. You can specify them using the `-t` option:

* notmyidea
* default
* martylachin 

You can define your own theme too, and specify it's emplacement in the same
way.

The `notmyidea` theme can make good use of the following settings:

* `GITHUB_URL` = your github URL (if you have one)
* `DISQUS_SITENAME` can handle disqus comments
* `LINKS` is a list of tuples Title, Url, for links
* `SOCIAL` (('twitter', 'yourtwitter complete url'),) and any other name/link
  you want to put under "social"

Why the name "Pelican" ?
------------------------

Heh, you didnt noticed? "Pelican" is an anagram for "Calepin" ;)

Dependencies
------------

At this time, pelican is dependent of the following python packages:

* feedgenerator, to generate the ATOM feeds.
* jinja2, for templating support.
* pygments, to have syntactic colorization
* docutils and Markdown

If you're not using python 2.7, you will also need `argparse`.

All those dependencies will be processed automaticaly if you install pelican
using setuptools/distribute or pip.

Source code
-----------

You can access the source code via mercurial at http://hg.notmyidea.org/pelican/
or via git on http://github.com/ametaireau/pelican/

Feedback !
----------

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback !

FAQ
---

Here are some frequently asqued questions.

How do I specify my site URL? I dont want to use the default "/home/…" folder.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure the `SITENAME` to your site base url, let's say
`http://myswebsite.tld`, in your settings file::

    SITENAME = "http://mywebsite.tld"
