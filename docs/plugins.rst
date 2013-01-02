.. _plugins:

Plugins
#######

Beginning with version 3.0, Pelican supports plugins. Plugins are a way to add
features to Pelican without having to directly modify the Pelican core.

Pelican is shipped with a set of bundled plugins, but you can easily implement
your own. This page describes how to use and create plugins.

How to use plugins
==================

To load plugins, you have to specify them in your settings file. There are two
ways to do so. The first method is to specify strings with the path to the
callables::

    PLUGINS = ['pelican.plugins.gravatar',]

Alternatively, another method is to import them and add them to the list::

    from pelican.plugins import gravatar
    PLUGINS = [gravatar,]

If your plugins are not in an importable path, you can specify a ``PLUGIN_PATH``
in the settings::

    PLUGIN_PATH = "plugins"
    PLUGINS = ["list", "of", "plugins"]

How to create plugins
=====================

Plugins are based on the concept of signals. Pelican sends signals, and plugins
subscribe to those signals. The list of signals are defined in a subsequent
section.

The only rule to follow for plugins is to define a ``register`` callable, in
which you map the signals to your plugin logic. Let's take a simple example::

    from pelican import signals

    def test(sender):
        print "%s initialized !!" % sender

    def register():
        signals.initialized.connect(test)



List of signals
===============

Here is the list of currently implemented signals:

=============================   ============================   ===========================================================================
Signal                          Arguments                       Description
=============================   ============================   ===========================================================================
initialized                     pelican object
finalized                       pelican object                  invoked after all the generators are executed and just before pelican exits
                                                                usefull for custom post processing actions, such as:
                                                                - minifying js/css assets.
                                                                - notify/ping search engines with an updated sitemap.
generator_init                  generator                       invoked in the Generator.__init__
article_generate_context        article_generator, metadata
article_generate_preread        article_generator               invoked before a article is read in ArticlesGenerator.generate_context;
                                                                use if code needs to do something before every article is parsed
article_generator_init          article_generator               invoked in the ArticlesGenerator.__init__
article_generator_finalized     article_generator               invoked at the end of ArticlesGenerator.generate_context
get_generators                  generators                      invoked in Pelican.get_generator_classes,
                                                                can return a Generator, or several
                                                                generator in a tuple or in a list.
pages_generate_context          pages_generator, metadata
pages_generator_init            pages_generator                 invoked in the PagesGenerator.__init__
=============================   ============================   ===========================================================================

The list is currently small, so don't hesitate to add signals and make a pull
request if you need them!

.. note::

   The signal ``content_object_init`` can send a different type of object as
   the argument. If you want to register only one type of object then you will
   need to specify the sender when you are connecting to the signal.

   ::

       from pelican import signals
       from pelican import contents

       def test(sender, instance):
               print "%s : %s content initialized !!" % (sender, instance)

       def register():
               signals.content_object_init.connect(test, sender=contents.Article)



List of plugins
===============

The following plugins are currently included with Pelican:

* `Asset management`_ ``pelican.plugins.assets``
* `Chronological Links`_ ``pelican.plugins.chronological_links``
* `GitHub activity`_ ``pelican.plugins.github_activity``
* `Global license`_ ``pelican.plugins.global_license``
* `Gravatar`_ ``pelican.plugins.gravatar``
* `Gzip cache`_ ``pelican.plugins.gzip_cache``
* `HTML tags for reStructuredText`_ ``pelican.plugins.html_rst_directive``
* `Related posts`_ ``pelican.plugins.related_posts``
* `Sitemap`_ ``pelican.plugins.sitemap``

Ideas for plugins that haven't been written yet:

* Tag cloud
* Translation

Plugin descriptions
===================

Asset management
----------------

This plugin allows you to use the `Webassets`_ module to manage assets such as
CSS and JS files. The module must first be installed::

    pip install webassets

The Webassets module allows you to perform a number of useful asset management
functions, including:

* CSS minifier (``cssmin``, ``yui_css``, ...)
* CSS compiler (``less``, ``sass``, ...)
* JS minifier (``uglifyjs``, ``yui_js``, ``closure``, ...)

Others filters include gzip compression, integration of images in CSS via data
URIs, and more. Webassets can also append a version identifier to your asset
URL to convince browsers to download new versions of your assets when you use
far-future expires headers. Please refer to the `Webassets documentation`_ for
more information.

When used with Pelican, Webassets is configured to process assets in the
``OUTPUT_PATH/theme`` directory. You can use Webassets in your templates by
including one or more template tags. The Jinja variable ``{{ ASSET_URL }}`` can
be used in templates and is relative to the ``theme/`` url. The
``{{ ASSET_URL }}`` variable should be used in conjunction with the
``{{ SITEURL }}`` variable in order to generate URLs properly. For example:

.. code-block:: jinja

    {% assets filters="cssmin", output="css/style.min.css", "css/inuit.css", "css/pygment-monokai.css", "css/main.css" %}
        <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">
    {% endassets %}

... will produce a minified css file with a version identifier that looks like:

.. code-block:: html

    <link href="http://{SITEURL}/theme/css/style.min.css?b3a7c807" rel="stylesheet">

These filters can be combined. Here is an example that uses the SASS compiler
and minifies the output:

.. code-block:: jinja

    {% assets filters="sass,cssmin", output="css/style.min.css", "css/style.scss" %}
        <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">
    {% endassets %}

Another example for Javascript:

.. code-block:: jinja

    {% assets filters="uglifyjs,gzip", output="js/packed.js", "js/jquery.js", "js/base.js", "js/widgets.js" %}
        <script src="{{ SITEURL }}/{{ ASSET_URL }}"></script>
    {% endassets %}

The above will produce a minified and gzipped JS file:

