.. _theming-pelican:

How to create themes for pelican
################################

Pelican uses the great `jinja2 <http://jinja.pocoo.org>`_ templating engine to
generate it's HTML output. The jinja2 syntax is really simple. If you want to
create your own theme, feel free to take inspiration from the "simple" theme,
which is available `here
<https://github.com/ametaireau/pelican/tree/master/pelican/themes/simple/templates>`_

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

* `static` contains all the static content. It will be copied on the output
  `theme/static` folder then. I've put the css and image folders, but they are
  just examples. Put what you need here.

* `templates` contains all the templates that will be used to generate the content.
  I've just put the mandatory templates here, you can define your own if it helps
  you to organize yourself while doing the theme.
 
Templates and variables
=======================

It's using a simple syntax, that you can embbed into your html pages.
This document describes which templates should exist on a theme, and which
variables will be passed to each template, while generating it.

All templates will receive the variables defined in your settings file, if they
are in caps. You can access them directly. 

Common variables
----------------

All of those settings will be given to all templates.

=============   ===================================================
Variable        Description
=============   ===================================================
articles        That's the list of articles, ordered desc. by date
                all the elements are `Article` objects, so you can 
                access their properties (e.g. title, summary, author
                etc.).
dates           The same list of article, but ordered by date,
                ascending.
tags            A dict containing each tags (keys), and the list of
                relative articles.
categories      A dict containing each category (keys), and the 
                list of relative articles.
pages           The list of pages.
=============   ===================================================

index.html
----------

Home page of your blog, will finally remain at output/index.html.

If pagination is active, next pages will remain at output/index`n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
articles_paginator      A paginator object of article list.
articles_page           The current page of articles.
dates_paginator         A paginator object of article list, ordered by date,
                        ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               'index'. Useful for pagination links.
===================     ===================================================

author.html
-------------

This template will be processed for each of the existing authors, and will
finally remain at output/author/`author_name`.html.

If pagination is active, next pages will remain at
output/author/`author_name``n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
author                  The name of the author being processed.
articles                Articles of this author.
dates                   Articles of this author, but ordered by date,
                        ascending.
articles_paginator      A paginator object of article list.
articles_page           The current page of articles.
dates_paginator         A paginator object of article list, ordered by date,
                        ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               'author/`author_name`'. Useful for pagination
                        links.
===================     ===================================================

category.html
-------------

This template will be processed for each of the existing categories, and will
finally remain at output/category/`category_name`.html.

If pagination is active, next pages will remain at
output/category/`category_name``n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
category                The name of the category being processed.
articles                Articles of this category.
dates                   Articles of this category, but ordered by date,
                        ascending.
articles_paginator      A paginator object of article list.
articles_page           The current page of articles.
dates_paginator         A paginator object of article list, ordered by date,
                        ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               'category/`category_name`'. Useful for pagination
                        links.
===================     ===================================================

article.html
-------------

This template will be processed for each article. .html files will be output
in output/`article_name`.html. Here are the specific variables it gets.

=============   ===================================================
Variable        Description
=============   ===================================================
article         The article object to be displayed.
category        The name of the category of the current article.
=============   ===================================================

page.html
---------

For each page, this template will be processed. It will create .html files in
output/`page_name`.html.

=============   ===================================================
Variable        Description
=============   ===================================================
page            The page object to be displayed. You can access to
                its title, slug and content.
=============   ===================================================

tag.html
--------

For each tag, this template will be processed. It will create .html files in
output/tag/`tag_name`.html.

If pagination is active, next pages will remain at
output/tag/`tag_name``n`.html.

===================     ===================================================
Variable                Description
===================     ===================================================
tag                     The name of the tag being processed.
articles                Articles related to this tag.
dates                   Articles related to this tag, but ordered by date,
                        ascending.
articles_paginator      A paginator object of article list.
articles_page           The current page of articles.
dates_paginator         A paginator object of article list, ordered by date,
                        ascending.
dates_page              The current page of articles, ordered by date,
                        ascending.
page_name               'tag/`tag_name`'. Useful for pagination links.
===================     ===================================================

Include skribit script
======================

In order to support skribit scripts in your themes, you must perform these
actions:

 * Copy `skribit_tab_script.html` and `skribit_widget_script.html` in your
   templates directory.
 * Add {% include 'skribit_tab_script.html' %} in your <head> part in order to
   support suggestions tab.
 * Add {% include 'skribit_widget_script.html' %} where you want in order to
   support sidebar widget.

You can take a look at notmyidea default theme for working example.


Inheritance
===========

The last version of Pelican supports inheritance from the ``simple`` theme, so you can reuse the templates of the ``simple`` theme in your own themes:

If one of the mandatory files in the ``templates/`` directory of your theme is missing, it will be replaced by the corresponding template from the ``simple`` theme, so if the HTML structure of a template of the ``simple`` theme is right for you, you don't have to rewrite it from scratch.

You can also extend templates of the ``simple`` themes in your own themes by using the ``{% extends %}`` directove as in the following example:

.. code-block:: html+jinja

    {% extends "!simple/index.html" %}   <!-- extends the ``index.html`` template of the ``simple`` theme -->

    {% extends "index.html" %}   <!-- "regular" extending -->


Example
-------

With this system, it is possible to create a theme with just two file.

base.html
"""""""""

The first file is the ``templates/base.html`` template:

.. code-block:: html+jinja

    {% extends "!simple/base.html" %}

    {% block head %}
    {{ super() }}
       <link rel="stylesheet" type="text/css" href="{{ SITEURL }}/theme/css/style.css" />
    {% endblock %}


1.    On the first line, we extends the ``base.html`` template of the ``simple`` theme, so we don't have to rewrite the entire file.
2.    On the third line, we open the ``head`` block, that has already been defined in the ``simple`` theme
3.    On the fourth line, the function ``super()`` keeps the content previously inserted in the ``head`` block.
4.    On the fifth line, we append a stylesheet to the page
5.    On the last line, we close the ``head`` block.

This file will be extended by all the others templates, so the stylesheet will be included in all pages.

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
