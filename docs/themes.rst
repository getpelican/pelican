How to create themes for pelican
################################

Pelican uses the great `jinja2 <http://jinjna.pocoo.org>`_ templating engine to
generate it's HTML output.

Structure
=========

To make your own theme, you must follow the following structure::

    ├── static
    │   ├── css
    │   └── images
    └── templates
        ├── archives.html
        ├── article.html
        ├── categories.html
        ├── category.html
        ├── index.html
        ├── page.html
        ├── tag.html
        └── tags.html

* `static` contains all the static content. It will be copied on the output
  `theme/static` folder then. I've put the css and image folders, but they are
  just examples. Put what you need here.

* `templates` contains all the templates that will be used to generate the content.
  I've just put the mandatory templates here, you can define your own if it helps 
  you to organize yourself while doing the theme.
 
Templates and variables
=======================

It's using a simple syntax, that you can embbed into your html pages.
This document describes which templates should exists on a theme, and which
variables will be passed to each template, while generating it.

All templates will receive the variables defined in your settings file, if they 
are in caps. You can access them directly. 

Common variables
----------------

=============   ===================================================
Variable        Description
=============   ===================================================
articles        That's the list of articles, ordsered desc. by date
                all the elements are `Article` objects, so you can 
                access their properties (e.g. title, summary, author
                etc. 
dates           The same list of article, but ordered by date,
                ascending
tags            A dict containing each tags (keys), and the list of
                relative articles.
categories      A dict containing each category (keys), and the 
                list of relative articles.
pages           The list of pages
=============   ===================================================

category.html
-------------

=============   ===================================================
Variable        Description
=============   ===================================================
articles        The articles of this category
category        The name of the category being processed
=============   ===================================================

article.html
-------------

=============   ===================================================
Variable        Description
=============   ===================================================
article         The article object to be displayed
category        The name of the category of the current article
=============   ===================================================

tag.html
--------

=============   ===================================================
Variable        Description
=============   ===================================================
tag             The name of the tag being processed
articles        Articles related to this tag
=============   ===================================================
