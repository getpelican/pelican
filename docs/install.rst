Installing Pelican
##################

Pelican currently runs best on Python |min_python|; earlier versions of Python are not supported.

Once Pelican is installed, you can run ``pelican --help`` to see basic usage
options. For more detail, refer to the :doc:`Publish<publish>` section.

You can install Pelican via several different methods.

**Recommended method:** `Pip <https://pip.pypa.io/>`_ User Install

To install Pelican via Pip::

    python3 -m pip install --user "pelican[markdown]"

Or, if you do not plan to use `Markdown <https://pypi.org/project/Markdown/>`_,
you can omit the ``[markdown]`` suffix::

    python3 -m pip install --user pelican

**Alternate method 1:** `Pipx <https://github.com/pypa/pipx>`_

Pipx lets you execute binaries from Python packages in isolated environments.
You can install Pipx by following its
`documentation <https://pipx.pypa.io>`_. After Pipx is installed,
you can install Pelican via::

    pipx install "pelican[markdown]"

**Alternate method 2:** `uv <https://docs.astral.sh/uv/>`_

Like Pipx, ``uv`` allows you to install tools in isolated environments.
If you have ``uv`` installed, you can install Pelican via::

    uv tool install "pelican[markdown]"

**Alternate method 3:** Virtual Environment

If you prefer to manually manage a virtual environment, you can create
a virtual environment for Pelican via venv_ before installing Pelican::

    python3 -m venv ~/virtualenvs/pelican
    source ~/virtualenvs/pelican/bin/activate
    python3 -m pip install "pelican[markdown]"

Alternatively, if you have the project source, you can replace the last command
with the following to install Pelican using the ``setuptools`` method::

    cd path-to-Pelican-source
    python3 -m pip install .

If you have Git installed and prefer to install the latest bleeding-edge
version of Pelican rather than a stable release, use the following command::

    python3 -m pip install -e "git+https://github.com/getpelican/pelican.git#egg=pelican"

To exit the virtual environment, type ``deactivate``.

Optional packages
-----------------

If you plan on using `Markdown <https://pypi.org/project/Markdown/>`_ as a
markup format, you can install Pelican with Markdown support::

    python3 -m pip install --user "pelican[markdown]"

Typographical enhancements can be enabled in your settings file, but first the
requisite `Typogrify <https://github.com/justinmayer/typogrify>`_ library must be
installed::

    python3 -m pip install --user typogrify

If you are using Pipx, you can inject packages into the Pipx-managed virtual
environment. For example, to add Typogrify::

    pipx inject pelican typogrify

To use ``uv`` to install Pelican with additional extra packages, use the
following example command, which will install both Markdown & Typogrify::

    uv tool install --with Markdown --with typogrify pelican

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

    python3 -m pip install --upgrade pelican

If you installed Pelican via ``setuptools`` or the bleeding-edge method,
perform the same step to install the most recent version.

If you installed with Pipx, upgrade via::

    pipx upgrade pelican

If you installed with ``uv``, upgrade via::

    uv tool upgrade pelican

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

.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _venv: https://docs.python.org/3/library/venv.html
