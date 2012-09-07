.. _plugins:

Plugins
#######

Since version 3.0, Pelican manages plugins. Plugins are a way to add features
to Pelican without having to directly hack Pelican code.

Pelican is shipped with a set of core plugins, but you can easily implement
your own (and this page describes how).

How to use plugins
==================

To load plugins, you have to specify them in your settings file. You have two
ways to do so.
Either by specifying strings with the path to the callables::

    PLUGINS = ['pelican.plugins.gravatar',] 

Or by importing them and adding them to the list::

    from pelican.plugins import gravatar
    PLUGINS = [gravatar, ]

If your plugins are not in an importable path, you can specify a ``PLUGIN_PATH``
in the settings::

    PLUGIN_PATH = "plugins"
    PLUGINS = ["list", "of", "plugins"]

How to create plugins
=====================

Plugins are based on the concept of signals. Pelican sends signals, and plugins
subscribe to those signals. The list of signals are defined in a following
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

=========================   ============================   ===========================================================================
Signal                      Arguments                      Description
=========================   ============================   ===========================================================================
initialized                 pelican object
finalized                   pelican object                 invoked after all the generators are executed and just before pelican exits
article_generate_context    article_generator, metadata
article_generator_init      article_generator              invoked in the ArticlesGenerator.__init__
get_generators              generators                     invoked in Pelican.get_generator_classes,
                                                           can return a Generator, or several
                                                           generator in a tuple or in a list.
pages_generate_context      pages_generator, metadata
pages_generator_init        pages_generator                invoked in the PagesGenerator.__init__
=========================   ============================   ===========================================================================

The list is currently small, don't hesitate to add signals and make a pull
request if you need them!

List of plugins
===============

Not all the list are described here, but a few of them have been extracted from
the Pelican core and provided in ``pelican.plugins``. They are described here:

Tag cloud
---------

Translation
-----------

GitHub activity
---------------

This plugin makes use of the ``feedparser`` library that you'll need to
install.

Set the ``GITHUB_ACTIVITY_FEED`` parameter to your GitHub activity feed.
For example, my setting would look like::

     GITHUB_ACTIVITY_FEED = 'https://github.com/kpanic.atom'

On the templates side, you just have to iterate over the ``github_activity``
variable, as in the example::

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



``github_activity`` is a list of lists. The first element is the title
and the second element is the raw HTML from GitHub.


Sitemap
-------

The plugin generates a sitemap of the blog.
It can generates plain text sitemaps or XML sitemaps.

Configuration
"""""""""""""

You can use the setting ``SITEMAP`` variable to configure the behavior of the
plugin.

The ``SITEMAP`` variable must be a Python dictionary, it can contain tree keys:


- ``format``, which set the output format of the plugin (``xml`` or ``txt``)

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

  An valid value is  ``always``, ``hourly``, ``daily``, ``weekly``, ``monthly``,
  ``yearly`` or ``never``.


If a key is missing or a value is incorrect, it will be replaced with the
default value.

The sitemap is saved in ``<output_path>/sitemap.<format>``.

.. note::
   ``priorities`` and ``changefreqs`` are informations for search engines.
   They are only used in the XML sitemaps.
   For more information: <http://www.sitemaps.org/protocol.html#xmlTagDefinitions>


Example
"""""""

Here is an example of configuration (it's also the default settings):

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
