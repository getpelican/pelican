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
page_generate_context           page_generator, metadata
page_generator_init             page_generator                  invoked in the PagesGenerator.__init__
page_generator_finalized        page_generator                  invoked at the end of PagesGenerator.generate_context
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

.. note::

   After Pelican 3.2, signal names were standardized.  Older plugins
   may need to be updated to use the new names:

   ==========================  ===========================
   Old name                    New name
   ==========================  ===========================
   article_generate_context    article_generator_context
   article_generate_finalized  article_generator_finalized
   article_generate_preread    article_generator_preread
   pages_generate_context      page_generator_context
   pages_generate_preread      page_generator_preread
   pages_generator_finalized   page_generator_finalized
   pages_generator_init        page_generator_init
   static_generate_context     static_generator_context
   static_generate_preread     static_generator_preread
   ==========================  ===========================

Recipes
=======

We eventually realised some of the recipes to create plugins would be best
shared in the documentation somewhere, so here they are!

How to create a new reader
--------------------------

One thing you might want is to add the support for your very own input
format. While it might make sense to add this feature in pelican core, we
wisely chose to avoid this situation, and have the different readers defined in
plugins.

The rationale behind this choice is mainly that plugins are really easy to
write and don't slow down pelican itself when they're not active.

No more talking, here is the example::

    from pelican import signals
    from pelican.readers import EXTENSIONS, Reader

    # Create a new reader class, inheriting from the pelican.reader.Reader
    class NewReader(Reader):
        enabled = True  # Yeah, you probably want that :-)

        # The list of extensions you want this reader to match with.
        # In the case multiple readers use the same extensions, the latest will
        # win (so the one you're defining here, most probably).
        file_extensions = ['yeah']

        # You need to have a read method, which takes a filename and returns
        # some content and the associated metadata.
        def read(self, filename):
            metadata = {'title': 'Oh yeah',
                        'category': 'Foo',
                        'date': '2012-12-01'}

            parsed = {}
            for key, value in metadata.items():
                parsed[key] = self.process_metadata(key, value)

            return "Some content", parsed

    def add_reader(arg):
        EXTENSIONS['yeah'] = NewReader

    # this is how pelican works.
    def register():
        signals.initialized.connect(add_reader)


Adding a new generator
----------------------

Adding a new generator is also really easy. You might want to have a look at
:doc:`internals` for more information on how to create your own generator.

::

    def get_generators(generators):
        # define a new generator here if you need to
        return generators

    signals.get_generators.connect(get_generators)
