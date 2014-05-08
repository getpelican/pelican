Tutorial 1: Blogging with Pelican
#################################

Installing Pelican
==================

The installation of Pelican is already covered in the Getting Started section, see
:ref:`installing_pelican`.

Initial Setup
=============

We're going to assume that you've followed the instructions in :ref:`installing_pelican`.
Time to create our blog!

First of all, we need to create a place on our filesystem to hold the blog.
We'll use a directory called ``blog`` in our home directory to begin with::

    $ mkdir ~/blog
    $ cd ~/blog

Once that's done you can use a helper script to initialise the
basiscs of our blog for us. Answer the questions to your liking::

    $ pelican-quickstart

This should result in a directory layout identical to this::

    $ tree .
    .
    ├── Makefile
    ├── content
    ├── develop_server.sh
    ├── output
    ├── pelicanconf.py
    └── publishconf.py

Don't worry too much about those files, we'll get to them in due time.

Makefile
--------

The ``Makefile`` contains a few commands that you can execute to generate your blog, upload it
or run a local development server so you can see what you're writing.

Execute ``make`` on the command line to get a complete listing::

    $ make
    Makefile for a pelican Web site

    Usage:
       make html                        (re)generate the web site
       make clean                       remove the generated files
       make regenerate                  regenerate files upon modification
       make publish                     generate using production settings
       make serve                       serve site at http://localhost:8000
       make devserver                   start/restart develop_server.sh
       ssh_upload                       upload the web site via SSH
       rsync_upload                     upload the web site via rsync+ssh
       dropbox_upload                   upload the web site via Dropbox
       ftp_upload                       upload the web site via FTP
       github                           upload the web site via gh-pages

content
-------

Content is a directory that will contain all your blog posts, extra's, pages,
images and anything else that is needed for your site, except the theme.

develop_server.sh
-----------------

This script will start a server listening on http://localhost:8000 where you
can preview your blog. It will automatically regenerate your blog every time
it detects that a file was written.

This is a very useful tool when you're writing your blog posts or developing
a theme::

    $ make devserver
    $ ./develop_server.sh stop

output
------

This directory is where all the generated content will go, basically holding
the HTML, CSS, Javascript and images that are going to make up your site.

You will need to upload the contents of this directory to your webhost.

pelicanconf.py
--------------

This file holds all the Pelican configuration settings for your blog. After
having run through ``pelican-quickstart`` it will look something like this::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*- #

    AUTHOR = u'Adam'
    SITENAME = u'Men are from mars'
    SITEURL = ''

    TIMEZONE = 'Europe/Paris'

    DEFAULT_LANG = u'en'

    # Blogroll
    LINKS =  (('Pelican', 'http://docs.notmyidea.org/alexis/pelican/'),
              ('Python.org', 'http://python.org'),
              ('Jinja2', 'http://jinja.pocoo.org'),
              ('You can modify those links in your config file', '#'),)

    # Social widget
    SOCIAL = (('You can add links in your config file', '#'),
              ('Another social link', '#'),)

    DEFAULT_PAGINATION = 10

publishconf.py
--------------

Since you might want different settings for cetrain configuration items when
publishing your site online any setting in ``pelicanconf.py`` can be overriden
or appended to in this file.

It should look something like this::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*- #

    import sys
    sys.path.append('.')
    from pelicanconf import *

    SITEURL = 'blog.example.com'

    DELETE_OUTPUT_DIRECTORY = True

    # Following items are often useful when publishing

    # Uncomment following line for absolute URLs in production:
    RELATIVE_URLS = False

    #DISQUS_SITENAME = ""
    #GOOGLE_ANALYTICS = ""

As you can see, we're already overriding ``SITEURL``. We've also explicitly
uncommented ``RELATIVE_URLS``. This is because locally we want 
relative URL's but when published on the internet it's best to have
absolute URL's. 

This is also very important for RSS/Atom feeds since those need to be addressed
through absolute URL's.

Concluding
----------

This is all you need to get you blogging with Pelican. In the next section
we'll cover writing our first blog post and generating the site.


Blogging
========

Now that we're all set up it's time to start blogging with Pelican. This
is a four step process:

1. Write our blogpost;
2. Preview our site;
3. Generate our content;
4. Upload it.

