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

* blog articles
* comments, via an external service (disqus). Please notice that while
  it's useful, it's an external service, and you'll not manage the
  comments by yourself. It could potentially eat your data.
* theming support (themes are done using `jinja2 <http://jinjna.pocoo.org>`_)
* PDF generation of the articles/pages (optional).

Why the name "Pelican" ?
========================

Heh, you didn't noticed? "Pelican" is an anagram for "Calepin" ;)

Source code
===========

You can access the source code via mercurial at http://hg.notmyidea.org/pelican/
or via git on http://github.com/ametaireau/pelican/

Feedback !
==========

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback !

Documentation
=============

.. toctree::
   :maxdepth: 2
   
   getting_started
   settings
   themes
   internals
   faq
