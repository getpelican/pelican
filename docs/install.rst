Installing Pelican
##################

Pelican currently runs best on Python 2.7.x and 3.3+; earlier versions of
Python are not supported.

You can install Pelican via several different methods. The simplest is via
`pip <http://www.pip-installer.org/>`_::

    pip install pelican

(Keep in mind that operating systems will often require you to prefix the above
command with ``sudo`` in order to install Pelican system-wide.)

While the above is the simplest method, the recommended approach is to create
a virtual environment for Pelican via virtualenv_ before installing Pelican.
Assuming you have virtualenv_ installed, you can then open a new terminal
session and create a new virtual environment for Pelican::

    virtualenv ~/virtualenvs/pelican
    cd ~/virtualenvs/pelican
    source bin/activate

Once the virtual environment has been created and activated, Pelican can be
installed via ``pip install pelican`` as noted above. Alternatively, if
you have the project source, you can install Pelican using the distutils
method::

    cd path-to-Pelican-source
    python setup.py install

If you have Git installed and prefer to install the latest bleeding-edge
version of Pelican rather than a stable release, use the following command::

    pip install -e "git+https://github.com/getpelican/pelican.git#egg=pelican"

Once Pelican is installed, you can run ``pelican --help`` to see basic usage
options. For more detail, refer to the :doc:`Publish<publish>` section.

Optional packages
-----------------

If you plan on using `Markdown <http://pypi.python.org/pypi/Markdown>`_ as a
markup format, you'll need to install the Markdown library::

    pip install Markdown

Typographical enhancements can be enabled in your settings file, but first the
requisite `Typogrify <http://pypi.python.org/pypi/typogrify>`_ library must be
installed::

    pip install typogrify

Dependencies
------------

When Pelican is installed, the following dependent Python packages should be
automatically installed without any action on your part:

* `feedgenerator <http://pypi.python.org/pypi/feedgenerator>`_, to generate the
  Atom feeds
* `jinja2 <http://pypi.python.org/pypi/Jinja2>`_, for templating support
* `pygments <http://pypi.python.org/pypi/Pygments>`_, for syntax highlighting
* `docutils <http://pypi.python.org/pypi/docutils>`_, for supporting
  reStructuredText as an input format
* `pytz <http://pypi.python.org/pypi/pytz>`_, for timezone definitions
* `blinker <http://pypi.python.org/pypi/blinker>`_, an object-to-object and
  broadcast signaling system
* `unidecode <http://pypi.python.org/pypi/Unidecode>`_, for ASCII
  transliterations of Unicode text
* `six <http://pypi.python.org/pypi/six>`_,  for Python 2 and 3 compatibility
  utilities
* `MarkupSafe <http://pypi.python.org/pypi/MarkupSafe>`_, for a markup safe
  string implementation
* `python-dateutil <https://pypi.python.org/pypi/python-dateutil>`_, to read
  the date metadata

Upgrading
---------

If you installed a stable Pelican release via ``pip`` and wish to upgrade to
the latest stable release, you can do so by adding ``--upgrade``::

    pip install --upgrade pelican

If you installed Pelican via distutils or the bleeding-edge method, simply
perform the same step to install the most recent version.

Kickstart your site
-------------------

Once Pelican has been installed, you can create a skeleton project via the
``pelican-quickstart`` command, which begins by asking some questions about
your site::

    pelican-quickstart

Once you finish answering all the questions, your project will consist of the
following hierarchy (except for *pages* — shown in parentheses below — which you
can optionally add yourself if you plan to create non-chronological content)::

    yourproject/
    ├── content
    │   └── (pages)
    ├── output
    ├── develop_server.sh
    ├── fabfile.py
    ├── Makefile
    ├── pelicanconf.py       # Main settings file
    └── publishconf.py       # Settings to use when ready to publish

The next step is to begin to adding content to the *content* folder that has
been created for you.

.. _virtualenv: http://www.virtualenv.org/
