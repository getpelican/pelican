How to create themes for pelican
################################

Pelican uses the great `jinja2 <http://jinjna.pocoo.org>`_ templating engine to
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
This document describes which templates should exists on a theme, and which
variables will be passed to each template, while generating it.

All templates will receive the variables defined in your settings file, if they 
are in caps. You can access them directly. 

Common variables
----------------

All of those settings will be given to all templates.

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

This template will be processed for each of the existing categories, and will
finally remain at output/category/`category_name`.html.

=============   ===================================================
Variable        Description
=============   ===================================================
articles        The articles of this category
category        The name of the category being processed
=============   ===================================================

article.html
-------------

This template will be processed for each article. .html files will be outputed
in output/`article_name`.html. Here are the specific variables it gets.

=============   ===================================================
Variable        Description
=============   ===================================================
article         The article object to be displayed
category        The name of the category of the current article
=============   ===================================================

tag.html
--------

For each tag, this template will be processed. It will create .html files in
/output/tag/`tag_name`.html

=============   ===================================================
Variable        Description
=============   ===================================================
tag             The name of the tag being processed
articles        Articles related to this tag
=============   ===================================================
