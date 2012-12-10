==========================
Pelican's Unified Codebase
==========================

:date: 2012-12-07

Unified means, this codebase runs without changes (or 2to3) in Python 2 and 3.
Specifically, it is tested for Python 2.6, 2.7 and 3.2.

At the time of this writing all tests pass, whether manually invoked
with ``unit2 discover`` within handmade virtual environments, or performed
by ``tox``, which tests on all 3 aforementioned versions::

    66 tests, 9 skips, no errors

During my first attempt to port Pelican to Python 3, I had used 2to3 and
applied manually corrections to achieve syntactical correctness. But as the
tests showed, more subtle bugs in the encoding of strings remained (e.g.
outputting b'...' instead of '...'). Also, the code was suitable for Python 3
only.

Building on the lessons learned with 2to3, this version of Pelican (py3k-v4)
now provides a single codebase for Python 2 and 3. It is a port of a clean
checkout of Pelican's latest master (3.1.1). Since I considered the gap between
Pelican's latest master and my previous ports too high, I did not merge, but
reviewed the code oculually.

The following chapter lists some hints, about what had to be changed. These
hints also may be valuable for those of you who provide new code and fixes.
Please code in a way that runs in both Python versions.


Unification
===========


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


About External Libraries
========================

Core
----

Pelican core depends on feedgenerator. To run on Py3k, you will need
feedgenerator-py3k which has a unified codebase too. Currently, it is
only available from github (a PyPi package will follow soon):

https://github.com/dmdm/feedgenerator-py3k/tree/from_django_1.5.dev20120824122350

BeautifulSoup had to be upgraded to bs4 (only bs4 supports Py3k), which has some
consequences:

- To parse XML like in the WordPress importer, also package lxml is
  required now.
- bs4 does not have ``convertEntities`` anymore.

Plugins
-------

On Python 2 you still can use all plugins and their dependencies as they are.
But if you like to run Pelican and the plugins on Python 3, you have to look
for compatible packages yourselves.

For **typogrify** and **smartypants**, on which typogrify depends, I provide
ready-made 2to3'd code:

- https://github.com/dmdm/smartypants.git
- https://github.com/dmdm/typogrify/tree/py3k

For **webassets** too I have 2to3'd code available:

- https://github.com/dmdm/webassets/tree/py3k

But it still has issues. One is that the less-css compiler is not correctly
invoked when I build the blog, e.g. with ``make html``. I have to invoke
the compiler manually afterwards::

    lessc themes/pymblog/static/less/pymblog.less > output/theme/css/pymblog.css

Be aware that the 2to3'd code of aforementioned libraries runs on Python 3 only.


Testing
=======

Testing on Python 2 is straightforward.

On Python 3, if you have installed the Py3k compatible versions of the
plugins, like shown in the previous chapter, manual testing with ``unit2 discover``
is also straightforward.

However, you must tell tox to use those Py3k libraries. If you forget this,
tox will pull the regular packages from PyPi and the tests will fail.

Tell tox about the local packages thusly: enter the source directory of
smartypants and run tox there. Do this again for typogrify and webassets.
Smartypants and typogrify do not have real tests, and webassets will fail
noisily, but as a result we get these libraries neatly packaged in tox's
distshare directory. And this we need to run tox for Pelican.

See also the comments in ``tox.ini``.
