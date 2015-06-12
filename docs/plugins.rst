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

.. note::

   When experimenting with different plugins (especially the ones that
   deal with metadata and content) caching may interfere and the
   changes may not be visible. In such cases disable caching with
   ``LOAD_CONTENT_CACHE = False`` or use the ``--ignore-cache``
   command-line switch.

If your plugins are not in an importable path, you can specify a list of paths
via the ``PLUGIN_PATHS`` setting. As shown in the following example, paths in
the ``PLUGIN_PATHS`` list can be absolute or relative to the settings file::

    PLUGIN_PATHS = ["plugins", "/srv/pelican/plugins"]
    PLUGINS = ["assets", "liquid_tags", "sitemap"]

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

.. note::

    Signal receivers are weakly-referenced and thus must not be defined within
    your ``register`` callable or they will be garbage-collected before the
    signal is emitted.

List of signals
===============

Here is the list of currently implemented signals:

=================================   ============================   ===========================================================================
Signal                              Arguments                       Description
=================================   ============================   ===========================================================================
initialized                         pelican object
finalized                           pelican object                 invoked after all the generators are executed and just before pelican exits
                                                                   useful for custom post processing actions, such as:
                                                                   - minifying js/css assets.
                                                                   - notify/ping search engines with an updated sitemap.
generator_init                      generator                      invoked in the Generator.__init__
all_generators_finalized            generators                     invoked after all the generators are executed and before writing output
readers_init                        readers                        invoked in the Readers.__init__
article_generator_context           article_generator, metadata
article_generator_preread           article_generator              invoked before a article is read in ArticlesGenerator.generate_context;
                                                                   use if code needs to do something before every article is parsed
article_generator_init              article_generator              invoked in the ArticlesGenerator.__init__
article_generator_pretaxonomy       article_generator              invoked before categories and tags lists are created
                                                                   useful when e.g. modifying the list of articles to be generated
                                                                   so that removed articles are not leaked in categories or tags
article_generator_finalized         article_generator              invoked at the end of ArticlesGenerator.generate_context
article_generator_write_article     article_generator, content     invoked before writing each article, the article is passed as content
article_writer_finalized            article_generator, writer      invoked after all articles and related pages have been written, but before
                                                                   the article generator is closed.
get_generators                      pelican object                 invoked in Pelican.get_generator_classes,
                                                                   can return a Generator, or several
                                                                   generators in a tuple or in a list.
get_writer                          pelican object                 invoked in Pelican.get_writer,
                                                                   can return a custom Writer.
page_generator_context              page_generator, metadata
page_generator_preread              page_generator                 invoked before a page is read in PageGenerator.generate_context;
                                                                   use if code needs to do something before every page is parsed.
page_generator_init                 page_generator                 invoked in the PagesGenerator.__init__
page_generator_finalized            page_generator                 invoked at the end of PagesGenerator.generate_context
page_writer_finalized               page_generator, writer         invoked after all pages have been written, but before the page generator
                                                                   is closed.
static_generator_context            static_generator, metadata
static_generator_preread            static_generator               invoked before a static file is read in StaticGenerator.generate_context;
                                                                   use if code needs to do something before every static file is added to the
                                                                   staticfiles list.
static_generator_init               static_generator               invoked in the StaticGenerator.__init__
static_generator_finalized          static_generator               invoked at the end of StaticGenerator.generate_context
content_object_init                 content_object                 invoked at the end of Content.__init__
content_written                     path, context                  invoked each time a content file is written.
feed_written                        path, context, feed            invoked each time a feed file is written.
=================================   ============================   ===========================================================================

.. warning::

   Avoid ``content_object_init`` signal if you intend to read ``summary``
   or ``content`` properties of the content object. That combination can
   result in unresolved links when :ref:`ref-linking-to-internal-content`
   (see `pelican-plugins bug #314`_). Use ``_summary`` and ``_content``
   properties instead, or, alternatively, run your plugin at a later
   stage (e.g. ``all_generators_finalized``).

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

One thing you might want is to add support for your very own input format.
While it might make sense to add this feature in Pelican core, we
wisely chose to avoid this situation and instead have the different readers
defined via plugins.

The rationale behind this choice is mainly that plugins are really easy to
write and don't slow down Pelican itself when they're not active.

No more talking — here is an example::

    from pelican import signals
    from pelican.readers import BaseReader

    # Create a new reader class, inheriting from the pelican.reader.BaseReader
    class NewReader(BaseReader):
        enabled = True  # Yeah, you probably want that :-)

        # The list of file extensions you want this reader to match with.
        # If multiple readers were to use the same extension, the latest will
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

    def add_reader(readers):
        readers.reader_classes['yeah'] = NewReader

    # This is how pelican works.
    def register():
        signals.readers_init.connect(add_reader)


Adding a new generator
----------------------

Adding a new generator is also really easy. You might want to have a look at
:doc:`internals` for more information on how to create your own generator.

::

    def get_generators(pelican_object):
        # define a new generator here if you need to
        return MyGenerator

    signals.get_generators.connect(get_generators)

.. _pelican-plugins bug #314: https://github.com/getpelican/pelican-plugins/issues/314
