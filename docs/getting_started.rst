Getting started
###############

Installing Pelican
==================

You're ready? Let's go! You can install Pelican via several different methods.
The simplest is via `pip <http://www.pip-installer.org/>`_::

    $ pip install pelican

If you don't have ``pip`` installed, an alternative method is ``easy_install``::

    $ easy_install pelican

While the above is the simplest method, the recommended approach is to create
a virtual environment for Pelican via `virtualenv <http://www.virtualenv.org/>`_
and `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_
before installing Pelican::

    $ sudo pip install --upgrade virtualenv virtualenvwrapper

Note that virtualenvwrapper, being a shell hack, usually requires that a new shell
be started in order to be sourced. Continue -perhaps in a new shell::

    $ mkvirtualenv pelican
    $ pip install pelican

Once the virtual environment has been created and activated, Pelican can be
be installed via ``pip`` or ``easy_install`` as noted above. Alternatively, if
you have the project source, you can install Pelican using the distutils 
method::

    $ cd path-to-Pelican-source
    $ python setup.py install

If you have Git installed and prefer to install the latest bleeding-edge
version of Pelican rather than a stable release, use the following command::

    $ pip install -e git://github.com/getpelican/pelican#egg=pelican

If you plan on using Markdown as a markup format, you'll need to install the
Markdown library as well::

    $ pip install Markdown

Upgrading
---------

If you installed a stable Pelican release via pip or easy_install and wish to
upgrade to the latest stable release, you can do so by adding ``--upgrade`` to
the relevant command. For pip, that would be::

    $ pip install --upgrade pelican

If you installed Pelican via distutils or the bleeding-edge method, simply
perform the same step to install the most recent version.

Dependencies
------------

At this time, Pelican is dependent on the following Python packages:

* feedgenerator, to generate the Atom feeds
* jinja2, for templating support
* docutils, for supporting reStructuredText as an input format

If you're not using Python 2.7, you will also need the ``argparse`` package.

Optionally:

* pygments, for syntax highlighting
* Markdown, for supporting Markdown as an input format

Kickstart a blog
================

Following is a brief tutorial for those who want to get started right away.
We're going to assume Pelican was installed in a virtual environment via the
following steps (if you're not using a virtual environment for Pelican, you can
skip to the ``pelican-quickstart`` command)::

    $ sudo pip install --upgrade virtualenv virtualenvwrapper
    $ mkvirtualenv pelican
    $ pip install pelican Markdown

Next we'll create a directory to house our site content and configuration files,
which can be located any place you prefer, and associate this new project with
the currently-active virtual environment::

    $ mkdir ~/code/yoursitename
    $ cd ~/code/yoursitename
    $ setvirtualenvproject

Now we can run the ``pelican-quickstart`` command, which will ask some questions
about your site::

    $ pelican-quickstart

Once you finish answering all the questions, you can begin adding content to the
*content* folder that has been created for you. (See *Writing articles using
Pelican* section below for more information about how to format your content.)
Once you have some content to generate, you can convert it to HTML via the
following command::

    $ make html

If you'd prefer to have Pelican automatically regenerate your site every time a
change is detected (handy when testing locally), use the following command
instead::

    $ make regenerate

To serve the site so it can be previewed in your browser at
http://localhost:8000::

    $ make serve

Normally you would need to run ``make regenerate`` and ``make serve`` in two
separate terminal sessions, but you can run both at once via::

    $ make devserver

The above command will simultaneously run Pelican in regeneration mode as well
as serve the output at http://localhost:8000. Once you are done testing your
changes, you should stop the development server via::

    $ ./develop_server stop

When you're ready to publish your site, you can upload it via the method(s) you
chose during the ``pelican-quickstart`` questionnaire. For this example, we'll
use rsync over ssh::

    $ make rsync_upload

That's it! Your site should now be live.

Writing articles using Pelican
==============================

File metadata
--------------

Pelican tries to be smart enough to get the information it needs from the
file system (for instance, about the category of your articles), but some
information you need to provide in the form of metadata inside your files.

You can provide this metadata in reStructuredText text files via the
following syntax (give your file the ``.rst`` extension)::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :tags: thats, awesome
    :category: yeah
    :author: Alexis Metaireau

Pelican implements an extension of reStructuredText to enable support for the
``abbr`` HTML tag. To use it, write something like this in your post::

    This will be turned into :abbr:`HTML (HyperText Markup Language)`.

You can also use Markdown syntax (with a file ending in ``.md``).
Markdown generation will not work until you explicitly install the ``Markdown``
package, which can be done via ``pip install Markdown``. Metadata syntax for
Markdown posts should follow this pattern::

    Date: 2010-12-03
    Title: My super title
    Tags: thats, awesome
    Slug: my-super-post

    This is the content of my super blog post.

Note that, aside from the title, none of this metadata is mandatory: if the date
is not specified, Pelican will rely on the file's "mtime" timestamp, and the
category can be determined by the directory in which the file resides. For
example, a file located at ``python/foobar/myfoobar.rst`` will have a category of
``foobar``.

Generate your blog
------------------

The ``make`` shortcut commands mentioned in the ``Kickstart a blog`` section
are mostly wrappers around the ``pelican`` command that generates the HTML from
the content. The ``pelican`` command can also be run directly::

    $ pelican /path/to/your/content/ [-s path/to/your/settings.py]

The above command will generate your weblog and save it in the ``content/``
folder, using the default theme to produce a simple site. The default theme is
simple HTML without styling and is provided so folks may use it as a basis for
creating their own themes.

Pelican has other command-line switches available. Have a look at the help to
see all the options you can use::

    $ pelican --help

Auto-reload
-----------

It's possible to tell Pelican to watch for your modifications, instead of
manually re-running it every time you want to see your changes. To enable this,
run the ``pelican`` command with the ``-r`` or ``--autoreload`` option.

Pages
-----

If you create a folder named ``pages``, all the files in it will be used to
generate static pages.

Then, use the ``DISPLAY_PAGES_ON_MENU`` setting, which will add all the pages to 
the menu.

If you want to exclude any pages from being linked to or listed in the menu
then add a ``status: hidden`` attribute to its metadata. This is useful for
things like making error pages that fit the generated theme of your site.

Importing an existing blog
--------------------------

It is possible to import your blog from Dotclear, WordPress, and RSS feeds using 
a simple script. See :ref:`import`.

Translations
------------

It is possible to translate articles. To do so, you need to add a ``lang`` meta
attribute to your articles/pages and set a ``DEFAULT_LANG`` setting (which is
English [en] by default). With those settings in place, only articles with the
default language will be listed, and each article will be accompanied by a list
of available translations for that article.

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

Syntax highlighting
---------------------

Pelican is able to provide colorized syntax highlighting for your code blocks.
To do so, you have to use the following conventions (you need to put this in
your content files).

For RestructuredText::

    .. code-block:: identifier

       your code goes here

For Markdown, format your code blocks thusly::

    :::identifier
    your code goes here

The specified identifier should be one that appears on the 
`list of available lexers <http://pygments.org/docs/lexers/>`_.

Publishing drafts
-----------------

If you want to publish an article as a draft (for friends to review before
publishing, for example), you can add a ``status: draft`` attribute to its
metadata. That article will then be output to the ``drafts`` folder and not
listed on the index page nor on any category page.

Viewing the generated files
---------------------------

The files generated by Pelican are static files, so you don't actually need
anything special to see what's happening with the generated files.

You can either use your browser to open the files on your disk::

    $ firefox output/index.html

Or run a simple web server using Python::

    cd output && python -m SimpleHTTPServer

