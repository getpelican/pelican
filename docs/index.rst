Pelican
#######

Pelican is a simple weblog generator, written in Python.

* Write your weblog entries directly with your editor of choice (vim!) in
  reStructuredText or Markdown
* A simple CLI tool to (re)generate the weblog
* Easy to interface with DVCSes and web hooks
* Completely static output is easy to host anywhere

Features
========

Pelican currently supports:

* Blog articles and pages
* Comments, via an external service (Disqus). (Please note that while
  useful, Disqus is an external service, and thus the comment data will be
  somewhat outside of your control and potentially subject to data loss.)
* Theming support (themes are created using `jinja2 <http://jinja.pocoo.org/>`_)
* PDF generation of the articles/pages (optional)
* Publication of articles in multiple languages
* Atom/RSS feeds
* Code syntax highlighting
* Import from WordPress, Dotclear, or RSS feeds
* Integration with external tools: Twitter, Google Analytics, etc. (optional)

Why the name "Pelican" ?
========================

Heh, you didn't notice? "Pelican" is an anagram for "Calepin" ;)

Source code
===========

You can access the source code via git at http://github.com/ametaireau/pelican/

Feedback / Contact us
=====================

If you want to see new features in Pelican, don't hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback! You can
also join the team at `#pelican on irc.freenode.org
<irc://irc.freenode.net/pelican>`_
(or if you don't have any IRC client, use `the webchat
<http://webchat.freenode.net/?channels=pelican&uio=d4>`_)
for quick feedback.

Documentation
=============

A French version of the documentation is available at :doc:`fr/index`.

.. toctree::
   :maxdepth: 2

   getting_started
   settings
   themes
   internals
   pelican-themes
   importer
   faq
   tips
   contribute
   report
