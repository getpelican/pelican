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

=========================   ============================   =========================================
Signal                      Arguments                      Description
=========================   ============================   =========================================
initialized                 pelican object
article_generate_context    article_generator, metadata
article_generator_init      article_generator              invoked in the ArticlesGenerator.__init__
pages_generate_context      pages_generator, metadata
pages_generator_init        pages_generator                invoked in the PagesGenerator.__init__
=========================   ============================   =========================================

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
