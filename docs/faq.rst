Frequently Asked Questions (FAQ)
################################

Here is a summary of the frequently asked questions for pelican.

Is it mandatory to have a configuration file ?
==============================================

No, it's not. Configurations files are just an easy way to configure pelican.
For the basic operations, it's possible to specify options while invoking
pelican with the command line (see `pelican --help` for more informations about
that)

I'm creating my own theme, how to use pygments ?
================================================

Pygment add some classes to the generated content, so the theming of your theme
will be done thanks to a css file. You can have a look to the one proposed by
default `on the project website <http://pygments.org/demo/15101/>`_

How do I create my own theme ?
==============================

Please refer yourself to :ref:`theming-pelican`.

How can I help ?
================

You have different options to help. First, you can use pelican, and report any
idea or problem you have on `the bugtracker
<http://github.com/ametaireau/pelican/issues>`_.

If you want to contribute, please have a look to `the git repository
<https://github.com/ametaireau/pelican/>`_, fork it, add your changes and do
a pull request, I'll review them as soon as possible.

You can also contribute by creating themes, and making the documentation
better.

I want to use markdown, but I got an error
==========================================

Markdown is not a hard dependency for pelican, so you will need to install it
by yourself. You can do so by typing::

    $ (sudo) pip install markdown

In case you don't have pip installed, consider installing it by doing::

    $ (sudo) easy_install pip
