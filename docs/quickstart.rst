Quickstart
##########

Reading through all the documentation is highly recommended, but for the truly
impatient, following are some quick steps to get started.

Installation
------------

Install Pelican (and optionally Markdown if you intend to use it) on Python
2.7.x or Python 3.3+ by running the following command in your preferred
terminal, prefixing with ``sudo`` if permissions warrant::

    pip install pelican markdown

Create a project
----------------

First, choose a name for your project, create an appropriately-named directory
for your site, and switch to that directory::

    mkdir -p ~/projects/yoursite
    cd ~/projects/yoursite

Create a skeleton project via the ``pelican-quickstart`` command, which begins
by asking some questions about your site::

    pelican-quickstart

For questions that have default values denoted in brackets, feel free to use
the Return key to accept those default values [#tzlocal_fn]_. When asked for
your URL prefix, enter your domain name as indicated (e.g.,
``http://example.com``).

Create an article
-----------------

You cannot run Pelican until you have created some content. Use your preferred
text editor to create your first article with the following content::

    Title: My First Review
    Date: 2010-12-03 10:20
    Category: Review

    Following is a review of my favorite mechanical keyboard.

Given that this example article is in Markdown format, save it as
``~/projects/yoursite/content/keyboard-review.md``.

Generate your site
------------------

From your site directory, run the ``pelican`` command to generate your site::

    pelican content

Your site has now been generated inside the ``output`` directory. (You may see a
warning related to feeds, but that is normal when developing locally and can be
ignored for now.)

Preview your site
-----------------

Open a new terminal session and run the following commands to switch to your
``output`` directory and launch Pelican's web server::

    cd ~/projects/yoursite/output
    python -m pelican.server

Preview your site by navigating to http://localhost:8000/ in your browser.

Continue reading the other documentation sections for more detail, and check out
the Pelican wiki's Tutorials_ page for links to community-published tutorials.

.. _Tutorials: https://github.com/getpelican/pelican/wiki/Tutorials

Footnotes
---------

.. [#tzlocal_fn] You can help localize default fields by installing the
                 optional `tzlocal <https://pypi.python.org/pypi/tzlocal>`_
                 module.
