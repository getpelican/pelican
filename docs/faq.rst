Frequently Asked Questions (FAQ)
################################

Here are some frequently asked questions about Pelican.

What's the best way to communicate a problem, question, or suggestion?
======================================================================

Please read our :doc:`feedback guidelines <contribute>`.

How can I help?
===============

There are several ways to help out. First, you can communicate any Pelican
suggestions or problems you might have via `Pelican Discussions
<https://github.com/getpelican/pelican/discussions>`_. Please first check the
existing list of discussions and issues (both open and closed) in order to
avoid submitting topics that have already been covered before.

If you want to contribute, please fork `the Git repository
<https://github.com/getpelican/pelican/>`_, create a new feature branch, make
your changes, and issue a pull request. Someone will review your changes as
soon as possible. Please refer to the :doc:`How to Contribute <contribute>`
section for more details.

You can also contribute by creating themes and improving the documentation.

Is the Pelican settings file mandatory?
=======================================

Configuration files are optional and are just an easy way to configure Pelican.
For basic operations, it's possible to specify options while invoking Pelican
via the command line. See ``pelican --help`` for more information.

Changes to the settings file take no effect
===========================================

When experimenting with different settings (especially the metadata ones)
caching may interfere and the changes may not be visible. In such cases, ensure
that caching is disabled via ``LOAD_CONTENT_CACHE = False`` or use the
``--ignore-cache`` command-line switch.

I'm creating my own theme. How do I use Pygments for syntax highlighting?
=========================================================================

Pygments adds some classes to the generated content. These classes are used by
themes to style code syntax highlighting via CSS. Specifically, you can
customize the appearance of your syntax highlighting via the ``.highlight pre``
class in your theme's CSS file. To see how various styles can be used to render
Django code, for example, use the style selector drop-down at top-right on the
`Pygments project demo site <https://pygments.org/demo/>`_.

You can use the following example commands to generate a starting CSS file from
a Pygments built-in style (in this case, "monokai") and then copy the generated
CSS file to your new theme::

    pygmentize -S monokai -f html -a .highlight > pygment.css
    cp pygment.css path/to/theme/static/css/

Don't forget to import your ``pygment.css`` file from your main CSS file.

How do I create my own theme?
=============================

Please refer to :ref:`theming-pelican`.

Can I override individual templates without forking the whole theme?
====================================================================

Yes, you can override existing templates of the theme that you are using, or
add new templates, via the ``THEME_TEMPLATES_OVERRIDES`` variable. For example,
to override the page template, you can define the location for your templates
like this::

    THEME_TEMPLATES_OVERRIDES = ["templates"]

You can then define a custom template in ``templates/page.html``.
See :ref:`settings/themes` for details.

I want to use Markdown, but I got an error.
===========================================

If you try to generate Markdown content without first installing the Markdown
library, you may see a message that says ``No valid files found in content``.
Markdown is not a hard dependency for Pelican, so if you have content in
Markdown format, you will need to explicitly install the Markdown library. You
can do so by typing the following command, prepending ``sudo`` if permissions
require it::

    python -m pip install markdown

Can I use arbitrary metadata in my templates?
=============================================

Yes. For example, to include a modified date in a Markdown post, one could
include the following at the top of the article::

    Modified: 2012-08-08

For reStructuredText, this metadata should of course be prefixed with a colon::

    :Modified: 2012-08-08

This metadata can then be accessed in templates such as ``article.html`` via::

    {% if article.modified %}
    Last modified: {{ article.modified }}
    {% endif %}

If you want to include metadata in templates outside the article context (e.g.,
``base.html``), the ``if`` statement should instead be::

    {% if article and article.modified %}

How do I make my output folder structure identical to my content hierarchy?
===========================================================================

Try these settings::

    USE_FOLDER_AS_CATEGORY = False
    PATH_METADATA = "(?P<path_no_ext>.*)\..*"
    ARTICLE_URL = ARTICLE_SAVE_AS = PAGE_URL = PAGE_SAVE_AS = "{path_no_ext}.html"

How do I assign custom templates on a per-page basis?
=====================================================

It's as simple as adding an extra line of metadata to any page or article that
you want to have its own template. For example, this is how it would be handled
for content in reST format::

    :template: template_name

For content in Markdown format::

    Template: template_name

Then just make sure your theme contains the relevant template file (e.g.
``template_name.html``). If you just want to add a new custom template to an
existing theme, you can also provide it in a directory specified by ``THEME_TEMPLATES_OVERRIDES`` (see :ref:`settings/themes`).

How can I override the generated URL of a specific page or article?
===================================================================

Include ``url`` and ``save_as`` metadata in any pages or articles that you want
to override the generated URL. Here is an example page in reST format::

    Override url/save_as page
    #########################

    :url: override/url/
    :save_as: override/url/index.html

With this metadata, the page will be written to ``override/url/index.html``
and Pelican will use the URL ``override/url/`` to link to this page.

How can I use a static page as my home page?
============================================

The override feature mentioned above can be used to specify a static page as
your home page. The following Markdown example could be stored in
``content/pages/home.md``::

    Title: Welcome to My Site
    URL:
    save_as: index.html

    Thank you for visiting. Welcome!

