How to contribute ?
###################
There are many ways to contribute to pelican. You can enhance the
documentation, add missing features, fix bugs or just report them.

Don't hesitate to fork and make a pull request on github.

Set up the development environment
==================================

You're free to setup up the environment in any way you like. Here is a way
using virtualenv and virtualenvwrapper. If you don't have them, you can install
them using::

    $ pip install virtualenvwrapper

Virtual environments allow you to work on an installation of python which is
not the one installed on your system. Especially, it will install the different
projects under a different location.

To create the virtualenv environment, you have to do::

    $ mkvirtualenv pelican --no-site-package

Then you would have to install all the dependencies::

    $ pip install -r dev_requirements.txt

Running the test suite
======================

Each time you add a feature, there are two things to do regarding tests:
checking that the tests run in a right way, and be sure that you add tests for
the feature you are working on or the bug you're fixing.

The tests leaves under "pelican/tests" and you can run them using the
"discover" feature of unittest2::

    python -m unittest2 discover
