pelican-themes
##############



Description
===========

``pelican-themes`` is a command line tool for managing themes for Pelican.


Usage
"""""

| pelican-themes [-h] [-l] [-i theme path [theme path ...]]
|                      [-r theme name [theme name ...]]
|                      [-s theme path [theme path ...]] [-v] [--version]

Optional arguments:
"""""""""""""""""""


-h, --help                              Show the help an exit

-l, --list                              Show the themes already installed

-i theme_path, --install theme_path     One or more themes to install

-r theme_name, --remove theme_name      One or more themes to remove

-s theme_path, --symlink theme_path     Same as "--install", but create a symbolic link instead of copying the theme.
                                        Useful for theme development

-v, --verbose                           Verbose output

--version                               Print the version of this script



Examples
========


Listing the installed themes
""""""""""""""""""""""""""""

With ``pelican-themes``, you can see the available themes by using the ``-l`` or ``--list`` option:

.. code-block:: console

    $ pelican-themes -l
    notmyidea
    two-column@
    simple
    $ pelican-themes --list
    notmyidea
    two-column@
    simple

In this example, we can see there are three themes available: ``notmyidea``, ``simple``, and ``two-column``.

``two-column`` is prefixed with an ``@`` because this theme is not copied to the Pelican theme path, but is instead just linked to it (see `Creating symbolic links`_ for details about creating symbolic links).

Note that you can combine the ``--list`` option with the ``-v`` or ``--verbose`` option to get more verbose output, like this:

.. code-block:: console

    $ pelican-themes -v -l
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/notmyidea
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/two-column (symbolic link to `/home/skami/Dev/Python/pelican-themes/two-column')
    /usr/local/lib/python2.6/dist-packages/pelican-2.6.0-py2.6.egg/pelican/themes/simple


Installing themes
"""""""""""""""""

You can install one or more themes using the ``-i`` or ``--install`` option.
This option takes as argument the path(s) of the theme(s) you want to install, and can be combined with the verbose option:

.. code-block:: console

    # pelican-themes --install ~/Dev/Python/pelican-themes/notmyidea-cms --verbose

.. code-block:: console

    # pelican-themes --install ~/Dev/Python/pelican-themes/notmyidea-cms\
                               ~/Dev/Python/pelican-themes/martyalchin \
                               --verbose

.. code-block:: console

    # pelican-themes -vi ~/Dev/Python/pelican-themes/two-column


Removing themes
"""""""""""""""

The ``pelican-themes`` command can also remove themes from the Pelican themes path.
The ``-r`` or ``--remove`` option takes as argument the name(s) of the theme(s) you want to remove, and can be combined with the ``--verbose`` option.

.. code-block:: console

    # pelican-themes --remove two-column

.. code-block:: console

    # pelican-themes -r martyachin notmyidea-cmd -v





Creating symbolic links
"""""""""""""""""""""""

``pelican-themes`` can also install themes by creating symbolic links instead of copying entire themes into the Pelican themes path.

To symbolically link a theme, you can use the ``-s`` or ``--symlink``, which works exactly as the ``--install`` option:

.. code-block:: console

    # pelican-themes --symlink ~/Dev/Python/pelican-themes/two-column

In this example, the ``two-column`` theme is now symbolically linked to the Pelican themes path, so we can use it, but we can also modify it without having to reinstall it after each modification.

This is useful for theme development:

.. code-block:: console

    $ sudo pelican-themes -s ~/Dev/Python/pelican-themes/two-column
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ firefox /tmp/out/index.html
    $ vim ~/Dev/Pelican/pelican-themes/two-column/static/css/main.css
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ cp /tmp/bg.png ~/Dev/Pelican/pelican-themes/two-column/static/img/bg.png
    $ pelican ~/Blog/content -o /tmp/out -t two-column
    $ vim ~/Dev/Pelican/pelican-themes/two-column/templates/index.html
    $ pelican ~/Blog/content -o /tmp/out -t two-column



Doing several things at once
""""""""""""""""""""""""""""

The ``--install``, ``--remove`` and ``--symlink`` option are not mutually exclusive, so you can combine them in the same command line to do more than one operation at time, like this:


.. code-block:: console

    # pelican-themes --remove notmyidea-cms two-column \
                     --install ~/Dev/Python/pelican-themes/notmyidea-cms-fr \
                     --symlink ~/Dev/Python/pelican-themes/two-column \
                     --verbose

In this example, the theme ``notmyidea-cms`` is replaced by the theme ``notmyidea-cms-fr``