.. code-block:: html

    <script src="http://{SITEURL}/theme/js/packed.js?00703b9d"></script>

Pelican's debug mode is propagated to Webassets to disable asset packaging
and instead work with the uncompressed assets. However, this also means that
the LESS and SASS files are not compiled. This should be fixed in a future
version of Webassets (cf. the related `bug report
<https://github.com/getpelican/pelican/issues/481>`_).

.. _Webassets: https://github.com/miracle2k/webassets
.. _Webassets documentation: http://webassets.readthedocs.org/en/latest/builtin_filters.html

Chronological Links
-------------------

This plugin allows you to include links to the next and previous articles
in chronological.  It currently ignores categories and tags. 

To use this plugin it must be included in your pelican settings file as 
usual::

    PLUGINS = ['Other Plugins...', 'pelican.plugins.chronological_links',]

It then adds four variables to each article

- next_url
- next_title
- previous_url
- previous_title

These variables can be included in your templates.  For instance in
``article.html`` you could have::

    {% if article.next_url %}
    <a href="{{article.next_url}}">{{article.next_title}}</a>
    {% endif %}


GitHub activity
---------------

This plugin makes use of the `feedparser`_ library that you'll need to
install.

Set the ``GITHUB_ACTIVITY_FEED`` parameter to your GitHub activity feed.
For example, to track Pelican project activity, the setting would be::

     GITHUB_ACTIVITY_FEED = 'https://github.com/getpelican.atom'

On the template side, you just have to iterate over the ``github_activity``
variable, as in this example::

     {% if GITHUB_ACTIVITY_FEED %}
        <div class="social">
                <h2>Github Activity</h2>
                <ul>

                {% for entry in github_activity %}
                    <li><b>{{ entry[0] }}</b><br /> {{ entry[1] }}</li>
                {% endfor %}
                </ul>
        </div><!-- /.github_activity -->
     {% endif %}

``github_activity`` is a list of lists. The first element is the title,
and the second element is the raw HTML from GitHub.

.. _feedparser: https://crate.io/packages/feedparser/

Global license
--------------

This plugin allows you to define a ``LICENSE`` setting and adds the contents of that
license variable to the article's context, making that variable available to use
from within your theme's templates.

Gravatar
--------

This plugin assigns the ``author_gravatar`` variable to the Gravatar URL and
makes the variable available within the article's context. You can add
``AUTHOR_EMAIL`` to your settings file to define the default author's email
address. Obviously, that email address must be associated with a Gravatar
account.

Alternatively, you can provide an email address from within article metadata::

    :email:  john.doe@example.com

If the email address is defined via at least one of the two methods above,
the ``author_gravatar`` variable is added to the article's context.

Gzip cache
----------

Certain web servers (e.g., Nginx) can use a static cache of gzip-compressed
files to prevent the server from compressing files during an HTTP call. Since
compression occurs at another time, these compressed files can be compressed
at a higher compression level for increased optimization.

The ``gzip_cache`` plugin compresses all common text type files into a ``.gz``
file within the same directory as the original file.

HTML tags for reStructuredText
------------------------------

This plugin allows you to use HTML tags from within reST documents. Following
is a usage example, which is in this case a contact form::

    .. html::

        <form method="GET" action="mailto:some email">
          <p>
            <input type="text" placeholder="Subject" name="subject">
            <br />
            <textarea name="body" placeholder="Message">
            </textarea>
            <br />
            <input type="reset"><input type="submit">
          </p>
        </form>

Related posts
-------------

This plugin adds the ``related_posts`` variable to the article's context.
To enable, add the following to your settings file::

    from pelican.plugins import related_posts
    PLUGINS = [related_posts]

You can then use the ``article.related_posts`` variable in your templates.
For example::

    {% if article.related_posts %}
        <ul>
        {% for related_post in article.related_posts %}
            <li>{{ related_post }}</li>
        {% endfor %}
        </ul>
    {% endif %}

Sitemap
-------

The sitemap plugin generates plain-text or XML sitemaps. You can use the
``SITEMAP`` variable in your settings file to configure the behavior of the
plugin.

The ``SITEMAP`` variable must be a Python dictionary and can contain three keys:

- ``format``, which sets the output format of the plugin (``xml`` or ``txt``)

- ``priorities``, which is a dictionary with three keys:

  - ``articles``, the priority for the URLs of the articles and their
    translations

  - ``pages``, the priority for the URLs of the static pages

  - ``indexes``, the priority for the URLs of the index pages, such as tags,
     author pages, categories indexes, archives, etc...

  All the values of this dictionary must be decimal numbers between ``0`` and ``1``.

- ``changefreqs``, which is a dictionary with three items:

  - ``articles``, the update frequency of the articles

  - ``pages``, the update frequency of the pages

  - ``indexes``, the update frequency of the index pages

  Valid frequency values are ``always``, ``hourly``, ``daily``, ``weekly``, ``monthly``,
  ``yearly`` and ``never``.

If a key is missing or a value is incorrect, it will be replaced with the
default value.

The sitemap is saved in ``<output_path>/sitemap.<format>``.

.. note::
   ``priorities`` and ``changefreqs`` are information for search engines.
   They are only used in the XML sitemaps.
   For more information: <http://www.sitemaps.org/protocol.html#xmlTagDefinitions>

**Example**

Here is an example configuration (it's also the default settings):

.. code-block:: python

    PLUGINS=['pelican.plugins.sitemap',]

    SITEMAP = {
        'format': 'xml',
        'priorities': {
            'articles': 0.5,
            'indexes': 0.5,
            'pages': 0.5
        },
        'changefreqs': {
            'articles': 'monthly',
            'indexes': 'daily',
            'pages': 'monthly'
        }
    }
