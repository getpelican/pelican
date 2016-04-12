Filing issues
=============

* Before you file an issue, try `asking for help`_ first.
* If determined to file an issue, first check for `existing issues`_, including
  closed issues.

.. _`asking for help`: `How to get help`_
.. _`existing issues`: https://github.com/getpelican/pelican/issues

How to get help
===============

Before you ask for help, please make sure you do the following:

1. Read the documentation_ thoroughly. If in a hurry, at least use the search
   field that is provided at top-left on the documentation_ pages. Make sure
   you read the docs for the Pelican version you are using.
2. Use a search engine (e.g., DuckDuckGo, Google) to search for a solution to
   your problem. Someone may have already found a solution, perhaps in the
   form of a plugin_ or a specific combination of settings.

3. Try reproducing the issue in a clean environment, ensuring you are using:

* latest Pelican release (or an up-to-date git clone of Pelican master)
* latest releases of libraries used by Pelican
* no plugins or only those related to the issue

**NOTE:** The most common sources of problems are anomalies in (1) themes,
(2) settings files, and (3) ``make``/``fab`` automation wrappers. If you can't
reproduce your problem when using the following steps to generate your site,
then the problem is almost certainly with your chosen theme and/or settings
file (and not Pelican itself)::

    cd ~/projects/your-site
    git clone https://github.com/getpelican/pelican ~/projects/pelican
    pelican content -s ~/projects/pelican/samples/pelican.conf.py -t ~/projects/pelican/pelican/themes/notmyidea

If despite the above efforts you still cannot resolve your problem, be sure to
include in your inquiry the following information, preferably in the form of
links to content uploaded to a `paste service`_, GitHub repository, or other
publicly-accessible location:

* Describe what version of Pelican you are running (output of ``pelican --version``
  or the HEAD commit hash if you cloned the repo) and how exactly you installed
  it (the full command you used, e.g. ``pip install pelican``).
* If you are looking for a way to get some end result, prepare a detailed
  description of what the end result should look like (preferably in the form of
  an image or a mock-up page) and explain in detail what you have done so far to
  achieve it.
* If you are trying to solve some issue, prepare a detailed description of how
  to reproduce the problem. If the issue cannot be easily reproduced, it cannot
  be debugged by developers or volunteers. Describe only the **minimum steps**
  necessary to reproduce it (no extra plugins, etc.).
* Upload your settings file or any other custom code that would enable people to
  reproduce the problem or to see what you have already tried to achieve the
  desired end result.
* Upload detailed and **complete** output logs and backtraces (remember to add
  the ``--debug`` flag: ``pelican --debug content [...]``)

.. _documentation: http://docs.getpelican.com/
.. _`paste service`: https://dpaste.de/

Once the above preparation is ready, you can contact people willing to help via
(preferably) the ``#pelican`` IRC channel or send a message to ``authors at getpelican dot com``.
Remember to include all the information you prepared.

The #pelican IRC channel
------------------------

* Because of differing time zones, you may not get an immediate response to your
  question, but please be patient and stay logged into IRC — someone will almost
  always respond if you wait long enough (it may take a few hours).
* If you don't have an IRC client handy, use the webchat_ for quick feedback.
* You can direct your IRC client to the channel using this `IRC link`_ or you
  can manually join the ``#pelican`` IRC channel on the `freenode IRC network`_.

.. _webchat: https://kiwiirc.com/client/irc.freenode.net/?#pelican
.. _`IRC link`: irc://irc.freenode.org/pelican
.. _`freenode IRC network`: http://www.freenode.org/


Contributing code
=================

Before you submit a contribution, please ask whether it is desired so that you
don't spend a lot of time working on something that would be rejected for a
known reason. Consider also whether your new feature might be better suited as
a plugin_ — you can `ask for help`_  to make that determination.

Using Git and GitHub
--------------------

* `Create a new git branch`_ specific to your change (as opposed to making
  your commits in the master branch).
* **Don't put multiple unrelated fixes/features in the same branch / pull request.**
  For example, if you're hacking on a new feature and find a bugfix that
  doesn't *require* your new feature, **make a new distinct branch and pull
  request** for the bugfix.
* Check for unnecessary whitespace via ``git diff --check`` before committing.
* First line of your commit message should start with present-tense verb, be 50
  characters or less, and include the relevant issue number(s) if applicable.
  *Example:* ``Ensure proper PLUGIN_PATH behavior. Refs #428.`` If the commit
  *completely fixes* an existing bug report, please use ``Fixes #585`` or ``Fix
  #585`` syntax (so the relevant issue is automatically closed upon PR merge).
* After the first line of the commit message, add a blank line and then a more
  detailed explanation (when relevant).
* `Squash your commits`_ to eliminate merge commits and ensure a clean and
  readable commit history.
* If you have previously filed a GitHub issue and want to contribute code that
  addresses that issue, **please use** ``hub pull-request`` instead of using
  GitHub's web UI to submit the pull request. This isn't an absolute
  requirement, but makes the maintainers' lives much easier! Specifically:
  `install hub <https://github.com/github/hub/#installation>`_ and then run
  `hub pull-request <https://github.com/github/hub/#git-pull-request>`_ to
  turn your GitHub issue into a pull request containing your code.

Contribution quality standards
------------------------------

* Adhere to `PEP8 coding standards`_ whenever possible. This can be eased via
  the `pep8 <http://pypi.python.org/pypi/pep8>`_ or `flake8
  <http://pypi.python.org/pypi/flake8/>`_ tools, the latter of which in
  particular will give you some useful hints about ways in which the
  code/formatting can be improved.
* Make sure your code is compatible with Python 2.7, 3.3, and 3.4 — see our
  `compatibility cheatsheet`_ for more details.
* Add docs and tests for your changes. Undocumented and untested features will
  not be accepted.
* `Run all the tests`_ **on all versions of Python supported by Pelican** to
  ensure nothing was accidentally broken.

Check out our `Git Tips`_ page or `ask for help`_ if you
need assistance or have any questions about these guidelines.

.. _`plugin`: http://docs.getpelican.com/en/latest/plugins.html
.. _`#pelican IRC channel`: http://webchat.freenode.net/?channels=pelican&uio=d4
.. _`Create a new git branch`: https://github.com/getpelican/pelican/wiki/Git-Tips#making-your-changes
.. _`Squash your commits`: https://github.com/getpelican/pelican/wiki/Git-Tips#squashing-commits
.. _`Run all the tests`: http://docs.getpelican.com/en/latest/contribute.html#running-the-test-suite
.. _`Git Tips`: https://github.com/getpelican/pelican/wiki/Git-Tips
.. _`PEP8 coding standards`: http://www.python.org/dev/peps/pep-0008/
.. _`ask for help`: `How to get help`_
.. _`compatibility cheatsheet`: http://docs.getpelican.com/en/latest/contribute.html#python-3-development-tips