... Rinse, repeat, profit!

Create a post
-------------

You can write posts in two ways, using `Markdown` or `reStructuredText` as a markup
language. Pelican works fine with both, this is purely a matter of preference.

For the rest of this tutorial we'll be using `Markdown` but when necessary we'll
show the `reStructuredText`'s equivalent.

Finding content
^^^^^^^^^^^^^^^

First things first, we need to tell Pelican where to actually find our content.
This is controlled by two settings named ``PATH`` and ``ARTICLE_DIR``, the latter
being relative to the former. You can set them up in ``pelicanconf.py`` like this:

.. code-block:: python

    PATH = 'content/'
    ARTICLE_DIR = 'posts/'


Writing content
^^^^^^^^^^^^^^^

Time to write a post. Pelican expects `Makrdown` files to end in ``.md`` and
`reStructuredText` files to end in ``.rst``.

.. code-block:: console

    $ mkdir -p content/posts
    $ vim content/posts/2013-03-25-my-first-post.md

In `Markdown` a post looks something like this::

    Title: My first post
    Author: Adam
    Slug: my-first-post
    Date: 2013-03-25 10:20
    Category: blog
    Summary: Short version for index and feeds
    Tags: pelican, awesome

    .... Write some text ....

The part that starts with ``Title`` and ends with a newline after ``Tags`` is
metadata about our blog post. Most of it can be ommitted and Pelican will use
it's defaults to handle it.

The metadata section looks slightly different in `reStructuredText`::

    My first post
    ##############

    :author: Adam
    :slug: my-super-post
    :date: 2013-03-25 10:20
    :category: blog
    :summary: Short version for index and feeds
    :tags: pelican, awesome

    .... Write some text ....


If you want to get to know the `Markdown` or `reStructured` text formats,
how you can use links, lists, headings and so forth there is plenty
documentation available on the internet.

Posting a draft
^^^^^^^^^^^^^^^

If you'd like to publish an article but not have it visible to everyone
just yet you can mark it as a draft. It will get generated and uploaded
with the rest of your content but there will be no links pointing to it.

Just add one more line of metadata:

* Markdown::

   Status: draft 

* reStructuredText::

    :status: draft


Preview site
------------

So, we've written our first post, time to have a look at it::

    $ make devserver
    /home/adam/blog/develop_server.sh restart
    SimpleHTTPServer PIDFile not found
    Pelican PIDFile not found
    Starting up Pelican and SimpleHTTPServer
    Serving HTTP on 0.0.0.0 port 8000 ...
    WARNING: Since feed URLs should always be absolute, you should specify FEED_DOMAIN in your settings. (e.g., 'FEED_DOMAIN = http://www.example.com')
    WARNING: Feeds generated without SITEURL set properly may not be valid

Now point your browser at http://localhost:8000 and voila, your blog with your
first post!

As you can see Pelican comes out of the box with a pretty decent theme though
you're free to switch to any one you like. Have a look at :ref:`theming-pelican`.

Generate content
----------------

Once your satisfied with your blog post and how your site looks it's time to
upload it to your webhost.

First off, stop the development server::

    $ ./develop_server.sh stop

Clean up everything it has left behind::

    $ make clean
    find /home/adam/blog/output -mindepth 1 -delete

Generate everything with production settings::

    $ make publish

This will now have populated the ``output/`` directory with everything you
need, all that remains to do is upload your site!

Feeds
=====

By default Pelican only generates `Atom` feeds but it's very easy to enable
the generation of `RSS` feeds as well.

.. code-block:: python

    FEED_ALL_RSS          = 'feeds/all.rss.xml'
    CATEGORY_FEED_RSS     = 'feeds/%s.rss.xml'
    TRANSLATION_FEED_ATOM = 'feeds/all-%s.atom.xml'
    TRANSLATION_FEED_RSS  = 'feeds/all-%s.rss.xml'

You can also enable feeds for tags:

.. code-block:: python

    TAG_FEED_ATOM = 'feeds/tag-%s.atom.xml'
    TAG_FEED_RSS  = 'feeds/tag-%s.rss.xml'

Images & static content
=======================

