.. _theming-pelican:

How to create themes for Pelican
################################

Pelican uses the great `Jinja2 <http://jinja.pocoo.org/>`_ templating engine to
generate its HTML output. Jinja2 syntax is really simple. If you want to
create your own theme, feel free to take inspiration from the `"simple" theme
<https://github.com/getpelican/pelican/tree/master/pelican/themes/simple/templates>`_.

Structure
=========

To make your own theme, you must follow the following structure::

    ├── static
    │   ├── css
    │   └── images
    └── templates
        ├── archives.html    // to display archives
        ├── article.html     // processed for each article
        ├── author.html      // processed for each author
        ├── authors.html     // must list all the authors
        ├── categories.html  // must list all the categories
        ├── category.html    // processed for each category
        ├── index.html       // the index. List all the articles
        ├── page.html        // processed for each page
        ├── tag.html         // processed for each tag
        └── tags.html        // must list all the tags. Can be a tag cloud.

* `static` contains all the static assets, which will be copied to the output
  `theme` folder. I've put the CSS and image folders here, but they are
  just examples. Put what you need here.

* `templates` contains all the templates that will be used to generate the content.
  I've just put the mandatory templates here; you can define your own if it helps
  you keep things organized while creating your theme.

Templates and variables
=======================

The idea is to use a simple syntax that you can embed into your HTML pages.
This document describes which templates should exist in a theme, and which
variables will be passed to each template at generation time.

All templates will receive the variables defined in your settings file, if they
are in all-caps. You can access them directly.

Common variables
----------------

All of these settings will be available to all templates.

=============   ===================================================
Variable        Description
=============   ===================================================
articles        The list of articles, ordered descending by date
                All the elements are `Article` objects, so you can
                access their attributes (e.g. title, summary, author
                etc.)
dates           The same list of articles, but ordered by date,
                ascending
tags            A list of (tag, articles) tuples, containing all
                the tags.
categories      A list of (category, articles) tuples, containing
                all the categories.
                and the list of respective articles (values)
pages           The list of pages
=============   ===================================================

index.html
----------

This is the home page of your blog, generated at output/index.html.

