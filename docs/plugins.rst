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

The following plugins are currently included with Pelican under ``pelican.plugins``:

* `GitHub activity`_
* `Global license`_
* `Gravatar`_
* `HTML tags for reStructuredText`_
* `Related posts`_

Ideas for plugins that haven't been written yet:

* Tag cloud
* Translation

Plugin descriptions
===================

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
<<<<<<< HEAD

Global license
--------------

This plugin allows you to define a LICENSE setting and adds the contents of that
license variable to the article's context, making that variable available to use
from within your theme's templates.

Gravatar
--------

This plugin assigns the ``author_gravatar`` variable to the Gravatar URL and
makes the variable available within the article's context. You can add
AUTHOR_EMAIL to your settings file to define the default author's email
address. Obviously, that email address must be associated with a Gravatar
account.

Alternatively, you can provide an email address from within article metadata::

    :email:  john.doe@example.com

If the email address is defined via at least one of the two methods above,
the ``author_gravatar`` variable is added to the article's context.

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
