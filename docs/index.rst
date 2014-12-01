Pelican |release|
=================


.. ifconfig:: release.endswith('.dev')

    .. warning::

        This documentation is for the version of Pelican currently under development.
        Were you looking for version |last_stable| documentation?


Pelican is a static site generator, written in Python_. Highlights include:

* Write your content directly with your editor of choice
  in reStructuredText_ or Markdown_ formats
* Includes a simple CLI tool to (re)generate your site
* Easy to interface with distributed version control systems and web hooks
* Completely static output is easy to host anywhere

Ready to get started? Check out the :doc:`Quickstart<quickstart>` guide.

Features
--------

Pelican |version| currently supports:

* Articles (e.g., blog posts) and pages (e.g., "About", "Projects", "Contact")
* Comments, via an external service (Disqus). If you prefer to have more
  control over your comment data, self-hosted comments are another option.
  Check out the `Pelican Plugins`_ repository for more details.
* Theming support (themes are created using Jinja2_ templates)
* Publication of articles in multiple languages
* Atom/RSS feeds
* Code syntax highlighting
* Import from WordPress, Dotclear, or RSS feeds
* Integration with external tools: Twitter, Google Analytics, etc. (optional)
* Fast rebuild times thanks to content caching and selective output writing

Why the name "Pelican"?
-----------------------

"Pelican" is an anagram for *calepin*, which means "notebook" in French. ;)

Source code
-----------

You can access the source code at: https://github.com/getpelican/pelican

How to get help, contribute, or provide feedback
------------------------------------------------

See our :doc:`feedback and contribution submission guidelines <contribute>`.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   quickstart
   install
   content
   publish
   settings
   themes
   plugins
   pelican-themes
   importer
   faq
   tips
   contribute
   internals
   report
   changelog

.. Links

.. _Python: http://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _Jinja2: http://jinja.pocoo.org/
.. _`Pelican documentation`: http://docs.getpelican.com/latest/
.. _`Pelican's internals`: http://docs.getpelican.com/en/latest/internals.html
.. _`Pelican plugins`: https://github.com/getpelican/pelican-plugins
