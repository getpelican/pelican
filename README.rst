Pelican |build-status| |pypi-version| |downloads| |repology|
============================================================

Pelican is a static site generator, written in Python_, that allows you to create
web sites by composing text files in formats such as Markdown, reStructuredText, and HTML.

With Pelican, you can create web sites without worrying about databases or server-side programming.
Pelican generates static sites that can be served via any web server or hosting service.

You can perform the following functions with Pelican:

* Compose content in Markdown_ or reStructuredText_ using your editor of choice
* Simple command-line tool (re)generates HTML, CSS, and JS from your source content
* Easy to interface with version control systems and web hooks
* Completely static output is simple to host anywhere


Features
--------

Pelican’s feature highlights include:

* Chronological content (e.g., articles, blog posts) as well as static pages
* Integration with external services
* Site themes (created using Jinja2_ templates)
* Publication of articles in multiple languages
* Generation of Atom and RSS feeds
* Code syntax highlighting via Pygments_
* Import existing content from WordPress, Dotclear, or RSS feeds
* Fast rebuild times due to content caching and selective output writing
* Extensible via a rich plugin ecosystem: `Pelican Plugins`_

Check out the `Pelican documentation`_ for further information.


How to get help, contribute, or provide feedback
------------------------------------------------

See our `contribution submission and feedback guidelines <CONTRIBUTING.rst>`_.


Source code
-----------

Pelican’s source code is `hosted on GitHub`_. For information on how it works,
have a look at `Pelican's internals`_.


Why the name “Pelican”?
-----------------------

“Pelican” is an anagram of *calepin*, which means “notebook” in French.


.. Links

.. _Python: https://www.python.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://daringfireball.net/projects/markdown/
.. _Jinja2: https://palletsprojects.com/p/jinja/
.. _Pygments: https://pygments.org/
.. _`Pelican Plugins`: https://github.com/pelican-plugins
.. _`Pelican documentation`: https://docs.getpelican.com/
.. _`Pelican's internals`: https://docs.getpelican.com/en/latest/internals.html
.. _`hosted on GitHub`: https://github.com/getpelican/pelican

.. |build-status| image:: https://img.shields.io/github/actions/workflow/status/getpelican/pelican/main.yml?branch=main
   :target: https://github.com/getpelican/pelican/actions/workflows/main.yml?query=branch%3Amain
   :alt: GitHub Actions CI: continuous integration status
.. |pypi-version| image:: https://img.shields.io/pypi/v/pelican.svg
   :target: https://pypi.org/project/pelican/
   :alt: PyPI: the Python Package Index
.. |downloads| image:: https://img.shields.io/pypi/dm/pelican.svg
   :target: https://pypi.org/project/pelican/
   :alt: Monthly Downloads from PyPI
.. |repology| image:: https://repology.org/badge/tiny-repos/pelican.svg
   :target: https://repology.org/project/pelican/versions
   :alt: Repology: the packaging hub
