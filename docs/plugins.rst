.. _plugins:

Plugins
#######

Beginning with version 3.0, Pelican supports plugins. Plugins are a way to add
features to Pelican without having to directly modify the Pelican core.

How to use plugins
==================

To load plugins, you have to specify them in your settings file. There are two
ways to do so. The first method is to specify strings with the path to the
callables::

    PLUGINS = ['package.myplugin',]

Alternatively, another method is to import them and add them to the list::

    from package import myplugin
    PLUGINS = [myplugin,]

If your plugins are not in an importable path, you can specify a ``PLUGIN_PATH``
in the settings. ``PLUGIN_PATH`` can be an absolute path or a path relative to
the settings file::

    PLUGIN_PATH = "plugins"
    PLUGINS = ["list", "of", "plugins"]

Where to find plugins
=====================

We maintain a separate repository of plugins for people to share and use.
Please visit the `pelican-plugins`_ repository for a list of available plugins.

.. _pelican-plugins: https://github.com/getpelican/pelican-plugins

Please note that while we do our best to review and maintain these plugins,
they are submitted by the Pelican community and thus may have varying levels of
support and interoperability.

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
pages_generator_finalized       pages_generator                 invoked at the end of PagesGenerator.generate_context
content_object_init             content_object                  invoked at the end of Content.__init__ (see note below)
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
