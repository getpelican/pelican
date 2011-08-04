Pelican
#######

Pelican is a simple weblog generator, writen in python.

* Write your weblog entries directly with your editor of choice (vim!) and
  directly in restructured text, or markdown.
* A simple cli-tool to (re)generate the weblog.
* Easy to interface with DVCSes and web hooks
* Completely static output, so easy to host anywhere !

Features
========

Pelican currently supports:

* blog articles and simple pages
* comments, via an external service (disqus). Please notice that while
  it's useful, it's an external service, and you'll not manage the
  comments by yourself. It could potentially eat your data. (optional)
* easy theming (themes are done using `jinja2 <http://jinjna.pocoo.org>`_)
* PDF generation of the articles/pages (optional).
* publication of articles in various languages
* RSS/Atom feeds
* wordpress/dotclear or RSS imports
* integration with various tools: twitter/google analytics/skribit (optional)

Why the name "Pelican" ?
========================

Heh, you didn't noticed? "Pelican" is an anagram for "Calepin" ;)

Source code
===========

You can access the source code via git on http://github.com/ametaireau/pelican/

Feedback / Contact us
=====================

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback! You can
also join the team at `#pelican on irc.freenode.org
<irc://irc.freenode.net/pelican>`_
(or if you don't have any IRC client, using `the webchat
<http://webchat.freenode.net/?channels=pelican&uio=d4>`_)
for quick feedback.

Documentation
=============

A french version of the documentation is available at :doc:`fr/index`.

.. toctree::
   :maxdepth: 2

   getting_started
   settings
   themes
   internals
   pelican-themes
   importer
   faq
   contribute
