Frequently Asked Questions (FAQ)
################################

Here are some frequently asked questions about Pelican.

What's the best way to communicate a problem, question, or suggestion?
======================================================================

If you have a problem, question, or suggestion, please start by striking up a
conversation on `#pelican on Freenode <irc://irc.freenode.net/pelican>`_.
Those who don't have an IRC client handy can jump in immediately via
`IRC webchat <http://webchat.freenode.net/?channels=pelican&uio=d4>`_. Because
of differing time zones, you may not get an immediate response to your question,
but please be patient and stay logged into IRC — someone will almost always
respond.

If you are unable to resolve your issue or if you have a feature request, please
refer to the `issue tracker <https://github.com/getpelican/pelican/issues>`_.

How can I help?
================

There are several ways to help out. First, you can use Pelican and report any
suggestions or problems you might have via IRC or the `issue tracker
<https://github.com/getpelican/pelican/issues>`_.

If you want to contribute, please fork `the git repository
<https://github.com/getpelican/pelican/>`_, create a new feature branch, make
your changes, and issue a pull request. Someone will review your changes as soon
as possible. Please refer to the :doc:`How to Contribute <contribute>` section
for more details.

You can also contribute by creating themes and improving the documentation.

Is it mandatory to have a configuration file?
=============================================

No, it's not. Configuration files are just an easy way to configure Pelican.
For basic operations, it's possible to specify options while invoking Pelican
via the command line. See ``pelican --help`` for more information.

I'm creating my own theme. How do I use Pygments for syntax highlighting?
=========================================================================

Pygments adds some classes to the generated content. These classes are used by
themes to style code syntax highlighting via CSS. Specifically, you can
customize the appearance of your syntax highlighting via the ``.codehilite pre``
class in your theme's CSS file. To see how various styles can be used to render
Django code, for example, you can use the demo `on the project website
<http://pygments.org/demo/15101/>`_.

How do I create my own theme?
==============================

Please refer to :ref:`theming-pelican`.

I want to use Markdown, but I got an error.
===========================================

Markdown is not a hard dependency for Pelican, so you will need to explicitly
install it. You can do so by typing the following, including ``sudo`` if
required::

    (sudo) pip install markdown

If you don't have pip installed, consider installing the pip installer via::

    (sudo) easy_install pip

Can I use arbitrary meta-data in my templates?
==============================================

Yes. For example, to include a modified date in a Markdown post, one could
include the following at the top of the article::

    Modified: 2012-08-08

That meta-data can then be accessed in the template::

    {% if article.modified %}
    Last modified: {{ article.modified }}
    {% endif %}

How do I assign custom templates on a per-page basis?
=====================================================

It's as simple as adding an extra line of metadata to any pages or articles you
want to have its own template.

    :template: template_name

Then just make sure your theme contains the relevant template file (e.g.
``template_name.html``).

What if I want to disable feed generation?
==========================================

To disable all feed generation, all feed settings should be set to ``None``.
All but two feed settings already default to ``None``, so if you want to disable
all feed generation, you only need to specify the following settings::

    FEED_ALL_ATOM = None
    CATEGORY_FEED_ATOM = None

Please note that ``None`` and ``''`` are not the same thing. The word ``None``
should not be surrounded by quotes.

I'm getting a warning about feeds generated without SITEURL being set properly
==============================================================================

`RSS and Atom feeds require all URLs and links in them to be absolute
<http://validator.w3.org/feed/docs/rss2.html#comments>`_.
In order to properly generate all URLs properly in Pelican you will need to set
``SITEURL`` to the full path of your blog. When using ``make html`` and the
default Makefile provided by the `pelican-quickstart` bootstrap script to test
build your site, it's normal to see this warning since ``SITEURL`` is
deliberately left undefined. If configured properly no other ``make`` commands
should result in this warning.

Feeds are still generated when this warning is displayed but may not validate.

My feeds are broken since I upgraded to Pelican 3.x
===================================================

Starting in 3.0, some of the FEED setting names were changed to more explicitly
refer to the Atom feeds they inherently represent (much like the FEED_RSS
setting names). Here is an exact list of the renamed setting names::

    FEED -> FEED_ATOM
    TAG_FEED -> TAG_FEED_ATOM
    CATEGORY_FEED -> CATEGORY_FEED_ATOM

Starting in 3.1, the new feed ``FEED_ALL_ATOM`` has been introduced: this
feed will aggregate all posts regardless of their language. This setting
generates ``'feeds/all.atom.xml'`` by default and ``FEED_ATOM`` now defaults to
``None``. The following feed setting has also been renamed::

    TRANSLATION_FEED -> TRANSLATION_FEED_ATOM

Older themes that referenced the old setting names may not link properly.
In order to rectify this, please update your theme for compatibility by changing
the relevant values in your template files. For an example of complete feed
headers and usage please check out the ``simple`` theme.
