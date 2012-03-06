How to contribute?
###################
There are many ways to contribute to Pelican. You can enhance the
documentation, add missing features, and fix bugs (or just report them).

Don't hesitate to fork and make a pull request on GitHub.

Setting up the development environment
======================================

You're free to set up your development environment any way you like. Here is a
way using virtualenv and virtualenvwrapper. If you don't have them, you can
install these packages via::

    $ pip install virtualenvwrapper

Virtual environments allow you to work on Python projects which are isolated
from one another so you can use different packages (and package versions) with
different projects.

To create a virtual environment, use the following syntax::

    $ mkvirtualenv pelican 

To manually install the dependencies::

    $ pip install -r dev_requirements.txt
    $ python setup.py develop

Running the test suite
======================

Each time you add a feature, there are two things to do regarding tests:
checking that the existing tests pass, and adding tests for your new feature
or for the bug you're fixing.

The tests live in "pelican/tests" and you can run them using the
"discover" feature of unittest2::

    $ unit2 discover