If the original blog index is still wanted, it can then be saved in a
different location by setting ``INDEX_SAVE_AS = 'blog_index.html'`` for
the ``'index'`` direct template.

What if I want to disable feed generation?
==========================================

To disable feed generation, all feed settings should be set to ``None``. All
but three feed settings already default to ``None``, so if you want to disable
all feed generation, you only need to specify the following settings::

    FEED_ALL_ATOM = None
    CATEGORY_FEED_ATOM = None
    TRANSLATION_FEED_ATOM = None
    AUTHOR_FEED_ATOM = None
    AUTHOR_FEED_RSS = None

The word ``None`` should not be surrounded by quotes. Please note that ``None``
and ``''`` are not the same thing.

I'm getting a warning about feeds generated without SITEURL being set properly
==============================================================================

`RSS and Atom feeds require all URL links to be absolute
<https://validator.w3.org/feed/docs/rss2.html#comments>`_. In order to properly
generate links in Pelican you will need to set ``SITEURL`` to the full path of
your site.

Feeds are still generated when this warning is displayed, but links within may
be malformed and thus the feed may not validate.

Can I force Atom feeds to show only summaries instead of article content?
=========================================================================

Instead of having to open a separate browser window to read articles, the
overwhelming majority of folks who use feed readers prefer to read content
within the feed reader itself. Mainly for that reason, Pelican does not support
restricting Atom feeds to only contain summaries. Unlike Atom feeds, the RSS
feed specification does not include a separate ``content`` field, so by default
Pelican publishes RSS feeds that only contain summaries (but can optionally be
set to instead publish full content RSS feeds). So the default feed generation
behavior provides users with a choice: subscribe to Atom feeds for full content
or to RSS feeds for just the summaries.

Is Pelican only suitable for blogs?
===================================

No. Pelican can be easily configured to create and maintain any type of static
site. This may require a little customization of your theme and Pelican
configuration. For example, if you are building a launch site for your product
and do not need tags on your site, you could remove the relevant HTML code from
your theme. You can also disable generation of tag-related pages via::

    TAGS_SAVE_AS = ''
    TAG_SAVE_AS = ''

Why does Pelican always write all HTML files even with content caching enabled?
===============================================================================

In order to reliably determine whether the HTML output is different before
writing it, a large part of the generation environment including the template
contexts, imported plugins, etc. would have to be saved and compared, at least
in the form of a hash (which would require special handling of unhashable
types), because of all the possible combinations of plugins, pagination, etc.
which may change in many different ways. This would require a lot more
processing time and memory and storage space. Simply writing the files each
time is a lot faster and a lot more reliable.

However, this means that the modification time of the files changes every time,
so a ``rsync`` based upload will transfer them even if their content hasn't
changed. A simple solution is to make ``rsync`` use the ``--checksum`` option,
which will make it compare the file checksums in a much faster way than Pelican
would.

How to process only a subset of all articles?
=============================================

It is often useful to process only e.g. 10 articles for debugging purposes.
This can be achieved by explicitly specifying only the filenames of those
articles in ``ARTICLE_PATHS``. A list of such filenames could be found using a
command similar to ``cd content; find -name '*.md' | head -n 10``.

My tag cloud is missing/broken since I upgraded Pelican
=======================================================

In an ongoing effort to streamline Pelican, tag cloud generation has been
moved out of Pelican core and into a separate `plugin
<https://github.com/pelican-plugins/tag-cloud>`_. See the :ref:`plugins`
documentation for further information about the Pelican plugin system.

Since I upgraded Pelican my pages are no longer rendered
========================================================

Pages were available to themes as lowercase ``pages`` and uppercase ``PAGES``.
To bring this inline with the :ref:`templates-variables` section, ``PAGES`` has
been removed. This is quickly resolved by updating your theme to iterate over
``pages`` instead of ``PAGES``. Just replace::

    {% for pg in PAGES %}

with something like::

    {% for pg in pages %}

How can I stop Pelican from trying to parse my static files as content?
=======================================================================

Pelican's article and page generators run before it's static generator. That
means if you use a setup similar to the default configuration, where a static
source directory is defined inside a ``*_PATHS`` setting, all files that have a
valid content file ending (``.html``, ``.rst``, ``.md``, ...) will be treated
as articles or pages before they get treated as static files.

To circumvent this issue either use the appropriate ``*_EXCLUDES`` setting or
disable the offending reader via ``READERS`` if you don't need it.

Why is [arbitrary Markdown syntax] not supported?
=================================================

Pelican does not directly handle Markdown processing and instead delegates that
task to the Python-Markdown_ project, the core of which purposefully follows
the original Markdown syntax rules and not the myriad Markdown "flavors" that
have subsequently propagated. That said, Python-Markdown_ is quite modular, and
the syntax you are looking for may be provided by one of the many available
`Markdown Extensions`_. Alternatively, some folks have created Pelican plugins
that support Markdown variants, so that may be your best choice if there is a
particular variant you want to use when writing your content.


.. _Python-Markdown: https://github.com/Python-Markdown/markdown
.. _Markdown Extensions: https://python-markdown.github.io/extensions/
