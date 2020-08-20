Pelican |build-status| |pypi-version| |repology|
================================================

Pelican is a static site generator, written in Python_.

* Write content in reStructuredText_ or Markdown_ using your editor of choice
* Includes a simple command line tool to (re)generate site files
* Easy to interface with version control systems and web hooks
* Completely static output is simple to host anywhere


Features
--------

Pelican currently supports:

* Chronological content (e.g., articles, blog posts) as well as static pages
* Integration with external services (e.g., Google Analytics and Disqus)
* Site themes (created using Jinja2_ templates)
* Publication of articles in multiple languages
* Generation of Atom and RSS feeds
* Syntax highlighting via Pygments_
* Importing existing content from WordPress, Dotclear, and other services
* Fast rebuild times due to content caching and selective output writing

Check out `Pelican's documentation`_ for further information.


How to get help, contribute, or provide feedback
------------------------------------------------

See our `contribution submission and feedback guidelines <CONTRIBUTING.rst>`_.


Source code
-----------

Pelican's source code is `hosted on GitHub`_. If you feel like hacking,
take a look at `Pelican's internals`_.


Why the name "Pelican"?
-----------------------

"Pelican" is an anagram of *calepin*, which means "notebook" in French.


.. Links

.. _Python: https://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://daringfireball.net/projects/markdown/
.. _Jinja2: https://palletsprojects.com/p/jinja/
.. _Pygments: https://pygments.org/
.. _`Pelican's documentation`: https://docs.getpelican.com/
.. _`Pelican's internals`: https://docs.getpelican.com/en/latest/internals.html
.. _`hosted on GitHub`: https://github.com/getpelican/pelican

.. |build-status| image:: https://img.shields.io/github/workflow/status/getpelican/pelican/build
   :target: https://github.com/getpelican/pelican/actions
   :alt: GitHub Actions CI: continuous integration status
.. |pypi-version| image:: https://img.shields.io/pypi/v/pelican.svg
   :target: https://pypi.python.org/pypi/pelican
   :alt: PyPI: the Python Package Index
.. |repology| image:: https://repology.org/badge/tiny-repos/pelican.svg
   :target: https://repology.org/project/pelican/versions
   :alt: Repology: the packaging hub
