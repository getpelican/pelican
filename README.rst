Pelican
=======

.. image:: https://secure.travis-ci.org/getpelican/pelican.png?branch=master
   :target: http://travis-ci.org/getpelican/pelican
   :alt: Travis-ci: continuous integration status.

Pelican is a static site generator, written in Python_.

* Write your weblog entries directly with your editor of choice (vim!)
  in reStructuredText_ or Markdown_
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
* Import from WordPress, Dotclear, or RSS feeds
* Integration with external tools: Twitter, Google Analytics, etc. (optional)
* Fast rebuild times thanks to content caching and selective output writing.

Have a look at the `Pelican documentation`_ for more information.

Why the name "Pelican"?
-----------------------

"Pelican" is an anagram for *calepin*, which means "notebook" in French. ;)

Source code
-----------

You can access the source code at: https://github.com/getpelican/pelican

If you feel hackish, have a look at the explanation of `Pelican's internals`_.

How to get help, contribute, or provide feedback
------------------------------------------------

See our `contribution submission and feedback guidelines <CONTRIBUTING.rst>`_.

.. Links

.. _Python: http://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _Jinja2: http://jinja.pocoo.org/
.. _`Pelican documentation`: http://docs.getpelican.com/
.. _`Pelican's internals`: http://docs.getpelican.com/en/latest/internals.html
