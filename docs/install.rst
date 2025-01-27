Installing Pelican
##################

Pelican currently runs best on |min_python|; earlier versions of Python are not supported.

You can install Pelican via several different methods. The simplest is via Pip_::

    python -m pip install pelican

Or, if you plan on using Markdown::

    python -m pip install "pelican[markdown]"

(Keep in mind that some operating systems will require you to prefix the above
command with ``sudo`` in order to install Pelican system-wide.)

While the above is the simplest method, the recommended approach is to create a
virtual environment for Pelican via virtualenv_ before installing Pelican.
Assuming you have virtualenv_ installed, you can then open a new terminal
session and create a new virtual environment for Pelican::

    virtualenv ~/virtualenvs/pelican
    cd ~/virtualenvs/pelican
    source bin/activate

Once the virtual environment has been created and activated, Pelican can be
installed via ``python -m pip install pelican`` as noted above. Alternatively, if you
have the project source, you can install Pelican using the setuptools method::

    cd path-to-Pelican-source
    python -m pip install .

If you have Git installed and prefer to install the latest bleeding-edge
version of Pelican rather than a stable release, use the following command::

    python -m pip install -e "git+https://github.com/getpelican/pelican.git#egg=pelican"

Once Pelican is installed, you can run ``pelican --help`` to see basic usage
options. For more detail, refer to the :doc:`Publish<publish>` section.

Optional packages
-----------------

If you plan on using `Markdown <https://pypi.org/project/Markdown/>`_ as a
markup format, you can install Pelican with Markdown support::

    python -m pip install "pelican[markdown]"

Typographical enhancements can be enabled in your settings file, but first the
requisite `Typogrify <https://pypi.org/project/typogrify/>`_ library must be
installed::

    python -m pip install typogrify

Dependencies
------------

When Pelican is installed, the following dependent Python packages should be
automatically installed without any action on your part:

* `feedgenerator <https://pypi.org/project/feedgenerator/>`_, to generate the
  Atom feeds
* `jinja2 <https://pypi.org/project/Jinja2/>`_, for templating support
* `pygments <https://pypi.org/project/Pygments/>`_, for syntax highlighting
* `docutils <https://pypi.org/project/docutils/>`_, for supporting
  reStructuredText as an input format
* `blinker <https://pypi.org/project/blinker/>`_, an object-to-object and
  broadcast signaling system
* `unidecode <https://pypi.org/project/Unidecode/>`_, for ASCII
  transliterations of Unicode text
  utilities
* `MarkupSafe <https://pypi.org/project/MarkupSafe/>`_, for a markup-safe
  string implementation
* `python-dateutil <https://pypi.org/project/python-dateutil/>`_, to read
  the date metadata

Upgrading
---------

If you installed a stable Pelican release via Pip_ and wish to upgrade to
the latest stable release, you can do so by adding ``--upgrade``::

    python -m pip install --upgrade pelican

If you installed Pelican via distutils or the bleeding-edge method, simply
perform the same step to install the most recent version.

Kickstart your site
-------------------

Once Pelican has been installed, you can create a skeleton project via the
``pelican-quickstart`` command, which begins by asking some questions about
your site::

    pelican-quickstart

If run inside an activated virtual environment, ``pelican-quickstart`` will
look for an associated project path inside ``$VIRTUAL_ENV/.project``. If that
file exists and contains a valid directory path, the new Pelican project will
be saved at that location. Otherwise, the default is the current working
directory. To set the new project path on initial invocation, use:
``pelican-quickstart --path /your/desired/directory``

Once you finish answering all the questions, your project will consist of the
following hierarchy (except for *pages* — shown in parentheses below — which
you can optionally add yourself if you plan to create non-chronological
content)::

    yourproject/
    ├── content
    │   └── (pages)
    ├── output
    ├── tasks.py
    ├── Makefile
    ├── pelicanconf.py       # Main settings file
    └── publishconf.py       # Settings to use when ready to publish

The next step is to begin to adding content to the *content* folder that has
been created for you.

.. _Pip: https://pip.pypa.io/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
