How to contribute?
###################
There are many ways to contribute to Pelican. You can enhance the
documentation, add missing features, and fix bugs (or just report them).

Don't hesitate to fork and make a pull request on GitHub. When doing so, please
create a new feature branch as opposed to making your commits in the master
branch.

Setting up the development environment
======================================

You're free to set up your development environment any way you like. Here is a
way using the `virtualenv <http://www.virtualenv.org/>`_ and `virtualenvwrapper
<http://www.doughellmann.com/projects/virtualenvwrapper/>`_ tools. If you don't
have them, you can install these both of these packages via::

    $ pip install virtualenvwrapper

Virtual environments allow you to work on Python projects which are isolated
from one another so you can use different packages (and package versions) with
different projects.

To create a virtual environment, use the following syntax::

    $ mkvirtualenv pelican

To clone the Pelican source::

    $ git clone https://github.com/getpelican/pelican.git src/pelican

To install the development dependencies::

    $ cd src/pelican
    $ pip install -r dev_requirements.txt

To install Pelican and its dependencies::

    $ python setup.py develop

Running the test suite
======================

Each time you add a feature, there are two things to do regarding tests:
checking that the existing tests pass, and adding tests for the new feature
or bugfix.

The tests live in "pelican/tests" and you can run them using the
"discover" feature of unittest2::

    $ unit2 discover

If you have made changes that affect the output of a Pelican-generated weblog,
then you should update the output used by functional tests.
To do so, you can use the following two commands::

    $ LC_ALL="C" pelican -o tests/output/custom/ -s samples/pelican.conf.py \
        samples/content/
    $ LC_ALL="C" pelican -o tests/output/basic/ samples/content/

Coding standards
================

Try to respect what is described in the `PEP8 specification
<http://www.python.org/dev/peps/pep-0008/>`_ when providing patches. This can be
eased via the `pep8 <http://pypi.python.org/pypi/pep8>`_ or `flake8
<http://pypi.python.org/pypi/flake8/>`_ tools, the latter of which in
particular will give you some useful hints about ways in which the
code/formatting can be improved.