Sometimes you need to use images in blog posts or have other files that you
want added to your blog and uploaded. Pelican can handle this too!

Images & media
--------------

Any file in ``content/images`` will automatically be picked up on by Pelican
and will be available in your site at ``/static/images``.

Pelican also has a ``STATIC_PATHS`` setting where you can add any other
directories that should be hanled like the ``images`` dircetory::

    STATIC_PATHS = [
        'images',
        'videos',
    ]

Files
-----

For other files, such as a ``robots.txt`` or the ``CNAME`` file needed for
Github Pages we can configure the ``FILES_TO_COPY`` setting in ``pelicanconf.py``::

    FILES_TO_COPY = (
        ('extra/CNAME', 'CNAME'),
    )

This will copy the file ``CNAME`` from ``content/extra/CNAME`` to ``output/CNAME``.


Pretty URL's
============

Pelican's defaults when it comes to how it saves files to disk and the URL's
that are eventually generated aren't perfect. By default Pelican generates
URL's that look like this::

    http://blog.example.com/my-first-post.html

On your filesystem it will look like::

    output/my-first-post.html

Some people prefer URL's without a 'file type' added to them and generally
also like to have the date in the URL when it concerns blog posts. 
This can be achieved by overriding some of Pelican's settings in ``pelicanconf.py``:

.. code-block:: python

    ARTICLE_URL          = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
    ARTICLE_SAVE_AS      = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
    ARTICLE_LANG_URL     = 'posts/{lang}/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
    ARTICLE_LANG_SAVE_AS = 'posts/{lang}/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

This will result in URL's that look like this::

    http://blog.example.com/posts/2013/03/25/my-first-post

On your filesystem it will look similar::

    output/posts/2013/03/25/my-first-post/index.html

By turning ``slug`` into a folder and then writing to an ``index.html`` we
trigger most webservers default behaviour of serving the ``index.html`` when
accessing a folder which gives us exactly what we want.

You can apply that same trick to change how URL's are generated for tags,
categories, pages and authors:

.. code-block:: python

    PAGE_URL          = 'pages/{slug}'
    PAGE_SAVE_AS      = 'pages/{slug}/index.html'
    PAGE_LANG_URL     = 'pages/{lang}/{slug}'
    PAGE_LANG_SAVE_AS = 'pages/{lang}/{slug}/index.html'
    AUTHOR_URL        = 'author/{slug}'
    AUTHOR_SAVE_AS    = 'author/{slug}/index.html'
    CATEGORY_URL      = 'category/{slug}'
    CATEGORY_SAVE_AS  = 'category/{slug}/index.html'
    TAG_URL           = 'tag/{slug}'
    TAG_SAVE_AS       = 'tag/{slug}/index.html'

Plugins
=======

Pelican provides plugins you can use to further enhance your site.

Two plugins which anyone should enable are:

* Sitemap
* Gzip Cache

Then there's also `Typogrify` which provides typesetting enhancements that
make your content look nicer.

Sitemap
-------

Building a sitemap makes it easier for search sites to index your sites and
also provides search sites with indications on how often they need to check
your site for new content.

To enable it, add this to ``pelicanconf.py``::

    PLUGINS = [
        'pelican.plugins.sitemap',
    ]

Now a sitemap will be generated together with the rest of your content.  

For furthre configuration of the `sitemap` plugin have a look at :ref:`plugins`.

Gzip Cache
----------

This plugin makes sure that when content is generated it is also compressed
through the use of ``gzip``. Most webservers are set up to serve gzip-compressed
content if it's available which will also make your site load faster client side.

Since this is only ever useful in production we're going to load this plugin
only when generating content for publishing.

To do this, add this to ``publishconf.py``::

    PLUGINS += [
        'pelican.plugins.gzip_cache'
    ]

Note the usage of ``+=``, we're appending to the plugins which we inherit from
``pelicanconf.py``, not overriding them.

Typogrify
---------

Before you can use Typogrify you actualy need to install it::

    $ pip install typogrify

Typogrify isn't a plugin that is loaded like the others, it just has one
setting in ``pelicanconf.py`` that controls it::

    TYPOGRIFY = True

Switch it from ``False`` to ``True``, regenerate your content and decide
for yourself wether to enable or disable it.
