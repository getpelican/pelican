Getting started
###############

Installing
==========

You're ready? Let's go! You can install Pelican via several different methods.
The simplest is via `pip <http://www.pip-installer.org/>`_::

    $ pip install pelican

If you don't have pip installed, an alternative method is easy_install::

    $ easy_install pelican

While the above is the simplest method, the recommended approach is to create
a virtual environment for Pelican via `virtualenv <http://www.virtualenv.org/>`_
and `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_
before installing Pelican::

    $ pip install virtualenvwrapper
    $ mkvirtualenv pelican

Once the virtual environment has been created and activated, Pelican can be
be installed via pip or easy_install as noted above. Alternatively, if you
have the project source, you can install Pelican using the distutils 
method::

    $ cd path-to-Pelican-source
    $ python setup.py install

If you have Git installed and prefer to install the latest bleeding-edge
version of Pelican rather than a stable release, use the following command::

    $ pip install -e git://github.com/ametaireau/pelican#egg=pelican

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

To launch Pelican, just use the ``pelican`` command::

    $ pelican /path/to/your/content/ [-s path/to/your/settings.py]

And… that's all! Your weblog will be generated and saved in the ``content/``
folder.

The above command will use the default theme to produce a simple site. It's not
very sexy, as it's just simple HTML output (without any style).

You can create your own style if you want. Have a look at the help to see all
the options you can use::

    $ pelican --help

Kickstart a blog
----------------

You also can use the ``pelican-quickstart`` script to start a new blog in
seconds by just answering a few questions. Just run ``pelican-quickstart`` and
you're done! (Added in Pelican 3.0)

Pages
-----

If you create a folder named ``pages``, all the files in it will be used to
generate static pages.

Then, use the ``DISPLAY_PAGES_ON_MENU`` setting, which will add all the pages to 
the menu.

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

Auto-reload
-----------

It's possible to tell Pelican to watch for your modifications, instead of
manually re-running it every time you want to see your changes. To enable this,
run the ``pelican`` command with the ``-r`` or ``--autoreload`` option.

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

(Tip: If using the latter method in conjunction with the auto-reload feature,
ensure that ``DELETE_OUTPUT_DIRECTORY`` is set to ``False`` in your settings file.)
