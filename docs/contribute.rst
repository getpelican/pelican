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

testing for python3
-------------------

On Python 3, if you have installed the Py3k compatible versions of the
plugins manual testing with ``unit2 discover`` is also straightforward.

However, you must tell tox to use those Py3k libraries. If you forget this,
tox will pull the regular packages from PyPi and the tests will fail.

Tell tox about the local packages thusly: enter the source directory of
smartypants and run tox there. Do this again for typogrify and webassets.
Smartypants and typogrify do not have real tests, and webassets will fail
noisily, but as a result we get these libraries neatly packaged in tox's
distshare directory. And this we need to run tox for Pelican.

Coding standards
================

Try to respect what is described in the `PEP8 specification
<http://www.python.org/dev/peps/pep-0008/>`_ when providing patches. This can be
eased via the `pep8 <http://pypi.python.org/pypi/pep8>`_ or `flake8
<http://pypi.python.org/pypi/flake8/>`_ tools, the latter of which in
particular will give you some useful hints about ways in which the
code/formatting can be improved.

Python3 support
===============

Here are some tips that may be useful when doing some code for both python2 and
python3 at the same time:

- Assume, every string and literal is unicode (import unicode_literals):
 
  - Do not use prefix ``u'``.
  - Do not encode/decode strings in the middle of sth. Follow the code to the
    source (or target) of a string and encode/decode at the first/last possible
    point.
  - In other words, write your functions to expect and to return unicode.
  - Encode/decode strings if e.g. the source is a Python function that is known
    to handle this badly, e.g. strftime() in Python 2.

- Use new syntax: print function, "except ... *as* e" (not comma) etc.
- Refactor method calls like ``dict.iteritems()``, ``xrange()`` etc. in a way
  that runs without code change in both Python versions.
- Do not use magic method ``__unicode()__`` in new classes. Use only ``__str()__``
  and decorate the class with ``@python_2_unicode_compatible``.
- Do not start int literals with a zero. This is a syntax error in Py3k.
- Unfortunately I did not find an octal notation that is valid in both
  Pythons. Use decimal instead.
- use six, e.g.:

  - ``isinstance(.., basestring) -> isinstance(.., six.string_types)``
  - ``isinstance(.., unicode) -> isinstance(.., six.text_type)``

- ``setlocale()`` in Python 2 bails when we give the locale name as unicode,
  and since we are using ``from __future__ import unicode_literals``, we do
  that everywhere!  As a workaround, I enclosed the localename with ``str()``;
  in Python 2 this casts the name to a byte string, in Python 3 this should do
  nothing, because the locale name already had been unicode.

- Kept range() almost everywhere as-is (2to3 suggests list(range())), just
  changed it where I felt necessary.

- Changed xrange() back to range(), so it is valid in both Python versions.