If pagination is active, subsequent pages will reside in output/index`n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
articles_paginator      A paginator object for the list of articles
articles_page           The current page of articles
dates_paginator         A paginator object for the article list, ordered by
                        date, ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               'index' -- useful for pagination links
===================     ===================================================

author.html
-------------

This template will be processed for each of the existing authors, with
output generated at output/author/`author_name`.html.

If pagination is active, subsequent pages will reside as defined by setting
AUTHOR_SAVE_AS (`Default:` output/author/`author_name'n'`.html).

===================     ===================================================
Variable                Description
===================     ===================================================
author                  The name of the author being processed
articles                Articles by this author
dates                   Articles by this author, but ordered by date,
                        ascending
articles_paginator      A paginator object for the list of articles
articles_page           The current page of articles
dates_paginator         A paginator object for the article list, ordered by
                        date, ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               AUTHOR_URL where everything after `{slug}` is
                        removed -- useful for pagination links
===================     ===================================================

category.html
-------------

This template will be processed for each of the existing categories, with
output generated at output/category/`category_name`.html.

If pagination is active, subsequent pages will reside as defined by setting
CATEGORY_SAVE_AS (`Default:` output/category/`category_name'n'`.html).

===================     ===================================================
Variable                Description
===================     ===================================================
category                The name of the category being processed
articles                Articles for this category
dates                   Articles for this category, but ordered by date,
                        ascending
articles_paginator      A paginator object for the list of articles
articles_page           The current page of articles
dates_paginator         A paginator object for the list of articles,
                        ordered by date, ascending
dates_page              The current page of articles, ordered by date,
                        ascending
page_name               CATEGORY_URL where everything after `{slug}` is
                        removed -- useful for pagination links
===================     ===================================================

article.html
-------------

This template will be processed for each article, with .html files saved
as output/`article_name`.html. Here are the specific variables it gets.

=============   ===================================================
Variable        Description
=============   ===================================================
article         The article object to be displayed
category        The name of the category for the current article
=============   ===================================================

page.html
---------

This template will be processed for each page, with corresponding .html files
saved as output/`page_name`.html.

=============   ===================================================
Variable        Description
=============   ===================================================
page            The page object to be displayed. You can access its
                title, slug, and content.
=============   ===================================================

tag.html
--------

This template will be processed for each tag, with corresponding .html files
saved as output/tag/`tag_name`.html.

If pagination is active, subsequent pages will reside as defined in setting
TAG_SAVE_AS (`Default:` output/tag/`tag_name'n'`.html).

===================     ===================================================
Variable                Description
===================     ===================================================
tag                     The name of the tag being processed
articles                Articles related to this tag
dates                   Articles related to this tag, but ordered by date,
                        ascending
articles_paginator      A paginator object for the list of articles
articles_page           The current page of articles
dates_paginator         A paginator object for the list of articles,
                        ordered by date, ascending
dates_page              The current page of articles, ordered by date,
                        ascending
page_name               TAG_URL where everything after `{slug}` is removed
                        -- useful for pagination links
===================     ===================================================

Feeds
=====

The feed variables changed in 3.0. Each variable now explicitly lists ATOM or
RSS in the name. ATOM is still the default. Old themes will need to be updated.
Here is a complete list of the feed variables::

    FEED_ATOM
    FEED_RSS
    FEED_ALL_ATOM
    FEED_ALL_RSS
    CATEGORY_FEED_ATOM
    CATEGORY_FEED_RSS
    TAG_FEED_ATOM
    TAG_FEED_RSS
    TRANSLATION_FEED_ATOM
    TRANSLATION_FEED_RSS


Inheritance
===========

Since version 3.0, Pelican supports inheritance from the ``simple`` theme, so
you can re-use the ``simple`` theme templates in your own themes.

If one of the mandatory files in the ``templates/`` directory of your theme is
missing, it will be replaced by the matching template from the ``simple`` theme.
So if the HTML structure of a template in the ``simple`` theme is right for you,
you don't have to write a new template from scratch.

You can also extend templates from the ``simple`` themes in your own themes by using the ``{% extends %}`` directive as in the following example:

.. code-block:: html+jinja

    {% extends "!simple/index.html" %}   <!-- extends the ``index.html`` template from the ``simple`` theme -->

    {% extends "index.html" %}   <!-- "regular" extending -->


Example
-------

With this system, it is possible to create a theme with just two files.

base.html
"""""""""

The first file is the ``templates/base.html`` template:

.. code-block:: html+jinja

    {% extends "!simple/base.html" %}

    {% block head %}
    {{ super() }}
       <link rel="stylesheet" type="text/css" href="{{ SITEURL }}/theme/css/style.css" />
    {% endblock %}


1.    On the first line, we extend the ``base.html`` template from the ``simple`` theme, so we don't have to rewrite the entire file.
2.    On the third line, we open the ``head`` block which has already been defined in the ``simple`` theme.
3.    On the fourth line, the function ``super()`` keeps the content previously inserted in the ``head`` block.
4.    On the fifth line, we append a stylesheet to the page.
5.    On the last line, we close the ``head`` block.

This file will be extended by all the other templates, so the stylesheet will be linked from all pages.

style.css
"""""""""

The second file is the ``static/css/style.css`` CSS stylesheet:

.. code-block:: css

    body {
        font-family : monospace ;
        font-size : 100% ;
        background-color : white ;
        color : #111 ;
        width : 80% ;
        min-width : 400px ;
        min-height : 200px ;
        padding : 1em ;
        margin : 5% 10% ;
        border : thin solid gray ;
        border-radius : 5px ;
        display : block ;
    }

    a:link    { color : blue ; text-decoration : none ;      }
    a:hover   { color : blue ; text-decoration : underline ; }
    a:visited { color : blue ;                               }

    h1 a { color : inherit !important }
    h2 a { color : inherit !important }
    h3 a { color : inherit !important }
    h4 a { color : inherit !important }
    h5 a { color : inherit !important }
    h6 a { color : inherit !important }

    pre {
        margin : 2em 1em 2em 4em ;
    }

    #menu li {
        display : inline ;
    }

    #post-list {
        margin-bottom : 1em ;
        margin-top : 1em ;
    }

Download
""""""""

You can download this example theme :download:`here <_static/theme-basic.zip>`.
