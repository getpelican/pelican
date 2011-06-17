.. _plugins:

Plugins
#######

Since version 2.8, pelican manages plugins. Plugins are a way to add feature to
pelican without having to directly hack pelican code.

Pelican is shipped with a set of core plugins, but you can easily implement
your own (and this page describes how)

How to use plugins?
====================

To load plugins, you have to specify a them in your settings file. You have two
ways to do so:  by specifying strings with the path to the callables: ::

    PLUGINS = ['pelican.plugins.gravatar',] 

Or by importing them and adding them to the list::

    from pelican.plugins import gravatar
    PLUGINS = [gravatar, ]

If your plugins are not in an importable path, you can specify a `PLUGIN_PATH`
in the settings::

    PLUGIN_PATH = "plugins"
    PLUGINS = ["list", "of", "plugins"]

How to create plugins?
======================

Plugins are based on the concept of signals. Pelican sends signals and plugins
subscribe to those signals. The list of signals are defined in a following
section.

The only rule to follow for plugins is to define a `register` callable, in
which you map the signals to your plugin logic. Let's take a simple exemple::

    from pelican import signals

    def test(sender):
        print "%s initialized !!" % sender

    def register():
        signals.initialized.connect(test)


List of signals
===============

Here is the list of currently implemented signals:

=========================   ============================   =====================
Signal                      Arguments                      Description
=========================   ============================   =====================
initialized                 pelican object
article_generate_context    article_generator, metadata
=========================   ============================   =====================

The list is currently small, don't hesitate to add signals and make a pull
request if you need them!

List of plugins
===============

Not all the list are described here, but a few of them have been extracted from
pelican core and provided in pelican.plugins. They are described here:

Tag cloud
---------

Translation
-----------
