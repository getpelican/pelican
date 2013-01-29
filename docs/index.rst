Pelican
=======

Pelican is a static site generator, written in Python_.

* Write your weblog entries directly with your editor of choice (vim!)
  in reStructuredText_, Markdown_, or AsciiDoc_
* Includes a simple CLI tool to (re)generate the weblog
* Easy to interface with DVCSes and web hooks
* Completely static output is easy to host anywhere

Features
--------

Pelican currently supports:

* Blog articles and pages
* Comments, via an external service (Disqus). (Please note that while
  useful, Disqus is an external service, and thus the comment data will be
  somewhat outside of your control and potentially subject to data loss.)
* Theming support (themes are created using Jinja2_ templates)
* PDF generation of the articles/pages (optional)
* Publication of articles in multiple languages
* Atom/RSS feeds
* Code syntax highlighting
* Asset management with `webassets`_ (optional)
* Import from WordPress, Dotclear, or RSS feeds
* Integration with external tools: Twitter, Google Analytics, etc. (optional)

Why the name "Pelican"?
-----------------------

"Pelican" is an anagram for *calepin*, which means "notebook" in French. ;)

Source code
-----------

You can access the source code at: https://github.com/getpelican/pelican

Feedback / Contact us
---------------------

If you want to see new features in Pelican, don't hesitate to offer suggestions,
clone the repository, etc. There are many ways to :doc:`contribute<contribute>`.
That's open source, dude!

Send a message to "authors at getpelican dot com" with any requests/feedback! You
can also join the team at `#pelican on Freenode`_ (or if you don't have an IRC
client handy, use the webchat_ for quick feedback.

Documentation
-------------

A French version of the documentation is available at :doc:`fr/index`.

.. toctree::
   :maxdepth: 2

   getting_started
   settings
   themes
   plugins
   internals
   pelican-themes
   importer
   faq
   tips
   contribute
   report
   changelog

.. Links

.. _Python: http://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _AsciiDoc: http://www.methods.co.nz/asciidoc/index.html
.. _Jinja2: http://jinja.pocoo.org/
.. _`Pelican documentation`: http://docs.getpelican.com/latest/
.. _`Pelican's internals`: http://docs.getpelican.com/en/latest/internals.html
.. _`#pelican on Freenode`: irc://irc.freenode.net/pelican
.. _webchat: http://webchat.freenode.net/?channels=pelican&uio=d4
.. _webassets: https://github.com/miracle2k/webassets
